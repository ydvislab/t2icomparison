"""Analyse the human aspect check. Usage: python3 analyze.py aspects_A.csv aspects_B.csv
Per aspect: on large-gap pairs, how often people agree with CLIP's direction (among pairs they did not mark "can't tell"),
how often they could not tell, and agreement between the two annotators (Cohen's kappa over left/right/none).
An aspect is flagged unreliable if CLIP agreement < 0.75 or "can't tell" > 40% on large-gap pairs.
Writes results/annotation/aspect_check.csv."""
import json, os, sys
import pandas as pd
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../results/annotation")
P = json.load(open(os.path.join(DATA_ROOT, "annotation_aspects/pairs.json")))
truth = pd.DataFrame(P["pairs"]).rename(columns={"clip": "clip_dir"}).set_index("pid")


def kappa(a, b):
    cats = ["left", "right", "none"]
    po = (a == b).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main(files):
    os.makedirs(OUT, exist_ok=True)
    d = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    d = d.join(truth[["kind", "clip_dir", "gap"]], on="pid")
    rows = []
    for a, g in d.groupby("aspect"):
        L = g[g.kind == "large"]
        decided = L[L.answer != "none"]
        r = dict(aspect=a, cn=P["aspects"][a]["cn"], poles=f"{P['aspects'][a]['lcn']} ↔ {P['aspects'][a]['rcn']}",
                 large_n=len(L), agree_clip=round((decided.answer == decided.clip_dir).mean(), 3) if len(decided) else None,
                 cant_tell=round((L.answer == "none").mean(), 3),
                 small_cant_tell=round((g[g.kind == "small"].answer == "none").mean(), 3))
        ann = g.annotator.unique()
        if len(ann) >= 2:
            w = g.pivot_table(index="pid", columns="annotator", values="answer", aggfunc="first").dropna()
            r["kappa"] = round(kappa(w[ann[0]], w[ann[1]]), 3)
        r["reliable"] = bool(r["agree_clip"] is not None and r["agree_clip"] >= .75 and r["cant_tell"] <= .4)
        rows.append(r)
    t = pd.DataFrame(rows).sort_values("agree_clip")
    t.to_csv(f"{OUT}/aspect_check.csv", index=False)
    print(t.to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1:])
