# Grounding Language in Images: Visual Auditing of Appearance Defaults and Their LLM-Driven Shifts in Text-to-Image Models

*Manuscript draft v2, updated 2026-10-22, for the Computers & Graphics special issue "Bridging Language and Vision: Recent Advancements in LLM and Visual Analytics". Supersedes v1 (`paper_en.md`, CG&A format).*

*Status markers:*
- *Q4, Q5, Q6 and human check round 3 are final (2026-10-19).*
- *[pending] marks results not yet available: the expert study, the second-encoder check, the free-text coder check, the closed models.*
- *External review of this draft: `docs/REVIEW_2026-10-22.md`.*
- *Elsevier format items (abstract ≤ 200 words, 3–5 highlights of ≤ 85 characters, graphical abstract) must be checked against the C&G guide for authors before submission.*
- *Sources of all numbers are in `results/`.*

---

## Highlights
- Separates where image defaults move from how much they narrow, per subject
- Guidance and distillation narrow appearance far more than they move it
- LLM rewriting adds no validated variety; its largest effect fails human checks
- Two tested VLMs report differences even between sets from one model
- A linked visual audit grounds each language-derived claim in image evidence

## Abstract

When a prompt leaves framing, palette or medium unspecified, a text-to-image model decides them, almost always alike. Language now shapes these appearance defaults in three ways:
- **it defines the axes** on which images are measured;
- **it intervenes**, when large language models (LLMs) rewrite prompts before generation;
- **it explains**, when vision-language models (VLMs) describe how two models differ.

Each role produces claims about images that can be wrong. We present a visual audit method that grounds such claims in image evidence. It places declared model configurations on language-defined, human-validated appearance axes, separates displacement from concentration under pre-registered margins, exposes per-subject structure and links every reading to the images.

Auditing 12 open configurations on 24 everyday subjects, we find that in FLUX.2 klein, guidance and distillation mainly concentrate appearance and displace only saturation, and that 38 of 60 pooled "no difference" comparisons on validated aspects hide opposite per-subject shifts. FLUX.2's official prompt rewriter adds no variety beyond our margins, and its largest apparent effect lies on an axis that people reject for rewritten images. Two VLMs report a difference even between image sets from one model, so their difference claims say little. [Five experts …]

---

## 1. Introduction

A prompt such as "a kitchen" names a subject and nothing else. It does not say whether the image should be a photograph or a painting, a close-up or a wide view, muted or vivid, plain or cluttered. The model decides, and modern models decide in nearly the same way every time. In a pilot, we generated 16 images of one minimal prompt and measured their diversity with the Vendi score [1]:
- diversity fell from 7.45 for Stable Diffusion 1.5 to 3.47 for SDXL-Turbo and 2.79 for FLUX.2 klein;
- within a single model, raising classifier-free guidance [2] from 1 to 4 lowered it from 5.95 to 2.32.

We call these unrequested, repeated decisions **appearance defaults**.

Defaults move whenever the people who build and evaluate models make an ordinary engineering decision: raising guidance, distilling a model to four steps, switching checkpoints. Increasingly, they also move through **language**.
- **Rewriting.** Production systems pass the user's prompt through an LLM that rewrites it into a long, detailed description before generation. FLUX.2 ships such an upsampler; Qwen-Image demonstrations use one.
- **Description.** When developers want to know how two models differ, they increasingly ask a VLM to describe the difference [10, 11].
- **Measurement.** The attributes along which images are measured are themselves often defined in words, as text prompts for an image–text encoder [17].

Language thus measures defaults, changes them and explains them. In each role it produces claims about images, and in each role those claims can be wrong in characteristic ways:
- an axis defined in words can be reversed;
- a rewriter can move outputs while appearing to diversify them;
- a description can call a narrowing a shift, or report a pooled change that is false for many subjects.

Current practice summarizes changes in defaults with a diversity score [1, 3, 4, 5], and an audit of distilled replacement models has shown that distillation shifts attribute distributions [6]. A score, or a sentence, leaves three questions open for an evaluator.
1. **Displacement or concentration?** "Less diverse" can mean that outputs moved to a different look, or that they collapsed onto the look they already had. These are different findings with different remedies.
2. **Pooled or per subject?** A change averaged over prompts can hide opposite changes on different subjects. In our audit, 38 of the 60 pooled "no difference" comparisons on validated aspects conceal subjects that move strongly in opposite directions.
3. **Is the claim right?** Whether a number from an encoder or a sentence from a VLM, a claim about images needs a route back to the images. Without one, an error looks exactly like a finding.

We present a **visual audit method** for appearance defaults that answers these questions, and we use it to audit 12 open configurations of five model families together with two LLM rewriters and two VLM describers. The method serves four audit tasks:
- **T1:** tell displacement from concentration;
- **T2:** check whether a pooled conclusion holds per subject;
- **T3:** trace a reading to the images to catch invalid measurements or attributions;
- **T4:** verify a claim stated in language.

The study answers six questions:
- **Q1 (confirmatory):** does raising guidance displace appearance, concentrate it, or both?
- **Q2 (descriptive):** where do configurations settle at their recommended settings, and do differences hold across subjects?
- **Q3 (pre-specified):** what does a distillation package change, compared with guidance?
- **Q4 (pre-registered):** what does LLM prompt rewriting change?
- **Q5 (pre-registered):** can VLMs describe these differences correctly?
- **Q6 (pre-registered):** can a VLM propose new appearance axes that people confirm?

