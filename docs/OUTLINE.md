# Paper outline (v2, 2026-10-11)

> Rewritten for the framing decided on 2026-10-11: the visual audit method is the headline and the model study is its evidence (`RESEARCH_PROPOSAL.md` v2). The earlier system-centred outline (in Chinese) is in git history. Limits: CG&A template, ≤14 pages including bios, about 8,000 words, abstract ≤150 words, **≤20 references**, 1–3 sidebars of 200–500 words (sidebar citations do not count).

## Title
**Visual Auditing of Appearance Defaults in Text-to-Image Models** (working title)

## Abstract (draft, ~140 words; numbers to be filled from the study)
When a prompt leaves lighting, framing or palette unspecified, a text-to-image model decides them, and evaluators who switch models or settings need to know what changed. A diversity score cannot tell whether outputs now settle somewhere else (displacement) or settle more tightly in the same place (concentration), nor whether a pooled conclusion holds for every subject. We present a visual audit method that places the outputs of many declared model configurations on human-validated appearance axes, calibrates each axis with explicit requests, separates displacement from concentration with stated uncertainty, and traces every reading to the images. We apply it to 12 open configurations on 24 everyday subjects. Raising guidance [concentrates / displaces] appearance in both families studied, and [N] of [M] apparent configuration differences change direction across subjects. [N] experts used the method to [result]. We close with lessons for auditing generative models visually.

## Contributions
1. **An audit method** for appearance defaults: validated aspect axes, reference-prompt calibration, separation of displacement and concentration with practical margins, and validity conditions for comparing configurations (declared settings, package changes not attributed to one factor, fixed baselines, per-subject reporting).
2. **A visual design and tool** that supports three audit tasks: (T1) displacement vs concentration, (T2) pooled vs per-subject, (T3) tracing a difference to images and catching measurement or attribution errors.
3. **An audit of 12 open configurations** with bounded findings: guidance in two families (primary), descriptive cross-configuration and per-subject structure, one distillation package case.
4. **An expert evaluation** (3–5 experts) on the three tasks against a box-plot / score-table-plus-image-grid baseline, and lessons for visual auditing of generative models.

## Structure and word budget
| § | Content | Words | Material |
|---|---|---|---|
| 1 Introduction | Defaults decide unspecified appearance; evaluators compare configurations; one score merges displacement and concentration and hides per-subject reversals; contributions | 900 | `STATUS.md`, pilot results |
| 2 Related work | Default and diversity measurement (DefaultShift, GRADE, DIMCIM, attribute-conditional benchmark, Vendi); comparing image sets (VisDiff, CompCon); visual analytics of generated images (ViBEx, Varif.ai, CUPID, GROVE); visual comparison (Gleicher) | 700 | `RESEARCH_PROPOSAL.md` §7, `RELATED_WORK.md` |
| 3 Audit method | 3.1 tasks T1–T3 and the evaluator's decisions; 3.2 aspects and their validation; 3.3 why request anchors were not used (pilot negative result); 3.4 location, width, uncertainty, margins; 3.5 validity conditions | 1,500 | proposal §3–5, `annotation/`, `anchors/` |
| 4 Visual design | Views and how each serves T1–T3; design rationale; designs we abandoned and why (projection envelopes read as spread, pooled baselines, card summaries) | 1,300 | `system/`, `DESIGN_HISTORY.md` |
| 5 Audit of 12 configurations | Setup (configurations, subjects, seeds, settings provenance); Q1 guidance; Q2 structure and per-subject reversals; Q3 distillation package vs DefaultShift; measurement failures the images exposed | 1,500 | study data |
| 6 Expert evaluation | Participants, tasks, baseline condition, what changed in their judgements, difficulties | 700 | sessions in week 4 |
| 7 Lessons and limitations | Lessons for visual auditing; limits: CLIP proxies, calibration from configurations inside the study, 32 seeds, 24 subjects, demographics out of scope | 600 | |

**Sidebars:** (1) *Displacement or concentration?* A two-panel toy example: two configurations with the same diversity score but different locations, and one with a shift but no loss of variety (~250 words). (2) *Product defaults*: the three closed services, descriptive and dated (~300 words).

## Figures and table
| # | Content | Task |
|---|---|---|
| 1 (teaser) | Same subject and seeds at CFG 1 and CFG 4: image strips on one calibrated axis, showing a concentration and a displacement side by side | T1 |
| 2 | Method pipeline: aspects → validation → standardized location and width → audit views | — |
| 3 | Interface overview with the three tasks marked | T1–T3 |
| 4 | Guidance in two families: per-subject calibrated distributions, endpoints with intervals | T1 |
| 5 | A pooled conclusion that reverses across subjects | T2 |
| 6 | A traced measurement failure or invalid attribution | T3 |
| Table 1 | Aspect validation: human agreement, abstentions, anchor separation, encoder agreement; kept or dropped | — |

## References (budget 20; identifiers checked 2026-10-11 unless marked)
1. DefaultShift — arXiv 2608.21784
2. CompCon, Discovering Divergent Representations between Text-to-Image Models — arXiv 2509.08940 (ICCV 2025)
3. GRADE — arXiv 2410.22592
4. DIMCIM — arXiv 2506.05108
5. Attribute-conditional diversity benchmark — arXiv 2511.10547
6. VisDiff, Describing Differences in Image Sets with Natural Language — arXiv 2312.02974 (CVPR 2024)
7. ViBEx — arXiv 2504.19703
8. Varif.ai — DOI 10.1145/3715336.3735847
9. CUPID — DOI 10.1111/cgf.15086
10. GROVE / Beyond One Output — arXiv 2604.18724 (verify)
11. Classifier-free guidance — arXiv 2207.12598
12. Stage-wise dynamics of CFG — arXiv 2509.22007 (ICLR 2026)
13. CLIP — arXiv 2103.00020
14. SigLIP 2 — arXiv 2502.14786
15. Gleicher 2018, Considerations for visualizing comparison — DOI 10.1109/TVCG.2017.2744199
16. Vendi Score — arXiv 2210.02410
17. Qwen-Image technical report — arXiv 2508.02324
18. An Exploration of Default Images in Text-to-Image Generation — arXiv 2505.09166
19. OpenBias — arXiv 2404.07990 (verify)
20. Open slot: FLUX.2 release or Adversarial Diffusion Distillation (arXiv 2311.17042), decided when §5 is written

Sidebar-only citations (not counted): Artificial Hivemind (arXiv 2510.22954), POET (arXiv 2504.13392), CADS (arXiv 2310.17347), PrompTHis (DOI 10.1109/TVCG.2024.3408255).
