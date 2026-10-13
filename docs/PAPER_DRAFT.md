# Visual Auditing of Appearance Defaults in Text-to-Image Models

*Paper logic draft, 2026-10-13. It is written as the paper will argue; [brackets] mark numbers or results that are not final. Preliminary observations come from 11 of 12 configurations with a provisional scale and are labelled as such. They are not claims until the frozen analysis is run.*

---

## Abstract (draft, ≤150 words)
When a prompt leaves lighting, framing or palette unspecified, a text-to-image model decides them. These **appearance defaults** change whenever developers swap a model or a setting, yet evaluation reports only how diverse the outputs are. A lower diversity score cannot tell whether outputs now settle somewhere else (**displacement**) or settle more tightly in the same place (**concentration**), nor whether the change holds for every subject. We present a visual audit method that places the outputs of many declared model configurations on human-validated appearance axes, separates displacement from concentration under pre-registered margins, and traces every reading back to the images. Auditing 12 open configurations on 24 everyday subjects, we find that raising guidance [mainly concentrates appearance and displaces only saturation and tone, in both model families studied], and that pooled conclusions can hide opposite shifts across subjects. [N] experts used the method to [result].

---

## 1. Introduction

### 1.1 Background: models decide what the prompt leaves open
A prompt such as "a kitchen" names a subject but says nothing about lighting, viewpoint, palette, framing or medium. The model fills in these attributes, and modern models fill them in **the same way almost every time**. In our pilot, the diversity of 16 images of one minimal prompt (Vendi score) fell from 7.45 (Stable Diffusion 1.5) to 3.47 (SDXL-Turbo) to 2.79 (FLUX.2 klein). Within a single model, raising classifier-free guidance from 1 to 4 lowered it from 5.95 to 2.32. We call these unprompted, repeated decisions **appearance defaults**.

Appearance defaults are not fixed properties of a model. Model developers and evaluators change them constantly, often without intending to: they raise guidance to improve prompt adherence, distil a model to make it faster, switch to a larger checkpoint, or adopt a new model family. Each change shifts the defaults that every downstream user receives.

### 1.2 Why it matters
- **For model developers.** A setting change is a design decision with side effects. Distillation and guidance are chosen for speed and fidelity, but they also change which looks users get by default. Developers need to see those side effects before release.
- **For evaluators and auditors.** Benchmarks report quality, prompt alignment and a diversity score. When two configurations differ, the evaluator needs to know **what** differs and **whether the difference is real**, not only by how much.
- **For users and society.** Defaults shape what millions of generated images look like. Homogenized defaults narrow visual culture, and default shifts can silently change how subjects are depicted. Auditing them is a prerequisite for discussing them.

### 1.3 The gap
Existing work measures *how much* outputs converge or *which* attributes differ:
- diversity scores (Vendi; DIMCIM; GRADE);
- attribute-level audits of distilled replacements (DefaultShift);
- automatic descriptions of differences between image sets (VisDiff, CompCon);
- visual exploration of one model's output space (ViBEx, Varif.ai).

Three questions an evaluator faces remain unanswered:
1. **Displacement or concentration?** "Less diverse" can mean that outputs moved to a different look, or that they collapsed onto the look they already had. The two have different consequences and different remedies, but a diversity score merges them.
2. **Pooled or per subject?** A change averaged over prompts can hide opposite changes on different subjects.
3. **Can the measurement be trusted?** Attribute scores come from automatic encoders. Without a route back to the images, a wrong measurement looks exactly like a finding.

### 1.4 Research questions
**Main question.** For a fixed set of minimal prompts and declared model configurations, which differences in appearance are displacements, which are concentrations, and which change from subject to subject, and how can an evaluator verify each in the images?

- **Q1 (primary).** Does raising guidance displace appearance, concentrate it, or both, and is the answer the same in two model families? This is a within-model intervention: only guidance changes, and seeds are paired.
- **Q2.** Where do 12 configurations settle at their recommended settings, how far apart are they, and do the differences persist across subjects? This question is descriptive and makes no causal attribution to family or scale.
- **Q3 (case).** What does a distillation package change, compared with raising guidance?