**Contributions.**
1. **An audit method for appearance defaults:**
   - language-defined appearance axes validated by people separately for each configuration set;
   - a fixed per-aspect scale;
   - a separation of displacement from concentration with pre-registered practical margins and hierarchical uncertainty;
   - explicit validity conditions for comparing configurations.
2. **A visual audit system** in which a main view of all configurations is linked to per-subject, per-contrast and per-image views, and to views for rewritten prompts and VLM statements.
3. **An audit of 12 open configurations** with bounded findings on guidance, distillation and cross-model structure.
4. **A pre-registered study of language in the loop:**
   - LLM prompt rewriting as an intervention on defaults;
   - VLM descriptions scored against the audit;
   - VLM-proposed axes passed through human validation.
5. **An expert evaluation** with five experts against a strong baseline, and lessons for LLM-assisted visual analytics: LLMs can propose, but a visual audit must verify.

We do not propose a new diversity metric. We make no causal claim beyond the interventions we control, and we evaluate the VLMs only on the questions the audit can answer.

---

## 2. Related Work

**Measuring defaults and diversity.**
- The Vendi score [1] measures the effective number of distinct samples in a set.
- DIMCIM [3] and GRADE [4] measure concept- and attribute-level diversity of text-to-image models and report narrow distributions for unspecified attributes. An attribute-conditional benchmark [5] measures diversity per attribute.
- A study of default images [7] characterizes what models produce for empty or minimal prompts.
- The closest work, DefaultShift [6], audits distilled replacement models against their teachers with closed attribute vocabularies and observes that distillation behaves like increased teacher guidance.

These works quantify how much outputs converge or which attributes change. None separates a shift of the typical output from a narrowing around it across many configurations, and none offers a visual route from a number back to the images. Our Q3 tests DefaultShift's observation against a measured guidance intervention in the same family.

**Guidance and distillation.** Classifier-free guidance [2] trades diversity for prompt adherence, and an analysis of its stage-wise dynamics [8] shows that strong guidance suppresses weaker modes, which predicts concentration. Distillation methods such as adversarial diffusion distillation [9] produce few-step models deployed as drop-in replacements.

**LLM prompt rewriting.**
- Prompt Expansion [19] trains a model that turns a short query into several detailed prompts and reports more aesthetic and more diverse images.
- LLM prompt modifiers [20] raise image diversity and reduce demographic bias for SDXL, SD 3.5 and FLUX.
- FLUX.2 ships an official upsampler that rewrites prompts with its own text encoder, a VLM [21].

These works measure diversity as a single quantity. Q4 asks what a rewriter does to the location and the spread of defaults separately, per subject, and whether the rewritten text predicts the change in the images.

**Describing differences with language.** VisDiff [10] and CompCon [11] describe in natural language how two image sets differ. Benchmarks score such descriptions by whether they match a reference difference [10, 22]. A description is not a calibrated statement: it does not say whether a difference is a shift or a narrowing, how large it is, or whether it holds per subject. Q5 scores VLM descriptions on exactly these points, against an audit with human-validated measurements.

**Visual analytics of generated images.** ViBEx [12] and Varif.ai [13] support the exploration of output variation for one model or prompt, and CUPID [14] visualizes distributions of generated images. Our setting is the comparison of many declared configurations, with the additional requirement that language-derived claims be verified.

**Visual comparison.** Gleicher's framework [15] distinguishes juxtaposition, superposition and explicit encoding. We encode differences explicitly (shift and spread ratio per subject), superpose configurations in the overview, and juxtapose only images.

---

## 3. The Audit Method

### 3.1 Tasks
The four audit tasks come from the decisions an evaluator faces when a setting changes, from the gaps of the work above, and from failures we met in this project.
- **T1, displacement or concentration.** Diversity metrics merge the two [1, 3, 4].
- **T2, pooled or per subject.** In our pilot, SDXL-Turbo shifted composition by +1.31 for "a house" and −1.33 for "a kitchen", while the pooled shift was +0.07.
- **T3, tracing a reading to the images.** An axis defined in words turned out to be reversed. A request for a close-up of a kitchen produced a face that the encoder scored as a perfect close-up. A contrast that changes several settings invites a wrong attribution.
- **T4, verifying a claim stated in language.** A rewriter's text or a VLM's description asserts how images look or differ. The claim must be checked against the same evidence as any other reading.

### 3.2 Study material
- **Prompts.** 24 minimal, uncontroversial prompts in six categories (people, animals, objects, indoor scenes, outdoor scenes, activities), each naming only its subject.
- **Configurations.** 12 open configurations at their model-card settings:
  - Stable Diffusion 1.5, SDXL, SDXL-Turbo and Stable Diffusion 3.5 Large;
  - FLUX.2 dev;
  - FLUX.2 klein-base 4B at guidance 4 and 1, klein 4B, klein-base 9B and klein 9B;
  - Qwen-Image-2512 [16] at guidance 4 and 1.
