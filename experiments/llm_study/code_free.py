"""Q5 free text: split each VLM answer into statements and code them (PREREG.md). Resumable per VLM file.
Usage: python code_free.py [--gpu 0]
Coder: Qwen3.5-4B, thinking off, constrained letter choice on the statement text alone (no images):
  property  A saturation, B medium (photo vs painting/illustration), C shot scale, D colour tone (modern vs vintage),
            E background (plain vs busy), F variety or uniformity across the images, G something else
  direction for A-E: is set B described as closer to the right pole, closer to the left pole, or neither;
            for F: is set B described as more varied, less varied (more uniform), or neither.
Statements: lines of the answer that start with "-", "*", "•" or a number, after stripping markers; the intro line
("Here are five ways ...") is dropped. Writes $T2IC_DATA/llm_study/q5/<vlm>/coded.csv and a 20% random sample
(seed 20261016) to results/q5/coding_check_sample.csv for the owner's check (statement, code; the check column is
filled by the owner)."""
import argparse, os, re, sys
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import numpy as np, pandas as pd, torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "aspects"))
from aspects import ASPECTS  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
POLES = {x["key"]: x for x in ASPECTS}
PROPS = [("sat", "colour saturation (muted vs vivid colours)"), ("medium", "medium (photograph vs painting or illustration)"),
         ("shot", "shot scale (close-up vs wide shot)"), ("tone", "colour tone (modern neutral vs vintage sepia)"),
         ("bg", "background (plain vs busy and detailed)"), ("variety", "how varied or uniform the images are"),
         ("other", "something else")]
LET = "ABCDEFG"

ap = argparse.ArgumentParser(); ap.add_argument("--gpu", type=int, default=0); a = ap.parse_args()
dev = f"cuda:{a.gpu}"
from transformers import AutoModelForImageTextToText, AutoProcessor  # noqa: E402
proc = AutoProcessor.from_pretrained(f"{DATA}/models/Qwen3.5-4B")
model = AutoModelForImageTextToText.from_pretrained(f"{DATA}/models/Qwen3.5-4B", dtype=torch.bfloat16).to(dev).eval()
lid = [proc.tokenizer.encode(x, add_special_tokens=False)[0] for x in LET]


@torch.no_grad()
def ask(q, opts):
    text = q + "\n" + "\n".join(f"{LET[i]}. {o}" for i, o in enumerate(opts)) + "\nAnswer with the letter only."
    t = proc.apply_chat_template([{"role": "user", "content": [{"type": "text", "text": text}]}],
                                 add_generation_prompt=True, tokenize=False, enable_thinking=False)
    inp = proc(text=[t], return_tensors="pt").to(dev)
    p = torch.softmax(model(**inp).logits[0, -1].float()[lid[:len(opts)]], 0).cpu().numpy()
    return int(p.argmax()), float(p.max())


def statements(text):
    out = []
    for line in str(text).splitlines():
        m = re.match(r"^\s*(?:[-*•]|\d+[.)])\s*(.+)$", line)
        if m and len(m.group(1).split()) >= 3:
            out.append(m.group(1).strip().strip("*").strip())
    return out


rows_all = []
for vlm in ("qwen", "mistral"):
    src = f"{DATA}/llm_study/q5/{vlm}/free.csv"
    if not os.path.exists(src):
        continue
    out = f"{DATA}/llm_study/q5/{vlm}/coded.csv"
    old = pd.read_csv(out) if os.path.exists(out) else pd.DataFrame()
    done = set(zip(old.contrast, old.level, old.unit)) if len(old) else set()
    rows = old.to_dict("records")
    for r in pd.read_csv(src).itertuples():
        if (r.contrast, r.level, r.unit) in done:
            continue
        for n, st in enumerate(statements(r.text)):
            head = f"A statement compares image set B with image set A:\n\"{st}\"\n"
            k, pk = ask(head + "Which property of the images does the statement mainly describe?", [d for _, d in PROPS])
            prop = PROPS[k][0]
            direction, pd_ = "", np.nan
            if prop in POLES:
                P = POLES[prop]
                j, pd_ = ask(head + "According to the statement, the images of set B are:",
                             [f"closer to \"{P['right']}\"", f"closer to \"{P['left']}\"", "neither / not stated"])
                direction = ["right", "left", "none"][j]
            elif prop == "variety":
                j, pd_ = ask(head + "According to the statement, the images of set B are:",
                             ["more varied", "less varied (more uniform)", "neither / not stated"])
                direction = ["more", "less", "none"][j]
            rows.append(dict(vlm=vlm, contrast=r.contrast, level=r.level, unit=r.unit, subject=r.subject, n=n,
                             statement=st, property=prop, p_property=round(pk, 3), direction=direction,
                             p_direction=round(pd_, 3) if pd_ == pd_ else ""))
        pd.DataFrame(rows).to_csv(out, index=False)
    print(vlm, len(rows), "statements coded", flush=True)
    rows_all += rows
C = pd.DataFrame(rows_all)
S = C.sample(frac=0.2, random_state=20261016)[["vlm", "contrast", "level", "unit", "statement", "property", "direction"]]
S["owner_check (ok / correct code)"] = ""
os.makedirs(f"{REPO}/results/q5", exist_ok=True)
S.to_csv(f"{REPO}/results/q5/coding_check_sample.csv", index=False, encoding="utf-8-sig")
print(C.groupby(["vlm", "property"]).size().unstack(fill_value=0).to_string())
print(C[C.property == "variety"].groupby(["vlm", "direction"]).size().to_string())
