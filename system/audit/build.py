"""Build the visual audit tool (rev5) for the model study: data.js, thumbnails and the static page.

Inputs ($T2IC_DATA = data folder):
  model_study/open/<group>/{meta.csv, clip_scores.csv}   groups that have been generated and CLIP-scored
  experiments/model_study/open/config.py                  declared settings of every group (provenance)
  experiments/model_study/prompts.py                      subjects, categories, prompt-implied aspects
  experiments/model_study/analysis/frozen_aspects.json     retained aspects (frozen 2026-10-12)
  experiments/model_study/analysis/frozen_margins.json     practical margins and the scale definition (frozen 2026-10-12)
  llm_study/<group>__<rewrite>/{meta.csv, clip_scores.csv} rewritten-prompt images of the LLM study (if scored)
  llm_study/rewrites_<llm>.csv                           the rewrites (text side of the rewrite view)
  llm_study/q5/<vlm>/coded.csv and results/q5/truth.csv   VLM statements and the audit's truth (statement view)
Output: $T2IC_DATA/audit_tool/{index.html, d3.min.js, data.js, thumbs/<group>/<job>.jpg}
Serve that folder with a static server, e.g. `python -m http.server 8772 --bind 127.0.0.1`.

All statistics of a contrast (location shift in scale units, log IQR ratio, bootstrap intervals, pooled estimates) are
computed in the browser for the contrast the user picks; this script only prepares scores, the scale and provenance.
The scale is the frozen one (experiments/model_study/analysis/frozen_scale.json, 12 open configurations); rewritten-prompt
groups are added as extra configurations that never enter the scale or the map's common centre.
"""
import glob, json, math, os, shutil, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):  # t-SNE thrashes with all 64 cores on a busy server
    os.environ.setdefault(_v, "8")
import numpy as np
import pandas as pd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MS = os.path.join(REPO, "experiments", "model_study")
sys.path.insert(0, MS)
sys.path.insert(0, os.path.join(MS, "open"))
sys.path.insert(0, os.path.join(REPO, "aspects"))
from prompts import EXCLUDED, MAIN  # noqa: E402
from config import GROUPS as GEN  # noqa: E402
from aspects import ASPECTS  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
SRC = f"{DATA}/model_study/open"
LLM = f"{DATA}/llm_study"
REWRITES = {"mistral": ("FLUX.2 rewrite", "rwF", "FLUX.2 upsampler (Mistral-Small-3.2-24B), one rewrite per seed"),
            "mistral_fixed": ("one FLUX.2 rewrite", "rw1", "the k = 0 FLUX.2 rewrite reused for all seeds"),
            "qwen": ("Qwen rewrite", "rwQ", "Qwen3.5-4B with the FLUX.2 instruction, one rewrite per seed")}
# aspects validated by people per configuration set (annotation/PROTOCOL.md section 7): round 1 validated all five on
# the configurations generated first, round 2 only shot, saturation and medium on the later ones; the rewritten-prompt
# images are checked in round 3 (until its result is in, they are marked pending)
ROUND1 = {"G01_sd15", "G02_sdxl", "G03_sdxl_turbo", "G06_klein_base4b_cfg4", "G07_klein_base4b_cfg1", "G08_klein4b"}
ROUND3_FILE = os.path.join(REPO, "results", "annotation_round3", "aspect_check.csv")


def validity(g):
    if "__" in g:
        if os.path.exists(ROUND3_FILE):
            r3 = pd.read_csv(ROUND3_FILE)
            ok = set(r3[r3.reliable.astype(bool)].aspect)
            return dict(set="round 3", aspects=[a for a in RETAINED if a in ok])
        return dict(set="round 3 (pending)", aspects=list(RETAINED))
    if g in ROUND1:
        return dict(set="round 1", aspects=list(RETAINED))
    return dict(set="round 2", aspects=["shot", "sat", "medium"])


Q5_CONTRASTS = {"guid_klein": ("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"), "guid_qwen": ("G10_qwen_image_cfg1", "G09_qwen_image_cfg4"),
                "pkg_klein4b": ("G07_klein_base4b_cfg1", "G08_klein4b"), "sdxl_turbo": ("G02_sdxl", "G03_sdxl_turbo"),
                "rw_klein": ("G08_klein4b", "G08_klein4b__mistral"), "rw_flux": ("G05_flux2_dev", "G05_flux2_dev__mistral")}
