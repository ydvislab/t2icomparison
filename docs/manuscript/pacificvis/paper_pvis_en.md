> **Superseded (2026-10-27):** the paper was restructured as a visual analytics system paper (draft 4, `latex/main.tex`): problem characterization with a formative study, three techniques, two case studies, expert study. This file keeps draft 3 for reference.

# Grounding Language in Images: Interactive Visual Analysis of Appearance Defaults in Text-to-Image Models

*PacificVis 2027 Conference Paper Track, draft 3 (2026-10-26; synced with `latex/main.tex` on 2026-10-27). From now on `latex/main.tex` is the primary text.*
- *Structure:* the experiments show how three common ways of judging default changes fail (numbers alone, language alone, eyes alone). The failures give the requirements, the system answers them, and the cases and the expert study test them.
- *Sources:* `docs/manuscript/paper_v2_en.md` (source text, numbers checked against `results/`); plan `docs/PACIFICVIS_PLAN.md`.
- *Limit:* 9 pages + 2 pages for acknowledgments and references, VGTC conference template. Target about 5,800 words of text with six figures and three tables.
- *Markers:* [pending] = result not yet available; [cite] = a verified reference still to be found (no reference is invented). Case details were read in the running system on 2026-10-26; screenshots in `figures/` (`shots.mjs`).
- *Name:* "DefaultScope" is a working name.

---

## Abstract

When a prompt leaves composition, colour or medium unsaid, a text-to-image model decides, and modern models decide almost the same way every time. Evaluators who change guidance, distil a model or add an LLM prompt rewriter need to know how these appearance defaults change. They judge in three ways: by numbers from an image–text encoder, by descriptions from a vision-language model (VLM), or by looking at a few images.

On 9,216 images from 12 open configurations, with two LLM rewriters and two VLM describers, we show that each way fails on its own:
- **Numbers alone:** an axis defined in words ran backwards; the strongest effect of a rewriter lay on an axis people reject; pooled "no change" hid opposite shifts in 38 of 60 cases; which aspects moved depended on the encoder.
- **Language alone:** VLMs reported differences between two sets from the same model in 98–100% of answers.
- **Eyes alone:** people reading the same 8-image grids found 3 of 10 real shifts.

From these failures we derive requirements for DefaultScope, a visual analytics system. It combines measurement over all seeds with the analyst's judgement of the images:
- the analyst compares a set of configurations against a reference;
- every verdict is computed live under adjustable margins and either of two encoders;
- every number and every language claim leads to the images that decide it;
- new aspects are defined in words but count only after the analyst has checked them.

Four cases and an expert study against a tables-and-images baseline [pending] show what the system adds.

**Keywords:** visual analytics, model comparison, text-to-image generation, LLM-assisted analysis, provenance.

---

## 1 Introduction

A prompt such as "a kitchen" names a subject and nothing else. The model decides the rest: whether the image is a photograph or a painting, a close-up or a wide view, muted or vivid, plain or cluttered. Modern models make nearly the same decision every time. In a pilot with 16 images per minimal prompt, the Vendi score [1] fell from 7.45 for Stable Diffusion 1.5 to 2.79 for FLUX.2 klein. Within one model, it fell from 5.95 to 2.32 when classifier-free guidance [2] rose from 1 to 4. We call these unrequested, recurring decisions **appearance defaults**.

The people who build, distil and select image models change these defaults with routine decisions: raising guidance, distilling to four steps, swapping a checkpoint, adding an LLM that rewrites the prompt (FLUX.2 ships one [21]). To know what such a decision did, they rely on one of three things:
1. **Numbers:** diversity scores [1, 3, 4, 5], or scores along attributes defined in words for an image–text encoder [17].
2. **Language:** a VLM asked to describe how two models differ [10, 11].
3. **Their eyes:** a look at a few images from each side.

Each gives an answer quickly, and each answer can be wrong. We measured how.

**Contributions:**
1. **A study of three failure modes** (Sec. 4), on 12 open configurations, two LLM rewriters and two VLM describers, partly pre-registered:
   - numbers without images mislead;
   - language without measurement asserts differences that are not there;
   - eyes without measurement miss real ones.
2. **A measurement framework** (Sec. 3) and **design requirements** derived from the failures (Sec. 4.4). The framework covers human-checked, language-defined aspects, per-subject shift and spread under explicit margins, and validity conditions.
3. **DefaultScope** (Sec. 5), a visual analytics system that answers each failure with a design:
   - a set-based comparison against a reference;
   - live verdicts under adjustable margins and two encoders;
   - linked views from configurations to single images;
   - language claims traced to image evidence;
   - user-defined aspects that count only after the analyst's check;
   - a findings log that replays the analysis state.
4. **Four cases and an expert study** (Secs. 6–7, [pending]) that compare the system with a baseline offering the same numbers and images without visualization and linking.

---

## 2 Related Work

