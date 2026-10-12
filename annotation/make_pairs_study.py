"""Human check of the CLIP aspects, round 1 on the study images (owner decision 2026-10-12; replaces the round-1 pairs
drawn from the pilot images, which the paper no longer uses). Same design and decision rule as PROTOCOL.md:
per aspect 12 large-gap pairs (one image from the prompt's top 15% and one from its bottom 15% on that aspect, pooled
over the available groups) and 4 small-gap pairs (both from the middle 40%); 15 aspects x 16 = 240 pairs; left/right
order and question order randomised; CLIP's answer is stored but never shown.

Differences from make_pairs.py: images come from $T2IC_DATA/model_study/open/<group>/ (only groups that have
clip_scores.csv; main prompts only); each aspect's 16 pairs use 16 different subjects spread over the 6 categories;
an aspect is never asked for a subject that implies it (prompts.EXCLUDED, e.g. in/out for "a kitchen"); no image is
used in more than one pair; images are stored as 512 px JPEG.

Usage: python make_pairs_study.py [--zip] [--page-only]
--page-only rebuilds label_aspects.html (and the zip) from the existing pairs.json without resampling, e.g. after a fix
to page_template.html; the pairs and images stay exactly the same.
Writes $T2IC_DATA/annotation_study/{pairs.json, label_aspects.html, img/} and, with --zip,
$T2IC_DATA/annotation_study_package.zip (page, images and the annotator guide) for annotators on their own computers.
Analyse with: python analyze.py --pairs $T2IC_DATA/annotation_study/pairs.json aspects_X.csv aspects_Y.csv
"""
import argparse, glob, json, os, random, sys, zipfile
import pandas as pd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "aspects"))
sys.path.insert(0, os.path.join(HERE, "..", "experiments", "model_study"))
from aspects import ASPECTS  # noqa: E402
from prompts import EXCLUDED, MAIN  # noqa: E402

DATA_ROOT = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
SRC = f"{DATA_ROOT}/model_study/open"
OUT = f"{DATA_ROOT}/annotation_study"
SEED, N_LARGE, N_SMALL, SIDE = 20261012, 12, 4, 512


def load():
    parts = []
    for d in sorted(glob.glob(f"{SRC}/G*")):
        if not os.path.exists(f"{d}/clip_scores.csv"):
            continue
        m = pd.read_csv(f"{d}/meta.csv").merge(pd.read_csv(f"{d}/clip_scores.csv"), on="job")
        m = m[m.kind == "main"].copy()
        m["group"] = os.path.basename(d)
        m["id"] = m.group + "__" + m.job
        parts.append(m)
    if not parts:
        sys.exit(f"no scored groups in {SRC}")
    return pd.concat(parts, ignore_index=True)


def subjects_for(aspect, rnd):
    """16 subjects for one aspect, spread over categories (round robin), skipping prompt-implied aspects."""
    by_cat = {}
    for cat, s in MAIN:
        if aspect not in EXCLUDED.get(s, ()):
            by_cat.setdefault(cat, []).append(s)
    for v in by_cat.values():
        rnd.shuffle(v)
    out, cats = [], sorted(by_cat)
    while len(out) < N_LARGE + N_SMALL and any(by_cat.values()):
        for c in cats:
            if by_cat[c] and len(out) < N_LARGE + N_SMALL:
                out.append(by_cat[c].pop())
    rnd.shuffle(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true")
    ap.add_argument("--page-only", action="store_true")
    a = ap.parse_args()
    if a.page_only:
        P = json.load(open(f"{OUT}/pairs.json", encoding="utf-8"))
        write_page(P["pairs"], P["aspects"])
        if a.zip:
            write_zip()
        return
    rnd = random.Random(SEED)
    D = load()
    used, pairs = set(), []
    for asp in ASPECTS:
        k = asp["key"]
        subs = subjects_for(k, rnd)
        if len(subs) < N_LARGE + N_SMALL:
            sys.exit(f"{k}: only {len(subs)} subjects available")
        for i, s in enumerate(subs):
            its = D[(D.subject == s) & ~D.id.isin(used)].sort_values(k).reset_index(drop=True)
            n = len(its)
            if i < N_LARGE:
                lo = its.iloc[rnd.randrange(int(n * .15))]
                hi = its.iloc[n - 1 - rnd.randrange(int(n * .15))]
                kind = "large"
            else:
                mid = its.iloc[int(n * .3): int(n * .7)]
                lo, hi = sorted([mid.iloc[j] for j in rnd.sample(range(len(mid)), 2)], key=lambda r: r[k])
                kind = "small"
            used.update([lo.id, hi.id])
            left, right = (lo, hi) if rnd.random() < .5 else (hi, lo)
            pairs.append(dict(pid=f"{k}-{i:02d}", aspect=k, kind=kind, prompt=s, left=left.id, right=right.id,
                              left_group=left.group, right_group=right.group,
                              clip=("right" if right[k] > left[k] else "left"), gap=round(abs(right[k] - left[k]), 5)))
    rnd.shuffle(pairs)

    os.makedirs(f"{OUT}/img", exist_ok=True)
    for pr in pairs:
        for side in ("left", "right"):
            dst = f"{OUT}/img/{pr[side]}.jpg"
            if not os.path.exists(dst):
                g, job = pr[side].split("__")
                Image.open(f"{SRC}/{g}/{job}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS).save(dst, quality=90)
    asp = {x["key"]: dict(cn=x["cn"], lcn=x["lcn"], rcn=x["rcn"], l=x["left"], r=x["right"]) for x in ASPECTS}
    groups = sorted(D.group.unique())
    json.dump(dict(seed=SEED, source="model_study/open", groups=groups, pairs=pairs, aspects=asp),
              open(f"{OUT}/pairs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    write_page(pairs, asp)
    print(f"{OUT}: {len(pairs)} pairs from groups {groups}; {len(os.listdir(f'{OUT}/img'))} images")
    if a.zip:
        write_zip()


def write_page(pairs, asp):
    page = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    shown = [{k: v for k, v in p.items() if k in ("pid", "aspect", "prompt", "left", "right")} for p in pairs]
    page = page.replace("/*DATA*/", "const PAIRS = " + json.dumps(shown, ensure_ascii=False)
                        + ";\nconst ASP = " + json.dumps(asp, ensure_ascii=False) + ";")
    open(f"{OUT}/label_aspects.html", "w", encoding="utf-8").write(page)


def write_zip():
    z = f"{DATA_ROOT}/annotation_study_package.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        f.write(f"{OUT}/label_aspects.html", "label_aspects.html")
        f.write(os.path.join(HERE, "ANNOTATOR_GUIDE.md"), "GUIDE_zh.md")
        for fn in sorted(os.listdir(f"{OUT}/img")):
            f.write(f"{OUT}/img/{fn}", f"img/{fn}")
    print(z, f"{os.path.getsize(z) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
