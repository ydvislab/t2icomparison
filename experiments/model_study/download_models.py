"""Download model weights (diffusers layout only) from hf-mirror / ModelScope with resume. Stdlib only.

Usage: python download_models.py [name ...]   (no names = all). Files go to $T2IC_DATA/models/<name>/.
FLUX.2 klein-base 4B and klein 9B reuse text_encoder/tokenizer/vae from klein 4B and klein-base 9B (identical
files, checked by SHA256); create those symlinks as described in docs/RUNBOOK.md."""
import json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext")) + "/models"
HF = "https://hf-mirror.com"
MS = "https://www.modelscope.cn"
UA = {"User-Agent": "t2ic-downloader"}

# name, source, repo, precision variant ("fp16" = take *.fp16.* files, None = take full files), skip prefixes
MODELS = [
    ("clip-vit-large-patch14", "hf", "openai/clip-vit-large-patch14", None, ()),
    ("sd15", "hf", "stable-diffusion-v1-5/stable-diffusion-v1-5", "fp16", ("safety_checker/",)),
    ("sdxl-turbo", "hf", "stabilityai/sdxl-turbo", "fp16", ()),
    ("Qwen3.5-4B", "hf", "Qwen/Qwen3.5-4B", None, ()),
    ("FLUX.2-klein-base-4B", "hf", "black-forest-labs/FLUX.2-klein-base-4B", None, ("text_encoder/", "tokenizer/", "vae/")),
    ("Qwen-Image-2512", "hf", "Qwen/Qwen-Image-2512", None, ()),
    ("sd35-large", "ms", "stabilityai/stable-diffusion-3.5-large", None, ("text_encoders/",)),
    ("FLUX.2-dev", "ms", "black-forest-labs/FLUX.2-dev", None, ()),
    ("FLUX.2-klein-base-9B", "ms", "black-forest-labs/FLUX.2-klein-base-9B", None, ()),
    ("FLUX.2-klein-9B", "ms", "black-forest-labs/FLUX.2-klein-9B", None, ("text_encoder/", "tokenizer/", "vae/")),
]


def get_json(url):
    for i in range(5):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:
            print(f"  list retry {i}: {e}", flush=True); time.sleep(5)
    raise RuntimeError(url)


def list_files(src, repo):
    if src == "hf":
        fs = get_json(f"{HF}/api/models/{repo}/tree/main?recursive=true")
        return [(f["path"], f["size"]) for f in fs if f["type"] == "file"], lambda p: f"{HF}/{repo}/resolve/main/{p}"
    d = get_json(f"{MS}/api/v1/models/{repo}/repo/files?Recursive=true&Revision=master")
    fs = d["Data"]["Files"]
    return [(f["Path"], f["Size"]) for f in fs if f["Type"] == "blob"], lambda p: f"{MS}/models/{repo}/resolve/master/{p}"


def keep(path, paths, variant, skip, repo):
    if path.startswith(skip):
        return False
    if re.search(r"\.(ckpt|bin|onnx|onnx_data|h5|msgpack|pb|jpg|png|gif)$", path) or "non_ema" in path:
        return False
    is_diffusers = "model_index.json" in paths
    if is_diffusers and "/" not in path and path.endswith(".safetensors"):
        return False  # single-file checkpoint duplicates
    if variant == "fp16":
        if path.endswith(".safetensors") and ".fp16." not in path and path.replace(".safetensors", ".fp16.safetensors") in paths:
            return False
    elif ".fp16." in path and path.replace(".fp16", "") in paths:
        return False
    return True


def fetch(url, dest, size):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) == size:
        return 0
    part = dest + ".part"
    for attempt in range(30):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        if have == size:
            break
        try:
            req = urllib.request.Request(url, headers={**UA, "Range": f"bytes={have}-"} if have else UA)
            with urllib.request.urlopen(req, timeout=60) as r, open(part, "ab" if have else "wb") as f:
                if have and r.status != 206:
                    f.seek(0); f.truncate()
                while True:
                    b = r.read(8 << 20)
                    if not b:
                        break
                    f.write(b)
        except Exception as e:
            print(f"  retry {attempt} {os.path.basename(dest)}: {e}", flush=True); time.sleep(min(60, 5 * (attempt + 1)))
    if os.path.getsize(part) != size:
        raise RuntimeError(f"size mismatch {dest}: {os.path.getsize(part)} != {size}")
    os.replace(part, dest)
    return size


def main(names):
    for name, src, repo, variant, skip in MODELS:
        if names and name not in names:
            continue
        files, url_of = list_files(src, repo)
        paths = {p for p, _ in files}
        todo = [(p, s) for p, s in files if keep(p, paths, variant, skip, repo)]
        total = sum(s for _, s in todo)
        print(f"== {name} ({repo}, {src}): {len(todo)} files, {total/1e9:.1f} GB", flush=True)
        t0 = time.time()
        with ThreadPoolExecutor(4) as ex:
            for p, s in todo:
                ex.submit(lambda p=p, s=s: fetch(url_of(p), f"{ROOT}/{name}/{p}", s))
        got = sum(os.path.getsize(f"{ROOT}/{name}/{p}") for p, _ in todo if os.path.exists(f"{ROOT}/{name}/{p}"))
        ok = got == total
        print(f"== {name} {'DONE' if ok else 'INCOMPLETE'} {got/1e9:.1f}/{total/1e9:.1f} GB in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
