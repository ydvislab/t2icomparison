# PacificVis 2027 plan (decided 2026-10-25)

## Decision
- **Target:** IEEE PacificVis 2027, Conference Paper Track, regular research paper.
- **Owner's decisions:** the owner decided on 2026-10-25:
  - **C&G dropped:** the Computers & Graphics special issue is dropped. PacificVis forbids the same or substantially overlapping work being under review elsewhere at the same time (`docs/manuscript/paper_v2_*.md` stays as the source text).
  - **Reframing:** the paper is reframed around visual analytics and interaction. The system is the main contribution; the statistical and LLM studies become findings that the system lets an analyst reach and check. The system must support exploration: conclusions are reached by interaction, not displayed as precomputed results.
- **System additions:**
  1. user-defined aspects with an in-tool human check;
  2. every verdict computed live from the current set, margins and data;
  3. a findings log (insight provenance).
- **Real data:** usage scenarios are run on real data from the expert offline package, copied to the local machine.

## Venue facts
Checked on 2026-10-25 at pacificvis2027.github.io, "Conference Papers" and "Paper Submission Guidelines".

| Item | Requirement |
|---|---|
| Abstract registration | 2026-11-02, 23:59 AoE (title, abstract, authors, keywords in PCS) |
| Full paper | 2026-11-09, 23:59 AoE |
| Notification | 1st round 2026-12-16; revision 2027-01-11; final 2027-01-25; camera-ready 2027-02-08 |
| Length | 9 pages + 2 pages for acknowledgments and references only |
| Template | IEEE VGTC conference template |
| Review | single- or double-blind (author's choice) |
| Dual submission | same or substantially overlapping work must not be under review elsewhere |
| Supplemental | videos, code, data encouraged; the paper must stand alone |
| AI disclosure | generated text, figures or code disclosed in the acknowledgments |
| Paper types | regular; "System Paper" checkbox available (judged on completeness, usability, practical value) |

## Paper structure (9 pages)
| § | Content | Pages | Source |
|---|---|---|---|
| 1 | **Introduction:** appearance defaults; language as axis, intervention and explanation; why the evaluator needs exploration rather than a score; contributions | 1 | v2 §1 rewritten |
| 2 | **Related work:** VA for generative models; visual comparison; LLM/VLM in VA; default and diversity measurement (short) | 0.75 | v2 §2 |
| 3 | **Requirements:** analysis tasks T1–T5 and design requirements, derived from pilot observations, prior work and the measurement pitfalls found in the project | 0.75 | v2 §3.1, INTERFACE.md |
| 4 | **Measurement backend:** language-defined aspects, human check, shift and spread with margins, live bootstrap (compact; details and pre-registrations in the supplement) | 0.75 | v2 §3.3–3.5 |
| 5 | **System:** comparison set, views A–E, linking, user-defined aspects with in-tool check, live verdicts, audit trail and findings log; design rationale | 2.5 | INTERFACE.md (rev13+) |
| 6 | **Usage scenarios:** each a path of interactions on real data that leads to a finding: (1) concentration under guidance and distillation; (2) a pooled "no change" that hides reversals; (3) a language-defined axis that fails on rewritten images; (4) checking VLM statements, including the null control; (5) a user-defined aspect explored and checked | 2 | v2 §5–6, results |
| 7 | **Expert evaluation:** formative sessions with domain experts; tasks, observations, feedback | 1 | EXPERT_SESSION.md |
| 8 | **Discussion:** language proposes, images decide; limitations; generality | 0.5 | v2 §8 |
| 9 | **Conclusion** | 0.25 | |

**Honesty rule for §6:** the findings were first established by scripted, partly pre-registered analyses. The scenarios show how the tool reaches and checks them, and the paper says so. A scenario never claims a discovery that the tool did not support. Findings first reached in the tool (new user-defined aspects, expert observations) are reported as such.

## Schedule
| Dates | Work | Who |
|---|---|---|
| 10-25 – 10-28 | System: live verdicts, findings log, user-defined aspects (in-browser CLIP text encoder + in-tool check); VGTC template; outline | Claude |
| 10-26 | Copy the expert offline package to the local machine (`~/va4ext/expert_offline/`) | owner |
| 10-28 – 11-01 | Usage scenarios on real data; draft §1–6; abstract | Claude |
| 11-02 | Register the abstract in PCS | owner |
| 11-02 – 11-06 | 3–5 expert sessions, about 45 min each, with the rev13+ package | owner (moderator sheets updated by Claude) |
| 11-06 – 11-08 | §7, figures, Codex review (gpt-6-astra low), revision | Claude |
| 11-09 | Submit | owner |

## Open items for the owner
- Author list and affiliations; single- or double-blind.
- PCS account and abstract registration by 11-02.
- Experts for 11-02 – 11-06; ethics wording for the paper.
- LaTeX: no TeX is installed locally. Either install `tectonic` locally or compile on Overleaf.
