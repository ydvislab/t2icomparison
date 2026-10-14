# Visual Auditing of Appearance Defaults in Text-to-Image Models

*Paper draft, revised 2026-10-14 to follow the argument of the paper, with all frozen analyses (Q1, Q2, Q3) and both human-check rounds. [Brackets] mark parts that are not final: the expert evaluation and the closed models. Section budgets follow `OUTLINE.md`.*

---

## Abstract (≈140 words; limit 150)
When a prompt leaves framing, palette or medium unspecified, a text-to-image model decides them, and it decides them the same way again and again. These **appearance defaults** change whenever developers raise guidance, distil a model or switch checkpoints. Yet evaluation reports only how diverse the outputs are. A diversity score cannot tell two things apart: outputs that now settle somewhere else (**displacement**) and outputs that settle more tightly in the same place (**concentration**). Nor can it tell whether a pooled conclusion holds for every subject. We present a visual audit method with four parts. It places many declared model configurations on human-validated appearance axes. It separates displacement from concentration under pre-registered margins. It shows the per-subject structure. It traces every reading to the images. We audit 12 open configurations on 24 everyday subjects. Guidance and distillation mainly concentrate appearance and displace only saturation. 61 of 140 pooled comparisons hide opposite shifts across subjects. [Five experts …]

---

## 1. Introduction (≈900 words)

### 1.1 Models decide what the prompt leaves open
A prompt such as "a kitchen" names a subject. It says nothing about medium, palette, framing, tone or background. The model fills these in, and modern models fill them in **almost the same way every time**. In our pilot, we measured the diversity (Vendi score) of 16 images of one minimal prompt:
- across models, it fell from 7.45 (Stable Diffusion 1.5) to 3.47 (SDXL-Turbo) and 2.79 (FLUX.2 klein);
- within one model, raising classifier-free guidance from 1 to 4 lowered it from 5.95 to 2.32.

We call these unrequested, repeated decisions **appearance defaults**.

### 1.2 Defaults change with every engineering decision
Defaults are not a fixed property of a model. Developers and evaluators change them constantly, usually as a side effect of other goals:
- they raise guidance for better prompt adherence;
- they distil a model to make it faster;
- they move to a larger checkpoint or a new model family.

Each change shifts the look that every downstream user receives by default. These shifts matter to three groups:
- developers need to see the side effects before release;
- evaluators need to know *what* changed and *whether* it is real, not only by how much;
- for society, homogenised defaults narrow the range of generated images, and default shifts can silently change how subjects are depicted.

### 1.3 Why a score is not enough
Current evaluation reports quality, prompt alignment and a diversity score. Closer work audits attributes of distilled replacements, describes differences between image sets in words, or lets a user explore one model's outputs (Section 2). For an evaluator who compares configurations, three questions remain open.
1. **Displacement or concentration?** "Less diverse" can mean two things: outputs moved to a different look, or they collapsed onto the look they already had. The consequences and remedies differ, but a diversity score merges them.
2. **Pooled or per subject?** A change averaged over prompts can hide opposite changes on different subjects. In our audit this is not rare: it happens in almost half of the comparisons.
3. **Is the measurement right?** Appearance scores come from automatic encoders. Without a route back to the images, a wrong measurement looks exactly like a finding. In our study, a wrong measurement occurred more than once.

### 1.4 Research question and audit tasks
**Main question.** Take a fixed set of minimal prompts and declared model configurations. Which appearance differences are displacements, which are concentrations, and which depend on the subject? And how can an evaluator verify each of them in the images?

The study answers three questions:
- **Q1 (primary, confirmatory).** Does raising guidance displace appearance, concentrate it, or both, and is the answer the same in two model families? This is a controlled intervention: only guidance changes, and the seeds are paired.
- **Q2 (descriptive).** Where do the configurations settle at their recommended settings, how far apart are they, and do the differences hold across subjects?
- **Q3 (pre-specified case).** What does a distillation package change, compared with raising guidance?

