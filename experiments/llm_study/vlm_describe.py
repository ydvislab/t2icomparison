"""Q5 and Q6: ask a VLM how two image sets differ (PREREG.md). Resumable.
Usage: python vlm_describe.py qwen|mistral [--contrasts c1,c2] [--levels subject,pooled] [--limit N] [--gpu 0]
Writes $T2IC_DATA/llm_study/q5/<vlm>/{mc.csv, free.csv, proposals.csv}.

Operational details (fixed before any VLM output was collected):
- Every question is a separate single-turn prompt with the same two grid images (set A first, set B second), so an
  answer never depends on an earlier answer.
- Grids: 256 px tiles. Subject level: seeds k = 0..7, 4 x 2. Pooled level: 16 subjects drawn without replacement and
  one seed per subject (numpy default_rng(20261015 + draw)), 4 x 4, the same subjects and seeds for A and B; 5 draws.
- Constrained choice: the three options are shown in a random order (random.Random keyed by the query), the answer
  is the option with the highest letter logit at the first generated position; probabilities are stored in the
  canonical order (right, left, none) / (more, less, same).
- Free text and proposals: greedy decoding, at most 300 new tokens.
- Qwen3.5-4B runs with thinking disabled; Mistral-Small-3.2-24B is the FLUX.2 dev text encoder (a VLM)."""
import argparse, json, os, random, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "aspects"))
from prompts import MAIN  # noqa: E402
from aspects import ASPECTS  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
FA = json.load(open(os.path.join(HERE, "..", "model_study", "analysis", "frozen_aspects.json"), encoding="utf-8"))
POLES = {x["key"]: x for x in ASPECTS if x["key"] in FA["retained"]}
NAMES = dict(sat="colour saturation", medium="medium (photograph or painting/illustration)",
             shot="shot scale (close-up or wide)", tone="colour tone (modern or vintage)",
             bg="background (plain or busy)")
OPEN, LLM = f"{DATA}/model_study/open", f"{DATA}/llm_study"
CONTRASTS = {
    "guid_klein": (f"{OPEN}/G07_klein_base4b_cfg1", f"{OPEN}/G06_klein_base4b_cfg4"),
    "guid_qwen": (f"{OPEN}/G10_qwen_image_cfg1", f"{OPEN}/G09_qwen_image_cfg4"),
    "pkg_klein4b": (f"{OPEN}/G07_klein_base4b_cfg1", f"{OPEN}/G08_klein4b"),
    "sdxl_turbo": (f"{OPEN}/G02_sdxl", f"{OPEN}/G03_sdxl_turbo"),
    "rw_klein": (f"{OPEN}/G08_klein4b", f"{LLM}/G08_klein4b__mistral"),
    "rw_flux": (f"{OPEN}/G05_flux2_dev", f"{LLM}/G05_flux2_dev__mistral"),
}
TILE, NDRAW, MAXNEW = 256, 5, 300

ap = argparse.ArgumentParser()
ap.add_argument("vlm", choices=["qwen", "mistral"])
ap.add_argument("--contrasts", default=",".join(CONTRASTS))
ap.add_argument("--levels", default="subject,pooled")
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--gpu", type=int, default=0)
a = ap.parse_args()
dev = f"cuda:{a.gpu}"
OUT = f"{LLM}/q5/{a.vlm}"
os.makedirs(OUT, exist_ok=True)

if a.vlm == "qwen":
    from transformers import AutoModelForImageTextToText, AutoProcessor
    proc = AutoProcessor.from_pretrained(f"{DATA}/models/Qwen3.5-4B")
    model = AutoModelForImageTextToText.from_pretrained(f"{DATA}/models/Qwen3.5-4B", dtype=torch.bfloat16)
    TPL = dict(enable_thinking=False)
else:
    from transformers import AutoProcessor, Mistral3ForConditionalGeneration
    proc = AutoProcessor.from_pretrained(f"{DATA}/models/FLUX.2-dev/tokenizer")
    model = Mistral3ForConditionalGeneration.from_pretrained(f"{DATA}/models/FLUX.2-dev/text_encoder",
                                                             dtype=torch.bfloat16)
    TPL = {}
model = model.to(dev).eval()
TOK = proc.tokenizer if hasattr(proc, "tokenizer") else proc
LET = [TOK.encode(x, add_special_tokens=False)[0] for x in "ABC"]