OUT = f"{DATA}/audit_tool"
THUMB = 192
FROZEN_A = json.load(open(os.path.join(MS, "analysis", "frozen_aspects.json"), encoding="utf-8"))
FROZEN_M = json.load(open(os.path.join(MS, "analysis", "frozen_margins.json"), encoding="utf-8"))
RETAINED = list(FROZEN_A["retained"])
SHOWN = RETAINED + ["inout"]          # inout is shown in the tool only (frozen_aspects.json)

LABEL = {  # short display names; the full settings come from config.py
    "G01_sd15": "SD 1.5", "G02_sdxl": "SDXL", "G03_sdxl_turbo": "SDXL-Turbo", "G04_sd35_large": "SD3.5 Large",
    "G05_flux2_dev": "FLUX.2 dev", "G06_klein_base4b_cfg4": "klein-base 4B · CFG 4",
    "G07_klein_base4b_cfg1": "klein-base 4B · CFG 1", "G08_klein4b": "klein 4B", "G09_qwen_image_cfg4": "Qwen-Image · CFG 4",
    "G10_qwen_image_cfg1": "Qwen-Image · CFG 1", "G11_klein_base9b": "klein-base 9B", "G12_klein9b": "klein 9B",
}
FAMILY = {"G01": "Stable Diffusion", "G02": "Stable Diffusion", "G03": "Stable Diffusion", "G04": "Stable Diffusion",
          "G05": "FLUX.2", "G06": "FLUX.2", "G07": "FLUX.2", "G08": "FLUX.2", "G11": "FLUX.2", "G12": "FLUX.2",
          "G09": "Qwen-Image", "G10": "Qwen-Image"}


def settings(g):
    base, _, rw = g.partition("__")
    G = GEN[base]
    s = dict(weights=G["path"], pipeline=G["pipe"], dtype=G["dtype"], resolution=f'{G["size"]}²', steps=G["steps"],
             guidance=f'{G.get("cfg_arg", "guidance_scale")} = {G["cfg"]}')
    neg = G.get("extra", {}).get("negative_prompt")
    s["negative_prompt"] = repr(neg) if neg is not None else "none"
    if G.get("variant"):
        s["variant"] = G["variant"]
    s["prompt"] = REWRITES[rw][2] if rw else "minimal prompt"
    return s


def gdir(g):
    return f"{LLM}/{g}" if "__" in g else f"{SRC}/{g}"


def text_encoder():
    import torch
    from transformers import CLIPModel, CLIPProcessor
    path = os.path.join(DATA, "models", "clip-vit-large-patch14")
    model, proc = CLIPModel.from_pretrained(path).eval(), CLIPProcessor.from_pretrained(path)

    def emb(texts):
        out = []
        with torch.no_grad():
            for i in range(0, len(texts), 64):
                f = model.get_text_features(**proc(text=list(texts[i:i + 64]), return_tensors="pt", padding=True,
                                                    truncation=True, max_length=77))
                out.append(torch.nn.functional.normalize(getattr(f, "pooler_output", f), dim=-1).numpy())
        return np.concatenate(out)
    return emb


def rewrite_data(groups, subjects):
    """Rewrite texts per rewritten group and subject ([k, text, text shift per shown aspect]). The text shift is the CLIP
    text-encoder score of the rewrite minus that of the original prompt, in text units (across-subject SD of the original
    prompts' text scores), as in experiments/llm_study/text_side.py."""
    rw_groups = [g for g in groups if "__" in g]
    if not rw_groups:
        return {}
    emb = text_encoder()
    keep = [next(x for x in ASPECTS if x["key"] == a) for a in SHOWN]
    L, Rr = emb([x["left"] for x in keep]), emb([x["right"] for x in keep])
    E0 = emb(subjects)
    S0 = E0 @ Rr.T - E0 @ L.T
    unit = S0.std(0, ddof=1)
    out = {}
    for g in rw_groups:
        rw = g.partition("__")[2]
        W = pd.read_csv(f"{LLM}/rewrites_{rw.replace('_fixed', '')}.csv")
        if rw.endswith("_fixed"):
            W["rewrite"] = W.i.map(W[W.k == 0].set_index("i").rewrite)
        E = emb(list(W.rewrite))
        T = (E @ Rr.T - E @ L.T - S0[W.i.values]) / unit
        rows = [[] for _ in subjects]
        for j, r in enumerate(W.itertuples()):
            rows[r.i].append([int(r.k), r.rewrite, [round(float(v), 3) for v in T[j]]])
        out[g] = rows
    return out


