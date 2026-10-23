"""Second encoder (sensitivity check, experiments/model_study/analysis/ENCODER_CHECK.md): score images on the frozen
aspects with SigLIP 2 (google/siglip2-so400m-patch14-384) using the same text poles as the CLIP scores.

Usage: python score_siglip.py <group dir> [<group dir> ...] [--force]
Writes siglip_scores.csv (job + one column per frozen aspect and inout) next to clip_scores.csv.
Score = cosine(image, right pole) - cosine(image, left pole), embeddings L2-normalised; text padded to the model's
max length (64), as SigLIP requires; images resized to 512 px first (as in score.py), then by the processor."""
import argparse, json, os, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from aspects import ASPECTS  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
PATH = os.path.join(DATA, "models", "siglip2-so400m-patch14-384")
FA = json.load(open(os.path.join(HERE, "..", "experiments", "model_study", "analysis", "frozen_aspects.json"), encoding="utf-8"))
KEYS = list(FA["retained"]) + ["inout"]
SIDE = 512


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--force", action="store_true"); a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModel.from_pretrained(PATH, dtype=torch.float16 if dev == "cuda" else torch.float32).to(dev).eval()
    proc = AutoProcessor.from_pretrained(PATH)
    poles = [next(x for x in ASPECTS if x["key"] == k) for k in KEYS]

    def text(t):
        inp = proc(text=t, return_tensors="pt", padding="max_length", max_length=64, truncation=True).to(dev)
        f = model.get_text_features(**inp)
        return torch.nn.functional.normalize(getattr(f, "pooler_output", f).float(), dim=-1).cpu().numpy()

    L, R = text([p["left"] for p in poles]), text([p["right"] for p in poles])
    for d in a.dirs:
        meta = pd.read_csv(f"{d}/meta.csv")
        out = f"{d}/siglip_scores.csv"
        if os.path.exists(out) and not a.force and set(pd.read_csv(out).job) >= set(meta.job):
            print(d, "up to date"); continue
        embs = []
        for i in range(0, len(meta), 32):
            ims = [Image.open(f"{d}/{j}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS) for j in meta.job[i:i + 32]]
            inp = proc(images=ims, return_tensors="pt").to(dev)
            f = model.get_image_features(pixel_values=inp["pixel_values"].to(model.dtype))
            embs.append(torch.nn.functional.normalize(getattr(f, "pooler_output", f).float(), dim=-1).cpu().numpy())
        E = np.concatenate(embs)
        S = pd.DataFrame(np.round(E @ R.T - E @ L.T, 5), columns=KEYS)
        S.insert(0, "job", meta.job.values)
        S.to_csv(out, index=False)
        print(d, len(S), "images scored")


if __name__ == "__main__":
    main()
