"""Q4 analysis: does LLM prompt rewriting displace or concentrate appearance defaults? (PREREG.md)
Reuses q1_primary.py unchanged (frozen scale, margins, aspects, hierarchical bootstrap, p values, Holm, verdicts);
bootstrap seed 20261015. Committed before any rewritten image was scored.

Primary (20 tests, Holm): P1 klein 4B original -> mistral rewrite; P2 FLUX.2 dev original -> mistral rewrite.
Descriptive (intervals, no p): D1 klein 4B original -> qwen; D2 klein 4B mistral -> qwen;
D3a klein 4B original -> mistral_fixed; D3b mistral_fixed -> mistral.
All contrasts share the checkpoint and the seeds, so seeds are paired. Per subject: Delta and lr with a 2,000-replicate
seed-bootstrap interval; a subject counts as shifted up/down when |Delta| >= 0.5 and its interval excludes 0 (Q3 rule);
a contrast hides opposite shifts on an aspect when the pooled shift is within the margin and >= 3 subjects shift each way.

Usage: python q4_analysis.py [--check-code]   (writes results/q4/)"""
import argparse, glob, json, math, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "analysis"))
import q1_primary as q1  # noqa: E402

SEED = 20261015
OUT = os.path.join(q1.REPO, "results", "q4")
LLM = f"{q1.DATA}/llm_study"
PRIMARY = [("P1 klein 4B: original -> FLUX.2 rewrite", "G08_klein4b", "G08_klein4b__mistral"),
           ("P2 FLUX.2 dev: original -> FLUX.2 rewrite", "G05_flux2_dev", "G05_flux2_dev__mistral")]
DESCRIPTIVE = [("D1 klein 4B: original -> Qwen rewrite", "G08_klein4b", "G08_klein4b__qwen"),
               ("D2 klein 4B: FLUX.2 rewrite -> Qwen rewrite", "G08_klein4b__mistral", "G08_klein4b__qwen"),
               ("D3a klein 4B: original -> fixed rewrite", "G08_klein4b", "G08_klein4b__mistral_fixed"),
               ("D3b klein 4B: fixed rewrite -> per-seed rewrite", "G08_klein4b__mistral_fixed", "G08_klein4b__mistral")]


def load():
    fr = []
    for d in sorted(glob.glob(f"{q1.SRC}/G05_*") + glob.glob(f"{q1.SRC}/G08_*") + glob.glob(f"{LLM}/G*__*")):
        if not os.path.exists(f"{d}/clip_scores.csv"):
            continue
        m = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/clip_scores.csv"), on="job")
        m = m[m.kind == "main"].copy()
        m["group"] = os.path.basename(d)
        fr.append(m[["group", "subject", "k"] + q1.ASPECTS])
    return pd.concat(fr, ignore_index=True)


def run(D, sc, contrasts, rng, tested):
    rows, per_subject = [], []
    for name, ga, gb in contrasts:
        if not ({ga, gb} <= set(D.group)):
            print("missing", name)
            continue
        subs, cats, A, B = q1.arrays(D, ga, gb)
        d, lr = q1.effects(A, B, sc)
        bd, bl = q1.hier_boot(cats, A, B, sc, rng)
        r2 = np.random.default_rng(SEED + 1)
        ps = []
        for i, s in enumerate(subs):
            seeds = r2.integers(0, A.shape[1], size=(q1.NSUB_BOOT, A.shape[1]))
            dd, ll = q1.effects(A[i][seeds], B[i][seeds], sc)
            for j, asp in enumerate(q1.ASPECTS):
                ps.append(dict(contrast=name, subject=s, category=cats[i], aspect=asp, delta=d[i, j],
                               delta_lo90=np.percentile(dd[:, j], 5), delta_hi90=np.percentile(dd[:, j], 95),
                               lr=lr[i, j], lr_lo90=np.percentile(ll[:, j], 5), lr_hi90=np.percentile(ll[:, j], 95)))
        ps = pd.DataFrame(ps)
        up = (ps.delta >= q1.M_LOC) & (ps.delta_lo90 > 0)
        down = (ps.delta <= -q1.M_LOC) & (ps.delta_hi90 < 0)
        per_subject.append(ps.assign(up=up, down=down))
        for j, asp in enumerate(q1.ASPECTS):
            nu, nd = int(up[ps.aspect == asp].sum()), int(down[ps.aspect == asp].sum())
            for eff, est, rep in [("location", np.median(d[:, j]), bd[:, j]), ("spread", np.median(lr[:, j]), bl[:, j])]:
                rows.append(dict(contrast=name, A=ga, B=gb, aspect=asp, effect=eff, estimate=est,
                                 lo90=np.percentile(rep, 5), hi90=np.percentile(rep, 95),
                                 p=q1.pval(rep[:, None])[0] if tested else np.nan, subjects_up=nu, subjects_down=nd))
    return pd.DataFrame(rows), (pd.concat(per_subject) if per_subject else pd.DataFrame())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check-code", action="store_true"); a = ap.parse_args()
    t0 = time.time()
    D = load()
    sc, S = q1.scale(D, False)
    rng = np.random.default_rng(SEED)
    T, PS = run(D, sc, PRIMARY, rng, True)
    T["p_holm"] = q1.holm(T.p) if len(T) else []
    T["significant"] = T.p_holm < q1.ALPHA
    T["verdict"] = [q1.verdict_loc(r.estimate, r.lo90, r.hi90, r.significant) if r.effect == "location"
                    else q1.verdict_spr(r.estimate, r.lo90, r.hi90, r.significant) for r in T.itertuples()]
    Dd, PSd = run(D, sc, DESCRIPTIVE, rng, False)
    if a.check_code:
        print(f"check-code: {len(D)} images, groups {sorted(D.group.unique())}; primary {T.shape}, descriptive "
              f"{Dd.shape}; {time.time() - t0:.0f}s. No effects printed, nothing written.")
        return
    os.makedirs(OUT, exist_ok=True)
    for t in (T, Dd):
        if len(t):
            t["ratio"] = np.where(t.effect == "spread", np.exp(t.estimate), np.nan)
            t["hides_opposite"] = (t.effect == "location") & (t.estimate.abs() < q1.M_LOC) & \
                                  (t.subjects_up >= 3) & (t.subjects_down >= 3)
    T.to_csv(f"{OUT}/primary.csv", index=False, float_format="%.4f")
    Dd.to_csv(f"{OUT}/descriptive.csv", index=False, float_format="%.4f")
    pd.concat([PS, PSd]).to_csv(f"{OUT}/per_subject.csv", index=False, float_format="%.4f")
    json.dump(dict(run=pd.Timestamp.now().isoformat(timespec="seconds"), scale=S["frozen"], n_boot=q1.NBOOT, seed=SEED),
              open(f"{OUT}/run.json", "w", encoding="utf-8"), indent=1)
    for t in (T, Dd):
        show = t.copy()
        show["est"] = [f"{e:+.2f}" if f == "location" else f"x{math.exp(e):.2f}" for e, f in zip(show.estimate, show.effect)]
        show["90%"] = [f"[{l:+.2f}, {h:+.2f}]" if f == "location" else f"[x{math.exp(l):.2f}, x{math.exp(h):.2f}]"
                       for l, h, f in zip(show.lo90, show.hi90, show.effect)]
        cols = ["contrast", "aspect", "effect", "est", "90%", "subjects_up", "subjects_down"]
        cols += ["p_holm", "verdict"] if "verdict" in show else []
        print(show[cols].to_string(index=False), "\n")
    print(f"{time.time() - t0:.0f}s; written to {OUT}")


if __name__ == "__main__":
    main()
