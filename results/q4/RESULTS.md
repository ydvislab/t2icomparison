# Q4 results: does LLM prompt rewriting displace or concentrate appearance defaults?

**Status, 2026-10-15 evening: preliminary, klein 4B side only.**
- P2 (FLUX.2 dev) is still generating.
- The final run applies Holm over all 20 tests of `PREREG.md`. This run corrected over the 10 klein tests only, so p values and verdicts may still change.
- Round 3 (human check on rewritten images) has not been run, so validity on these images is not yet established.

**Setup** (`experiments/llm_study/PREREG.md`, deviation 1):
- **Rewriters:** FLUX.2's official upsampler (Mistral-Small-3.2-24B with BFL's system message, temperature 0.15) and Qwen3.5-4B with the same instruction.
- **Rewrites:** one per seed; median 156 words (FLUX.2) and 126 words (Qwen).
- **Images:** klein 4B, same seeds as the original images, so every rewritten image is paired with an original from the same starting noise.

## P1: klein 4B, original prompt → FLUX.2 rewrite
| Aspect | Shift (90% interval) | Subjects up / down | Spread ratio | Verdict (preliminary) |
|---|---|---|---|---|
| medium | **+0.53** [+0.20, +0.92] toward painting/illustration | 12 / 2 | ×1.31 | **displaced**; spread inconclusive |
| background | +0.49 [+0.07, +1.02] toward busy | 12 / 2 | ×1.30 | inconclusive |
| saturation | −0.24 | 5 / 8 | ×1.24 | same place, same spread |
| shot | −0.01 | 5 / 6 | ×1.28 | same place, same spread |
| tone | −0.15 | 4 / 6 | ×1.13 | same place, same spread |

- **Rewriting does not restore variety beyond the margin.** Spreads widen by ×1.13–1.31, below the 1.5 margin.
- **What it does is move the medium:** klein's photographs become more illustration-like. In `figures/largest_shifts_klein.jpg` (top row: bird, original vs. rewritten), the rewritten birds are visibly rendered as detailed illustrations.

## Descriptive contrasts
- **D1: original → Qwen rewrite.**
  - Saturation shifts toward **muted** (−0.62; 15 subjects down, 4 up).
  - Medium shifts toward painting (+0.56; 14 up).
  - Example (figure, bottom row): "a traveler" becomes a medieval fantasy wanderer in misty forests and lamp-lit stone streets, muted and dark.
- **D2: FLUX.2 rewrite → Qwen rewrite.** Saturation differs by −0.36, so **the choice of LLM changes the defaults**.
- **D3: fixed vs. per-seed rewrites.**
  - One rewrite reused for all seeds **concentrates** every aspect relative to the original (×0.71–0.79).
  - Varying the rewrite across seeds widens it again (×1.25–1.80 against the fixed rewrite).
  - **The extra variety under rewriting comes from sampling different texts, not from releasing the model's own defaults.** A single detailed rewrite narrows the output.

## Text side vs. image side (exploratory; `text_words.csv`, `text_vs_image.csv`)
- **Every rewrite of both LLMs describes lighting** (100%): "soft, diffused", "warm", "natural light".
  - Time of day appears in 15% (FLUX.2) and 38% (Qwen) of rewrites.
  - Photographic or cinematic words appear in 18% and 38%.
- **Language and image disagree.**
  - The rewrites' text moves toward "vivid" (CLIP text score +2.0 and +9.6 text units) and toward "a photograph" (−3.5 and −4.8).
  - The images move the other way: toward illustration (both LLMs) and, for Qwen, toward muted colour.
  - Per subject, the text shift predicts the image shift only weakly: Spearman 0.42 for saturation and 0.58 for background with the FLUX.2 rewriter; about 0 otherwise.
- **Reading:** what a rewrite *says* about appearance is not what the generator *does* with it. Auditing a rewriter requires looking at the images, not at the rewritten text.

Files: `primary.csv`, `descriptive.csv`, `per_subject.csv`, `text_*.csv`, `run.json`.
