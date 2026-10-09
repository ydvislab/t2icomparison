"""Uncertainty for the Hidden-or-Lost pilot: per-subject consistency, bootstrap over subjects, Wilson CIs."""
import os, numpy as np, pandas as pd
from config import DATA, PROBES, ACCEPT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../results/hidden_or_lost")
M = ["sd15", "sdxl_turbo", "klein4b"]
rng = np.random.default_rng(0)
div = pd.concat([pd.read_csv(f"{DATA}/{m}/diversity.csv") for m in M]).pivot(index="subject", columns="model", values="vendi")[M]
print("Vendi per subject:\n", div.round(2).to_string())
for a, b in [("sd15", "klein4b"), ("sdxl_turbo", "klein4b"), ("sd15", "sdxl_turbo")]:
    d = div[a] - div[b]
    boots = [d.sample(len(d), replace=True, random_state=int(s)).mean() for s in rng.integers(0, 1e9, 5000)]
    print(f"{a} - {b}: mean diff {d.mean():.2f}, 95% CI [{np.percentile(boots,2.5):.2f}, {np.percentile(boots,97.5):.2f}], "
          f"{(d > 0).sum()}/{len(d)} subjects lower for {b}")


def wilson(k, n, z=1.96):
    p = k / n; c = (p + z*z/(2*n)) / (1 + z*z/n); h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return c - h, c + h


rows = []
for m in M:
    meta = pd.read_csv(f"{DATA}/{m}/meta.csv").merge(pd.read_csv(f"{DATA}/{m}/labels_qwen.csv"), on="job")
    pr = meta[meta.probe != "base"].copy()
    pr["comply"] = [r[PROBES[r.probe][1]] in ACCEPT.get(r.probe, {PROBES[r.probe][2]}) for _, r in pr.iterrows()]
    for typ in ["typical", "atypical"]:
        g = pr[pr.probe.map(lambda p: PROBES[p][3]) == typ]
        lo, hi = wilson(g.comply.sum(), len(g))
        rows.append(dict(model=m, typ=typ, k=int(g.comply.sum()), n=len(g), rate=g.comply.mean(), lo=lo, hi=hi))
R = pd.DataFrame(rows); R.to_csv(f"{OUT}/reach_ci.csv", index=False)
print("\nreachability with 95% Wilson CI:\n", R.round(3).to_string(index=False))
div.to_csv(f"{OUT}/vendi_by_subject.csv")
