# Human check, round 2: results (2026-10-14)

Design: `annotation/PROTOCOL.md` §5b. 120 pairs from the 6 configurations that were not in round 1 (SD3.5 Large, FLUX.2 dev, Qwen-Image-2512 at CFG 4 and 1, klein-base 9B, klein 9B), on the 5 frozen aspects. The decision rule is unchanged: on the large-gap pairs, agreement with CLIP ≥ 0.75 and "can't tell" ≤ 0.40.

**Labels used (owner decision, 2026-10-14):**
- Two of the three annotators (B and C) had forgotten the annotation criteria during their first pass.
- The owner re-briefed each of them separately on the annotator guide; no answers were shown. Each then re-labelled the 120 pairs independently.
- The result below uses annotator A's labels and the re-labels of B and C. The first pass is superseded and kept in `first_pass/`.
- Re-labelling did not move answers toward CLIP: of the changed answers, 9 now match CLIP and 28 matched it before. The main change was that C began to use "can't tell" as the guide intends (6% → 40%).
- `annotation/round2_redo.py` prints this comparison (`redo.txt`).

**Files:**
- `aspect_check.csv` and `pair_answers.csv` (from `annotation/analyze.py`);
- `sensitivity.txt` (from `annotation/round2_sensitivity.py`: leave-one-out, a fourth annotator D as a sensitivity check, agreement by gap size).

## Result
| Aspect | Round 1 (round-1 configurations) | Round 2 (later configurations) | Leave one out (round 2) | With D |
|---|---|---|---|---|
| shot | pass 0.90 | **pass 0.96** [0.82, 0.99], can't tell 0.25, κ 0.75 | pass in all three | pass |
| saturation | pass 0.92 | **pass 0.77** [0.59, 0.88], can't tell 0.17, κ 0.20 | pass in 2 of 3 | pass |
| medium | pass 0.90 | **pass 0.77** [0.57, 0.90], can't tell 0.39, κ 0.42 | pass in 2 of 3 | pass |
| background | pass 0.81 | fail 0.70, can't tell 0.25 | fail in all three | fail |
| tone | pass 0.94 | fail 0.64, can't tell 0.31 | fail in all three | fail |

Saturation and medium pass, but not stably: each fails when annotator A is left out. As in round 1, a pass of this kind is reported as "pass, not stable".

## Why background and tone fail here
- The later configurations are more alike (Q2: FLUX.2 dev and the klein models have the narrowest spreads), so the "large-gap" pairs within this pool differ less. Median gap of the large-gap pairs, in scale units:

  | Aspect | Round 1 | Round 2 |
  |---|---|---|
  | medium | 5.6 | 1.8 |
  | background | 4.7 | 3.1 |
  | saturation | 4.4 | 3.5 |
  | tone | 3.7 | 3.0 |
  | shot | 4.1 | 4.7 |

- Agreement rises with the gap: saturation is at 0.42 below 1 unit and at 0.84–0.86 at 3 units or more (both rounds, all tiers).

## Consequences for the claims
| Claim | Configurations | Status |
|---|---|---|
| Q1, klein-base 4B | round 1 | stands (all five aspects validated) |
| Q1, Qwen-Image | round 2 | saturation result stands (validated, not stable); tone and background readings not validated on this configuration |
| Q3, klein 4B package | round 1 | stands |
| Q2, SDXL signature | round 1 | stands |
| Q2, Qwen-Image signature | round 2 | closer framing (shot) stands; vintage tone not validated |
| Q2, hidden opposite shifts | mixed | stands as a statement about the scores; background and tone counts on the later configurations are not validated |

**Methodological finding:**
- An aspect that people confirm on one set of models need not hold on a more homogeneous set.
- Agreement grows with the size of the difference.
- Hence: validate per configuration set, and read differences together with their magnitude.
