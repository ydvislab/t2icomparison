"""Caption-density analysis: Vendi (DINOv2, 8 seeds) and VLM dimension entropy per condition + key contrasts.
Usage: python analyze.py   (expects embed.py/label.py outputs from ../hidden_or_lost run with HOL_DATA set)"""
import os, sys, numpy as np, pandas as pd
from config import CONDITIONS, DATA

DIMS = {"medium": 6, "lighting": 5, "framing": 3, "color": 3, "quality": 3}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../results/caption_density")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)


def ent(x, k):
    p = np.bincount(np.asarray(x).astype(int), minlength=k) / len(x); p = p[p > 0]
    return float(-(p * np.log(p)).sum() / np.log(k))


per_subj, summ = [], []
for c in CONDITIONS:
    d = f"{DATA}/{c}"
    if not os.path.exists(f"{d}/diversity.csv"):
        continue
    div = pd.read_csv(f"{d}/diversity.csv")
    lab = pd.read_csv(f"{d}/labels_qwen.csv") if os.path.exists(f"{d}/labels_qwen.csv") else None
    meta = pd.read_csv(f"{d}/meta.csv")
    for s, g in div.groupby("subject"):
        row = dict(condition=c, subject=s, vendi=float(g.vendi.iloc[0]))
        if lab is not None:
            gl = meta.merge(lab, on="job")
            gl = gl[gl.subject == s]
            row["dim_entropy"] = np.mean([ent(gl[k], n) for k, n in DIMS.items()])
            row["adherence"] = float(gl.subject_present.mean())
        per_subj.append(row)
P = pd.DataFrame(per_subj)
for c, g in P.groupby("condition", sort=False):
    summ.append(dict(condition=c, model=CONDITIONS[c][0], weights=os.path.basename(CONDITIONS[c][1]),
                     steps=CONDITIONS[c][2], cfg=CONDITIONS[c][3], style=CONDITIONS[c][4],
                     vendi=g.vendi.mean(), dim_entropy=g.get("dim_entropy", pd.Series(dtype=float)).mean(),
                     adherence=g.get("adherence", pd.Series(dtype=float)).mean()))
S = pd.DataFrame(summ); S.to_csv(f"{OUT}/summary.csv", index=False); P.to_csv(f"{OUT}/per_subject.csv", index=False)
pd.set_option("display.width", 200)
print(S.round(3).to_string(index=False))


def contrast(a, b, col="vendi"):
    if a not in set(P.condition) or b not in set(P.condition):
        return
    A = P[P.condition == a].set_index("subject")[col]; B = P[P.condition == b].set_index("subject")[col]
    d = (A - B).dropna()
    bs = [d.sample(len(d), replace=True, random_state=int(s)).mean() for s in rng.integers(0, 1e9, 4000)]
    print(f"{col:11s} {a:>18s} - {b:<18s}: {d.mean():+.2f}  95% CI [{np.percentile(bs,2.5):+.2f}, {np.percentile(bs,97.5):+.2f}]  "
          f"({(d > 0).sum()}/{len(d)} subjects positive)")


print("\nKey contrasts (paired by subject, bootstrap over subjects):")
for col in ["vendi", "dim_entropy"]:
    if col in P:
        contrast("sd15_cfg1_min", "kbase_cfg1_min", col)     # 1 caption-density test (pure conditionals)
        contrast("kbase_cfg1_min", "kbase_cfg4_min", col)    # 2 guidance
        contrast("kbase_cfg4_min", "klein_min", col)         # 3 distillation
        contrast("klein_dense", "klein_min", col)            # 4 text style within models
        contrast("klein_open", "klein_min", col)
        contrast("kbase_cfg1_dense", "kbase_cfg1_min", col)
        contrast("sd15_cfg75_dense", "sd15_cfg75_min", col)
        contrast("sd15_cfg75_open", "sd15_cfg75_min", col)
        contrast("sd15_cfg75_min", "kbase_cfg4_min", col)    # guided vs guided
