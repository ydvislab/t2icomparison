"""Generate all jobs for one open-model group on CUDA. Resumable.

Usage: python gen.py <group> [--gpu 0] [--batch 4] [--limit N] [--jobset study|anchor_pilot] [--seeds N] [--device DEV]
--jobset anchor_pilot generates the calibration-anchor pilot (../anchors/anchors.py) into model_study/anchors_pilot/;
--seeds overrides the number of seeds of an anchor job set (smoke tests only); --device overrides cuda:<gpu>.
Each image uses its own torch.Generator seeded with the job seed. In bf16 the GPU kernels still differ slightly with
batch size (about 5% of pixels change by more than 8/255 for klein 4B, the image content is the same), so keep the
batch size fixed for a whole group; it is recorded in meta.csv. The study uses --batch 4 for every group.
"""
import argparse, os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
import pandas as pd
import torch
import diffusers

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from prompts import jobs  # noqa: E402
from config import DATA, GROUPS, MODELS, N_CONTROL, N_MAIN, OUT  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "anchors"))
from anchors import PILOT_SEEDS, pilot_jobs  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("group", choices=sorted(GROUPS))
ap.add_argument("--gpu", type=int, default=0)
ap.add_argument("--batch", type=int, default=4)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--jobset", choices=["study", "anchor_pilot"], default="study")
ap.add_argument("--seeds", type=int, default=0)
ap.add_argument("--device", default="")
a = ap.parse_args()

G = GROUPS[a.group]
dev = a.device or f"cuda:{a.gpu}"
if a.jobset == "study":
    if a.seeds:
        sys.exit("--seeds applies to anchor job sets only; the study seed counts are fixed in config.py")
    all_jobs, out_dir = jobs(N_MAIN, N_CONTROL), f"{OUT}/{a.group}"
else:
    all_jobs, out_dir = pilot_jobs(a.seeds or PILOT_SEEDS), f"{DATA}/model_study/anchors_pilot/{a.group}"
os.makedirs(out_dir, exist_ok=True)
meta_path = f"{out_dir}/meta.csv"
rows = pd.read_csv(meta_path).to_dict("records") if os.path.exists(meta_path) else []
if rows and "batch" in rows[0] and int(rows[0]["batch"]) != a.batch:
    sys.exit(f"{a.group} was started with --batch {rows[0]['batch']}; resume with the same batch size")
done = {r["job"] for r in rows}
todo = [j for j in all_jobs if j["job"] not in done]
if a.limit:
    todo = todo[:a.limit]
print(a.group, "todo", len(todo), "done", len(done), flush=True)
if not todo:
    sys.exit(0)

kw = dict(torch_dtype=getattr(torch, G["dtype"]))
if G.get("variant"):
    kw.update(variant=G["variant"], use_safetensors=True)
if G["pipe"] == "StableDiffusionPipeline":
    kw.update(safety_checker=None, feature_extractor=None, requires_safety_checker=False)
pipe = getattr(diffusers, G["pipe"]).from_pretrained(f"{MODELS}/{G['path']}", **kw).to(dev)
pipe.set_progress_bar_config(disable=True)
cfg_arg = G.get("cfg_arg", "guidance_scale")
extra = G.get("extra", {})

t0 = time.time()
batches = [todo[i:i + a.batch] for i in range(0, len(todo), a.batch)]
for n, B in enumerate(batches):
    # one prompt per batch keeps memory predictable; split batches that straddle two prompts
    for P in [[j for j in B if j["prompt"] == p] for p in dict.fromkeys(j["prompt"] for j in B)]:
        t = time.time()
        gens = [torch.Generator("cpu").manual_seed(j["seed"]) for j in P]
        call = dict(prompt=[j["prompt"] for j in P], height=G["size"], width=G["size"],
                    num_inference_steps=G["steps"], generator=gens, **{cfg_arg: G["cfg"]})
        call.update({k: [v] * len(P) for k, v in extra.items()})
        with torch.inference_mode():
            imgs = pipe(**call).images
        sec = round((time.time() - t) / len(P), 2)
        for j, img in zip(P, imgs):
            img.save(f"{out_dir}/{j['job']}.png")
            rows.append(dict(j, group=a.group, pipe=G["pipe"], path=G["path"], dtype=G["dtype"],
                             variant=G.get("variant", ""), size=G["size"], steps=G["steps"], cfg=G["cfg"],
                             cfg_arg=cfg_arg, extra=repr(extra), year=G["year"], batch=a.batch, seconds=sec,
                             diffusers=diffusers.__version__, torch=torch.__version__))
    if n % 5 == 0 or n == len(batches) - 1:
        pd.DataFrame(rows).to_csv(meta_path, index=False)
        print(f"{a.group} {sum(len(b) for b in batches[:n+1])}/{len(todo)} {time.time()-t0:.0f}s", flush=True)
print(a.group, "done", f"{time.time()-t0:.0f}s", flush=True)
