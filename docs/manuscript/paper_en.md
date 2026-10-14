# Visual Auditing of Appearance Defaults in Text-to-Image Models

*Manuscript draft v1, 2026-10-14. Written to the length and structure of an IEEE CG&A regular feature article (≤ 14 pages including bios, ≈ 7,500 words, ≤ 20 references, abstract ≤ 150 words). [Bracketed] text marks results that are not yet available (expert evaluation, closed models) and figure placeholders. Numbers come from `results/`; each section names its source in a comment for checking and will be stripped before submission.*

---

## Abstract

When a prompt leaves framing, palette or medium unspecified, a text-to-image model decides them, and it decides them the same way again and again. These appearance defaults change whenever developers raise guidance, distill a model or switch checkpoints, yet evaluations report only how diverse the outputs are. A diversity score cannot tell whether outputs settle somewhere else (displacement) or more tightly in the same place (concentration), nor whether a pooled conclusion holds for every subject. We present a visual audit method that places declared model configurations on human-validated appearance axes, separates displacement from concentration under pre-registered margins, shows per-subject structure and traces every reading to the images. Auditing 12 open configurations on 24 everyday subjects, we find that guidance and distillation mainly concentrate appearance and displace only saturation, and that 61 of 140 pooled comparisons hide opposite shifts across subjects. [Five experts …]

---

## Introduction

A prompt such as "a kitchen" names a subject and nothing else. It does not say whether the image should be a photograph or a painting, a close-up or a wide view, muted or vivid, plain or cluttered. The model decides, and modern models decide in nearly the same way every time. In a pilot, we generated 16 images of one minimal prompt and measured their diversity with the Vendi score [1]. Diversity fell from 7.45 for Stable Diffusion 1.5 to 3.47 for SDXL-Turbo and 2.79 for FLUX.2 klein. Within a single model, raising classifier-free guidance [2] from 1 to 4 lowered it from 5.95 to 2.32. We call these unrequested, repeated decisions **appearance defaults**.

Appearance defaults are not a fixed property of a model. They move whenever the people who build and evaluate models make an ordinary engineering decision. Guidance is raised for better prompt adherence. A model is distilled so that it runs in four steps instead of fifty. A checkpoint is replaced by a larger one, or a team moves to a new model family. Each of these decisions is taken for another reason, and each changes the look that every downstream user receives by default. Developers need to see these side effects before a release. Evaluators need to know what changed and whether the change is real, not only how large it is. Beyond both groups, defaults shape what millions of generated images look like, so a homogenized or shifted default narrows or silently changes how subjects are depicted.

Current practice summarizes such changes with a diversity score, often next to quality and prompt-alignment metrics. Recent benchmarks have shown convincingly that diversity falls as models improve [3, 4, 5], and an audit of distilled replacement models has shown that distillation shifts attribute distributions [6]. But a single score leaves three questions open for an evaluator who compares configurations.

1. **Displacement or concentration?** "Less diverse" can mean that outputs moved to a different look, or that they collapsed onto the look they already had. These are different findings with different remedies. A diversity score merges them.
2. **Pooled or per subject?** A change averaged over prompts can hide opposite changes on different subjects. In our audit this is the rule rather than the exception: almost half of the pooled "no difference" comparisons conceal subjects that move strongly in opposite directions.
3. **Is the measurement right?** Appearance attributes are scored by automatic encoders. Without a route back to the images, a wrong measurement looks exactly like a finding. We met wrong measurements more than once in this project.

These questions call for a combination that neither metrics nor existing visual tools provide. The analysis must be aligned across many configurations on a shared and validated measurement. It must separate where outputs settle from how tightly they settle. It must show the per-subject structure behind every pooled number. And it must keep each reading connected to the images it came from.

We present a **visual audit method** for appearance defaults and use it to audit 12 open configurations of five model families. The method is built around three audit tasks: telling displacement from concentration (T1), checking whether a pooled conclusion holds per subject (T2), and tracing a reading to the images to catch invalid measurements or attributions (T3). The audit answers three research questions:
- **Q1 (confirmatory):** does raising guidance displace appearance, concentrate it, or both, in two model families?
- **Q2 (descriptive):** where do configurations settle at their recommended settings, and do their differences hold across subjects?
- **Q3 (pre-specified case):** what does a distillation package change, compared with guidance?

