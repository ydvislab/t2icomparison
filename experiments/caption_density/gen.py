"""Generate one or more conditions. Usage: python gen.py <cond> [<cond> ...] (resumable)"""
import gc, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd, torch
from config import CONDITIONS, DATA, SIZE, jobs

for cond in sys.argv[1:]:
    kind, path, steps, cfg, style = CONDITIONS[cond]
    out = f"{DATA}/{cond}"; os.makedirs(out, exist_ok=True)
    mp = f"{out}/meta.csv"
    rows = pd.read_csv(mp).to_dict("records") if os.path.exists(mp) else []
    done = {r["job"] for r in rows}
    todo = [j for j in jobs(cond) if j["job"] not in done]
    print(cond, "todo", len(todo), flush=True)
    if not todo:
        continue
    if kind == "klein":
        from diffusers import Flux2KleinPipeline
        dt = torch.bfloat16
        prompts = sorted({j["prompt"] for j in todo} | ({""} if cfg > 1 else set()))
        enc = Flux2KleinPipeline.from_pretrained(path, transformer=None, vae=None, torch_dtype=dt).to("mps")
        with torch.no_grad():
            E = {p: enc.encode_prompt(prompt=p, device="mps")[0].cpu() for p in prompts}
        del enc; gc.collect(); torch.mps.empty_cache()
        pipe = Flux2KleinPipeline.from_pretrained(path, text_encoder=None, tokenizer=None, torch_dtype=dt).to("mps")
        neg = E.get("")
        def run(j, g):
            kw = dict(prompt_embeds=E[j["prompt"]].to("mps"), height=SIZE, width=SIZE,
                      num_inference_steps=steps, guidance_scale=cfg, generator=g)
            if cfg > 1:
                kw["negative_prompt_embeds"] = neg.to("mps")
            return pipe(**kw).images[0]
    else:
        from diffusers import StableDiffusionPipeline
        pipe = StableDiffusionPipeline.from_single_file(
            f"{path}/v1-5-pruned-emaonly.safetensors", config=path, torch_dtype=torch.float16, safety_checker=None,
            feature_extractor=None, requires_safety_checker=False, local_files_only=True).to("mps")
        run = lambda j, g: pipe(j["prompt"], height=SIZE, width=SIZE, num_inference_steps=steps,
                                guidance_scale=cfg, generator=g).images[0]
    pipe.set_progress_bar_config(disable=True)
    t0 = time.time()
    for n, j in enumerate(todo):
        t = time.time()
        img = run(j, torch.Generator("cpu").manual_seed(j["seed"]))
        img.save(f"{out}/{j['job']}.png")
        rows.append(dict(j, condition=cond, steps=steps, cfg=cfg, style=style, size=SIZE, seconds=round(time.time() - t, 2)))
        if n % 6 == 0 or n == len(todo) - 1:
            pd.DataFrame(rows).to_csv(mp, index=False)
            print(f"{cond} {n+1}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
    del pipe; gc.collect(); torch.mps.empty_cache()
    print(cond, "done", f"{time.time()-t0:.0f}s", flush=True)
