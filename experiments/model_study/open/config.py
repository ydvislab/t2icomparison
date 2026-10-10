"""Open-model groups G1–G12 (docs/PLAN.md §4). Settings follow each official model card (checked 2026-10-10),
except that every group uses only the minimal prompt: no negative prompt (Qwen-Image gets the single space
its pipeline needs to run true CFG), no prompt enhancement."""
import os

DATA = os.path.expanduser(os.environ.get("T2IC_DATA", "~/va4ext"))
MODELS = f"{DATA}/models"
OUT = f"{DATA}/model_study/open"
N_MAIN, N_CONTROL = 32, 16

# pipe: diffusers pipeline class; size: square side in px (native resolution from the model card);
# dtype: weights dtype; variant: diffusers weight variant; extra: additional call arguments
GROUPS = {
    "G01_sd15":           dict(pipe="StableDiffusionPipeline", path="sd15", variant="fp16", dtype="float16",
                               size=512, steps=50, cfg=7.5, year=2022),
    "G02_sdxl":           dict(pipe="StableDiffusionXLPipeline", path="sdxl", variant="fp16", dtype="float16",
                               size=1024, steps=50, cfg=5.0, year=2023),
    "G03_sdxl_turbo":     dict(pipe="StableDiffusionXLPipeline", path="sdxl-turbo", variant="fp16", dtype="float16",
                               size=512, steps=1, cfg=0.0, year=2023),
    "G04_sd35_large":     dict(pipe="StableDiffusion3Pipeline", path="sd35-large", dtype="bfloat16",
                               size=1024, steps=28, cfg=3.5, year=2024),
    "G05_flux2_dev":      dict(pipe="Flux2Pipeline", path="FLUX.2-dev", dtype="bfloat16",
                               size=1024, steps=50, cfg=4.0, year=2025),
    "G06_klein_base4b_cfg4": dict(pipe="Flux2KleinPipeline", path="FLUX.2-klein-base-4B", dtype="bfloat16",
                               size=1024, steps=50, cfg=4.0, year=2026),
    "G07_klein_base4b_cfg1": dict(pipe="Flux2KleinPipeline", path="FLUX.2-klein-base-4B", dtype="bfloat16",
                               size=1024, steps=50, cfg=1.0, year=2026),
    "G08_klein4b":        dict(pipe="Flux2KleinPipeline", path="FLUX.2-klein-4B", dtype="bfloat16",
                               size=1024, steps=4, cfg=1.0, year=2026),
    "G09_qwen_image_cfg4": dict(pipe="QwenImagePipeline", path="Qwen-Image-2512", dtype="bfloat16",
                               size=1328, steps=50, cfg=4.0, cfg_arg="true_cfg_scale", extra=dict(negative_prompt=" "),
                               year=2025),
    "G10_qwen_image_cfg1": dict(pipe="QwenImagePipeline", path="Qwen-Image-2512", dtype="bfloat16",
                               size=1328, steps=50, cfg=1.0, cfg_arg="true_cfg_scale", extra=dict(negative_prompt=" "),
                               year=2025),
    "G11_klein_base9b":   dict(pipe="Flux2KleinPipeline", path="FLUX.2-klein-base-9B", dtype="bfloat16",
                               size=1024, steps=50, cfg=4.0, year=2026),
    "G12_klein9b":        dict(pipe="Flux2KleinPipeline", path="FLUX.2-klein-9B", dtype="bfloat16",
                               size=1024, steps=4, cfg=1.0, year=2026),
}
