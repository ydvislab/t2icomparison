# Paper progress: completed steps and to-do steps

*2026-10-13. Ordered as the paper will present them. Every experimental detail that the paper's logic depends on is listed with its source in this repository. The paper logic draft is `PAPER_DRAFT.md` (Chinese: `PAPER_DRAFT_zh.md`).*

---

# Part I: Completed steps

## 1. Problem and motivation (Introduction; sidebar 1)

### 1.1 Pilot study A, "hidden or lost?"
Source: `experiments/hidden_or_lost/RESULTS.md`, 2026-10-01; background only, because DIMCIM already reports the main finding.
- **Setup:**
  - SD 1.5 (512², 25 steps, CFG 7.5), SDXL-Turbo (512², 4 steps, CFG 0) and FLUX.2 klein 4B (768², 4 steps);
  - 12 minimal prompts × 16 seeds;
  - 6 subjects × 11 explicit requests × 4 seeds;
  - 1,368 images in total.
- **Measures:**
  - DINOv2-base Vendi;
  - Qwen3.5-4B (thinking off, constrained letter choice) entropy over 5 dimensions;
  - compliance with explicit requests.
- **Findings:**
  - Default diversity falls with model generation: Vendi 7.45 → 3.47 → 2.79, a drop of 4.66 [3.36, 6.02] from SD 1.5 to klein, lower in all 12 subjects.
  - Compliance with atypical requests rises: 0.73 → 0.73 → 0.93.
  - Diversity is suppressed by default rather than lost: it can be requested back.

### 1.2 Pilot study B, "where does the collapse come from?"
Source: `experiments/caption_density/RESULTS.md`, 2026-10-02.
- **Setup:** 10 conditions × 6 subjects × 8 seeds = 480 images, 512².
- **Findings:**
  - Guidance is the main cause: klein-base CFG 1 → 4 lowers Vendi from 5.95 to 2.32 (6 of 6 subjects).
  - Distillation lowers it a further 0.49 (2.32 → 1.83) without changing dimension entropy.
  - Prompt phrasing (caption-like, "any style") changes it by about ±0.01.
  - At CFG 1, SD 1.5 and klein-base are similarly diverse, but SD 1.5 goes off-topic (on-topic rate 0.625).
- **Use in the paper:** motivates guidance as the primary intervention, and shows that "less diverse" hides *what* was fixed. For example, Turbo fixes palette (sepia) while klein fixes content and composition.

### 1.3 Positioning
Sources: `NOVELTY_CHECK.md`, `RESEARCH_PROPOSAL.md` §7, `REVIEW_PROPOSAL.md`.
- **Taken by others, used as background:** diversity falls (DIMCIM, GRADE); guidance reduces diversity (CFG; stage-wise CFG analysis); distilled replacements shift attributes (DefaultShift, the closest work); differences between image sets can be discovered (CompCon, VisDiff); single-model visual exploration (ViBEx, Varif.ai).
- **External adversarial review of proposal v1 (2026-10-11):** significance 7/10, novelty 4/10, soundness 3/10, venue fit 5/10. The verdict was "reject as written; salvageable with narrowing". **v2 adopted every point:**
  - the audit method is the headline;
  - guidance is the only primary intervention;
  - 4–6 validated aspects instead of 15;
  - repaired statistics;
  - an expert evaluation against a baseline.

## 2. Requirements and design history (Visual design; Lessons)
Sources: `DESIGN_HISTORY.md`, `REVIEW_PROTO3.md`, `system/history/`, `results/design_history/`.

### 2.1 Earlier prototypes, 2026-10-02
| Version | Design | Outcome |
|---|---|---|
| Prototype 2 | Juxtaposition of 3 models: per-group average image, aspect × group box plots, thumbnail strips | Does not scale to many groups; weak coordination between views |
| Prototype 3 rev1–2 | Gleicher's taxonomy: superposition (shared projection) and explicit encoding (aspect × group matrix) for the overview, juxtaposition only for selected groups; a brush on a shared axis | The skeleton that was kept |
| Prototype 4 | PrompTHis-style setting-change graph | Rejected: its edges have no meaning for independent model samples |
| rev3 | Projection-centred view with thumbnail markers | Too cluttered |
| rev3.1 | Cluster cards | Rejected: "not a visualization design" |
| rev4 | Clean projection with density contours, minimal text | External review: visualization contribution 3/10. It found four errors: contours read as spread, hidden groups changed the baseline, stacked thumbnails, inconsistent selection |
| rev4.1 | Corrections 1–4 | Superseded by rev5 |

