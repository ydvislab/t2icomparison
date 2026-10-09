"""VLM measurement (Qwen3.5-4B, thinking off, letter-logit constrained choice) of every image of one model:
the five generic dimensions + subject presence. Usage: python label.py <model_key> [--resize 448]"""
import argparse, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd, torch
from PIL import Image
from transformers import AutoModelForImageTextToText, AutoProcessor
from config import DATA, DIMENSIONS, PROBES
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

QWEN = os.path.join(DATA_ROOT, "models/Qwen3.5-4B")
ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("--resize", type=int, default=448)
args = ap.parse_args()
proc = AutoProcessor.from_pretrained(QWEN)
model = AutoModelForImageTextToText.from_pretrained(QWEN, dtype=torch.bfloat16).to("mps").eval()
LET = "ABCDEF"
lid = [proc.tokenizer.encode(l, add_special_tokens=False)[0] for l in LET]


def ask(img, q, opts):
    text = q + "\n" + "\n".join(f"{LET[i]}. {o}" for i, o in enumerate(opts)) + "\nAnswer with the letter only."
    msgs = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": text}]}]
    prompt = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    inp = proc(text=[prompt], images=[img], return_tensors="pt").to("mps")
    with torch.no_grad():
        lg = model(**inp).logits[0, -1].float()
    p = torch.softmax(lg[lid[: len(opts)]], 0).cpu().numpy()
    return int(p.argmax()), p


d = f"{DATA}/{args.model}"
meta = pd.read_csv(f"{d}/meta.csv")
out = f"{d}/labels_qwen.csv"
rows = pd.read_csv(out).to_dict("records") if os.path.exists(out) else []
done = {r["job"] for r in rows}
t0 = time.time()
for n, r in enumerate(meta.itertuples()):
    if r.job in done:
        continue
    img = Image.open(f"{d}/{r.job}.png").convert("RGB").resize((args.resize, args.resize))
    rec = dict(job=r.job)
    # base images: all five dimensions; probe images: only the probed dimension (+ subject presence)
    dims = DIMENSIONS if r.probe == "base" else {PROBES[r.probe][1]: DIMENSIONS[PROBES[r.probe][1]]}
    for dim, (q, opts) in dims.items():
        k, p = ask(img, q, opts)
        rec[dim] = k
        rec[f"{dim}_conf"] = round(float(p.max()), 4)
    k, p = ask(img, f"Does this image show {r.subject}?", ["yes", "no"])
    rec["subject_present"] = int(k == 0)
    rows.append(rec)
    if n % 10 == 0:
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"{args.model} {len(rows)}/{len(meta)} {time.time()-t0:.0f}s", flush=True)
pd.DataFrame(rows).to_csv(out, index=False)
print(args.model, "labelled", len(rows), f"{time.time()-t0:.0f}s")
