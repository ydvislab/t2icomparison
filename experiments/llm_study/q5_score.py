"""Q5 scoring: are the VLMs' constrained answers about set differences right? (PREREG.md)
Usage: python q5_score.py [--round3 results/annotation_round3/aspect_check.csv]
Ground truth from all 32 seeds with the frozen scale and margins:
  per subject  shift: right/left if |Delta| >= 0.5 and the per-subject 90% seed-bootstrap interval (2,000 replicates,
               seed 20261016) excludes 0; none if the interval lies inside (-0.5, 0.5); otherwise not scored.
               variety: less/more if the IQR ratio is beyond 1/1.5 or 1.5 and its interval excludes 1; same if the
               interval lies inside (1/1.5, 1.5); otherwise not scored.
  pooled       verdicts of Q1 (results/q1/primary.csv), Q3 (results/q3/primary.csv, packages.csv) and Q4
               (results/q4/primary.csv): displaced -> right/left, same place -> none; concentrated -> less,
               widened -> more, same spread -> same; any other verdict is not scored. A pooled aspect is marked
               misleading when the pooled shift is within the margin but >= 3 subjects shift each way (per-subject rule).
Only aspects validated on every configuration set involved are scored: round-1 set all five; round-2 set shot, sat,
medium; rewritten images: aspects passing round 3 (all five until round 3 is in, reported as provisional).
Writes results/q5/{truth.csv, scored.csv, summary.csv}."""
import argparse, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
import q1_primary as q1  # noqa: E402
import q4_analysis as q4  # noqa: E402

OUT = os.path.join(q1.REPO, "results", "q5")
R1 = {"G01_sd15", "G02_sdxl", "G03_sdxl_turbo", "G06_klein_base4b_cfg4", "G07_klein_base4b_cfg1", "G08_klein4b"}
R2_VALID = {"shot", "sat", "medium"}
CONTRASTS = {"guid_klein": ("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"),
             "guid_qwen": ("G10_qwen_image_cfg1", "G09_qwen_image_cfg4"),
             "pkg_klein4b": ("G07_klein_base4b_cfg1", "G08_klein4b"),
             "sdxl_turbo": ("G02_sdxl", "G03_sdxl_turbo"),
             "rw_klein": ("G08_klein4b", "G08_klein4b__mistral"),
             "rw_flux": ("G05_flux2_dev", "G05_flux2_dev__mistral")}
POOLED_FILES = [("results/q1/primary.csv", "verdict"), ("results/q3/primary.csv", "verdict"),
                ("results/q3/packages.csv", "label"), ("results/q4/primary.csv", "verdict")]


def valid(group, r3):
    if "__" in group:
        return r3
    return set(q1.ASPECTS) if group in R1 else R2_VALID


