# LLM study: pre-registration (Q4, Q5, Q6)

Written and committed on 2026-10-15, **before any rewritten image was generated or scored and before any VLM output was collected**. The frozen scale, margins, aspects and bootstrap of Q1 apply unchanged (`../model_study/analysis/frozen_*.json`, `q1_primary.py`). Any later change is reported as a deviation.

The study frames language in three roles:
- language as **intervention**: an LLM rewrites the prompt (Q4);
- language as **explanation**: a VLM describes how two image sets differ (Q5);
- language as **measurement**: a VLM proposes new appearance axes (Q6).

The visual audit checks each role against the images.

## Q4: does LLM prompt rewriting displace or concentrate appearance defaults?

**Rewriters** (`rewrite.py`). There is one rewrite per subject and seed, because a deployed rewriter rewrites every request independently.
- **mistral:** FLUX.2's official prompt upsampler as shipped in diffusers 0.41: the FLUX.2 dev text encoder Mistral-Small-3.2-24B, the official T2I system message and temperature 0.15.
- **qwen:** Qwen3.5-4B with the same system message and temperature.

**Generators** (`gen_rewritten.py`): settings, seeds, job names and batch size are identical to the study images, so each rewritten image is paired with the original image from the same starting noise.

**Primary contrasts.** Original minimal prompt → mistral rewrite, in two generators:
- **P1:** klein 4B (G08);
- **P2:** FLUX.2 dev (G05), the generator the official upsampler belongs to.

**Tests.** 2 contrasts × 5 aspects × 2 effects = 20 tests. Effects, bootstrap (10,000 replicates, seed 20261015; seeds paired, since each contrast shares the checkpoint), intervals, p values, Holm correction and verdict rules are exactly those of `q1_primary.py`. Both "concentrated" and "widened" are possible spread verdicts.

**Descriptive** (no p values; per-subject reversal counts with the Q3 rule):
- **D1:** klein 4B, original → qwen rewrite;
- **D2:** klein 4B, mistral → qwen rewrite: does the rewriting LLM matter?
- **D3:** klein 4B, mistral_fixed (the k = 0 rewrite reused for all seeds) vs. original and vs. mistral: how much of any change in spread comes from varying the text across seeds?

**Text side** (exploratory):
- **Text score:** each rewrite gets a CLIP text-encoder score on every aspect (similarity to the right pole minus similarity to the left pole). Its shift relative to the original prompt's text score is compared with the image-side shift (Spearman correlation over subjects).
- **Word families:** the share of rewrites containing words from pre-specified families, counted case-insensitively on word stems:

  | Family | Words |
  |---|---|
  | lighting | light, lit, glow, sunlight, shadow |
  | time of day | morning, afternoon, evening, sunset, golden hour, dusk, dawn, night |
  | cinematic / photographic | cinematic, photograph, photorealistic, realistic, lens, depth of field, bokeh, mm |
  | colour | warm, vibrant, muted, saturated, pastel, color/colour |
  | background | background, surrounded, scene, environment |
  | style | painting, illustration, watercolor, render, style |

**Validity.** Rewritten images are a new configuration set, so they get their own human check (round 3, below). Claims on aspects that fail there are flagged, as in round 2.

## Q5: can a VLM describe these differences correctly?

**Describers:**
- Qwen3.5-4B, thinking off;
- Mistral-Small-3.2-24B, the FLUX.2 dev text encoder, which is a VLM.

Decoding is greedy.

**Contrasts** (A → B):
1. klein-base 4B, CFG 1 → 4;
2. Qwen-Image, CFG 1 → 4;
3. klein 4B package (klein-base 4B CFG 1 → klein 4B);
4. SDXL → SDXL-Turbo;
5. klein 4B, original → mistral rewrite;
6. FLUX.2 dev, original → mistral rewrite.

**Input.** Per subject, two grid images, each 4 × 2 of 256 px tiles: seeds k = 0–7 of A, then of B. This is the per-subject level. At the pooled level, two 4 × 4 grids of 16 images: one image per randomly drawn subject (without replacement) and a random seed, drawn 5 times with seed 20261015.

**Questions** (one conversation per grid pair):
- **Free text:** "List up to five ways in which the images of set B differ in appearance from the images of set A."
- **Constrained choice, per frozen aspect,** scored by letter logits:
  - shift: "B is more <right pole> / B is more <left pole> / no clear difference";
  - variety: "B is more varied / B is less varied / about equally varied".

**Ground truth** (from all 32 seeds, frozen scale and margins):
- **Per-subject shift:** "right" or "left" if |Δ| ≥ 0.5 and the per-subject 90% seed-bootstrap interval (2,000 replicates) excludes 0; "none" if that interval lies inside ±0.5; otherwise ambiguous and not scored.
- **Per-subject variety:** "less" or "more" if the IQR ratio is beyond 1/1.5 or 1.5 and its interval excludes 1; "similar" if the interval lies inside [1/1.5, 1.5]; otherwise not scored.
- **Pooled:** the pooled verdicts of Q1, Q3 and Q4 (displaced / same place; concentrated / widened / same spread). A pooled answer is additionally marked **misleading per subject** when the contrast hides opposite shifts on that aspect (Q3 rule).

