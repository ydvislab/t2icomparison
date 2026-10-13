"""Q2 (descriptive structure) and Q3 (distillation package case), pre-registered in frozen_q2q3.json.

Inherits the definitions of q1_primary.py (Delta, log IQR ratio, frozen scale, margins, verdict rules, Holm, bootstrap p)
and adds only what frozen_q2q3.json specifies. Committed before the run on the study data; any later change is a
documented deviation.

Usage: python q2_q3.py                 (requires all 12 configurations scored and frozen_scale.json; writes results/q2/, results/q3/)
       python q2_q3.py --check-code    (prints only shapes and timings, writes nothing; for testing without looking at effects)
       python q2_q3.py --nboot-scale 0.05   (testing only: scales every replicate count down)
"""
import argparse, itertools, json, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q1_primary as q1  # noqa: E402

FQ = json.load(open(os.path.join(HERE, "frozen_q2q3.json"), encoding="utf-8"))
ASPECTS, M_LOC, M_LR = q1.ASPECTS, q1.M_LOC, q1.M_LR
Q3_PRIMARY = ("klein 4B package", "G07_klein_base4b_cfg1", "G08_klein4b")
Q3_DESCRIPTIVE = [("klein 9B package", "G11_klein_base9b", "G12_klein9b"),
                  ("SDXL -> Turbo", "G02_sdxl", "G03_sdxl_turbo")]
Q2_CONFIGS = FQ["Q2"]["configurations"]
N3, N2, NSUB, SEED3, SEED2 = 10_000, 2_000, 2_000, 20261014, 20261015


def subject_arrays(D, g):
    """(n_subj, n_seed, n_asp) scores of configuration g, subjects in prompts.MAIN order, seeds by k."""
    out = []
    for _, s in q1.MAIN:
        x = D[(D.group == g) & (D.subject == s)].sort_values("k")
        out.append(x[ASPECTS].to_numpy())
    return np.stack(out)


def med_iqr(X):
    """Median and IQR over the seed axis (-2)."""
    p = np.percentile(X, [25, 50, 75], axis=-2)
    return p[1], p[2] - p[0]


def boot_unpaired(cats, A, B, sc, rng, n):
    """Replicate medians over subjects of Delta and lr with A and B seeds resampled independently: (n, n_asp) each."""
    s = np.array([sc[a] for a in ASPECTS])
    idx = [np.where(cats == c)[0] for c in pd.unique(cats)]
    bd, bl = np.empty((n, len(ASPECTS))), np.empty((n, len(ASPECTS)))
    for start in range(0, n, 500):
        m = min(500, n - start)
        subj = np.concatenate([rng.choice(ic, size=(m, len(ic))) for ic in idx], axis=1)
        sa = rng.integers(0, A.shape[1], size=(m, subj.shape[1], A.shape[1]))
        sb = rng.integers(0, B.shape[1], size=(m, subj.shape[1], B.shape[1]))
        ma, ia = med_iqr(A[subj[..., None], sa]); mb, ib = med_iqr(B[subj[..., None], sb])
        bd[start:start + m] = np.median((mb - ma) / s, axis=1)
        bl[start:start + m] = np.median(np.log(ib / ia), axis=1)
    return bd, bl


def subject_delta_ci(A, B, sc, rng, n):
    """Per-subject Delta point estimate and 90% seed-bootstrap interval (A and B resampled independently)."""
    s = np.array([sc[a] for a in ASPECTS])
    ma, _ = med_iqr(A); mb, _ = med_iqr(B)
    d = (mb - ma) / s
    lo, hi = np.empty_like(d), np.empty_like(d)
    for i in range(A.shape[0]):
        sa = rng.integers(0, A.shape[1], size=(n, A.shape[1])); sb = rng.integers(0, B.shape[1], size=(n, B.shape[1]))
        bm_a, _ = med_iqr(A[i][sa]); bm_b, _ = med_iqr(B[i][sb])
        r = (bm_b - bm_a) / s
        lo[i], hi[i] = np.percentile(r, 5, axis=0), np.percentile(r, 95, axis=0)
    return d, lo, hi


def opposite_counts(d, lo, hi, pooled):
    """Subjects shifted >= 0.5 against the pooled direction (interval excluding 0), and both-way counts."""
    up = (d >= M_LOC) & (lo > 0)
    down = (d <= -M_LOC) & (hi < 0)
    against = np.where(pooled >= 0, down.sum(0), up.sum(0))
    return up.sum(0), down.sum(0), against


def label_interval(lo, hi, margin, same):
    if lo > -margin and hi < margin: return same
    if lo >= margin or hi <= -margin: return "beyond margin"
    return "unresolved"


