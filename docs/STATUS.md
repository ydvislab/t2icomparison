# Status (2026-10-13, evening)

> One page: what evidence exists, where the work stands, and what is missing. Questions and methods: `RESEARCH_PROPOSAL.md` v2. Plan, generation design and decisions: `PLAN.md`. Outline: `OUTLINE.md` v2.

## 1. In one sentence
When a prompt leaves appearance unspecified, a text-to-image model decides it (a **generation default**). The paper presents a **visual audit method** that tells evaluators whether a change of model or setting *displaces* appearance (outputs settle elsewhere) or *concentrates* it (outputs settle more tightly in the same place), whether a pooled conclusion holds for every subject, and that traces every reading to the images. A study of 12 open configurations is its evidence; guidance in two families is the primary intervention.

**Direction changes:** 2026-10-10 the focus moved from the system to the models; 2026-10-11, after an external review (`REVIEW_PROPOSAL.md`: significance 7, novelty 4, soundness 3, venue fit 5 for the v1 proposal), the owner made the audit method the headline and narrowed the claims.

## 2. Novelty (`RESEARCH_PROPOSAL.md` §7)
- **Taken, background only:** default diversity falls as models improve (DIMCIM, GRADE); guidance reduces diversity (CFG literature, stage-wise CFG analysis); distilled replacements shift attribute distributions, with direction of moved mass separated from entropy change and with guidance probes (DefaultShift, which also audits background, lighting and viewpoint); prompt-conditioned appearance differences between models can be discovered (CompCon, VisDiff).
- **Remaining:** a visual audit on shared, human-checked, interpretable aspect axes across many declared configurations, which separates displacement from concentration, shows when a pooled conclusion reverses across subjects, makes measurement uncertainty visible and traces every reading to the images; and the within-model guidance contrast in two families on scene-level appearance. (Calibrated axes were part of this until the anchor pilot failed on 2026-10-12; the claim is narrower without them, and the difference from DefaultShift and CompCon must be stated explicitly in the paper.)

## 3. Pilot evidence (small, local, motivation only)
Measured with DINOv2 / VLM; not human-checked.
- **Default diversity falls across model generations** (`experiments/hidden_or_lost/RESULTS.md`, 1,368 images): Vendi for 16 images of the same minimal prompt drops from SD1.5 7.45 to SDXL-Turbo 3.47 to klein 2.79, and it drops for all 12 subjects. Compliance when an attribute is requested rises (atypical requests 0.73, 0.73, 0.93).
- **Mostly due to sampling settings** (`experiments/caption_density/RESULTS.md`, 480 images): within klein-base, CFG 1→4 lowers Vendi from 5.95 to 2.32 (6/6 subjects). Distilled klein lowers it a further 0.49. Prompt phrasing, including "any style", changes it by about ±0.01.
- **What is fixed differs by model:** SDXL-Turbo converges on palette (sepia/brown), while klein converges on content and composition. Turbo's composition median is +1.31 on "a house" and −1.33 on "a kitchen", and pooling the two cancels it out (+0.07).

## 4. Study design (approved 2026-10-10; questions narrowed 2026-10-11, see `RESEARCH_PROPOSAL.md` §3)
- **Prompts:** 24 minimal prompts in 6 categories plus 6 control prompts (`PROMPTS.md`).
- **Groups:** 12 open-model groups (SD1.5, SDXL base, SDXL-Turbo, SD3.5 Large, FLUX.2 [dev], klein-base 4B at CFG 4 and 1, klein 4B, klein-base 9B, klein 9B, Qwen-Image-2512 at CFG 4 and 1) and 3 closed product defaults (GPT-image, Gemini image, Seedream).
- **Samples:** 32 seeds per main prompt and 16 per control prompt for open models: 9,216 study images (generated). 16 per prompt for closed models, about 1,440 API calls (not yet run).
- **Measurement:** 5 aspects frozen after human check round 1 (sat, medium, shot, tone, bg; `experiments/model_study/analysis/frozen_aspects.json`), scored with CLIP ViT-L/14 (`aspects/score.py`). Location shift Δ = (median_B − median_A) / s_aspect with a fixed per-aspect scale computed from all 12 configurations (`frozen_scale.json`); spread = log IQR ratio within each subject; margins 0.5 and log 1.5 (`frozen_margins.json`); hierarchical bootstrap. Prompt-implied aspects are excluded per subject. No calibration by request prompts (pilot failed); the 6 control prompts check that each aspect responds.

