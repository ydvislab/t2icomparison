"""Human reading of the VLM grids (deviation 4, PREREG.md): people answer the same constrained questions on the same
grid pairs the VLMs saw, so VLM answers can be compared with people reading the same 8-vs-8 images.

Design (fixed before the package is built; seed 20261024):
- Items: 48. For each of the six Q5 contrasts, 6 subject-level items on aspects validated for both sides (and with a
  decided 32-seed truth in results/q5/truth.csv): 3 shift questions (one with truth "none" when available, the others
  random) and 3 variety questions (random). For each null contrast (klein 4B vs itself, SDXL vs itself; B seeds shifted
  by 16), 3 shift and 3 variety items on random subject x aspect cells. No subject x aspect cell is used twice within
  a contrast.
- Stimulus: exactly the first-draw grids of vlm_describe.py (seeds k = 0..7, 4 x 2 tiles of 256 px; B shifted by 16 in
  the null contrasts), shown as set A above set B.
- Questions: the VLMs' constrained questions in Chinese with the English poles; the three options in a random order per
  item (the same for every annotator).
- Annotators: the three annotators of rounds 1-3, independently. Answers are stored in canonical form
  (right/left/none, more/less/same).
Usage: python make_grid_check.py   (writes $T2IC_DATA/grid_check/ and $T2IC_DATA/grid_check_package.zip)"""
import json, os, random, sys, zipfile
import pandas as pd
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "model_study"))
sys.path.insert(0, os.path.join(REPO, "aspects"))
from prompts import MAIN  # noqa: E402
from aspects import ASPECTS  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
OPEN, LLM = f"{DATA}/model_study/open", f"{DATA}/llm_study"
OUT = f"{DATA}/grid_check"
CONTRASTS = {"guid_klein": (f"{OPEN}/G07_klein_base4b_cfg1", f"{OPEN}/G06_klein_base4b_cfg4", 0),
             "guid_qwen": (f"{OPEN}/G10_qwen_image_cfg1", f"{OPEN}/G09_qwen_image_cfg4", 0),
             "pkg_klein4b": (f"{OPEN}/G07_klein_base4b_cfg1", f"{OPEN}/G08_klein4b", 0),
             "sdxl_turbo": (f"{OPEN}/G02_sdxl", f"{OPEN}/G03_sdxl_turbo", 0),
             "rw_klein": (f"{OPEN}/G08_klein4b", f"{LLM}/G08_klein4b__mistral", 0),
             "rw_flux": (f"{OPEN}/G05_flux2_dev", f"{LLM}/G05_flux2_dev__mistral", 0)}
NULLS = {"null_klein4b": (f"{OPEN}/G08_klein4b", f"{OPEN}/G08_klein4b", 16), "null_sdxl": (f"{OPEN}/G02_sdxl", f"{OPEN}/G02_sdxl", 16)}
KEEP = ["sat", "medium", "shot", "tone", "bg"]
P = {x["key"]: x for x in ASPECTS}
TILE = 256


def grid(paths):
    g = Image.new("RGB", (4 * TILE, 2 * TILE), "white")
    for n, p in enumerate(paths):
        g.paste(Image.open(p).convert("RGB").resize((TILE, TILE), Image.LANCZOS), ((n % 4) * TILE, (n // 4) * TILE))
    return g


def main():
    rnd = random.Random(20261024)
    T = pd.read_csv(os.path.join(REPO, "results", "q5", "truth.csv"), keep_default_na=False)
    T = T[(T.level == "subject") & (T.validated.astype(str) == "True")]
    items = []
    for c in CONTRASTS:
        t = T[T.contrast == c]
        sh, va = t[t["shift"] != ""], t[t["variety"] != ""]
        used, pick = set(), []
        none_rows = sh[sh["shift"] == "none"]
        order = (list(none_rows.sample(frac=1, random_state=rnd.randrange(10**6)).itertuples())[:1]
                 + list(sh.sample(frac=1, random_state=rnd.randrange(10**6)).itertuples()))
        for r in order:
            if len([p for p in pick if p[1] == "shift"]) == 3: break
            if (r.unit, r.aspect) not in used: used.add((r.unit, r.aspect)); pick.append((r, "shift"))
        for r in va.sample(frac=1, random_state=rnd.randrange(10**6)).itertuples():
            if len([p for p in pick if p[1] == "variety"]) == 3: break
            if (r.unit, r.aspect) not in used: used.add((r.unit, r.aspect)); pick.append((r, "variety"))
        for r, q in pick:
            items.append(dict(contrast=c, unit=r.unit, aspect=r.aspect, question=q, truth32=getattr(r, "shift") if q == "shift" else r.variety))
    for c in NULLS:
        cells = [(f"s{i:02d}", a) for i in range(len(MAIN)) for a in KEEP]
        rnd.shuffle(cells)
        for k, (u, a) in enumerate(cells[:6]):
            items.append(dict(contrast=c, unit=u, aspect=a, question="shift" if k < 3 else "variety", truth32="none" if k < 3 else "same"))
    rnd.shuffle(items)
    os.makedirs(f"{OUT}/img", exist_ok=True)
    for n, it in enumerate(items):
        A, B, off = {**CONTRASTS, **NULLS}[it["contrast"]]
        i = int(it["unit"][1:])
        jobs = [f"m{i:02d}_{k:02d}" for k in range(8)]
        jobs_b = [f"m{i:02d}_{(k + off) % 32:02d}" for k in range(8)]
        it["id"] = f"g{n:02d}"
        it["subject"] = MAIN[i][1]
        grid([f"{A}/{j}.png" for j in jobs]).save(f"{OUT}/img/{it['id']}_A.jpg", quality=85)
        grid([f"{B}/{j}.png" for j in jobs_b]).save(f"{OUT}/img/{it['id']}_B.jpg", quality=85)
        p = P[it["aspect"]]
        if it["question"] == "shift":
            canon = [("right", f"更接近「{p['rcn']}」（{p['right']}）"), ("left", f"更接近「{p['lcn']}」（{p['left']}）"), ("none", "没有明显差别")]
            it["q"] = f"比较两组图的【{p['cn']}】：整体来看，B 组相比 A 组："
        else:
            canon = [("more", "更多样（组内差异更大）"), ("less", "更单一（组内差异更小）"), ("same", "差不多")]
            it["q"] = f"比较两组图各自组内在【{p['cn']}】（从「{p['lcn']}」到「{p['rcn']}」）上的差异程度：B 组相比 A 组："
        r2 = random.Random(f"grid|{it['id']}")
        r2.shuffle(canon)
        it["options"] = canon
    json.dump(items, open(f"{OUT}/items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    page = open(os.path.join(HERE, "grid_check_template.html"), encoding="utf-8").read()
    pub = [{k: it[k] for k in ("id", "subject", "q", "options")} for it in items]   # no contrast or truth on the page
    page = page.replace("/*ITEMS*/[]", json.dumps(pub, ensure_ascii=False))
    open(f"{OUT}/grid_check.html", "w", encoding="utf-8").write(page)
    z = f"{DATA}/grid_check_package.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        f.write(f"{OUT}/grid_check.html", "grid_check.html")
        for fn in sorted(os.listdir(f"{OUT}/img")):
            f.write(f"{OUT}/img/{fn}", f"img/{fn}")
    print(len(items), "items;", z, f"{os.path.getsize(z) / 1e6:.1f} MB")
    print(pd.DataFrame(items).groupby(["contrast", "question"]).truth32.value_counts().to_string())


if __name__ == "__main__":
    main()
