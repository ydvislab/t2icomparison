# Anchor pilot: first reading (2026-10-12)

Run on the GPU server on 2026-10-12: G08 klein 4B and G09 Qwen-Image-2512 (true CFG 4), 576 images each, `--batch 4`; CLIP scores via `aspects/score.py`; tables from `analyze_pilot.py` (`cells.csv`, `phrasings.csv`, `references.csv`). Contact sheets are kept locally (`$T2IC_DATA/model_study/anchors_pilot/sheets/`).

Check 3 (stability) is complete for G08 only. It needs the G09 study images, which are being generated; rerun `analyze_pilot.py` when they are finished.

## Checks against the pre-set rules (`experiments/model_study/anchors/README.md`)
| Aspect | Phrasing | 1 Separation (both refs) | 2 Side effects (median max off-target \|AUC−0.5\| < 0.3) | 3 Stability (x range < 0.15) | 4 Fidelity (contact sheets) |
|---|---|---|---|---|---|
| light | 0 "in cool blue / warm golden light" | pass (AUC 1.0 in every subject) | **fail** (0.50; mostly tone, time) | G08 pass (0.09 over all phrasings) | pass |
| light | 1 "lit by cold bluish / warm amber light" | pass | **fail** (0.50; tone) | as above | pass |
| light | 2 "with a cool blue / warm golden color cast" | pass | **fail** (0.50; tone) | as above | pass |
| shot | 0 "an extreme close-up of {s}" / "a wide shot of {s} from far away" | pass | **fail** (0.50; time, center, light) | G08: 0.08 over phrasings 0–1; 0.60 when phrasing 2 is included | **fail for Qwen-Image**: for "a kitchen" and "a market" all 8 close-ups show a man's face, not the scene |
| shot | 1 "{s}, seen from very close up" / "seen from a great distance" | pass | **fail** (0.50; angle, bg) | as above | partial: Qwen-Image "a market" shows faces in 3 of 8; wide requests become high-angle aerial views in both models |
| shot | 2 "{s}, filling the whole frame" / "small in a wide view" | **fail** (AUC min 0.46 / 0.67) | **fail** | drives the 0.60 range | fail: "filling the whole frame" gives wide views of scenes |

## Observations
- **Check 2 cannot be passed as implemented.** With 8 + 8 images, any other aspect that separates the two request sets perfectly gives |AUC − 0.5| = 0.5, so the median of the maximum over 14 aspects is 0.5 in every cell. The coupled aspects are partly real: warm golden light comes with a golden-hour, sunset-like scene (tone, time), and wide requests come with high-angle views (angle). The rule's intent was that a request should not *mainly* change another aspect, which is a relative-size question that a saturated AUC cannot answer. Any change to the rule is an owner decision and must be documented as a deviation, because the rules were fixed before the run.
- **The measurement passes where the images fail.** CLIP separates Qwen-Image's "extreme close-up" requests perfectly (AUC 1.0) while the images replace the scene with a face. This is the "trace to evidence" case the audit method is meant to catch, and it shows why check 4 cannot be automated with the same encoder.
- **Defaults are visible in the anchors themselves.** klein 4B's wide kitchen views are almost the same image across 8 seeds.

## Owner decisions (2026-10-12) and the result of the revised rule
- **Check 2 revised (documented deviation):** because the AUC-based rule cannot discriminate, side effects are now compared by size. For each subject, the largest |Hedges' g| of the request on another aspect is divided by |g| on the target aspect (`off_ratio` in `cells.csv`). A phrasing is usable if the median over subjects is at most 0.5. The threshold was set before the g values were computed.
- **shot is not calibrated.** It is reported on the uncalibrated scale, and the Qwen-Image "close-up becomes a face" images are kept as a case study of a measurement failure caught by inspecting the images.
- **Result for light under the revised rule (all 14 other aspects):** the median off_ratio is 0.61, 0.81 and 0.56 (phrasings 0, 1, 2) for klein 4B, and 0.59, 0.69 and 0.55 for Qwen-Image. **No phrasing passes; phrasing 2 misses narrowly.** The largest side effects are on tone, mood and time: warm/cool light requests also make the images look like golden hour or evening, and CLIP's "sepia tones" and "moody" texts respond to warm light.
- **Sensitivity (not a rule; computed after seeing the result above):** if side effects are counted only on the candidate aspects of `RESEARCH_PROPOSAL.md` §4.1 (sat, shot, angle, dof, medium), the medians are 0.26, 0.43 and 0.43 (klein 4B) and 0.23, 0.35 and 0.29 (Qwen-Image), and every phrasing passes. Using this would be a second, post-hoc deviation and needs an explicit owner decision.
