# Grounding Language in Images: Interactive Visual Analysis of Appearance Defaults in Text-to-Image Models

*PacificVis 2027 Conference Paper Track, first draft (2026-10-26). Source text: `docs/manuscript/paper_v2_en.md`; plan: `docs/PACIFICVIS_PLAN.md`. Limit: 9 pages + 2 pages for acknowledgments and references, VGTC conference template.*

*Markers:*
- *[pending]: result not yet available (expert sessions, the user-defined-aspect scenario, real-data screenshots).*
- *[verify]: a reference whose identifier must be checked before submission.*
- *[cite]: a place where a verified reference still has to be found; no reference is invented.*
- *The system name "DefaultScope" is a working name.*

---

## Abstract

When a prompt leaves composition, colour or medium unsaid, a text-to-image model decides, and modern models decide almost the same way every time. Language now shapes these appearance defaults in three roles:
- it defines the axes along which images are measured;
- large language models (LLMs) rewrite prompts before generation;
- vision-language models (VLMs) describe how two models differ.

Each role produces claims about images that can be wrong. Diversity scores and generated descriptions hand evaluators conclusions without a path back to the images.

We present DefaultScope, a visual analytics system in which evaluators reach and check such conclusions themselves. The system has four parts:
- a comparison set of up to six configurations, with a reference and a focus;
- linked views from configurations to subjects to single images;
- verdicts on shift and concentration, computed live under adjustable margins;
- language claims traced to image evidence.

Analysts can also define their own appearance axes in words and check them against their own judgement before using them. Five usage scenarios on 9,216 images from 12 open configurations show how an analyst finds four things with the system:
- guidance and distillation narrow appearance more reliably than they move it;
- pooled "no change" verdicts hide opposite shifts across subjects;
- a rewriter's strongest effect lies on an axis people reject;
- VLMs report differences between two image sets from the same model.

[Expert study: pending.]

**Keywords:** visual analytics, model comparison, text-to-image generation, provenance, LLM-assisted analysis.

---

## 1 Introduction

A prompt such as "a kitchen" names a subject and nothing else. Whether the image is a photograph or a painting, a close-up or a wide view, muted or vivid, plain or cluttered is decided by the model. Modern models make nearly the same decision every time. In a pilot with 16 images per minimal prompt, the Vendi score [1] fell:
- from 7.45 for Stable Diffusion 1.5 to 3.47 for SDXL-Turbo and 2.79 for FLUX.2 klein;
- within one model, from 5.95 to 2.32 when classifier-free guidance [2] rose from 1 to 4.

We call these unrequested, recurring decisions **appearance defaults**.

The people who build, distil and select image models change these defaults with every routine decision: raising guidance, distilling to four steps, swapping a checkpoint. More and more, the defaults are also shaped through **language**:
- production pipelines let an LLM rewrite the user's prompt before generation (FLUX.2 ships such a rewriter);
- developers ask VLMs to describe how two models differ [10, 11];
- the attributes used to measure images are themselves defined in words, as text prompts of an image–text encoder [17].

Each role produces claims about images, and each can fail in its own way:
- an axis defined in words can run backwards;
- a rewriter can appear to add variety while moving the output elsewhere;
- a description can call a narrowing a shift, or report a pooled change that does not hold for most subjects.

Current practice summarizes default changes with diversity scores [1, 3, 4, 5] or a written description [10, 11]. Both hand the evaluator a conclusion and leave three questions open:
1. **Moved or narrowed?** "Less diverse" can mean a different look or a tighter grip on the same look; the two call for different responses.
2. **Pooled or per subject?** Averages over prompts can hide opposite changes on different subjects.
3. **True of the images?** A number from an encoder and a sentence from a VLM both need a path back to the pictures, or errors look exactly like findings.

These questions are exploratory. Which configurations to compare, which aspect matters, which subjects disagree and which images to inspect are not known in advance. So the answer should not be another score or another report but a system in which the evaluator can ask, check and record.

We present **DefaultScope** (Fig. 1). Its design rests on three ideas:
- **compare sets, not pairs:** a comparison set of up to six configurations, with a reference and a focus, in which every view identifies members by position and label;
- **separate shift from concentration everywhere:** per subject, with margins the analyst can move and verdicts that update live;
- **treat every language-derived claim as a hypothesis:** an axis name, a rewritten prompt or a VLM statement is linked to the measurement, the subject and the images that decide it. Analysts can define new axes in words, but an axis enters the analysis only after they have checked it against their own judgement in the tool.

