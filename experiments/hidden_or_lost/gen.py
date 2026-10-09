"""Generate all jobs for one model. Usage: python gen.py <model_key>  (resumable)"""
import gc, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd
import torch
from config import DATA, GENERATORS, jobs

key = sys.argv[1]
G = GENERATORS[key]
dev, dt = "mps", (torch.bfloat16 if G["kind"] == "klein" else torch.float16)
out_dir = f"{DATA}/{key}"
os.makedirs(out_dir, exist_ok=True)
meta_path = f"{out_dir}/meta.csv"
rows = pd.read_csv(meta_path).to_dict("records") if os.path.exists(meta_path) else []
done = {r["job"] for r in rows}
todo = [j for j in jobs() if j["job"] not in done]
print(key, "todo", len(todo), flush=True)
if not todo:
    sys.exit(0)

if G["kind"] == "sd15":
    from diffusers import StableDiffusionPipeline
    pipe = StableDiffusionPipeline.from_single_file(
        f"{G['path']}/v1-5-pruned-emaonly.safetensors", config=G["path"], torch_dtype=dt,
        safety_checker=None, feature_extractor=None, requires_safety_checker=False,
        local_files_only=True).to(dev)
    run = lambda j, g: pipe(j["prompt"], height=G["size"], width=G["size"], num_inference_steps=G["steps"],
                            guidance_scale=G["cfg"], generator=g).images[0]
elif G["kind"] == "sdxl":
    from diffusers import StableDiffusionXLPipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(G["path"], torch_dtype=dt, variant="fp16",
                                                     use_safetensors=True).to(dev)
    run = lambda j, g: pipe(j["prompt"], height=G["size"], width=G["size"], num_inference_steps=G["steps"],
                            guidance_scale=G["cfg"], generator=g).images[0]
elif G["kind"] == "klein":
    from diffusers import Flux2KleinPipeline
    prompts = sorted({j["prompt"] for j in todo})
    enc = Flux2KleinPipeline.from_pretrained(G["path"], transformer=None, vae=None, torch_dtype=dt).to(dev)
    with torch.no_grad():
        E = {p: enc.encode_prompt(prompt=p, device=dev)[0].cpu() for p in prompts}
    del enc; gc.collect(); torch.mps.empty_cache()
    pipe = Flux2KleinPipeline.from_pretrained(G["path"], text_encoder=None, tokenizer=None, torch_dtype=dt).to(dev)
    run = lambda j, g: pipe(prompt_embeds=E[j["prompt"]].to(dev), height=G["size"], width=G["size"],
                            num_inference_steps=G["steps"], guidance_scale=G["cfg"], generator=g).images[0]
pipe.set_progress_bar_config(disable=True)

t0 = time.time()
for n, j in enumerate(todo):
    g = torch.Generator("cpu").manual_seed(j["seed"])
    t = time.time()
    img = run(j, g)
    img.save(f"{out_dir}/{j['job']}.png")
    rows.append(dict(j, model=key, year=G["year"], size=G["size"], steps=G["steps"], cfg=G["cfg"],
                     seconds=round(time.time() - t, 2)))
    if n % 8 == 0 or n == len(todo) - 1:
        pd.DataFrame(rows).to_csv(meta_path, index=False)
        print(f"{key} {n+1}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
print(key, "done", f"{time.time()-t0:.0f}s")