The visual method supports three **audit tasks**:
- **T1:** tell displacement from concentration;
- **T2:** check whether a pooled conclusion holds per subject;
- **T3:** trace a reading to the images and detect invalid measurements or attributions.

### 1.5 Approach
We generate repeated outputs of 12 open configurations for 24 minimal prompts with shared seeds, and score them on appearance aspects defined by pairs of text poles. Only aspects that human annotators confirm are kept. For any change from configuration A to configuration B, we measure, per subject and aspect:
- **displacement** as the shift of the median, in a fixed per-aspect scale;
- **concentration** as the ratio of interquartile ranges.

Practical margins and the primary tests were frozen before any comparison was examined. A visual audit system with a main view of all configurations and linked auxiliary views supports T1–T3 and leads every reading back to the images.

### 1.6 Contributions
1. **An audit method for appearance defaults:**
   - human-validated appearance axes;
   - a separation of displacement from concentration, with pre-registered practical margins and hierarchical uncertainty;
   - validity conditions for comparing configurations: declared settings, no single-factor attribution when several settings change, per-subject reporting, and fixed baselines.
2. **A visual audit system.** A configuration map of all configurations, linked to a subject × configuration matrix, contrast views, per-subject distributions and sorted image evidence, designed for tasks T1–T3.
3. **An audit of 12 open configurations** with bounded findings:
   - the guidance intervention in two families;
   - where configurations settle and whether differences hold across subjects;
   - a distillation case;
   - measurement failures that only the images exposed.
4. **An expert evaluation** with [N] experts on the three tasks, against a baseline of box plots or a score table with an image grid, and lessons for the visual auditing of generative models.

**Not claimed:** a new diversity metric; that diversity falls as models improve (shown by DIMCIM and GRADE); a causal account of what determines defaults.

---

## 2. Related work (to be written; ≤20 references in total)
- **Measuring defaults and diversity:** Vendi, DIMCIM, GRADE, the attribute-conditional diversity benchmark. DefaultShift is the closest work: it audits distilled replacements with closed attribute vocabularies and has no visual workflow.
- **Guidance and distillation:** CFG and stage-wise CFG dynamics (theory: guidance suppresses weaker modes); distillation methods.
- **Comparing image sets:** VisDiff, CompCon (discovery of differences, not calibrated location and concentration).
- **Visual analytics of generated images:** ViBEx, Varif.ai, CUPID; GROVE for distributions of language-model outputs.
- **Visual comparison:** Gleicher (juxtaposition, superposition, explicit encoding).

---

## 3. Method (done)

### 3.1 Study design
- **Prompts:** 24 minimal, uncontroversial prompts in 6 categories (people, animals, objects, indoor, outdoor, activity) that name only the subject, plus 6 control prompts that request one attribute.
- **Configurations:** 12 open configurations, each at its model-card settings:
  - SD 1.5, SDXL, SDXL-Turbo and SD3.5 Large;
  - FLUX.2 dev, klein-base 4B (CFG 4 and CFG 1), klein 4B, klein-base 9B and klein 9B;
  - Qwen-Image-2512 (CFG 4 and CFG 1).
  - Three closed services are reported descriptively in a sidebar.
- **Samples:** 32 seeds per prompt, shared by all configurations, giving about 10,400 images. Each configuration uses a fixed batch size, because bf16 outputs vary slightly with batch size.
- **Provenance:** pipeline, scheduler, text encoder and every setting are read from the weights and declared. One consequence: klein 4B vs 9B also changes the text encoder, so scale is not tested as a cause.

