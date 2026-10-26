# Grounding Language in Images: Interactive Visual Analysis of Appearance Defaults in Text-to-Image Models

*PacificVis 2027 Conference Paper Track, draft 2 (2026-10-26).*
- *Structure:* measurement framework, then experiments, then the visual analytics system and the cases it supports.
- *Sources:* `docs/manuscript/paper_v2_en.md` (source text, numbers checked against `results/`); plan `docs/PACIFICVIS_PLAN.md`.
- *Limit:* 9 pages + 2 pages for acknowledgments and references, VGTC conference template. Target about 5,800 words of text with six figures and two tables.
- *Markers:* [pending] = result not yet available; [read on real data] = a detail to confirm in the running system; [cite] = a verified reference still to be found (no reference is invented).
- *Name:* "DefaultScope" is a working name.

---

## Abstract

When a prompt leaves composition, colour or medium unsaid, a text-to-image model decides, and modern models decide almost the same way every time. Language now shapes these appearance defaults in three roles:
- it defines the axes along which images are measured;
- large language models (LLMs) rewrite prompts before generation;
- vision-language models (VLMs) describe how two models differ.

Each role produces claims about images that can be wrong.

We contribute a measurement framework, an experimental study and a visual analytics system.
- **Framework.** Aspects are defined in words and kept only after people confirm them. Each change is split into a shift and a change in spread, per subject, under explicit margins.
- **Experiments.** On 9,216 images from 12 open configurations, with two LLM rewriters and two VLM describers:
  - guidance and distillation narrow appearance under two encoders;
  - pooled "no change" verdicts hide opposite shifts in 38 of 60 cases;
  - a rewriter's strongest effect lies on an axis people reject;
  - VLMs report differences between two sets from the same model in 98–100% of answers, people reading the same grids in a third.
- **System.** DefaultScope lets evaluators reach and check such findings themselves. It links a comparison set of up to six configurations to subjects and single images, computes verdicts live under adjustable margins, and traces language claims to the images that decide them.

Four cases and [pending: expert sessions] show how analysts use it.

**Keywords:** visual analytics, model comparison, text-to-image generation, LLM-assisted analysis, provenance.

---

## 1 Introduction

A prompt such as "a kitchen" names a subject and nothing else. The model decides the rest: whether the image is a photograph or a painting, a close-up or a wide view, muted or vivid, plain or cluttered. Modern models make nearly the same decision every time. In a pilot with 16 images per minimal prompt, the Vendi score [1] fell from 7.45 for Stable Diffusion 1.5 to 2.79 for FLUX.2 klein. Within one model, it fell from 5.95 to 2.32 when classifier-free guidance [2] rose from 1 to 4. We call these unrequested, recurring decisions **appearance defaults**.

The people who build, distil and select image models change these defaults with routine decisions: raising guidance, distilling to four steps, swapping a checkpoint. More and more, defaults are also shaped through **language**:
- production pipelines let an LLM rewrite the prompt before generation (FLUX.2 ships such a rewriter [21]);
- developers ask VLMs to describe how two models differ [10, 11];
- the attributes used to measure images are themselves defined in words, as text prompts of an image–text encoder [17].

Each role produces claims about images, and each can fail:
- an axis defined in words can run backwards;
- a rewriter can appear to add variety while moving the output elsewhere;
- a description can call a narrowing a shift.

Current practice summarizes default changes with diversity scores [1, 3, 4, 5] or written descriptions [10, 11]. Both hand the evaluator a conclusion and leave three questions open:
1. **Moved or narrowed?** "Less diverse" can mean a different look or a tighter grip on the same look.
2. **Pooled or per subject?** Averages over prompts can hide opposite changes on different subjects.
3. **True of the images?** A number from an encoder and a sentence from a VLM both need a path back to the pictures, or errors look exactly like findings.

