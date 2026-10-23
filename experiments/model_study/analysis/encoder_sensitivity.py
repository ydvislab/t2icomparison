"""Second-encoder sensitivity check (ENCODER_CHECK.md): rerun the primary tests of Q1, Q3 and Q4 with SigLIP 2 scores,
compare verdicts with the committed CLIP results, correlate per-subject effects, and score SigLIP's directions against
the human checks. Reuses q1_primary.py, q2_q3.py and q4_analysis.py unchanged.

Usage: python encoder_sensitivity.py [--check-code]   (needs siglip_scores.csv in every group dir; writes results/encoder_check/)"""
import argparse, glob, json, os, sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "llm_study"))
import q1_primary as q1  # noqa: E402
import q2_q3  # noqa: E402

OUT = os.path.join(q1.REPO, "results", "encoder_check")
LLM = f"{q1.DATA}/llm_study"
Q4 = [("P1 klein 4B: original -> FLUX.2 rewrite", "G08_klein4b", "G08_klein4b__mistral"),
      ("P2 FLUX.2 dev: original -> FLUX.2 rewrite", "G05_flux2_dev", "G05_flux2_dev__mistral")]


def load(score_file):
    fr = []
    for d in sorted(glob.glob(f"{q1.SRC}/G*")) + sorted(glob.glob(f"{LLM}/G*__*")):
        if not os.path.exists(f"{d}/{score_file}"):
            continue
        m = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/{score_file}"), on="job")
        m = m[m.kind == "main"].copy(); m["group"] = os.path.basename(d)
        fr.append(m[["group", "subject", "k"] + q1.ASPECTS + ["inout"]])
    return pd.concat(fr, ignore_index=True)


def tests(D, sc, contrasts, paired, seed):
    rng, rows, per = np.random.default_rng(seed), [], {}
    for name, ga, gb in contrasts:
        subs, cats, A, B = q1.arrays(D, ga, gb)
        d, lr = q1.effects(A, B, sc)
        bd, bl = q1.hier_boot(cats, A, B, sc, rng) if paired else q2_q3.boot_unpaired(cats, A, B, sc, rng, q1.NBOOT)
        per[name] = (d, lr)
        for j, asp in enumerate(q1.ASPECTS):
            for eff, est, rep in [("location", np.median(d[:, j]), bd[:, j]), ("spread", np.median(lr[:, j]), bl[:, j])]:
                rows.append(dict(contrast=name, aspect=asp, effect=eff, estimate=est, lo90=np.percentile(rep, 5),
                                 hi90=np.percentile(rep, 95), p=q1.pval(rep[:, None])[0]))
    T = pd.DataFrame(rows)
    T["p_holm"] = q1.holm(T.p); T["significant"] = T.p_holm < q1.ALPHA
    T["verdict"] = [q1.verdict_loc(r.estimate, r.lo90, r.hi90, r.significant) if r.effect == "location"
                    else q1.verdict_spr(r.estimate, r.lo90, r.hi90, r.significant) for r in T.itertuples()]
    return T, per


def human_agreement():
    """SigLIP's direction against the human answers of rounds 1-3 (five frozen aspects, large-gap pairs)."""
    rows = []
    for rnd, path in [("round 1", "annotation_study"), ("round 2", "annotation_round2"), ("round 3", "annotation_round3")]:
        p = os.path.join(q1.REPO, "results", path, "pair_answers.csv")
        if not os.path.exists(p):
            continue
        P = pd.read_csv(p)
        P = P[P.aspect.isin(q1.ASPECTS) & (P.kind == "large")]
        for r in P.itertuples():
            sl, sr = SIG.get(r.left), SIG.get(r.right)
            if sl is None or sr is None:
                continue
            sig_dir = "right" if sr[r.aspect] > sl[r.aspect] else "left"
            for ann in ("A", "B", "C"):
                ans = getattr(r, ann, None)
                if isinstance(ans, str):
                    rows.append(dict(round=rnd, aspect=r.aspect, answer=ans, clip=r.clip_dir, siglip=sig_dir))
    H = pd.DataFrame(rows)
    out = []
    for (rnd, asp), g in H.groupby(["round", "aspect"]):
        dec = g[g.answer != "none"]
        out.append(dict(round=rnd, aspect=asp, n=len(g), cant_tell=1 - len(dec) / len(g),
                        agree_clip=(dec.answer == dec.clip).mean(), agree_siglip=(dec.answer == dec.siglip).mean(),
                        clip_siglip_same_direction=(g.clip == g.siglip).mean()))
    return pd.DataFrame(out)


SIG = {}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check-code", action="store_true"); a = ap.parse_args()
    C, S = load("clip_scores.csv"), load("siglip_scores.csv")
    opens = [os.path.basename(d) for d in sorted(glob.glob(f"{q1.SRC}/G*"))]
    sc_clip = {k: json.load(open(q1.SCALE_FILE, encoding="utf-8"))["scale"][k] for k in q1.ASPECTS}
    sc_sig, _ = q1.scale(S[S.group.isin(opens)], True)
    # image id as used in the annotation files: <group with "-" for rewrites>__<job>
    for d in sorted(glob.glob(f"{q1.SRC}/G*")) + sorted(glob.glob(f"{LLM}/G*__*")):
        if os.path.exists(f"{d}/siglip_scores.csv"):
            g = os.path.basename(d).replace("__", "-")
            for r in pd.read_csv(f"{d}/siglip_scores.csv").to_dict("records"):
                SIG[f"{g}__{r['job']}"] = r
    families = [("Q1", q1.PAIRS, True, q1.SEED), ("Q3", [q2_q3.Q3_PRIMARY], False, q2_q3.SEED3), ("Q4", Q4, True, 20261015)]
    allrows, corr = [], []
    for fam, contrasts, paired, seed in families:
        Tc, pc = tests(C, sc_clip, contrasts, paired, seed)
        Ts, ps = tests(S, sc_sig, contrasts, paired, seed)
        M = Tc.merge(Ts, on=["contrast", "aspect", "effect"], suffixes=("_clip", "_siglip"))
        M.insert(0, "family", fam); allrows.append(M)
        for name in pc:
            for j, asp in enumerate(q1.ASPECTS):
                corr.append(dict(family=fam, contrast=name, aspect=asp,
                                 spearman_delta=spearmanr(pc[name][0][:, j], ps[name][0][:, j])[0],
                                 spearman_lr=spearmanr(pc[name][1][:, j], ps[name][1][:, j])[0]))
    V = pd.concat(allrows)
    if a.check_code:
        print("check-code:", V.shape, len(corr), "rows; nothing written"); return
    os.makedirs(OUT, exist_ok=True)
    V.to_csv(f"{OUT}/verdicts.csv", index=False, float_format="%.4f")
    pd.DataFrame(corr).to_csv(f"{OUT}/per_subject_correlation.csv", index=False, float_format="%.3f")
    H = human_agreement(); H.to_csv(f"{OUT}/human_agreement.csv", index=False, float_format="%.3f")
    json.dump(dict(scale_siglip=sc_sig, scale_clip=sc_clip, run=pd.Timestamp.now().isoformat(timespec="seconds")),
              open(f"{OUT}/run.json", "w"), indent=1)
    show = V[["family", "contrast", "aspect", "effect", "estimate_clip", "verdict_clip", "estimate_siglip", "verdict_siglip"]]
    print(show.to_string(index=False))
    print(pd.DataFrame(corr).groupby("family")[["spearman_delta", "spearman_lr"]].median())
    print(H.to_string(index=False))


if __name__ == "__main__":
    main()