## 5. Infrastructure (2026-10-12)
- **GPU server:** 2 × H200 NVL (141 GB each). Agreed split: GPU 0 for this project, GPU 1 for the TVCG2026 project. A second TVCG2026 vLLM service (GLM-4.5V-FP8) had taken GPU 0 on 2026-10-10; it was stopped on 2026-10-12 at the owner's request, and GPU 0 is back with this project.
- **Code and data on the server:** the owner's workspace `yd/t2icomparison/` (`code/`, `data/` = `T2IC_DATA`, `ops/`, `logs/`); see `docs/RUNBOOK.md` §5. The server copy of the code is at `ce17ea0`.
- **Environment:** ready and checked (torch 2.14.1+cu130, diffusers 0.41.0, transformers 5.19.0; all six pipelines import; GPU arithmetic works).
- **Weights:** all downloaded (about 290 GB), including FLUX.2 [dev], klein-base 9B and klein 9B. Provenance and the resulting design caveats are in `docs/PROVENANCE.md` (klein 4B vs 9B also changes the text encoder).
- **Study generation:** see §7 item 1 (864 images per group, `--batch 4`; tmux session `t2ic`). Groups are CLIP-scored as they finish; no contrast between groups is examined before the owner freezes the margins.

## 6. System
The audit tool (rev5, `system/audit/`, see its README) replaces the rev4.1 comparison system for the three audit tasks: configuration map (main view) with designed-contrast arrows and a contrast-overview mode; subject × configuration matrix with reversal detection; five contrast scatters with the frozen margins; paired-seed trajectories; per-subject distributions; appearance map (per-subject t-SNE); sorted image strips; settings chips with a warning when several settings differ. It is built for all 12 configurations × 24 subjects.

**Earlier version (rev4.1, `system/`, kept as design history):**
| View | Question it answers |
|---|---|
| Aspect × group matrix | Location (median tick) and spread (middle-50% bar) of every group on every aspect; one shared axis per row; optional reference group |
| Aspect distribution strip | Every image of every group placed at its score on the current aspect; one brush on the shared axis selects the same interval in all groups |
| Image space | Per-prompt t-SNE shared by all groups, for finding unexpected appearances; hulls only locate groups and are not read as spread |
| Selection panel | Share k/N per group (including 0); aspects on which the selection is skewed; the images |
| Settings and log | Settings on hover; differences from the reference group, with a "cannot attribute" warning when more than one setting differs; findings saved with their comparison conditions |

rev4.1 was built for 13 groups × 6 pilot prompts. The audit tool still has to handle groups whose settings are undeclared (the closed models).

## 7. Missing for the paper
1. **Generation: done** (2026-10-13 18:08): all 12 open configurations, 9,216 study images, CLIP-scored; final scale frozen (`experiments/model_study/analysis/frozen_scale.json`). Closed-model API runs by the owner.
2. **Calibration anchor pilot: done, calibration dropped** (2026-10-12): shot failed fidelity (Qwen-Image turned close-ups of scenes into faces), light failed the revised side-effect rule; reported as a negative result (`results/anchors_pilot/NOTES.md`, `RESEARCH_PROPOSAL.md` §4.2).
3. **Human check of aspects: round 1 done** (2026-10-12, 240 pairs from the study images, 3 annotators in the primary analysis): 5 aspects kept and frozen (sat, medium, shot, tone, bg); round 2 covers the groups generated later (G04, G05, G09–G12).
4. **Q1 primary analysis: done** (2026-10-13; `results/q1/RESULTS.md`): guidance mainly concentrates appearance; only saturation is displaced (klein-base 4B); Qwen-Image shows the same directions with smaller effects. Remaining analysis (week 3): Q1 guidance (primary), Q2 descriptive structure, Q3 one distillation case; practical margins frozen 2026-10-12 (`experiments/model_study/analysis/frozen_margins.json`); hierarchical bootstrap.
5. **Views and figures for the three audit tasks** (weeks 3–4): the audit tool covers 12 configurations × 24 subjects; the closed models still have to be added as undeclared-setting configurations.
6. **Expert evaluation** (week 4): 3–5 experts, the three tasks, against a box-plot or score-table-plus-image-grid baseline.
7. **Writing** (weeks 4–5): English, ≤20 references, 2 sidebars; outline v2 in `OUTLINE.md`.

## 8. Main risks
- **Time:** round 2 of the human check, Q2/Q3, the encoder check, the expert evaluation and the full draft in about 4 weeks.
- **Measurement:** five aspects passed round 1; if one fails round 2 on the later configurations, it is reported per configuration or dropped. CLIP remains a proxy (the style axis was reversed), so every claim is shown with images.
- **Novelty:** DefaultShift and CompCon are close, and without calibration the method claim is narrower; every claim must rest on the human-validated visual audit (displacement vs concentration, per-subject reversals, traceability) and the guidance contrast, not on "what is fixed" in general. A fresh external novelty review of the current version is planned before submission.
- **Closed models:** settings, seeds and versions are not under our control; sidebar only, dated, no attribution.