**Visual analytics for generative image models.**
- ViBEx [12] and Varif.ai [13] support exploring how outputs vary for one model or prompt.
- CUPID [14] visualizes distributions of generated images.
- PromptMagician [23] helps users refine prompts by exploring the images they produce.

These systems help users understand one model's output space. We compare several declared configurations, and verify the claims made about them in language.

**Visual comparison.** Gleicher's framework [15] distinguishes juxtaposition, superposition and explicit encoding. DefaultScope uses each:
- **explicit encoding:** per-subject shift and spread ratio;
- **superposition:** configurations on one map;
- **juxtaposition:** images and set members in aligned lanes and small multiples.

Comparing many items calls for layouts that give each item a stable place [26, 27]; we follow this for the members of a comparison set, which keep their slot in every view instead of a hue. Effects are shown with their intervals against explicit margins, following work on how uncertainty displays are read and evaluated [28].

**LLMs and VLMs in visual analytics.** Language models are used across analysis workflows, for example to recommend insights and summarize findings [24].
- **Describing differences:** VisDiff [10] and CompCon [11] describe differences between image sets in natural language.
- **Benchmarks:** they score whether such descriptions name a reference difference [10], or whether a model identifies a change between two images, with "no difference" as one option [22].

None calibrates a description against a human-validated measurement, or gives the analyst a visual route from a sentence to the images. We treat generated language as a claim to verify, in line with work on provenance in visual analysis [25].

**Measuring defaults and diversity.**
- **Diversity scores:** Vendi [1], DIMCIM [3], GRADE [4] and attribute-conditioned benchmarks [5] quantify diversity.
- **Default images:** studies of default images [7] characterize the outputs of minimal prompts.
- **Distillation:** DefaultShift [6] observes that distillation acts like raised guidance.
- **Prompt rewriting:** rewriters add variety in aggregate [19, 20].

These works report how much outputs converge. They do not separate a move of the typical output from a narrowing around it, per subject, and they offer no path from the number to the images.

---

## 3 Measurement Framework

**Data.**
- **Prompts:** 24 minimal prompts in six categories (people, animals, objects, interiors, outdoor scenes, activities), each naming only a subject.
- **Configurations:** 12 open configurations at their model-card settings:
  - SD 1.5, SDXL, SDXL-Turbo, SD 3.5 Large;
  - FLUX.2 dev;
  - FLUX.2 klein-base 4B at guidance 4 and 1, klein 4B, klein-base 9B, klein 9B;
  - Qwen-Image-2512 [16] at guidance 4 and 1.
- **Images:** every configuration renders every prompt from the same 32 seeds, giving 9,216 images. Every setting is read from the weights and declared.

**Language-defined aspects with a human check.** An image's score on an aspect is its CLIP ViT-L/14 [17] similarity to a right-pole phrase minus its similarity to a left-pole phrase, for example "muted desaturated colors" vs. "vivid saturated colors".
- **The check:** people check an aspect before use. Annotators see a same-prompt image pair with a large score gap and pick the image closer to the right pole, or "can't tell".
- **The rule,** fixed before labelling: an aspect is kept for a set of configurations if at least 75% of the decidable judgements agree with the encoder and at most 40% are "can't tell".
- **Second encoder:** all scores are repeated with SigLIP 2 [18] under the same poles.

**Shift and spread.** For a contrast A → B, per subject and aspect:
- **shift:** Δ = (median_B − median_A)/s. Here s is a per-aspect scale, frozen once from the 12 configurations, so one unit is the typical spread of one configuration on one subject;
- **spread ratio:** IQR_B / IQR_A.

**Margins and inference.**
- **Margins,** frozen before any comparison was examined:
  - a shift of at least 0.5 units is a displacement;
  - a ratio beyond 1.5 or below 1/1.5 is a change in spread;
  - "same place" and "same spread" require the 90% interval to lie inside the margin.
- **Bootstrap:** a hierarchical bootstrap resamples subjects within categories and images within cells, with seeds paired when A and B share a checkpoint.
- **Verdicts in the system:** the system marks a change only when the whole 90% interval lies beyond the margin. This is stricter than the confirmatory rule of the experiments (significant after correction, estimate beyond the margin).
- **Pre-registration:** primary tests are Holm-corrected. Before each analysis, we committed the aspects, margins, scale and code; for the LLM study also the rewriters, VLM prompts and scoring rules.

**Validity conditions.**
1. Every setting is declared.
2. A contrast that changes several settings is a package and is not attributed to one of them.
3. A pooled result is never read without its per-subject structure.
4. Baselines do not move when configurations are shown or hidden.
5. Measurement validity is stated per configuration set and per encoder.
6. A claim stated in language is a hypothesis to check against the images.

---

## 4 How Judging Without Visual Analysis Fails

We report the experiments by the way of judging they test.

