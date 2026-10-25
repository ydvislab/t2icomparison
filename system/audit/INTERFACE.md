# Interface: final design and its rationale (rev10, 2026-10-22; comparison set rev12, 2026-10-24; review fixes rev13, 2026-10-25)

The principles below are design requirements, each tied to a task; they are hypotheses for the expert study, not results (external review 2026-10-25, `docs/REVIEW_2026-10-25_interface.md`). This file fixes the interface of the audit tool and gives, for every view, mode and control, the task it serves and why nothing else in the interface serves it. It is the basis for the design section of the paper (Section 4) and for the owner's review of the interface.

## 1. Principles
1. **Familiar encodings first:** positions on common scales, distributions (dots, densities, interval bars), scatter plots with density contours, small multiples, parallel coordinates, a diverging colour scale for polarity. The one compound glyph (the contrast overview) carries a persistent key.
2. **Each quantity has one home view; repetition is deliberate and marked.** A measured effect is drawn in E, the images in C, the distributions in D. Overview (▦) and provenance (⛓) views restate a quantity only as a summary that points to its home view (the trail gives numbers and "→ E", "→ C" instead of redrawing the scatter and the images' axis).
3. **Text on demand:** views carry pole words and panel titles only; numbers, settings and statements appear on hover or selection.
4. **Each view serves a task no other view serves as directly** (Section 3 names the task). This is a design claim to be tested, not a demonstrated fact.
5. **No appearance switches:** a control may change *what is analysed* (pair, aspect, subject, mode of a panel), never only *how it looks*. A mode exists only if it serves a task that the other modes of the same panel cannot serve.
6. **Contours only on metric spaces:** density contours summarize where points lie *in units that mean something*. They are drawn on the configuration map (scale units) and nowhere on the t-SNE appearance map, whose distances and areas have no metric meaning.
7. **Many configurations: identity by labelled slots, role by colour.** The views compare a *set* of up to six configurations. Where a view has categorical slots (a matrix column, a shift column, an image lane, a parallel axis, a row in the distributions, a small multiple, a row of the contrast overview), each member has its own slot, in the same set order everywhere. Where position encodes a measurement (the map, the scatters), identity is carried by a direct label, placed so that labels do not overlap. Colour encodes only the two roles: the **reference** (blue; every contrast starts from it, and every reference-relative view puts 0 at its median) and the **focus** (orange; the member the per-subject views detail). Hue never has to tell six members apart. Statement- and rewrite-level views stay pairwise, with the reason given in Section 4.

## 2. Tasks
- **T1 Displacement or concentration:** does a change of model or setting move the typical output, narrow it, or both?
- **T2 Pooled or per subject:** does a pooled conclusion hold for every subject?
- **T3 Trace to images:** does a reading survive a look at the images, and is the contrast attributable to one setting?
- **T4 Verify a language claim:** is a statement made in language (a VLM description, a rewritten prompt, an axis name) supported by the images?
- **T5 Compare many configurations:** across a set of configurations (a chain such as guidance 1 → 4 → distilled, the paper's Q1 → Q3 chain, or a family such as 4B / 9B, base / distilled), which members move the typical output, which narrow it, for which subjects, and how one seed travels through all of them?

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
| Comparison set bar: up to six chips in chain order; click a chip: make it the focus; click its dot: make it the reference; × removes a member; "+ add" or shift-click on the map adds one; ⇄ swaps reference and focus | the configurations under audit and their roles | all; T5 |
| Settings chips (⚠ n settings) | — (shows which declared settings differ) | T3: attribution |
| Aspect buttons (struck through when not validated for the pair) | the aspect in every view | all |
| Main-view modes ◎ ▦ ❝ ⛓ | which of four questions panel A answers (Section 3) | T1, T4, T3 |
| Evidence modes ⫽ ∿ ⁘ ✎ | which of four questions panel D answers (Section 3) | T1, coupling, discovery, T4 |
| Subject selector | the subject in C, D and the trail | T2, T3 |
| ⇅ order by shift, ⇄ step through flagged subjects (matrix) | row order; the selected subject | T2: find reversals |
| Wheel and drag on the configuration map; double-click or ⟲ resets | the visible region of the map (semantic zoom: marks keep their size; marks outside the view become edge triangles) | entry to T1 when configurations overlap (the Stable Diffusion family) |
| Brush in a scatter | a group of subjects, highlighted in all scatters and the matrix | T2: does a group disagree |
| Margin handles in the scatters | the margins used for display, with a reset to the pre-registered values | robustness of verdicts to the margin |
| Brush on the image axis or in the rewrite view | a group of seeds, highlighted in C and D | T1, T4 at the level of images |
| Trail: ‹ › seed, ✓ / ✗, + save trail, ⤓ | the seed in the chain; the analyst's verdict; the record of findings | T3, T4; provenance |

**Removed in rev10, with the reason**
- **Figure-mode button:** it changed only the appearance (persistent numbers for paper figures). It is now a URL parameter (`index.html?figure`) used to produce figures, not a control of the analysis.
- **Verdict glyphs on the aspect buttons:** they repeated the pooled estimate that the contrast scatters (E) already show (principle 2).
- **Findings board:** it duplicated the audit trail's saved list as a second record of findings. The trail records any finding: a claim, an aspect of a pair, a subject and a seed, with the analyst's verdict.
- **Density contours on the t-SNE appearance map** (rev8): principle 6.

**The comparison set in every view (rev12, 2026-10-24; rev13, 2026-10-25)**

| View | With a set of K members (identity by position) | Why it stays pairwise, where it does |
|---|---|---|
| Set bar (header) | K chips in chain order; roles REF and FOCUS | — |
| A ◎ configuration map | every member ringed and labelled; an arrow from the reference to every member; density contours for reference and focus | contours for more than two members overlap into an unreadable field (tested with five); a member's subjects appear on hover, its spread is read in E and D |
| A ▦ contrast overview | the set is its own group (one row per member, reference → member) above the designed contrasts; the focus row shaded; a persistent key decodes the glyph | — |
| B matrix | the member columns come first, in set order (rewritten configurations included), the other configurations follow narrower; **one shift column per member** (reference → member) on one common scale, each with its own reversal outlines and edge triangles for shifts beyond the scale; a click on a column's label makes that member the focus | the ⇄ badge and the ⇅ order follow the focus; any member becomes the focus with one click |
| C image axis | one lane per member | — |
| D ⫽ paired seeds | parallel coordinates, one axis per member in set order; neighbours that share starting noise are joined seed by seed, others are matched by rank and dashed (the same correspondence as the two-member view and the trail) | the ▶ morph animation was cut: it moved images by seed ID even where seeds do not share starting noise |
| D ∿ distributions | per retained aspect, one row per member: 10–90% range, IQR, median; a member–aspect not validated by people is faded and marked ⊘ | overlaid densities are kept for two members only |
| D ⁘ appearance map | small multiples, one panel per member on the same layout; hovering an image marks its seed in every panel | — |
| E contrast scatters | per-subject dots for reference → focus; every other member as a labelled diamond with its 90% interval, faded on its own validity; brushing subjects adds, for every member, a hollow diamond at the brushed subjects' median | 24 subjects × K members in one scatter would hide the subjects |
| A ❝ statements, ⛓ audit trail | a saved trail stores the whole set, its order, the evidence mode, the margins and the brushed subjects and seeds, and restores them | a VLM statement and a rewritten prompt are claims about one pair, so they are checked on reference → focus; a subject-level statement is dropped when another subject is chosen; a rewrite is read only against its own base |

**Zoom keeps the density estimate (2026-10-24):** the kernel bandwidth of the map's contours is fixed in scale units, so zooming magnifies the same density instead of re-estimating it at a finer bandwidth (which broke the contours into one blob per subject and changed the spread reading with the zoom level, against principle 6).

**Fixed after the interface review (rev13, 2026-10-25)**
- **One origin:** every reference-relative view is centred on the reference's median. Before, the parallel coordinates and the lanes used the first member of the set.
- **Validity per member:** unknown validity counts as not validated. E fades only the reference → focus marks for that pair; every other member fades on its own validity in E, C, D.
- **Seed selections:** a selection survives hovering another subject.
- **Edge triangles for configurations:** a configuration outside the zoomed map becomes an edge triangle.
- **Verdict symbols:** the statement verdict bar carries symbols (✓ ≈ ○ ✗ ?).
- **Header and scatter labels:** the set bar wraps onto its own row when long. The scatter pole words read as change (← / →), with a key "↔ shift · ↕ spread".
- **Margins:** a margin change redraws the trail and the statements.
- **Baseline:** `baseline.html` gets the same comparison set (a reference and up to five configurations in every table, box plot, image grid and text list). Its rewrite text is no longer truncated.

## 5. Linking
| Action | Effect |
|---|---|
| Choose a reference or focus (set bar, a point or arrow on the map, a glyph or row in the overview, a matrix shift-column label, a scatter diamond, a statement) | every view recomputes; set members keep their slots |
| Choose an aspect (buttons, a scatter, a row in ∿) | every view switches to the aspect |
| Hover a subject (scatter dot, matrix row) | the subject is highlighted in all scatters, the matrix and the map |
| Click a subject (scatter dot, matrix row, trail stage 2) | C, D and the trail show that subject |
| Hover or brush images or seeds (C, D) | the same images or seeds are highlighted in C and D |
| Select a statement (❝) and press ⛓ | the trail starts from that statement |
| Click a saved trail | the pair, aspect, subject, seed, statement and verdict of that trail are restored |

## 6. Palette ("cool and crisp")
Cool light surfaces (page #f3f6fa, white panels with hairline borders), ink #0b1220. Data hue is reserved for the two roles: **reference blue #2563eb, focus orange #f97316** (dataviz validator: CVD ΔE 32.8, normal 41.5, pass). Further members of the comparison set are ink (#3d4a5c) and are told apart by position and label (principle 7). A hue per member was tried and rejected: with A and B fixed, the validator (all pairs, protan and deutan, clear of the pole scale and the status colours) admits only one further hue in both themes, and the first version's violet was indistinguishable from A for deuteranopes (ΔE 0.4). Configuration families are shapes (circle Stable Diffusion, square FLUX.2, triangle Qwen-Image), not hues. The pole colour scale runs **teal #0d9488 → grey → ochre #a16207** (validated against A and B in all pairs). Status colours follow the reference status steps (good #0ca30c, critical #d03b3b, warning #e0a100, muted for "no shift") and never stand alone: every status mark carries a symbol (✓ ✗ ≈ ○ ⇄ ⊘) or a shape (a contradicted statement is a hollow glyph). Selection is a dark ring, so no extra hue competes with A and B.