def statements(groups):
    """VLM free-text statements (coded by experiments/llm_study/code_free.py) with the audit's verdict for the same
    contrast, level, unit and aspect (results/q5/truth.csv, written by q5_score.py)."""
    tp = os.path.join(REPO, "results", "q5", "truth.csv")
    if not os.path.exists(tp):
        return []
    T = pd.read_csv(tp, keep_default_na=False)
    idx = {(r.contrast, r.level, r.unit, r.aspect): r for r in T.itertuples()}
    out = []
    for vlm in ("qwen", "mistral"):
        p = f"{LLM}/q5/{vlm}/coded.csv"
        if not os.path.exists(p):
            continue
        for r in pd.read_csv(p, keep_default_na=False).itertuples():
            A, B = Q5_CONTRASTS.get(r.contrast, (None, None))
            if A not in groups or B not in groups:
                continue
            unit = r.unit if r.level == "subject" else "*"
            si = int(unit[1:]) if r.level == "subject" else -1
            verdict, asp = "outside the measured aspects", ""
            if r.property in RETAINED and r.direction in ("right", "left"):
                asp = r.property
                t = idx.get((r.contrast, r.level, unit, asp))
                if t is None or str(t.validated) != "True":
                    verdict = "aspect not validated here"
                elif t.shift == "":
                    verdict = "audit undecided"
                elif t.shift == r.direction:
                    verdict = "confirmed"
                elif t.shift == "none":
                    verdict = "narrowed, did not move" if t.variety == "less" else "audit: no shift"
                else:
                    verdict = "contradicted"
            elif r.property == "variety" and r.direction in ("less", "more"):
                ts = [idx.get((r.contrast, r.level, unit, a)) for a in RETAINED]
                ts = [t for t in ts if t is not None and str(t.validated) == "True" and t.variety != ""]
                hit = [t.aspect for t in ts if t.variety == r.direction]
                verdict = ("confirmed on " + ", ".join(hit)) if hit else ("not on the measured aspects" if ts else "audit undecided")
                asp = hit[0] if hit else ""
            out.append(dict(vlm=vlm, A=A, B=B, level=r.level, si=si, text=r.statement, prop=r.property,
                            dir=r.direction, aspect=asp, verdict=verdict))
    return out


