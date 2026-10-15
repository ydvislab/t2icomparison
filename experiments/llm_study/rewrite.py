"""LLM prompt rewriting for Q4 (PREREG.md). Usage: python rewrite.py mistral|qwen [--gpu 0]
Writes $T2IC_DATA/llm_study/rewrites_<llm>.csv: one rewrite per (subject, seed k), because a deployed rewriter
rewrites every request independently.
  mistral  FLUX.2's official prompt upsampler: the FLUX.2 dev text encoder (Mistral-Small-3.2-24B),
           SYSTEM_MESSAGE_UPSAMPLING_T2I (copied by diffusers from black-forest-labs/flux2), the message format of
           diffusers' format_input, temperature 0.15 (the official default), at most 512 new tokens.
           Deviation (2026-10-15): diffusers' Flux2Pipeline.upsample_prompt pads every input on the right to 2,048
           tokens; with transformers 5.19 this produced degenerate text (the system message echoed, broken words), so
           the same model and messages are called without padding. Kept for the record as
           rewrites_mistral_diffusers_padded.csv; no image was generated from it.
  qwen     Qwen3.5-4B with the same system message, temperature and token limit, thinking disabled.
The 32 rewrites of a subject are 32 samples (num_return_sequences) of one unpadded input, drawn after
torch.manual_seed(100000 * subject index)."""
import argparse, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd, torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model_study"))
from prompts import MAIN  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
N, TEMP, MAX_NEW = 32, 0.15, 512
ap = argparse.ArgumentParser()
ap.add_argument("llm", choices=["mistral", "qwen"])
ap.add_argument("--gpu", type=int, default=0)
ap.add_argument("--only", type=int, default=0, help="test: first N subjects, print, write nothing")
a = ap.parse_args()
dev = f"cuda:{a.gpu}"
os.makedirs(f"{DATA}/llm_study", exist_ok=True)
out = f"{DATA}/llm_study/rewrites_{a.llm}.csv"

from diffusers.pipelines.flux2.system_messages import SYSTEM_MESSAGE_UPSAMPLING_T2I as SYS
from transformers import AutoProcessor
if a.llm == "mistral":
    from transformers import Mistral3ForConditionalGeneration
    proc = AutoProcessor.from_pretrained(f"{DATA}/models/FLUX.2-dev/tokenizer")
    model = Mistral3ForConditionalGeneration.from_pretrained(f"{DATA}/models/FLUX.2-dev/text_encoder",
                                                             dtype=torch.bfloat16).to(dev).eval()
    TPL = {}
else:
    from transformers import AutoModelForImageTextToText
    proc = AutoProcessor.from_pretrained(f"{DATA}/models/Qwen3.5-4B")
    model = AutoModelForImageTextToText.from_pretrained(f"{DATA}/models/Qwen3.5-4B", dtype=torch.bfloat16).to(dev).eval()
    TPL = dict(enable_thinking=False)
TOK = proc.tokenizer if hasattr(proc, "tokenizer") else proc


def rewrite(p):
    msgs = [{"role": "system", "content": [{"type": "text", "text": SYS}]},
            {"role": "user", "content": [{"type": "text", "text": p}]}]          # diffusers format_input
    inp = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_dict=True,
                                   return_tensors="pt", **TPL).to(dev)
    with torch.no_grad():
        g = model.generate(**inp, max_new_tokens=MAX_NEW, do_sample=True, temperature=TEMP, num_return_sequences=N)
    return TOK.batch_decode(g[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)


rows, t0 = [], time.time()
for i, (cat, s) in enumerate(MAIN[:a.only] if a.only else MAIN):
    torch.manual_seed(100000 * i)
    for k, r in enumerate(rewrite(s)):
        rows.append(dict(i=i, k=k, category=cat, subject=s, seed=100000 * i + k, llm=a.llm,
                         rewrite=" ".join(r.strip().split())))
    print(a.llm, s, f"{time.time() - t0:.0f}s", rows[-1]["rewrite"][:100], flush=True)
if a.only:
    for r in rows[::8]:
        print("---", r["subject"], r["k"], "|", r["rewrite"])
    sys.exit(0)
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out, len(rows))
