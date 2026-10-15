"""LLM prompt rewriting for Q4 (PREREG.md). Usage: python rewrite.py mistral|qwen [--gpu 0]
Writes $T2IC_DATA/llm_study/rewrites_<llm>.csv: one rewrite per (subject, seed k), because a deployed rewriter
rewrites every request independently.
  mistral  FLUX.2's official prompt upsampler as shipped in diffusers (Flux2Pipeline.upsample_prompt): the FLUX.2 dev
           text encoder (Mistral-Small-3.2-24B), SYSTEM_MESSAGE_UPSAMPLING_T2I (copied by diffusers from
           black-forest-labs/flux2), temperature 0.15 (the official default), at most 512 new tokens.
  qwen     Qwen3.5-4B with the same system message, temperature and token limit, thinking disabled.
The 32 rewrites of a subject are sampled in one batch after torch.manual_seed(100000 * subject index)."""
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
a = ap.parse_args()
dev = f"cuda:{a.gpu}"
os.makedirs(f"{DATA}/llm_study", exist_ok=True)
out = f"{DATA}/llm_study/rewrites_{a.llm}.csv"

if a.llm == "mistral":
    from diffusers import Flux2Pipeline
    pipe = Flux2Pipeline.from_pretrained(f"{DATA}/models/FLUX.2-dev", transformer=None, vae=None,
                                         torch_dtype=torch.bfloat16)
    pipe.text_encoder.to(dev)

    def rewrite(p):
        return pipe.upsample_prompt([p] * N, temperature=TEMP, device=dev)
else:
    from diffusers.pipelines.flux2.system_messages import SYSTEM_MESSAGE_UPSAMPLING_T2I as SYS
    from transformers import AutoModelForImageTextToText, AutoProcessor
    path = f"{DATA}/models/Qwen3.5-4B"
    proc = AutoProcessor.from_pretrained(path)
    proc.tokenizer.padding_side = "left"
    model = AutoModelForImageTextToText.from_pretrained(path, dtype=torch.bfloat16).to(dev).eval()

    def rewrite(p):
        msgs = [{"role": "system", "content": [{"type": "text", "text": SYS}]},
                {"role": "user", "content": [{"type": "text", "text": p}]}]
        t = proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
        inp = proc(text=[t] * N, return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            g = model.generate(**inp, max_new_tokens=MAX_NEW, do_sample=True, temperature=TEMP)
        return proc.batch_decode(g[:, inp["input_ids"].shape[1]:], skip_special_tokens=True)

rows, t0 = [], time.time()
for i, (cat, s) in enumerate(MAIN):
    torch.manual_seed(100000 * i)
    for k, r in enumerate(rewrite(s)):
        rows.append(dict(i=i, k=k, category=cat, subject=s, seed=100000 * i + k, llm=a.llm,
                         rewrite=" ".join(r.strip().split())))
    print(a.llm, s, f"{time.time() - t0:.0f}s", rows[-1]["rewrite"][:100], flush=True)
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out, len(rows))