- **Images.** Every configuration generates 32 images per prompt from the same 32 seeds, giving 9,216 images. The batch size is fixed per configuration, because bf16 outputs depend slightly on it.
- **Declared settings.** Pipeline, scheduler, text encoder and every sampling setting are read from the weights and declared. As a consequence, klein 4B and 9B use different text encoders, so model scale is not treated as a cause.
- **LLM study images.** For the LLM study (Section 6), each prompt is additionally rewritten 32 times per rewriter, once per seed, and images are generated from the rewrites with the same seeds.

### 3.3 Language-defined axes and their human validation
An image's score on an aspect is its CLIP ViT-L/14 [17] similarity to a right-hand text pole minus its similarity to a left-hand pole, for example "muted desaturated colors" versus "vivid saturated colors". The axis is defined entirely in language, which makes it cheap and open-ended, and also fallible. We therefore keep an aspect only if people confirm that the encoder orders images correctly on it.

**Procedure.**
- For each candidate aspect we sample same-prompt image pairs with large, medium or small CLIP gaps.
- Annotators see the two images and the two poles, and choose the image closer to the right pole, or "can't tell".
- The decision rule is fixed before labelling. An aspect is kept if, on the large-gap pairs, people agree with CLIP's direction on at least 75% of the pairs they could judge, and answer "can't tell" on at most 40%.
- Annotators work independently and see neither CLIP's answers nor each other's labels.

**Round 1** used 240 pairs from the configurations generated first (SD 1.5, SDXL, SDXL-Turbo, klein-base 4B at both guidance values, klein 4B) and three annotators. Seven of 15 candidate aspects passed (Table 1). Five were frozen for the analysis:
- saturation;
- medium (photograph vs. painting);
- shot (extreme close-up vs. wide view);
- tone (modern vs. vintage; read as a warm, yellowed photographic look, which also carries warm light);
- background (plain vs. busy).

Mood passed, but it is coupled with tone. Indoor/outdoor passed, but not stably. Several aspects failed:
- **style** was systematically reversed: CLIP called klein's polished photographs "stylized", and people agreed with its direction on only 17% of pairs;
- **quality, depth of field, composition, clutter, lighting and viewpoint** were unreliable;
- **time of day** could not be judged.

A fourth annotator never used "can't tell", against the guide. We excluded these labels after labelling and before the aspects were frozen; the exclusion was not a rule fixed in advance. With all four annotators, the five retained aspects keep their verdicts, but lighting and viewpoint would pass instead of fail. Both analyses are in the supplementary material.

**Round 2** checked the six later configurations with 120 pairs, the same rule and the same annotators. Two annotators had lost track of the criteria in their first pass and labelled the pairs again after a re-briefing on the guide; we report that labelling (the superseded first pass is in the supplementary material). Results:
- shot passes (0.96);
- saturation (0.77) and medium (0.77) pass, though not stably;
- background (0.70) and tone (0.64) fail.

The later configurations are much more alike, so pairs that count as "large-gap" within them differ far less. For medium, the median gap of these pairs is 1.8 scale units against 5.6 in round 1. Across both rounds, agreement rises with the gap: for saturation, from 0.42 below one scale unit to 0.84–0.86 at three units or more.

**Round 3** checked the five aspects on the rewritten-prompt images of Q4 (60 pairs) and the six VLM-proposed axes of Q6 (96 pairs), with the same annotators and rule.
- On rewritten images, saturation (0.90) and tone (0.89) pass, and medium (0.77) passes, though not stably.
- Shot (0.63) and background (0.38) fail. Background falls below 0.5: on these long, detailed scenes, CLIP's "busy background" reading is more often the opposite of people's than the same.
- None of the VLM-proposed axes passes (Section 6.3).

**Validity is stated per configuration set:**
- all five aspects hold on the round-1 configurations;
- shot, saturation and medium hold on the later configurations;
- every finding that depends on an aspect not validated for its configuration set is labelled as such.

**Table 1. Human validation of language-defined appearance aspects.** Agreement with CLIP on large-gap pairs (95% Wilson interval), share of "can't tell", and mean pairwise Cohen's κ. Rounds 1 and 2: 12 large-gap pairs × 3 annotators = 36 judgements per aspect; round 3: 12 pairs per aspect on rewritten images and 16 per VLM-proposed axis (`results/annotation_round3/`).

| Aspect (left ↔ right pole) | Round 1: agreement | can't tell | κ | Round 2: agreement | can't tell | κ | Round 3 (rewrites) | Use |
|---|---|---|---|---|---|---|---|---|
| saturation (muted ↔ vivid) | 0.92 [0.78, 0.97] | 0.00 | 0.67 | 0.77 [0.59, 0.88] | 0.17 | 0.20 | 0.90 | all three sets |
| medium (photo ↔ painting) | 0.90 [0.75, 0.97] | 0.14 | 0.50 | 0.77 [0.57, 0.90] | 0.39 | 0.42 | 0.77 | all three sets |
| shot (close-up ↔ wide) | 0.90 [0.74, 0.96] | 0.19 | 0.55 | 0.96 [0.82, 0.99] | 0.25 | 0.75 | 0.63 ✗ | rounds 1–2 sets |
| tone (modern ↔ vintage) | 0.94 [0.80, 0.98] | 0.11 | 0.29 | 0.64 [0.45, 0.80] | 0.31 | 0.36 | 0.89 | round-1 set, rewrites |
| background (plain ↔ busy) | 0.81 [0.65, 0.91] | 0.11 | 0.33 | 0.70 [0.52, 0.84] | 0.25 | 0.23 | 0.38 ✗ | round-1 set |
| VLM-proposed axes (Q6): lighting, sharpness, idealized, contrast, texture, detail | | | | | | | 0.70, 0.68, 0.68, 0.56, 0.47, 0.34 ✗ | dropped |
| style, quality, depth of field, composition, lighting, viewpoint, clutter, time | fail | | | | | | | dropped |

