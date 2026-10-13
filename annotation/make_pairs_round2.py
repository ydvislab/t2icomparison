"""Human check, round 2 (annotation/PROTOCOL.md §5b): do the 5 frozen aspects also hold on the configurations that were
not in round 1?

Design (fixed before the package is built):
- Images: only the configurations absent from round 1, i.e. G04 SD3.5 Large, G05 FLUX.2 dev, G09/G10 Qwen-Image-2512
  (true CFG 4 / 1), G11 klein-base 9B and G12 klein 9B; main prompts only.
- Aspects: the 5 frozen aspects (experiments/model_study/analysis/frozen_aspects.json): sat, medium, shot, tone, bg.
- Per aspect 24 pairs, one per subject (all 24 subjects), both images of a pair from the same subject. Gap tiers by the
  rank of the CLIP score within that subject's pool of round-2 images: 12 "large" (one image from the bottom 15%, one from
  the top 15%), 8 "medium" (one from ranks 15-35%, one from 65-85%) and 4 "small" (both from the middle 40%). Tiers are
  assigned to subjects so that every category gets 2 large pairs per aspect.
- 120 pairs in total; no image is used twice; left/right order and question order randomised; CLIP's answer is stored
  but never shown; seed 20261016. Pair ids carry an "r2" tag so they never collide with round-1 answers in the browser.
- Decision rule: the round-1 rule on the large-gap pairs (agreement with CLIP >= 0.75 and "can't tell" <= 0.40); medium
  and small tiers are reported descriptively.

Usage: python make_pairs_round2.py [--zip] [--page-only]
Writes $T2IC_DATA/annotation_round2/{pairs.json, label_aspects.html, img/} and, with --zip,
$T2IC_DATA/annotation_round2_package.zip. Analyse with:
python analyze.py --pairs $T2IC_DATA/annotation_round2/pairs.json aspects_X.csv aspects_Y.csv aspects_Z.csv
(results go to results/annotation_round2/).
"""
import argparse, json, os, random, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_pairs_study as mps  # noqa: E402
from make_pairs_study import ASPECTS, MAIN  # noqa: E402

FROZEN = json.load(open(os.path.join(HERE, "..", "experiments", "model_study", "analysis", "frozen_aspects.json"),
                        encoding="utf-8"))
KEEP = list(FROZEN["retained"])
GROUPS = ["G04_sd35_large", "G05_flux2_dev", "G09_qwen_image_cfg4", "G10_qwen_image_cfg1", "G11_klein_base9b", "G12_klein9b"]
OUT = f"{mps.DATA_ROOT}/annotation_round2"
SEED, SIDE = 20261016, 512
TIERS = ["large"] * 12 + ["medium"] * 8 + ["small"] * 4


def tiers_for_subjects(rnd):
    """Tier per subject: within each category of 4 subjects, 2 large, then medium/small spread over categories."""
    cats = {}
    for c, s in MAIN:
        cats.setdefault(c, []).append(s)
    rest = ["medium"] * 8 + ["small"] * 4
    rnd.shuffle(rest)
    out = {}
    for c in sorted(cats):
        subs = cats[c][:]
        rnd.shuffle(subs)
        out[subs[0]], out[subs[1]] = "large", "large"
        out[subs[2]], out[subs[3]] = rest.pop(), rest.pop()
    return out


def pick(its, kind, rnd):
    n = len(its)
    band = lambda a, b: its.iloc[int(n * a): int(n * b)]
    if kind == "large":
        lo, hi = band(0, .15), band(.85, 1)
    elif kind == "medium":
        lo, hi = band(.15, .35), band(.65, .85)
    else:
        mid = band(.3, .7)
        a, b = rnd.sample(range(len(mid)), 2)
        return sorted([mid.iloc[a], mid.iloc[b]], key=lambda r: r.name)
    return lo.iloc[rnd.randrange(len(lo))], hi.iloc[rnd.randrange(len(hi))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--page-only", action="store_true")
    a = ap.parse_args()
    mps.OUT = OUT                                   # write_page() writes into this round's folder
    asp = {x["key"]: dict(cn=x["cn"], lcn=x["lcn"], rcn=x["rcn"], l=x["left"], r=x["right"]) for x in ASPECTS if x["key"] in KEEP}
    if a.page_only:
        P = json.load(open(f"{OUT}/pairs.json", encoding="utf-8"))
        mps.write_page(P["pairs"], P["aspects"])
    else:
        rnd = random.Random(SEED)
        D = mps.load()
        missing = set(GROUPS) - set(D.group)
        if missing:
            sys.exit(f"not scored yet: {sorted(missing)}")
        D = D[D.group.isin(GROUPS)]
        used, pairs = set(), []
        for k in KEEP:
            tier = tiers_for_subjects(rnd)
            for i, (_, s) in enumerate(MAIN):
                its = D[(D.subject == s) & ~D.id.isin(used)].sort_values(k).reset_index(drop=True)
                lo, hi = pick(its, tier[s], rnd)
                lo, hi = sorted([lo, hi], key=lambda r: r[k])
                used.update([lo.id, hi.id])
                left, right = (lo, hi) if rnd.random() < .5 else (hi, lo)
                pairs.append(dict(pid=f"{k}-r2-{i:02d}", aspect=k, kind=tier[s], prompt=s, left=left.id, right=right.id,
                                  left_group=left.group, right_group=right.group,
                                  clip=("right" if right[k] > left[k] else "left"), gap=round(abs(right[k] - left[k]), 5)))
        rnd.shuffle(pairs)
        os.makedirs(f"{OUT}/img", exist_ok=True)
        for pr in pairs:
            for side in ("left", "right"):
                dst = f"{OUT}/img/{pr[side]}.jpg"
                if not os.path.exists(dst):
                    g, job = pr[side].split("__")
                    Image.open(f"{mps.SRC}/{g}/{job}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS).save(dst, quality=90)
        json.dump(dict(seed=SEED, source="model_study/open", round=2, results_dir="annotation_round2", groups=GROUPS,
                       pairs=pairs, aspects=asp), open(f"{OUT}/pairs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        mps.write_page(pairs, asp)
        print(f"{OUT}: {len(pairs)} pairs from {GROUPS}; {len(os.listdir(f'{OUT}/img'))} images")
    if a.zip:
        z = f"{mps.DATA_ROOT}/annotation_round2_package.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            f.write(f"{OUT}/label_aspects.html", "label_aspects.html")
            f.write(os.path.join(HERE, "ANNOTATOR_GUIDE.md"), "GUIDE_zh.md")
            for fn in sorted(os.listdir(f"{OUT}/img")):
                f.write(f"{OUT}/img/{fn}", f"img/{fn}")
        print(z, f"{os.path.getsize(z) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