def grid(paths, cols):
    rows = (len(paths) + cols - 1) // cols
    g = Image.new("RGB", (cols * TILE, rows * TILE), "white")
    for n, p in enumerate(paths):
        g.paste(Image.open(p).convert("RGB").resize((TILE, TILE), Image.LANCZOS), ((n % cols) * TILE, (n // cols) * TILE))
    return g


def encode(imgs, text):
    msgs = [{"role": "user", "content": [{"type": "image", "image": imgs[0]}, {"type": "image", "image": imgs[1]},
                                         {"type": "text", "text": text}]}]
    inp = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_dict=True,
                                   return_tensors="pt", **TPL)
    return {k: (v.to(dev, torch.bfloat16) if v.is_floating_point() else v.to(dev)) for k, v in inp.items()}


@torch.no_grad()
def choose(imgs, text):
    lg = model(**encode(imgs, text)).logits[0, -1].float()
    return torch.softmax(lg[LET], 0).cpu().numpy()


@torch.no_grad()
def generate(imgs, text):
    inp = encode(imgs, text)
    g = model.generate(**inp, max_new_tokens=MAXNEW, do_sample=False)
    return TOK.decode(g[0, inp["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def intro(level, subject):
    what = (f"8 images generated from the prompt \"{subject}\"" if level == "subject"
            else "16 images, each generated from a different short everyday prompt (the same prompts in both sets)")
    return f"The first picture is a grid of {what} by generator A (set A). The second picture shows the same for generator B (set B).\n"


def units(level):
    if level == "subject":
        for i, (_, s) in enumerate(MAIN):
            yield f"s{i:02d}", s, [f"m{i:02d}_{k:02d}" for k in range(8)], 4
    else:
        for d in range(NDRAW):
            r = np.random.default_rng(20261015 + d)
            subj = r.choice(len(MAIN), 16, replace=False)
            yield f"d{d}", None, [f"m{i:02d}_{int(r.integers(32)):02d}" for i in subj], 4


def load_rows(name):
    p = f"{OUT}/{name}.csv"
    return (pd.read_csv(p).to_dict("records") if os.path.exists(p) else []), p


mc, mc_p = load_rows("mc")
free, free_p = load_rows("free")
prop, prop_p = load_rows("proposals")
done = {(r["contrast"], r["level"], r["unit"], r["aspect"], r["question"]) for r in mc}
done_free = {(r["contrast"], r["level"], r["unit"]) for r in free}
done_prop = {(r["contrast"], r["unit"]) for r in prop}
t0, n = time.time(), 0
for c in a.contrasts.split(","):
    A, B = CONTRASTS[c]
    if not (os.path.exists(f"{B}/meta.csv") and os.path.exists(f"{A}/meta.csv")):
        print("skip", c, "(images missing)", flush=True)
        continue
    for level in a.levels.split(","):
        for unit, subject, jobs, cols in units(level):
            imgs = [grid([f"{A}/{j}.png" for j in jobs], cols), grid([f"{B}/{j}.png" for j in jobs], cols)]
            head = intro(level, subject)
            for asp, P in POLES.items():
                for q in ("shift", "variety"):
                    if (c, level, unit, asp, q) in done:
                        continue
                    if q == "shift":
                        canon = [f"closer to \"{P['right']}\"", f"closer to \"{P['left']}\"", "no clear difference"]
                        stem = f"Compare the two sets in {NAMES[asp]}. Compared with set A, the images of set B are overall:"
                    else:
                        canon = ["more varied", "less varied", "about equally varied"]
                        stem = (f"Compare how much the images within each set vary in {NAMES[asp]} "
                                f"(from \"{P['left']}\" to \"{P['right']}\"). Compared with set A, the images of set B are:")
                    order = list(range(3))
                    random.Random(f"{a.vlm}|{c}|{level}|{unit}|{asp}|{q}").shuffle(order)
                    text = head + stem + "\n" + "\n".join(f"{'ABC'[m]}. {canon[o]}" for m, o in enumerate(order)) \
                        + "\nAnswer with the letter only."
                    p = choose(imgs, text)
                    pc = np.zeros(3)
                    for m, o in enumerate(order):
                        pc[o] = p[m]
                    mc.append(dict(vlm=a.vlm, contrast=c, level=level, unit=unit, subject=subject or "", aspect=asp,
                                   question=q, answer=["right", "left", "none"][int(pc.argmax())] if q == "shift"
                                   else ["more", "less", "same"][int(pc.argmax())],
                                   p0=round(pc[0], 4), p1=round(pc[1], 4), p2=round(pc[2], 4), order="".join(map(str, order))))
                    n += 1
            if (c, level, unit) not in done_free:
                txt = generate(imgs, head + "List up to five ways in which the images of set B differ in appearance "
                                            "from the images of set A. One short statement per line.")
                free.append(dict(vlm=a.vlm, contrast=c, level=level, unit=unit, subject=subject or "", text=txt))
            if level == "pooled" and a.vlm == "mistral" and (c, unit) not in done_prop:
                txt = generate(imgs, head + "Propose up to five pairs of opposite short descriptions (left pole, right "
                                            "pole) of appearance properties that distinguish these two sets. One pair "
                                            "per line, formatted as: left pole | right pole")
                prop.append(dict(vlm=a.vlm, contrast=c, unit=unit, text=txt))
            pd.DataFrame(mc).to_csv(mc_p, index=False)
            pd.DataFrame(free).to_csv(free_p, index=False)
            if prop:
                pd.DataFrame(prop).to_csv(prop_p, index=False)
            print(f"{a.vlm} {c} {level} {unit} mc={len(mc)} {time.time() - t0:.0f}s", flush=True)
            if a.limit and n >= a.limit:
                sys.exit(0)
print(a.vlm, "done", len(mc), "choices", len(free), "texts", f"{time.time() - t0:.0f}s")
