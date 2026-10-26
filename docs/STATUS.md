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

## 3. Done on 2026-10-26
- **Audit tool:** user-defined aspects with an in-tool check (bundled CLIP text encoder, ONNX fp16, cosine 1.0000 to PyTorch; self-check on first use) and an encoder switch (CLIP | SigLIP 2, with each encoder's scale and validity). Deployed on the server build.
- **PacificVis draft 3** (`docs/manuscript/pacificvis/`, English and Chinese): the experiments are organised as three failure modes of judging without visual analysis; Table 3 links each failure to a requirement, a design, a case and an expert task.
- **Expert study:** tool versus baseline, about 60 minutes (`EXPERT_SESSION.md` section 7, sheets regenerated).

## 4. Missing before submission (paper 2026-11-09; abstract 2026-11-02)
1. **Owner:** authors and affiliations; single- or double-blind; abstract registration in PCS by 11-02.
2. **Expert sessions:** five experts and a pilot, a blinded second judge; the offline package is rebuilt from the final tool before the pilot.
3. **Case 6.5:** the owner's own in-tool check of a user-defined aspect on real data.
4. **Cases 6.1–6.4:** the bracketed details read on real data; screenshots.
5. **Figures:** teaser, framework, failure evidence, interface, two case figures.
6. **VGTC LaTeX** (tectonic or Overleaf), page fit to 9 + 2, abstract shortened, AI-use disclosure.
7. Owner's coder check of `results/q5/coding_check_sample.csv` (464 statements).
