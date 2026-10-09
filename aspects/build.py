"""Aspect measurement: CLIP ViT-L/14 image embeddings and 15 bipolar aspect scores for every base image.

(This was the data step of the earlier prototype 2; its interface is no longer used.)
Writes $T2IC_DATA/proto2/: data.js, emb.npz (normalised CLIP image embeddings),
img/t (thumbnails), img/f (detail), img/avg (pixel averages per group x prompt).
"""
import json, os, sys
import numpy as np, pandas as pd, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aspects import ASPECTS  # noqa: E402
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

CLIP = os.path.join(DATA_ROOT, "models/clip-vit-large-patch14")
OUT = os.path.join(DATA_ROOT, "proto2")
HOL = os.path.join(DATA_ROOT, "hidden_or_lost")
CD = os.path.join(DATA_ROOT, "caption_density")
DATASETS = {
    "models": dict(name="模型比较（极简 prompt，每个 16 个种子）",
                   groups=[("sd15", "SD1.5 (2022)"), ("sdxl_turbo", "SDXL-Turbo (2023)"), ("klein4b", "FLUX.2 klein (2026)")],
                   root=HOL, key="model"),
    "conditions": dict(name="条件比较（同一模型家族的不同设置，每个 8 个种子）",
                       groups=[("klein_min", "klein 蒸馏版"), ("kbase_cfg1_min", "klein-base CFG 1"), ("kbase_cfg4_min", "klein-base CFG 4"),
                               ("klein_dense", "klein · caption 式写法"), ("klein_open", "klein · '任何风格'"),
                               ("kbase_cfg1_dense", "klein-base CFG 1 · caption 式"), ("sd15_cfg1_min", "SD1.5 CFG 1"),
                               ("sd15_cfg75_min", "SD1.5 CFG 7.5"), ("sd15_cfg75_dense", "SD1.5 7.5 · caption 式"),
                               ("sd15_cfg75_open", "SD1.5 7.5 · '任何风格'")],
                       root=CD, key="condition"),
}


def records():
    rows = []
    for ds, cfg in DATASETS.items():
        for g, _ in cfg["groups"]:
            M = pd.read_csv(f"{cfg['root']}/{g}/meta.csv")
            for r in M[M.probe == "base"].itertuples():
                rows.append(dict(id=f"{ds}__{g}__{r.job}", ds=ds, group=g, prompt=r.subject, seed=int(r.seed),
                                 path=f"{cfg['root']}/{g}/{r.job}.png"))
    return pd.DataFrame(rows)


@torch.no_grad()
def main():
    D = records()
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = CLIPModel.from_pretrained(CLIP).to(dev).eval()
    proc = CLIPProcessor.from_pretrained(CLIP)
    embs = []
    for i in range(0, len(D), 32):
        ims = [Image.open(p).convert("RGB") for p in D.path[i:i + 32]]
        x = proc(images=ims, return_tensors="pt").to(dev)
        e = model.get_image_features(**x)
        e = getattr(e, "pooler_output", e)  # transformers 5 returns an output object
        embs.append(torch.nn.functional.normalize(e, dim=-1).cpu().numpy())
        print(f"embed {i + len(ims)}/{len(D)}", flush=True)
    E = np.concatenate(embs)

    def text(t):
        x = proc(text=t, return_tensors="pt", padding=True).to(dev)
        e = model.get_text_features(**x)
        return torch.nn.functional.normalize(getattr(e, "pooler_output", e), dim=-1).cpu().numpy()

    scores = {}
    for a in ASPECTS:
        L, R = text([a["left"]])[0], text([a["right"]])[0]
        scores[a["key"]] = np.round(E @ R - E @ L, 4)
    os.makedirs(OUT, exist_ok=True)
    np.savez(f"{OUT}/emb.npz", ids=D.id.values, emb=E)
    for sub in ("t", "f", "avg"):
        os.makedirs(f"{OUT}/img/{sub}", exist_ok=True)
    for r in D.itertuples():
        t, f = f"{OUT}/img/t/{r.id}.jpg", f"{OUT}/img/f/{r.id}.jpg"
        if not (os.path.exists(t) and os.path.exists(f)):
            im = Image.open(r.path).convert("RGB")
            im.resize((384, 384), Image.LANCZOS).save(f, "JPEG", quality=90)
            im.resize((96, 96), Image.LANCZOS).save(t, "JPEG", quality=85)
    for (ds, g, p), sub in D.groupby(["ds", "group", "prompt"]):
        arr = np.stack([np.asarray(Image.open(x).convert("RGB").resize((192, 192)), dtype=np.float32) for x in sub.path])
        Image.fromarray(arr.mean(0).astype(np.uint8)).save(f"{OUT}/img/avg/{ds}__{g}__{p.replace(' ', '_')}.jpg", quality=90)
    imgs = []
    for k, r in enumerate(D.itertuples()):
        imgs.append(dict(id=r.id, ds=r.ds, group=r.group, prompt=r.prompt, seed=r.seed,
                         s={a["key"]: float(scores[a["key"]][k]) for a in ASPECTS}))
    meta = dict(datasets={k: dict(name=v["name"], groups=[dict(key=g, name=n) for g, n in v["groups"]],
                                  prompts=sorted(D[D.ds == k].prompt.unique().tolist())) for k, v in DATASETS.items()},
                aspects=ASPECTS)
    with open(f"{OUT}/data.js", "w", encoding="utf-8") as fh:
        fh.write("const META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
        fh.write("const IMGS = " + json.dumps(imgs, ensure_ascii=False) + ";\n")
    print(f"{OUT}: {len(D)} images, {len(ASPECTS)} aspects")


if __name__ == "__main__":
    main()