def main():
    groups = [os.path.basename(d) for d in sorted(glob.glob(f"{SRC}/G*")) if os.path.exists(f"{d}/clip_scores.csv")]
    groups += [os.path.basename(d) for d in sorted(glob.glob(f"{LLM}/G*__*")) if os.path.exists(f"{d}/clip_scores.csv")
               and os.path.basename(d).partition("__")[0] in groups]
    if not groups:
        sys.exit(f"no scored groups in {SRC}")
    cat = {s: c for c, s in MAIN}
    subjects = [s for _, s in MAIN]
    frames = []
    for g in groups:
        m = pd.read_csv(f"{gdir(g)}/meta.csv").merge(pd.read_csv(f"{gdir(g)}/clip_scores.csv"), on="job")
        m = m[m.kind == "main"].copy()
        m["group"] = g
        frames.append(m)
    D = pd.concat(frames, ignore_index=True)

    # the frozen scale (frozen_scale.json, 12 open configurations); before it exists, the same definition over the
    # scored open groups (provisional). Rewritten-prompt groups never enter the scale.
    sf = os.path.join(MS, "analysis", "frozen_scale.json")
    opens = [g for g in groups if "__" not in g]
    if os.path.exists(sf):
        scale = {a: float(json.load(open(sf, encoding="utf-8"))["scale"][a]) for a in SHOWN}
        complete = True
    else:
        scale = {}
        for a in SHOWN:
            v = [x[a].var(ddof=1) for (g, s), x in D[D.group.isin(opens)].groupby(["group", "subject"]) if a not in EXCLUDED.get(s, ())]
            scale[a] = float(math.sqrt(np.mean(v)))
        complete = len(opens) == len(GEN)

    # thumbnails
    for g in groups:
        os.makedirs(f"{OUT}/thumbs/{g}", exist_ok=True)
        for job in D[D.group == g].job:
            dst = f"{OUT}/thumbs/{g}/{job}.jpg"
            if not os.path.exists(dst):
                Image.open(f"{gdir(g)}/{job}.png").convert("RGB").resize((THUMB, THUMB), Image.LANCZOS).save(dst, quality=85)

    asp = {x["key"]: dict(left=x["left"], right=x["right"]) for x in ASPECTS if x["key"] in SHOWN}
    meta = dict(
        built=pd.Timestamp.now().isoformat(timespec="minutes"),
        groups=[dict(id=g, label=LABEL.get(g.partition("__")[0], g) + (" · " + REWRITES[g.partition("__")[2]][0] if "__" in g else ""),
                     family=FAMILY.get(g[:3], ""), settings=settings(g), n=int((D.group == g).sum()),
                     rewrite=REWRITES[g.partition("__")[2]][1] if "__" in g else "", base=g.partition("__")[0])
                for g in groups],
        all_groups=len(GEN),
        subjects=[dict(name=s, category=cat[s], excluded=list(EXCLUDED.get(s, ()))) for s in subjects],
        aspects=[dict(key=a, retained=a in RETAINED, **asp[a]) for a in SHOWN],
        scale=scale, scale_provisional=not complete, scale_groups=opens,
        validity={g: validity(g) for g in groups},
        margins=dict(location=FROZEN_M["location_effect"]["displacement_margin"], log_iqr=math.log(1.5)),
    )
    # scores: group -> subject index -> list of [k, seed, job, s_a1, s_a2, ...] in SHOWN order
    scores = {}
    for g in groups:
        x = D[D.group == g]
        scores[g] = [[[int(r.k), int(r.seed), r.job] + [round(float(getattr(r, a)), 5) for a in SHOWN]
                      for r in x[x.subject == s].sort_values("k").itertuples()] for s in subjects]
    # appearance map per subject: t-SNE of the CLIP image embeddings of every image of every scored configuration
    # (cosine distance, perplexity 30, PCA initialisation, fixed seed), so all configurations share one map per subject.
    # Coordinates are stored in the same order as SCORES and rescaled to [0, 1].
    from sklearn.manifold import TSNE
    emb = {}
    for g in groups:
        z = np.load(f"{gdir(g)}/clip_emb.npz", allow_pickle=True)
        emb[g] = dict(zip(z["job"], z["emb"]))
    tsne = {g: [None] * len(subjects) for g in groups}
    for si, s in enumerate(subjects):
        keys = [(g, r.job) for g in groups for r in D[(D.group == g) & (D.subject == s)].sort_values("k").itertuples()]
        X = np.stack([emb[g][j] for g, j in keys])
        Y = TSNE(n_components=2, perplexity=30, metric="cosine", init="pca", random_state=0).fit_transform(X)
        Y = (Y - Y.min(0)) / np.ptp(Y, 0).clip(1e-9)
        i = 0
        for g in groups:
            n = int(((D.group == g) & (D.subject == s)).sum())
            tsne[g][si] = [[round(float(a), 4), round(float(b), 4)] for a, b in Y[i:i + n]]
            i += n
    meta["tsne"] = "t-SNE of CLIP ViT-L/14 image embeddings per subject over all scored configurations (cosine, perplexity 30, seed 0)"
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/data.js", "w", encoding="utf-8") as f:
        f.write("const META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
        f.write("const SCORES = " + json.dumps(scores, separators=(",", ":")) + ";\n")
        f.write("const TSNE = " + json.dumps(tsne, separators=(",", ":")) + ";\n")
        f.write("const REWRITE = " + json.dumps(rewrite_data(groups, subjects), ensure_ascii=False, separators=(",", ":")) + ";\n")
        f.write("const STATEMENTS = " + json.dumps(statements(groups), ensure_ascii=False, separators=(",", ":")) + ";\n")
    shutil.copy(os.path.join(HERE, "index.html"), f"{OUT}/index.html")
    shutil.copy(os.path.join(HERE, "baseline.html"), f"{OUT}/baseline.html")
    shutil.copy(os.path.join(REPO, "system", "d3.min.js"), f"{OUT}/d3.min.js")
    print(f"{OUT}: {len(groups)} groups ({'complete' if complete else 'scale provisional'}), {len(D)} images;",
          "scale:", {a: round(v, 4) for a, v in scale.items()})


if __name__ == "__main__":
    main()
