"""Hidden or Lost? Pilot: is the diversity newer T2I models drop hidden (recoverable by asking) or lost?"""
import os
DATA_ROOT = os.environ.get("T2IC_DATA", os.path.expanduser("~/va4ext"))  # external data drive (images, models)

DATA = os.environ.get("HOL_DATA", os.path.join(DATA_ROOT, "hidden_or_lost"))
MODELS = os.path.join(DATA_ROOT, "models")

# model key -> loader settings (native-ish resolution, recommended sampler settings)
GENERATORS = {
    "sd15":       dict(year=2022, kind="sd15",  path=f"{MODELS}/sd15", size=512, steps=25, cfg=7.5),
    "sdxl":       dict(year=2023, kind="sdxl",  path=f"{MODELS}/sdxl", size=768, steps=25, cfg=6.0),
    "sdxl_turbo": dict(year=2023, kind="sdxl",  path=f"{MODELS}/sdxl-turbo", size=512, steps=4, cfg=0.0),
    "klein4b":    dict(year=2026, kind="klein", path=f"{MODELS}/FLUX.2-klein-4B", size=768, steps=4, cfg=1.0),
}

# minimal, underspecified subjects (no medium, lighting, framing, colour or quality words)
SUBJECTS = ["a car", "a dog", "a person reading a book", "a kitchen", "a house", "a bird on a branch",
            "a city street", "a cup of coffee", "a doctor", "a bicycle", "a living room", "a mountain"]
BASE_SEEDS = 16

# reachability probes: explicit requests for one value of one dimension
PROBE_SUBJECTS = ["a car", "a dog", "a person reading a book", "a kitchen", "a city street", "a cup of coffee"]
PROBE_SEEDS = 4
PROBES = {  # name: (template, dimension, expected option index, typicality)
    "night":      ("{s}, at night",                                   "lighting", 1, "typical"),
    "sunset":     ("{s}, at sunset",                                  "lighting", 2, "typical"),
    "bw":         ("a black and white photo of {s}",                   "color",    2, "typical"),
    "closeup":    ("an extreme close-up of {s}",                       "framing",  0, "typical"),
    "wide":       ("{s}, wide shot from far away",                     "framing",  2, "typical"),
    "oil":        ("an oil painting of {s}",                           "medium",   1, "typical"),
    "cartoon":    ("a cartoon illustration of {s}",                    "medium",   2, "typical"),
    "crayon":     ("a child's crayon drawing of {s}",                  "medium",   4, "atypical"),
    "amateur":    ("an amateur, blurry, badly lit phone snapshot of {s}", "quality", 1, "atypical"),
    "ugly":       ("an ugly, poorly composed, overexposed photo of {s}",   "quality", 2, "atypical"),
    "lowq":       ("a very low quality, pixelated JPEG of {s}",        "quality",  2, "atypical"),
}
# for 'amateur' both "amateur snapshot" (1) and "blurry/low quality" (2) count as compliant
ACCEPT = {"amateur": {1, 2}}

# generic dimensions measured on every image (multiple choice, last option = other/unclear where present)
DIMENSIONS = {
    "medium":   ("What kind of image is this?",
                 ["a photograph", "a painting", "a cartoon or illustration", "a 3D render", "a sketch or drawing (pencil, crayon)", "other"]),
    "lighting": ("What is the lighting / time of day?",
                 ["daylight", "night", "sunset or golden hour", "studio or indoor lighting", "unclear"]),
    "framing":  ("How is the main subject framed?",
                 ["close-up", "medium shot", "wide shot from far away"]),
    "color":    ("What best describes the colours?",
                 ["vivid and colourful", "muted or natural colours", "black and white"]),
    "quality":  ("What best describes the image quality?",
                 ["polished, professional-looking", "amateur snapshot", "blurry, low quality or badly exposed"]),
}


def jobs():
    """All (image_id, model-independent) generation jobs."""
    out = []
    for si, s in enumerate(SUBJECTS):
        for k in range(BASE_SEEDS):
            out.append(dict(job=f"base_s{si:02d}_{k:02d}", subject=s, probe="base", prompt=s, seed=1000 * si + k))
    for si, s in enumerate(PROBE_SUBJECTS):
        for pi, (p, (tpl, dim, exp, typ)) in enumerate(PROBES.items()):
            for k in range(PROBE_SEEDS):
                out.append(dict(job=f"probe_{p}_s{si:02d}_{k:02d}", subject=s, probe=p,
                                prompt=tpl.format(s=s), seed=50000 + 1000 * si + 10 * pi + k))
    return out
