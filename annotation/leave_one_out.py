"""Leave-one-annotator-out robustness of the round-1 verdicts (rule of PROTOCOL.md section 4). Annotator files are
mapped to A, B, C, ... in the order given on the command line, as in analyze.py.
Usage: python leave_one_out.py aspects_X.csv aspects_Y.csv ...   (pairs from $T2IC_DATA/annotation_study/pairs.json)"""
import json, os, sys, pandas as pd
D = os.environ["T2IC_DATA"] + "/annotation_study"
P = pd.DataFrame(json.load(open(f"{D}/pairs.json", encoding="utf-8"))["pairs"]).set_index("pid")
files = sys.argv[1:]
ann = {chr(ord("A") + i): f for i, f in enumerate(files)}
X = pd.concat([pd.read_csv(f).assign(who=a) for a, f in ann.items()])
X = X.join(P[["kind", "clip"]], on="pid")
L = X[X.kind == "large"]
def verdict(sub):
    out = {}
    for a, g in sub.groupby("aspect"):
        dec = g[g.answer != "none"]
        agree = (dec.answer == dec["clip"]).mean(); ct = (g.answer == "none").mean()
        out[a] = ("PASS" if agree >= .75 and ct <= .4 else "fail") + f" {agree:.2f}/{ct:.2f}"
    return out
cols = {f"all {len(ann)}": verdict(L)}
for drop in ann:
    cols[f"without {drop}"] = verdict(L[L.who != drop])
T = pd.DataFrame(cols)
T["stable"] = T.apply(lambda r: len({v.split()[0] for v in r}) == 1, axis=1)
print(T.to_string())