Our contributions are:
- **An audit method** for appearance defaults. It combines appearance axes validated by people separately for each set of configurations, a fixed per-aspect scale, a separation of displacement from concentration with pre-registered practical margins and hierarchical uncertainty, and explicit validity conditions for comparing configurations.
- **A visual audit system** in which a main view of all configurations is linked to per-subject, per-contrast and per-image views designed for T1–T3.
- **An audit of 12 open configurations** with bounded findings:
  - guidance concentrates appearance first and displaces only saturation;
  - a distillation package repeats and strengthens this pattern;
  - most configurations share their defaults, while two have strong signatures;
  - pooled comparisons frequently hide opposite shifts;
  - measurement validity itself depends on the configuration set.
- **An expert evaluation** with five experts against a strong baseline, and lessons for the visual auditing of generative models.

We do not propose a new diversity metric, we do not claim that diversity falls as models improve (others have shown this [3, 4]), and we make no causal claim about what determines defaults beyond the guidance intervention we control.

---

## Related Work

**Measuring defaults and diversity.** The Vendi score [1] measures the effective number of distinct samples in a set. DIMCIM [3] and GRADE [4] measure diversity for text-to-image models at the level of concepts and attributes. They report that models produce narrow distributions for unspecified attributes and that diversity tends to fall in newer models. An attribute-conditional benchmark [5] measures diversity per attribute. A study of default images [7] characterizes what models produce when the prompt is empty or minimal. Closest to our work is DefaultShift [6]. It audits distilled replacement models against their teachers with closed attribute vocabularies and observes that distillation behaves like increased teacher guidance. These works quantify *how much* outputs converge or *which* attributes change. None separates a shift of the typical output from a narrowing around it across a set of configurations, and none offers a visual workflow that leads from a number back to the images. Our Q3 tests DefaultShift's observation directly by comparing a distillation package with a measured guidance intervention in the same family.

**Guidance and distillation.** Classifier-free guidance [2] trades diversity for prompt adherence. An analysis of its stage-wise dynamics [8] shows that strong guidance suppresses weaker modes, which predicts concentration. Distillation methods such as adversarial diffusion distillation [9] produce few-step models that are widely deployed as drop-in replacements. Q1 asks whether concentration under guidance is accompanied by displacement, and on which appearance aspects.

**Comparing image sets.** VisDiff [10] and CompCon [11] describe in natural language how two sets of generated images differ. They are powerful tools for discovering differences, but their output is a description, not a calibrated statement. It does not say whether a difference is a shift or a narrowing, how large it is relative to a stated margin, or whether it holds for each subject.

**Visual analytics of generated images.** ViBEx [12] and Varif.ai [13] support the exploration of output variation for one model or prompt. CUPID [14] visualizes distributions of generated images through contrastive embeddings. These systems help a user understand and steer one generator. Our setting is different: an evaluator compares many declared configurations and needs aligned, validated and traceable comparisons.

**Visual comparison.** Gleicher's framework [15] distinguishes juxtaposition, superposition and explicit encoding. We use explicit encoding for the differences that matter (shift and spread ratio per subject), superposition for the configuration overview, and juxtaposition only for images.

---

## The Audit Method

### Tasks

The three audit tasks come from the decisions an evaluator faces when a setting changes, from the gaps of the work above, and from failures we met in this project.
- **T1, displacement or concentration.** Diversity metrics merge the two [1, 3, 4], and DefaultShift [6] separates direction from entropy only for closed categories and replacement pairs.
- **T2, pooled or per subject.** In our pilot, SDXL-Turbo shifted composition by +1.31 for "a house" and −1.33 for "a kitchen", while the pooled shift was +0.07.
- **T3, tracing to evidence.** An automatic axis turned out to be reversed. A request for a close-up of a kitchen produced a face that the encoder scored as a perfect close-up. And a contrast that changes several settings at once invites an attribution to one of them.

### Study material

We use 24 minimal, uncontroversial prompts in six categories (people, animals, objects, indoor scenes, outdoor scenes, activities). Each prompt names only its subject, for example "a doctor", "a bowl of fruit" or "a train station".

The audit covers 12 open configurations, each at the settings recommended on its model card:
- Stable Diffusion 1.5, SDXL, SDXL-Turbo and Stable Diffusion 3.5 Large;
- FLUX.2 dev;
- FLUX.2 klein-base 4B at guidance 4 and 1, klein 4B, klein-base 9B and klein 9B;
- Qwen-Image-2512 [16] at guidance 4 and 1.

