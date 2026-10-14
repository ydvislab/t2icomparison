# Q3 results: what does a distillation package change?

Run 2026-10-14 with `experiments/model_study/analysis/q2_q3.py`. The server copy was checked byte-identical to the pre-registered version (`68577bf`; rules in `frozen_q2q3.json`). As disclosed there, some of these contrasts had already been viewed in the audit tool, so Q3 is a pre-specified analysis, not a blind test. The frozen scale and margins are those of Q1. Files: `primary.csv` (10 tests, Holm within Q3), `packages.csv` (descriptive), `reversals.csv`, `run.json`.

**How to read the tables:**
- **Shift** is in scale units, toward the right pole (vivid / painting / wide / vintage / busy).
- **Spread** is the IQR ratio B / A.
- **Intervals** are 90%. A and B are resampled independently, because the two checkpoints differ.

## Primary case: klein 4B package (klein-base 4B, CFG 1 → klein 4B; new checkpoint, 50 → 4 steps, CFG 1 in both)
| Aspect | Shift | Spread |
|---|---|---|
| saturation | **+0.95** [+0.67, +1.19] → **displaced** (toward vivid) | **×0.41** [0.37, 0.55] → **concentrated** |
| medium | −0.47 [−0.64, −0.25] → shift below margin (toward photo) | **×0.48** [0.38, 0.57] → **concentrated** |
| shot | +0.16 [−0.23, +0.35] → same place | **×0.50** [0.41, 0.60] → **concentrated** |
| tone | −0.31 [−0.62, −0.05] → inconclusive | **×0.49** [0.40, 0.60] → **concentrated** |
| background | +0.20 [−0.14, +0.45] → same place | **×0.63** [0.49, 0.70] → **concentrated** |

**Reading:**
- The klein distillation package concentrates all five aspects beyond the margin, and displaces only saturation, toward vivid colour.
- This is the pattern of raising guidance in the base model (Q1, klein-base 4B: saturation displaced +0.65; four aspects concentrated), as strong or stronger on every aspect (tone narrows ×0.49 in both; saturation, medium and shot narrow more).
- This agrees with DefaultShift's observation that distilled models behave like increased teacher guidance.
- Because the package changes the checkpoint and the step count together, the effect is not attributed to either one.

## Descriptive packages (no p values; never attributed to one setting)
- **klein 9B package** (klein-base 9B → klein 9B):
  - small effects: saturation +0.38 and background +0.34, both unresolved;
  - spreads ×0.77–0.88, mostly "same spread".
  - The 9B distillation changes defaults much less than the 4B one.
- **SDXL → SDXL-Turbo** (checkpoint, scheduler, 50 → 1 steps, CFG 5 → 0, 1024 → 512 px):
  - every pooled shift is "same place" or unresolved;
  - spreads narrow (×0.51–0.72) but stay unresolved.
  - Per subject, however, **4 of 5 aspects hide opposite shifts** (`reversals.csv`). For saturation, 9 subjects become more vivid and 6 more muted; for shot, 5 wider and 9 closer.
  - Each counted subject's own 90% interval excludes 0, and its shift is at least 0.5.
  - This is the T2 case: a pooled "no change" that is false for most subjects.
  - In the audit tool, the reversal count uses point estimates only (10 up, 7 down for saturation); the stricter interval rule here gives 9 and 6.
- **Reversals in the primary case:** saturation moves toward vivid in 15 subjects and toward muted in none. Shot and background hide opposite shifts (5 up / 5 down; 7 up / 4 down).