We answer these questions in two steps.
1. A measurement framework and a set of controlled experiments establish what changes, and how far language-derived claims can be trusted.
2. An evaluator cannot know in advance which configurations, aspects, subjects and images matter. We therefore built a visual analytics system in which evaluators reach, check and record such conclusions themselves.

**Contributions:**
1. **A measurement framework** for appearance defaults (Sec. 4):
   - human-checked, language-defined aspects;
   - per-subject shift and spread under explicit margins;
   - validity conditions for comparing configurations.
2. **An experimental study** (Sec. 5) of 12 open configurations, two LLM rewriters and two VLM describers, partly pre-registered. It shows that:
   - guidance and distillation mainly narrow appearance;
   - pooled verdicts hide reversals;
   - language-derived claims fail in specific, checkable ways.
3. **DefaultScope** (Sec. 6), a visual analytics system with:
   - a set-based comparison model;
   - linked views from configurations to images;
   - verdicts computed live under adjustable margins;
   - language claims traced to image evidence;
   - user-defined, user-checked aspects;
   - a findings log that replays the analysis state.
4. **Four cases and an expert evaluation** (Secs. 7–8, [pending]) of how analysts use the system.

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

[cite: comparison of many items; uncertainty visualization of effects with intervals and margins.]

**LLMs and VLMs in visual analytics.** Language models are used across analysis workflows, for example to recommend insights and summarize findings [24].
- **Describing differences:** VisDiff [10] and CompCon [11] describe differences between image sets in natural language.
- **Benchmarks:** they score whether such descriptions name a reference difference [10], or whether a model identifies a change between two images, with "no difference" as one option [22].

None calibrates a description against a human-validated measurement, or gives the analyst a visual route from a sentence to the images. We treat generated language as a claim to verify, in line with work on provenance in visual analysis [25].

**Measuring defaults and diversity.**
- **Diversity scores:** Vendi [1], DIMCIM [3], GRADE [4] and attribute-conditioned benchmarks [5] quantify diversity.
- **Default images:** studies of default images [7] characterize the outputs of empty or minimal prompts.
- **Distillation:** DefaultShift [6] compares distilled models with their teachers on a closed attribute list and observes that distillation acts like raised guidance.
- **Prompt rewriting:** rewriters add variety in aggregate [19, 20].

These works report how much outputs converge. They do not separate a move of the typical output from a narrowing around it, per subject, and they offer no path from the number to the images.

---

## 3 Tasks and Requirements

**Users:** researchers and engineers who train, distil, evaluate or select text-to-image models and the language components around them.

The tasks come from three sources:
- the decisions these users take when a setting changes;
- the gaps of the measures above;
- measurement failures we met in this project, each of which looked like a finding until the images were inspected (Sec. 5.1).

**Tasks:**
- **T1 Shift or concentration:** does a change move the typical output, narrow it, or both?
- **T2 Pooled or per subject:** does a pooled conclusion hold for every subject, and which subjects go against it?
- **T3 Trace to images:** does a reading survive a look at the images, and can the contrast be attributed to one setting?
- **T4 Verify a language claim:** is an axis name, a rewritten prompt or a VLM description supported by the images?
- **T5 Compare many configurations:** along a chain (guidance 1 → 4 → distilled) or a family, which members move or narrow appearance, and for which subjects?

**Requirements:**
- **R1 Explore, do not report:** every verdict is computed from the data in view, under margins the analyst can move. (T1, T2)
- **R2 Many configurations, one reference:** configurations are compared as a set against an explicit reference. Identity is carried by position and label, not by hue. (T5)
- **R3 Every reading reaches the images:** from any number, a path leads to its subjects and images, with an honest image correspondence (same seed, or rank-matched). (T3)
- **R4 Language is a hypothesis:** axis names, rewrites and statements are linked to the evidence that decides them, and new axes are checked by people before use. (T4)
- **R5 Findings are reproducible:** a conclusion is stored with the full analysis state and can be replayed. (all tasks)

---

## 4 Measurement Framework