### 4.1 F1: Numbers without images mislead
**F1a. A number can measure the wrong thing.** Three rounds of human checks decided which aspects enter the analysis (Table 1).
- **Round 1** (240 pairs): 7 of 15 candidate aspects passed, and five were frozen: saturation, medium (photo vs. painting), shot (close-up vs. wide), tone (modern vs. vintage) and background (plain vs. busy). "Style" ran backwards: CLIP called polished photographs "stylized", and people agreed with its direction on only 17% of pairs.
- **Round 2:** validity did not transfer to the later, more homogeneous configurations.
- **Round 3:** on images from rewritten prompts, background failed with 0.38. CLIP's "busy" is more often the opposite of people's reading than the same.
- **The headline effect was a measurement failure.** The strongest result of the pre-registered rewriting study is FLUX.2 dev's background moving toward "busy" after rewriting (+0.67 [+0.47, +0.91], 17 subjects up, none down), on exactly this axis. Read as a number, it would have been the headline finding.

**Table 1.** Agreement with the encoder on large-gap pairs, CLIP / SigLIP 2 (✗ = fails the frozen rule).

| Aspect | Round 1 (first six) | Round 2 (later six) | Round 3 (rewrites) |
|---|---|---|---|
| saturation | 0.92 / 0.92 | 0.77 / 0.73 ✗ | 0.90 / 0.90 |
| medium | 0.90 / 0.90 | 0.77 / 0.77 | 0.77 / 0.77 |
| shot | 0.90 / 0.90 | 0.96 / 0.96 | 0.63 ✗ / 0.75 |
| tone | 0.94 / 0.94 | 0.64 ✗ / 0.88 | 0.89 / 0.68 ✗ |
| background | 0.81 / 0.84 | 0.70 ✗ / 0.70 ✗ | 0.38 ✗ / 0.56 ✗ |

**F1b. A pooled number hides opposite shifts.** On validated aspects, 38 of the 60 pooled comparisons that fall within the margin hide opposite shifts: at least three subjects shift beyond +0.5 and three beyond −0.5.
- **SDXL → SDXL-Turbo** (a package of five settings) is the clearest case. Every pooled shift is "same place" or unresolved, yet four of five aspects hide opposite shifts.
- **On saturation,** 9 subjects become more vivid and 6 more muted, each with its own interval excluding zero; "a horse" moves +2.33, "a bird on a branch" −2.07.

**F1c. One number merges shift and narrowing, and the shift depends on the encoder.**
- **Guidance:** in klein-base 4B, raising guidance from 1 to 4 narrows four aspects beyond the margin (saturation ×0.51 [0.43, 0.61], medium ×0.53, tone ×0.49, background ×0.65) and shifts only saturation (+0.65 [+0.43, +0.93]); 15 of 24 subjects turn vivid by at least the margin, none muted.
- **Distillation:** the distilled klein 4B (new checkpoint, 50 → 4 steps) narrows all five aspects (×0.41–0.63) and shifts saturation (+0.95). This is the guidance pattern, more strongly, as DefaultShift observed [6].
- **Second encoder:** under SigLIP 2, the narrowing holds (guidance ×0.52–0.62; distillation ×0.48–0.58, saturation +1.03). But guidance now shifts medium (+1.08), shot (−0.86) and tone (−1.59), and saturation falls below the margin (+0.44). Per-subject readings agree only moderately between the encoders (median Spearman 0.33–0.67).

A diversity score would report "less diverse" for both encoders and hide that only the narrowing is robust.

### 4.2 F2: Language without measurement asserts what is not there
**Setup (pre-registered).**
- **Describers:** Qwen3.5-4B and Mistral-Small-3.2-24B.
- **Input:** 8 vs. 8 images per subject for six contrasts, shown as two grids.
- **Questions:**
  - a free-text description;
  - constrained questions per aspect: "closer to ⟨right⟩ / ⟨left⟩ / no clear difference" and "more / less / about equally varied".
- **Truth:** the audit on all 32 seeds, on validated aspects.

**Exploratory checks,** added after the first scoring:
- **Null control:** one configuration on both sides, seeds shifted by 16.
- **Stability:** a second, disjoint draw of grids.
- **People:** the same questions answered by people (Sec. 4.3).

**Results** (Table 2).
- **Differences that are not there:** both VLMs report a shift between two sets from the same configuration in 98–100% of answers.
- **Stable answers, not sampling noise:**
  - a second draw of grids gives the same answer in 88–93% of cases;
  - where the eight shown seeds decide, they agree with the 32-seed truth in 98–100% of cases.
- **Narrowing called movement:** in 12–13 of 13 cases.
- **False pooled shifts:** a pooled shift is described in 49–50 of 50 pooled "no change" cases that hide reversals.
- **Direction is often right:** given a real difference, Mistral-24B reads the direction of variety correctly in 79% of per-subject cases.