### 3.2 Measurement and its validation
- **Aspects:** an image's score on an aspect is its CLIP similarity to the right pole minus its similarity to the left pole (e.g. "muted desaturated colors" ↔ "vivid saturated colors").
- **Human check:** 240 same-prompt image pairs drawn from the study images, judged independently by 3 annotators. The decision rule was fixed in advance: an aspect is kept if people agree with CLIP's direction on at least 75% of clear pairs and say "can't tell" on at most 40%. A fourth annotator was excluded for never using "can't tell"; including them does not change the stable verdicts.
- **Kept (frozen):**

  | Aspect | Agreement with CLIP |
  |---|---|
  | saturation | 0.92 |
  | medium | 0.90 |
  | shot | 0.90 |
  | tone | 0.94 |
  | background | 0.81 |

- **Dropped:**
  - style: CLIP is systematically reversed and agrees with people on only 0.17 of pairs;
  - quality, depth of field, composition, lighting and viewpoint: unreliable;
  - time of day and indoor/outdoor: too little variation.
- **Negative result: calibration by explicit requests.** We tried to calibrate each axis with prompts that request each pole. It failed:
  - requesting warm light also produced golden-hour scenes;
  - requesting a wide shot produced aerial views;
  - Qwen-Image turned "an extreme close-up of a kitchen" into a man's face, which CLIP scored as a perfect close-up.

  We report this as a negative result and use a fixed per-aspect scale instead.

### 3.3 Displacement, concentration and validity
For a change A → B, per subject and aspect:
- Δ = (median_B − median_A) / s_aspect, where s_aspect is the pooled within-cell standard deviation over all 12 configurations, frozen once all are generated;
- the concentration effect is log(IQR_B / IQR_A).

**Practical margins (frozen before any comparison was examined):**
- |Δ| ≥ 0.5 counts as a displacement;
- an IQR ratio beyond 1.5 or below 1/1.5 counts as a change in spread;
- "same place" or "same spread" requires the 90% interval to lie inside the margin (equivalence).

**Uncertainty:** a hierarchical bootstrap that resamples subjects within categories and images within groups, keeping seeds paired within a checkpoint.

**Primary tests:** 2 families × 5 aspects × 2 effects = 20, Holm-corrected.

**Validity conditions:**
- every setting is declared;
- a package change (several settings) is reported as a package;
- results are reported per subject;
- baselines do not move when configurations are shown or hidden.

---

## 4. The visual audit system (done; additions planned)
One screen with a **main view** and linked **auxiliary views**:

| View | Encodes | Task |
|---|---|---|
| **Configuration map** (main) | Each configuration at its typical location (x) and spread (y) on the chosen aspect. Arrows mark the designed contrasts: solid for guidance only, dashed for a package change. Hovering a subject shows where each configuration puts it | Q2; entry point to T1 |
| **Subject × configuration matrix** | Colour = location of each configuration for each subject; a row that changes colour is a subject-dependent default | T2 |
| **Contrast scatters** (one per aspect) | One dot per subject at (Δ, log IQR ratio); the frozen margins as bands; the pooled estimate with its interval; a warning when several settings differ | T1, T2, T3 |
| **Per-subject distributions** | Smooth densities of A and B with every image as a tick | T1 |
| **Image strips** | All images sorted along the aspect; the same seed is highlighted across configurations | T3 |

All views share the selected aspect, configuration pair, subject and image. Text is minimal and numbers appear on hover.

**Analysis views so that analysts discover patterns instead of only inspecting them:**
1. **Paired-seed trajectories** (done): each image of A is joined to the image of B made from the same seed, so displacement appears as curves leaning one way and concentration as curves converging. When A and B do not share the starting noise, images are matched by rank instead.
2. **Reversal detection** (done): a per-subject shift column in the matrix flags subjects displaced against the pooled direction, with a counter that steps through them and an ordering by shift.
3. **Contrast overview** (done): every designed contrast × aspect as one glyph (an arrow for displacement, a circle against a reference circle for spread, a count of reversed subjects). It shows at once that guidance and the klein distillation package move saturation and tone the same way, while SDXL → Turbo has no pooled shift but many reversed subjects.
4. **Appearance map** (done): all images of one subject from every configuration on a shared t-SNE of CLIP image embeddings, with A and B as density contours, for defaults outside the five aspects (e.g. the same face or composition every time).

