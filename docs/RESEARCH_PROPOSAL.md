# Research proposal: visual auditing of appearance defaults in text-to-image models

> v2, 2026-10-11, revised after an adversarial external review of v1 (`REVIEW_PROPOSAL.md`, which also summarizes what v1 proposed). Venue: IEEE CG&A regular paper, mid-November 2026. Generation of G01–G12 is running with the design in `PLAN.md` §3–4; nothing here requires regenerating it. Owner decisions are in §9.

## 1. What changed from v1
- **Claims narrowed.** v1 asked what *determines* defaults across five factors. The design cannot support that: family, scale and product contrasts change several things at once, and DefaultShift already covers distillation replacements, including direction of moved mass versus entropy change and guidance probes. v2 claims a validated visual audit with bounded empirical findings.
- **One primary intervention:** guidance, within two families. Everything else is descriptive.
- **Fewer aspects:** 4–6 aspects that pass validation, instead of 15.
- **Statistics repaired:** no pooled-spread normalization (it hid universally shared tight defaults), no sign-permutation test (degenerate), no change-on-baseline regression (mathematically coupled), no "4 of 6 categories" gate.

## 2. Question
**For a fixed set of minimal prompts and declared model configurations, which differences in image appearance are displacements (outputs settle somewhere else), which are concentrations (outputs settle more tightly in the same place), and which change from subject to subject, and how can an evaluator verify each distinction in the images?**

Contribution type for CG&A: an applied visual method for auditing generative models, demonstrated on a 12-configuration study, with bounded findings and an expert evaluation. Not claimed: a general explanation of what determines defaults; a new diversity metric; that diversity falls as models improve.

**Framing (decided 2026-10-11):** the audit method is the headline and the model findings are its evidence. Working title: *Visual Auditing of Appearance Defaults in Text-to-Image Models*.

## 3. Questions and what each can show
| | Question | Comparisons | Type |
|---|---|---|---|
| **Q1 (primary)** | Does raising guidance displace appearance, concentrate it, or both? Is the answer the same in two families? | G07 → G06 (klein-base 4B, CFG 1 → 4); G10 → G09 (Qwen-Image-2512, true CFG 1 → 4) | Within-model setting intervention; paired seeds. Note: the two pipelines implement guidance differently (Qwen-Image rescales the guided prediction), so CFG 4 is not the same dose across families |
| **Q2** | Where do configurations at their recommended settings settle, how far apart are they, and do those differences persist across subjects? | G01, G02, G04, G05, G06, G08, G09, G11 at defaults; within-subject contrasts | Descriptive. No attribution to family, scale or architecture |
| **Q3 (case)** | What does a distillation package change? | G07 → G08 (klein 4B: same CFG 1; steps 50 → 4 and checkpoint change) | One package case, positioned against DefaultShift |
| Sidebar | Closed product defaults (C1–C3) | Descriptive, dated API versions | No attribution |

Dropped as hypotheses: family relocates (not separable), scale (one pair; the text encoder also changes between klein 4B and 9B: Qwen3 2560-d vs 4096-d, verified 2026-10-12, `PROVENANCE.md`), product layer (no intervention), mode amplification (needs an errors-in-variables design; exploratory only).

## 4. Measurement
### 4.1 Aspects
Start from the 15 CLIP bipolar aspects (`aspects/aspects.py`) and keep **4–6** that pass all checks in §4.3. Priority candidates: lighting temperature, saturation, framing (shot), viewpoint (angle), depth of field, and medium (photo vs painting; treated as categorical if interpolation is not meaningful). Composite aspects (tone, composition, quality, mood, style, background/clutter) are dropped unless validation supports a precise reading.

