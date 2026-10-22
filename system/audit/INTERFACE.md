# Interface: final design and its rationale (rev10, 2026-10-22)

This file fixes the interface of the audit tool and gives, for every view, mode and control, the task it serves and why nothing else in the interface serves it. It is the basis for the design section of the paper (Section 4) and for the owner's review of the interface.

## 1. Principles
1. **Established encodings only:** positions on common scales, distributions (dots, densities, box-like bands), scatter plots with density contours, small multiples, a diverging colour scale for polarity.
2. **One encoding per quantity:** a quantity is drawn in one view; other views refer to it through linking, not by drawing it again.
3. **Text on demand:** views carry pole words and panel titles only; numbers, settings and statements appear on hover or selection.
4. **Every view is indispensable:** each answers a question that no other view answers.
5. **No appearance switches:** a control may change *what is analysed* (pair, aspect, subject, mode of a panel), never only *how it looks*. A mode exists only if it serves a task that the other modes of the same panel cannot serve.
6. **Contours only on metric spaces:** density contours summarize where points lie *in units that mean something*. They are drawn on the configuration map (scale units) and nowhere on the t-SNE appearance map, whose distances and areas have no metric meaning.

## 2. Tasks
- **T1 Displacement or concentration:** does a change of model or setting move the typical output, narrow it, or both?
- **T2 Pooled or per subject:** does a pooled conclusion hold for every subject?
- **T3 Trace to images:** does a reading survive a look at the images, and is the contrast attributable to one setting?
- **T4 Verify a language claim:** is a statement made in language (a VLM description, a rewritten prompt, an axis name) supported by the images?

## 3. Views
| Panel | View | Question it answers (task) | Why no other view answers it |
|---|---|---|---|
| A | **Configuration map** (◎) | Where does every configuration settle on this aspect, and how tightly; which pair to compare (entry to T1) | The only view of all 12 configurations at once; density contours of the selected pair's 24 per-subject positions show whether a configuration is consistent across subjects (metric axes: scale units) |
| A | **Contrast overview** (▦) | Do the designed contrasts behave alike across aspects (e.g. distillation repeats guidance) (T1 across contrasts) | The only view of all designed contrasts × aspects; the scatters (E) show one pair |
| A | **VLM statements** (❝) | Which statements did the VLMs make about this pair, and which does the audit confirm (T4 overview) | The only view of all statements; the trail follows one |
| A | **Audit trail** (⛓) | Does one claim survive measurement, subject and images (T3, T4) | The only view that places claim, measurement, subject and images in one chain with a verdict at each link |
| B | **Subject × configuration matrix** with shift column | Where does each configuration put each subject; which subjects go against the pooled shift (T2) | The only per-subject view across all configurations; the shift column and ⇄ count expose reversals |
| C | **Image axis** | What do the images of A and B look like along the aspect (T3) | The only view of the images themselves, placed by their scores |
| D | **Paired seeds** (⫽) | Does each image move or do the images converge (T1 at the level of single images) | The only view that pairs an image of A with an image of B (same seed, or rank-matched and labelled so) |
| D | **All aspects of one subject** (∿) | Does one appearance change show up on several aspects at once (coupling) | The only view of all aspects together; the others show one aspect |
| D | **Appearance map** (⁘) | Is there a default the five aspects do not name | The only view not defined by the language axes; dots only, no contours (principle 6) |
| D | **Rewrites** (✎) | Does what each rewrite says match where its image lands (T4 for rewriting) | The only view that places text-side against image-side positions for every rewrite of a subject |
| E | **Contrast scatters** (five aspects) | For the selected pair, per subject: shift and spread ratio against the margins, and the pooled estimate with its interval (T1, T2) | The only view of the measured effects with their uncertainty and margins |

## 4. Controls
| Control | What it changes | Task |
|---|---|---|
| A and B selectors, ⇄ swap | the pair under audit | all |
| Settings chips (⚠ n settings) | — (shows which declared settings differ) | T3: attribution |
| Aspect buttons (struck through when not validated for the pair) | the aspect in every view | all |
| Main-view modes ◎ ▦ ❝ ⛓ | which of four questions panel A answers (Section 3) | T1, T4, T3 |
| Evidence modes ⫽ ∿ ⁘ ✎ | which of four questions panel D answers (Section 3) | T1, coupling, discovery, T4 |
| Subject selector | the subject in C, D and the trail | T2, T3 |
| ⇅ order by shift, ⇄ step through flagged subjects (matrix) | row order; the selected subject | T2: find reversals |
| Brush in a scatter | a group of subjects, highlighted in all scatters and the matrix | T2: does a group disagree |
| Margin handles in the scatters | the margins used for display, with a reset to the pre-registered values | robustness of verdicts to the margin |
| Brush on the image axis or in the rewrite view | a group of seeds, highlighted in C and D | T1, T4 at the level of images |
| Trail: ‹ › seed, ✓ / ✗, + save trail, ⤓ | the seed in the chain; the analyst's verdict; the record of findings | T3, T4; provenance |

**Removed in rev10, with the reason**
- **Figure-mode button:** it changed only the appearance (persistent numbers for paper figures). It is now a URL parameter (`index.html?figure`) used to produce figures, not a control of the analysis.
- **Verdict glyphs on the aspect buttons:** they repeated the pooled estimate that the contrast scatters (E) already show (principle 2).
- **Findings board:** it duplicated the audit trail's saved list as a second record of findings. The trail records any finding: a claim, an aspect of a pair, a subject and a seed, with the analyst's verdict.
- **Density contours on the t-SNE appearance map** (rev8): principle 6.

## 5. Linking
| Action | Effect |
|---|---|
| Choose a pair (selectors, a point or arrow on the map, a glyph in the overview, a statement) | every view recomputes for the pair |
| Choose an aspect (buttons, a scatter, a row in ∿) | every view switches to the aspect |
| Hover a subject (scatter dot, matrix row) | the subject is highlighted in all scatters, the matrix and the map |
| Click a subject (scatter dot, matrix row, trail stage 2) | C, D and the trail show that subject |
| Hover or brush images or seeds (C, D) | the same images or seeds are highlighted in C and D |
| Select a statement (❝) and press ⛓ | the trail starts from that statement |
| Click a saved trail | the pair, aspect, subject, seed, statement and verdict of that trail are restored |

## 6. Palette ("cool and crisp")
Cool light surfaces (page #f3f6fa, white panels with hairline borders), ink #0b1220. Data hue is reserved: **A blue #2563eb, B orange #f97316** (dataviz validator: CVD ΔE 32.8, normal 41.5, pass). Configuration families are shapes (circle Stable Diffusion, square FLUX.2, triangle Qwen-Image), not hues. The pole colour scale runs **teal #0d9488 → grey → ochre #a16207** (validated against A and B in all pairs). Status colours follow the reference status steps (good #0ca30c, critical #d03b3b, warning #e0a100, muted for "no shift") and never stand alone: every status mark carries a symbol (✓ ✗ ≈ ○ ⇄ ⊘) or a shape (a contradicted statement is a hollow glyph). Selection is a dark ring, so no extra hue competes with A and B.