Every configuration generates 32 images per prompt from the same 32 seeds, giving 9,216 images. bf16 outputs depend slightly on batch size, so the batch size is fixed per configuration. Pipeline, scheduler, text encoder and every sampling setting are read from the weights and declared. Declaration has consequences: klein 4B and 9B use different text encoders, so we do not treat model scale as a cause. [Three closed services were sampled descriptively and appear in a sidebar.]

### Appearance aspects and their validation

An image's score on an aspect is its CLIP ViT-L/14 [17] similarity to a right-hand text pole minus its similarity to a left-hand pole, for example "muted desaturated colors" versus "vivid saturated colors". Such scores are cheap and consistent, but they are proxies. We therefore keep an aspect only if people confirm that CLIP orders images correctly on it.

**Validation procedure.** For each candidate aspect we sampled same-prompt image pairs, some with a large CLIP gap and some with a medium or small gap. Annotators saw the two images and the two poles and chose the image closer to the right pole, or "can't tell". The decision rule was fixed before any labels were collected. An aspect is kept if, on the large-gap pairs, people agree with CLIP's direction on at least 75% of the pairs they could judge, and answer "can't tell" on at most 40%. Annotators worked independently and saw neither CLIP's answers nor each other's labels.

**Round 1.** Round 1 used 240 pairs from the configurations generated first (SD 1.5, SDXL, SDXL-Turbo, klein-base 4B at both guidance values and klein 4B), and three annotators. Of 15 candidate aspects, seven passed (Table 1). Saturation, medium (photograph vs. painting), shot (extreme close-up vs. wide view), tone (modern vs. vintage) and background (plain vs. busy) were frozen for the analysis. Mood also passed, but it is coupled with tone, so we kept only tone to avoid counting one change twice. Indoor/outdoor passed, but not stably, and is shown in the system only.

Several aspects failed:
- **Style** failed in the most instructive way. CLIP called klein's polished photographs "stylized", and people agreed with its direction on only 17% of pairs, so the axis was systematically reversed.
- **Quality, depth of field, composition, clutter, lighting and viewpoint** were unreliable.
- **Time of day** could not be judged, because nearly every image is set in daytime.

A fourth annotator never used "can't tell", against the guide, and was excluded before the analysis; including them changes no verdict.

**Round 2.** The six later configurations (SD3.5 Large, FLUX.2 dev, Qwen-Image at both guidance values, klein-base 9B and klein 9B) received their own check: 120 pairs, the same rule and the same three annotators. Two annotators had lost track of the criteria in their first pass, so after a re-briefing on the guide they labelled the pairs again, and we report that labelling. (The superseded first pass is in the supplementary material; it validates shot only.)

On the later configurations:
- shot passes (0.96);
- saturation (0.77) and medium (0.77) pass, though not stably: each fails when one annotator is left out;
- background (0.70) and tone (0.64) fail.

The reason is visible in the pairs themselves. The later configurations are much more alike than the early ones, so pairs that count as "large-gap" within them differ far less in absolute terms. For medium, the median gap of these pairs is 1.8 scale units in round 2 against 5.6 in round 1. Across both rounds, agreement rises with the gap: for saturation it is 0.42 below one scale unit and 0.84–0.86 at three units or more.

We therefore state validity **per configuration set**:
- all five aspects are validated on the round-1 configurations;
- shot, saturation and medium are validated on the later configurations;
- background and tone are not validated on the later configurations, and every finding that depends on them there is labelled as such.

**Table 1. Human validation of appearance aspects.** Agreement with CLIP on large-gap pairs (95% Wilson interval), share of "can't tell", and mean pairwise Cohen's κ; 36 judgements per aspect and round.