### 4.2 Reference-prompt calibration (anchors)
- For each retained aspect, subject and pole: an explicit request prompt from a fixed template (e.g. "a city street, in warm golden light").
- **Pilot (decided 2026-10-11):** 2 aspects × 6 subjects × 2 poles × 3 phrasings × 2 references × 8 seeds = 1,152 images; jobs, decision rules and server steps in `experiments/model_study/anchors/README.md`.
- Two reference configurations (G08 klein 4B and G09 Qwen-Image-2512, recommended settings), **8 seeds** each: 6 aspects × 24 subjects × 2 poles × 2 references × 8 = **4,608 images**, before exclusions. Pilot on 2 aspects × 6 subjects first, with 2–3 alternative pole phrasings.
- Calibrated location x = (median − L)/(R − L) and calibrated width w = IQR/(R − L), where L and R are the reference medians for the two poles. Values outside [0, 1] are kept. 0 and 1 are request-conditioned reference points in score units, not physical endpoints or perceptual units, and 0.5 is not "neutral".
- Calibration is computed per reference model as well as pooled; results are shown with each reference alone. Anchor uncertainty is propagated by resampling anchor images. Cells with an unstable or small gap (R − L) are excluded rather than rescued.
- Semantic exclusions (aspects implied by the prompt) and the existing 6 control prompts are kept; anchor separation answers a different question.
- These are anchors from configurations that are themselves in the study: "fixed reference-prompt calibration", not an external ground truth.

### 4.3 Validation
1. **Human check, round 1** (`annotation/PROTOCOL.md`, existing 240 pairs): used as a *screen* for which aspects to keep.
2. **Human check, round 2** (redesigned): held-out pairs spanning small, medium and large score differences, across categories and the new models, including images behind the main comparisons; abstentions reported; uncertainty clustered by item. Also checks anchor fidelity: the requested attribute is present and the subject is preserved.
3. **Second encoder** (SigLIP 2): effect magnitudes and conclusions compared, disagreements reported (not silently filtered). This is a sensitivity check, not validation.
4. **Coupling:** correlations between retained aspects reported, so one appearance change is not counted twice.
5. **Resolution:** resizing standardizes the encoder input only; native resolution remains part of each configuration and is declared.

## 5. Analysis
- **Effect sizes first.** For each contrast and cell: Δx (calibrated location shift) and the log ratio of IQRs (within the cell, so no pooled denominator), with intervals.
- **Practical margins fixed before analysis (frozen after the anchor pilot):** e.g. |Δx| ≥ 0.15 counts as a displacement, |log IQR ratio| ≥ log 1.5 as a change in concentration. "Same place" requires the interval for Δx to lie within the margin (equivalence), not a non-significant shift.
- **Uncertainty:** hierarchical bootstrap: resample subjects within categories, resample whole image score vectors within groups (keeping seed pairing within a checkpoint), resample anchor images per reference.
- **Primary tests (pre-declared, corrected together):** for Q1, the median Δx and the median log IQR ratio across subjects, per family and aspect. Everything per cell is shown but treated as exploratory.
- **Subject dependence (Q2):** within-subject contrasts between configurations, and how their sign and size vary across the sampled subjects; category estimates with leave-one-category-out sensitivity. No variance-decomposition claim.
- **Full distributions:** every reported result is shown with its full score distribution and images, because median and IQR can hide multiple modes and minority appearances. With 32 seeds, a mode of probability 5% is missed about 19% of the time; this limits claims about rare appearances.

## 6. The visual method
The review judged a location–spread scatter with arrows to be a useful conventional plot, not a contribution by itself. The contribution is the **workflow** that makes three audit tasks possible, each tied to images:
1. **Displacement vs concentration:** for a chosen contrast (e.g. CFG 1 → 4), aligned calibrated distributions per subject, faceted by aspect, showing both endpoints with intervals and anchor images.
2. **Pooled vs per-subject:** a pooled conclusion that changes after inspecting subjects (e.g. the composition reversal between "a house" and "a kitchen").
3. **Trace to evidence:** following an apparent difference to the images and catching a measurement failure or an invalid attribution (several settings changed).
- Arrows are labelled as a setting change or a package replacement. No arrowhead-density contours in the main argument. The t-SNE view stays in the tool but out of the paper unless it answers a specific question.
- **Expert evaluation:** 3–5 experts from the group perform the three tasks on real cases and explain how their judgement changed. Baseline condition: aligned box plots or a score table plus image grid. No claims of statistically established speed or accuracy.

