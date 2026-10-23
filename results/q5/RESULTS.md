# Q5 results: can a VLM describe these differences correctly?

**Final run, 2026-10-19.**
- **Coverage:** both VLMs (Qwen3.5-4B; Mistral-Small-3.2-24B), all six pre-registered contrasts, and the two null controls of deviation 2.
- **Round 3 applied (2026-10-19):** the rewriting contrasts are scored only on aspects validated on both sides. Numbers below are from the run without round-3 restrictions; with them, per-subject rates change by at most 0.02 and pooled variety accuracy by up to 0.06 (0.33 → 0.38, 0.36 → 0.42); every conclusion holds (`summary.csv` is the restricted run).
- **Pending:** the owner's check of the free-text coder (`coding_check_sample.csv`, 20% sample).
- **Scoring:** `PREREG.md`, `q5_score.py`, `free_score.py`.

## Constrained answers
| Level | Question | n | Qwen3.5-4B accuracy | Mistral-24B accuracy | Truth "no difference" |
|---|---|---|---|---|---|
| per subject | shift | 369 | 0.47 | 0.47 | 22% |
| per subject | variety | 251 | 0.63 | **0.78** | 0% |
| pooled | shift | 80 | 0.13 | 0.13 | **88%** |
| pooled | variety | 75 | 0.36 | 0.33 | 33% |

| Characteristic error | Qwen3.5-4B | Mistral-24B |
|---|---|---|
| Concentration reported as a shift (truth: same place, less varied) | 13 of 14 | 14 of 14 |
| Pooled shift claimed where opposite per-subject shifts cancel | 59 of 60 | 60 of 60 |
| **Null control: a shift reported between two sets from the same configuration** | **98%** (subject), 98% (pooled) | **100%**, 100% |
| **Null control: a change in variety reported** | 99%, 100% | 100%, 100% |

## Free text
| | Qwen3.5-4B | Mistral-24B |
|---|---|---|
| Statements about variety | 582 of 1,160 | 517 of 1,160 |
| Units where the audit finds narrowing that the free text mentions | 92% | 86% |
| **Null control: units whose free text claims a difference on a measured aspect or variety** | **90%** | **93%** |
| Per-subject directional statements that are correct | 0.69 | 0.74 |
| Pooled directional statements that are correct | 0.57 (n = 14) | 0.18 (n = 33) |

## Reading
1. **A VLM asked how two sets differ always finds a difference.**
   - Between two sets of images from the same configuration (different seeds), both VLMs report a shift and a change in variety in 98–100% of constrained answers.
   - In 90–93% of their free-text descriptions, they claim a difference on a measured aspect or in variety.
   - Their descriptions therefore carry no information about *whether* two configurations differ.
2. **Given a real difference, the larger VLM often gets the direction of variety right** (0.78 per subject; about 0.9 for distillation and SDXL → Turbo). Its free text mentions narrowing where the audit finds it (86%). But it mentions narrowing almost as often where there is none, so the mention is not evidence.
3. **Narrowing is described as movement, and pooled claims are false where they matter.**
   - Every case the audit marks "same place, less varied" was answered with a shift.
   - Every pooled "no change" that hides opposite per-subject shifts was described as a pooled shift.
4. **Consequence for the method.** A VLM description can suggest where to look. It cannot replace the audit's decision of whether, where and for which subjects a difference exists. The statement view of the audit tool links every statement to that evidence.

## Deviation 3: stability across draws and truth from the shown seeds (exploratory)
Files: `stability.csv`, `shown_seed_truth.csv` (`q5_stability.py`).

| | Qwen3.5-4B | Mistral-24B |
|---|---|---|
| Same answer on a second, disjoint draw of grids (subject shift / variety; chance ≈ 0.5) | 0.88 / 0.91 | 0.93 / 0.88 |
| Per-subject shift accuracy against the 32-seed / the 8-seed truth (n = 171) | 0.60 / 0.61 | 0.56 / 0.58 |
| Per-subject variety accuracy against the 32-seed / the 8-seed truth (n = 48) | 0.63 / 0.63 | 0.73 / 0.73 |
| 8-seed and 32-seed truth agree where both are decided | 0.98 (shift), 1.00 (variety) | |

- **The answers are stable,** not random: a new draw of images gives the same answer in 88–93% of cases.
- **The 8 shown seeds are not the reason for the errors.** Where the shown seeds decide, they agree with the 32-seed truth in 98–100% of cases, and accuracy hardly changes. The errors are systematic.

## Deviation 4: people reading the same grids (exploratory)
Files: `grid_check_summary.csv`, `grid_check_items.csv` (`make_grid_check.py`, `grid_check_score.py`).
- **Design:** three annotators (H1–H3, independent) answered the VLMs' constrained questions on 48 first-draw grid pairs:
  - 36 items from the six contrasts (18 shift: 5 right, 5 left, 8 none; 18 variety: 12 less, 6 more);
  - 12 null items.
- **People's majority:** two of three answers agree; one variety item has no majority.

| | People (majority) | H1 / H2 / H3 | Qwen3.5-4B | Mistral-24B |
|---|---|---|---|---|
| **Null items: a difference reported** (n = 12) | **0.33** | 0.17 / 0.50 / 0.25 | **1.00** | **1.00** |
| Real items: answered "no difference" | 0.34 | 0.47 / 0.14 / 0.36 | 0.00 | 0.00 |
| Real shift, truth right/left: correct (n = 10) | 3/10 | 2 / 6 / 3 | 6/10 | **8/10** |
| Real shift, truth none: correct (n = 8) | 2/8 | 4 / 2 / 3 | 0/8 | 0/8 |
| Real variety: correct (n = 18; 17 for the majority) | 12/17 | 11 / 17 / 10 | 13/18 | **15/18** |
| Agreement with the people's majority | | | 0.36 | 0.38 |

Fleiss' κ among the people: 0.41 (shift), 0.54 (variety).

### Reading (deviation 4; 48 items, so differences of a few items are not reliable)
1. **The VLMs' false alarms are not forced by the grids.** On the null items, people mostly see no difference (two thirds of majority answers), while both VLMs report one every time. The inability to answer "no difference" belongs to the VLMs, not to 8-vs-8 grids.
2. **Eight images are hard for people too.** People report a difference on a third of the null items, miss most real shifts (3 of 10), and agree with each other only moderately.
3. **Given a real difference, the VLMs read direction at least as well as people's quick reading.** Mistral-24B gets 8 of 10 real shifts and 15 of 18 variety changes, against 3 of 10 and 12 of 17 for the people's majority.
4. **Real items where the audit finds no shift are hard for everyone.** People get 2 of 8, both VLMs 0 of 8.
5. **Consequence:** neither a VLM's description nor a person's look at a few images settles whether two configurations differ. The audit's decision rests on 32 seeds and validated measures.
- **Limitation:** all variety items had a real difference, so these items do not test variety false alarms outside the null items.
