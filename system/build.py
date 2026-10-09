"""Build the comparison system (prototype 3) data: 13 groups (3 models + 10 generation conditions) on the 6 prompts they share.

Reuses the CLIP embeddings and aspect scores written by ../aspects/build.py ($T2IC_DATA/proto2/{emb.npz,data.js}) and adds a joint 2-D
image map per prompt (t-SNE over the CLIP embeddings of all 13 groups, so positions are shared by all groups).
Run with a Python that has scikit-learn (the system python3 here):  python3 build.py
Writes $T2IC_DATA/proto3/{index.html, d3.min.js, data.js, emb.npz -> ../proto2/emb.npz, img -> ../proto2/img}.
Serve that folder with any static server, e.g. `python3 -m http.server 8771 --bind 127.0.0.1`.
"""
import importlib.util, json, os, re, shutil
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.manifold import TSNE
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(DATA_ROOT, "proto2")
ROOT = {"models": os.path.join(DATA_ROOT, "hidden_or_lost"), "conditions": os.path.join(DATA_ROOT, "caption_density")}
CKPT = {"sd15": "SD 1.5", "sdxl-turbo": "SDXL-Turbo", "FLUX.2-klein-4B": "FLUX.2 klein 4B（蒸馏）",
        "FLUX.2-klein-base-4B": "FLUX.2 klein base 4B"}
STYLE = {"minimal": "极简（只写主题）", "dense": "caption 式", "open": "\"任何风格\"式"}
OUT = os.path.join(DATA_ROOT, "proto3")
GROUPS = [  # (dataset, group key in prototype 2, label, family, seeds)
    ("models", "sd15", "SD1.5", "SD", 16),
    ("models", "sdxl_turbo", "SDXL-Turbo", "SDXL", 16),
    ("models", "klein4b", "klein", "FLUX.2", 16),
    ("conditions", "klein_min", "klein·极简", "FLUX.2", 8),
    ("conditions", "klein_dense", "klein·caption 式", "FLUX.2", 8),
    ("conditions", "klein_open", "klein·任何风格", "FLUX.2", 8),
    ("conditions", "kbase_cfg1_min", "base CFG1·极简", "FLUX.2", 8),
    ("conditions", "kbase_cfg1_dense", "base CFG1·caption 式", "FLUX.2", 8),
    ("conditions", "kbase_cfg4_min", "base CFG4·极简", "FLUX.2", 8),
    ("conditions", "sd15_cfg1_min", "SD1.5 CFG1·极简", "SD", 8),
    ("conditions", "sd15_cfg75_min", "SD1.5 CFG7.5·极简", "SD", 8),
    ("conditions", "sd15_cfg75_dense", "SD1.5·caption 式", "SD", 8),
    ("conditions", "sd15_cfg75_open", "SD1.5·任何风格", "SD", 8),
]


def load_js(path):
    txt = open(path, encoding="utf-8").read()
    meta = json.loads(re.search(r"const META = (.*?);\n", txt, re.S).group(1))
    imgs = json.loads(re.search(r"const IMGS = (.*?);\n", txt, re.S).group(1))
    return meta, imgs


def load_config(name):
    spec = importlib.util.spec_from_file_location(f"{name}_config", os.path.join(HERE, "..", "experiments", name, "config.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def settings(ds, g):
    """Generation settings of one group, read from the generation configs (not from the label)."""
    if ds == "models":
        G = load_config("hidden_or_lost").GENERATORS[g]
        return dict(ckpt=CKPT[os.path.basename(G["path"])], steps=G["steps"], cfg=G["cfg"], size=G["size"], style=STYLE["minimal"])
    cfg = load_config("caption_density")
    _, path, steps, guidance, style = cfg.CONDITIONS[g]
    return dict(ckpt=CKPT[os.path.basename(path)], steps=steps, cfg=guidance, size=cfg.SIZE, style=STYLE[style])


def find_reused(imgs, paths):
    """Pixel-identical images within a prompt (the same generation reused by two groups).
    The first group in GROUPS order keeps the image; later copies get dupOf = id of the kept image."""
    order = {f"{ds[0]}:{g}": i for i, (ds, g, *_) in enumerate(GROUPS)}
    for p in sorted({d["prompt"] for d in imgs}):
        its = sorted([d for d in imgs if d["prompt"] == p], key=lambda d: order[d["g"]])
        seen = {}
        for d in its:
            a = np.asarray(Image.open(paths[d["id"]]).convert("RGB"))
            key = (a.shape, a[::64, ::64].tobytes())
            for other_id, other in seen.get(key, []):
                if np.array_equal(a, other):
                    d["dupOf"] = other_id
                    break
            else:
                seen.setdefault(key, []).append((d["id"], a))


def main():
    meta2, imgs2 = load_js(f"{P2}/data.js")
    z = np.load(f"{P2}/emb.npz", allow_pickle=True)
    E = dict(zip(z["ids"], z["emb"]))
    shared = sorted(set(meta2["datasets"]["conditions"]["prompts"]) & set(meta2["datasets"]["models"]["prompts"]))
    gid = {(ds, g): f"{ds[0]}:{g}" for ds, g, *_ in GROUPS}
    gen, paths = {}, {}  # actual generation prompt text and source file of every image
    for ds, g, *_ in GROUPS:
        M = pd.read_csv(f"{ROOT[ds]}/{g}/meta.csv")
        for r in M[M.probe == "base"].itertuples():
            gen[f"{ds}__{g}__{r.job}"] = r.prompt
            paths[f"{ds}__{g}__{r.job}"] = f"{ROOT[ds]}/{g}/{r.job}.png"
    imgs = [dict(id=d["id"], g=gid[(d["ds"], d["group"])], prompt=d["prompt"], gp=gen[d["id"]], seed=d["seed"], s=d["s"])
            for d in imgs2 if (d["ds"], d["group"]) in gid and d["prompt"] in shared]
    find_reused(imgs, paths)
    for p in shared:  # joint layout per prompt: every group shares the same coordinates
        idx = [i for i, d in enumerate(imgs) if d["prompt"] == p]
        X = np.stack([E[imgs[i]["id"]] for i in idx])
        Y = TSNE(n_components=2, perplexity=15, metric="cosine", init="pca", random_state=0).fit_transform(X)
        Y = (Y - Y.min(0)) / (Y.max(0) - Y.min(0))
        for i, (x, y) in zip(idx, Y):
            imgs[i]["x"], imgs[i]["y"] = round(float(x), 4), round(float(y), 4)
    meta = dict(prompts=shared, aspects=meta2["aspects"],
                groups=[dict(key=gid[(ds, g)], name=n, family=f, seeds=s, ds=ds, **settings(ds, g)) for ds, g, n, f, s in GROUPS])
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/data.js", "w", encoding="utf-8") as fh:
        fh.write("const META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
        fh.write("const IMGS = " + json.dumps(imgs, ensure_ascii=False) + ";\n")
    for name in ("img", "emb.npz"):
        if not os.path.lexists(f"{OUT}/{name}"):
            os.symlink(f"../proto2/{name}", f"{OUT}/{name}")
    for f in ("index.html", "d3.min.js"):
        shutil.copy(os.path.join(HERE, f), f"{OUT}/{f}")
    reused = [d for d in imgs if "dupOf" in d]
    print(f"{OUT}: {len(imgs)} images, {len(GROUPS)} groups, prompts {shared}")
    print(f"pixel-identical reused images: {len(reused)}", sorted({(d['prompt'], d['g']) for d in reused}))


if __name__ == "__main__":
    main()