**Contributions:**
1. A task analysis of comparing appearance defaults across text-to-image configurations, with five analysis tasks and the design requirements that follow from measurement pitfalls we met (Sec. 3).
2. DefaultScope, a visual analytics system with:
   - a set-based comparison model;
   - linked views from configurations to images;
   - live verdicts under adjustable margins;
   - user-defined, user-checked language axes;
   - audit trails and a findings log that replay the analysis state (Sec. 5).
3. Five usage scenarios on 9,216 images from 12 open configurations, two LLM rewriters and two VLM describers. They show how analysts reach and check findings, including results that contradict the language-derived claims (Sec. 6).
4. An evaluation with domain experts [pending] (Sec. 7).

---

## 2 Related Work

**Visual analytics for generative image models.**
- ViBEx [12] and Varif.ai [13] support exploring how outputs vary for one model or prompt.
- CUPID [14] visualizes distributions of generated images.
- [cite: VA for prompt engineering and for model comparison of generative models.]

These systems help users understand one model's output space. Our setting is the comparison of several declared configurations, together with the verification of claims made about them in language.

**Visual comparison.** Gleicher's framework [15] distinguishes juxtaposition, superposition and explicit encoding. DefaultScope uses each in one place:
- it encodes differences explicitly (per-subject shift and spread ratio);
- it superposes configurations on one map;
- it juxtaposes images and set members in aligned lanes and small multiples.

[cite: comparison of many items and small multiples; uncertainty visualization of effects with intervals and margins.]

**LLMs and VLMs in visual analytics.** Language models are increasingly used to generate hypotheses, descriptions and summaries in analysis workflows [cite]. VisDiff [10] and CompCon [11] describe differences between image sets in natural language; benchmarks score whether such descriptions name a reference difference [10, 22 verify]. None of these calibrates a description against a human-validated measurement, or gives the analyst a visual route from a sentence to the images that confirm or contradict it. DefaultScope treats generated language as a claim to verify, in line with work on provenance and analytic verification [cite].

**Measuring defaults and diversity.**
- **Diversity scores:** Vendi [1], DIMCIM [3], GRADE [4] and attribute-conditioned benchmarks [5] quantify diversity; studies of default images [7] characterize outputs of empty or minimal prompts.
- **Distillation:** DefaultShift [6] compares distilled models with their teachers on a closed attribute list and observes that distillation acts like raised guidance.
- **Prompt rewriting:** rewriters add variety in aggregate [19, 20 verify].

These works report how much outputs converge. They do not separate a move of the typical output from a narrowing around it, per subject, and they offer no path from the number to the images.

---

## 3 Task Analysis

**Users:** researchers and engineers who train, distil, evaluate or select text-to-image models and the language components around them (rewriters, describers).

The tasks below come from three sources:
- the decisions these users take when a setting changes;
- gaps in the measures above;
- failures we met while measuring defaults in this project, each of which looked like a finding until the images were inspected (Sec. 6.3).

**Tasks:**
- **T1 Shift or concentration:** does a change of model or setting move the typical output, narrow it, or both?
- **T2 Pooled or per subject:** does a pooled conclusion hold for every subject, and which subjects go against it?
- **T3 Trace to images:** does a reading survive a look at the images, and can the contrast be attributed to one setting?
- **T4 Verify a language claim:** is a statement made in language (an axis name, a rewritten prompt, a VLM description) supported by the images?
- **T5 Compare many configurations:** across a chain or family of configurations (guidance 1 → 4 → distilled; 4B vs. 9B), which members move or narrow appearance, for which subjects, and how does one seed travel through all of them?

**Design requirements:**
- **R1 Explore, do not report:** every verdict is computed from the data the analyst is looking at, under margins the analyst can move. Precomputed conclusions are not shown as such. (T1, T2)
- **R2 Many configurations, one reference:** configurations are compared as a set against an explicit reference, with identity carried by position and label rather than by hue. (T5)
- **R3 Every reading reaches the images:** from any number a path leads to the subjects and then to the images that produce it, with an honest correspondence between images (same seed or rank-matched). (T3)
- **R4 Language is a hypothesis:** axis names, rewrites and VLM statements are linked to the evidence that decides them, and new language-defined axes are checked by people before use. (T4)
- **R5 Findings are reproducible:** what the analyst concludes is stored with the full analysis state and can be replayed. (all tasks)