### 2.2 Lessons kept for the paper
1. Projection envelopes are not spread.
2. Hiding data must not move the statistical baseline.
3. Pooling prompts hides reversals (Turbo composition: house +1.31, kitchen −1.33, pooled +0.07).
4. A comparison must carry its settings (the old "distillation" contrast changed weights, steps and guidance at once).
5. Coordinated views need some repeated cues.
6. Displayed position and selection must agree.
7. Measurements must be traceable to images.

### 2.3 Owner's requirements for the visual design
- established encodings (distributions, scatter + contours);
- little text, details on hover;
- no duplicated encodings;
- views that are indispensable;
- a main view with linked auxiliary views on one adaptive screen;
- all configurations visible at once, not only pairs;
- D3;
- smooth lines.

## 3. Study design (Section 3.1)
- **Prompts** (`PROMPTS.md`, `experiments/model_study/prompts.py`):
  - 24 minimal, uncontroversial subjects in 6 categories × 4;
  - 6 control prompts;
  - prompt-implied aspects excluded per subject (in/out for 8 subjects).
- **Configurations** (`PLAN.md` §4, `experiments/model_study/open/config.py`): 12 open configurations at model-card settings.
  - Stable Diffusion family:
    - G01 SD 1.5 (50 steps, CFG 7.5, 512²);
    - G02 SDXL (50 steps, CFG 5, 1024²);
    - G03 SDXL-Turbo (1 step, CFG 0, 512²);
    - G04 SD3.5 Large (28 steps, CFG 3.5, 1024²).
  - FLUX.2 family:
    - G05 FLUX.2 dev (50 steps, guidance 4, 1024²);
    - G06/G07 klein-base 4B (50 steps, CFG 4 / 1);
    - G08 klein 4B (4 steps, CFG 1);
    - G11 klein-base 9B (50 steps, CFG 4);
    - G12 klein 9B (4 steps, CFG 1).
  - Qwen-Image-2512:
    - G09/G10 (50 steps, true CFG 4 / 1, 1328², negative prompt " ").
- **Designed contrasts:**
  - guidance only: G07 → G06 and G10 → G09;
  - packages: G07 → G08 (klein distillation), G02 → G03 (SDXL → Turbo), G11 → G12 (klein 9B distillation).
- **Seeds:** 32 per main prompt (16 per control), the same list for every configuration (seed = 100000 · prompt index + k), giving 9,216 study images.
- **Determinism:** in bf16 the outputs change slightly with batch size (about 5% of pixels by more than 8/255 for klein 4B, with the same content). The batch size is therefore fixed at 4 for every group, recorded in the metadata, and enforced when a run resumes.
- **Provenance** (`PROVENANCE.md`): pipeline, scheduler, denoiser and text encoder are read from every set of weights.
  - klein 4B vs 9B also changes the text encoder (Qwen3 2560-d vs 4096-d), so scale is not tested as a cause.
  - SDXL vs Turbo also differ in scheduler and timestep spacing.
  - Qwen-Image rescales its guided prediction, so CFG 4 is not the same dose as klein's CFG 4.
- **Infrastructure** (`RUNBOOK.md` §5): 2 × H200 server, GPU 0 for this project, 35.2 GPU-hours of generation on one H200 (study and anchor pilot, from the run logs); environment pinned (torch 2.14.1+cu130, diffusers 0.41.0, transformers 5.19.0).

## 4. Measurement and its validation (Section 3.2; Table 1)
- **Aspects:** 15 bipolar CLIP ViT-L/14 aspects. Score = similarity to the right pole − similarity to the left pole. Images are resized to 512 px before encoding (`aspects/score.py`).
- **Calibration-anchor pilot: a negative result** (`experiments/model_study/anchors/`, `results/anchors_pilot/NOTES.md`).
  - Design: 2 aspects × 6 subjects × 2 poles × 3 phrasings × 2 reference models × 8 seeds = 1,152 images. Four decision rules were fixed before the run.
  - **shot:** no phrasing passed. Qwen-Image drew a man's face for "an extreme close-up of a kitchen / market", which CLIP scored as perfectly separated.
  - **light:** every phrasing separated the poles and looked right, but the side-effect rule failed: the AUC rule saturated, and its revised effect-size version failed narrowly at 0.55 against a limit of 0.5. The cause is that warm/cool requests also changed time of day and mood.
  - A second, post-hoc revision was considered and rejected. **Calibration is dropped** (owner decision); a fixed per-aspect scale is used instead.
