"""Human check, round 3 (experiments/llm_study/PREREG.md): (a) do the 5 frozen aspects hold on the rewritten-prompt
images of Q4, and (b) which VLM-proposed candidate axes (Q6) pass the same rule?

Design (fixed before the package is built):
- Part a (Q4): images of G08 klein 4B and G05 FLUX.2 dev generated from the FLUX.2 rewrites
  ($T2IC_DATA/llm_study/<group>__mistral). Per frozen aspect 12 pairs from 12 different subjects (2 per category):
  8 "large" (one image from the bottom 15%, one from the top 15% of that subject's pool of 64 rewritten images by the
  aspect's CLIP score) and 4 "small" (both from the middle 40%).
- Part b (Q6): candidate axes from candidates.json ([{key, left, right}], written when the Q6 candidates are fixed).
  Scores: CLIP ViT-L/14 image embeddings already stored by aspects/score.py (clip_emb.npz) of the 12 study
  configurations, dotted with the difference of the L2-normalised pole text embeddings. Per candidate 16 pairs from 16
  subjects: 12 large and 4 small, tiers as in part a, pools = all study images of the subject.
- No image is used twice; left/right order and question order randomised; CLIP's answer is stored but never shown;
  seed 20261018; pair ids carry an "r3" tag.
- Decision rule: unchanged (agreement with CLIP >= 0.75 and "can't tell" <= 0.40 on large-gap pairs).

Usage: python make_pairs_round3.py [--candidates candidates.json] [--zip]
Writes $T2IC_DATA/annotation_round3/{pairs.json, label_aspects.html, img/}; analyse with
python analyze.py --pairs $T2IC_DATA/annotation_round3/pairs.json aspects_A.csv aspects_B.csv aspects_C.csv"""
import argparse, glob, json, os, random, sys, zipfile
import numpy as np, pandas as pd, torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_pairs_study as mps  # noqa: E402
from make_pairs_study import ASPECTS, MAIN  # noqa: E402

FROZEN = json.load(open(os.path.join(HERE, "..", "experiments", "model_study", "analysis", "frozen_aspects.json"),
                        encoding="utf-8"))
KEEP = list(FROZEN["retained"])
LLM = f"{mps.DATA_ROOT}/llm_study"
Q4_GROUPS = ["G08_klein4b__mistral", "G05_flux2_dev__mistral"]
OUT = f"{mps.DATA_ROOT}/annotation_round3"
SEED, SIDE = 20261018, 512


def load_dirs(dirs):
    parts = []
    for d in dirs:
        m = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/clip_scores.csv"), on="job")
        e = np.load(f"{d}/clip_emb.npz", allow_pickle=True)
        emb = dict(zip(e["job"], e["emb"]))
        m = m[m.kind == "main"].copy()
        m["dir"], m["group"] = d, os.path.basename(d).replace("__", "-")
        m["id"] = m.group + "__" + m.job
        m["emb"] = [emb[j] for j in m.job]
        parts.append(m)
    return pd.concat(parts, ignore_index=True)


def tiers(rnd, n_large, n_small, per_cat):
    """Subjects and tiers: per_cat subjects per category, n_large large and n_small small overall."""
    by_cat = {}
    for c, s in MAIN:
        by_cat.setdefault(c, []).append(s)
    for v in by_cat.values():
        rnd.shuffle(v)
    subs = [by_cat[c][r] for r in range(per_cat) for c in sorted(by_cat)][:n_large + n_small]  # round robin
    t = ["large"] * n_large + ["small"] * n_small
    rnd.shuffle(t)
    return list(zip(subs, t))


def pick(its, kind, rnd):
    n = len(its)
    band = lambda a, b: its.iloc[int(n * a): int(n * b)]
    if kind == "large":
        lo, hi = band(0, .15), band(.85, 1)
        return lo.iloc[rnd.randrange(len(lo))], hi.iloc[rnd.randrange(len(hi))]
    mid = band(.3, .7)
    a, b = rnd.sample(range(len(mid)), 2)
    return mid.iloc[a], mid.iloc[b]