The method supports three **audit tasks**:
- **T1:** tell displacement from concentration;
- **T2:** check whether a pooled conclusion holds per subject;
- **T3:** trace a reading to the images, and detect invalid measurements or attributions.

### 1.5 Contributions
1. **An audit method for appearance defaults.** It has four parts:
   - appearance axes, each validated by people separately for each set of configurations;
   - a fixed per-aspect scale;
   - a separation of displacement from concentration, with pre-registered practical margins and hierarchical uncertainty;
   - validity conditions for comparing configurations.
2. **A visual audit system** (D3). A main view of all configurations is linked to per-subject, per-contrast and per-image views, designed for T1–T3.
3. **An audit of 12 open configurations** with bounded findings:
   - guidance concentrates first and displaces only saturation;
   - a distillation package repeats the guidance pattern;
   - most configurations share their defaults, with two strong signatures;
   - pooled comparisons often hide opposite shifts;
   - validation itself depends on the configuration set.
4. **An expert evaluation** with [five] experts on T1–T3 against a strong baseline (score table plus image grid), followed by interviews, and lessons for the visual auditing of generative models.

**Not claimed:**
- a new diversity metric;
- that diversity falls as models improve (shown by DIMCIM and GRADE);
- a causal account of what determines defaults beyond the guidance intervention.

---

## 2. Related work (≈700 words; ≤20 references)
- **Measuring defaults and diversity.**
  - Vendi, DIMCIM and GRADE quantify how much outputs converge, and the attribute-conditional benchmark does so per attribute.
  - An exploration of default images characterises what models produce for empty prompts.
  - **DefaultShift is the closest work.** It audits distilled replacements with closed attribute vocabularies, and observes that distillation acts like increased teacher guidance. It has no visual workflow, and it does not separate where outputs settle from how tightly they settle across a set of configurations. Our Q3 tests that observation directly against a guidance intervention in the same family.
- **Guidance and distillation.** Classifier-free guidance; its stage-wise dynamics, where guidance suppresses weaker modes, predict concentration. Q1 measures whether displacement accompanies it.
- **Comparing image sets.** VisDiff and CompCon describe differences between image sets in words. They discover differences, but they do not say whether a difference is a shift or a narrowing, or whether it holds per subject.
- **Visual analytics of generated images.**
  - ViBEx and Varif.ai explore the output space of one model or one prompt; CUPID visualises distributions of generated images.
  - GROVE does the same for distributions of language-model outputs.
  - None of them compares many declared configurations on validated axes.
- **Visual comparison.** Gleicher's juxtaposition, superposition and explicit encoding inform our design. The contrast views encode differences explicitly, and the image strips juxtapose them.

---

## 3. Audit method (≈1,500 words)

### 3.1 From evaluator decisions to tasks
T1–T3 come from three sources:
- the decisions an evaluator makes when a setting changes;
- the gaps of the closest work (Section 2);
- the failures we met in this project:
  - a pilot reversal: SDXL-Turbo composition shifts +1.31 for "a house" and −1.33 for "a kitchen", pooled +0.07;
  - a reversed CLIP axis;
  - "close-up" requests that produced faces.

### 3.2 Study material and provenance
- **Prompts:** 24 minimal, uncontroversial prompts in six categories (people, animals, objects, indoor, outdoor, activity). Each names only the subject.
- **Configurations:** 12 open configurations, each at its model-card settings:
  - SD 1.5, SDXL, SDXL-Turbo and SD3.5 Large;
  - FLUX.2 dev;
  - klein-base 4B (CFG 4 and CFG 1), klein 4B, klein-base 9B and klein 9B;
  - Qwen-Image-2512 (CFG 4 and CFG 1).
  - [Three closed services are reported descriptively in a sidebar.]
