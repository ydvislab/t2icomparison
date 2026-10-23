"""Q5 deviation 3 (exploratory, PREREG.md): answer stability across two disjoint draws of grids, and scoring against
a truth computed from the 8 seeds the VLM saw. Usage: python q5_stability.py   (writes results/q5/stability.csv and
results/q5/shown_seed_truth.csv)
- Stability: first-draw answers (q5/<vlm>/mc.csv) vs second-draw answers (q5/<vlm>_draw2/mc.csv) for the same
  contrast, level, unit index, aspect and question. Agreement = share identical; chance = sum over answers of the product
  of the two draws' answer frequencies in that cell (contrast x level x question).
- Shown-seed truth (subject level, first draw): shift and variety verdicts from seeds k = 0..7 with the frozen margins
  and a 2,000-replicate seed bootstrap over those 8 seeds (same rules as q5_score.py); accuracy on rows where both the
  32-seed and the 8-seed truth are decided, and on rows decided by the 8-seed truth only. Validated aspects as q5_score."""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
import q1_primary as q1  # noqa: E402
import q5_score as q5  # noqa: E402

OUT = q5.OUT


def stability():
    rows = []
    for vlm in ("qwen", "mistral"):
        p1, p2 = f"{q5.q4.LLM}/q5/{vlm}/mc.csv", f"{q5.q4.LLM}/q5/{vlm}_draw2/mc.csv"
        if not (os.path.exists(p1) and os.path.exists(p2)):
            continue
        M1, M2 = pd.read_csv(p1), pd.read_csv(p2)
        M1 = M1[M1.contrast.isin(q5.CONTRASTS)]
        J = M1.merge(M2, on=["contrast", "level", "unit", "aspect", "question"], suffixes=("_1", "_2"))
        for (c, lev, qq), g in J.groupby(["contrast", "level", "question"]):
            f1, f2 = g.answer_1.value_counts(normalize=True), g.answer_2.value_counts(normalize=True)
            rows.append(dict(vlm=vlm, contrast=c, level=lev, question=qq, n=len(g), agreement=(g.answer_1 == g.answer_2).mean(),
                             chance=float(sum(f1.get(k, 0) * f2.get(k, 0) for k in set(f1.index) | set(f2.index)))))
        for (lev, qq), g in J.groupby(["level", "question"]):
            f1, f2 = g.answer_1.value_counts(normalize=True), g.answer_2.value_counts(normalize=True)
            rows.append(dict(vlm=vlm, contrast="ALL", level=lev, question=qq, n=len(g), agreement=(g.answer_1 == g.answer_2).mean(),
                             chance=float(sum(f1.get(k, 0) * f2.get(k, 0) for k in set(f1.index) | set(f2.index)))))
    return pd.DataFrame(rows)


def truth8():
    """Subject-level shift and variety verdicts from seeds k = 0..7 only (the seeds shown in the first-draw grids)."""
    D = q5.load_all()
    sc, _ = q1.scale(D, False)
    r3p = os.path.join(q1.REPO, "results", "annotation_round3", "aspect_check.csv")
    r3 = pd.read_csv(r3p); r3_valid = set(r3[r3.reliable.astype(bool)].aspect) & set(q1.ASPECTS)
    truth = []
    for c, (ga, gb) in q5.CONTRASTS.items():
        if not ({ga, gb} <= set(D.group)):
            continue
        ok = q5.valid(ga, r3_valid) & q5.valid(gb, r3_valid)
        subs, cats, A, B = q1.arrays(D, ga, gb)
        A8, B8 = A[:, :8], B[:, :8]
        d, lr = q1.effects(A8, B8, sc)
        rng = np.random.default_rng(20261023)
        for i in range(len(subs)):
            seeds = rng.integers(0, 8, size=(q1.NSUB_BOOT, 8))
            dd, ll = q1.effects(A8[i][seeds], B8[i][seeds], sc)
            for j, asp in enumerate(q1.ASPECTS):
                lo, hi = np.percentile(dd[:, j], [5, 95]); llo, lhi = np.percentile(ll[:, j], [5, 95])
                sh = ("right" if d[i, j] > 0 else "left") if abs(d[i, j]) >= q1.M_LOC and (lo > 0 or hi < 0) else \
                     ("none" if lo > -q1.M_LOC and hi < q1.M_LOC else "")
                va = ("more" if lr[i, j] > 0 else "less") if abs(lr[i, j]) >= q1.M_LR and (llo > 0 or lhi < 0) else \
                     ("same" if llo > -q1.M_LR and lhi < q1.M_LR else "")
                truth.append(dict(contrast=c, level="subject", unit=f"s{i:02d}", aspect=asp, validated=asp in ok, shift8=sh, variety8=va))
    return pd.DataFrame(truth)


def shown_truth():
    T8 = truth8()
    T32 = pd.read_csv(os.path.join(OUT, "truth.csv"), keep_default_na=False)
    rows = []
    for vlm in ("qwen", "mistral"):
        M = pd.read_csv(f"{q5.q4.LLM}/q5/{vlm}/mc.csv")
        M = M[(M.level == "subject") & M.contrast.isin(q5.CONTRASTS)]
        X = M.merge(T8, on=["contrast", "level", "unit", "aspect"]).merge(T32[["contrast", "level", "unit", "aspect", "shift", "variety"]],
                                                                       on=["contrast", "level", "unit", "aspect"])
        X = X[X.validated]
        for qq, t8, t32 in [("shift", "shift8", "shift"), ("variety", "variety8", "variety")]:
            g = X[X.question == qq]
            both = g[(g[t8] != "") & (g[t32].astype(str) != "")]
            only8 = g[g[t8] != ""]
            rows.append(dict(vlm=vlm, question=qq, n_both=len(both), acc_vs_32=(both.answer == both[t32]).mean(),
                             acc_vs_8=(both.answer == both[t8]).mean(), n_decided_8=len(only8),
                             acc_vs_8_all=(only8.answer == only8[t8]).mean(),
                             truth8_none_or_same=(only8[t8].isin(["none", "same"])).mean(),
                             truths_agree=(both[t8] == both[t32]).mean()))
    return pd.DataFrame(rows)


def main():
    S = stability(); S.to_csv(os.path.join(OUT, "stability.csv"), index=False, float_format="%.3f")
    print(S[S.contrast == "ALL"].to_string(index=False))
    T = shown_truth(); T.to_csv(os.path.join(OUT, "shown_seed_truth.csv"), index=False, float_format="%.3f")
    print(T.to_string(index=False))


if __name__ == "__main__":
    main()