| Aspect (left ↔ right pole) | Round 1: agreement | can't tell | κ | Round 2: agreement | can't tell | κ | Use |
|---|---|---|---|---|---|---|---|
| saturation (muted ↔ vivid) | 0.92 [0.78, 0.97] | 0.00 | 0.67 | 0.77 [0.59, 0.88] | 0.17 | 0.20 | both sets |
| medium (photo ↔ painting) | 0.90 [0.75, 0.97] | 0.14 | 0.50 | 0.77 [0.57, 0.90] | 0.39 | 0.42 | both sets |
| shot (close-up ↔ wide) | 0.90 [0.74, 0.96] | 0.19 | 0.55 | 0.96 [0.82, 0.99] | 0.25 | 0.75 | both sets |
| tone (modern ↔ vintage) | 0.94 [0.80, 0.98] | 0.11 | 0.29 | 0.64 [0.45, 0.80] | 0.31 | 0.36 | round-1 set |
| background (plain ↔ busy) | 0.81 [0.65, 0.91] | 0.11 | 0.33 | 0.70 [0.52, 0.84] | 0.25 | 0.23 | round-1 set |
| style, quality, depth of field, composition, lighting, viewpoint, clutter, time | fail | | | | | | dropped |

**A negative result.** We first tried to calibrate each axis with prompts that explicitly request each pole, so that a default could be expressed as a position between "asked for vivid" and "asked for muted". It failed.
- Requests change more than the requested aspect: "warm light" also produced golden-hour scenes, and "wide shot" produced aerial views.
- Some requests change the subject itself: Qwen-Image turned "an extreme close-up of a kitchen" into a man's face, which CLIP scored as a perfect close-up.

Request prompts are therefore not clean poles. We use a fixed, data-derived scale instead.

### Displacement, concentration and uncertainty

For a change from configuration A to configuration B, we compute two quantities for every subject and aspect.
- **Displacement** is Δ = (median_B − median_A) / s, where s is the aspect's scale. The scale is the square root of the mean within-cell variance of the aspect score over all subject × configuration cells of the 12 configurations. It was computed once after all configurations had been generated and was then frozen, so one unit is the typical spread of one configuration on one subject. The scale does not change when configurations are added to or hidden from a view.
- **Concentration** is log(IQR_B / IQR_A), the change of the interquartile range.

**Practical margins,** frozen before any comparison was examined:
- a shift of at least 0.5 scale units counts as a displacement;
- an IQR ratio above 1.5 or below 1/1.5 counts as a change in spread;
- a verdict of "same place" or "same spread" requires the whole 90% interval to lie inside the margin, an equivalence test, so that absence of evidence is never reported as evidence of absence.

**Uncertainty** comes from a hierarchical bootstrap with 10,000 replicates. It resamples subjects within categories and images within cells, and keeps seeds paired whenever A and B share a checkpoint.

**Pre-registration.** The aspects, the margins, the scale definition and the analysis code were committed to version control before each analysis was run.
- Q1 is confirmatory: 20 primary tests (two families × five aspects × two effects), Holm-corrected. An effect is called a displacement or a change in spread when it is significant after correction and its estimate exceeds the margin.
- Q2 and Q3 were specified in advance but are not blind, because some of their contrasts had been viewed in the tool during development.

### Validity conditions

The method attaches five conditions to every comparison, and the system enforces them visually:
1. every setting of every configuration is declared;
2. a contrast that changes several settings is a package and is never attributed to one of them;
3. a pooled result is never shown without its per-subject structure;
4. baselines do not move when configurations are shown or hidden;
5. measurement validity is stated for the configuration set involved.

---

> **Sidebar: Displacement or concentration?**
> Consider three configurations generating "a kitchen". A produces muted and vivid kitchens in equal measure. B produces only vivid kitchens. C produces only kitchens of A's most common, moderately saturated look. B and C have the same, lower diversity than A, and a diversity score treats them alike. Yet B has been displaced: its typical output moved, and a user who wants muted kitchens must now ask for them. C has been concentrated: its typical output stayed where it was, but the alternatives disappeared. Remedies differ too. Displacement may be acceptable or even intended (a model tuned for vivid colour); concentration calls for prompts or sampling that restore variety. Our method reports the two separately, per subject, each against a stated margin. [Figure: three strips and their positions in shift × spread-ratio space.]

---

## The Visual Audit System

The system is a single screen built with D3. It has one main view and several auxiliary views, linked through shared selections of aspect, configuration pair, subject and image. Selecting any of these in one view updates all others. Text inside the views is minimal: numbers, settings and labels appear on hover. Colour identifies configurations consistently across views, and the frozen margins are drawn wherever a shift or a ratio is shown. [Figure 3: the interface, with T1–T3 marked.]

### Main view: where configurations settle

