"""Q5 free text scored against the audit (PREREG.md: coded statements are scored like the constrained answers).
Usage: python free_score.py   (needs results/q5/truth.csv from q5_score.py and q5/<vlm>/coded.csv from code_free.py)
- Aspect statements (coded to one of the 5 aspects with a direction): compared with the audit's shift truth for the
  same contrast, level, unit and aspect, where that truth is scored (validated aspect, verdict not ambiguous).
- Variety statements: a unit (one grid pair) "mentions narrowing" if any statement is coded variety/less. Compared with
  how many validated aspects of that unit the audit finds less varied.
Writes results/q5/free_summary.csv."""
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
import q1_primary as q1  # noqa: E402

DATA = q1.DATA
OUT = os.path.join(q1.REPO, "results", "q5")
T = pd.read_csv(f"{OUT}/truth.csv")
T = T[T.validated]
rows = []
for vlm in ("qwen", "mistral"):
    p = f"{DATA}/llm_study/q5/{vlm}/coded.csv"
    if not os.path.exists(p):
        continue
    C = pd.read_csv(p)
    C["key_unit"] = C.unit.where(C.level == "subject", "*")
    n_units = C.groupby(["contrast", "level", "unit"]).ngroups
    for prop, g in C.groupby("property"):
        rows.append(dict(vlm=vlm, measure=f"statements on {prop}", value=len(g), n=len(C)))
    A = C[C.property.isin(q1.ASPECTS) & C.direction.isin(["right", "left"])]
    X = A.merge(T[["contrast", "level", "unit", "aspect", "shift"]], left_on=["contrast", "level", "key_unit", "property"],
                right_on=["contrast", "level", "unit", "aspect"], suffixes=("", "_t"))
    X = X[X["shift"].fillna("") != ""]
    for lev, g in X.groupby("level"):
        rows.append(dict(vlm=vlm, measure=f"{lev}: aspect statements with correct direction", value=(g.direction == g["shift"]).mean(), n=len(g)))
        rows.append(dict(vlm=vlm, measure=f"{lev}: aspect statements where audit says no shift", value=(g["shift"] == "none").mean(), n=len(g)))
    V = C[C.property == "variety"]
    less_units = V[V.direction == "less"].groupby(["contrast", "level", "unit"]).size().index
    TU = T.assign(key=list(zip(T.contrast, T.level, T.unit)))
    lessT = TU[TU.variety == "less"].groupby(["contrast", "level", "unit"]).size()
    units = C.groupby(["contrast", "level", "key_unit"]).size().index
    hit, tot, false_less = 0, 0, 0
    for c, lev, u in units:
        uid = (c, lev, u if lev == "subject" else "*")
        truth_less = lessT.get(uid, 0) > 0
        said_less = any((c, lev, uu) in set(less_units) for uu in ([u] if lev == "subject" else C[(C.contrast == c) & (C.level == lev)].unit.unique()))
        tot += truth_less
        hit += truth_less and said_less
        false_less += (not truth_less) and said_less
    rows.append(dict(vlm=vlm, measure="units where audit finds narrowing that the free text mentions", value=hit / tot if tot else float("nan"), n=tot))
    rows.append(dict(vlm=vlm, measure="units with variety statements 'less' / all units", value=len(less_units) / n_units, n=n_units))
S = pd.DataFrame(rows)
S.to_csv(f"{OUT}/free_summary.csv", index=False, float_format="%.3f")
print(S.to_string(index=False))