**A negative result.** We first tried to calibrate each axis with prompts that explicitly request each pole. Requests change more than the requested aspect: "warm light" also produced golden-hour scenes, and "wide shot" produced aerial views. Some requests change the subject itself: Qwen-Image turned "an extreme close-up of a kitchen" into a man's face, which CLIP scored as a perfect close-up. Request prompts are therefore not clean poles, and we use a fixed, data-derived scale instead. This is an early instance of the theme of this paper: what language asks for is not what the image shows.

### 3.4 Displacement, concentration and uncertainty
For a change from configuration A to B, we compute two quantities per subject and aspect.
- **Displacement** is Δ = (median_B − median_A)/s. Here s is the aspect's scale: the square root of the mean within-cell variance over all subject × configuration cells of the 12 configurations. It was computed once and then frozen, so one unit is the typical spread of one configuration on one subject.
- **Concentration** is log(IQR_B/IQR_A).

**Practical margins,** frozen before any comparison was examined:
- a shift of at least 0.5 scale units is a displacement;
- an IQR ratio beyond 1.5 or below 1/1.5 is a change in spread;
- "same place" and "same spread" require the 90% interval to lie inside the margin (equivalence).

**Uncertainty** comes from a hierarchical bootstrap with 10,000 replicates. It resamples subjects within categories and images within cells, with seeds paired when A and B share a checkpoint.

**Pre-registration.** Aspects, margins, scale, analysis code and, for the LLM study, the rewriters, prompts to the VLMs and scoring rules were committed to version control before each analysis was run. Deviations are reported where they occur.
- Q1 has 20 primary tests and Q4 has 20, each Holm-corrected. An effect is called a displacement or a change in spread when it is significant after correction and its estimate exceeds the margin. This shows that the effect differs from zero and that its best estimate exceeds the margin, not that the true effect does: for klein saturation, the interval starts at +0.43.
- "Same place" and "same spread" use unadjusted 90% intervals and are descriptive compatibility statements, not corrected tests.
- The intervals refer to new subjects from these six categories and new seeds, for these configurations; they do not generalize to other prompts or models.
- Q2 and Q3 were specified in advance but are not blind.

### 3.5 Validity conditions
1. Every setting of every configuration is declared.
2. A contrast that changes several settings is a package and is never attributed to one of them.
3. A pooled result is never shown without its per-subject structure.
4. Baselines do not move when configurations are shown or hidden.
5. Measurement validity is stated for the configuration set involved.
6. A claim stated in language, whether from a rewriter, a VLM or an axis name, is treated as a hypothesis to be checked against the images, never as evidence.

---

## 4. The Visual Audit System

The system is a single screen built with D3. It has one main view and several auxiliary views, linked through shared selections of aspect, configuration pair, subject and image. Text inside the views is minimal; numbers, settings and statements appear on hover or selection. Colour identifies configurations consistently, and the frozen margins are drawn wherever a shift or a ratio is shown. [Figure 3: the interface, with T1–T4 marked.]

### 4.1 Main view: where configurations settle
The **configuration map** places each configuration at its typical location (x) and spread (y) on the selected aspect.
- Arrows connect the designed contrasts: solid arrows change guidance only, dashed arrows change a package of settings, and dotted arrows change only the prompt (original → rewritten).
- Hovering a subject redraws the map for that subject alone.

An alternative main view, the **contrast overview**, shows every contrast × aspect as one glyph:
- an arrow for the pooled shift;
- a circle against a reference circle for the spread ratio;
- a count of subjects displaced against the pooled direction.

It shows at once, for example, that guidance and the klein distillation package affect saturation in the same way, while SDXL → SDXL-Turbo has small pooled arrows but many reversed subjects.

### 4.2 Per-subject views
The **subject × configuration matrix** has one row per subject, coloured by location. A shift column for the selected pair flags subjects displaced against the pooled direction, with a counter and a sort by shift (T2).

The **contrast scatters**, one per aspect, place each subject at (Δ, log IQR ratio) with the margins as bands and the pooled estimate as a diamond with its interval. When the pair differs in several settings, a warning replaces the attribution. Dots on both sides of the pooled diamond are the visual signature of a hidden reversal.

### 4.3 Evidence views
- **Paired-seed trajectories** join each image of A to the image of B from the same seed. Displacement appears as lines leaning one way, concentration as lines converging. The lines are trajectories only when A and B share the starting noise (same pipeline and resolution); otherwise images are matched by rank, which aligns quantiles and is drawn dashed.
- **Distributions** show densities of A and B with every image as a tick.
- **The appearance map** places all images of a subject from every configuration on a shared t-SNE of CLIP image embeddings. It is an index to images that reveals defaults outside the five aspects; because t-SNE preserves only local neighbourhoods, areas and distances on it are not read as spread (Section 4.5).
- **Image strips** show all images sorted along the aspect, with the same seed highlighted across configurations.

