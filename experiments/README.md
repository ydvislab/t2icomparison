# 背景实验

两个实验都只作论文的动机证据（发现本身已有人发表），同时提供比较系统的 13 组图像。

| 目录 | 问题 | 进入比较系统的组 |
|---|---|---|
| `hidden_or_lost/` | 三代模型（SD1.5、SDXL-Turbo、FLUX.2 klein）的默认多样性与"明确要求时能否做到" | 3 个模型 × 6 个共同 prompt × 16 个种子 |
| `caption_density/` | 同一模型家族内，引导、蒸馏、prompt 写法各自的影响 | 10 个条件 × 6 个 prompt × 8 个种子 |

结果和结论见各自的 `RESULTS.md`；运行步骤见 `docs/RUNBOOK.md`。

## Model study (`model_study/`)
The main study of the paper: what text-to-image models decide when a prompt leaves attributes unspecified, and which factor (guidance, distillation, scale, family, product layer) is responsible. The design is in `docs/PLAN.md` §2–4, and the prompt set is in `docs/PROMPTS.md`.

| Path | Contents |
|---|---|
| `prompts.py` | 24 minimal prompts (6 categories), 6 control prompts, prompt-implied aspects to exclude, and the job and seed list shared by all groups |
| `download_models.py` | Downloads weights in diffusers layout from hf-mirror / ModelScope, resumable |
| `open/` | Open-model groups G01–G12 (`config.py`, settings from the model cards) and the CUDA generation script `gen.py` |
| `anchors/` | Calibration anchors: explicit pole requests that define the calibrated aspect scale; the pilot job set, its analysis and the decision rules (`anchors/README.md`) |
| `closed/` | Closed-model product defaults (OpenAI, Gemini, Seedream) run locally through their APIs; see `closed/README.md` |