The **configuration map** places each configuration at its typical location (x, median over subjects of the per-subject median) and its typical spread (y) on the selected aspect. Arrows connect the designed contrasts. Solid arrows change guidance only; dashed arrows change a package of settings, and hovering one lists the differing settings. Hovering a subject in any other view redraws the map for that subject alone, which shows at once whether the configurations keep their order. The map answers Q2 at a glance and is the entry point to T1: a long horizontal arrow is a displacement candidate, a downward arrow a concentration candidate.

An alternative main view, the **contrast overview**, shows every designed contrast × aspect as one glyph:
- an arrow whose length and direction encode the pooled shift;
- a circle whose size, against a reference circle, encodes the spread ratio;
- a small count of subjects displaced against the pooled direction.

This view shows the whole audit on one screen. For example, it is immediately clear that guidance and the klein distillation package affect saturation and tone in the same way, while SDXL → SDXL-Turbo has small pooled arrows but many reversed subjects.

### Per-subject views: does the pooled answer hold?

The **subject × configuration matrix** has one row per subject and one column per configuration, coloured by location on the selected aspect. A row that changes colour across columns is a subject-dependent default. For the selected pair, a shift column shows each subject's Δ. Subjects displaced against the pooled direction are flagged; a counter steps through them, and a sort orders the rows by shift. This view serves T2 directly.

The **contrast scatters** are one small scatter per aspect for the selected pair. Each dot is a subject at (Δ, log IQR ratio). The frozen margins appear as bands, so a dot outside the vertical band is a displacement and a dot outside the horizontal band a change in spread. The pooled estimate appears as a diamond with its 90% interval. When the pair differs in more than one setting, a warning replaces the attribution. Dots that straddle the pooled diamond on both sides of zero are the visual signature of a hidden reversal.

### Evidence views: from a number to the images

The bottom panel shows the selected subject and pair in one of three modes.
- **Paired-seed trajectories** join each image of A to the image of B generated from the same seed. Displacement appears as lines leaning one way; concentration appears as lines converging. When A and B do not share starting noise, images are matched by rank and the view says so.
- **Distributions** show the densities of A and B on the aspect, with every image as a tick.
- **The appearance map** places all images of the selected subject from every configuration on a shared t-SNE of CLIP image embeddings, with A and B drawn as density contours. It reveals defaults that lie outside the five aspects, such as the same face or the same composition in every image.

**Image strips** show every image of the selected cells sorted along the aspect. Images from the same seed are highlighted across configurations. Every dot, tick and trajectory in the other views leads to an image here, which is how a reading is verified or rejected (T3).

### Design decisions

Three principles guided the design:
- use established encodings (distributions, scatter plots, contours) rather than novel glyphs wherever possible;
- encode each quantity in one view only;
- make every number lead to images.

Three earlier designs were abandoned for reasons that generalize:
- **Projection envelopes.** An early version drew envelopes around each configuration on the embedding projection. Readers took their size as spread, but t-SNE preserves only local neighbourhoods, so the envelopes could not support that reading. Spread is now read only on validated aspects.
- **Pooled baselines that depended on visibility.** In another version, the concentration of "city street / SDXL-Turbo / tone" was 0.78 with all configurations visible, 0.35 with three and 1.00 with Turbo alone. Baselines are now fixed to all configurations, and hiding only stops drawing.
- **Summary cards and a pooled all-prompts view.** These hid exactly the reversals that T2 must expose, and they were removed.

---

## Auditing 12 Configurations

<!-- sources: results/q1/RESULTS.md, results/q3/RESULTS.md, results/q2/RESULTS.md, results/annotation_round2/RESULTS.md -->

### Q1: guidance concentrates first and displaces only saturation

Raising guidance from 1 to 4 is the cleanest intervention available: the checkpoint, the seeds and every other setting stay fixed. In klein-base 4B, whose measurements are validated on all five aspects, four of the five aspects concentrate beyond the margin. Their spread falls to about half: saturation ×0.51 [0.43, 0.61], medium ×0.53, tone ×0.49 and background ×0.65. Shot also narrows significantly (×0.68) but stays just inside the margin.

Only one aspect is also displaced. Saturation moves toward vivid colour by +0.65 [+0.43, +0.93] scale units. Medium, shot and background stay in the same place under the equivalence rule. Tone moves slightly toward a modern look (−0.37), but not significantly after correction. Per subject, saturation moves toward vivid in 15 of 24 subjects and toward muted in none, and leaving out any one category leaves every conclusion unchanged.