**Data.**
- **Prompts:** 24 minimal prompts in six categories (people, animals, objects, interiors, outdoor scenes, activities), each naming only a subject.
- **Configurations:** 12 open configurations at their model-card settings:
  - SD 1.5, SDXL, SDXL-Turbo, SD 3.5 Large;
  - FLUX.2 dev;
  - FLUX.2 klein-base 4B at guidance 4 and 1, klein 4B, klein-base 9B, klein 9B;
  - Qwen-Image-2512 [16] at guidance 4 and 1.
- **Images:** every configuration renders every prompt from the same 32 seeds, giving 9,216 images. Every setting is read from the weights and declared.

**Language-defined aspects with a human check.** An image's score on an aspect is its CLIP ViT-L/14 [17] similarity to a right-pole phrase minus its similarity to a left-pole phrase, for example "muted desaturated colors" vs. "vivid saturated colors". Such an axis is cheap and open, and it can be wrong, so people check it before use.
- **The check:** annotators see a same-prompt image pair with a large score gap and pick the image closer to the right pole, or "can't tell".
- **The rule,** fixed before labelling: an aspect is kept for a set of configurations if at least 75% of the decidable judgements agree with CLIP and at most 40% are "can't tell".

**Shift and spread.** For a contrast A → B, per subject and aspect:
- **shift:** Δ = (median_B − median_A)/s. Here s is a per-aspect scale, frozen once from the 12 configurations, so one unit is the typical spread of one configuration on one subject;
- **spread ratio:** IQR_B / IQR_A.

**Margins and inference.**
- **Margins,** frozen before any comparison was examined:
  - a shift of at least 0.5 units is a displacement;
  - a ratio beyond 1.5 or below 1/1.5 is a change in spread;
  - "same place" and "same spread" require the 90% interval to lie inside the margin.
- **Bootstrap:** a hierarchical bootstrap resamples subjects within categories and images within cells, with seeds paired when A and B share a checkpoint. The experiments use 10,000 replicates.
- **Pre-registration:** primary tests are Holm-corrected. Before each analysis, we committed the aspects, margins, scale and code; for the LLM study also the rewriters, VLM prompts and scoring rules.

**Validity conditions.**
1. Every setting is declared.
2. A contrast that changes several settings is a package and is not attributed to one of them.
3. A pooled result is never read without its per-subject structure.
4. Baselines do not move when configurations are shown or hidden.
5. Measurement validity is stated per configuration set.
6. A claim stated in language is a hypothesis to check against the images.

---

## 5 Experiments

### 5.1 E1: Which language-defined aspects can be trusted?
Three rounds of human checks decided which aspects enter the analysis (Table 1). Three annotators labelled independently.

**Round 1** (240 pairs, first six configurations): 7 of 15 candidate aspects passed. Five were frozen: saturation, medium (photo vs. painting), shot (close-up vs. wide), tone (modern vs. vintage) and background (plain vs. busy). Several failed:
- **style** ran backwards: CLIP called polished photographs "stylized", and people agreed with its direction on only 17% of pairs;
- **quality, depth of field, composition, lighting and viewpoint** were unreliable.

**Round 2** (later six configurations, which are far more alike): shot, saturation and medium pass; tone (0.64) and background (0.70) fail. Validity found on varied configurations did not transfer to homogeneous ones.

**Round 3** (images from rewritten prompts):
- saturation and tone pass; medium passes, though not stably;
- shot (0.63) and background (0.38) fail. On these long, detailed scenes, CLIP's "busy background" is more often the opposite of people's reading than the same.

**Table 1.** Agreement with CLIP on large-gap pairs (✗ = fails the frozen rule).

| Aspect | Round 1 (first six) | Round 2 (later six) | Round 3 (rewrites) |
|---|---|---|---|
| saturation | 0.92 | 0.77 | 0.90 |
| medium | 0.90 | 0.77 | 0.77 |
| shot | 0.90 | 0.96 | 0.63 ✗ |
| tone | 0.94 | 0.64 ✗ | 0.89 |
| background | 0.81 | 0.70 ✗ | 0.38 ✗ |