- **Samples:** 32 shared seeds per prompt, giving 9,216 images. Batch size is fixed per configuration, because bf16 outputs depend slightly on it.
- **Provenance:** pipeline, scheduler, text encoder and every setting are read from the weights and declared. As a consequence, klein 4B vs 9B also changes the text encoder, so scale is not tested as a cause.

### 3.3 Appearance aspects and their validation
- **Score.** An image's score on an aspect is its CLIP ViT-L/14 similarity to the right text pole minus its similarity to the left pole, for example "muted desaturated colors" ↔ "vivid saturated colors".
- **Decision rule, fixed before annotation.** An aspect is kept if two conditions hold on pairs with a large CLIP gap:
  - people agree with CLIP's direction on at least 75% of the pairs;
  - they answer "can't tell" on at most 40%.
- **Round 1** (240 same-prompt pairs from the round-1 configurations; 3 independent annotators).
  - 15 candidate aspects were tested.
  - **Five were kept and frozen:** saturation 0.92, medium 0.90, shot 0.90, tone 0.94 and background 0.81.
  - **Dropped:**
    - style: CLIP is systematically reversed and agrees with people on only 0.17 of pairs; it calls klein's polished photographs "stylized";
    - mood: it passed, but it is coupled with tone, so only tone is kept and one change is not counted twice;
    - quality, depth of field, composition, clutter, lighting and viewpoint: unreliable;
    - time of day: too little variation in the images to judge;
    - indoor/outdoor: shown in the tool only.
  - A fourth annotator was excluded before analysis for never using "can't tell". Including them does not change the verdicts.
- **Round 2** (120 pairs drawn only from the six configurations added later; same annotators, same rule).
  - **Shot passes** (0.94, stable when any annotator is left out).
  - Saturation (0.71) and background (0.74) fall just short; medium (0.71) and tone (0.60) fail.
  - A fourth annotator in a sensitivity analysis changes nothing.
  - **Re-annotation (not pre-specified).** Two annotators had forgotten the criteria. After a separate re-briefing on the guide, without access to CLIP's answers, they re-labelled the 120 pairs.
    - Shot still passes (0.96).
    - Saturation (0.77) and medium (0.77) pass narrowly, but not when the third annotator is left out.
    - Background and tone still fail.
    - The re-labels did not move toward CLIP: of the changed answers, 9 now match CLIP and 28 matched it before. The main change is that one annotator began to use "can't tell" (6% → 40%).
    - Both versions are reported (Table 1).
- **Why round 2 is harder.** The later configurations are more alike, so the pairs labelled "large-gap" differ much less in absolute terms. Median gap of the large-gap pairs, in scale units:

  | Aspect | Round 1 | Round 2 |
  |---|---|---|
  | medium | 5.6 | 1.8 |
  | background | 4.7 | 3.1 |
  | saturation | 4.4 | 3.5 |
  | tone | 3.7 | 3.0 |
  | shot | 4.1 | 4.7 |

  - Agreement rises with the gap. For saturation it is 0.42 below 1 unit and 0.83–0.84 at 3 units or more.
- **Consequence.** Validity is reported **per configuration set**:
  - all five aspects are validated on SD 1.5, SDXL, SDXL-Turbo and the klein-base 4B / klein 4B family;
  - on the later six configurations, shot is validated, saturation and medium are borderline, and background and tone are not validated.
- **Negative result: calibration by request prompts.** We tried to anchor each axis with prompts that request each pole, and it failed:
  - "warm light" also produced golden-hour scenes;
  - "wide shot" produced aerial views;
  - Qwen-Image turned "an extreme close-up of a kitchen" into a man's face, which CLIP scored as a perfect close-up.

  We use a fixed per-aspect scale instead (§3.4).

### 3.4 Displacement, concentration and uncertainty
For a change A → B, per subject and aspect:
- **displacement** Δ = (median_B − median_A) / s_aspect. Here s_aspect is the pooled within-cell standard deviation over all 12 configurations, frozen once all were generated. One unit is therefore the typical spread of one configuration on one subject;
- **concentration** = log(IQR_B / IQR_A).

