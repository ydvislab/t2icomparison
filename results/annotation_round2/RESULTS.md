# Human check, round 2: results (2026-10-14)

Design: `annotation/PROTOCOL.md` §5b, fixed before the package was built. 120 pairs from the 6 configurations that were not in round 1 (SD3.5 Large, FLUX.2 dev, Qwen-Image-2512 at CFG 4 and 1, klein-base 9B, klein 9B), on the 5 frozen aspects. The rule is unchanged: on the large-gap pairs, agreement with CLIP ≥ 0.75 and "can't tell" ≤ 0.40.

**Annotators:**
- **Primary analysis:** the three annotators of round 1 (A, B, C), as the protocol specifies.
- **Sensitivity only:** a fourth annotator, D, a co-author who was not in the protocol.

**Files:** `aspect_check.csv` and `pair_answers.csv` (primary analysis); `sensitivity.txt` (from `annotation/round2_sensitivity.py`). Raw exports stay on the server.

## Primary result
| Aspect | Round 1 (round-1 configurations) | Round 2 (later configurations) | Leave-one-out in round 2 | With D |
|---|---|---|---|---|
| shot | pass 0.90 | **pass 0.94** | pass in all three | pass 0.93 |
| saturation | pass 0.92 | fail 0.71 (can't tell 0.03) | pass in 2 of 3 | fail 0.73 |
| background | pass 0.81 | fail 0.74 | pass in 1 of 3 | fail 0.73 |
| medium | pass 0.90 | fail 0.71 (can't tell 0.33) | fail in all three | fail 0.73 |
| tone | pass 0.94 | fail 0.60 | fail in all three | fail 0.71 |

## Why round 2 is harder
- **The later configurations are more alike.**
  - The six configurations in round 2 are mostly photographic and concentrated (Q2: FLUX.2 dev and the klein models have the narrowest spreads).
  - So pairs ranked "large" inside round 2's pool are much less different in absolute terms than in round 1. In scale units, the median CLIP gap of large pairs is:

    | Aspect | Round 1 | Round 2 |
    |---|---|---|
    | medium | 5.6 | 1.8 |
    | background | 4.7 | 3.1 |
    | saturation | 4.4 | 3.5 |
    | tone | 3.7 | 3.0 |
    | shot | 4.1 | 4.7 |

  - Shot is the only aspect whose round-2 gaps are as large as in round 1, and it is the only one that passes.
- **Agreement depends on how large the difference is** (both rounds, all tiers, 3 annotators; `sensitivity.txt`):
  - saturation: agreement 0.42 below 1 scale unit, 0.75 at 1–2 units, 0.83–0.84 at 3 units or more;
  - medium: 1.00 at 4 units or more, but 0.43–0.62 below 2;
  - tone and background: unstable below 2 units, 0.69–0.94 above.
  - In short: CLIP's reading matches people when two images really differ, and becomes noise when they barely do.

## What this means for the claims (to be decided by the owner; nothing is dropped silently)
1. **Validity depends on the configuration set.** The protocol requires that an aspect which passes round 1 and fails round 2 be reported per configuration set and flagged in the paper.
   - Saturation, medium, tone and background are validated on SD 1.5, SDXL, SDXL-Turbo and the klein-base 4B / klein 4B family.
   - Among the later configurations only shot is validated; saturation and background are borderline.
2. **Q1, klein-base 4B: supported.** Both G06 and G07 were in round 1, so the klein side of Q1 (saturation displaced, four aspects concentrated) stands on validated measurement.
3. **Q1, Qwen-Image-2512: to be qualified.** Measurement on Qwen-Image is validated only for shot. The few round-2 saturation pairs involving Qwen-Image agree 0.62 (9 pairs, too few to decide).
   - The Qwen-Image results were weaker anyway: only the saturation concentration and a small saturation shift reached significance.
   - The paper should state that the second family's direction is consistent, but measured with lower validated reliability.
4. **Q3 (klein 4B package):** both configurations are in round 1, so the result stands. **Q2 signatures:** the SDXL signature lies on round-1 configurations and is validated; the Qwen-Image signature on shot (closer framing) is validated by round 2; its tone signature is not.
5. **A methodological finding in its own right.** An aspect that people confirm on one set of models need not hold on another, and CLIP agreement rises with the size of the difference. This supports the method's requirements:
   - validate per configuration set;
   - read differences together with their magnitude;
   - keep every reading traceable to the images (task T3).