Qwen-Image-2512 shows the same direction with smaller effects on its validated aspects:
- saturation concentrates (×0.64 [0.54, 0.78]) and shifts toward vivid by +0.39, which is significant but below the margin;
- medium and shot stay in the same place, and medium keeps the same spread;
- tone and background are not validated on this configuration set, so we do not interpret their readings.

The smaller effects are consistent with Qwen-Image's rescaled guidance, so guidance 4 is not the same dose in both pipelines.

**Answer to Q1.** Raising guidance mainly concentrates appearance: it removes alternatives rather than moving the typical output. The one exception, in both families, is saturation, which also becomes more vivid. [Figure 1, teaser: the same seeds at guidance 1 and 4 in the paired-seed view. Medium lines converge in place; saturation lines lean toward vivid and converge.] [Figure 4: per-subject shift and spread ratio for both families, with margins and pooled intervals.]

**Workflow.** An analyst starts from the solid guidance arrow on the configuration map, which points down and slightly right on saturation. The contrast scatters show the subject dots below the spread band on four aspects, but outside the shift band only for saturation. The paired-seed trajectories for one subject show lines that converge for medium and converge while leaning for saturation. The image strips confirm both readings in the images.

### Q3: a distillation package repeats the guidance pattern, more strongly

The klein 4B package replaces klein-base 4B, run at guidance 1, with the distilled klein 4B. This changes the checkpoint and reduces the steps from 50 to 4; guidance is 1 in both.
- **All five aspects concentrate** beyond the margin (×0.41 to ×0.63).
- **Only saturation is displaced**, by +0.95 [+0.67, +1.19] toward vivid.

This is the guidance pattern of Q1, as strong or stronger: tone narrows ×0.49 in both cases, and saturation, medium and shot narrow more under distillation. The result supports DefaultShift's observation that distillation acts like increased guidance [6]. Here the observation is made against a measured guidance intervention in the same family, on validated aspects. Because the package changes the checkpoint and the step count together, the system marks it as a package and we attribute the effect to neither.

The klein 9B package changes defaults much less: no shift is resolved, and spreads change by ×0.77 to ×0.88.

### Q2: shared defaults, two signatures, and pooled numbers that mislead

**Shared defaults and two signatures.** For Q2 we compare the eight configurations specified in the pre-registration at their recommended settings: SD 1.5, SDXL, SD3.5 Large, FLUX.2 dev, klein-base 4B, klein 4B, Qwen-Image and klein-base 9B. Most of them share their defaults: per aspect, only 5 to 8 of the 28 configuration pairs differ beyond the margin. Two configurations have strong signatures.
- **SDXL** leans toward painting (medium +3.64 [+1.55, +4.16] from the common centre), muted colour (saturation −1.68), busy backgrounds (+1.12) and a vintage tone (+0.65).
- **Qwen-Image** frames subjects closer (shot −1.81 [−2.44, −0.79]).

Every other configuration stays within ±0.5 of the centre on every validated aspect. Spreads differ more than locations. SD 1.5 is the most varied, while FLUX.2 dev and the klein models are the most concentrated.

**Defaults depend on the subject.** Nine configuration × aspect combinations have subject-dependent defaults, meaning at least three subjects lie beyond the margin on each side. For example, SDXL's tone is vintage for 13 subjects and modern for 3.

**Pooled comparisons hide opposite shifts.** We count a comparison as hiding opposite shifts when its pooled difference lies within the margin but at least three subjects shift beyond +0.5 and three beyond −0.5. This holds for **61 of the 140** configuration-pair × aspect comparisons. Shot (16), background (15) and tone (13) contribute most; the background and tone counts involving the later configurations rest on aspects not validated there.

The clearest single case is SDXL → SDXL-Turbo. It is a package of five settings: checkpoint, scheduler, steps (50 → 1), guidance (5 → 0) and resolution (1024 → 512). Every pooled shift is "same place" or unresolved, so a pooled table would report that Turbo keeps SDXL's defaults. Yet four of five aspects hide opposite shifts. For saturation, 9 subjects become more vivid and 6 more muted, each with its own interval excluding zero. In the system, the dashed arrow on the map is short, but the saturation scatter shows dots on both sides of the pooled diamond. The matrix sorted by shift names the subjects that go each way, and the image strips show the difference. The system also warns that five settings differ, so none of this is attributed to distillation. [Figure 5.]

