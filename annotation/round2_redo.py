"""Round 2 re-annotation: verdicts and test-retest.
Usage: python annotation/round2_redo.py PAIRS_JSON A.csv B.csv C.csv D.csv B_redo.csv C_redo.csv
A-C are the round-2 annotators (first-pass labels), D the sensitivity annotator, and B', C' the re-labels of
B and C made after a re-briefing on the annotator guide; the re-labels are the round-2 result (owner decision
2026-10-14). Same decision rule as PROTOCOL.md section 4 on the large-gap pairs. Prints to stdout."""
import json, sys
import pandas as pd

pairs, files = sys.argv[1], sys.argv[2:]
t = pd.DataFrame(json.load(open(pairs, encoding="utf-8"))["pairs"]).set_index("pid")
A = {k: pd.read_csv(f).set_index("pid")["answer"].reindex(t.index) for k, f in zip(["A", "B", "C", "D", "B'", "C'"], files)}


def check(names):
    out = {}
    for asp, g in t[t.kind == "large"].groupby("aspect"):
        ans = pd.concat([A[n][g.index] for n in names])
        clip = pd.concat([g["clip"]] * len(names))
        dec = ans != "none"
        agr, none = (ans[dec] == clip[dec]).mean(), 1 - dec.mean()
        out[asp] = f"{'PASS' if agr >= .75 and none <= .40 else 'fail'} {agr:.2f}/{none:.2f}"
    return out


sets = {"original A,B,C": ["A", "B", "C"], "re-labelled A,B',C'": ["A", "B'", "C'"], "re-labelled + D": ["A", "B'", "C'", "D"],
        "without A": ["B'", "C'"], "without B'": ["A", "C'"], "without C'": ["A", "B'"],
        "B": ["B"], "B'": ["B'"], "C": ["C"], "C'": ["C'"], "A": ["A"]}
print("== large-gap pairs: agreement with CLIP / can't tell (12 pairs per aspect per annotator)")
print(pd.DataFrame({k: check(v) for k, v in sets.items()}).T.to_string())
print("\n== test-retest over all 120 pairs")
for a, b in [("B", "B'"), ("C", "C'")]:
    x, y = A[a], A[b]
    chg = x != y
    agr = lambda s: (s[s != "none"] == t["clip"][s != "none"]).mean()
    print(f"{a} -> {b}: identical {(x == y).mean():.2f}; left/right reversed {((x != 'none') & (y != 'none') & chg).mean():.2f}; "
          f"can't tell {(x == 'none').mean():.2f} -> {(y == 'none').mean():.2f}; agreement with CLIP (all tiers) {agr(x):.2f} -> {agr(y):.2f}")
    print(f"   of {chg.sum()} changed answers, {((y == t['clip']) & chg).sum()} now match CLIP and {((x == t['clip']) & chg).sum()} matched CLIP before")