**Practical margins, frozen before any comparison was examined:**
- |Δ| ≥ 0.5 is a displacement;
- an IQR ratio beyond 1.5 or below 1/1.5 is a change in spread;
- "same place" and "same spread" require the 90% interval to lie inside the margin (equivalence).

**Uncertainty:** a hierarchical bootstrap. It resamples subjects within categories and images within cells, and keeps seeds paired within one checkpoint.

**Pre-registration:** the margins, the aspects, the scale and the analysis code were committed before each analysis was run.
- Q1 has 20 primary tests (2 families × 5 aspects × 2 effects), Holm-corrected.
- Q2 and Q3 are pre-specified but were not blind: some contrasts had already been viewed in the tool.

### 3.5 Validity conditions
1. Every setting of every configuration is declared.
2. A contrast that changes several settings is reported as a package and never attributed to one setting.
3. Every pooled result is reported with its per-subject structure.
4. Baselines do not move when configurations are shown or hidden.
5. Measurement validity is stated per configuration set (§3.3).

---

## 4. The visual audit system (≈1,300 words)
The system has one screen: a **main view** and linked **auxiliary views**. All views share the selected aspect, configuration pair, subject and image. Text is minimal, and numbers appear on hover.

| View | Encodes | Task |
|---|---|---|
| **Configuration map** (main) | Each configuration at its typical location (x) and spread (y) on the chosen aspect. Arrows mark the designed contrasts: solid for guidance only, dashed for a package. Hovering a subject shows where each configuration puts it | Q2; entry to T1 |
| **Contrast overview** (alternative main view) | Every designed contrast × aspect as one glyph: an arrow for displacement, a circle against a reference circle for spread, and a count of reversed subjects | T1, T2 at a glance |
| **Subject × configuration matrix** | Colour gives the location of each configuration for each subject. A shift column flags subjects displaced against the pooled direction; one control steps through them, another sorts by shift | T2 |
| **Contrast scatters** (one per aspect) | One dot per subject at (Δ, log IQR ratio), with the frozen margins as bands, the pooled estimate with its interval, and a warning when several settings differ | T1, T2, T3 |
| **Paired-seed trajectories** | Each image of A joined to the image of B with the same seed. Displacement appears as curves leaning one way, concentration as curves converging; images are matched by rank when A and B do not share starting noise | T1 |
| **Distributions** | Densities of A and B, with every image as a tick | T1 |
| **Appearance map** | All images of one subject from every configuration on a shared t-SNE of CLIP image embeddings, with A and B as density contours. It shows defaults outside the five aspects, such as the same face or composition every time | T3, beyond the axes |
| **Image strips** | All images sorted along the aspect, with the same seed highlighted across configurations | T3 |

**Design rationale** (in `DESIGN_HISTORY.md`):
- established encodings only: distributions, scatter and contours;
- no encoding is duplicated across views;
- every number leads to images.

**Abandoned designs:**
- projection envelopes, which were read as spread;
- pooled baselines, which moved when configurations were hidden;
- card summaries, which hid the per-subject structure.

[Figure 3: interface with T1–T3 marked.]

---

## 5. Audit of 12 configurations (≈1,500 words)

### 5.1 Q1: guidance concentrates first, and displaces only saturation (T1)
*Confirmatory; `results/q1/RESULTS.md`.*

**klein-base 4B, CFG 1 → 4**
- Four aspects concentrate beyond the margin:
  - saturation ×0.51;
  - medium ×0.53;
  - tone ×0.49;
  - background ×0.65.
- Shot narrows below the margin (×0.68).
- **Only saturation is also displaced**, toward vivid colour: +0.65 [+0.43, +0.93].
- Medium, shot and background stay in the same place. Tone's shift toward modern (−0.37) is not significant after Holm correction.
- Per subject, saturation moves toward vivid in 15 of 24 subjects and toward muted in none.