def run_q3(D, cats, sc, nscale, out_rows):
    rng = np.random.default_rng(SEED3)
    prim, desc, rev = [], [], []
    for name, ga, gb in [Q3_PRIMARY] + Q3_DESCRIPTIVE:
        A, B = subject_arrays(D, ga), subject_arrays(D, gb)
        d, lr = q1.effects(A, B, sc)
        bd, bl = boot_unpaired(cats, A, B, sc, rng, max(200, int(N3 * nscale)))
        sd, slo, shi = subject_delta_ci(A, B, sc, rng, max(100, int(NSUB * nscale)))
        for j, asp in enumerate(ASPECTS):
            for eff, est, rep in [("location", np.median(d[:, j]), bd[:, j]), ("spread", np.median(lr[:, j]), bl[:, j])]:
                r = dict(contrast=name, A=ga, B=gb, aspect=asp, effect=eff, estimate=est,
                         lo90=np.percentile(rep, 5), hi90=np.percentile(rep, 95))
                if name == Q3_PRIMARY[0]:
                    r["p"] = q1.pval(rep[:, None])[0]; prim.append(r)
                else:
                    m = M_LOC if eff == "location" else M_LR
                    r["label"] = label_interval(r["lo90"], r["hi90"], m, "same place" if eff == "location" else "same spread")
                    desc.append(r)
        pooled = np.median(d, axis=0)
        up, down, against = opposite_counts(sd, slo, shi, pooled)
        for j, asp in enumerate(ASPECTS):
            rev.append(dict(contrast=name, A=ga, B=gb, aspect=asp, pooled_delta=pooled[j], subjects_up=int(up[j]),
                            subjects_down=int(down[j]), subjects_against_pooled=int(against[j]),
                            hides_opposite_shifts=bool(abs(pooled[j]) < M_LOC and up[j] >= 3 and down[j] >= 3)))
    P = pd.DataFrame(prim)
    P["p_holm"] = q1.holm(P.p); P["significant"] = P.p_holm < q1.ALPHA
    P["verdict"] = [q1.verdict_loc(r.estimate, r.lo90, r.hi90, r.significant) if r.effect == "location"
                    else q1.verdict_spr(r.estimate, r.lo90, r.hi90, r.significant) for r in P.itertuples()]
    out_rows.update(q3_primary=P, q3_packages=pd.DataFrame(desc), q3_reversals=pd.DataFrame(rev))


