"""Q1 primary analysis: does raising guidance displace or concentrate appearance? (docs/RESEARCH_PROPOSAL.md §3, §5)

Follows frozen_margins.json and frozen_aspects.json (frozen 2026-10-12, before any contrast was examined). The
operational details below are not spelled out in those files; they are fixed here, committed BEFORE the final run,
and must not be changed after seeing the results (any change is a documented deviation):

  Contrasts   klein-base 4B: G07 (CFG 1) -> G06 (CFG 4); Qwen-Image-2512: G10 (true CFG 1) -> G09 (true CFG 4).
  Aspects     sat, medium, shot, tone, bg (frozen_aspects.json). Main prompts only (24 subjects).
  Effects     per subject: Delta = (median_B - median_A) / s_aspect; lr = log(IQR_B / IQR_A). The primary statistics
              are the medians of Delta and of lr over subjects (2 families x 5 aspects x 2 effects = 20 tests).
  Scale       s_aspect as defined in frozen_margins.json, from all 12 open configurations; computed on the first full
              run and written to frozen_scale.json; later runs load it and never recompute.
  Bootstrap   10,000 replicates, seed 20261013. Each replicate resamples subjects with replacement within each of the
              6 categories (4 per category), then, for every drawn subject, resamples its 32 seeds with replacement;
              the same seed indices are used for A and B (both members of each pair share the checkpoint, so seeds are
              paired) and for all aspects (whole image score vectors). Quantiles use linear interpolation (numpy
              default, as in the audit tool).
  Interval    90% percentile interval of the replicate medians.
  p value     two-sided bootstrap p for H0: effect = 0, p = min(1, 2 * min(P(rep <= 0), P(rep >= 0))), at least 1/B.
  Correction  Holm over the 20 tests, alpha = 0.05.
  Verdicts    location: "same place" if the 90% interval lies within (-0.5, 0.5) [frozen equivalence rule];
              otherwise "displaced" if Holm-significant and |median Delta| >= 0.5; otherwise "shift below margin" if
              Holm-significant; otherwise "inconclusive".
              spread: "same spread" if the 90% interval of lr lies within (-log 1.5, log 1.5); otherwise
              "concentrated" / "widened" if Holm-significant and |median lr| >= log 1.5 (sign decides); otherwise
              "change below margin" if Holm-significant; otherwise "inconclusive".
  Exploratory (not tested, not corrected): per-subject effects with a per-subject 90% seed-bootstrap interval
              (2,000 replicates), and leave-one-category-out medians.

Usage: python q1_primary.py                 (requires all 12 configurations scored; writes results/q1/)
       python q1_primary.py --check-code    (runs on whatever is scored, prints only shapes and timings, writes nothing,
                                             so the code can be tested without looking at any effect)
"""
import argparse, glob, json, math, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
from prompts import EXCLUDED, MAIN  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
SRC = f"{DATA}/model_study/open"
OUT = os.path.join(REPO, "results", "q1")
FM = json.load(open(os.path.join(HERE, "frozen_margins.json"), encoding="utf-8"))
FA = json.load(open(os.path.join(HERE, "frozen_aspects.json"), encoding="utf-8"))
SCALE_FILE = os.path.join(HERE, "frozen_scale.json")
ASPECTS = list(FA["retained"])
PAIRS = [("klein-base 4B", "G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"),
         ("Qwen-Image-2512", "G10_qwen_image_cfg1", "G09_qwen_image_cfg4")]
M_LOC, M_LR = FM["location_effect"]["displacement_margin"], math.log(1.5)
NBOOT, SEED, NSUB_BOOT, ALPHA = 10_000, 20261013, 2_000, 0.05
ALL_GROUPS = 12


def load():
    fr = []
    for d in sorted(glob.glob(f"{SRC}/G*")):
        if not os.path.exists(f"{d}/clip_scores.csv"):
            continue
        m = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/clip_scores.csv"), on="job")
        m = m[m.kind == "main"].copy()
        m["group"] = os.path.basename(d)
        fr.append(m)
    return pd.concat(fr, ignore_index=True)


