"""Round-2 sensitivity (exploratory, not part of the decision rule): verdicts with an extra annotator D and leaving one
annotator out; CLIP gap of large pairs per round; agreement by CLIP gap in scale units over both rounds; saturation pairs
involving Qwen-Image. Usage (run from the repository root on the server, after source ops/env.sh):
python annotation/round2_sensitivity.py r1_A.csv r1_B.csv r1_C.csv r2_A.csv r2_B.csv r2_C.csv [r2_D.csv]"""
import json, os, sys, numpy as np, pandas as pd
D = os.environ["T2IC_DATA"]
sys.path.insert(0, "annotation")
scale = json.load(open("experiments/model_study/analysis/frozen_scale.json"))["scale"]
def load(rnd, files):
    P = pd.DataFrame(json.load(open(f"{D}/{rnd}/pairs.json", encoding="utf-8"))["pairs"]).set_index("pid")
    X = pd.concat([pd.read_csv(f).assign(who=w) for w, f in files.items()]).join(P[["kind", "clip", "gap", "left_group", "right_group"]], on="pid")
    X["gap_s"] = X.gap / X.aspect.map(scale)
    return X
def verdict(sub):
    dec = sub[sub.answer != "none"]; a = (dec.answer == dec["clip"]).mean(); ct = (sub.answer == "none").mean()
    return a, ct

R2 = load("annotation_round2", dict(zip("ABCD", sys.argv[4:8])))
R1 = load("annotation_study", dict(zip("ABC", sys.argv[1:4])))
A5 = ["sat", "medium", "shot", "tone", "bg"]
print("== round 2, large-gap pairs: agreement / can't tell")
rows = {}
for name, who in [("primary A,B,C", "ABC"), ("+ D (4)", "ABCD"), ("D only", "D"), ("without A", "BC"), ("without B", "AC"), ("without C", "AB")]:
    L = R2[(R2.kind == "large") & R2.who.isin(list(who))]
    rows[name] = {a: "%s %.2f/%.2f" % (("PASS" if verdict(L[L.aspect == a])[0] >= .75 and verdict(L[L.aspect == a])[1] <= .4 else "fail"), *verdict(L[L.aspect == a])) for a in A5}
print(pd.DataFrame(rows).to_string())
print("\n== CLIP gap of 'large' pairs in scale units (median): round 1 vs round 2")
for a in A5:
    g1 = R1[(R1.kind == "large") & (R1.aspect == a) & (R1.who == "A")].gap_s.median()
    g2 = R2[(R2.kind == "large") & (R2.aspect == a) & (R2.who == "A")].gap_s.median()
    print(f"  {a:7s} round1 {g1:.2f}  round2 {g2:.2f}")
print("\n== agreement by CLIP gap (scale units), both rounds pooled, annotators A,B,C, all tiers")
Allp = pd.concat([R1.assign(rnd=1), R2[R2.who.isin(list("ABC"))].assign(rnd=2)])
Allp["bin"] = pd.cut(Allp.gap_s, [0, 1, 2, 3, 4, 100], labels=["<1", "1-2", "2-3", "3-4", ">=4"])
T = Allp.groupby(["aspect", "bin"], observed=True).apply(lambda s: "%.2f/%.2f n%d" % (*verdict(s), len(s)), include_groups=False).unstack()
print(T.to_string())
print("\n== round 2, saturation pairs involving Qwen-Image (G09/G10), large+medium tiers, A,B,C")
q = R2[(R2.aspect == "sat") & R2.who.isin(list("ABC")) & (R2.left_group.str[:3].isin(["G09", "G10"]) | R2.right_group.str[:3].isin(["G09", "G10"])) & R2.kind.isin(["large", "medium"])]
print("  pairs %d, agreement %.2f, can't tell %.2f" % (q.pid.nunique(), *verdict(q)))