def run_q2(D, cats, sc, nscale, out_rows):
    rng = np.random.default_rng(SEED2)
    s = np.array([sc[a] for a in ASPECTS])
    X = {g: subject_arrays(D, g) for g in Q2_CONFIGS}
    med = np.stack([med_iqr(X[g])[0] for g in Q2_CONFIGS], axis=1)          # (n_subj, n_cfg, n_asp)
    iqr = np.stack([med_iqr(X[g])[1] for g in Q2_CONFIGS], axis=1)
    centre = np.median(med, axis=1, keepdims=True)
    L = (med - centre) / s
    # hierarchical bootstrap: one subject draw per replicate shared by all configurations; seeds per configuration
    n = max(200, int(N2 * nscale))
    idx = [np.where(cats == c)[0] for c in pd.unique(cats)]
    bL, bW = np.empty((n, len(Q2_CONFIGS), len(ASPECTS))), np.empty((n, len(Q2_CONFIGS), len(ASPECTS)))
    bP = np.empty((n, len(Q2_CONFIGS), len(Q2_CONFIGS), len(ASPECTS)))
    for start in range(0, n, 100):
        m = min(100, n - start)
        subj = np.concatenate([rng.choice(ic, size=(m, len(ic))) for ic in idx], axis=1)
        ms, qs = [], []
        for g in Q2_CONFIGS:
            sd = rng.integers(0, X[g].shape[1], size=(m, subj.shape[1], X[g].shape[1]))
            a, b = med_iqr(X[g][subj[..., None], sd]); ms.append(a); qs.append(b)
        ms, qs = np.stack(ms, axis=2), np.stack(qs, axis=2)                  # (m, n_subj, n_cfg, n_asp)
        Lb = (ms - np.median(ms, axis=2, keepdims=True)) / s
        bL[start:start + m] = np.median(Lb, axis=1)
        bW[start:start + m] = np.median(qs / s, axis=1)
        bP[start:start + m] = np.median((ms[:, :, None] - ms[:, :, :, None]) / s, axis=1)   # [i, j] = j - i
    loc = []
    for k, g in enumerate(Q2_CONFIGS):
        for j, asp in enumerate(ASPECTS):
            loc.append(dict(config=g, aspect=asp, location=np.median(L[:, k, j]), loc_lo90=np.percentile(bL[:, k, j], 5),
                            loc_hi90=np.percentile(bL[:, k, j], 95), spread=np.median(iqr[:, k, j] / s[j]),
                            spread_lo90=np.percentile(bW[:, k, j], 5), spread_hi90=np.percentile(bW[:, k, j], 95)))
    pw, hid = [], []
    for (i, ga), (k, gb) in itertools.combinations(enumerate(Q2_CONFIGS), 2):
        d = (med[:, k] - med[:, i]) / s
        sd, slo, shi = subject_delta_ci(X[ga], X[gb], sc, rng, max(100, int(NSUB * nscale)))
        pooled = np.median(d, axis=0)
        up, down, _ = opposite_counts(sd, slo, shi, pooled)
        for j, asp in enumerate(ASPECTS):
            lo, hi = np.percentile(bP[:, i, k, j], 5), np.percentile(bP[:, i, k, j], 95)
            pw.append(dict(A=ga, B=gb, aspect=asp, delta=pooled[j], lo90=lo, hi90=hi,
                           label=label_interval(lo, hi, M_LOC, "same place")))
            hid.append(dict(A=ga, B=gb, aspect=asp, pooled_delta=pooled[j], subjects_up=int(up[j]), subjects_down=int(down[j]),
                            hides_opposite_shifts=bool(abs(pooled[j]) < M_LOC and up[j] >= 3 and down[j] >= 3)))
    # subject-dependent defaults: per-subject seed bootstrap of L with the centre held fixed
    sdd = []
    for k, g in enumerate(Q2_CONFIGS):
        nb = max(100, int(NSUB * nscale))
        lo, hi = np.empty((L.shape[0], len(ASPECTS))), np.empty((L.shape[0], len(ASPECTS)))
        for i in range(L.shape[0]):
            sd = rng.integers(0, X[g].shape[1], size=(nb, X[g].shape[1]))
            r = (med_iqr(X[g][i][sd])[0] - centre[i, 0]) / s
            lo[i], hi[i] = np.percentile(r, 5, axis=0), np.percentile(r, 95, axis=0)
        hi_side = ((L[:, k] >= M_LOC) & (lo > 0)).sum(0); lo_side = ((L[:, k] <= -M_LOC) & (hi < 0)).sum(0)
        for j, asp in enumerate(ASPECTS):
            sdd.append(dict(config=g, aspect=asp, subjects_right=int(hi_side[j]), subjects_left=int(lo_side[j]),
                            subject_dependent=bool(hi_side[j] >= 3 and lo_side[j] >= 3)))
    out_rows.update(q2_locations=pd.DataFrame(loc), q2_pairwise=pd.DataFrame(pw),
                    q2_hidden_opposite=pd.DataFrame(hid), q2_subject_dependent=pd.DataFrame(sdd))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-code", action="store_true")
    ap.add_argument("--nboot-scale", type=float, default=1.0)
    a = ap.parse_args()
    t0 = time.time()
    D = q1.load()
    if not os.path.exists(q1.SCALE_FILE):
        sys.exit("frozen_scale.json is missing: it is written by q1_primary.py on its first full run and never recomputed")
    sc = {k: json.load(open(q1.SCALE_FILE, encoding="utf-8"))["scale"][k] for k in ASPECTS}
    need = set(Q2_CONFIGS) | {g for _, x, y in [Q3_PRIMARY] + Q3_DESCRIPTIVE for g in (x, y)}
    missing = need - set(D.group.unique())
    if missing:
        sys.exit(f"not scored yet: {sorted(missing)}")
    cats = np.array([c for c, _ in q1.MAIN])
    res = {}
    run_q3(D, cats, sc, a.nboot_scale, res)
    run_q2(D, cats, sc, a.nboot_scale, res)
    if a.check_code:
        print("check-code:", {k: v.shape for k, v in res.items()}, f"{time.time() - t0:.0f}s. No effects printed, nothing written.")
        return
    for k, v in res.items():
        q, name = k.split("_", 1)
        os.makedirs(os.path.join(q1.REPO, "results", q), exist_ok=True)
        v.to_csv(os.path.join(q1.REPO, "results", q, f"{name}.csv"), index=False, float_format="%.4f")
    for q in ("q2", "q3"):
        json.dump(dict(run=pd.Timestamp.now().isoformat(timespec="seconds"), frozen=FQ["frozen"], nboot_scale=a.nboot_scale,
                       scale=sc), open(os.path.join(q1.REPO, "results", q, "run.json"), "w", encoding="utf-8"), indent=1)
    print(res["q3_primary"][["aspect", "effect", "estimate", "lo90", "hi90", "p_holm", "verdict"]].to_string(index=False))
    print(f"\n{time.time() - t0:.0f}s; written to results/q2/ and results/q3/")


if __name__ == "__main__":
    main()
