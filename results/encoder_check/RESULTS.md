# Second-encoder check: results (2026-10-23)

Specification: `experiments/model_study/analysis/ENCODER_CHECK.md`, committed before any SigLIP 2 score.
- **Encoder:** SigLIP 2 (so400m-patch14-384).
- **Inputs:** the same text poles, the same margins, bootstrap and Holm families.
- **Scale:** its own scale, by the frozen definition.

Files: `verdicts.csv` (every primary test, CLIP and SigLIP side by side), `per_subject_correlation.csv`, `human_agreement.csv`, `run.json`. Reproducibility manifest for all images and score tables: `results/MANIFEST.json`.

## 1. Agreement with people (large-gap pairs of rounds 1–3)
| Round | Aspect | CLIP | SigLIP 2 | Same direction |
|---|---|---|---|---|
| 1 | saturation / medium / shot / tone / background | 0.92 / 0.90 / 0.90 / 0.94 / 0.81 | 0.92 / 0.90 / 0.90 / 0.94 / 0.84 | 92–100% |
| 2 | saturation / medium / shot / tone / background | 0.77 / 0.77 / 0.96 / 0.64 / 0.70 | 0.73 / 0.77 / 0.96 / **0.88** / 0.70 | 50–100% |
| 3 (rewrites) | saturation / medium / shot / tone / background | 0.90 / 0.76 / 0.63 / 0.89 / 0.38 | 0.90 / 0.76 / 0.75 / **0.68** / 0.56 | 75–100% |

- **The encoders are equally good on these pairs.** On the pairs people judged, SigLIP 2 agrees with them about as often as CLIP. Where they differ, neither is better throughout: SigLIP is better on round-2 tone, worse on round-3 tone.
- **The comparison favours CLIP,** because the pairs were selected by CLIP's gaps.

## 2. Verdicts of the primary tests
| Claim | CLIP | SigLIP 2 | Reading (rule fixed in advance) |
|---|---|---|---|
| Q1 klein-base 4B: medium, tone, background concentrate | concentrated ×0.53, ×0.49, ×0.65 | concentrated ×0.52, ×0.53, ×0.62 | **robust** |
| Q1 klein-base 4B: saturation concentrates | ×0.51 concentrated | ×0.70, change below margin | weaker, same direction |
| Q1 klein-base 4B: shot | ×0.68, below margin | ×0.58 concentrated | stronger with SigLIP |
| Q1 klein-base 4B: **only saturation is displaced** | sat +0.65 displaced; medium, shot and background in the same place; tone inconclusive | sat +0.44 below margin; **medium +1.08, shot −0.86, tone −1.59 displaced**; background below margin | **encoder-dependent** |
| Q3 klein 4B package: all five concentrate | ×0.41–0.63 | ×0.48–0.58, all five concentrated | **robust** |
| Q3 klein 4B package: saturation displaced | +0.95 | +1.03 | **robust** |
| Q3: other aspects | medium below margin, shot same, tone inconclusive | medium inconclusive, shot inconclusive, **tone −1.22 displaced** | encoder-dependent |
| Q1 Qwen-Image | saturation concentrated, small shift; tone same place | saturation below margin; **tone −0.64 displaced and concentrated**; medium concentrated | encoder-dependent (and tone not validated there) |
| Q4: no widening on validated aspects | no aspect widened | no aspect widened | **robust** |
| Q4 P2: FLUX.2 dev background displaced | +0.67 | +0.93 | robust across encoders, but background is not validated on these images (round 3) |

## 3. Per-subject agreement between the encoders
- **Median Spearman of per-subject Δ:** 0.36 (Q1), 0.33 (Q3), 0.67 (Q4).
- **Median Spearman of log IQR ratios:** 0.25, 0.27, 0.40.
- Per-subject readings depend on the encoder much more than pooled concentration does.

## Reading
1. **Concentration is robust.** Raising guidance and distilling narrow appearance under both encoders, on the same aspects (Q1 klein: medium, tone, background; Q3: all five).
2. **The direction and set of displacements are not robust.** "Only saturation moves" holds with CLIP; with SigLIP 2, guidance also moves medium, shot and tone. The paper must state displacement findings as CLIP findings and present the encoder dependence. The claim that survives both encoders is "concentration on every aspect we can validate; saturation moves under distillation".
3. **Per-subject structure is encoder-sensitive.** This strengthens the case for tracing readings to images (T3): a single encoder's per-subject reading is not a finding without the images.
