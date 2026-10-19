# Q4 results: does LLM prompt rewriting displace or concentrate appearance defaults?

**Final run, 2026-10-19.**
- All 20 pre-registered tests, Holm-corrected together (`experiments/llm_study/q4_analysis.py`, `PREREG.md`).
- **Pending:** human check round 3 on the rewritten images. Until it is in, validity on these images is not established. Aspects that fail there will be flagged.
- **Correction of the preliminary run (2026-10-15):** that run corrected over the 10 klein tests only and called the klein medium shift "displaced". With all 20 tests it is not significant (p_holm 0.053) and is reported as a trend.

**Setup** (`PREREG.md`, deviation 1):
- **Rewriters:**
  - FLUX.2's official upsampler: Mistral-Small-3.2-24B with BFL's system message, temperature 0.15;
  - Qwen3.5-4B with the same instruction.
- **Rewrites:** one per seed. Median length is 156 words (FLUX.2) and 126 words (Qwen).
- **Images:** klein 4B and FLUX.2 dev, with the same seeds as the original images.

## Validity (human check round 3, 2026-10-19)
- **On rewritten images:**
  - saturation and tone pass;
  - medium passes, not stably;
  - shot and background fail.
- **Readings below are interpretable only on aspects validated on both sides:**
  - P1 klein 4B: saturation, tone, medium;
  - P2 FLUX.2 dev: saturation, medium. FLUX.2 dev's own images are in round 2, where only shot, saturation and medium passed.
- **The confirmed P2 background displacement is not interpretable.** Background fails on both sides, and on the rewritten images CLIP's background reading disagrees with people (0.38).
- **The answer to Q4 on validated aspects:**
  - no confirmed displacement;
  - no widening beyond the margin;
  - a trend toward illustration (medium +0.53 and +0.37).
- **D1 (Qwen rewrites)** was not checked separately and is read with the same aspects.

## Primary tests (original prompt → FLUX.2 rewrite)
| Aspect | P1 klein 4B: shift | spread | P2 FLUX.2 dev: shift | spread |
|---|---|---|---|---|
| saturation | −0.24, same place | ×1.24, same spread | +0.28, inconclusive | ×1.31, inconclusive |
| medium | +0.53 [+0.20, +0.92], p_holm .053, inconclusive (12 subjects up, 2 down) | ×1.31, inconclusive | +0.37 [+0.14, +0.72], inconclusive | ×1.49 [1.16, 1.99], inconclusive |
| shot | −0.01, same place | ×1.28, same spread | +0.11, same place | ×1.09, same spread |
| tone | −0.15, same place | ×1.13, same spread | −0.06, inconclusive | ×1.03, same spread |
| background | +0.49, inconclusive | ×1.30, inconclusive | **+0.67 [+0.47, +0.91], p_holm .002, displaced** (17 up, 0 down) | ×1.09, inconclusive |

**Answer to Q4 before validation** (kept for the record; see Validity above).
1. The official FLUX.2 rewriter displaces FLUX.2 dev's background toward busy: 17 of 24 subjects move that way and none the other way. **Background is not validated on these images, so this is not a finding about appearance.**
2. **Rewriting does not make outputs more varied beyond the margin** in either generator. Every spread ratio is between ×1.03 and ×1.49, and none is resolved as "widened".
3. **klein 4B moves toward illustration (+0.53) and busier backgrounds (+0.49)** in most subjects. Neither effect survives the correction over 20 tests, so both are reported as trends. The images show it clearly (`figures/largest_shifts_klein.jpg`).

## Descriptive contrasts (no p values)
- **D1: klein 4B, original → Qwen rewrite.**
  - Saturation shifts toward muted (−0.62 [−0.82, −0.27]; 15 subjects down, 4 up).
  - Medium shifts toward illustration (+0.56).
  - Example: "a traveler" becomes a medieval fantasy wanderer.
- **D2: FLUX.2 rewrite → Qwen rewrite on klein 4B.** Saturation differs by −0.36 [−0.57, −0.14], so the rewriting LLM changes the defaults.
- **D3: fixed vs. per-seed rewrites.**
  - One rewrite reused for all seeds concentrates every aspect relative to the original prompt (×0.71–0.79).
  - Varying the rewrite across seeds widens it again (×1.25–1.80).
  - **The variety under rewriting comes from sampling different texts, not from the generator.**

## Text side vs. image side (exploratory)
- **Lighting** is described in every rewrite of both LLMs. Time of day appears in 15% (FLUX.2) and 38% (Qwen) of rewrites; photographic or cinematic words in 18% and 38%.
- **Direction of the text.** On the CLIP text side, the rewrites move toward "vivid", "busy background", "vintage tone" and "a photograph".
- **Direction of the images.**
  - Background moves toward busy, as the text says.
  - Medium moves toward illustration, against the text.
  - Saturation moves toward muted for the Qwen rewriter, against the text.
- **Per subject, the text-side shift predicts the image-side shift only for:**
  - saturation with the FLUX.2 rewriter (Spearman 0.42 on klein 4B, 0.53 on FLUX.2 dev);
  - background (0.58 and 0.41).
  - It does not predict medium, shot or tone, and does not predict anything for the Qwen rewriter.
- **Reading:** what a rewrite says about appearance is only partly what the generator does with it.

Files: `primary.csv`, `descriptive.csv`, `per_subject.csv`, `text_words.csv`, `text_vs_image.csv`, `text_scores.csv`, `run.json`.
