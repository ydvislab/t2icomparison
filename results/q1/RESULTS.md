# Q1 primary results: does raising guidance displace or concentrate appearance?

Run 2026-10-13 18:11 with `experiments/model_study/analysis/q1_primary.py`. The server copy was checked byte-identical to the version committed before the run (`38ad8ed`, 14:47). The scale was computed from all 12 configurations (9,216 study images) and frozen in `experiments/model_study/analysis/frozen_scale.json`. Margins and verdict rules come from `frozen_margins.json` (frozen 2026-10-12) and the script header. Files: `primary.csv` (the 20 tests), `per_subject.csv` and `leave_one_category_out.csv` (exploratory), `run.json`.

**Reading the numbers:**
- **Shift** is the change of the median in scale units, positive toward the right pole: vivid, painting, wide, vintage and busy for saturation, medium, shot, tone and background respectively.
- **Spread** is the ratio of interquartile ranges, B / A; below 1 means more concentrated.
- **Intervals** are 90% hierarchical bootstrap intervals (10,000 replicates); **p** values are Holm-adjusted over the 20 tests.

## Primary tests (CFG 1 → CFG 4)
| Aspect | klein-base 4B: shift | klein-base 4B: spread | Qwen-Image-2512: shift | Qwen-Image-2512: spread |
|---|---|---|---|---|
| saturation | **+0.65** [+0.43, +0.93] p .002 → **displaced** (toward vivid) | **×0.51** [0.43, 0.61] p .002 → **concentrated** | +0.39 [+0.18, +0.59] p .012 → shift below margin | **×0.64** [0.54, 0.78] p .003 → **concentrated** |
| medium | −0.03 [−0.20, +0.11] → same place | **×0.53** [0.43, 0.62] p .002 → **concentrated** | −0.21 [−0.43, +0.01] → same place | ×0.81 [0.69, 1.04] → same spread |
| shot | +0.07 [−0.18, +0.27] → same place | ×0.68 [0.58, 0.79] p .002 → change below margin | +0.01 [−0.22, +0.26] → same place | ×0.74 [0.61, 0.93] p .21 → inconclusive |
| tone | −0.37 [−0.70, −0.15] p .053 → inconclusive | **×0.49** [0.42, 0.60] p .002 → **concentrated** | −0.32 [−0.47, −0.21] p .002 → same place (small shift toward modern) | ×0.78 [0.66, 0.97] p .46 → inconclusive |
| background | +0.14 [−0.11, +0.26] → same place | **×0.65** [0.53, 0.75] p .002 → **concentrated** | −0.20 [−0.40, +0.02] → same place | ×0.76 [0.63, 0.90] p .09 → inconclusive |

## Answer to Q1
1. **Guidance mainly concentrates appearance.**
   - In klein-base 4B, raising guidance from 1 to 4 concentrates 4 of 5 aspects beyond the margin: saturation, medium, tone and background, to about half of their spread. The fifth aspect, shot, narrows significantly (×0.68) but stays just inside the margin.
   - Only one aspect is also displaced: saturation, toward vivid colour. Medium, shot and background stay in the same place under the equivalence rule. Tone moves toward a more modern look (−0.37), but this is not significant after correction.
2. **The direction is the same in both families; the size is not.**
   - In Qwen-Image-2512, saturation is concentrated (×0.64) and shifted toward vivid colour (+0.39, significant but below the 0.5 margin).
   - Tone shifts slightly toward modern but stays within the "same place" margin.
   - The other spreads narrow by 0.74–0.81 without reaching significance.
   - Every shift has the same sign as in klein. The smaller effects are consistent with Qwen-Image's guidance rescaling, so CFG 4 is not the same dose in both pipelines (`docs/PROVENANCE.md`, `RESEARCH_PROPOSAL.md` §3).
3. **Robustness (exploratory).**
   - Leaving out any one category keeps every direction and the approximate size (point medians only; intervals and verdicts were not recomputed). klein saturation shift ranges +0.60 to +0.77, klein concentration ratios 0.44 to 0.74, Qwen saturation shift +0.35 to +0.43.
   - Per subject, the saturation shift goes in one direction only: 15 of 24 subjects (klein) and 10 of 24 (Qwen) move toward vivid by at least the 0.5 margin (point estimates; 14 and 10 when each subject's 90% interval must also exclude zero), and none moves that far toward muted.
   - Tone moves toward modern by at least the margin in 10 (klein) and 9 (Qwen) subjects (point estimates; 8 and 8 with the interval rule), and toward vintage in at most 1.

## Changes from the preliminary observations
The preliminary statement "displaces saturation and tone in both families" does not hold as stated. Saturation is displaced beyond the margin in klein only; in Qwen-Image it shifts below the margin. Tone shifts consistently toward modern, but the shift reaches neither significance (klein) nor the margin (Qwen). The paper drafts are corrected accordingly.