**Other language fails in the same way.**
- **Rewritten text:** it moves toward "a photograph", while the images move toward illustration (+0.53 and +0.37, not significant after correction). Per subject, on validated aspects, the text predicts the image only for saturation (Spearman 0.42–0.53).
- **VLM-proposed axes:** six new axes proposed by a VLM (sharpness, level of detail, natural vs. idealized, contrast, lighting, texture) were understood by people ("can't tell" in 11–25% of judgements), but none passed the check (0.34–0.70).

### 4.3 F3: Eyes without measurement miss real differences
Three annotators answered the VLMs' constrained questions on 48 of the same grid pairs: 36 from the contrasts, 12 null pairs.
- **On null pairs,** their majority reported a difference in 4 of 12. The VLMs did so in 12 of 12, so the VLMs' false alarms are not forced by the grids.
- **On real shifts,** their majority found the direction in 3 of 10 (Mistral-24B: 8 of 10). Agreement among people was moderate (Fleiss' κ 0.41 for shift, 0.54 for variety).

Eight images per side are too few for a person to separate a default change from sampling noise. Yet showing 32 images per side for 24 subjects and 12 configurations is more than anyone can read without guidance.

**Table 2.** VLM answers against the audit; the lower block compares people and VLMs on the same 48 items.

| | Qwen3.5-4B | Mistral-24B | People (majority) |
|---|---|---|---|
| Per-subject shift accuracy (full set) | 0.49 | 0.48 | |
| Per-subject variety accuracy (full set) | 0.63 | 0.79 | |
| Narrowing without a shift, answered "shift" | 12/13 | 13/13 | |
| Pooled "no change" hiding reversals, described as a pooled shift | 49/50 | 50/50 | |
| **Null control: a shift reported** | **98%** | **100%** | |
| Same answer on a second draw of grids | 0.88–0.91 | 0.88–0.93 | |
| *48 items:* null items with a difference reported | **12/12** | **12/12** | **4/12** |
| *48 items:* real shifts, direction correct | 6/10 | 8/10 | 3/10 |
| *48 items:* variety correct | 13/18 | 15/18 | 12/17 |

### 4.4 What follows: tasks and requirements
No single way of judging is enough:
- **numbers** need the images and the per-subject structure;
- **language** needs a measurement to check it against;
- **eyes** need the measurement to tell them where to look.

An evaluator therefore needs to move between all three, and visual analytics is how they can.

**Tasks** (from the failures and from the decisions evaluators take):
- **T1 Shift or narrowing:** does a change move the typical output, narrow it, or both, and under which encoder? (F1c)
- **T2 Pooled or per subject:** does a pooled conclusion hold for every subject, and which subjects go against it? (F1b)
- **T3 Trust a reading:** is the aspect valid for these configurations, and can the contrast be attributed to one setting? (F1a)
- **T4 Verify a language claim:** is a VLM statement, a rewrite or an axis name supported by the images? (F2)
- **T5 Compare many configurations:** along a chain or a family, which members move or narrow appearance, and for which subjects?

**Requirements:**
- **R1 Explore, do not report:** every verdict is computed from the data in view, under margins and an encoder the analyst can change. (F1c)
- **R2 Many configurations, one reference:** configurations are compared as a set against an explicit reference, identified by position and label rather than hue. (T5)
- **R3 Every reading reaches the images:** from any number, a path leads to its subjects and images, chosen by the measurement over all seeds. (F1b, F3)
- **R4 Language is a hypothesis:** statements, rewrites and axis names are linked to the evidence that decides them; validity is shown per configuration and encoder; new axes count only after a human check. (F1a, F2)
- **R5 Findings are reproducible:** a conclusion is stored with the full analysis state and can be replayed. (all)

**Table 3.** From failure to design, case and evaluation.

| Failure (evidence) | Requirement | Design in DefaultScope | Case | Expert task |
|---|---|---|---|---|
| F1a an aspect measures the wrong thing (style, background on rewrites) | R4 | validity mark ⊘ per member and encoder; user-defined aspects with an in-tool check | 6.3 | T3 |
| F1b pooled numbers hide reversals (38 of 60) | R3 | per-member shift columns, reversal badge, subject dots around the pooled diamond | 6.2 | T2 |
| F1c shift and narrowing merged; shifts encoder-specific | R1 | shift × spread scatters, margin handles, encoder switch | 6.1 | T1 |
| F2 VLMs assert differences; text and image disagree | R4, R3 | statements with live verdicts, audit trail, rewrite view | 6.4 | T4 |
| F3 a few images are not enough | R3, R1 | images placed on the axis over all seeds, paired-seed lines, brushing | all | all |

---

## 5 DefaultScope

DefaultScope is a single-screen web system (D3) with five linked panels (Fig. 4).
- **Computation:** a build step precomputes the encoder scores of all 12,288 images (the 9,216 study images and 3,072 from rewritten prompts); everything else is computed in the browser. Recomputing every interval of a contrast (six aspects, 24 subjects, 400 bootstrap resamples per cell) takes about 0.2 s on a desktop browser, so verdicts follow changes of the set, the encoder or the margins without a visible delay.
- **Running:** the system runs from disk; user-defined aspects need a local web server.

### 5.1 The comparison set and the encoder (R1, R2)
The header holds a **comparison set** of up to six configurations in chain order, with two roles:
- **Reference (blue):** every contrast is measured from it.
- **Focus (orange):** the member detailed by the per-subject views.

**Further members** are drawn in ink. Each is identified by its slot (a matrix column, an image lane, a parallel axis, a distribution row, a small multiple) and by a direct label, so hue never has to distinguish six members.

**Settings:** a chip lists the declared settings that differ from the reference. A ⚠ chip warns when more than one differs, so the contrast is not attributed to one setting (T3).

**Encoder switch (CLIP | SigLIP 2):** it replaces the scores, the frozen scale and the validity of every aspect. Every view and verdict is then recomputed under the other encoder. A finding that changes when the analyst switches is encoder-specific (F1c).

### 5.2 Panel A: where configurations settle
- **◎ Configuration map (T1, T5).**
  - **Encoding:** each configuration sits at its typical location (x) and typical spread (y) on the chosen aspect. Families are shapes.
  - **Arrows** join designed contrasts: solid for guidance only, dashed for a package, dotted for prompt rewriting.
  - **Density contours** of the 24 per-subject positions show whether a member behaves consistently across subjects.
  - **Zoom:** semantic zoom keeps the estimate fixed in scale units.
- **▦ Contrast overview.** One row per contrast and one glyph per aspect:
  - an arrow for the pooled shift, dashed while its interval reaches into the margin;
  - a disc against a unit ring for the spread ratio;
  - ⇄n for subjects against the pooled direction.
- **❝ VLM statements (T4).**
  - **Glyphs:** each statement about the pair is a glyph in a subject × aspect grid. Colour and a symbol give the audit's verdict: ✓ confirmed, ≈ narrowed but did not move, ○ no shift, ✗ contradicted.
  - **Live verdicts (R1):** they are recomputed from the current data, margins and encoder; a tooltip shows the frozen verdict when the two differ.
  - **Analyst's verdict:** analysts add their own ✓ or ✗.
- **⛓ Audit trail (T3, T4).** One claim (a statement, a rewrite or an axis name) is followed through four stages, with a verdict on each link:
  1. the claim;
  2. the measurement that decides it;
  3. one subject;
  4. its images (same seed, or rank-matched and labelled so).

### 5.3 Panels B–E: from subjects to images (R3)
- **B, subjects × configurations (T2).**
  - **Matrix:** each cell is coloured by where a configuration puts a subject between the poles.
  - **Shift columns:** one per member, on a common scale. Subjects that move against that member's pooled direction beyond the margin are outlined.
  - **Reversal badge:** it steps through these subjects.
- **C, images on the axis (T3).** Every image of the selected subject is placed by its score, one lane per member, with the margin band and each member's median. The measurement over all seeds decides where to look, and the images show what the number means (F3).
- **D, evidence for one subject (T1, T5).**
  - **Paired seeds:** parallel coordinates, one axis per member. Members that share the starting noise are joined seed by seed; otherwise images are rank-matched and drawn dashed. Leaning lines show a shift; converging lines show a narrowing.
  - **Distributions:** the subject on every validated aspect.
  - **Appearance map:** a shared t-SNE of CLIP image embeddings, one small multiple per member, as an index to defaults that the aspects do not name.
  - **Rewrites:** each rewrite placed by what its text says against where its image lands.
- **E, contrast scatters (T1, T2).**
  - **Encoding:** one scatter per aspect. Each subject is a dot at (shift, log spread ratio) with its interval; the margins are bands; the pooled estimate and every further member are labelled diamonds.
  - **Margin handles:** dragging them changes the margins for exploration, and every verdict updates.
  - **Brushing:** brushing subjects highlights them everywhere and adds the brushed subjects' median for every member.
  - **Validity:** an aspect not validated for a member, under the current encoder, is marked ⊘.

### 5.4 User-defined aspects with an in-tool check (R4)
1. **Define:** an analyst types two pole phrases. The phrases are embedded in the browser with the same CLIP text encoder, bundled and run locally. Every image is then scored from its stored embedding, exactly as the frozen aspects.
   - The bundled ONNX encoder matches PyTorch at cosine 1.0000. The tool checks itself on first use: it reproduces the stored saturation scores of all 12,288 images within 0.004 scale units.
2. **Use:** the aspect enters every view at once, marked ⊘.
3. **Check:** the analyst judges 12 large-gap pairs from the current set, blind to configuration and score. Pairs are sampled as in round 1: one image from a subject's top 15% and one from its bottom 15%. The frozen rule of Sec. 3 decides whether the aspect counts for these configurations.
4. **Record:** the result is stored with the aspect and in the findings log.

This turns F1a and the failed VLM-proposed axes into an interaction: words do not measure images until a person confirms they do.

### 5.5 Linking, provenance and design rationale
- **Linking:** choosing a member, aspect or subject in any view updates every other view.
- **Findings log (☆, R5):** a finding is stored with the whole analysis state (set and roles, encoder, aspect, subject, panel modes, margins, brushed subjects, statement, map zoom) and replays on a click.
- **Design principles:**
  - each quantity has one home view;
  - density contours appear only on metric spaces;
  - no status relies on colour alone.
- **Discarded designs:**
  - convex hulls on the projection, which readers took for spread;
  - baselines that changed with the visible configurations;
  - summary cards that pooled all prompts and hid the reversals of T2.

---

## 6 Cases

Each case starts from a failure of Sec. 4 and follows an analyst through DefaultScope on the real data. The findings were first established by the scripted analyses. The cases show how the system lets an analyst reach and check them, and what it adds that a number, a sentence or a few images do not. [Real-data screenshots: pending.]

### 6.1 Is it a shift, a narrowing, or the encoder? (F1c; T1, T5)
1. **Set:** klein-base 4B at guidance 1 is the reference, guidance 4 the focus, and the distilled klein 4B a third member.
2. **Scatters:** in E, the focus's diamonds lie below the spread band on four aspects, and the distilled member's lie further down on all five. Only saturation's diamond lies right of the shift band.
3. **Seeds:** in D, the seed lines lean right and converge from guidance 1 to 4. The segment to klein 4B is rank-matched and dashed, because its checkpoint differs.
4. **Encoder:** the analyst switches to SigLIP 2. The diamonds stay below the spread band, but on medium the focus now moves toward illustration (+1.08), and the map shows its arrow leaving the reference.
5. **Margins:** dragging the spread margin shows how robust the narrowing is. Medium, tone and saturation stay narrowed, with their whole interval beyond the margin, up to a margin of ×1.52–1.62; background and shot only up to ×1.26 and ×1.20.
6. **Record:** the analyst logs "narrows like guidance, more strongly; which aspects move is encoder-specific", with both states in the findings log.

**Without the system:** a diversity score says "less diverse" under both encoders, and a single-encoder analysis reports its own shifts as facts.

### 6.2 A pooled "no change" that hides reversals (F1b; T2, T3)
1. **Overview:** the contrast overview shows SDXL → SDXL-Turbo with short arrows and a large ⇄ count.
2. **Scatter:** the pooled saturation diamond sits inside the shift band, with subject dots on both sides.
3. **Subjects:** the badge (⇄ 7) steps through the subjects that turn muted beyond the margin against the slightly positive pooled shift: "a bird on a branch", "a car", "a kitchen", "a library", "a city street", "a mountain" and "a picnic". In the shift column, "a horse" and "a cup of coffee" are the longest bars on the vivid side.
4. **Images:** in C, Turbo's images of the horse sit on the vivid side, and those of the bird on the muted side.
5. **Attribution:** the ⚠ chip lists five differing settings, so the finding is not attributed to distillation.

**Without the system:** the pooled number says "no difference", and eight images of one subject would show only one direction.

### 6.3 Auditing a prompt rewriter (F1a, F2; T3, T4)
1. **Contrast:** the analyst compares FLUX.2 dev with its rewritten-prompt version.
2. **Background:** E shows the strongest effect, toward a busy background, but the card carries ⊘.
3. **Images:** in C, for "a picnic" (the subject with the largest shift), the rewritten images are scored far toward "busy", yet they show the same kind of grassy scene as the originals. This is the failure the round-3 check measured.
4. **Validated aspects:** the diamonds of saturation (×1.31) and medium (×1.49) stay inside the spread band. Medium's interval reaches beyond it, so widening is undecided, not shown.
5. **Rewrites:** in D, rewrites whose text leans toward "photograph" sit next to images that drifted toward illustration.

**Without the system:** the strongest number would have become the headline, and the rewriter's text would have suggested the opposite of what the images show.

### 6.4 Checking what a VLM says (F2, F3; T4)
1. **A contradicted statement.** In ❝ for SDXL → Turbo, a Mistral-24B statement about "a restaurant" reads: "Set B images include more detailed architectural elements such as arched windows and ornate moldings." It is coded to background, toward busy, and marked ✗. Qwen3.5-4B made nearly the same claim, which the coder placed outside the measured aspects. The trail shows the restaurant's backgrounds becoming much plainer (−1.68 [−2.95, −1.15]) and less varied (×0.12), while the pooled shift is +0.11, so the trail also marks that pooling hides the subject. The images confirm it.
2. **A confirmed statement.** For "a car": "Set B images have a more sepia tone and muted color palette." The trail shows tone toward vintage (+1.44) and saturation toward muted (−1.47).
3. **The verdict bar.** Of the 290 statements about this pair:
   - 94 fall outside or beside the measured aspects;
   - 74 cannot be decided by the audit;
   - 112 are confirmed, most of them statements about variety;
   - 6 claim a shift that the audit does not find, and 4 are contradicted.

   For klein guidance, 11 statements are marked ≈: a narrowing described as a change in look.
4. **Margins and encoder.** Dragging the shift margin or switching the encoder changes some verdicts live, which shows which statements are robust.

**Without the system:** the sentence reads as plausible. Eight images per side do not settle it either, because people miss most real shifts there (F3).

### 6.5 Defining and checking a new aspect (F1a; R4)
Scored in the running system on 2026-10-27 (`case65.mjs`); the in-tool human check is still to be done by the analyst.
- **A suspected default:** the analyst suspects that guidance and distillation push scenes toward daylight, and defines "a scene in daylight" ↔ "a scene at night". After the encoder's self-check, the aspect enters every view, marked ⊘.
  - **Numbers:** they fit the suspicion. Guidance narrows the aspect (×0.52) and leans toward daylight (−0.28); distillation does so more (×0.50, −0.46; 12 subjects toward daylight beyond the margin, one the other way).
  - **Images:** they give a first reason for caution. For "a city street", the images scored nearest "at night" are grey, hazy daylight streets rather than night scenes (Fig. 8).
  - [pending: the analyst's in-tool check on the klein chain.]
- **A failed proposal:** for contrast, the analyst enters the axis a VLM proposed and people rejected: "a simple image with little detail" ↔ "a highly detailed, intricate image" (agreement 0.34).
  - **Numbers:** it shows a shift toward "detailed" in every contrast, including the rewriter (+0.75, 16 subjects up, 3 down) and distillation (+0.72).
  - **What it means:** an analyst who trusted the words would report that rewriting and distillation add detail. On this axis CLIP mostly orders images the opposite way from people, and the ⊘ mark and the check stop that reading.
  - [pending: the in-tool check of the detail axis.]

---

## 7 Expert Study [pending]
**Question:** does the visual analysis help experts avoid the failures of Sec. 4, compared with the same numbers and images without it?

**Design.**
- **Participants:** five researchers who train, evaluate or select generative image models (5–10 years in imaging research), at least two from outside the authors' group; prior involvement is recorded. A pilot session precedes them.
- **Conditions:** each expert solves T1–T4 twice, once with DefaultScope and once with a **baseline**, on different cases of the same kind. Condition order and case assignment are counterbalanced.
  - The baseline has the same pooled and per-subject numbers with intervals, the settings, the validation table, sortable image grids and the VLM statements as text. It has no visual encoding of effects and no linking.
- **Tasks:** one per failure: T1 shift or narrowing (F1c), T2 pooled or per subject (F1b), T3 trust a reading (F1a), T4 verify a VLM statement (F2).
- **Measures:**
  - correctness by rules fixed in advance, scored by a second judge blind to condition;
  - the evidence cited;
  - confidence (1–5) and time;
  - an interview.
- **Reporting:** formative and descriptive (correct answers out of five per task and condition, and interview themes), with no statistical claims.
- **Caveat:** the tool displays the audit, so correctness with the tool partly means reading the audit correctly. The baseline shows the same numbers, so the comparison isolates visual encoding and linking.

**Results:** [pending].

---

## 8 Discussion

**Why visual analysis, and not a better score or a better VLM.** Our experiments show three ways of judging failing in complementary ways:
- **numbers** were wrong when the measure was wrong, pooled or encoder-specific;
- **language** asserted differences that were not there;
- **eyes** on a few images missed real differences.

Each failure is repaired by what another way provides:
- numbers by a look at the images;
- language by a measurement;
- eyes by a measurement over all seeds that tells them where to look.

A visual analytics system is where these meet. This is the sense in which the visualization is necessary here: it is not an illustration of results computed elsewhere, but the place where measurement, language and human judgement check one another.

**Language proposes, images decide.** This suggests a division of labour for LLM-assisted visual analytics:
- language models propose candidates, suspected differences and summaries;
- a visual analysis with validated measures, explicit margins and a path to the images decides.

DefaultScope builds this into the interface: statements are hypotheses with verdicts, and new axes must pass a check before they count.

**Generality.** The design needs four ingredients:
- configurations rendered on shared prompts and seeds;
- a measurement that can be defined in words;
- a human check for that measurement;
- per-unit effects with uncertainty.

These carry over to video or text-to-3D defaults, and to comparing LLM outputs along language-defined attributes.

**Limitations.**
- **Measurement:** CLIP and SigLIP aspects are approximations, and shift findings are encoder-specific.
- **Validity under SigLIP:** it is judged on pairs sampled by CLIP gaps, which favours CLIP.
- **Margins:** the 0.5 margin is not a perceptual unit.
- **Images:** native resolutions differ (512–1328 px).
- **Language data:** one rewriter instruction; two open VLMs with one prompt format; the human grid check has three annotators and 48 items.
- **Scale:** the comparison set holds six members.
- **Evaluation:** the expert study is small and formative.

## 9 Conclusion
Evaluators judge how text-to-image defaults change by numbers, by language, or by looking at a few images. On 12 open configurations, each of these failed on its own:
- numbers measured the wrong thing, hid reversals and depended on the encoder;
- VLMs reported differences that were not there;
- people with eight images missed real differences.

DefaultScope combines the three. It computes verdicts over all seeds under margins and encoders the analyst can change, leads every number and claim to its images, and lets the analyst define and check new aspects.

---

## Acknowledgments
[Annotators; experts; funding.] AI-use disclosure per IEEE policy: [tools, parts, use].

## References
*Verified: 1–18 (`docs/OUTLINE.md`, 2026-10-11); 19–25 on 2026-10-26 (arXiv, GitHub, Crossref). One [cite] place remains (Sec. 2, visual comparison).*

1. Vendi Score. arXiv:2210.02410.
2. Classifier-Free Diffusion Guidance. arXiv:2207.12598.
3. DIMCIM. arXiv:2506.05108.
4. GRADE. arXiv:2410.22592.
5. Attribute-conditional diversity benchmark. arXiv:2511.10547.
6. DefaultShift. arXiv:2608.21784.
7. An Exploration of Default Images in Text-to-Image Generation. arXiv:2505.09166.
8. Stage-wise dynamics of classifier-free guidance. arXiv:2509.22007.
9. Adversarial Diffusion Distillation. arXiv:2311.17042.
10. VisDiff. arXiv:2312.02974.
11. CompCon. arXiv:2509.08940.
12. ViBEx. arXiv:2504.19703.
13. Varif.ai. DOI 10.1145/3715336.3735847.
14. CUPID. DOI 10.1111/cgf.15086.
15. Gleicher, Considerations for Visualizing Comparison. DOI 10.1109/TVCG.2017.2744199.
16. Qwen-Image Technical Report. arXiv:2508.02324.
17. CLIP. arXiv:2103.00020.
18. SigLIP 2. arXiv:2502.14786.
19. Datta et al., Prompt Expansion for Adaptive Text-to-Image Generation. arXiv:2312.16720.
20. Peinl, Using LLMs as prompt modifier to avoid biases in AI image generators. arXiv:2504.11104.
21. Black Forest Labs, FLUX.2: Frontier Visual Intelligence, 2025. github.com/black-forest-labs/flux2.
22. Wan, Zheng, Chang, VDiff-Bench: A Challenging Benchmark for Fine-Grained Image Difference Identification. arXiv:2609.06245.
23. Feng et al., PromptMagician: Interactive Prompt Engineering for Text-to-Image Creation. IEEE TVCG 2024. DOI 10.1109/TVCG.2023.3327168.
24. Zhao et al., LEVA: Using Large Language Models to Enhance Visual Analytics. IEEE TVCG 2024. DOI 10.1109/TVCG.2024.3368060.
25. Ragan, Endert, Sanyal, Chen, Characterizing Provenance in Visualization and Data Analysis. IEEE TVCG 22(1), 2016. DOI 10.1109/TVCG.2015.2467551.

## Figures and tables (plan)
| # | Content | Section |
|---|---|---|
| Fig. 1 (teaser) | The interface on the klein chain (`fig4_interface.png`), or a teaser built from it [to decide at layout] | 1 |
| Fig. 2 | Framework: aspect in words → human check → shift and spread per subject → verdict, under two encoders [to draw] | 3 |
| Fig. 3 | Failure evidence (`fig3_failures.png/.pdf`, `make_data_figures.py`): (a) per-subject saturation shifts of SDXL → Turbo around the pooled +0.17, coloured beyond the margin (10 vivid, 7 muted; 9 and 6 with an interval excluding zero, the count in the text); (b) klein guidance, pooled shift and spread per aspect, CLIP filled vs SigLIP 2 hollow; (c) the 48 grid pairs, VLMs vs people | 4 |
| Fig. 4 | Interface with panels A–E and the encoder switch (`fig4_interface.png`, full width) | 5 |
| Fig. 5 | Case 6.1: the same view under CLIP and SigLIP 2, maps and the medium and tone scatters (`fig5_case61.png`, full width) | 6 |
| Fig. 6 | (a) Case 6.2: scatter with subjects on both sides, lanes of a horse and a bird; (b) case 6.3: background ⊘ and medium scatters, the picnic lane (`fig6_cases_62_63.png`, full width) | 6 |
| Fig. 7 | Case 6.4: the audit trail of the restaurant statement (`fig7_case64.png`, one column) | 6 |
| Table 1 | Human validation per round and encoder | 4.1 |
| Table 2 | VLM answers, null control and the human grid check | 4.3 |
| Table 3 | From failure to requirement, design, case and expert task | 4.4 |