Every later finding is read only on aspects validated for both sides of its contrast.

### 5.2 E2: Guidance and distillation narrow appearance
**Guidance.** In klein-base 4B, raising guidance from 1 to 4 concentrates four aspects beyond the margin: saturation ×0.51 [0.43, 0.61], medium ×0.53, tone ×0.49 and background ×0.65.
- **Shift:** only saturation is also displaced, toward vivid colour (+0.65 [+0.43, +0.93]).
- **Per subject:** 15 of 24 subjects move toward vivid by at least the margin, and none moves that far toward muted.
- **Qwen-Image-2512:** the same direction with smaller effects (saturation ×0.64, +0.39).

**Distillation.** Replacing klein-base 4B with the distilled klein 4B (new checkpoint, 50 → 4 steps):
- concentrates all five aspects (×0.41–0.63);
- displaces saturation (+0.95 [+0.67, +1.19]).

This is the guidance pattern, more strongly. It supports DefaultShift's observation [6] against a measured guidance intervention in the same family.

**Second encoder.** We rescored with SigLIP 2 [18] under the same poles, margins and inference. It agrees with people on the checked pairs about as often as CLIP does.
- **The narrowing is robust:** guidance again concentrates medium, tone and background (×0.52–0.62), and distillation all five aspects (×0.48–0.58). Distillation's saturation shift also holds (+1.03).
- **Which aspects guidance moves is not robust:** with SigLIP, saturation stays below the margin (+0.44), while medium (+1.08), shot (−0.86) and tone (−1.59) are displaced.
- **Per-subject readings agree only moderately** between the encoders (median Spearman 0.33–0.67).

**Answer.** Guidance and distillation remove alternatives on every aspect we can validate, under two encoders. Which aspects they also move depends on the encoder, so shift findings are reported as encoder-specific.

### 5.3 E3: Pooled verdicts hide opposite shifts
- **Across all configuration pairs,** on validated aspects, 38 of the 60 pooled comparisons that fall within the margin hide opposite shifts: at least three subjects shift beyond +0.5 and three beyond −0.5.
- **SDXL → SDXL-Turbo** (a package of five settings) is the clearest case. Every pooled shift is "same place" or unresolved, yet four of five aspects hide opposite shifts.
  - On saturation, 9 subjects become more vivid and 6 more muted, each with its own interval excluding zero.
  - "A horse" moves +2.33, while "a bird on a branch" moves −2.07.

A pooled number alone would report no difference.

### 5.4 E4: What does LLM prompt rewriting change? (pre-registered)
**Setup.**
- **Rewriters:** FLUX.2's official rewriter (Mistral-Small-3.2-24B with Black Forest Labs' instruction, temperature 0.15 [21]) and Qwen3.5-4B with the same instruction.
- **Rewrites:** each prompt is rewritten once per seed.
- **Generation:** images come from klein 4B and FLUX.2 dev with the original seeds.
- **Tests:** 20, Holm-corrected.

**Results.**
- **No validated widening.** On aspects validated for both sides, no spread widens beyond the margin (×1.13–1.49).
- **Medium drifts toward illustration** in both generators (+0.53 and +0.37). The unadjusted intervals exclude zero, but neither drift is significant after correction.
- **The largest effect is a measurement failure.** The strongest result of the whole family is FLUX.2 dev's background moving toward "busy" (+0.67 [+0.47, +0.91], 17 subjects up, none down). It lies on the axis that people contradict on rewritten images (0.38). Without the human check, it would have been the headline finding.
- **The rewriter matters.** With Qwen3.5-4B, saturation moves toward muted (−0.62).
- **Variety comes from sampling text.** Reusing one rewrite for all seeds concentrates every aspect (×0.71–0.79); varying the rewrite per seed widens it again (×1.25–1.80 against the fixed rewrite).
- **Text and image agree only in part.** The rewritten text moves toward "a photograph", while the images move toward illustration. Per subject, on validated aspects, the text predicts the image only for saturation (Spearman 0.42–0.53).