def make(D, key, label, plan, used, rnd):
    pairs = []
    for i, (s, kind) in enumerate(plan):
        its = D[(D.subject == s) & ~D.id.isin(used)].sort_values(key).reset_index(drop=True)
        lo, hi = sorted(pick(its, kind, rnd), key=lambda r: r[key])
        used.update([lo.id, hi.id])
        left, right = (lo, hi) if rnd.random() < .5 else (hi, lo)
        pairs.append(dict(pid=f"{label}-r3-{i:02d}", aspect=label, kind=kind, prompt=s, left=left.id, right=right.id,
                          left_group=left.group, right_group=right.group, left_dir=left.dir, right_dir=right.dir,
                          clip=("right" if right[key] > left[key] else "left"), gap=round(float(abs(right[key] - left[key])), 5)))
    return pairs


@torch.no_grad()
def text_dir(cands):
    from transformers import CLIPModel, CLIPProcessor
    path = os.path.join(mps.DATA_ROOT, "models", "clip-vit-large-patch14")
    model, proc = CLIPModel.from_pretrained(path).eval(), CLIPProcessor.from_pretrained(path)

    def emb(t):
        f = model.get_text_features(**proc(text=t, return_tensors="pt", padding=True))
        return torch.nn.functional.normalize(getattr(f, "pooler_output", f), dim=-1).numpy()
    return emb([c["right"] for c in cands]) - emb([c["left"] for c in cands])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default="")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args()
    rnd = random.Random(SEED)
    mps.OUT = OUT
    asp = {x["key"]: dict(cn=x["cn"], lcn=x["lcn"], rcn=x["rcn"], l=x["left"], r=x["right"]) for x in ASPECTS if x["key"] in KEEP}
    used, pairs = set(), []
    Q4 = load_dirs([f"{LLM}/{g}" for g in Q4_GROUPS])
    for k in KEEP:
        pairs += make(Q4, k, k, tiers(rnd, 8, 4, 2), used, rnd)
    if a.candidates:
        cands = json.load(open(a.candidates, encoding="utf-8"))
        S = load_dirs(sorted(glob.glob(f"{mps.SRC}/G*")))
        E = np.stack(S.emb.to_numpy())
        T = text_dir(cands)
        for c, t in zip(cands, T):
            key = "cand_" + c["key"]
            S[key] = E @ t
            pairs += make(S, key, key, tiers(rnd, 12, 4, 3), used, rnd)
            asp[key] = dict(cn=c.get("cn", c["key"]), lcn=c.get("lcn", c["left"]), rcn=c.get("rcn", c["right"]),
                            l=c["left"], r=c["right"])
    rnd.shuffle(pairs)
    os.makedirs(f"{OUT}/img", exist_ok=True)
    for pr in pairs:
        for side in ("left", "right"):
            dst = f"{OUT}/img/{pr[side]}.jpg"
            if not os.path.exists(dst):
                job = pr[side].split("__")[-1]
                Image.open(f"{pr[side + '_dir']}/{job}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS).save(dst, quality=90)
    for pr in pairs:
        pr.pop("left_dir"), pr.pop("right_dir")
    json.dump(dict(seed=SEED, source="llm_study+model_study/open", round=3, results_dir="annotation_round3",
                   groups=Q4_GROUPS, pairs=pairs, aspects=asp), open(f"{OUT}/pairs.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    mps.write_page(pairs, asp)
    print(f"{OUT}: {len(pairs)} pairs; {len(os.listdir(f'{OUT}/img'))} images")
    if a.zip:
        z = f"{mps.DATA_ROOT}/annotation_round3_package.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            f.write(f"{OUT}/label_aspects.html", "label_aspects.html")
            f.write(os.path.join(HERE, "ANNOTATOR_GUIDE.md"), "GUIDE_zh.md")
            for fn in sorted(os.listdir(f"{OUT}/img")):
                f.write(f"{OUT}/img/{fn}", f"img/{fn}")
        print(z, f"{os.path.getsize(z) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
