# Human check, round 3: results (2026-10-19)

**Design:** `experiments/llm_study/PREREG.md` (round 3) and `annotation/make_pairs_round3.py`, committed before the package was built. 156 pairs:
- **Part a (Q4), 60 pairs:** the five frozen aspects on the rewritten-prompt images (klein 4B and FLUX.2 dev with FLUX.2 rewrites). 12 pairs per aspect: 8 with a large CLIP gap, 4 with a small gap.
- **Part b (Q6), 96 pairs:** the six VLM-proposed candidate axes (`q6_candidates.json`) on the study images. 16 pairs per candidate: 12 large, 4 small.

**Annotators and rule:**
- The same three annotators as in rounds 1 and 2 (A, B, C), working independently.
- Unchanged decision rule: on large-gap pairs, agreement with CLIP ≥ 0.75 and "can't tell" ≤ 0.40.
- "Stable" means the verdict holds when any one annotator is left out.

**Files:** `aspect_check.csv`, `pair_answers.csv` (from `annotation/analyze.py`).

## Part a: the five aspects on rewritten-prompt images
| Aspect | Agreement [95% CI] | Can't tell | κ | Verdict |
|---|---|---|---|---|
| saturation | 0.90 [0.71, 0.97] | 0.13 | 0.45 | **pass, stable** |
| tone | 0.89 [0.68, 0.97] | 0.21 | 0.47 | **pass, stable** |
| medium | 0.77 [0.52, 0.90] | 0.29 | 0.26 | pass, not stable (fails without B: can't tell 0.44) |
| shot | 0.63 [0.38, 0.81] | 0.33 | 0.35 | fail |
| background | **0.38** [0.18, 0.61] | 0.33 | 0.31 | **fail, stable** (below 0.5: CLIP's background reading is often the opposite of people's on these images) |

## Part b: VLM-proposed axes (Q6)
| Candidate (left ↔ right) | Agreement [95% CI] | Can't tell | κ | Verdict |
|---|---|---|---|---|
| lighting: flat ↔ dramatic | 0.70 [0.51, 0.84] | 0.25 | 0.12 | fail (passes only without C) |
| sharpness: soft ↔ crisp | 0.68 [0.49, 0.82] | 0.22 | 0.49 | fail |
| natural ↔ idealized/retouched | 0.68 [0.50, 0.81] | 0.14 | 0.27 | fail |
| contrast: flat ↔ dramatic tones | 0.56 [0.39, 0.71] | 0.11 | 0.24 | fail |
| texture: grainy ↔ smooth | 0.47 [0.30, 0.63] | 0.11 | −0.08 | fail |
| detail: simple ↔ intricate | **0.34** [0.20, 0.51] | 0.11 | 0.27 | fail (CLIP's direction is mostly the opposite of people's) |

## Consequences for the claims
1. **Validity on rewritten images.**
   - Saturation and tone are validated; medium is validated but not stably.
   - Background and shot are not validated.
   - The Qwen-rewritten images were not sampled separately. Their readings rest on the FLUX.2-rewritten result and are flagged as such.
2. **Q4 is read only on aspects validated on both sides of each contrast:**
   - P1 klein 4B: round-1 set ∩ round 3 = saturation, tone, medium;
   - P2 FLUX.2 dev: round-2 set ∩ round 3 = saturation, medium.
3. **The only confirmed Q4 displacement is not interpretable.** That displacement was FLUX.2 dev's background moving toward busy (+0.67, p_holm .002). Background is validated neither on FLUX.2 dev's original images (round 2) nor on rewritten images (round 3).
   - It is reported as a measurement that people do not support.
   - On validated aspects, rewriting produces no confirmed displacement and no widening beyond the margin. Medium moves toward illustration in both generators (+0.53 and +0.37, intervals excluding 0), but not significantly after correction.
4. **Q5 is rescored** with round-3 validity (`results/q5/`). Every conclusion holds.
5. **Q6: no VLM-proposed axis passes.** People understand the proposed properties, but CLIP does not order images along them as people do. For level of detail it mostly orders them the other way.
   - Language can propose appearance properties, but a proposed property is not yet a measurement.
   - This supports the method's rule: an axis enters the audit only after human validation.
