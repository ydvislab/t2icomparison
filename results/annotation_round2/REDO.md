# Human check, round 2: re-annotation (2026-10-14)

## What happened
- After the round-2 analysis, the owner found that annotators B and C had forgotten the annotation criteria. The owner re-briefed each of them separately on the annotator guide, and each re-labelled the same 120 pairs.
- Neither annotator saw CLIP's answers or the other's labels.
- Annotator A (the owner) and D did not re-label.
- **This re-annotation was not pre-specified.**
  - It is reported **alongside** the original round 2 (`RESULTS.md`), never instead of it.
  - The original labels stay the protocol's primary result.
- Output: `redo.txt`, produced by `annotation/round2_redo.py`.

## Result (large-gap pairs: agreement with CLIP / can't tell; rule ≥ 0.75 and ≤ 0.40)
| Aspect | Original A, B, C | Re-labelled A, B′, C′ | Leaving one annotator out (re-labelled) | + D |
|---|---|---|---|---|
| shot | pass 0.94/0.14 | **pass 0.96/0.25** | pass in all three | pass |
| saturation | fail 0.71/0.03 | **pass 0.77/0.17** | pass in 2 of 3 (fails without A: 0.67) | pass 0.78 |
| medium | fail 0.71/0.33 | **pass 0.77/0.39** (can't tell just under 0.40) | pass in 2 of 3 (fails without A: can't tell 0.46) | pass 0.77 |
| background | fail 0.74/0.14 | fail 0.70/0.25 | fail in all three | fail |
| tone | fail 0.60/0.31 | fail 0.64/0.31 | fail in all three | fail 0.74 |

## Did the re-briefing push answers toward CLIP? No.
- **B → B′:**
  - 84% of answers are identical; no left/right answer was reversed.
  - Of the 19 changed answers, 4 now match CLIP, while 6 matched CLIP before.
- **C → C′:**
  - "can't tell" rose from 6% to 40%, so C now uses the option as the guide intends; C had almost never used it.
  - Of the 49 changed answers, 5 now match CLIP, while 22 matched CLIP before; most of these became "can't tell".
  - Only 7% of answers reversed direction.
- **What raised agreement:** abstaining on pairs that are hard to judge. Answers were not turned toward CLIP.
  - C's original pattern resembles that of the round-1 annotator who was excluded for never using "can't tell". No exclusion rule was fixed for round 2, however, so the original labels are not discarded.

## Reading
1. **Shot is robustly validated** on the later configurations, under both versions.
2. **Saturation and medium are borderline.**
   - They fail with the original labels and pass narrowly with the re-labels.
   - With the re-labels, each passes only while annotator A is included.
   - In the paper they are reported as "borderline on the later configurations", with both numbers.
3. **Background and tone fail** under both versions; they are not validated on the later configurations.
4. **Qwen-Image saturation pairs** (9 pairs) agree 0.62 (original) and 0.65 (re-labelled). These pairs alone remain too few to decide.

## What the paper says
Human check round 2 (Table 1):
- the original result;
- the re-annotation result, with the reason it was done and the test-retest figures above.

Claim status: unchanged from `RESULTS.md`, except that saturation and medium on the later configurations move from "fail" to "borderline".