def scale(D, check):
    """s_aspect per frozen_margins.json; frozen on the first full run."""
    if os.path.exists(SCALE_FILE) and not check:
        S = json.load(open(SCALE_FILE, encoding="utf-8"))
        return {a: S["scale"][a] for a in ASPECTS}, S
    groups = sorted(D.group.unique())
    if len(groups) != ALL_GROUPS and not check:
        sys.exit(f"only {len(groups)} of {ALL_GROUPS} configurations are scored; the scale needs all 12")
    sc = {}
    for a in ASPECTS + ["inout"]:
        v = [x[a].var(ddof=1) for (g, s), x in D.groupby(["group", "subject"]) if a not in EXCLUDED.get(s, ())]
        sc[a] = float(math.sqrt(np.mean(v)))
    S = dict(frozen=pd.Timestamp.now().isoformat(timespec="seconds"), groups=groups, n_images=int(len(D)),
             definition=FM["location_effect"]["s_aspect"], scale=sc)
    if not check:
        json.dump(S, open(SCALE_FILE, "w", encoding="utf-8"), indent=1)
    return {a: sc[a] for a in ASPECTS}, S


def arrays(D, ga, gb):
    """Per subject: score arrays (n_seeds x n_aspects) of A and B, aligned by seed index k."""
    subs, cats, A, B = [], [], [], []
    for cat, s in MAIN:
        xa = D[(D.group == ga) & (D.subject == s)].sort_values("k")
        xb = D[(D.group == gb) & (D.subject == s)].sort_values("k")
        assert list(xa.k) == list(xb.k), f"seeds not paired for {s}"
        subs.append(s); cats.append(cat); A.append(xa[ASPECTS].to_numpy()); B.append(xb[ASPECTS].to_numpy())
    return subs, np.array(cats), np.stack(A), np.stack(B)          # (n_subj, n_seed, n_asp)


def effects(A, B, sc):
    """Per subject Delta and lr for every aspect; A, B: (..., n_seed, n_asp)."""
    s = np.array([sc[a] for a in ASPECTS])
    q = lambda X, p: np.percentile(X, p, axis=-2)
    d = (q(B, 50) - q(A, 50)) / s
    lr = np.log((q(B, 75) - q(B, 25)) / (q(A, 75) - q(A, 25)))
    return d, lr                                                    # (..., n_asp)


def hier_boot(cats, A, B, sc, rng):
    """Replicate medians over subjects of Delta and lr: (NBOOT, n_asp) each."""
    n_subj, n_seed, _ = A.shape
    idx_cat = [np.where(cats == c)[0] for c in pd.unique(cats)]
    bd, bl = np.empty((NBOOT, len(ASPECTS))), np.empty((NBOOT, len(ASPECTS)))
    chunk = 500
    for start in range(0, NBOOT, chunk):
        n = min(chunk, NBOOT - start)
        subj = np.concatenate([rng.choice(ic, size=(n, len(ic)), replace=True) for ic in idx_cat], axis=1)  # (n, n_subj)
        seeds = rng.integers(0, n_seed, size=(n, subj.shape[1], n_seed))
        Ab = A[subj[..., None], seeds]                              # (n, n_subj, n_seed, n_asp)
        Bb = B[subj[..., None], seeds]
        d, lr = effects(Ab, Bb, sc)
        bd[start:start + n], bl[start:start + n] = np.median(d, axis=1), np.median(lr, axis=1)
    return bd, bl


def pval(rep):
    return np.maximum(1 / len(rep), np.minimum(1, 2 * np.minimum((rep <= 0).mean(0), (rep >= 0).mean(0))))


def holm(p):
    p = np.asarray(p); o = np.argsort(p); m = len(p); adj = np.empty(m); run = 0
    for r, i in enumerate(o):
        run = max(run, (m - r) * p[i]); adj[i] = min(1, run)
    return adj


def verdict_loc(est, lo, hi, sig):
    if lo > -M_LOC and hi < M_LOC: return "same place"
    if sig and abs(est) >= M_LOC: return "displaced"
    return "shift below margin" if sig else "inconclusive"


