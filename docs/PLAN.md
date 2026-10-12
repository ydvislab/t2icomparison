# Plan

> Updated 2026-10-11 after the owner adopted the external review's recommendation: the paper's headline is the visual audit method, and the model study is its evidence. The research questions, measurement and analysis are in `RESEARCH_PROPOSAL.md` v2 (review: `REVIEW_PROPOSAL.md`); this file keeps the generation design, timeline and decisions. Earlier versions are in git history.

## 1. Positioning
- **Headline: a visual method for auditing appearance defaults** in text-to-image models (working title: *Visual Auditing of Appearance Defaults in Text-to-Image Models*). It lets an evaluator tell displacement (outputs settle elsewhere) from concentration (outputs settle more tightly in the same place), see when a pooled conclusion changes across subjects, and trace every reading to the images.
- **Evidence: a study of 12 open configurations** on 24 minimal prompts, with guidance (two families) as the primary intervention and descriptive cross-model and per-subject structure. Bounded findings only.
- **Not claimed:** a general explanation of what determines defaults; a new diversity metric; that diversity falls as models improve (DIMCIM, GRADE) or that guidance reduces diversity (CFG literature, stage-wise CFG analysis).
- **Scope:** offline comparison of many models and settings. Interactive tools for creators are out of scope.

## 2. Research questions
See `RESEARCH_PROPOSAL.md` §2–3: Q1 (primary) guidance displaces or concentrates, in klein-base 4B and Qwen-Image-2512; Q2 where configurations settle at their recommended settings and whether differences persist across subjects (descriptive); Q3 one distillation package case (klein-base 4B → klein 4B); closed models in a sidebar. Family, scale and product layer are not tested as causes.

## 3. Prompts
24 minimal prompts in 6 categories × 4, plus 6 control prompts. See `PROMPTS.md`. 32 seeds per main prompt for open models, 16 for controls and for closed models. One fixed seed list per prompt, shared by all open-model groups.

## 4. Models and settings
Settings marked "verify" must be checked against the official model card and the installed diffusers version before generation.

| Group | Model | Setting | Role |
|---|---|---|---|
| G1 | Stable Diffusion 1.5 | model-card default (CFG 7.5, 50 steps, 512²) | Earlier generation (regenerated; the pilot images used 25 steps and other seeds) |
| G2 | SDXL base 1.0 | model-card default (verify) | Distillation pair with G3; Stability generation ladder |
| G3 | SDXL-Turbo | 1 step, CFG 0, 512² | Distilled (regenerated; the pilot images used 4 steps and other seeds) |
| G4 | SD3.5 Large | model-card default (verify) | Stability generation ladder; another family |
| G5 | FLUX.2 [dev] 32B | model-card default (guidance 4, verify steps) | Scale within the FLUX.2 family |
| G6 | FLUX.2 klein-base 4B | CFG 4 | Guidance pair with G7; scale pair with G5 |
| G7 | FLUX.2 klein-base 4B | CFG 1 | Guidance pair with G6 |
| G8 | FLUX.2 klein 4B | 4 steps, CFG 1 (distilled) | Distillation pair with G6 |
| G9 | Qwen-Image-2512 | true CFG 4, 50 steps, empty negative prompt | Another family (LLM text encoder) |
| G10 | Qwen-Image-2512 | true CFG 1 | Guidance pair with G9: tests whether the guidance effect generalises across families |
| G11 | FLUX.2 klein-base 9B | model-card default (CFG 4, 50 steps) | Scale ladder 4B → 9B → 32B with G6 and G5; distillation pair with G12 |
| G12 | FLUX.2 klein 9B | model-card default (distilled; verify steps) | Distillation pair with G11 |
| C1 | GPT-image (OpenAI API) | API default; rewriting off if possible | Product default |
| C2 | Gemini image model (Google API) | API default | Product default |
| C3 | Seedream (ByteDance, Volcengine API) | API default; rewriting on/off if it can be toggled | Product default; product-layer effect |

Designed comparisons for RQ2:
- **Guidance:** G6 vs G7 and G9 vs G10. Each pair changes only guidance, in two families.
- **Distillation:** G2 vs G3, G6 vs G8 and G11 vs G12. Distillation also changes steps and guidance; this is reported as the distillation package, not as a single factor.
- **Scale within a family:** G6 (4B) → G11 (9B) → G5 (32B). The two klein-base models share architecture family, settings (CFG 4, 50 steps) and release, so 4B vs 9B is the cleanest scale contrast; the 32B [dev] model also differs in training and is reported as a family-internal contrast.
- **Generation within a vendor:** G1 → G2 → G4.
- **Family at defaults:** G4 vs G5 vs G9.
- **Product layer:** C1–C3. Settings are not declared, so they are compared on location and spread only, with no attribution.