def load_all():
    fr = [q4.load()]
    for d in sorted(set(g for p in CONTRASTS.values() for g in p if "__" not in g)):
        p = f"{q1.SRC}/{d}"
        m = pd.read_csv(f"{p}/meta.csv").merge(pd.read_csv(f"{p}/clip_scores.csv"), on="job")
        fr.append(m[m.kind == "main"].assign(group=d)[["group", "subject", "k"] + q1.ASPECTS])
    return pd.concat(fr, ignore_index=True).drop_duplicates(["group", "subject", "k"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--round3", default=""); a = ap.parse_args()
    if a.round3:
        r3 = pd.read_csv(a.round3)
        r3_valid, provisional = set(r3[r3.reliable.astype(bool)].aspect) & set(q1.ASPECTS), False
    else:
        r3_valid, provisional = set(q1.ASPECTS), True
    D = load_all()
    sc, _ = q1.scale(D, False)
    pooled = {}
    for f, col in POOLED_FILES:
        p = os.path.join(q1.REPO, f)
        if os.path.exists(p):
            for r in pd.read_csv(p).itertuples():
                pooled[(r.A, r.B, r.aspect, r.effect)] = (getattr(r, col), r.estimate)
    truth = []
    for c, (ga, gb) in CONTRASTS.items():
        if not ({ga, gb} <= set(D.group)):
            print("missing", c); continue
        ok = valid(ga, r3_valid) & valid(gb, r3_valid)
        subs, cats, A, B = q1.arrays(D, ga, gb)
        d, lr = q1.effects(A, B, sc)
        rng = np.random.default_rng(20261016)
        up = np.zeros(len(q1.ASPECTS), int); down = np.zeros(len(q1.ASPECTS), int)
        for i, s in enumerate(subs):
            seeds = rng.integers(0, A.shape[1], size=(q1.NSUB_BOOT, A.shape[1]))
            dd, ll = q1.effects(A[i][seeds], B[i][seeds], sc)
            for j, asp in enumerate(q1.ASPECTS):
                lo, hi = np.percentile(dd[:, j], [5, 95]); llo, lhi = np.percentile(ll[:, j], [5, 95])
                if abs(d[i, j]) >= q1.M_LOC and (lo > 0 or hi < 0):
                    sh = "right" if d[i, j] > 0 else "left"
                elif lo > -q1.M_LOC and hi < q1.M_LOC:
                    sh = "none"
                else:
                    sh = ""
                if abs(lr[i, j]) >= q1.M_LR and (llo > 0 or lhi < 0):
                    va = "more" if lr[i, j] > 0 else "less"
                elif llo > -q1.M_LR and lhi < q1.M_LR:
                    va = "same"
                else:
                    va = ""
                up[j] += sh == "right"; down[j] += sh == "left"
                truth.append(dict(contrast=c, level="subject", unit=f"s{i:02d}", aspect=asp, validated=asp in ok,
                                  shift=sh, variety=va, delta=d[i, j], ratio=np.exp(lr[i, j])))
        for j, asp in enumerate(q1.ASPECTS):
            vl, el = pooled.get((ga, gb, asp, "location"), ("", np.nan))
            vs, _ = pooled.get((ga, gb, asp, "spread"), ("", np.nan))
            sh = {"displaced": "right" if el > 0 else "left", "same place": "none"}.get(vl, "")
            va = {"concentrated": "less", "widened": "more", "same spread": "same"}.get(vs, "")
            mis = bool(abs(np.median(d[:, j])) < q1.M_LOC and up[j] >= 3 and down[j] >= 3)
            truth.append(dict(contrast=c, level="pooled", unit="*", aspect=asp, validated=asp in ok, shift=sh,
                              variety=va, delta=np.median(d[:, j]), ratio=np.exp(np.median(lr[:, j])), misleading=mis))
    T = pd.DataFrame(truth)
    os.makedirs(OUT, exist_ok=True)
    T.to_csv(f"{OUT}/truth.csv", index=False, float_format="%.4f")
    rows = []
    for vlm in ("qwen", "mistral"):
        p = f"{q4.LLM}/q5/{vlm}/mc.csv"
        if not os.path.exists(p):
            continue
        M = pd.read_csv(p)
        M["key_unit"] = np.where(M.level == "subject", M.unit, "*")
        X = M.merge(T, left_on=["contrast", "level", "key_unit", "aspect"], right_on=["contrast", "level", "unit", "aspect"],
                    suffixes=("", "_t"))
        X["truth"] = np.where(X.question == "shift", X["shift"], X["variety"])
        X = X[X.validated & (X.truth.fillna("") != "")]
        X["correct"] = X.answer == X.truth
        rows.append(X.assign(vlm=vlm))
    if not rows:
        print("no VLM answers yet"); return
    S = pd.concat(rows)
    S.to_csv(f"{OUT}/scored.csv", index=False, float_format="%.4f")
    summ = []
    for (vlm, level, q), g in S.groupby(["vlm", "level", "question"]):
        summ.append(dict(vlm=vlm, level=level, question=q, n=len(g), accuracy=g.correct.mean(),
                         answer_none_or_same=(g.answer.isin(["none", "same"])).mean(),
                         truth_none_or_same=(g.truth.isin(["none", "same"])).mean()))
    for vlm, g in S[S.level == "subject"].groupby("vlm"):
        sh = g[g.question == "shift"].set_index(["contrast", "unit", "aspect"])
        va = g[g.question == "variety"].set_index(["contrast", "unit", "aspect"])
        j = sh.join(va[["truth", "answer"]], rsuffix="_v", how="inner")
        conc = j[(j.truth == "none") & (j.truth_v == "less")]
        summ.append(dict(vlm=vlm, level="subject", question="concentration reported as shift", n=len(conc),
                         accuracy=np.nan, rate=(conc.answer != "none").mean() if len(conc) else np.nan))
        less = va[va.truth == "less"]
        summ.append(dict(vlm=vlm, level="subject", question="missed concentration (truth less, answer same)",
                         n=len(less), rate=(less.answer == "same").mean() if len(less) else np.nan))
        more = va[va.truth == "more"]
        summ.append(dict(vlm=vlm, level="subject", question="widening missed (truth more, answer same)",
                         n=len(more), rate=(more.answer == "same").mean() if len(more) else np.nan))
    P = S[(S.level == "pooled") & (S.question == "shift")]
    for vlm, g in P.groupby("vlm"):
        m = g[g.misleading.astype(bool)]
        summ.append(dict(vlm=vlm, level="pooled", question="pooled shift claimed on misleading aspects",
                         n=len(m), rate=(m.answer != "none").mean() if len(m) else np.nan))
    # null controls (deviation 2): the same configuration on both sides, so the truth is "no difference" and "about equally
    # varied" by construction; the false-difference rate is the share of answers that report a shift or a change in variety
    for vlm in ("qwen", "mistral"):
        p = f"{q4.LLM}/q5/{vlm}/mc.csv"
        if not os.path.exists(p):
            continue
        N = pd.read_csv(p)
        N = N[N.contrast.str.startswith("null_")]
        for (lev, q), g in N.groupby(["level", "question"]):
            summ.append(dict(vlm=vlm, level=lev, question=f"null control: {q} reported", n=len(g),
                             rate=(g.answer != ("none" if q == "shift" else "same")).mean()))
    U = pd.DataFrame(summ).assign(provisional_round3=provisional)
    U.to_csv(f"{OUT}/summary.csv", index=False, float_format="%.3f")
    print(U.to_string(index=False))
    print("\nby contrast (subject level):")
    print(S[S.level == "subject"].groupby(["vlm", "contrast", "question"]).correct.agg(["mean", "size"]).round(2).to_string())


if __name__ == "__main__":
    main()
