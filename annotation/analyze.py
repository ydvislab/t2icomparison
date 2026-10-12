"""Analyse the human aspect check. Usage: python3 analyze.py [--pairs PAIRS_JSON] aspects_<X>.csv aspects_<Y>.csv
--pairs defaults to $T2IC_DATA/annotation_aspects/pairs.json (pilot-image round); the study-image round 1 uses
$T2IC_DATA/annotation_study/pairs.json (make_pairs_study.py), and its results go to results/annotation_study/.
Per aspect: on large-gap pairs, how often people agree with CLIP's direction (among pairs they did not mark "can't tell",
with a 95% Wilson interval), how often they could not tell, and agreement between the two annotators (Cohen's kappa over
left/right/none; with 3+ annotators the mean pairwise kappa and Fleiss' kappa). An aspect is flagged unreliable if CLIP agreement < 0.75 or "can't tell" > 40% on large-gap pairs
(rule fixed before labelling, see PROTOCOL.md).
Annotators are renamed A, B, ... in file order so the tracked results carry no names.
Writes results/annotation/{aspect_check.csv, pair_answers.csv}."""
import json, math, os, sys
import pandas as pd
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

ARGS = sys.argv[1:]
PAIRS = os.path.join(DATA_ROOT, "annotation_aspects/pairs.json")
if ARGS[:1] == ["--pairs"]:
    PAIRS, ARGS = ARGS[1], ARGS[2:]
P = json.load(open(PAIRS, encoding="utf-8"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../results",
                   "annotation_study" if P.get("source") == "model_study/open" else "annotation")
truth = pd.DataFrame(P["pairs"]).rename(columns={"clip": "clip_dir"}).set_index("pid")


def kappa(a, b):
    cats = ["left", "right", "none"]
    po = (a == b).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def fleiss(w):
    """Fleiss' kappa over left/right/none for a pairs x annotators table of answers."""
    cats = ["left", "right", "none"]
    n = w.shape[1]
    counts = pd.DataFrame({c: (w == c).sum(axis=1) for c in cats})
    p_i = ((counts ** 2).sum(axis=1) - n) / (n * (n - 1))
    p_j = counts.sum() / (len(w) * n)
    pe = (p_j ** 2).sum()
    return (p_i.mean() - pe) / (1 - pe) if pe < 1 else 1.0


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 3), round(c + h, 3)


def main(files):
    os.makedirs(OUT, exist_ok=True)
    parts = []
    for n, f in enumerate(files):
        x = pd.read_csv(f)
        x["annotator"] = chr(ord("A") + n)
        parts.append(x)
    d = pd.concat(parts, ignore_index=True)
    d = d.join(truth[["kind", "clip_dir", "gap"]], on="pid")
    missing = {a: len(truth) - g.pid.nunique() for a, g in d.groupby("annotator")}
    if any(missing.values()):
        print("unanswered pairs per annotator:", missing)
    rows = []
    for a, g in d.groupby("aspect"):
        L = g[g.kind == "large"]
        decided = L[L.answer != "none"]
        k = int((decided.answer == decided.clip_dir).sum())
        lo, hi = wilson(k, len(decided))
        r = dict(aspect=a, cn=P["aspects"][a]["cn"], poles=f"{P['aspects'][a]['lcn']} ↔ {P['aspects'][a]['rcn']}",
                 large_n=len(L), agree_clip=round(k / len(decided), 3) if len(decided) else None, agree_lo=lo, agree_hi=hi,
                 cant_tell=round((L.answer == "none").mean(), 3),
                 small_cant_tell=round((g[g.kind == "small"].answer == "none").mean(), 3))
        ann = sorted(g.annotator.unique())
        if len(ann) >= 2:
            w = g.pivot_table(index="pid", columns="annotator", values="answer", aggfunc="first").dropna()
            ks = [kappa(w[x], w[y]) for i, x in enumerate(ann) for y in ann[i + 1:]]
            r["kappa"] = round(sum(ks) / len(ks), 3)  # mean pairwise Cohen's kappa (= Cohen's kappa for 2 annotators)
            if len(ann) >= 3:
                r["fleiss"] = round(fleiss(w[ann]), 3)
            # per-annotator agreement with CLIP on large-gap pairs, to spot an annotator who differs from the rest
            for x in ann:
                dx = decided[decided.annotator == x]
                r[f"agree_{x}"] = round((dx.answer == dx.clip_dir).mean(), 3) if len(dx) else None
        r["reliable"] = bool(r["agree_clip"] is not None and r["agree_clip"] >= .75 and r["cant_tell"] <= .4)
        rows.append(r)
    t = pd.DataFrame(rows).sort_values("agree_clip")
    t.to_csv(f"{OUT}/aspect_check.csv", index=False)
    # one row per pair: every annotator's answer next to CLIP's, for the review meeting and the paper's error examples
    w = d.pivot_table(index="pid", columns="annotator", values="answer", aggfunc="first")
    pa = truth.join(w).reset_index()
    ans = [c for c in w.columns]
    pa["all_against_clip"] = pa.apply(lambda r: all(r[c] not in (r.clip_dir, "none") for c in ans if pd.notna(r[c])), axis=1)
    pa["annotators_disagree"] = pa[ans].nunique(axis=1) > 1
    pa.sort_values(["aspect", "pid"]).to_csv(f"{OUT}/pair_answers.csv", index=False)
    print(t.to_string(index=False))
    print(f"\npairs where every annotator contradicts CLIP: {int(pa.all_against_clip.sum())}; "
          f"pairs where annotators disagree: {int(pa.annotators_disagree.sum())}")


if __name__ == "__main__":
    main(ARGS)
