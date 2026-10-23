# Second-encoder sensitivity check: specification (2026-10-23, before any SigLIP 2 score was computed)

**Question.** Do the paper's verdicts depend on CLIP ViT-L/14? The same pipeline is rerun with a second, independently trained image–text encoder. Planned in `OUTLINE.md` (reference 18) and requested by the 2026-10-22 review (action 4).

## Encoder and scores
- **Encoder:** `google/siglip2-so400m-patch14-384` (SigLIP 2; arXiv 2502.14786), fp16.
- **Scores:** the same text poles as the frozen aspects. Score = cos(image, right) − cos(image, left) (`aspects/score_siglip.py`).
- **Images:** all 9,216 study images and the 3,072 rewritten-prompt images.
- **Scale:** the frozen definition (`frozen_margins.json`: square root of the mean within-cell variance over the 12 open configurations, prompt-implied aspects excluded), computed once from the SigLIP scores. It is not compared with the CLIP scale.
- **Unchanged:** margins (0.5; ×1.5), bootstrap (10,000 replicates), Holm families, verdict rules.

## Analyses
1. **Human agreement.** On every human-check pair of rounds 1 (study images, 3 annotators), 2 (re-labels) and 3 (part a), SigLIP's direction replaces CLIP's. For the five frozen aspects, the agreement with people and "can't tell" on large-gap pairs are computed exactly as in `annotation/analyze.py`. Large-gap pairs were selected by CLIP, so this favours CLIP; the comparison is reported as such.
2. **Verdicts.** The primary tests are rerun with SigLIP scores, with their own Holm correction as in the original analyses:
   - Q1: 20 tests;
   - Q3 primary: 10 tests;
   - Q4 primary: 20 tests.

   For every test the CLIP verdict and the SigLIP verdict are tabulated, with the estimates and intervals.
3. **Per-subject agreement.** For each of these contrasts and aspects, the Spearman correlation between CLIP and SigLIP per-subject Δ, and between their log IQR ratios.

## Reading rule (fixed now)
- **Robust:** a headline verdict whose SigLIP verdict has the same category (displaced / concentrated / same place / same spread / inconclusive / below margin) or a stronger version of it in the same direction.
- **Encoder-dependent:** otherwise, and reported as such in the paper.
- **Headline verdicts:**
  - Q1 klein saturation (displaced, concentrated) and klein medium, tone and background (concentrated);
  - Q3 all five concentrated and saturation displaced;
  - Q4: no widening on validated aspects.

Script: `encoder_sensitivity.py`; results: `results/encoder_check/`.
