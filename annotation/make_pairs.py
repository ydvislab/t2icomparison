"""Human check of the CLIP aspects used by the comparison system (round 1: the 13 existing groups).
The system only compares aspect scores *within a prompt*, so the check is pairwise and within a prompt:
"which of these two images is more <right pole> (vs <left pole>)?".
Per aspect: 12 large-gap pairs (one image from the prompt's top 15% and one from its bottom 15% on that aspect) test
whether CLIP's direction matches people; 4 small-gap pairs (both from the middle 40%) show how noisy the middle is.
15 aspects x 16 = 240 pairs, left/right order randomised; CLIP's answer is stored but never shown.
Reused (pixel-identical) images are excluded. Writes $T2IC_DATA/annotation_aspects/{pairs.json, label_aspects.html, img/} ($T2IC_DATA defaults to ~/va4ext).
Usage: python3 make_pairs.py"""
import json, os, random, re, shutil
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

SRC = os.path.join(DATA_ROOT, "proto3")
OUT = os.path.join(DATA_ROOT, "annotation_aspects")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED, N_LARGE, N_SMALL = 20261008, 12, 4


def load():
    t = open(f"{SRC}/data.js", encoding="utf-8").read()
    meta = json.loads(re.search(r"const META = (.*?);\n", t, re.S).group(1))
    imgs = json.loads(re.search(r"const IMGS = (.*?);\n", t, re.S).group(1))
    return meta, [d for d in imgs if "dupOf" not in d]


def main():
    rnd = random.Random(SEED)
    meta, imgs = load()
    prompts = meta["prompts"]
    pairs = []
    for a in meta["aspects"]:
        k = a["key"]
        for i in range(N_LARGE + N_SMALL):
            p = prompts[i % len(prompts)]  # spread pairs over the six prompts
            its = sorted([d for d in imgs if d["prompt"] == p], key=lambda d: d["s"][k])
            n = len(its)
            if i < N_LARGE:
                lo, hi = rnd.choice(its[: int(n * .15)]), rnd.choice(its[-int(n * .15):])
                kind = "large"
            else:
                mid = its[int(n * .3): int(n * .7)]
                lo, hi = sorted(rnd.sample(mid, 2), key=lambda d: d["s"][k])
                kind = "small"
            left, right = (lo, hi) if rnd.random() < .5 else (hi, lo)
            pairs.append(dict(pid=f"{k}-{i:02d}", aspect=k, kind=kind, prompt=p, left=left["id"], right=right["id"],
                              clip=("right" if right["s"][k] > left["s"][k] else "left"),
                              gap=round(abs(right["s"][k] - left["s"][k]), 5)))
    rnd.shuffle(pairs)
    os.makedirs(f"{OUT}/img", exist_ok=True)
    for pr in pairs:
        for side in ("left", "right"):
            dst = f"{OUT}/img/{pr[side]}.jpg"
            if not os.path.exists(dst):
                shutil.copy(os.path.realpath(f"{SRC}/img/f/{pr[side]}.jpg"), dst)
    asp = {a["key"]: dict(cn=a["cn"], lcn=a["lcn"], rcn=a["rcn"], l=a["left"], r=a["right"]) for a in meta["aspects"]}
    json.dump(dict(seed=SEED, pairs=pairs, aspects=asp), open(f"{OUT}/pairs.json", "w"), ensure_ascii=False, indent=1)
    page = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    page = page.replace("/*DATA*/", "const PAIRS = " + json.dumps([{k: v for k, v in p.items() if k not in ("clip", "gap", "kind")} for p in pairs], ensure_ascii=False)
                        + ";\nconst ASP = " + json.dumps(asp, ensure_ascii=False) + ";")
    open(f"{OUT}/label_aspects.html", "w", encoding="utf-8").write(page)
    print(f"{OUT}: {len(pairs)} pairs, {len(os.listdir(f'{OUT}/img'))} images")


if __name__ == "__main__":
    main()