---

## 4 Data and Measurement Backend

**Data.**
- **Prompts:** 24 minimal prompts in six categories (people, animals, objects, interiors, outdoor scenes, activities), each naming only a subject.
- **Configurations:** 12 open configurations at their model-card settings:
  - SD 1.5, SDXL, SDXL-Turbo, SD 3.5 Large;
  - FLUX.2 dev;
  - klein-base 4B at guidance 4 and 1, klein 4B, klein-base 9B, klein 9B;
  - Qwen-Image-2512 [16] at guidance 4 and 1.
- **Images and settings:** each configuration renders each prompt with the same 32 seeds, giving 9,216 images. Every setting is read from the weights and declared.
- **Language data** (Sec. 6):
  - prompts rewritten once per seed by FLUX.2's official rewriter (Mistral-Small-3.2-24B) and by Qwen3.5-4B with the same instruction;
  - descriptions of differences from Qwen3.5-4B and Mistral-Small-3.2-24B.

**Language-defined aspects.** An image's score on an aspect is its CLIP ViT-L/14 [17] similarity to a right-pole phrase minus that to a left-pole phrase ("muted desaturated colors" vs. "vivid saturated colors").

Such an axis is cheap and open, and it can be wrong. Annotators therefore check it before use:
- **The check:** they see a large-gap image pair from one prompt and pick the image closer to the right pole, or "can't tell".
- **Acceptance rule:** an axis is kept for a set of configurations if at least 75% of decidable judgements agree with CLIP and at most 40% are "can't tell". The rule was fixed before labelling.

Three rounds of checks kept five aspects:
- saturation, medium (photo vs. painting), shot (close-up vs. wide), tone (modern vs. vintage) and background (plain vs. busy);
- validity is recorded per set of configurations (Table 1).

The other axes failed:
- "style" ran backwards (17% agreement);
- quality, depth of field, composition, lighting and viewpoint were unreliable;
- six axes proposed by a VLM all failed (Sec. 6.4).

**Table 1.** Agreement with CLIP on large-gap pairs (✗ = fails the frozen rule).

| Aspect | Round 1 (first six configs) | Round 2 (later six) | Round 3 (rewritten images) |
|---|---|---|---|
| saturation | 0.92 | 0.77 | 0.90 |
| medium | 0.90 | 0.77 | 0.77 |
| shot | 0.90 | 0.96 | 0.63 ✗ |
| tone | 0.94 | 0.64 ✗ | 0.89 |
| background | 0.81 | 0.70 ✗ | 0.38 ✗ |

**Shift and concentration.** For a contrast A → B, per subject and aspect:
- **Shift:** Δ = (median_B − median_A)/s, where s is a per-aspect scale frozen once from the 12 configurations (one unit ≈ the typical spread of one configuration on one subject).
- **Spread ratio:** IQR_B / IQR_A, shown on a log scale.
- **Margins:** a shift of at least 0.5 units moves; a ratio beyond 1.5 or below 1/1.5 widens or narrows. "Same" requires the 90% interval to lie inside the margins.
- **Uncertainty:** in the tool, a hierarchical bootstrap (subjects resampled within categories, images within cells, seeds paired when the checkpoint is shared), recomputed whenever the set or the margins change.

The confirmatory analyses behind the findings (10,000 resamples, Holm-corrected, partly pre-registered) are in the supplement. The tool shows their intervals only in figure mode.

---

## 5 DefaultScope

DefaultScope is a single-screen web system (D3) with five linked panels (Fig. 2). It runs offline from disk; one optional feature (user-defined aspects) needs a local web server.

### 5.1 The comparison set (R2)
The header holds the **comparison set**: up to six configurations in chain order, with two roles.
- **Reference (blue):** every contrast is measured from it, and every reference-relative view places 0 at its median.
- **Focus (orange):** the member that the per-subject views detail.
- **Further members:** drawn in ink and identified by their slot (a matrix column, a shift column, an image lane, a parallel axis, a distribution row, a small multiple, a row of the contrast overview) and by a direct label.