- **Human check, round 1** (`annotation/PROTOCOL.md` §5, §7; `results/annotation_study/`):
  - **Pairs:** 240 same-subject pairs drawn from the study images (6 configurations scored at the time). Per aspect: 12 large-gap and 4 small-gap pairs, spread over 16 subjects and 6 categories; no image reused; seed 20261012.
  - **Rule fixed before labelling:** an aspect is kept if agreement with CLIP is at least 0.75 on large-gap pairs and "can't tell" is at most 40%.
  - **Annotators:** 4 independent annotators. One was excluded for never using "can't tell" (0% against 17–39%), a protocol violation. The primary analysis uses 3; the 4-annotator analysis is kept as a sensitivity check. A leave-one-annotator-out check identifies which verdicts are stable.
  - **Page fixes found while piloting:** answers were lost when initials were entered late, and annotators needed a "both images at the same pole" rule. The fixes did not change the pairs (checked by hash).
  - **Results (3 annotators):**
    - stable pass: sat 0.92, medium 0.90, shot 0.90, tone 0.94, mood 0.87, bg 0.81;
    - unstable pass: inout;
    - stable fail: style 0.17 (CLIP reversed), quality 0.50, dof 0.62, center 0.65, clean and time (too many "can't tell");
    - fail: light 0.72, angle.
  - **Frozen 2026-10-12** (`frozen_aspects.json`, commit 0dc66d1): **sat, medium, shot, tone, bg**. Mood was dropped because it moves with tone; inout is shown in the tool only.

## 5. Analysis (Section 3.3; Section 5)
- **Frozen before any contrast was examined** (`frozen_margins.json`, commit e5c5883, 2026-10-12):
  - Δ = (median_B − median_A) / s_aspect, with a displacement margin of 0.5;
  - spread = log IQR ratio, with a margin of log 1.5;
  - "same place" and "same spread" by equivalence of the 90% interval;
  - a hierarchical bootstrap;
  - 20 primary tests (2 families × 5 aspects × 2 effects), Holm-corrected.
- **Operational details fixed before the final run** (`q1_primary.py` header, commit 38ad8ed, 14:47):
  - 10,000 replicates;
  - subjects resampled within categories; seeds paired and whole score vectors resampled;
  - two-sided bootstrap p;
  - verdict rules.

  The code was tested only in a mode that prints no effects, and on synthetic data with known answers (a +1 shift gives 1.00, ×0.5 gives 0.50, Holm values are correct).
- **Scale:** computed from all 12 configurations (9,216 images) and frozen at 18:11 (`frozen_scale.json`). The run was checked byte-identical to the committed script.
- **Q1 result** (`results/q1/RESULTS.md`): raising guidance mainly concentrates appearance.
  - klein-base 4B, concentration beyond the margin: sat ×0.51, medium ×0.53, tone ×0.49, bg ×0.65; shot ×0.68 is below the margin.
  - Displacement only in saturation, toward vivid: +0.65 [+0.43, +0.93].
  - Qwen-Image shows the same directions with smaller effects: saturation concentrated (×0.64) and shifted below the margin (+0.39); tone shifts toward modern within the "same place" margin.
  - Robust when any one category is left out.
  - Saturation shifts toward vivid in 15 (klein) and 10 (Qwen) of 24 subjects, toward muted in none.
  - **Correction:** the preliminary claim of a tone displacement in both families was withdrawn.

## 6. The visual audit system (Section 4)
Sources: `system/audit/`, README.
- **Pipeline:** `build.py` prepares scores, the scale, provenance, thumbnails and a per-subject t-SNE of CLIP embeddings (cosine, perplexity 30, seed 0, CPU threads capped). `index.html` (D3 v7) computes every contrast in the browser, using the same definitions as the analysis script.
- **Layout:** one adaptive screen (tested at 1280×760, 1440×900 and 1920×1080) with a **main view** and linked **auxiliary views**:

| View | Task |
|---|---|
| Configuration map (main): all 12 configurations by typical location and spread; designed contrasts as arrows (solid = guidance, dashed = package); off-scale per-subject positions shown as edge triangles | Q2, entry to T1 |
| Contrast overview (main, second mode): designed contrasts × aspects as glyphs (arrow = displacement, circle against a reference circle = spread, ⇄n = reversed subjects) | T1, Q1 vs Q3 |
| Subject × configuration matrix with a per-subject shift column, reversal flags, stepping and ordering by shift | T2 |
| Contrast scatters (5, stacked): subjects at (Δ, log IQR ratio), frozen margins as bands, pooled estimate with interval, ⚠ when several settings differ | T1, T2, T3 |
| Paired-seed trajectories: solid when A and B share the starting noise, rank-matched dashed otherwise | T1 |
| Distributions of one subject (smooth densities, image ticks) | T1 |
| Appearance map: per-subject t-SNE with A/B density contours | defaults outside the 5 aspects |
| Image strips sorted along the aspect; the same seed highlighted across configurations | T3 |

