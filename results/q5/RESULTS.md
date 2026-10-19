# Q5 results: can a VLM describe these differences correctly?

**Final run, 2026-10-19.**
- **Coverage:** both VLMs (Qwen3.5-4B; Mistral-Small-3.2-24B), all six pre-registered contrasts, and the two null controls of deviation 2.
- **Round 3 applied (2026-10-19):** the rewriting contrasts are scored only on aspects validated on both sides. Numbers below are from the run without round-3 restrictions; with them, every rate changes by at most 0.03 and every conclusion holds (`summary.csv` is the restricted run).
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
