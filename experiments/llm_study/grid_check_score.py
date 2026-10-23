"""Deviation 4 (exploratory, PREREG.md): people's answers on the VLM grids, scored like the VLMs' answers on the same items.
Usage: python grid_check_score.py   (reads $T2IC_DATA/grid_check/items.json and $T2IC_DATA/grid_check/answers/*.csv;
writes results/q5/grid_check_{summary,items}.csv; annotators appear as H1-H3 in sorted order of their labels)
- Truths: the 32-seed truth stored with each item (results/q5/truth.csv) and the 8-seed truth of the shown seeds
  (q5_stability.truth8); null items have "none"/"same" by construction.
- Raters: each person, the majority of the people (no majority -> unscored), and each VLM's first-draw answer on the
  same contrast x subject x aspect x question (q5/<vlm>/mc.csv).
- Measures: accuracy on real items against each truth; share of null items where a difference is reported; share of
  "no difference" answers on real items; Fleiss' kappa among the people; agreement of each VLM with the people's majority."""
import glob, json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
import q5_score as q5  # noqa: E402
import q5_stability as st  # noqa: E402

GC = f"{q5.q4.LLM}/../grid_check"
NODIFF = {"none", "same"}


def fleiss(M):
    cats = sorted(set(M.values.ravel()))
    n = M.shape[1]
    P = np.array([[(row == c).sum() for c in cats] for row in M.values])
    Pi = ((P * (P - 1)).sum(1)) / (n * (n - 1))
    pj = P.sum(0) / P.sum()
    return (Pi.mean() - (pj ** 2).sum()) / (1 - (pj ** 2).sum())


def main():
    I = pd.DataFrame(json.load(open(f"{GC}/items.json", encoding="utf-8")))
    H = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{GC}/answers/*.csv"))])
    names = sorted(H.annotator.unique())
    H["rater"] = H.annotator.map({a: f"H{k + 1}" for k, a in enumerate(names)})
    W = H.pivot(index="id", columns="rater", values="answer")
    people = list(W.columns)
    maj = W.apply(lambda r: r.value_counts().index[0] if r.value_counts().iloc[0] >= 2 else "", axis=1)
    X = I.set_index("id").join(W).assign(people=maj)
    T8 = st.truth8()
    X = X.reset_index().merge(T8[["contrast", "unit", "aspect", "shift8", "variety8"]], on=["contrast", "unit", "aspect"], how="left")
    X["truth8"] = np.where(X.question == "shift", X.shift8, X.variety8)
    X.loc[X.contrast.str.startswith("null_"), "truth8"] = X.truth32
    X["truth8"] = X.truth8.fillna("")
    for vlm in ("qwen", "mistral"):
        M = pd.read_csv(f"{q5.q4.LLM}/q5/{vlm}/mc.csv")
        M = M[M.level == "subject"][["contrast", "unit", "aspect", "question", "answer"]].rename(columns={"answer": vlm})
        X = X.merge(M, on=["contrast", "unit", "aspect", "question"], how="left")
    X["null"] = X.contrast.str.startswith("null_")
    rows = []
    for r in people + ["people", "qwen", "mistral"]:
        for qq in ("shift", "variety", "both"):
            g = X if qq == "both" else X[X.question == qq]
            real, nul = g[~g.null & (g[r].fillna("") != "")], g[g.null & (g[r].fillna("") != "")]
            d8 = real[real.truth8 != ""]
            rows.append(dict(rater=r, question=qq, n_real=len(real), acc_32=(real[r] == real.truth32).mean(),
                             n_8=len(d8), acc_8=(d8[r] == d8.truth8).mean(),
                             nodiff_real=real[r].isin(NODIFF).mean(), n_null=len(nul),
                             null_diff_reported=(~nul[r].isin(NODIFF)).mean(),
                             agree_people=(g[r] == g.people)[g.people != ""].mean() if r not in people + ["people"] else np.nan))
    S = pd.DataFrame(rows)
    k = {qq: fleiss(W.loc[X[X.question == qq].id]) for qq in ("shift", "variety")}
    S = pd.concat([S, pd.DataFrame([dict(rater="fleiss_kappa_people", question=qq, acc_32=v) for qq, v in k.items()])])
    S.to_csv(os.path.join(q5.OUT, "grid_check_summary.csv"), index=False, float_format="%.3f")
    X[["id", "contrast", "unit", "subject", "aspect", "question", "truth32", "truth8"] + people + ["people", "qwen", "mistral"]] \
        .to_csv(os.path.join(q5.OUT, "grid_check_items.csv"), index=False)
    print(S.to_string(index=False))
    print("truths agree on real items:", (X[~X.null & (X.truth8 != "")].truth8 == X[~X.null & (X.truth8 != "")].truth32).mean())


if __name__ == "__main__":
    main()
