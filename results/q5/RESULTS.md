# Q5 results: can a VLM describe these differences correctly?

**Status, 2026-10-15 evening: preliminary.**
- **Done (2026-10-16):** both VLMs on 5 of 6 contrasts (guidance in klein-base 4B and in Qwen-Image, the klein 4B package, SDXL → Turbo, klein 4B original → FLUX.2 rewrite).
- **Still to run:**
  - the FLUX.2 dev rewriting contrast, once its images are generated;
  - the null controls of deviation 2.
- **Provisional:** the rewriting contrast is scored on all five aspects until round 3 is in.
- **Scoring rules:** `PREREG.md`, `q5_score.py`. Only aspects validated on the configuration sets involved are scored.

## Constrained answers
| Level | Question | n | Qwen3.5-4B accuracy | Mistral-24B accuracy | VLMs say "no difference" | Truth is "no difference" |
|---|---|---|---|---|---|---|
| per subject | shift | 321 | 0.50 | 0.49 | 3% / 0% | 22% |
| per subject | variety | 235 | 0.64 | **0.81** | 0% / 0% | 0% |
| pooled | shift | 80 | **0.15** | **0.15** | 1% / 0% | **81%** |
| pooled | variety | 70 | 0.39 | 0.36 | 0% / 0% | 29% |

| Characteristic error | Qwen3.5-4B | Mistral-24B |
|---|---|---|
| Concentration reported as a shift (truth: same place, less varied) | 13 of 14 | **14 of 14** |
| Pooled shift claimed where a pooled "no change" hides opposite per-subject shifts | 54 of 55 | **55 of 55** |
| Missed concentration (truth less varied, answer "about equally varied") | 0 of 211 | 0 of 211 |

## Reading (preliminary)
1. **The larger VLM sees variety better.**
   - Mistral-24B judges whether a set became more or less varied correctly in 81% of per-subject cases (91% for the klein 4B package, 90% for SDXL → Turbo).
   - Qwen3.5-4B reaches 64%.
2. **Neither VLM ever says "no difference".**
   - Every pair of sets is described as shifted on every aspect, including the 22% of per-subject cases and 81% of pooled cases where the audit shows the typical output stayed in place.
   - So every narrowing is also reported as a move, which is the confusion of displacement and concentration that T1 targets.
3. **Pooled descriptions are wrong where they matter most.**
   - On aspects where opposite per-subject shifts cancel in the pool, both VLMs report a pooled shift in essentially every answer.
   - A description of "how model B differs from model A" therefore asserts changes that are false for many subjects (T2).
4. **Free text** often mentions uniformity and sometimes states things that are not in the images. It will be coded as pre-registered.
5. **Null control:** the null contrasts of deviation 2 will show whether the "always a difference" behaviour comes from the question format.

Files: `truth.csv`, `scored.csv`, `summary.csv`.