### 4.4 Language views
- **Rewrite view.** For a rewriting contrast, it lists the rewritten prompts of the selected subject next to their images. It marks the pre-registered word families (lighting, time of day, cinematic, colour, background, style), and it plots each rewrite's text-side score against its image's score on the selected aspect. A rewrite that says "vivid" next to an image that is muted is visible as a point off the diagonal.
- **Statement view.** For a VLM description of a contrast, each statement is listed with its coded aspect and direction. Selecting a statement selects the matching contrast scatter, trajectories and images, and colours the statement by the audit's verdict: confirmed, contradicted, or "the audit finds a narrowing, not a shift" (T4).

### 4.5 Design decisions
Three principles guided the design:
- use established encodings;
- encode each quantity in one view only;
- make every number and every statement lead to images.

Three earlier designs were abandoned:
- **projection envelopes**, which readers took as spread although t-SNE preserves only local neighbourhoods;
- **baselines that moved with visibility**, which made one concentration read 0.78, 0.35 or 1.00 depending on which configurations were shown;
- **summary cards and a pooled all-prompts view**, which hid exactly the reversals T2 must expose.

---

## 5. Auditing 12 Configurations

### 5.1 Q1: guidance concentrates first and displaces only saturation
In klein-base 4B, whose measurements are validated on all five aspects, raising guidance from 1 to 4 concentrates four aspects beyond the margin: saturation ×0.51 [0.43, 0.61], medium ×0.53, tone ×0.49 and background ×0.65. Shot narrows (×0.68) but stays inside the margin.