Dropped: HunyuanImage (too large; not needed for any comparison).

## 5. Venue limits (IEEE CG&A, checked 2026-10-07)
- CG&A template; at most 14 pages including title, authors, abstract, captions, acknowledgements, references and bios; about 8000 words; abstract ≤150 words.
- **At most 20 references** (hard limit). 1–3 sidebars of 200–500 words each; sidebar citations do not count toward the 20.
- First-round review target is about 2 months; a short promotional video is needed for the final version.
- Open question: whether CG&A remains the best venue for a model-centred study (see section 7).

## 6. Timeline
| Week | Dates | Tasks | Who |
|---|---|---|---|
| 1 | 10/7–10/13 | Outline; human-check materials; refocus on the models; prompt set; server environment | Done except environment |
| 2 | 10/14–10/20 | Download models; CUDA generation scripts; generate G1–G12 (about 10,400 images); closed-model API runs; round 1 human check of aspects (existing pairs) | Executor; owner + 1 student for annotation; owner for API keys |
| 3 | 10/21–10/27 | Aspect scores for all groups; control-prompt check; round 2 human check on new images; analysis for RQ1–RQ3 with per-prompt and per-category statistics | Executor; owner + student |
| 4 | 10/28–11/3 | Scale the system to about 13 groups; figures; English draft; expert feedback sessions | Executor drafts, owner revises; owner arranges experts |
| 5 | 11/4–11/10 | Revision; external review; CG&A template; verify the 20 references; submit | Both |

This timeline is tight for a study of this size. Week 2 is the critical path.

## 7. Owner decisions
| Item | Decision |
|---|---|
| Add open models | **Yes**: G2, G4, G5, G9, G10 (2026-10-10); G11, G12 added the same day for the scale ladder |
| Closed models | Generated by the owner locally with `experiments/model_study/closed/` (2026-10-10) |
| Closed models | **Yes**, three product defaults (2026-10-10); reported in a sidebar, descriptive only (2026-10-11) |
| HunyuanImage | **No** (2026-10-10) |
| Paper focus | ~~The models; the system is the instrument (2026-10-10)~~ → **the visual audit method is the headline; the model study is its evidence** (2026-10-11, following the external review) |
| Prompt set | **24 prompts** in `PROMPTS.md` (2026-10-10) |
| Human check | Round 1 (existing 240 pairs) screens aspects; round 2 to be redesigned with graded pairs and the new models (2026-10-11) |
| Aspects | **Frozen 2026-10-12** after round 1 (3 annotators; one excluded for never using "can't tell"): sat, medium, shot, tone, bg (`experiments/model_study/analysis/frozen_aspects.json`) |
| Calibration anchors | Pilot run (2 aspects × 6 subjects × 2 poles × 3 phrasings × 2 reference models × 8 seeds, 2026-10-11/12); **dropped after the pilot** (2026-10-12): shot failed fidelity, light failed the revised side-effect rule; no second post-hoc revision; full anchor set cancelled. See `RESEARCH_PROPOSAL.md` §4.2 and `results/anchors_pilot/NOTES.md` |
| Second encoder | SigLIP 2 as a sensitivity check (2026-10-11, following the review) |
| Practical margins | **Frozen 2026-10-12**: |Δ| ≥ 0.5 in units of a fixed per-aspect scale (pooled within-cell SD over all 12 open configurations), IQR ratio ≥ 1.5, equivalence by 90% intervals; `experiments/model_study/analysis/frozen_margins.json` |
| Expert feedback | 3–5 experts from the group, arranged by the owner |
| Venue and deadline | **IEEE CG&A, mid-November 2026** (2026-10-11); CVPR 2027 (deadline 2026-11-16) considered and declined for this paper (2026-10-12) |
| Follow-up paper | A separate project (own repository, own server folder, own session) develops a method for the vision venues (ICCV 2027 or later): a displacement/concentration decomposition of guidance and a corrected guidance method. Boundary: this paper claims the visual audit method and bounded descriptive findings; the follow-up claims the mechanism and the method. Shared assets (prompt set, anchor calibration, generated images) may be reused there with citation, but neither paper reports the other's main results as its own (2026-10-12) |
| Author order and affiliations | Later |

## 8. Owner to-do
1. API keys for the closed models: set them as environment variables on the server yourself (keys never go into the repository or the chat). State which of the three are available.
2. FLUX.2 [dev] licence: accept the non-commercial licence on Hugging Face with your own account. The server reaches Hugging Face only through a mirror, so check whether a ModelScope copy exists before arranging a token.
3. Do round 1 of the aspect human check with one student and export the CSV (`annotation/PROTOCOL.md`).
4. Arrange 3–5 experts for 10/28–11/3; check whether ethics review is required.
5. Decide the venue and deadline (section 7).