**Qwen-Image-2512, CFG 1 → 4**
- Same directions, smaller effects:
  - saturation concentrated ×0.64;
  - saturation shift toward vivid +0.39, below the margin;
  - tone in the same place;
  - all other aspects inconclusive.
- Two qualifications:
  - Qwen-Image rescales guidance, so CFG 4 is not the same dose in both families;
  - on these configurations, saturation is only borderline in round 2 (and its 9 Qwen-Image pairs agree 0.62–0.65), so the Qwen-Image result is reported as **consistent in direction but measured with lower validated reliability**.

**Answer to Q1:** in the family where the measurement is fully validated, raising guidance mainly concentrates appearance. It displaces only saturation.

[Figure 1 (teaser): the same seeds at CFG 1 and 4 on paired-seed trajectories. Medium tightens in place; saturation moves and tightens.]
[Figure 4: per-subject Δ and spread ratios with intervals and margins, both families.]

### 5.2 Q3: a distillation package repeats the guidance pattern (T1)
*Pre-specified; `results/q3/RESULTS.md`.*

**klein 4B package** (klein-base 4B at CFG 1 → klein 4B; new checkpoint, 50 → 4 steps)
- All five aspects concentrate beyond the margin (×0.41–0.63).
- Only saturation is displaced: +0.95 [+0.67, +1.19], toward vivid.
- This is the guidance pattern of Q1, as strong or stronger:
  - tone narrows ×0.49 in both;
  - saturation, medium and shot narrow more.
- This agrees with DefaultShift's observation that distillation acts like increased guidance. Here the comparison is with a measured guidance intervention in the same family, on validated aspects.
- The package changes the checkpoint and the step count together, so the effect is not attributed to either one.

**klein 9B package**
- It changes defaults much less: shifts are unresolved, and spreads are ×0.77–0.88.

### 5.3 Q2: shared defaults, two signatures, and pooled numbers that mislead (T2)
*Descriptive; 8 configurations at their recommended settings; `results/q2/RESULTS.md`.*

**Most configurations share their defaults.**
- Only 5–8 of 28 configuration pairs per aspect differ beyond the margin.
- Two configurations have strong signatures:
  - **SDXL:** painting-like (medium +3.64), muted (saturation −1.68), busy backgrounds (+1.12) and vintage tone (+0.65). These lie on round-1 configurations and are validated;
  - **Qwen-Image:** closer framing (shot −1.81), validated in round 2. Its vintage tone (+0.71) is not validated on this configuration set.
- Spread: SD 1.5 is the most varied, and FLUX.2 dev and the klein models are the most concentrated.

**Defaults depend on the subject.**
- Nine configuration × aspect combinations are subject-dependent. For example, SDXL's tone is vintage for 13 subjects and modern for 3.

**Pooled comparisons hide opposite shifts.**
- In **61 of 140** pair × aspect comparisons, the pooled difference lies within the margin, yet at least three subjects shift beyond +0.5 and three beyond −0.5.
- Example: SDXL vs Qwen-Image on tone is pooled +0.03, with 9 subjects shifting each way.

**The clearest single case: SDXL → SDXL-Turbo** (a package of checkpoint, scheduler, steps, guidance and resolution)
- Every pooled shift is "same place" or unresolved.
- Yet 4 of 5 aspects hide opposite shifts. For saturation, 9 subjects become more vivid and 6 more muted.
- The system also warns that five settings differ, so nothing here is attributed to distillation.

[Figure 5: the SDXL → Turbo saturation scatter straddling the pooled estimate, with matrix rows and images.]

### 5.4 Measurement failures that only the images exposed (T3)
- **Style axis:** CLIP scored klein's polished photographs as "stylized", which is systematically reversed. Image strips sorted by the axis showed it at once; the human check confirmed it (0.17).
- **"Close-up" faces:** a request for an extreme close-up of a kitchen produced a man's face. CLIP rated it a perfect close-up.
- **Validity that does not transfer:** aspects validated on one configuration set fall short on a more homogeneous set, where gaps are small (§3.3).
- In all three cases a score alone looked like a finding; the route to the images exposed the error.

