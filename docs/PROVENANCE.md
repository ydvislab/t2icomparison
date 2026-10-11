# Model provenance (checked 2026-10-12)

Read from the downloaded weights' `model_index.json`, scheduler and component configs on the GPU server (`$T2IC_DATA/models`). Sources: hf-mirror.com for SD1.5, SDXL-Turbo, klein-base 4B and Qwen-Image-2512; ModelScope for SD3.5 Large, FLUX.2 [dev], klein-base 9B and klein 9B; SDXL base 1.0 and klein 4B were copied from earlier downloads of the same Hugging Face repositories. Generation settings per group are in `experiments/model_study/open/config.py`; the installed software is torch 2.14.1+cu130, diffusers 0.41.0 and transformers 5.19.0.

| Weights | Pipeline | Scheduler (from the repository) | Denoiser | Text encoder(s) |
|---|---|---|---|---|
| `sd15` (fp16) | StableDiffusionPipeline | PNDM | UNet2DConditionModel | CLIP text, 768-d, 12 layers |
| `sdxl` (fp16) | StableDiffusionXLPipeline | Euler, epsilon, leading spacing | UNet2DConditionModel | CLIP text 768-d + OpenCLIP bigG 1280-d |
| `sdxl-turbo` (fp16) | StableDiffusionXLPipeline | Euler ancestral, epsilon, trailing spacing | UNet2DConditionModel | as SDXL |
| `sd35-large` | StableDiffusion3Pipeline | Flow-match Euler, shift 3.0 | SD3Transformer2DModel | CLIP-L + OpenCLIP bigG + T5-XXL |
| `FLUX.2-dev` | Flux2Pipeline | Flow-match Euler, shift 3.0, dynamic shifting | Flux2Transformer2DModel | Mistral 3 (5120-d, 40 layers) |
| `FLUX.2-klein-base-4B` | Flux2KleinPipeline | Flow-match Euler, shift 3.0, dynamic shifting | Flux2Transformer2DModel | Qwen3, 2560-d, 36 layers (identical files to klein 4B) |
| `FLUX.2-klein-4B` | Flux2KleinPipeline | as klein-base 4B | Flux2Transformer2DModel | Qwen3, 2560-d, 36 layers |
| `FLUX.2-klein-base-9B` | Flux2KleinPipeline | as klein-base 4B | Flux2Transformer2DModel | Qwen3, **4096-d**, 36 layers (identical files to klein 9B) |
| `FLUX.2-klein-9B` | Flux2KleinPipeline | as klein-base 4B | Flux2Transformer2DModel | Qwen3, 4096-d, 36 layers |
| `Qwen-Image-2512` | QwenImagePipeline | Flow-match Euler, shift 1.0, dynamic shifting | QwenImageTransformer2DModel | Qwen2.5-VL, 3584-d, 28 layers |

## Consequences for the design
- **klein 4B vs 9B is not a pure scale contrast:** the text encoder changes too (2560-d vs 4096-d Qwen3). This confirms the external review's concern (`REVIEW_PROPOSAL.md` point 2); scale stays out of the hypotheses.
- **Within each guidance pair** (G06/G07 klein-base 4B, G09/G10 Qwen-Image-2512) the weights, scheduler, steps and resolution are identical; only the guidance scale differs.
- **Distillation package (Q3, G07 → G08):** same text encoder, VAE and scheduler configuration; the transformer checkpoint and the step count (50 → 4) change.
- **Shared components** were verified by file hash before linking: klein-base 4B uses klein 4B's text encoder, tokenizer and VAE; klein 9B uses klein-base 9B's.
- **SDXL base vs SDXL-Turbo** also differ in scheduler (Euler vs Euler ancestral) and timestep spacing, in addition to the checkpoint, steps, guidance and resolution.
