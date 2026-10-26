# Status (2026-10-26)

> One page: what evidence exists, where the work stands, what is missing. Target and conventions: `CLAUDE.md`. Manuscript: `docs/manuscript/pacificvis/paper_pvis_en.md` (PacificVis draft; plan `PACIFICVIS_PLAN.md`); source text `docs/manuscript/paper_v2_en.md` and `paper_v2_zh.md`. Last external review: `REVIEW_2026-10-22.md`. Earlier status pages are in git history.

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
| Q5: VLM descriptions, pre-registered, plus null control | done; both VLMs report differences in 98–100% of same-configuration controls; answers stable across draws and unchanged against the shown-seed truth (deviation 3); people reading the same grids report a difference on a third of null pairs (deviation 4) | `results/q5/` |
| Second encoder (SigLIP 2) | done; concentration robust, displacements encoder-specific | `results/encoder_check/` |
| Q6: VLM-proposed axes | done; none passes | `results/annotation_round3/` |
| Audit tool | rev13 with live verdicts and the findings log (2026-10-25); user-defined aspects in progress | `system/audit/` (README, INTERFACE.md); baseline for the study `baseline.html` |
| Statistical figures (Q1, validation, Q5) | done | `docs/manuscript/figures/` |
| External review of manuscript v2 | done 2026-10-22: reject today, major revision likely after pending work | `REVIEW_2026-10-22.md` |

## 3. Running now (2026-10-26)
- **User-defined aspects with an in-tool check** (`PACIFICVIS_PLAN.md`): in-browser CLIP text encoder; the fidelity test against PyTorch (cosine ≥ 0.99) has not passed yet.
- **PacificVis draft** (`docs/manuscript/pacificvis/paper_pvis_en.md`): first full draft; numbers checked against the result files on 2026-10-26; references 19–25 verified.

## 4. Missing before submission (paper 2026-11-09; abstract 2026-11-02)
1. **Owner:** authors and affiliations; single- or double-blind; abstract registration in PCS by 11-02.
2. **Expert study:** the draft (§7, 45-minute open exploration) and `EXPERT_SESSION.md` with the sheets (75 minutes, tool vs. baseline, T1–T4) disagree; one design must be chosen, then the offline package rebuilt with the final tool and the sheets updated.
3. **User-defined aspects:** finish, pass the fidelity test, run scenario 6.5 on real data.
4. **Scenarios 6.1–6.4 on real data:** fill the bracketed subjects and statements; decide whether the tool gets a seed-split null contrast (6.4 step 4).
5. **Figures:** teaser, interface, set across views, three scenario figures (real-data screenshots).
6. **VGTC LaTeX** (no TeX locally: tectonic or Overleaf), page fit to 9 + 2, AI-use disclosure.
7. Owner's coder check of `results/q5/coding_check_sample.csv` (464 statements).
