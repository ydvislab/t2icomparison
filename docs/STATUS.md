# Status (2026-10-23)

> One page: what evidence exists, where the work stands, what is missing. Target and conventions: `CLAUDE.md`. Manuscript: `docs/manuscript/paper_v2_en.md` (Chinese in step: `paper_v2_zh.md`). Last external review: `REVIEW_2026-10-22.md`. Earlier status pages are in git history.

## 1. In one sentence
Language now measures, changes and explains the appearance defaults of text-to-image models: text poles define the axes, LLMs rewrite prompts, VLMs describe differences. The paper presents a visual audit method that separates displacement from concentration, exposes per-subject structure and traces every reading, including language-derived claims, to human-validated image evidence. It targets the IEEE PacificVis 2027 conference track (paper due 2026-11-09), reframed as a visual analytics paper; the C&G special-issue target is dropped (2026-10-25, `PACIFICVIS_PLAN.md`).

## 2. Evidence in hand
| Part | State | Where |
|---|---|---|
| Study images: 12 open configurations × 24 subjects × 32 seeds | done, 9,216 images | `PROVENANCE.md`, `RUNBOOK.md` |
| Human check, round 1: 15 candidate axes | done; 5 axes frozen | `annotation/PROTOCOL.md` §7 |
| Human check, round 2: later configurations | done (re-annotation used, first pass archived); shot, sat, medium valid | `results/annotation_round2/` |
| Human check, round 3: rewritten images and VLM-proposed axes | done; sat, tone (and medium, not stably) valid on rewrites; 0 of 6 proposed axes pass | `results/annotation_round3/` |
| Q1: guidance, confirmatory | done | `results/q1/` |
| Q2, Q3: structure and distillation, pre-specified | done | `results/q2/`, `results/q3/` |
| Q4: LLM prompt rewriting, pre-registered | done; no validated widening; the largest effect (FLUX.2 dev background) is on an axis that people reject | `results/q4/` |
| Q5: VLM descriptions, pre-registered, plus null control | done; both VLMs report differences in 98–100% of same-configuration controls | `results/q5/` |
| Q6: VLM-proposed axes | done; none passes | `results/annotation_round3/` |
| Audit tool | rev10 deployed on the server (2026-10-23, real data) | `system/audit/` (README, INTERFACE.md); baseline for the study `baseline.html` |
| Statistical figures (Q1, validation, Q5) | done | `docs/manuscript/figures/` |
| External review of manuscript v2 | done 2026-10-22: reject today, major revision likely after pending work | `REVIEW_2026-10-22.md` |

## 3. Running now (2026-10-23)
- **Second encoder (SigLIP 2):** download, then scoring and the rerun of the Q1/Q3/Q4 primary tests, as specified in `experiments/model_study/analysis/ENCODER_CHECK.md`.
- **Q5 deviation 3 (exploratory):** a second draw of grids to measure answer stability, and a truth computed from the shown seeds (`experiments/llm_study/PREREG.md`).

## 4. Missing before submission (ranked)
1. **Expert study** (protocol revised 2026-10-23, `EXPERT_SESSION.md`): five experts, ideally at least two from outside the group; a pilot session; a blinded second judge. The owner schedules the sessions.
2. Q5 supplement results (stability; shown-seed truth) and the coder check by the owner (`results/q5/coding_check_sample.csv`).
3. Encoder check results, and the paper text on encoder dependence.
4. Interface figure and three case figures (guidance; pooled reversal; language claim traced in the audit trail).
5. Data manifest (model revisions, seeds, hashes, library versions), reference check (19–22), C&G formatting (highlights, graphical abstract).
6. Optional: closed-model sidebar (only if completed and validated).
