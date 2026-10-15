"""Generate the study images from rewritten prompts (Q4, PREREG.md). Resumable.
Usage: python gen_rewritten.py <group> <condition> [--gpu 0]
  group      an open configuration from ../model_study/open/config.py (settings unchanged)
  condition  mistral | qwen        one rewrite per seed, from rewrites_<llm>.csv
             mistral_fixed         the k = 0 rewrite of each subject reused for all 32 seeds
Output: $T2IC_DATA/llm_study/<group>__<condition>/<job>.png + meta.csv, with the same job names and seeds as the
original study images, so every rewritten image is paired with the original image from the same starting noise.
Batches of 4 consecutive seeds of one subject (batch size fixed at 4, as in the study)."""
import argparse, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd, torch, diffusers

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "model_study", "open"))
from config import DATA, GROUPS, MODELS  # noqa: E402

BATCH = 4
ap = argparse.ArgumentParser()
ap.add_argument("group", choices=sorted(GROUPS))
ap.add_argument("condition", choices=["mistral", "qwen", "mistral_fixed"])
ap.add_argument("--gpu", type=int, default=0)
ap.add_argument("--offload", action="store_true", help="model CPU offload (same weights and dtype; for a shared GPU)")
a = ap.parse_args()
G, dev = GROUPS[a.group], f"cuda:{a.gpu}"
R = pd.read_csv(f"{DATA}/llm_study/rewrites_{a.condition.replace('_fixed', '')}.csv")
if a.condition.endswith("_fixed"):
    first = R[R.k == 0].set_index("i").rewrite
    R["rewrite"] = R.i.map(first)
R["job"] = [f"m{i:02d}_{k:02d}" for i, k in zip(R.i, R.k)]
out_dir = f"{DATA}/llm_study/{a.group}__{a.condition}"
os.makedirs(out_dir, exist_ok=True)
meta_path = f"{out_dir}/meta.csv"
rows = pd.read_csv(meta_path).to_dict("records") if os.path.exists(meta_path) else []
done = {r["job"] for r in rows}
todo = R[~R.job.isin(done)]
print(a.group, a.condition, "todo", len(todo), "done", len(done), flush=True)
if todo.empty:
    sys.exit(0)

kw = dict(torch_dtype=getattr(torch, G["dtype"]))
if G.get("variant"):
    kw.update(variant=G["variant"], use_safetensors=True)
pipe = getattr(diffusers, G["pipe"]).from_pretrained(f"{MODELS}/{G['path']}", **kw)
if a.offload:
    pipe.enable_model_cpu_offload(gpu_id=a.gpu)
else:
    pipe = pipe.to(dev)
pipe.set_progress_bar_config(disable=True)
cfg_arg, extra = G.get("cfg_arg", "guidance_scale"), G.get("extra", {})
t0 = time.time()
for n, (_, P) in enumerate(todo.groupby([todo.i, todo.k // BATCH], sort=True)):
    t = time.time()
    call = dict(prompt=list(P.rewrite), height=G["size"], width=G["size"], num_inference_steps=G["steps"],
                generator=[torch.Generator("cpu").manual_seed(int(s)) for s in P.seed], **{cfg_arg: G["cfg"]})
    call.update({k: [v] * len(P) for k, v in extra.items()})
    with torch.inference_mode():
        imgs = pipe(**call).images
    sec = round((time.time() - t) / len(P), 2)
    for r, img in zip(P.itertuples(), imgs):
        img.save(f"{out_dir}/{r.job}.png")
        rows.append(dict(job=r.job, kind="main", category=r.category, subject=r.subject, prompt=r.rewrite,
                         original_prompt=r.subject, seed=r.seed, k=r.k, condition=a.condition, group=a.group,
                         pipe=G["pipe"], path=G["path"], size=G["size"], steps=G["steps"], cfg=G["cfg"],
                         batch=BATCH, offload=a.offload, seconds=sec, diffusers=diffusers.__version__, torch=torch.__version__))
    if n % 5 == 0:
        pd.DataFrame(rows).to_csv(meta_path, index=False)
        print(f"{a.group} {a.condition} {len(rows)}/{len(R)} {time.time() - t0:.0f}s", flush=True)
pd.DataFrame(rows).to_csv(meta_path, index=False)
print(a.group, a.condition, "done", f"{time.time() - t0:.0f}s", flush=True)