## 7. Case material found with the system (Section 5; exploratory except where noted)
- **Case 1, guidance concentrates first** (formal Q1 result above). The contrast overview also shows the klein distillation row with the same pattern, stronger (Q3, not yet formally tested).
- **Case 2, pooled "no change" hides opposite shifts** (SDXL → Turbo): pooled saturation +0.17 while 10 subjects become more vivid and 7 more muted (⇄7 in the tool; ⚠ 4 settings differ).
- **Case 3, model signatures** (Q2, exploratory): Qwen-Image frames closer (shot −1.6); SDXL is painting-like, muted and busy; SDXL's tone default depends strongly on the subject.
- **Measurement failures caught through images** (T3): the reversed style axis; the "close-up" faces.

---

# Part II: To-do steps (in order)

| # | Step | What exactly | Done when |
|---|---|---|---|
| 1 | **Pre-register Q2 and Q3** — *done 2026-10-13*: `experiments/model_study/analysis/frozen_q2q3.json` and `q2_q3.py`, committed before any run on the study data; tested on synthetic data with planted effects (all recovered) and in `--check-code` mode. Run on the server: `python experiments/model_study/analysis/q2_q3.py` (writes `results/q2/`, `results/q3/`). Disclosure in the JSON: some of these contrasts were already seen in the audit tool, so Q2/Q3 are pre-specified descriptive analyses, not blind tests | (as originally planned) | Script header and a frozen JSON committed |
| 2 | **Human check, round 2** | About 90–120 pairs per annotator from the configurations not in round 1 (G04, G05, G09–G12), on the 5 frozen aspects only; same rule; the same 3 annotators | Each frozen aspect still passes on the new configurations, or is reported per configuration |
| 3 | **Second encoder (SigLIP 2) sensitivity** | Promised in proposal §4.3: re-score with SigLIP 2 and compare Q1 conclusions; report disagreements | Q1 table with both encoders |
| 4 | **Run Q3 and Q2** | With the pre-registered rules; the per-subject reversal counts become formal descriptive results | `results/q2/`, `results/q3/` |
| 5 | **Task and requirement grounding** | Short formative interviews (2–3 model developers or evaluators, about 20 minutes each) or a documented task analysis from the literature and the external reviews, deriving T1–T3 and the design requirements | A requirements table that the design section cites |
| 6 | **Case studies written as analyst workflows** | 2 main cases (guidance; pooled vs per subject) and 1 short case (signatures or measurement failure), each as a sequence of interactions with screenshots, what was found, and how it was verified in images | Figures 4–6 and their text |
| 7 | **Expert evaluation** | 3–5 experts, about 40 minutes each. Three tasks (T1–T3) on real cases, each with the system and with a baseline (box plots or a score table plus an image grid), counterbalanced. Record findings, confidence, time and think-aloud; semi-structured interview. Check the institution's ethics requirements | Section 6 with per-task outcomes and quotes |
| 8 | **Closed models (sidebar)** | The owner runs GPT-image, Gemini and Seedream locally (`experiments/model_study/closed/`); add them to the tool as undeclared-setting configurations | Sidebar with dated API versions |
| 9 | **Optional: guidance dose sweep** | klein-base 4B and Qwen-Image at CFG 1, 2, 3, 4, 6 (no training; about 8–10 GPU hours on GPU 0) so that the system shows dose-response paths. It strengthens Q1 and the visual argument; it is not required | Decide by Oct 18 |
| 10 | **Figures** | Teaser (the same subject at CFG 1 / 4 on the trajectory view), method pipeline, interface overview, case figures, design-alternatives figure, Table 1 (aspect validation) | All figures at print resolution |
| 11 | **Writing** | Expand `PAPER_DRAFT.md`; related work with ≤ 20 verified references; 2 sidebars; limitations | Full draft by Nov 1 |
| 12 | **Submission checks** | CG&A template, ≤ 14 pages, abstract ≤ 150 words, reference verification, reproducibility audit (scripts, frozen files, commits), an external adversarial review | Submit by mid-November |