**Answer to Q2.** Most open configurations settle in similar places on the validated aspects, and two carry strong signatures. But in almost half of all comparisons, a pooled "no difference" is false for many subjects. Comparing configurations by a pooled number is unreliable for appearance defaults.

### Measurement failures that only the images exposed

Three failures in this project looked like findings until the images were inspected.
- **Style axis.** CLIP's style axis ranked klein's polished photographs as "stylized". In the image strips, sorting by the axis put photographs at the stylized end, which made the reversal obvious, and the human check confirmed it (17% agreement).
- **Close-up request.** The calibration request for an extreme close-up of a kitchen produced a man's face, which CLIP scored as a perfect close-up.
- **Validity across configuration sets.** Background and tone, validated on the early configurations, did not hold among the more homogeneous later ones, where the differences are small (Table 1).

In each case a number alone would have been reported as a result. These failures are why T3 is a task of the method rather than an afterthought. [Figure 6: the style reversal traced from the axis to the images.]

---

> **Sidebar: Product defaults.** [Three closed services, sampled on the 24 prompts with 16 images each on (date); descriptive only, because their settings are not declared and may change without notice. Planned content: where each service settles on the validated aspects relative to the open configurations, and how concentrated it is.]

---

## Expert Evaluation

We asked whether the method helps experts reach correct, image-backed judgements on the three audit tasks that a conventional presentation makes hard. The study was approved by [institution]'s ethics board.

**Participants.** Five researchers who train, evaluate or select text-to-image models [roles and experience to be summarized].

**Design.** Each expert solved every task twice: once with the system and once with a baseline, on different cases of the same kind. The baseline was deliberately strong. It offered a score table with every number the system uses (median and spread per configuration and aspect, per-subject medians on request) and an image grid with every image, unsorted. What it lacked was alignment, margins, per-subject structure and image linking. Condition order was counterbalanced across experts and case assignment rotated. Expected answers were fixed from the frozen analyses before the sessions.

Cases used only aspects validated on the configurations involved:
- **T1** compared klein-base 4B saturation (moves and tightens) with medium (tightens in place).
- **T2** used SDXL → Turbo saturation (pooled small, opposite shifts across subjects) and one Q2 comparison flagged as hiding opposite shifts.
- **T3** used the reversed style axis and a package contrast presented as the effect of a single setting.

**Procedure.** Each session lasted about 45 minutes:
1. consent and background;
2. a training case for each condition;
3. the six task trials with think-aloud;
4. a semi-structured interview, covering:
   - which readings the expert would have got wrong with the table and grid;
   - when they went to the images and whether that changed their answer;
   - what they would need to audit their own settings changes;
   - what was unclear or misleading.

For each trial we recorded the answer, whether it matched the expected answer, the evidence cited, confidence (1–5) and time.

**Results.** [Per task: correct answers with the system vs. the baseline (counts out of five), whether answers cited image evidence, confidence, and typical errors. Themes from think-aloud and interviews with representative quotes. We report descriptively; with five participants we make no statistical claim about speed or accuracy.]

---

## Lessons and Limitations

**Separate location from spread before reading "less diverse".** In every intervention we audited, narrowing was larger and more common than moving. Guidance and distillation removed alternatives far more than they changed the typical output. An evaluator who reads a lower diversity score as "the model now prefers a different look" will usually be wrong. Diversity metrics remain useful, but they should be accompanied by the two components.

**Never read a pooled shift without its per-subject structure.** Almost half of the pooled "no difference" comparisons concealed subjects moving strongly in opposite directions. A pooled table is a summary of these structures, not a substitute for them, and a visual audit should make the per-subject view the default rather than a drill-down.

**Validate measurements per configuration set, and read differences with their size.** Two-thirds of the candidate aspects did not survive human validation. More subtly, aspects that people confirmed on varied models did not hold among similar models, because the differences were small. Agreement between people and CLIP rose with the size of the difference. Measurement validity is therefore a property of an aspect *and* a configuration set, and small differences on a proxy axis should be read with care even when the axis is validated.

**Keep a route from every number to the images.** Two encoder failures and one validity failure were found by looking at images, not by statistics. Linking every mark to its images costs little and is the only general safeguard against a confident wrong measurement.

