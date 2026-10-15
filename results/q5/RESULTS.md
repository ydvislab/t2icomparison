# Q5 results: can a VLM describe these differences correctly?

**Status, 2026-10-15 evening: preliminary.**
- **Done:** Qwen3.5-4B on the four contrasts with existing images (guidance in klein-base 4B and in Qwen-Image, the klein 4B package, SDXL → Turbo).
- **Still to run:**
  - Mistral-Small-3.2-24B, after the FLUX.2 dev generation has freed the GPU;
  - the two rewriting contrasts.
- **Scoring rules:** `PREREG.md`, `q5_score.py`. Only aspects validated on the configuration sets involved are scored.

## Constrained answers, Qwen3.5-4B
| Level | Question | n | Accuracy | VLM says "no difference" | Truth is "no difference" |
|---|---|---|---|---|---|
| per subject | shift | 235 | 0.51 | 3% | 20% |
| per subject | variety | 208 | 0.66 | 0% | 0% |
| pooled | shift | 60 | **0.17** | 2% | **83%** |
| pooled | variety | 55 | 0.49 | 0% | 9% |

- **The VLM almost never says "no difference".** Where the audit finds that the typical output stayed in place, the VLM still reports a shift.
- **Concentration reported as a shift:** in 12 of 13 per-subject cases that the audit marks "same place, less varied", the VLM answers with a shift.
- **Pooled overreach:** on aspects where a pooled "no change" hides opposite per-subject shifts, the VLM claims a pooled shift in 39 of 40 answers.
- **Free text is different.** It often names concentration ("more uniform", "more consistent backgrounds") and sometimes demographic narrowing ("exclusively male"). Some statements are unsupported, for example a black-and-white image that is not in the grid. The free text will be coded as pre-registered (Qwen3.5-4B coder, owner check of a 20% sample).

**Preliminary reading.** A small VLM asked "how do these sets differ?" reports a direction for almost every aspect. It cannot tell a narrowing from a move, and it repeats pooled shifts that are false for many subjects. These are exactly the errors the audit method is built to expose (T1, T2). Mistral-24B will show whether a larger VLM behaves differently.
