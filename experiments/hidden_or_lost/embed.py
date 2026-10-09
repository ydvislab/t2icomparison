"""DINOv2 embeddings + Vendi score per (model, subject) on base images. Usage: python embed.py <model_key>"""
import os, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel
from config import DATA
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

DINO = os.path.join(DATA_ROOT, "models/dinov2-base")
key = sys.argv[1]
d = f"{DATA}/{key}"
meta = pd.read_csv(f"{d}/meta.csv")
proc = AutoImageProcessor.from_pretrained(DINO)
net = AutoModel.from_pretrained(DINO).to("mps").eval()
embs = {}
for i in range(0, len(meta), 16):
    chunk = meta.iloc[i:i + 16]
    ims = [Image.open(f"{d}/{j}.png").convert("RGB") for j in chunk.job]
    with torch.no_grad():
        out = net(**proc(images=ims, return_tensors="pt").to("mps"))
    e = torch.nn.functional.normalize(out.last_hidden_state[:, 0].float(), dim=-1).cpu().numpy()
    embs.update(dict(zip(chunk.job, e)))
np.savez(f"{d}/dino_cls.npz", jobs=np.array(list(embs)), emb=np.stack(list(embs.values())))


def vendi(X):
    K = X @ X.T / len(X)
    w = np.clip(np.linalg.eigvalsh(K), 1e-12, None)
    return float(np.exp(-(w * np.log(w)).sum()))


rows = []
base = meta[meta.probe == "base"]
for s, g in base.groupby("subject"):
    X = np.stack([embs[j] for j in g.job])
    rows.append(dict(model=key, subject=s, n=len(X), vendi=vendi(X),
                     mean_pairwise_dist=float(1 - (X @ X.T)[np.triu_indices(len(X), 1)].mean())))
pd.DataFrame(rows).to_csv(f"{d}/diversity.csv", index=False)
print(pd.DataFrame(rows).round(3).to_string(index=False))
