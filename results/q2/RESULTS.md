# Q2 results: where do configurations settle, and do differences persist across subjects?

Run 2026-10-14 with `experiments/model_study/analysis/q2_q3.py`, pre-registered in `frozen_q2q3.json` (`68577bf`). Q2 is descriptive: there are no p values and no attribution to family, scale or architecture.

**Scope:** 8 configurations at their recommended settings: SD 1.5, SDXL, SD3.5 Large, FLUX.2 dev, klein-base 4B (CFG 4), klein 4B, Qwen-Image-2512 (CFG 4) and klein-base 9B.

**Measures:**
- **Location:** per subject, the distance from the median of the 8 configurations' medians, in scale units. The typical location is the median over subjects, with a 90% hierarchical bootstrap interval.
- **Spread:** the IQR in scale units (1 ≈ the average within-cell spread of the 12 configurations).

Files: `locations.csv`, `pairwise.csv` (28 pairs × 5 aspects), `subject_dependent.csv`, `hidden_opposite.csv`, `run.json`.

## 1. Most configurations share their defaults; a few have strong signatures
- **Pairwise:** only 5–8 of the 28 configuration pairs per aspect differ beyond the margin in pooled location (saturation 8, medium 7, shot 7, background 7, tone 5).
- **Signatures** (typical location beyond ±0.5, 90% interval excluding 0):
  - **SDXL:** painting-like (medium **+3.64** [+1.55, +4.16]), muted (saturation **−1.68**), busy backgrounds (**+1.12**), vintage tone (**+0.65**).
  - **Qwen-Image-2512:** closer framing (shot **−1.81** [−2.44, −0.79]) and vintage tone (**+0.71**).
  - **All others** (SD 1.5, SD3.5 Large, FLUX.2 dev, the klein models) stay within ±0.5 of the centre on every aspect, apart from the bounds of single intervals.
- **Spread:**
  - SD 1.5 is the most varied (1.33–1.50 on four aspects);
  - SDXL is wide (1.13–2.07);
  - FLUX.2 dev is the most concentrated (0.61–0.92, with medium 0.61), followed by klein 4B (0.57–0.84) and klein-base 4B at CFG 4 (0.59–0.98).

## 2. Defaults often depend on the subject
- **9 configuration × aspect combinations** have subject-dependent defaults: at least 3 subjects on each side beyond ±0.5, each with its own interval excluding 0. Examples:
  - SDXL tone: 13 subjects vintage, 3 modern;
  - Qwen-Image background: 9 busy, 6 plain;
  - SD 1.5 saturation: 9 vivid, 4 muted.
- **61 of the 140 pair × aspect comparisons hide opposite shifts:** the pooled difference lies within the margin, but at least 3 subjects shift beyond +0.5 and 3 beyond −0.5. The count is highest for shot (16), background (15) and tone (13).
  - Example: SDXL vs Qwen-Image on tone, pooled +0.03, but 9 subjects shift each way.

**Reading:** comparing configurations by a pooled number is unreliable for appearance defaults. In almost half of the comparisons, "no difference" overall means opposite differences on different subjects. This is the main evidence for task T2 and for per-subject views in the audit method.