---

## 5. Case studies (planned; preliminary observations from 11 of 12 configurations, provisional scale)

**Case 1: Guidance concentrates first, and displaces only some aspects (Q1, Q3; T1).**
- *Preliminary:* raising guidance from 1 to 4 narrows the spread on all five aspects:
  - klein-base 4B: IQR ratio ×0.49–0.68;
  - Qwen-Image: IQR ratio ×0.64–0.81.
- It displaces outputs consistently on only two aspects:
  - toward more saturated colour (15 of 24 subjects for klein, 10 for Qwen, none in the opposite direction);
  - toward a more modern, less vintage tone (9 subjects in each family).
- The effect is weaker for Qwen-Image, whose pipeline rescales the guided prediction, so CFG 4 is not the same dose in both families.
- klein's distilled model resembles strong guidance (saturation displaced in 18 subjects; spread ×0.41), in line with DefaultShift's observation that distilled models behave like increased teacher guidance.
- *Workflow:* the guidance arrows on the map → contrast scatters → paired seeds → image strips.

**Case 2: A pooled "no change" hides opposite shifts (SDXL → SDXL-Turbo; T2, T3).**
- *Preliminary:* the pooled saturation shift is only +0.17, but 10 subjects become more vivid and 7 more muted. Background is split the same way (7 busier, 7 plainer).
- The system also warns that four declared settings differ (weights, resolution, steps, guidance), so none of these differences can be attributed to distillation alone.
- *Workflow:* the dashed arrow → the scatter whose dots straddle the pooled diamond → matrix rows that reveal which subjects go which way → images.

**Case 3 (optional or sidebar): model signatures (Q2).**
- *Preliminary:*
  - Qwen-Image frames subjects closer (shot −1.6 / −1.4);
  - SDXL leans toward painting (medium +3.5), muted colour (saturation −1.6) and busy backgrounds;
  - SDXL's tone default is strongly subject-dependent.
- *Measurement failures caught through the images* (CLIP's reversed style axis; the "close-up" faces) illustrate T3.

---

## 6. Expert evaluation (planned, Oct 28 – Nov 3)
- [3–5] researchers in generative modelling or evaluation, about 40 minutes each.
- Three tasks matching T1–T3, solved with the system and with a baseline (box plots, or a score table with an image grid).
- We report what they found, how their judgements changed, and where the system was hard to use. No claim of statistically established speed or accuracy is made.

## 7. Lessons and limitations (outline)
- **Lessons:**
  - separate location from spread before reading "less diverse";
  - never read a pooled shift without its per-subject structure;
  - every measurement needs a route back to images;
  - human validation removed two-thirds of the candidate aspects;
  - explicit request prompts are not clean calibration poles.
- **Limitations:**
  - CLIP proxies (five aspects survive, and lighting and viewpoint are not among them);
  - 32 seeds × 24 subjects describe these samples, and appearances rarer than about 5% can be missed;
  - the configurations are at recommended settings, and family and scale are not causal factors;
  - demographic attributes are out of scope.

---

## Appendix: what has been completed (2026-10-13)
| Item | State |
|---|---|
| Prompt set, configuration design, provenance | Done |
| Generation | 11 of 12 configurations done (about 9,500 images); FLUX.2 dev running |
| CLIP scoring | Done for the 11 configurations |
| Human check, round 1 | Done; 5 aspects frozen |
| Calibration pilot | Done; negative result recorded |
| Frozen margins, scale definition, primary tests | Done (git commits e5c5883, 0dc66d1) |
| Visual audit system | Main view plus 4 auxiliary views (D3); analysis additions planned |
| Paper brief for co-authors | `docs/PAPER_BRIEF.md` |
| Remaining | Final scale and primary analysis; system additions; round 2 human check; closed models; expert sessions; writing |
