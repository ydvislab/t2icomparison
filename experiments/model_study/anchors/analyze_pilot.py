"""Analyse the anchor pilot (docs/RESEARCH_PROPOSAL.md §4.2) and choose the phrasing for the full anchor set.

Usage: python analyze_pilot.py [group ...]      (default: G08_klein4b G09_qwen_image_cfg4)
Needs, per group, $T2IC_DATA/model_study/anchors_pilot/<group>/{meta.csv, clip_scores.csv} (gen.py --jobset anchor_pilot,
then aspects/score.py). If the study images of the same group are scored too ($T2IC_DATA/model_study/open/<group>/
clip_scores.csv), the calibrated location x of the default images is computed for every phrasing.

Per group x aspect x subject x phrasing:
  L, R      median target-aspect score of left-pole / right-pole requests
  gap       R - L, with a 90% bootstrap interval (images resampled within each pole)
  auc       P(score of a right-pole image > score of a left-pole image); 1 = perfectly separated
  off_auc   largest |AUC - 0.5| over the other 14 aspects (scale-free side effect), and which aspect
  x         (median score of the default images - L) / gap, if default images are available
Writes results/anchors_pilot/{cells.csv, phrasings.csv, references.csv} and contact sheets
$T2IC_DATA/model_study/anchors_pilot/sheets/<group>_<aspect>.jpg (rows: pole x phrasing per subject; columns: seeds).
"""
import os, sys
import numpy as np, pandas as pd
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "aspects"))
from aspects import ASPECTS  # noqa: E402
from anchors import PILOT_SUBJECTS, PILOT_TEMPLATES  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
PILOT = f"{DATA}/model_study/anchors_pilot"
STUDY = f"{DATA}/model_study/open"
OUT = os.path.join(HERE, "..", "..", "..", "results", "anchors_pilot")
KEYS = [x["key"] for x in ASPECTS]
rng = np.random.default_rng(0)


def auc(lo, hi):
    """P(hi > lo) + 0.5 P(hi == lo) over all pairs."""
    lo, hi = np.asarray(lo)[:, None], np.asarray(hi)[None, :]
    return float(((hi > lo) + 0.5 * (hi == lo)).mean())


def gap_ci(lo, hi, n=1000):
    b = [np.median(rng.choice(hi, len(hi))) - np.median(rng.choice(lo, len(lo))) for _ in range(n)]
    return np.percentile(b, [5, 95])


def load(group):
    d = f"{PILOT}/{group}"
    if not os.path.exists(f"{d}/clip_scores.csv"):
        sys.exit(f"{d}/clip_scores.csv missing: run aspects/score.py {d}")
    A = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/clip_scores.csv"), on="job")
    D = None
    if os.path.exists(f"{STUDY}/{group}/clip_scores.csv"):
        D = pd.read_csv(f"{STUDY}/{group}/meta.csv").merge(pd.read_csv(f"{STUDY}/{group}/clip_scores.csv"), on="job")
        D = D[D.kind == "main"]
    return A, D


def cells(group, A, D):
    rows = []
    for (asp, subj, v), g in A.groupby(["aspect", "subject", "phrasing"]):
        lo, hi = g[g.pole == "left"], g[g.pole == "right"]
        L, R = float(np.median(lo[asp])), float(np.median(hi[asp]))
        c_lo, c_hi = gap_ci(lo[asp].values, hi[asp].values)
        off = {b: abs(auc(lo[b], hi[b]) - 0.5) for b in KEYS if b != asp}
        worst = max(off, key=off.get)
        r = dict(group=group, aspect=asp, subject=subj, phrasing=v, n_left=len(lo), n_right=len(hi), L=round(L, 5),
                 R=round(R, 5), gap=round(R - L, 5), gap_lo=round(c_lo, 5), gap_hi=round(c_hi, 5),
                 auc=round(auc(lo[asp], hi[asp]), 3), off_auc=round(off[worst], 3), off_aspect=worst)
        if D is not None and (D.subject == subj).any() and R != L:
            r["x_default"] = round((float(np.median(D[D.subject == subj][asp])) - L) / (R - L), 3)
        rows.append(r)
    return pd.DataFrame(rows)


def sheet(group, A, aspect, side=96):
    d = f"{PILOT}/{group}"
    seeds = sorted(A.k.unique())
    rows = [(s, p, v) for s in PILOT_SUBJECTS for p in ("left", "right") for v in range(len(PILOT_TEMPLATES[aspect][p]))]
    rows = [r for r in rows if ((A.aspect == aspect) & (A.subject == r[0]) & (A.pole == r[1]) & (A.phrasing == r[2])).any()]
    if not rows:
        return
    lab = 260
    im = Image.new("RGB", (lab + side * len(seeds), side * len(rows)), "white")
    dr = ImageDraw.Draw(im)
    for i, (s, p, v) in enumerate(rows):
        g = A[(A.aspect == aspect) & (A.subject == s) & (A.pole == p) & (A.phrasing == v)].set_index("k")
        dr.text((4, i * side + side // 2 - 6), g.prompt.iloc[0][:44], fill="black")
        for c, k in enumerate(seeds):
            if k in g.index:
                im.paste(Image.open(f"{d}/{g.loc[k, 'job']}.png").convert("RGB").resize((side, side)), (lab + c * side, i * side))
    os.makedirs(f"{PILOT}/sheets", exist_ok=True)
    im.save(f"{PILOT}/sheets/{group}_{aspect}.jpg", quality=85)


def main(groups):
    os.makedirs(OUT, exist_ok=True)
    C = []
    for g in groups:
        if not os.path.exists(f"{PILOT}/{g}/meta.csv"):
            print("skip", g, "(no pilot images)")
            continue
        A, D = load(g)
        C.append(cells(g, A, D))
        for asp in A.aspect.unique():
            sheet(g, A, asp)
    C = pd.concat(C, ignore_index=True)
    C.to_csv(f"{OUT}/cells.csv", index=False)
    # one row per group x aspect x phrasing, summarised over subjects
    agg = dict(subjects=("subject", "nunique"), auc_min=("auc", "min"), auc_median=("auc", "median"),
               gap_lo_min=("gap_lo", "min"), off_auc_median=("off_auc", "median"), off_auc_max=("off_auc", "max"))
    P = C.groupby(["group", "aspect", "phrasing"]).agg(**agg).reset_index()
    if "x_default" in C:
        # sensitivity of the calibrated default position to the phrasing: range of x over phrasings, per subject
        xr = C.groupby(["group", "aspect", "subject"]).x_default.agg(lambda s: s.max() - s.min()).rename("x_range")
        P = P.merge(xr.groupby(["group", "aspect"]).median().rename("x_range_median").reset_index(), on=["group", "aspect"])
    P.to_csv(f"{OUT}/phrasings.csv", index=False)
    print(P.to_string(index=False))
    # agreement between reference models: anchors of each phrasing, per subject
    if C.group.nunique() >= 2:
        W = C.pivot_table(index=["aspect", "subject", "phrasing"], columns="group", values=["L", "R", "gap"])
        W.columns = [f"{a}_{b}" for a, b in W.columns]
        W.reset_index().to_csv(f"{OUT}/references.csv", index=False)
        print(f"\nreference agreement written for {C.group.nunique()} groups")
    print(f"\nsheets: {PILOT}/sheets/")


if __name__ == "__main__":
    main(sys.argv[1:] or ["G08_klein4b", "G09_qwen_image_cfg4"])
