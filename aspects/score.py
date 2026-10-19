"""Score generated images on the 15 bipolar aspects with CLIP ViT-L/14.

Usage: python score.py <group dir> [<group dir> ...] [--force]
Each group dir holds <job>.png and meta.csv (as written by experiments/model_study/open/gen.py). Writes, per dir,
clip_scores.csv (job + one column per aspect key) and clip_emb.npz (job ids and L2-normalised image embeddings).
Score = cosine similarity to the right-pole text minus cosine similarity to the left-pole text (aspects.py).
Every image is resized to 512x512 before the CLIP processor. This equalizes the encoder input only; content differences
that come with the native generation resolution (512-1328 px) remain and are part of each configuration.
"""
import argparse, os, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aspects import ASPECTS  # noqa: E402

DATA_ROOT = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
CLIP = os.path.join(DATA_ROOT, "models", "clip-vit-large-patch14")
SIDE = 512


def device():
    if torch.cuda.is_available():
        return "cuda"
    return "mps" if torch.backends.mps.is_available() else "cpu"


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    dev = device()
    model = CLIPModel.from_pretrained(CLIP).to(dev).eval()
    proc = CLIPProcessor.from_pretrained(CLIP)

    def text(t):
        e = model.get_text_features(**proc(text=t, return_tensors="pt", padding=True).to(dev))
        return torch.nn.functional.normalize(getattr(e, "pooler_output", e), dim=-1).cpu().numpy()

    Lt, Rt = text([x["left"] for x in ASPECTS]), text([x["right"] for x in ASPECTS])
    for d in a.dirs:
        meta = pd.read_csv(f"{d}/meta.csv")
        out = f"{d}/clip_scores.csv"
        if os.path.exists(out) and not a.force and set(pd.read_csv(out).job) >= set(meta.job):
            print(d, "up to date")
            continue
        embs = []
        for i in range(0, len(meta), 32):
            ims = [Image.open(f"{d}/{j}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS) for j in meta.job[i:i + 32]]
            e = model.get_image_features(**proc(images=ims, return_tensors="pt").to(dev))
            embs.append(torch.nn.functional.normalize(getattr(e, "pooler_output", e), dim=-1).cpu().numpy())
        E = np.concatenate(embs)
        S = pd.DataFrame(np.round(E @ Rt.T - E @ Lt.T, 5), columns=[x["key"] for x in ASPECTS])
        S.insert(0, "job", meta.job.values)
        S.to_csv(out, index=False)
        np.savez(f"{d}/clip_emb.npz", job=meta.job.values, emb=E)
        print(d, len(S), "images scored")


if __name__ == "__main__":
    main()
