"""Build the visual audit tool (rev5) for the model study: data.js, thumbnails and the static page.

Inputs ($T2IC_DATA = data folder):
  model_study/open/<group>/{meta.csv, clip_scores.csv}   groups that have been generated and CLIP-scored
  experiments/model_study/open/config.py                  declared settings of every group (provenance)
  experiments/model_study/prompts.py                      subjects, categories, prompt-implied aspects
  experiments/model_study/analysis/frozen_aspects.json     retained aspects (frozen 2026-10-12)
  experiments/model_study/analysis/frozen_margins.json     practical margins and the scale definition (frozen 2026-10-12)
Output: $T2IC_DATA/audit_tool/{index.html, d3.min.js, data.js, thumbs/<group>/<job>.jpg}
Serve that folder with a static server, e.g. `python -m http.server 8772 --bind 127.0.0.1`.

All statistics of a contrast (location shift in scale units, log IQR ratio, bootstrap intervals, pooled estimates) are
computed in the browser for the contrast the user picks; this script only prepares scores, the scale and provenance.
The scale s_aspect follows frozen_margins.json; it is marked provisional until all 12 open groups are scored.
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
    G = GEN[g]
    s = dict(weights=G["path"], pipeline=G["pipe"], dtype=G["dtype"], resolution=f'{G["size"]}²', steps=G["steps"],
             guidance=f'{G.get("cfg_arg", "guidance_scale")} = {G["cfg"]}')
    neg = G.get("extra", {}).get("negative_prompt")
    s["negative_prompt"] = repr(neg) if neg is not None else "none"
    if G.get("variant"):
        s["variant"] = G["variant"]
    return s


def main():
    groups = [os.path.basename(d) for d in sorted(glob.glob(f"{SRC}/G*")) if os.path.exists(f"{d}/clip_scores.csv")]
    if not groups:
        sys.exit(f"no scored groups in {SRC}")
    cat = {s: c for c, s in MAIN}
    subjects = [s for _, s in MAIN]
    frames = []
    for g in groups:
        m = pd.read_csv(f"{SRC}/{g}/meta.csv").merge(pd.read_csv(f"{SRC}/{g}/clip_scores.csv"), on="job")
        m = m[m.kind == "main"].copy()
        m["group"] = g
        frames.append(m)
    D = pd.concat(frames, ignore_index=True)

    # scale per aspect (frozen definition): sqrt of the mean within-cell variance over group x subject cells,
    # skipping subjects that imply the aspect
    scale = {}
    for a in SHOWN:
        v = [x[a].var(ddof=1) for (g, s), x in D.groupby(["group", "subject"]) if a not in EXCLUDED.get(s, ())]
        scale[a] = float(math.sqrt(np.mean(v)))
    complete = len(groups) == len(GEN)

    # thumbnails
    for g in groups:
        os.makedirs(f"{OUT}/thumbs/{g}", exist_ok=True)
        for job in D[D.group == g].job:
            dst = f"{OUT}/thumbs/{g}/{job}.jpg"
            if not os.path.exists(dst):
                Image.open(f"{SRC}/{g}/{job}.png").convert("RGB").resize((THUMB, THUMB), Image.LANCZOS).save(dst, quality=85)

    asp = {x["key"]: dict(left=x["left"], right=x["right"]) for x in ASPECTS if x["key"] in SHOWN}
    meta = dict(
        built=pd.Timestamp.now().isoformat(timespec="minutes"),
        groups=[dict(id=g, label=LABEL.get(g, g), family=FAMILY.get(g[:3], ""), settings=settings(g),
                     n=int((D.group == g).sum())) for g in groups],
        all_groups=len(GEN),
        subjects=[dict(name=s, category=cat[s], excluded=list(EXCLUDED.get(s, ()))) for s in subjects],
        aspects=[dict(key=a, retained=a in RETAINED, **asp[a]) for a in SHOWN],
        scale=scale, scale_provisional=not complete, scale_groups=groups,
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
        z = np.load(f"{SRC}/{g}/clip_emb.npz", allow_pickle=True)
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
    shutil.copy(os.path.join(HERE, "index.html"), f"{OUT}/index.html")
    shutil.copy(os.path.join(REPO, "system", "d3.min.js"), f"{OUT}/d3.min.js")
    print(f"{OUT}: {len(groups)} groups ({'complete' if complete else 'scale provisional'}), {len(D)} images;",
          "scale:", {a: round(v, 4) for a, v in scale.items()})


if __name__ == "__main__":
    main()