Hue therefore never has to distinguish six members. With blue and orange fixed, a colour-vision validator admitted only one further hue in both light and dark themes, and an early version with one hue per member failed it. A click on any member makes it the focus, and a click on its dot makes it the reference. A chip's tooltip lists the declared settings it changes against the reference; a ⚠ chip warns when more than one setting differs, so the contrast cannot be attributed to one of them (T3).

### 5.2 Panel A: where configurations settle
Panel A has four modes, each answering a question no other view answers.

**◎ Configuration map (T1, T5).**
- **Encoding:** each configuration is placed at its typical location (x, scale units from each subject's cross-configuration centre) and typical spread (y, median IQR) on the chosen aspect.
- **Marks:** families are shapes (circle Stable Diffusion, square FLUX.2, triangle Qwen-Image). Arrows join designed contrasts (solid: guidance only; dashed: a package of changes; dotted: prompt rewriting), and the reference is joined to every set member.
- **Density contours:** contours of the 24 per-subject positions show for reference and focus whether a configuration is consistent across subjects.
- **Zoom:** semantic zoom keeps the density estimate fixed in scale units, so zooming magnifies the contours without re-estimating them. Marks outside the view become edge triangles.

**▦ Contrast overview (T1 across contrasts).** One row per contrast, one glyph per aspect:
- an arrow for the pooled shift, dashed while the interval reaches into the margin;
- a disc against a dashed unit ring for the spread ratio;
- ⇄n for subjects that go against the pooled direction.

The set's contrasts form their own group above the designed contrasts, with a persistent key. At a glance, distillation repeats the guidance pattern, and SDXL → Turbo has short arrows over many reversed subjects.

**❝ VLM statements (T4).**
- **Layout:** every statement a VLM made about the reference → focus pair sits in a subject × aspect grid. Shape encodes the VLM; colour and a symbol encode the audit's verdict (✓ confirmed, ≈ narrowed but did not move, ○ no shift, ✗ contradicted).
- **Live verdicts (R1):** each verdict is recomputed from the current data and margins with the rule of the confirmatory scoring, and a tooltip shows the frozen verdict when the two differ.
- **Analyst's verdict:** analysts add their own ✓ or ✗.

**⛓ Audit trail (T3, T4).** One claim is followed through four stages, with a verdict on each link:
- **the claim:** a VLM statement, a rewritten prompt, or an axis defined in words;
- **its measurement:** the numbers that decide it, pointing to the scatter in E;
- **one subject:** pointing to the images in C;
- **the images:** same seed, or rank-matched and labelled so; the last link is the analyst's own verdict.

A trail restates numbers and points to panels E and C instead of redrawing them.

### 5.3 Panel B: subjects × configurations (T2)
- **Matrix:** each row is a subject, each cell is coloured by where a configuration puts that subject (teal ↔ ochre between the aspect's poles). Set members' columns come first, in set order; the other configurations follow, narrower.
- **Shift columns:** one per member, on one common scale, show the per-subject shift from the reference. Subjects that move against that contrast's pooled direction beyond the margin are outlined in red, and shifts beyond the scale end in an edge triangle.
- **Navigation:** a badge counts the focus's reversals and steps through them; rows can be ordered by shift.

### 5.4 Panel C: images on the axis (T3)
Every image of the selected subject is placed by its score on a shared axis, one lane per member. The margin band and each member's median are marked. Hovering or brushing images highlights the same seeds in C and D.

### 5.5 Panel D: evidence for one subject
- **⫽ Paired seeds (T1, T5):** parallel coordinates with one axis per member. Neighbours that share starting noise (same pipeline and resolution) are joined seed by seed. Otherwise images are matched by rank and the segment is dashed, as a quantile alignment rather than a trajectory. Leaning lines show a shift; converging lines show concentration.
- **∿ Distributions:** the subject on every validated aspect, which exposes coupled changes. Two members are drawn as densities; more members as one interval row each (10–90% range, IQR, median).
- **⁘ Appearance map:** all images of the subject from every configuration on a shared t-SNE of CLIP image embeddings, one small multiple per member. It is an index to images that can reveal a default the five aspects do not name. Because t-SNE keeps only neighbourhoods, it carries no contours and is not read as spread.
- **✎ Rewrites (T4):** shown only when a rewritten-prompt configuration is compared with its own base. Each rewrite is placed at what its text says about the aspect (text-side score) against where its image lands (image-side shift). Word families (lighting, time of day, colour, style) can be highlighted.

### 5.6 Panel E: contrast scatters (T1, T2)
- **Encoding:** one scatter per aspect. Each subject of reference → focus is a dot at (shift, log spread ratio) with its interval, the margins are bands, and the pooled estimate is a diamond with its 90% interval. Every further member is a labelled diamond with its own interval.
- **Margin handles:** dragging them changes the margins for exploration; every verdict in the system updates (R1), and a chip restores the frozen margins.
- **Brushing:** brushing subjects highlights them everywhere and adds, for every member, a hollow diamond at the brushed subjects' median, so the analyst can ask whether a group of subjects disagrees.
- **Validity:** an aspect not validated for a member fades that member's marks and is marked ⊘.

### 5.7 User-defined aspects with an in-tool check (R4) [implementation in progress]
1. **Define:** an analyst types two pole phrases ("daylight" ↔ "a scene at night"). The system embeds them in the browser with the same CLIP text encoder (an ONNX export, bundled and run locally) and scores every image from stored image embeddings.
2. **Use:** the aspect enters every view at once, with a scale computed as for the frozen aspects, but marked "not validated".
3. **Check:** the analyst opens a check that shows about 12 large-gap image pairs from the current set, side by side, and picks the image closer to the right pole or "can't tell". The frozen acceptance rule decides whether the aspect passes for these configurations.
4. **Keep the record:** the result is stored with the aspect and shown wherever it is used.

This turns the project's central lesson (words do not measure images until people confirm they do) into an interaction.

### 5.8 Linking and provenance (R3, R5)
- **Linking:** choosing a member, an aspect or a subject in any view updates every other view. Hovering a subject highlights it in the scatters, the matrix and the map; hovering an image highlights its seed in C and D.
- **Findings log (☆):** analysts record a finding from any view. Each record (a note or a saved audit trail) stores the whole analysis state: set and roles, aspect, subject, panel modes, margins, brushed subjects and seeds, the statement, the map zoom. A click replays it, and the log exports as CSV.

### 5.9 Design rationale
Four principles guided the design; they are design hypotheses for the evaluation, not results.
- **Each quantity has one home view:** effects in E, images in C, raw distributions in D. Overviews and trails restate a number only as a pointer to its home.
- **No control changes only appearance:** every control changes what is analysed. Figure mode is a URL parameter, not a control.
- **Density contours only on metric spaces:** the map has them, the t-SNE map does not.
- **Status never relies on colour alone:** every status mark carries a symbol or a shape.

We discarded three earlier designs:
- convex hulls on the projection, which readers took for spread;
- baselines that changed with which configurations were shown, so that one concentration read as 0.78, 0.35 or 1.00;
- summary cards that pooled all prompts and hid exactly the reversals T2 must reveal.

An external review of the interface found that an earlier version (rev12) was a pairwise workflow with set displays attached. That review led to the reference-centred origin, per-member validity, one correspondence policy and set-aware brushing described above.

---

## 6 Usage Scenarios

The scenarios follow an evaluator through DefaultScope on the real data. Each finding below was first established by the scripted analyses in the supplement (partly pre-registered). The scenarios show how the system lets an analyst reach and check it, and where the interaction adds what the scripts did not. [Screenshots from the real-data build: pending.]

### 6.1 Guidance narrows appearance; what it moves depends on the encoder (T1, T5)
1. **Set up:** the analyst puts klein-base 4B at guidance 1 as reference, guidance 4 as focus, and the distilled klein 4B as a third member.
2. **Map:** on saturation, the focus's contours shrink and move right.
3. **Contrast scatters:** across E, the focus's diamonds sit below the spread band on four aspects. Saturation narrows to ×0.51 [0.43, 0.61], medium ×0.53, tone ×0.49, background ×0.65. Only saturation also shifts, +0.65 [+0.43, +0.93].
4. **Subjects:** the matrix's focus shift column shows 15 of 24 subjects moving toward vivid by at least a margin and none toward muted.
5. **Seeds:** in D the paired-seed lines lean right and converge, so single images move and gather.
6. **Distillation:** the third member's diamonds land further down: all five aspects narrow (×0.41–0.63), and saturation shifts more (+0.95). Distillation repeats the guidance pattern, more strongly, as DefaultShift [6] observed.
7. **Margins:** dragging the margin handles shows how far the verdicts depend on the margins. [The spread margin at which the narrowing verdicts change: read on real data.]

Re-scoring with a second encoder (SigLIP 2 [18]) keeps the narrowing but not the shifts: medium, shot and tone shift under SigLIP and saturation does not. The system marks shift findings as encoder-specific.

### 6.2 A pooled "no change" that hides reversals (T2, T3)
1. **Overview:** the contrast overview shows SDXL → SDXL-Turbo with short arrows and a large ⇄ count on saturation.
2. **Scatter:** making the pair reference and focus, the analyst sees the pooled diamond inside the shift band ("same place" or undecided) and the subject dots on both sides of it.
3. **Reversals:** the badge steps through the reversals. 9 subjects become more vivid and 6 more muted, each with an interval excluding zero.
4. **Images:** lane C for [a subject that turned vivid; from real data] shows Turbo's images on the vivid side; for [a subject that turned muted] they sit on the muted side.
5. **Attribution:** the ⚠ chip says five declared settings differ, so the analyst records the finding without attributing it.

Across all configuration pairs, 38 of 60 pooled "no change" comparisons on validated aspects hide such opposite shifts. A pooled number alone would have reported no difference.

### 6.3 An axis that fails on rewritten images (T3, T4)
1. **Contrast:** the analyst compares FLUX.2 dev with its own rewritten-prompt version (official rewriter).
2. **Background:** E shows the strongest effect of the whole rewriting study, toward a busy background (+0.67, 17 subjects in that direction, none against), but the card is marked ⊘ (not validated).
3. **Images:** opening C, the analyst sees rewritten images rated "busy" that people would call plain. The round-3 check had found that annotators agreed with CLIP on background for only 38% of rewritten pairs.
4. **What holds:** turning to validated aspects, the analyst finds no validated widening (ratios ×1.13–1.49, none beyond the margin) and a consistent drift toward illustration (+0.37 to +0.53).
5. **Rewrites:** in the ✎ view, rewrites that say "photograph" sit next to images that drifted toward illustration; only for saturation does text predict image (Spearman 0.42–0.53).

Without the per-aspect validity and the route to the images, the measurement error would have been the paper's most prominent finding.

### 6.4 Checking what a VLM says (T4)
1. **Statements:** in ❝ for klein-base 4B guidance 1 → 4, [a confirmed Mistral-24B statement, quoted from the real data] carries ✓ on saturation.
2. **Contradiction:** [a contradicted pooled statement for SDXL → Turbo, quoted from the real data] carries ✗; following it into the trail, the analyst sees that the subjects disagree and the images show the reversal.
3. **Narrowing called a shift:** where the audit finds narrowing without a shift, both VLMs answered "shift" in 12–13 of 13 cases.
4. **Same model on both sides:** when the analyst sets the same configuration on both sides (different seeds), the statements still claim differences. The VLMs reported a shift in 98–100% of such answers, whereas the system shows every diamond inside the bands.
5. **Hidden reversals:** for 49–50 of 50 pooled "no change" cases that hide reversals, the VLMs described a pooled shift.

The VLM text points to where to look; the views decide what is true.

### 6.5 Defining and checking a new aspect (T4, R4) [pending: run on real data once Sec. 5.7 is complete]
1. **Define:** the analyst suspects that the distilled model defaults to daylight and types "a scene at night" ↔ "a scene in daylight".
2. **Inspect:** the new aspect appears in every view, marked not validated. [Result: map, scatter, matrix.]
3. **Check:** the analyst runs the in-tool check on 12 large-gap pairs. [Agreement, can't tell, pass or fail.]
4. **Contrast:** a second phrase pair proposed by a VLM in the study ("rich detail" ↔ "minimal detail", which failed the round-3 check at 0.34) fails the in-tool check as well, and the tool keeps it marked.

---

## 7 Expert Evaluation [pending]

- **Participants:** [3–5] researchers who train, evaluate or select text-to-image models, at least [n] from outside the authors' group; prior involvement is recorded.
- **Procedure (about 45 minutes per session):**
  1. a 10-minute tutorial on a training case (klein 4B original → FLUX.2 rewrite, saturation);
  2. three open exploration tasks with think-aloud: (a) characterize what distillation does to klein's appearance (T1, T5); (b) decide whether SDXL-Turbo is "more vivid" than SDXL (T2, T3); (c) decide whether to trust a VLM's description of a pair (T4);
  3. a semi-structured interview: trust, usefulness of the set, live verdicts, user-defined aspects, and missing functions.
- **Data collected:** findings recorded in the findings log (with replayable state), the paths of views used, the time to the first supported finding, and interview quotes.
- **Reporting:** formative and descriptive, with no comparative accuracy claims.
- **Results:** [pending].

---

## 8 Discussion

**Separate position from spread before saying "less diverse".** Across guidance, distillation and fixed rewriting, the narrowing survived a second encoder, while the set of moved aspects did not. A system that shows one diversity number would have hidden both facts.

**Do not read a pooled shift without its per-subject structure.** Most pooled "no change" verdicts on validated aspects hid opposite shifts. Both VLMs described them as pooled shifts.

**Language proposes, images decide.** In all three roles, language attached to images carried information and was unreliable:
- axis names ran backwards or did not transfer between configuration sets;
- rewritten text described appearances the generator did not render;
- VLM descriptions reported differences between two sets from one model;
- VLM-proposed axes were understood by people but could not be measured with CLIP.

This suggests a division of labour for LLM-assisted visual analytics: language models propose candidates, suspected differences and readable summaries, and a visual analysis with validated measures, explicit margins and a path to the images decides. DefaultScope builds this into the interface: statements are hypotheses with verdicts, and new axes must pass a check before they count.

**Generality.** The design relies on four ingredients:
- configurations rendered on shared prompts and seeds;
- a measurement that can be defined in words;
- a human check for that measurement;
- per-unit effects with uncertainty.

These carry over to other generative settings, such as video or text-to-3D defaults, or the comparison of LLM outputs along language-defined attributes.

**Limitations.**
- **Measurement:** CLIP aspects are approximations, and shift findings are encoder-specific.
- **Margins:** the scale comes from these configurations, so the 0.5 margin is not a perceptual unit.
- **Resolution:** native resolutions differ (512–1328 px), which may affect cross-family comparisons.
- **Language data:** the rewriters use one instruction; the VLMs are two open models with one prompt format.
- **Scale:** the set is limited to six members by the layout. Twelve configurations are shown together only on the map and the matrix.
- **Evaluation:** the expert evaluation is small and formative.

## 9 Conclusion
Language now measures, changes and explains the appearance defaults of text-to-image models, and each role produces claims that can be wrong. DefaultScope lets evaluators compare sets of configurations, separate shift from concentration per subject, move the margins and watch verdicts change, and follow every claim (from an axis name, a rewriter or a VLM) to the images that decide it. On 12 open configurations it leads an analyst to four findings:
- guidance and distillation mainly narrow appearance;
- pooled "no change" hides reversals;
- a rewriter's strongest effect is a measurement error;
- VLMs report differences that are not there.

---

## Acknowledgments
[Annotators; experts; funding.] AI-use disclosure per IEEE policy: [tools, parts, use].

## References
*Verified: 1–18 (`docs/OUTLINE.md`, 2026-10-11). [verify]: 19–22. [cite] places need further verified VA references (VA for generative models and prompt engineering, LLMs in VA, provenance, uncertainty).*

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
19. Prompt Expansion. arXiv:2312.16720. [verify]
20. LLMs as prompt modifier. arXiv:2504.11104. [verify]
21. FLUX.2 reference implementation (prompt upsampling). [verify citation form]
22. VDiff-Bench. arXiv:2609.06245. [verify]

## Figures (plan; 9 pages leave room for about six)
| # | Content | Section |
|---|---|---|
| 1 (teaser) | DefaultScope with a five-member set, the trail of a contradicted VLM statement and the images | 1 |
| 2 | Interface with panels A–E and tasks T1–T5 marked (real data) | 5 |
| 3 | The comparison set across views: matrix shift columns, lanes, parallel axes, small multiples for one chain | 5.1 |
| 4 | Scenario 6.1: contrast scatters and paired seeds for guidance and distillation | 6.1 |
| 5 | Scenario 6.2/6.3: hidden reversals (matrix + lanes) and the background axis failing on rewrites (⊘ + images) | 6.2–6.3 |
| 6 | Scenario 6.5: defining and checking a user aspect | 6.5 |