### 5.5 E5: Can VLMs describe these differences? (pre-registered)
**Setup.**
- **Describers:** Qwen3.5-4B and Mistral-Small-3.2-24B.
- **Input:** 8 vs. 8 images per subject for six contrasts, shown as two grids.
- **Questions:**
  - a free-text description;
  - constrained questions per aspect: "closer to ⟨right⟩ / ⟨left⟩ / no clear difference" and "more / less / about equally varied".
- **Truth:** the audit on all 32 seeds, on validated aspects.

**Exploratory checks,** added after the first scoring:
- **Null control:** one configuration on both sides, seeds shifted by 16.
- **Stability:** a second, disjoint draw of grids.
- **People:** three annotators answered the same questions on 48 of the same grid pairs.

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

**Reading.**
- **Both VLMs almost always report a difference,** even between two sets from one model.
- **The eight images are not the reason:**
  - the answers are stable across draws;
  - where the eight shown seeds decide, they agree with the 32-seed truth in 98–100% of cases;
  - people reading the same grids mostly see no difference in the null pairs.
- **Eight images are hard for people too.** People miss most real shifts, and agree with each other only moderately (Fleiss' κ 0.41 for shift, 0.54 for variety).
- **Neither a VLM's description nor a quick look settles whether configurations differ.**
  - That decision needs the full set of seeds and validated measures.
  - It also needs the per-subject structure: both VLMs describe narrowing as movement, and repeat pooled claims that are false for many subjects.

### 5.6 E6: Can a VLM propose new aspects?
- **Proposals:** asked for opposite-pole pairs that separate the sets, Mistral-24B mostly restated aspects we already measure.
- **Candidates:** six new properties qualified by the pre-registered rule: sharpness, level of detail, natural vs. idealized, contrast, lighting character and texture.
- **Check:** none passes round 3 (0.34–0.70). For level of detail (0.34), CLIP mostly orders the images the opposite way from people.
- **Reading:** people understood the properties ("can't tell" in only 11–25% of judgements), but CLIP does not order images along them as people do. A VLM can propose what to measure; it cannot extend the measurement by itself.

---

## 6 DefaultScope

The experiments answer fixed questions on fixed contrasts. An evaluator facing a new model, a new setting or a new claim needs to ask such questions directly. DefaultScope is a single-screen web system (D3) with five linked panels (Fig. 4). It runs from disk; user-defined aspects need a local web server.

### 6.1 The comparison set (R2)
The header holds a **comparison set** of up to six configurations in chain order, with two roles:
- **Reference (blue):** every contrast is measured from it, and reference-relative views place 0 at its median.
- **Focus (orange):** the member detailed by the per-subject views.

**Further members** are drawn in ink. Each is identified by its slot (a matrix column, an image lane, a parallel axis, a distribution row, a small multiple) and by a direct label. Hue therefore never has to distinguish six members. With blue and orange fixed, a colour-vision check admitted only one further hue, and an earlier version with one hue per member failed it.

**Settings:** a member's chip lists the declared settings that differ from the reference. A ⚠ chip warns when more than one setting differs, so the contrast is not attributed to one setting (T3).

### 6.2 Panel A: where configurations settle
- **◎ Configuration map (T1, T5).**
  - **Encoding:** each configuration sits at its typical location (x) and typical spread (y) on the chosen aspect. Families are shapes.
  - **Arrows** join designed contrasts: solid for guidance only, dashed for a package, dotted for prompt rewriting.
  - **Density contours** of the 24 per-subject positions show, for each member, whether it behaves consistently across subjects.
  - **Zoom:** semantic zoom keeps the density estimate fixed in scale units, and marks outside the view become edge triangles.
- **▦ Contrast overview (T1 across contrasts).** One row per contrast and one glyph per aspect:
  - an arrow for the pooled shift, dashed while the interval reaches into the margin;
  - a disc against a unit ring for the spread ratio;
  - ⇄n for subjects against the pooled direction.
- **❝ VLM statements (T4).**
  - **Glyphs:** each statement about the reference → focus pair is a glyph in a subject × aspect grid. Shape encodes the VLM; colour and a symbol encode the audit's verdict: ✓ confirmed, ≈ narrowed but did not move, ○ no shift, ✗ contradicted.
  - **Live verdicts (R1):** verdicts are recomputed from the current data and margins with the rule of E5. A tooltip shows the frozen verdict when the two differ.
  - **Analyst's verdict:** analysts add their own ✓ or ✗.
- **⛓ Audit trail (T3, T4).** One claim (a statement, a rewrite or an axis defined in words) is followed through four stages, with a verdict on each link:
  1. the claim;
  2. the measurement that decides it;
  3. one subject;
  4. its images (same seed, or rank-matched and labelled so).

### 6.3 Panels B–E: from subjects to images
- **B, subjects × configurations (T2).**
  - **Matrix:** each cell is coloured by where a configuration puts a subject between the aspect's poles. Set members' columns come first.
  - **Shift columns:** one per member, on a common scale, show each subject's shift from the reference. Subjects that move against that member's pooled direction beyond the margin are outlined.
  - **Reversal badge:** it counts the focus's reversals and steps through them.
- **C, images on the axis (T3).** Every image of the selected subject is placed by its score, one lane per member, with the margin band and each member's median.
- **D, evidence for one subject (T1, T3, T5).**
  - **Paired seeds:** parallel coordinates with one axis per member. Members that share the starting noise are joined seed by seed; otherwise images are matched by rank and the segment is dashed. Leaning lines show a shift; converging lines show a narrowing.
  - **Distributions:** the subject on every validated aspect, to expose coupled changes.
  - **Appearance map:** all images of the subject on a shared t-SNE of CLIP image embeddings, one small multiple per member. It is an index to defaults that the five aspects do not name. It carries no contours and is not read as spread.
  - **Rewrites:** for a rewriting contrast, each rewrite is placed at what its text says about the aspect, against where its image lands.
- **E, contrast scatters (T1, T2).**
  - **Encoding:** one scatter per aspect. Each subject is a dot at (shift, log spread ratio) with its interval, and the margins are bands. The pooled estimate is a diamond with its interval, and every further member is a labelled diamond.
  - **Margin handles:** dragging them changes the margins for exploration. Every verdict in the system updates (R1), and a chip restores the frozen margins.
  - **Brushing:** brushing subjects highlights them everywhere and adds, for every member, the brushed subjects' median.
  - **Validity:** an aspect not validated for a member fades that member's marks and is marked ⊘.

### 6.4 User-defined aspects (R4) [implementation in progress]
1. **Define:** an analyst types two pole phrases. The system embeds them in the browser with the same CLIP text encoder (bundled, run locally) and scores every image from stored image embeddings.
2. **Use:** the new aspect enters every view at once, marked "not validated".
3. **Check:** the analyst judges about 12 large-gap pairs from the current set, side by side. The frozen rule of Sec. 4 decides whether the aspect passes for these configurations.
4. **Keep the record:** the result is stored with the aspect and shown wherever it is used.

This turns the lesson of E1 and E6 into an interaction: words do not measure images until people confirm they do.

### 6.5 Linking, provenance and design rationale
- **Linking:** choosing a member, aspect or subject in any view updates every other view. Hovering a subject or an image highlights it everywhere.
- **Findings log (☆, R5):** a finding recorded from any view stores the whole analysis state: set and roles, aspect, subject, panel modes, margins, brushed subjects, statement and map zoom. A click replays it.
- **Design principles:**
  - each quantity has one home view (effects in E, images in C, distributions in D); overviews restate a number only as a pointer to its home;
  - density contours appear only on metric spaces;
  - no status relies on colour alone.
- **Discarded designs:**
  - convex hulls on the projection, which readers took for spread;
  - baselines that changed with the visible configurations, so that one concentration read as 0.78, 0.35 or 1.00;
  - summary cards that pooled all prompts and hid exactly the reversals of T2.

---

## 7 Cases

Each case follows an analyst through DefaultScope on the real data. The findings were first established by the scripted analyses of Sec. 5. The cases show how the system reaches and checks them, and what the interaction adds: which subjects, which images, and whether a claim survives. [Real-data screenshots: pending.]

### 7.1 Following a chain: guidance, then distillation (T1, T5)
1. **Set:** the analyst sets klein-base 4B at guidance 1 as reference and guidance 4 as focus, and adds the distilled klein 4B.
2. **Map:** on saturation, both members sit to the right of the reference and lower: they move toward vivid and narrow.
3. **Scatters:** in E, the focus's diamonds lie below the spread band on four aspects. The distilled member's diamonds lie further down, on all five (E2).
4. **Seeds:** in D, the seed lines lean right and converge from guidance 1 to 4. Klein 4B uses a different checkpoint, so its segment is rank-matched and drawn dashed, and the analyst does not read it as single images moving.
5. **Margins:** dragging the spread margin shows how far the verdicts depend on the frozen choice. [read on real data: the margin at which a verdict changes]
6. **Record:** the analyst logs "narrows like guidance, more strongly; shift findings encoder-specific (E2)".

**What the system adds:** which members narrow on which aspects, read from one screen, and a visible break in seed correspondence where the checkpoint changes.

### 7.2 A pooled "no change" that hides reversals (T2, T3)
1. **Overview:** the contrast overview shows SDXL → SDXL-Turbo with short arrows and a large ⇄ count.
2. **Scatter:** with the pair as reference and focus, the pooled saturation diamond sits inside the shift band, with subject dots on both sides.
3. **Subjects:** the reversal badge steps through the subjects. "A horse" and "a cup of coffee" turn vivid; "a bird on a branch" and "a car" turn muted (E3).
4. **Images:** lane C for "a horse" shows Turbo's images on the vivid side; for "a bird on a branch", they sit on the muted side.
5. **Attribution:** the ⚠ chip lists five differing settings, so the analyst records the finding without attributing it to distillation.

**What the system adds:** the names of the subjects that disagree, and the images that show it. A pooled number and a subject count give neither.

### 7.3 Auditing a prompt rewriter (T3, T4)
1. **Contrast:** the analyst compares FLUX.2 dev with its rewritten-prompt version.
2. **Background:** E shows the strongest effect, toward a busy background, but the card carries ⊘ (not validated on rewrites).
3. **Images:** opening C, the analyst finds rewritten images scored "busy" that a person would call plain. This is the failure the round-3 check measured (E1).
4. **Validated aspects:** no diamond lies above the spread band, and medium leans toward illustration with an interval that reaches into the margin.
5. **Rewrites:** in D, rewrites whose text leans toward "photograph" sit next to images that drifted toward illustration.

**What the system adds:** the validity mark stops the analyst before the most prominent effect, and the images explain why.

### 7.4 Checking what a VLM says (T4)
1. **A contradicted statement.** In ❝ for SDXL → Turbo, one Mistral-24B statement about "a restaurant" reads: "Set B images include more detailed architectural elements such as arched windows and ornate moldings." [read on real data: its coded aspect and glyph.] Following it into the trail, the analyst sees that the restaurant's backgrounds become much plainer (−1.68) and far less varied (×0.12), and the images confirm it.
2. **A confirmed statement.** For "a car", the statement reads: "Set B images have a more sepia tone and muted color palette." The trail shows tone moving toward vintage (+1.44) and saturation toward muted (−1.47).
3. **The verdict bar.** For the pair as a whole, the bar summarizes the verdicts. [read on real data: the share of ≈ "narrowed, did not move"; E5 predicts many.]
4. **Margins.** Dragging the shift margin changes some verdicts live. This shows the analyst which statements depend on the margin and which do not.

**What the system adds:** a statement becomes a hypothesis with a verdict and a path to its images, instead of a summary to accept or reject wholesale.

### 7.5 Defining and checking a new aspect (T4, R4) [pending: run on real data once Sec. 6.4 is complete]
- **A suspected default:** the analyst suspects that the distilled model defaults to daylight and types "a scene at night" ↔ "a scene in daylight". [Result: map, scatter, matrix; the in-tool check.]
- **A failed proposal:** for contrast, the analyst enters a VLM-proposed pair that failed round 3 ("rich detail" ↔ "minimal detail", 0.34). [Result of the in-tool check.]

---

## 8 Expert Evaluation [pending]
[Design to be fixed: either 45-minute formative sessions with open exploration tasks, or tool-versus-baseline sessions on T1–T4 (`docs/EXPERT_SESSION.md`).]
- **Participants:** [3–5] researchers who train, evaluate or select text-to-image models, at least [n] from outside the authors' group. Prior involvement is recorded.
- **Data:** findings in the log (with replayable state), view paths, time to the first supported finding, interview themes.
- **Reporting:** formative and descriptive.
- **Results:** [pending].

---

## 9 Discussion

**Separate position from spread before saying "less diverse".** Across guidance, distillation and rewriting, the narrowing survived a second encoder, while the set of moved aspects did not. One diversity number hides both facts. A system that shows both, per subject, lets an evaluator say which one happened.

**Read no pooled verdict without its subjects.** Most pooled "no change" verdicts on validated aspects hid opposite shifts, and both VLMs described them as pooled shifts. Showing the subjects next to the pooled estimate is therefore not a detail of the interface but a condition for a correct reading.

**Language proposes, images decide.** In all three roles, language carried information and was unreliable:
- axis names ran backwards or did not transfer between configuration sets;
- rewritten text described appearances the generator did not render;
- VLM descriptions reported differences between two sets from one model;
- VLM-proposed axes were understood by people but could not be measured with CLIP.

This suggests a division of labour for LLM-assisted visual analytics:
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
- **Measurement:** CLIP aspects are approximations, and shift findings are encoder-specific.
- **Margins:** the scale comes from these configurations, so the 0.5 margin is not a perceptual unit.
- **Images:** native resolutions differ (512–1328 px), which may affect cross-family comparisons.
- **Language data:** one rewriter instruction; two open VLMs with one prompt format; the human grid check has three annotators and 48 items.
- **Scale:** the comparison set holds six members; all twelve configurations appear together only on the map and the matrix.
- **Evaluation:** the expert evaluation is small and formative.

## 10 Conclusion
Language now measures, changes and explains the appearance defaults of text-to-image models, and each role produces claims that can be wrong. Our experiments on 12 open configurations show three things:
- guidance and distillation mainly narrow appearance;
- pooled "no change" hides reversals;
- rewriters and VLMs make claims that the images do not support.

DefaultScope lets evaluators reach such conclusions themselves. With it, they can:
- compare sets of configurations;
- separate shift from concentration per subject;
- move the margins and watch verdicts change;
- follow every claim to the images that decide it.

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
| Fig. 1 (teaser) | DefaultScope with a three-member chain (guidance 1 → 4 → distilled) and the trail of a contradicted VLM statement down to its images | 1 |
| Fig. 2 | Framework: language-defined aspect → human check → shift and spread per subject → verdict | 4 |
| Fig. 3 | Experiment results: per-subject shift × spread for guidance and distillation (both encoders); validation agreement by round | 5 |
| Fig. 4 | Interface with panels A–E and tasks T1–T5 marked (real data) | 6 |
| Fig. 5 | Cases 7.2 and 7.3: reversals (matrix + lanes) and the ⊘ background axis with its images | 7 |
| Fig. 6 | Case 7.4: a VLM statement traced to its images, or case 7.5 when ready | 7 |
| Table 1 | Human validation per round | 5.1 |
| Table 2 | VLM answers, null control and the human grid check | 5.5 |