def verdict_spr(est, lo, hi, sig):
    if lo > -M_LR and hi < M_LR: return "same spread"
    if sig and abs(est) >= M_LR: return "concentrated" if est < 0 else "widened"
    return "change below margin" if sig else "inconclusive"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check-code", action="store_true"); a = ap.parse_args()
    t0 = time.time(); D = load(); sc, S = scale(D, a.check_code)
    rng = np.random.default_rng(SEED)
    rows, per_subject, loco = [], [], []
    for fam, ga, gb in PAIRS:
        subs, cats, A, B = arrays(D, ga, gb)
        d, lr = effects(A, B, sc)                                   # (n_subj, n_asp)
        bd, bl = hier_boot(cats, A, B, sc, rng)
        for j, asp in enumerate(ASPECTS):
            for eff, est, rep in [("location", np.median(d[:, j]), bd[:, j]), ("spread", np.median(lr[:, j]), bl[:, j])]:
                rows.append(dict(family=fam, A=ga, B=gb, aspect=asp, effect=eff, estimate=est,
                                 lo90=np.percentile(rep, 5), hi90=np.percentile(rep, 95), p=pval(rep[:, None])[0]))
        # exploratory: per-subject seed bootstrap and leave-one-category-out
        r2 = np.random.default_rng(SEED + 1)
        for i, s in enumerate(subs):
            seeds = r2.integers(0, A.shape[1], size=(NSUB_BOOT, A.shape[1]))
            dd, ll = effects(A[i][seeds], B[i][seeds], sc)
            for j, asp in enumerate(ASPECTS):
                per_subject.append(dict(family=fam, subject=s, category=cats[i], aspect=asp, delta=d[i, j],
                                        delta_lo90=np.percentile(dd[:, j], 5), delta_hi90=np.percentile(dd[:, j], 95),
                                        lr=lr[i, j], lr_lo90=np.percentile(ll[:, j], 5), lr_hi90=np.percentile(ll[:, j], 95)))
        for c in pd.unique(cats):
            keep = cats != c
            for j, asp in enumerate(ASPECTS):
                loco.append(dict(family=fam, left_out=c, aspect=asp, delta=np.median(d[keep, j]), lr=np.median(lr[keep, j])))
    T = pd.DataFrame(rows)
    T["p_holm"] = holm(T.p)
    T["significant"] = T.p_holm < ALPHA
    T["verdict"] = [verdict_loc(r.estimate, r.lo90, r.hi90, r.significant) if r.effect == "location"
                    else verdict_spr(r.estimate, r.lo90, r.hi90, r.significant) for r in T.itertuples()]
    T["ratio"] = np.where(T.effect == "spread", np.exp(T.estimate), np.nan)
    if a.check_code:
        print(f"check-code: {len(D)} images from {D.group.nunique()} groups; table {T.shape}, per-subject "
              f"{len(per_subject)} rows, loco {len(loco)} rows; {time.time() - t0:.0f}s. No effects printed, nothing written.")
        return
    os.makedirs(OUT, exist_ok=True)
    T.to_csv(f"{OUT}/primary.csv", index=False, float_format="%.4f")
    pd.DataFrame(per_subject).to_csv(f"{OUT}/per_subject.csv", index=False, float_format="%.4f")
    pd.DataFrame(loco).to_csv(f"{OUT}/leave_one_category_out.csv", index=False, float_format="%.4f")
    json.dump(dict(run=pd.Timestamp.now().isoformat(timespec="seconds"), scale=S, n_boot=NBOOT, seed=SEED),
              open(f"{OUT}/run.json", "w", encoding="utf-8"), indent=1)
    show = T.copy()
    show["estimate"] = [f"{e:+.2f}" if f == "location" else f"x{math.exp(e):.2f}" for e, f in zip(show.estimate, show.effect)]
    show["90% interval"] = [f"[{l:+.2f}, {h:+.2f}]" if f == "location" else f"[x{math.exp(l):.2f}, x{math.exp(h):.2f}]"
                            for l, h, f in zip(show.lo90, show.hi90, show.effect)]
    print(show[["family", "aspect", "effect", "estimate", "90% interval", "p_holm", "verdict"]].to_string(index=False))
    print(f"\n{time.time() - t0:.0f}s; written to {OUT}")


if __name__ == "__main__":
    main()