Only saturation is also displaced, toward vivid colour, by +0.65 [+0.43, +0.93] scale units. Per subject, it moves toward vivid by at least the margin in 15 of 24 subjects (14 when each subject's own 90% interval must also exclude zero), and by that much toward muted in none. Medium, shot and background stay in the same place, and tone's small shift toward modern is not significant.

Qwen-Image-2512 shows the same direction with smaller effects on its validated aspects:
- saturation concentrates (×0.64) and shifts toward vivid (+0.39, below the margin);
- medium and shot stay in place.

Its rescaled guidance means that guidance 4 is not the same dose in both pipelines. **In klein-base 4B, raising guidance mainly removed alternatives rather than moving the typical output, saturation being the exception; Qwen-Image showed the same directions with smaller effects, significant only for saturation.** Two guidance values do not show a dose-response. [Figure 1: paired-seed trajectories at guidance 1 and 4. Figure 4: per-subject shift and spread ratio, both families.]

### 5.2 Q3: a distillation package repeats the guidance pattern, more strongly
Replacing klein-base 4B (guidance 1) with the distilled klein 4B changes the checkpoint and reduces the steps from 50 to 4.
- **All five aspects concentrate** (×0.41 to ×0.63).
- **Only saturation is displaced** (+0.95 [+0.67, +1.19]).

This is the guidance pattern, as strong or stronger, and it supports DefaultShift's observation [6] against a measured guidance intervention in the same family. The package is not attributed to either of its parts. The klein 9B package changes defaults much less (spreads ×0.77–0.88, no resolved shift).

### 5.3 Q2: shared defaults, two signatures, and pooled numbers that mislead
Among the eight configurations specified for Q2, only 5 to 8 of the 28 pairs per aspect differ beyond the margin. Two configurations have strong signatures:
- **SDXL** leans toward painting (medium +3.64 [+1.55, +4.16]), muted colour (−1.68), busy backgrounds (+1.12) and a vintage tone (+0.65);
- **Qwen-Image** frames subjects closer (shot −1.81 [−2.44, −0.79]).

Spreads differ more than locations: SD 1.5 is the most varied, FLUX.2 dev and the klein models the most concentrated.

**Pooled comparisons hide opposite shifts.** In **61 of 140** configuration-pair × aspect comparisons, the pooled difference lies within the margin, yet at least three subjects shift beyond +0.5 and three beyond −0.5. (Background and tone counts that involve the later configurations rest on aspects not validated there; on validated aspects only, 38 of the 60 pooled comparisons within the margin hide opposite shifts.)

The clearest case is SDXL → SDXL-Turbo, a package of five settings. Every pooled shift is "same place" or unresolved, yet four of five aspects hide opposite shifts. For saturation, 9 subjects become more vivid and 6 more muted, each with its own interval excluding zero. [Figure 5.]

### 5.4 Measurement failures that only the images exposed
Three failures in this project looked like findings until the images were inspected:
- **the reversed style axis:** its name said "stylized" while the images were polished photographs;
- **the close-up request:** "close-up of a kitchen" produced a face;
- **validity that did not transfer:** background and tone, validated on varied configurations, failed on homogeneous ones.

In each case the language attached to a number (an axis name, a request) did not match what the images showed.

---

## 6. Language in the Loop: Rewriting, Describing and Proposing

This section reports the pre-registered LLM study (`experiments/llm_study/PREREG.md`, committed before any rewritten image or VLM output existed).

### 6.1 Q4: what does LLM prompt rewriting change?
**Setup.**
- **Rewriters:**
  - FLUX.2's official prompt upsampler: Mistral-Small-3.2-24B, the FLUX.2 dev text encoder, with Black Forest Labs' system message and temperature 0.15 [21];
  - Qwen3.5-4B with the same instruction.
- **Rewrites:** each of the 24 prompts is rewritten once per seed, as a deployed rewriter would rewrite each request independently. Median length is 156 words (FLUX.2) and 126 words (Qwen).
- **Generation:** images come from klein 4B and FLUX.2 dev with the original seeds, so each rewritten image is paired with an original image from the same starting noise.
- **Tests:** 20 pre-registered tests, Holm-corrected.
- **Deviation 1:** the diffusers implementation of the upsampler pads every input to 2,048 tokens. With our library versions this produced degenerate text, so the same model and messages were called without padding before any image was generated.

**Rewriting adds no validated variety, and its largest effect fails validation.** Each contrast is read only on aspects validated on both its sides (Table 1): saturation, tone and medium for klein 4B; saturation and medium for FLUX.2 dev.
- **Spread.** In neither generator does any validated aspect become more varied beyond the margin (ratios ×1.13–1.49, none resolved as widened).
- **Location.** No validated aspect is displaced after correction for 20 tests. Medium moves toward painting/illustration in both generators: +0.53 [+0.20, +0.92] in klein 4B (12 subjects up, 2 down) and +0.37 [+0.14, +0.72] in FLUX.2 dev. Both intervals exclude zero, so this is a consistent trend. In the images, photographic birds become detailed illustrations (Figure 6).
- **The largest effect is a measurement failure.**
  - The strongest result of the whole test family is FLUX.2 dev's backgrounds moving toward busy: +0.67 [+0.47, +0.91], Holm-corrected p = .002, 17 of 24 subjects up, none down.
  - It lies on an axis that people did not validate for FLUX.2 dev's images (round 2), and that they contradict on rewritten images (agreement 0.38, round 3).
  - Read without the human check, it would have been the headline finding. It is the clearest instance of T3 in this study.

**The choice of LLM changes the defaults.**
- With Qwen3.5-4B as rewriter, saturation moves toward **muted** (−0.62; 15 subjects down).
- Medium again moves toward illustration (+0.56).
- The two rewriters differ by −0.36 in saturation.
- "A traveler" becomes a medieval fantasy wanderer in misty forests and lamp-lit streets, a reading of the subject that neither the user nor the generator chose.

**The extra variety comes from sampling text, not from releasing the generator's defaults.**
- Reusing one rewrite for all 32 seeds **concentrates** every aspect relative to the original prompt (×0.71–0.79).
- Varying the rewrite across seeds widens it again (×1.25–1.80 against the fixed rewrite).
- In this design, a single detailed rewrite narrows the output, and the variety under per-seed rewriting comes mostly from sampling different texts. This is one fixed-rewrite comparison with one rewriter instruction; it does not show that the diversity gains reported for rewriting [19, 20] have the same source.

**Text and image agree only in part** (validated aspects only).
- Every rewrite of both LLMs specifies lighting, typically "soft, diffused" or "warm".
- **The text moves toward "a photograph", while the images move toward illustration.**
- **The text moves toward "vivid", while the Qwen-rewritten images become muted.** The Qwen-rewritten images were not sampled in round 3 and are read with the aspects validated for the FLUX.2 rewrites.
- **Per subject,** with the FLUX.2 rewriter the text-side shift predicts the image-side shift for saturation (Spearman 0.42 on klein 4B, 0.53 on FLUX.2 dev). It predicts nothing for medium or tone, or for the Qwen rewriter.

What a rewrite *says* about appearance is only partly what the generator *does* with it: auditing a rewriter requires its images, not only its text.

### 6.2 Q5: can VLMs describe these differences correctly?
**Setup.**
- **Describers:** Qwen3.5-4B and Mistral-Small-3.2-24B.
- **Input:** each VLM sees two grids (8 images of A, 8 of B) per subject, or 16 vs. 16 across subjects at the pooled level, for six contrasts:
  - the two guidance contrasts;
  - the klein 4B package;
  - SDXL → Turbo;
  - the two rewriting contrasts.
- **Questions:** each VLM gives a free-text description and answers constrained questions per aspect, with options in random order:
  - "closer to <right> / closer to <left> / no clear difference";
  - "more / less / about equally varied".
- **Ground truth** is the audit on all 32 seeds, scored only on aspects validated for the configurations involved. It depends on our frozen margin: a VLM that reports a real shift smaller than 0.5 scale units counts as wrong. The null control below does not depend on the margin, because there the truth is "no difference" by construction.
- **Null control (deviation 2, added after the first answers were scored, so exploratory):** the same configuration on both sides (klein 4B; SDXL), with B using seeds shifted by 16. Here the truth is "no difference" by construction.

**Table 2. VLM answers against the audit** (six contrasts and two null controls; each contrast scored on aspects validated on both its sides).

| | Qwen3.5-4B | Mistral-24B | Audit |
|---|---|---|---|
| Per-subject shift accuracy (n = 320) | 0.49 | 0.48 | 22% "no difference" |
| Per-subject variety accuracy (n = 235) | 0.63 | **0.79** | |
| Pooled shift accuracy (n = 70) | 0.14 | 0.14 | 86% "no difference" |
| Concentration reported as a shift | 12/13 | 13/13 | |
| Pooled shift claimed where opposite per-subject shifts cancel | 49/50 | 50/50 | |
| **Null control: shift reported** (subject / pooled) | 98% / 98% | **100% / 100%** | 0% |
| **Null control: change in variety reported** | 99% / 100% | 100% / 100% | 0% |
| **Null control: free text claims a difference** (units) | 90% | 93% | 0% |

**Findings:**
- **Asked how two sets differ, both tested VLMs almost always report a difference** (with this prompt format and these grids).
  - Between two sets from the same configuration, both VLMs report a shift and a change in variety in 98–100% of constrained answers.
  - In free text, 90–93% of their descriptions claim a difference on a measured aspect or in variety.
  - A claim of difference from these VLMs therefore says little about *whether* two configurations differ (T4). We measured false-positive rates, not discrimination over a balanced set of same and different pairs; the descriptions can still carry information about direction (below).
  - The VLMs saw 8 vs. 8 images per subject (16 vs. 16 pooled), while the audit used 32 seeds; some answers scored as wrong may describe real differences between the two samples shown.
- **Given a real difference, the larger VLM often reads the direction of variety correctly.** Mistral-24B is right in 79% of per-subject cases, about 90% for distillation and SDXL → Turbo. Its free text mentions narrowing in 88% of the units where the audit finds it. It mentions narrowing almost as often where there is none, so the mention is not evidence.
- **Narrowing becomes movement, and pooled claims fail where they matter.**
  - Of the cases the audit marks "same place, less varied", 12 of 13 (Qwen3.5-4B) and 13 of 13 (Mistral-24B) were answered with a shift (T1).
  - Of the pooled "no change" cases that hide opposite per-subject shifts, 49 of 50 (Qwen3.5-4B) and 50 of 50 (Mistral-24B) were described as a pooled shift (T2).
- **Free-text coding.** Statements are coded with a constrained LLM coder; the first author checks a 20% sample [pending].

**Reading.** A VLM's description of "how model B differs from model A" can suggest where to look, but it is not a finding. It asserts differences that do not exist, calls narrowing movement, and repeats pooled claims that are false for many subjects. The statement view (Section 4.4) therefore links each statement to the evidence that confirms or contradicts it.

### 6.3 Q6: can a VLM propose new appearance axes?
- **Proposals.** Asked to propose opposite-pole pairs that distinguish the sets, Mistral-24B mostly restates properties we already measure (dark ↔ bright, close-up ↔ wide, muted ↔ vivid, indoor ↔ outdoor).
- **Candidates.** By the pre-registered rule (proposed for at least two contrasts, not among the round-1 candidates), six new properties qualify:
  - overall sharpness;
  - level of detail;
  - natural vs. idealized/retouched;
  - contrast;
  - lighting character (flat vs. dramatic);
  - surface texture.
- **Validation.** None of the six passes round 3:
  - lighting 0.70, sharpness 0.68, natural vs. idealized 0.68, contrast 0.56, texture 0.47;
  - level of detail 0.34, which CLIP mostly orders the opposite way from people.
- **Reading.** People understood the proposed properties; the annotators used "can't tell" in only 11–25% of judgements. But CLIP does not order images along them as people do. A property stated in language becomes a measurement only after human validation, so the VLM can propose what to measure but cannot extend the measurement by itself.

---

## 7. Expert Evaluation [pending]
- **Ethics and participants.** Approved by [institution]'s ethics board. Five researchers who train, evaluate or select text-to-image models.
- **Design.** Each expert solves T1–T4 twice, with the system and with a strong baseline, on different cases of the same kind:
  - the baseline offers a score table with every number the system uses, an unsorted image grid, the rewritten prompts and the VLM descriptions as text;
  - condition order is counterbalanced, and expected answers are fixed from the frozen analyses.
- **Cases** use only validated aspects:
  - T1: klein-base 4B saturation vs. medium;
  - T2: SDXL → Turbo saturation and a Q2 comparison that hides opposite shifts;
  - T3: a reading on an aspect not validated for its configurations (Qwen-Image tone) and a package read as one setting (SDXL → Turbo);
  - T4: one VLM statement the audit contradicts and one it confirms (`docs/EXPERT_SESSION.md`).
- **Sessions** last about 55 minutes with think-aloud and a semi-structured interview, which includes the question: "Would you trust a VLM's description of how two models differ? What would you need to check?"
- **Results** [per task: correct answers with system vs. baseline out of five, image evidence cited, confidence, themes and quotes; reported descriptively].

---

## 8. Discussion

**Separate location from spread before reading "less diverse".** In the guidance and distillation contrasts and the fixed-rewrite condition, narrowing was larger and more common than moving: they removed alternatives more than they moved the typical output. Per-seed rewriting was the exception: it neither narrowed nor widened beyond the margin.

**Never read a pooled shift without its per-subject structure.** On validated aspects, 38 of the 60 pooled "no difference" comparisons concealed opposite shifts, and both VLMs turned every such case they were asked about into a pooled claim.

**Language proposes; images decide.** In all three roles, the language attached to images was informative but not reliable:
- **axis names** were reversed or failed to transfer between configuration sets;
- **rewrites** described looks that the generator did not produce, and the largest measured effect of rewriting lay on an axis that people reject for rewritten images;
- **VLM descriptions** reported differences even between sets from the same model.

- **VLM-proposed axes** were understood by people but not measured by CLIP as people see them.

This suggests a division of labour for LLM-assisted visual analytics. LLMs are good at proposing what to look at: candidate axes, suspected differences, readable summaries. A visual audit with validated measurements, stated margins and a route to the images decides what is true. The statement view makes this division part of the interface.

**Validate per configuration set and read differences with their size.** Eight of the 15 candidate axes failed human validation in round 1, and all six VLM-proposed ones failed in round 3. Axes confirmed on varied models did not all hold among similar ones or on rewritten images, and agreement rose with the size of the difference.

**Limitations.**
- CLIP axes are proxies: five of fifteen candidates survived, and lighting and viewpoint are not among them. A second encoder [18] is used as a sensitivity check [pending].
- The scale is derived from the configurations themselves, so the 0.5 margin depends on which configurations were included; it is not a perceptual unit.
- Configurations differ in native resolution (512–1328 px). Resizing to a common encoder input does not remove resolution effects on content, so cross-configuration contrasts (Q2, SDXL → Turbo) may include them; Q1 and Q4 hold resolution fixed.
- 32 seeds × 24 subjects describe these samples.
- The rewriters run with one official instruction and one temperature. The VLMs are two open models queried with one prompt format; larger proprietary VLMs may behave differently. The null control shows that, with this format, the VLMs report a difference regardless of the images.
- Configurations are compared at recommended settings, so family and scale are not causal factors.
- Demographic attributes are out of scope, although VLM free text occasionally reported them ("exclusively male").
- The expert study is small and drawn from the authors' network.

## 9. Conclusion
Language now measures, changes and explains the appearance defaults of text-to-image models. We showed that in each role it produces claims that can be wrong in characteristic ways, and we presented a visual audit method that grounds every such claim in human-validated, per-subject image evidence with pre-registered margins.

Applied to 12 open configurations, two LLM rewriters and two VLM describers, it shows:
- in FLUX.2 klein, guidance and distillation mainly narrow appearance;
- on validated aspects, 38 of 60 pooled "no difference" comparisons hide opposite shifts across subjects;
- an official prompt rewriter adds no validated variety, and its largest apparent effect is a measurement failure;
- both tested VLMs, with our question format, report differences even between image sets from the same model.

The method and the system make these checks routine before a model, a setting or a rewriter is released.

---

## Acknowledgments
[Annotators; expert participants; funding.]

## References
*1–18 verified 2026-10-11 (`docs/OUTLINE.md`). 19–22 are new for v2 and must be verified (identifiers from searches on 2026-10-15) before submission. The CG&A cap of 20 references no longer applies.*

1. The Vendi Score: A Diversity Evaluation Metric for Machine Learning. arXiv:2210.02410.
2. Classifier-Free Diffusion Guidance. arXiv:2207.12598.
3. DIMCIM. arXiv:2506.05108.
4. GRADE: Quantifying Sample Diversity in Text-to-Image Models. arXiv:2410.22592.
5. Attribute-conditional diversity benchmark for text-to-image models. arXiv:2511.10547.
6. DefaultShift. arXiv:2608.21784.
7. An Exploration of Default Images in Text-to-Image Generation. arXiv:2505.09166.
8. Stage-wise dynamics of classifier-free guidance. arXiv:2509.22007.
9. Adversarial Diffusion Distillation. arXiv:2311.17042.
10. Describing Differences in Image Sets with Natural Language (VisDiff). arXiv:2312.02974.
11. Discovering Divergent Representations between Text-to-Image Models (CompCon). arXiv:2509.08940.
12. ViBEx. arXiv:2504.19703.
13. Varif.ai. DOI 10.1145/3715336.3735847.
14. CUPID. DOI 10.1111/cgf.15086.
15. M. Gleicher, Considerations for Visualizing Comparison. DOI 10.1109/TVCG.2017.2744199.
16. Qwen-Image Technical Report. arXiv:2508.02324.
17. Learning Transferable Visual Models From Natural Language Supervision (CLIP). arXiv:2103.00020.
18. SigLIP 2. arXiv:2502.14786.
19. Prompt Expansion for Adaptive Text-to-Image Generation. arXiv:2312.16720 (ACL 2024). [verify]
20. Using LLMs as prompt modifier to avoid biases in AI image generators. arXiv:2504.11104. [verify]
21. Black Forest Labs, FLUX.2 (model and reference implementation including prompt upsampling), github.com/black-forest-labs/flux2, commit 5a5d316. [verify citation form]
22. VDiff-Bench: A Challenging Benchmark for Fine-Grained Image Difference Identification. arXiv:2609.06245. [verify]

## Figures (plan)
| # | Content | Section |
|---|---|---|
| Graphical abstract / 1 | The three roles of language (axis, rewrite, description), each with one audited example and its image evidence | 1 |
| 2 | Method pipeline: language-defined axes → human validation per configuration set → fixed scale → shift and spread with margins → linked views | 3 |
| 3 | Interface with T1–T4 marked, including rewrite and statement views | 4 |
| 4 | Q1: per-subject shift × spread ratio, both families | 5.1 |
| 5 | SDXL → Turbo saturation: hidden opposite shifts | 5.3 |
| 6 | Q4: original vs. rewritten images with the same seeds (bird: photo → illustration; traveler: modern hiker → fantasy wanderer), plus text-side vs. image-side shift | 6.1 |
| 7 | Q5: VLM answers against the audit, with one contradicted statement traced to the images | 6.2 |
| 8 | Expert results | 7 |