## 7. Novelty (corrected after review)
| Work | Covers | Difference that remains |
|---|---|---|
| **DefaultShift** (arXiv 2608.21784) | 14 distilled-replacement pairs; colour (primary), background, lighting, viewpoint by VLM in closed vocabularies; direction of moved mass vs entropy (67 of 1,152 cells with small entropy change but large shift); guidance probes (DMD2's shift aligns with increasing teacher CFG) | Object prompts and replacement pairs only; categorical TV, not calibrated continuous position and width; no within-model guidance contrast across families; no visual audit workflow. **Strongest threat.** |
| **CompCon** (arXiv 2509.08940, ICCV 2025) | Prompt-conditioned appearance differences between models (palette, night, background, clutter, style); appendix compares four models | Discovery of differences, not calibrated location and concentration under declared settings |
| **GRADE** (arXiv 2410.22592) | Object-attribute distributions for 12 models, entropy, "default behaviours", cross-model TVD, inverse scaling | Object attributes; no guidance contrast; no calibration |
| **DIMCIM** (arXiv 2506.05108) | Does-It vs Can-It for underspecified vs explicit prompts | Anchors calibrate the scale; the reachability design itself is not new |
| **Attribute-conditional benchmark** (arXiv 2511.10547) | Human-evaluated diversity incl. background, architecture, weather, time of day | Diversity ranking, not location or audit |
| **Stage-wise CFG** (arXiv 2509.22007, ICLR 2026) | Theory: guidance suppresses weaker modes and contracts within modes | Q1 is an empirical attribute-level reading; no directional prediction claimed |
| **VisDiff** (CVPR 2024), **OpenBias** (arXiv 2404.07990), **Default Images** (arXiv 2505.09166) | Describing differences between image sets (incl. SD versions); open-set bias discovery; cross-prompt default images | Comparative image-set auditing context; must be cited |
| ViBEx, Varif.ai; GROVE (VIS 2026) | Visual exploration of one output set; distributions of text outputs | Multi-configuration calibrated comparison with provenance |

**Remaining novelty** (review: 4/10 before narrowing): a validated visual audit on shared, calibrated, interpretable coordinates, with declared configuration contrasts and visible measurement uncertainty; plus the within-model guidance result in two families on scene-level appearance. Reference budget (20) goes to the closest competing work first.

## 8. Plan for the remaining five weeks
| Week | Outcome |
|---|---|
| Oct 12–18 | Freeze Q1–Q3, primary contrasts and margins; round 1 human check; pilot anchors and phrasings; record checkpoint revisions, schedulers, text encoders and actual settings |
| Oct 19–25 | Generation and anchors complete; round 2 validation; measurement pipeline frozen; failed aspects recorded; uncertainty for primary contrasts |
| Oct 26–Nov 1 | Analysis and full draft; only the views needed for the three tasks; expert sessions begin |
| Nov 2–8 | Expert evaluation; sensitivity checks (anchors, encoder, categories); no new scope |
| Nov 9–15 | Adversarial review, reproducibility audit, figures, submission |

## 9. Owner decisions (2026-10-11)
1. Framing: **the audit method is the headline** (review recommendation adopted).
2. Anchors: **pilot first** (`experiments/model_study/anchors/`); the full set is sized after the pilot.
3. Following the review: SigLIP 2 sensitivity check; closed models in a sidebar; aspects reduced to 4–6 after round 1.
4. Practical margins: the values in §5 are provisional and are frozen after the anchor pilot, before any study data is analysed.