Only aspects validated on the configuration set involved are scored.

**Measures:**
- accuracy of shift answers;
- accuracy of variety answers;
- **concentration-as-displacement rate:** the share of subject × aspect cases with truth "none + less varied" that the VLM answers with a shift;
- **missed concentration:** truth "less varied", VLM answers "about equally varied";
- **pooled overreach:** pooled shift claims on aspects marked misleading per subject.

**Free text.** Each statement is coded to {one of the 5 aspects + direction, variety, other}:
- the coder is Qwen3.5-4B with constrained choice;
- the owner checks a random 20% sample, and coding accuracy is reported;
- coded statements are scored like the constrained answers.

## Q6: VLM-proposed appearance axes
1. **Proposal.** For each Q5 contrast, the Mistral describer receives the pooled grids and is asked: "Propose up to five pairs of opposite short descriptions (left pole, right pole) of appearance properties that distinguish these two sets."
2. **Candidates.** Proposals are merged by the executor when they name the same property, without looking at any CLIP score. Up to 6 properties qualify: those proposed for at least two contrasts and not already among the 15 round-1 candidates. Properties proposed more often are taken first; ties are broken by first appearance.
3. **Scoring and validation.** CLIP scores the candidates with the same scoring script. They are validated in round 3 with the frozen rule. A candidate that passes is reported as a VLM-proposed, human-validated aspect, and the audit tool can show it. It is not added to the Q1–Q4 primary tests.

## Human check, round 3
- **Q4 images:**
  - 12 pairs per aspect from the rewritten images (klein 4B mistral and FLUX.2 dev mistral): 8 with a large CLIP gap and 4 with a small gap;
  - 60 pairs in all.
- **Q6 candidates:**
  - 16 pairs per candidate, drawn from all study images: 12 with a large gap and 4 with a small gap.
- **Procedure:** same page, guide, annotators and decision rule as before (≥ 0.75 agreement and ≤ 0.40 "can't tell" on large-gap pairs). Pairs are drawn by a sampler committed before the package is built.

## Operational details (added 2026-10-15, before any Q5 output and before any rewritten image was scored)
- **Q5:** questions are separate single-turn prompts; option order is randomized per query; grids and seeds are as written in the header of `vlm_describe.py`.
  - A smoke test (2 queries, Qwen3.5-4B, guidance contrast, first subject) only checked that the script runs. Its output was deleted unread.
- **Q4 analysis:** `q4_analysis.py`, which reuses `q1_primary.py` unchanged.
- **Text side:** `text_side.py`. Its text-side unit is the across-subject SD of the original prompts' text scores, because the image scale does not apply to text.

## Deviation 1 (2026-10-15, before any image was generated from a rewrite)
- **Problem:** diffusers' `Flux2Pipeline.upsample_prompt` pads every input on the right to 2,048 tokens. With the installed transformers 5.19, this produced degenerate rewrites: the system message was echoed back and words were broken.
- **Fix:** `rewrite.py` now calls the same model with the same system message, message format, temperature and token limit, without padding. The 32 rewrites of a subject are 32 samples of one unpadded input.
- **Check:** two subjects were inspected and gave fluent rewrites.
- **Record:** the degenerate file is kept as `rewrites_mistral_diffusers_padded.csv`. No image was generated from it.

## Deviation 2 (2026-10-16, after the first Q5 answers were scored)
- **Why:** both VLMs almost never answered "no clear difference". To test whether the question format itself invites a difference, we add two **null contrasts** that were not pre-registered: klein 4B against itself and SDXL against itself, with B using seeds shifted by 16 (k + 16 mod 32) and everything else as in Q5.
- **Truth:** "no difference" and "about equally varied" by construction.
- **Measure:** the share of null answers that report a shift or a change in variety (false-difference rate).
- **Status:** reported as an added control, outside the pre-registered measures.

## Deviation 3 (2026-10-23, after the external review of 2026-10-22; exploratory)
- **Reason:** the reviewer noted two things.
  - The VLMs saw 8 (pooled: 16) images per set, while the audit's truth uses all 32 seeds, so some "wrong" answers may describe real sample fluctuation.
  - Answer stability across grids was not measured.
- **Two exploratory analyses are added, specified before running:**
  1. **Second draw.** Both VLMs answer the same constrained questions for the six Q5 contrasts on a disjoint draw of grids:
     - subject level: seeds k = 8–15;
     - pooled: five new draws with numpy seeds 20261115 + d;
     - script: `vlm_describe.py --draw2`, written to `q5/<vlm>_draw2/`.
     - **Measure:** agreement between the two draws per contrast, level and question (share of identical answers).
     - **Reference:** the agreement expected if each VLM answered at random with its own answer frequencies.
  2. **Truth from the shown images.** Constrained answers of the first draw are also scored against a truth computed from the 8 seeds the VLM saw, k = 0–7, with the same margins and a per-subject bootstrap over those 8 seeds. Per subject only, because pooled grids mix subjects.
- **Reporting:** both are reported as exploratory and change none of the pre-registered measures.
