"""Hidden-or-Lost pilot analysis across models. Usage: python analyze.py [model ...]"""
import os, sys, json
import numpy as np, pandas as pd
from config import ACCEPT, DATA, DIMENSIONS, GENERATORS, PROBES

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../results/hidden_or_lost")
os.makedirs(OUT, exist_ok=True)
models = sys.argv[1:] or [m for m in GENERATORS if os.path.exists(f"{DATA}/{m}/labels_qwen.csv")]
models = sorted(models, key=lambda m: (GENERATORS[m]["year"], m))


def norm_entropy(x, k):
    x = np.asarray(x).astype(int)
    p = np.bincount(x, minlength=k) / len(x)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum() / np.log(k))


summ, probe_rows, dim_rows = [], [], []
for m in models:
    d = f"{DATA}/{m}"
    meta = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/labels_qwen.csv"), on="job")
    base = meta[meta.probe == "base"]
    div = pd.read_csv(f"{d}/diversity.csv") if os.path.exists(f"{d}/diversity.csv") else None
    ent = {dim: np.mean([norm_entropy(g[dim].values, len(opts)) for _, g in base.groupby("subject")])
           for dim, (q, opts) in DIMENSIONS.items()}
    top = {dim: np.mean([np.bincount(g[dim].values.astype(int)).max() / len(g) for _, g in base.groupby("subject")])
           for dim in DIMENSIONS}
    for dim in DIMENSIONS:
        dist = np.bincount(base[dim].values.astype(int), minlength=len(DIMENSIONS[dim][1])) / len(base)
        dim_rows.append(dict(model=m, dim=dim, entropy=ent[dim], top_share=top[dim],
                             **{f"p_{o}": round(float(x), 3) for o, x in zip(DIMENSIONS[dim][1], dist)}))
    pr = meta[meta.probe != "base"].copy()
    pr["dim"] = pr.probe.map(lambda p: PROBES[p][1])
    pr["typ"] = pr.probe.map(lambda p: PROBES[p][3])
    pr["comply"] = [r[r.dim] in ACCEPT.get(r.probe, {PROBES[r.probe][2]}) for _, r in pr.iterrows()]
    pr["comply_and_subject"] = pr.comply & (pr.subject_present == 1)
    for p, g in pr.groupby("probe"):
        probe_rows.append(dict(model=m, probe=p, typ=PROBES[p][3], comply=g.comply.mean(),
                               comply_and_subject=g.comply_and_subject.mean(), n=len(g)))
    summ.append(dict(model=m, year=GENERATORS[m]["year"],
                     vendi_mean=float(div.vendi.mean()) if div is not None else np.nan,
                     pairwise_dist=float(div.mean_pairwise_dist.mean()) if div is not None else np.nan,
                     default_entropy_mean=float(np.mean(list(ent.values()))),
                     subject_adherence_base=float(base.subject_present.mean()),
                     reach_typical=float(pr[pr.typ == "typical"].comply.mean()),
                     reach_atypical=float(pr[pr.typ == "atypical"].comply.mean()),
                     reach_atypical_with_subject=float(pr[pr.typ == "atypical"].comply_and_subject.mean())))

S, P, Dm = pd.DataFrame(summ), pd.DataFrame(probe_rows), pd.DataFrame(dim_rows)
S.to_csv(f"{OUT}/summary.csv", index=False); P.to_csv(f"{OUT}/probes.csv", index=False); Dm.to_csv(f"{OUT}/dimensions.csv", index=False)
pd.set_option("display.width", 220)
print(S.round(3).to_string(index=False))
print("\ncompliance by probe:")
print(P.pivot(index="probe", columns="model", values="comply")[models].round(2).to_string())
print("\ndefault entropy by dimension (base images, normalised):")
print(Dm.pivot(index="dim", columns="model", values="entropy")[models].round(2).to_string())
