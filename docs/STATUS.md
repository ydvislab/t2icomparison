# Status (2026-10-10)

> One page: what evidence exists, where the work stands, and what is missing. Plan and timeline: `PLAN.md`. Outline: `OUTLINE.md` (still written for the earlier system-centred framing; to be revised).

## 1. In one sentence
When a prompt leaves an attribute unspecified, the text-to-image model decides it (a **generation default**). This study asks what models decide, whether different models decide the same thing, and which factor (guidance, distillation, scale, family, product layer) is responsible. A visual comparison system that ties every reading back to the images is the instrument.

**Direction change on 2026-10-10:** the paper's focus moved from the system to the models. Research questions RQ1–RQ3 are in `PLAN.md` §2. A study needs more prompts, seeds and models than the earlier 13 groups × 6 prompts, so most of the measurement will be redone at the new scale.

## 2. Novelty (`NOVELTY_CHECK.md`)
- **Already published, used only as background:** default diversity falls as models improve (DIMCIM); guidance reduces diversity (CFG literature; stage-wise CFG analysis, ICLR 2026); attribute-level diversity scores for 5 models (attribute-conditional benchmark, ICLR 2026); default shift under acceleration in closed vocabularies (DefaultShift, Aug 2026); embedding-space homogenization of DALL-E 3 and Imagen 4 (a Zenodo preprint, not peer reviewed).
- **Open, and the target of this study:** *what* each model fixes (location, not only spread), whether models share defaults, which factor moves location versus spread, and whether defaults depend on the subject.
- New related work to add: GROVE (IEEE VIS 2026, distributions of LM outputs), DyEval (TVCG 2026), Vipera (CHI 2026), CHI 2026 diversity metrics vs human judgement.
- The novelty check was done without the planned cross-model reviewer (Codex could not start locally). Re-run it with the dossier in `.aris/novelty/` when available.

## 3. Pilot evidence (small, local, motivation only)
Measured with DINOv2 / VLM; not human-checked.
- **Default diversity falls across model generations** (`experiments/hidden_or_lost/RESULTS.md`, 1,368 images): Vendi for 16 images of the same minimal prompt drops from SD1.5 7.45 to SDXL-Turbo 3.47 to klein 2.79, and it drops for all 12 subjects. Compliance when an attribute is requested rises (atypical requests 0.73, 0.73, 0.93).
- **Mostly due to sampling settings** (`experiments/caption_density/RESULTS.md`, 480 images): within klein-base, CFG 1→4 lowers Vendi from 5.95 to 2.32 (6/6 subjects). Distilled klein lowers it a further 0.49. Prompt phrasing, including "any style", changes it by about ±0.01.
- **What is fixed differs by model:** SDXL-Turbo converges on palette (sepia/brown), while klein converges on content and composition. Turbo's composition median is +1.31 on "a house" and −1.33 on "a kitchen", and pooling the two cancels it out (+0.07).

## 4. Study design (approved 2026-10-10; details in `PLAN.md` §3–4)
- **Prompts:** 24 minimal prompts in 6 categories plus 6 control prompts (`PROMPTS.md`).
- **Groups:** 12 open-model groups (SD1.5, SDXL base, SDXL-Turbo, SD3.5 Large, FLUX.2 [dev], klein-base 4B at CFG 4 and 1, klein 4B, klein-base 9B, klein 9B, Qwen-Image-2512 at CFG 4 and 1) and 3 closed product defaults (GPT-image, Gemini image, Seedream).
- **Samples:** 32 seeds per main prompt for open models, which is about 10,400 images. 16 per prompt for closed models, which is about 1,440 API calls.
- **Measurement:** 15 bipolar aspects (`aspects/aspects.py`, CLIP ViT-L/14), standardized within each prompt. Location is the median; spread is the group IQR divided by the pooled IQR; both have bootstrap intervals. Prompt-implied aspects are excluded per prompt. The human check decides which aspects stay, and the control prompts check that each aspect responds.

## 5. Infrastructure
- **GPU server:** 2 × H200 NVL (141 GB each). This project uses GPU 0 only.
- **Code and data on the server:** everything is in the owner's workspace `yd/t2icomparison/` on the data disk (`code/`, `data/` = `T2IC_DATA`, `ops/`, `logs/`); see `docs/RUNBOOK.md` §5. GPU 0 is used for this project and GPU 1 is reserved for another project.
- **Network:** Hugging Face and GitHub are not reachable directly. The hf-mirror and ModelScope mirrors and the PyPI mirrors (Tsinghua, Aliyun) work. Aliyun stalled on large wheels, so the environment uses Tsinghua.
- **Environment:** `data/env` (Python 3.10, torch 2.14.1, diffusers 0.41.0 from PyPI, which is expected to include `Flux2KleinPipeline`, transformers ≥ 5.18). Installation is in progress, and the GPU check is pending.
- **Weights already on the server** (from other projects; to be linked, not copied): FLUX.2 klein 4B, DINOv2-base, SDXL base 1.0 (Hugging Face cache). Qwen-Image-Edit-2511 is present but is an editing model, not the text-to-image Qwen-Image-2512.
- **Still to download:** SD1.5, SDXL-Turbo, klein-base 4B, SD3.5 Large, FLUX.2 [dev], Qwen-Image-2512, CLIP ViT-L/14, Qwen3.5-4B.
- **Generation scripts** hard-code Apple `mps`. They need a CUDA version before any run on the server.

## 6. System (rev4.1, `system/`)
| View | Question it answers |
|---|---|
| Aspect × group matrix | Location (median tick) and spread (middle-50% bar) of every group on every aspect; one shared axis per row; optional reference group |
| Aspect distribution strip | Every image of every group placed at its score on the current aspect; one brush on the shared axis selects the same interval in all groups |
| Image space | Per-prompt t-SNE shared by all groups, for finding unexpected appearances; hulls only locate groups and are not read as spread |
| Selection panel | Share k/N per group (including 0); aspects on which the selection is skewed; the images |
| Settings and log | Settings on hover; differences from the reference group, with a "cannot attribute" warning when more than one setting differs; findings saved with their comparison conditions |

Built for 13 groups × 6 prompts. It must scale to about 13 groups × 24 prompts and handle groups whose settings are undeclared (the closed models).

## 7. Missing for the paper
1. **Generation at the new scale** (week 2): all open groups and the closed-model API runs.
2. **Human check of aspects** (weeks 2–3): round 1 on the existing pairs; round 2 on images from the new models. Known ambiguous aspects: "tone" mixes era with palette, "composition" mixes centring with symmetry, and "quality" measures professional versus casual wording.
3. **Analysis for RQ1–RQ3** (week 3): effects must hold across prompts and categories, not only in the pooled data.
4. **System scaling and figures** (weeks 3–4).
5. **Expert feedback** (week 4): 3–5 experts, about 40 minutes each.
6. **Writing** (weeks 4–5): English, ≤20 references, 1–2 sidebars. The outline must be rewritten for the model-centred framing.

## 8. Main risks
- **Time:** about 10,000 images, two human-check rounds and a reframed paper in 5 weeks. The venue and deadline are still open (`PLAN.md` §7).
- **Measurement:** if most aspects fail the human check, reduce the aspect set, or switch to human-defined aspects judged by a VLM.
- **Overlap:** the "how much" findings are taken. Every claim must be about *what* is fixed and *why*.
- **Closed models:** settings, seeds and model versions are not under our control, and services may rewrite prompts. Closed-model results are therefore reported as product defaults with dated API versions, never attributed to a single factor.