[Figure 6: one traced failure.]

### 5.5 What the human checks change in the claims
| Claim | Configurations | Validated aspects | Status |
|---|---|---|---|
| Q1, klein-base 4B | round 1 | all five | stands |
| Q1, Qwen-Image | round 2 | shot; saturation and medium borderline | qualified: same direction, lower validated reliability |
| Q3, klein 4B package | round 1 | all five | stands |
| Q2, SDXL signature | round 1 | all five | stands |
| Q2, Qwen-Image signature | round 2 | shot | shot stands; tone qualified |
| Q2, hidden opposite shifts (61/140) | mixed | — | stands as a statement about the scores; per-aspect counts on round-2 configurations qualified |

These statuses hold under both the original and the re-annotated round 2.

---

## 6. Expert evaluation (≈700 words)
*[Planned; protocol in `EXPERT_STUDY.md`; ethics approval obtained; five experts recruited.]*
- **Participants:** five researchers who train, evaluate or select text-to-image models.
- **Design:** within subjects. Each task (T1–T3) is solved once with the system and once with a baseline, on different cases of the same kind:
  - the baseline is a score table with every number the system uses, plus an unsorted image grid;
  - the condition order is counterbalanced.
- **Cases:**
  - T1: klein-base 4B saturation (moves and tightens) vs medium (tightens in place);
  - T2: SDXL → Turbo saturation, plus one Q2 comparison that hides opposite shifts;
  - T3: the reversed style axis, plus a package contrast read as the effect of one setting.
  - Cases use aspects validated on the configurations involved.
- **Measures:**
  - correctness against answers fixed in advance;
  - whether the answer cites image evidence;
  - confidence;
  - think-aloud remarks;
  - a semi-structured interview.
- **Reporting:** descriptive counts and themes; no statistical claim about speed or accuracy.
- [Results.]

---

## 7. Lessons and limitations (≈600 words)
**Lessons for auditing generative models visually**
1. Separate location from spread before reading "less diverse". In our audit, guidance and distillation narrow far more than they move.
2. Never read a pooled shift without its per-subject structure. Almost half of the pooled "no difference" comparisons were false for many subjects.
3. Every measurement needs a route back to images. Two encoder failures and one validity failure were found that way.
4. Validate per configuration set, and read differences with their magnitude:
   - human validation removed two-thirds of the candidate aspects;
   - an aspect validated on varied models may not hold among similar ones.
5. Request prompts are not clean calibration poles.

**Limitations**
- CLIP proxies: only five aspects survive, and lighting and viewpoint are not among them.
- The scale is computed from the 12 configurations themselves and is not calibrated to perceptual units.
- Validation is weaker on the later, more homogeneous configurations.
- 32 seeds × 24 subjects describe these samples; appearances rarer than about 5% can be missed.
- Configurations are at recommended settings, and family and scale are not causal factors.
- Demographic attributes are out of scope.
- The expert evaluation is small and drawn from the authors' network.

---

## Appendix: state of the work (2026-10-14)
| Item | State |
|---|---|
| Prompts, configurations, provenance | Done |
| Generation and CLIP scoring, 12 configurations (9,216 images) | Done |
| Human check, round 1 | Done; 5 aspects frozen |
| Human check, round 2 | Done: shot passes. Re-annotation: saturation and medium borderline; background and tone fail |
| Calibration pilot | Done; negative result |
| Q1 (confirmatory), Q2 and Q3 (pre-specified) | Done (`results/q1–q3/`) |
| Visual audit system | Done: main view, contrast overview and 6 linked views |
| Expert evaluation | Protocol drafted; 5 experts; ethics approved; baseline page and session sheets to build |
| Remaining | SigLIP 2 check, closed models (owner), figures, writing, submission checks |