**Request prompts are not calibration poles.** Asking a model for a pole changes more than the pole, sometimes the subject itself. A data-derived scale with stated margins is more honest than an anchored scale whose anchors are themselves defaults.

**Limitations.**
- CLIP aspects are proxies. Only five of fifteen candidates survived, and lighting and viewpoint are not among them; a second encoder [18] is used as a sensitivity check [result].
- The scale is derived from the 12 configurations themselves and is not calibrated to perceptual units.
- On the later, more homogeneous configurations, only three aspects are validated.
- Thirty-two seeds and 24 subjects describe these samples: appearances rarer than about 5% can be missed, and other prompt sets may show other defaults.
- Configurations are compared at recommended settings, so family and scale are not causal factors.
- We deliberately excluded demographic attributes, which require a different validation design.
- The expert evaluation is small and drawn from the authors' professional network.

---

## Conclusion

Text-to-image models decide what prompts leave open, and the people who build and evaluate them change those decisions with every setting they touch. We showed that a diversity score is not enough to audit such changes. It merges displacement with concentration, it hides opposite changes across subjects, and it cannot reveal when its own measurements are wrong. Our visual audit method addresses all three on human-validated, per-configuration-set axes with pre-registered margins and a route from every number to the images.

Applied to 12 open configurations, it shows three things:
- guidance and distillation mainly concentrate appearance, and displace only saturation;
- most open models share their defaults, apart from two strong signatures;
- pooled comparisons are unreliable for almost half of all configuration pairs.

We hope the method and its lessons help make default shifts something that is checked before release rather than discovered afterward.

---

## Acknowledgments
[Annotators; expert participants; funding.]

## References
*Identifiers verified 2026-10-11 (see `docs/OUTLINE.md`); author lists to be completed from the verified records.*

1. The Vendi Score: A Diversity Evaluation Metric for Machine Learning. arXiv:2210.02410.
2. Classifier-Free Diffusion Guidance. arXiv:2207.12598.
3. DIMCIM. arXiv:2506.05108.
4. GRADE: Quantifying Sample Diversity in Text-to-Image Models. arXiv:2410.22592.
5. Attribute-conditional diversity benchmark for text-to-image models. arXiv:2511.10547.
6. DefaultShift. arXiv:2608.21784.
7. An Exploration of Default Images in Text-to-Image Generation. arXiv:2505.09166.
8. Stage-wise dynamics of classifier-free guidance. arXiv:2509.22007 (ICLR 2026).
9. Adversarial Diffusion Distillation. arXiv:2311.17042.
10. Describing Differences in Image Sets with Natural Language (VisDiff). arXiv:2312.02974 (CVPR 2024).
11. Discovering Divergent Representations between Text-to-Image Models (CompCon). arXiv:2509.08940 (ICCV 2025).
12. ViBEx. arXiv:2504.19703.
13. Varif.ai. DOI 10.1145/3715336.3735847.
14. CUPID. DOI 10.1111/cgf.15086.
15. M. Gleicher, Considerations for Visualizing Comparison. IEEE TVCG, DOI 10.1109/TVCG.2017.2744199.
16. Qwen-Image Technical Report. arXiv:2508.02324.
17. Learning Transferable Visual Models From Natural Language Supervision (CLIP). arXiv:2103.00020.
18. SigLIP 2. arXiv:2502.14786.

*(18 of 20 slots used; two remain for the closed-model sidebar or reviewer requests.)*

## Figures (plan)
| # | Content | Section |
|---|---|---|
| 1 (teaser) | Paired-seed trajectories, klein-base 4B guidance 1 → 4, one subject: medium converges in place; saturation leans and converges | Introduction / Q1 |
| 2 | Method pipeline: aspects → human validation per configuration set → fixed scale → shift and spread with margins → audit views | Audit method |
| 3 | Interface overview, T1–T3 marked | System |
| 4 | Q1: per-subject shift × spread ratio, both families, margins and pooled intervals | Q1 |
| 5 | SDXL → Turbo saturation: scatter straddling the pooled diamond, matrix sorted by shift, image strips | Q2 |
| 6 | Style axis reversal traced to images | Measurement failures |
| Sidebar | Three toy configurations: equal diversity, different stories | Sidebar 1 |

## Author biographies
[Name, affiliation, research interests, degree, contact; about 60 words each.]
