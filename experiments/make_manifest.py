"""Reproducibility manifest (requested by the 2026-10-22 review): what was generated, with what, and fingerprints of
every image set and score table. Usage: python experiments/make_manifest.py   (writes results/MANIFEST.json)

Per model folder: SHA-256 of every config and weight index file, and the total size of the weight files.
Per generated group: the number of images, SHA-256 over the sorted per-image SHA-256 digests, the generation settings
and library versions recorded in meta.csv, and SHA-256 of each score table (clip_scores.csv, siglip_scores.csv).
Also: prompts and seeds (from prompts.py), the rewrites files and the frozen analysis files. No paths or host names."""
import glob, hashlib, json, os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "model_study"))
from prompts import CONTROLS, MAIN, jobs  # noqa: E402

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))


def sha(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def models():
    out = {}
    for d in sorted(glob.glob(f"{DATA}/models/*")):
        files = sorted(glob.glob(f"{d}/**/*", recursive=True))
        cfg = {os.path.relpath(f, d): sha(f) for f in files if f.endswith((".json", ".txt", ".model", ".jinja")) and os.path.isfile(f)}
        w = [f for f in files if f.endswith((".safetensors", ".bin"))]
        out[os.path.basename(d)] = dict(config_sha256=cfg, weight_files=len(w), weight_bytes=sum(os.path.getsize(f) for f in w))
    return out


def group(d):
    meta = pd.read_csv(f"{d}/meta.csv")
    digests = sorted(sha(f"{d}/{j}.png") for j in meta.job)
    keep = [c for c in ("pipe", "path", "dtype", "variant", "size", "steps", "cfg", "cfg_arg", "extra", "batch", "condition",
                        "offload", "two_stage", "diffusers", "torch") if c in meta]
    settings = {c: sorted(map(str, meta[c].dropna().unique())) for c in keep}
    tables = {t: sha(f"{d}/{t}") for t in ("clip_scores.csv", "siglip_scores.csv") if os.path.exists(f"{d}/{t}")}
    return dict(images=len(meta), images_sha256=hashlib.sha256("".join(digests).encode()).hexdigest(), settings=settings, score_tables=tables)


def main():
    M = dict(created=pd.Timestamp.now().isoformat(timespec="seconds"),
             prompts=dict(main=MAIN, controls=CONTROLS), seeds="seed = 100000 * prompt index + k (main, k < 32); 100000 * (50 + control index) + k (controls, k < 16)",
             n_jobs=len(jobs(32, 16)), models=models(), groups={}, files={})
    for d in sorted(glob.glob(f"{DATA}/model_study/open/G*")) + sorted(glob.glob(f"{DATA}/llm_study/G*__*")):
        M["groups"][os.path.basename(d)] = group(d)
    for f in sorted(glob.glob(f"{DATA}/llm_study/rewrites_*.csv")):
        M["files"][os.path.basename(f)] = sha(f)
    for f in sorted(glob.glob(os.path.join(REPO, "experiments", "model_study", "analysis", "frozen_*.json"))):
        M["files"][os.path.relpath(f, REPO)] = sha(f)
    json.dump(M, open(os.path.join(REPO, "results", "MANIFEST.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("groups", len(M["groups"]), "models", len(M["models"]))


if __name__ == "__main__":
    main()
