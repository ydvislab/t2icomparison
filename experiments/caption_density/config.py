"""Caption-density mechanism test: is klein's default collapse caused by the text side
(dense-caption training: unspecified attributes never learned) or by the sampler side
(distillation, classifier-free guidance)? Same seeds across all conditions (paired)."""
import os
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

DATA = os.path.join(DATA_ROOT, "caption_density")
MODELS = os.path.join(DATA_ROOT, "models")
SUBJECTS = ["a doctor", "a cup of coffee", "a house", "a city street", "a person reading a book", "a kitchen"]
SEEDS = 8
SIZE = 512
STYLES = {
    "minimal": "{s}",
    "dense":   "This image shows {s}. The main subject of this image is {s}.",   # caption-like, no attribute info
    "open":    "{s}, in any style, any setting, any lighting, any colors",       # explicit generic request for variety
}
# condition -> (model kind, weights dir, steps, guidance, prompt style)
CONDITIONS = {
    "klein_min":        ("klein", f"{MODELS}/FLUX.2-klein-4B", 4, 1.0, "minimal"),
    "klein_dense":      ("klein", f"{MODELS}/FLUX.2-klein-4B", 4, 1.0, "dense"),
    "klein_open":       ("klein", f"{MODELS}/FLUX.2-klein-4B", 4, 1.0, "open"),
    "kbase_cfg1_min":   ("klein", f"{MODELS}/FLUX.2-klein-base-4B", 28, 1.0, "minimal"),
    "kbase_cfg1_dense": ("klein", f"{MODELS}/FLUX.2-klein-base-4B", 28, 1.0, "dense"),
    "kbase_cfg4_min":   ("klein", f"{MODELS}/FLUX.2-klein-base-4B", 28, 4.0, "minimal"),
    "sd15_cfg75_min":   ("sd15", f"{MODELS}/sd15", 25, 7.5, "minimal"),
    "sd15_cfg75_dense": ("sd15", f"{MODELS}/sd15", 25, 7.5, "dense"),
    "sd15_cfg75_open":  ("sd15", f"{MODELS}/sd15", 25, 7.5, "open"),
    "sd15_cfg1_min":    ("sd15", f"{MODELS}/sd15", 25, 1.0, "minimal"),
}


def jobs(cond):
    style = CONDITIONS[cond][4]
    return [dict(job=f"s{si:02d}_{k:02d}", subject=s, probe="base", prompt=STYLES[style].format(s=s),
                 seed=7000 * si + k) for si, s in enumerate(SUBJECTS) for k in range(SEEDS)]
