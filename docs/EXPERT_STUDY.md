# Expert evaluation: protocol (draft, 2026-10-13)

> For paper §6 (`OUTLINE.md`). Draft for the owner to approve; the owner recruits 3–5 experts from the group and checks the institution's ethics requirements before the first session. Nothing here has been run.

## 1. Goal and claims
The evaluation asks whether the audit method lets experts reach **correct, image-backed judgements** on the three audit tasks that a score table plus image grid makes hard. With 3–5 participants it supports qualitative claims only: what experts found, what they verified, where they hesitated, and how their judgement changed. No statistical claim about speed or accuracy is made.

## 2. Participants
3–5 researchers who train, evaluate or select text-to-image models (the owner's group). Record for each: role, years with generative models, whether they have used CLIP-based metrics. No compensation decisions or personal data beyond this are stored in the repository; notes are anonymised as E1–E5.

## 3. Conditions
| | Audit tool | Baseline |
|---|---|---|
| What it shows | `system/audit/` (configuration map, contrast overview, matrix with reversal flags, contrast scatters with margins, paired-seed trajectories, distributions, image strips, settings chips) | A score table (per configuration × aspect: median and IQR in scale units, and per-subject medians on request) plus an image grid (all images of a chosen configuration and subject, unsorted) |
| Data | identical: the same 12 configurations, 24 subjects, 5 aspects and frozen scale | identical |

The baseline is deliberately not weak: it has every number the tool uses, and every image. It lacks the alignment, the margins, the per-subject structure and the image linking.

**Design:** within subjects. Each expert does all three tasks, each task once with the tool and once with the baseline on a *different* case of the same kind (§4), so no case is solved twice. The condition order is counterbalanced across experts (tool first / baseline first) and the case assignment is rotated.

## 4. Tasks and cases
Each task has two cases of the same kind (a and b). Expected answers are fixed from the frozen analyses before the sessions and stored with the session sheet, not shown to the experts.

| Task | Question to the expert | Case a | Case b | Expected answer (from) |
|---|---|---|---|---|
| **T1 displacement vs concentration** | "When guidance goes from 1 to 4, does [aspect] move, tighten, or both? Show the images that convince you." | klein-base 4B, saturation (moves toward vivid and tightens) | klein-base 4B, medium (tightens in place) | `results/q1/RESULTS.md` |
| **T2 pooled vs per subject** | "Overall, does [contrast] change [aspect]? Is that true for every subject?" | SDXL → SDXL-Turbo, saturation (pooled small; opposite shifts across subjects) | a Q2 pair flagged "hides opposite shifts" in `results/q2/hidden_opposite.csv` | `results/q3/reversals.csv`, `results/q2/` |
| **T3 trace to evidence** | "Here is a reading: [claim]. Is it supported by the images? If not, why?" | the style axis (CLIP calls klein's polished photographs "stylized": reversed) | a contrast that changes several settings at once (e.g. SDXL → Turbo), read as the effect of one setting | `results/annotation_study/`, `PROVENANCE.md` |

Per task about 6 minutes per condition. Cases b of T2 and the T1/T3 alternates are chosen by the executor from the frozen results once Q2 and Q3 are run, before any session.

## 5. Session (about 45 minutes)
1. Consent and background (3 min).
2. Introduction to the tool and to the baseline on a training case not used later (guidance on tone in Qwen-Image), 8 min each condition at most.
3. Tasks T1–T3 in the counterbalanced order, think-aloud (about 36 min in total including both conditions).
4. Semi-structured interview (8 min):
   - Which reading would you have got wrong with the table and grid alone? Why?
   - When did you go to the images, and did that change your answer?
   - What would you need to use this for your own model or setting changes?
   - What in the tool is unclear or misleading?

## 6. What is recorded
Per task and condition: the answer, whether it matches the expected answer, the images or views cited as evidence, self-rated confidence (1–5), time to answer, and notable think-aloud remarks. Screen recordings only with consent; they stay outside the repository. Results are summarised in the repository as anonymised tables and quotes (`results/expert_study/`).

## 7. Analysis and reporting
- Per task: correct answers with the tool vs the baseline (counts out of n), confidence, whether the answer cited image evidence, and typical failure modes. Reported descriptively.
- Themes from think-aloud and interviews, with representative quotes.
- Limits stated in the paper: few participants, from the authors' group, a single session each, cases chosen by the authors.

## 8. Still needed
1. Owner: participants and dates (target 10/28–11/3); ethics check.
2. Executor: the baseline page (score table + image grid) built from the same data as the tool; session sheet with case assignment and expected answers, after Q2/Q3 are run.
3. Owner approval of this protocol.

## 9. Task grounding (for paper §3.1)
The three tasks come from the evaluator decisions identified in the external reviews (`REVIEW_PROTO3.md`, `REVIEW_PROPOSAL.md`) and from the gaps of the closest work, rather than from formative interviews:
- **T1** follows from the observation that a diversity score merges two different changes (DIMCIM, GRADE, Vendi) and that DefaultShift separates direction of moved mass from entropy only in closed categories for replacement pairs.
- **T2** follows from the reversal found in the pilot (SDXL-Turbo composition: "a house" +1.31, "a kitchen" −1.33, pooled +0.07) and the review's requirement to show subject-level heterogeneity.
- **T3** follows from the measurement failures found in this project (CLIP's reversed style axis; Qwen-Image's "close-up" faces that CLIP scores as perfectly separated) and from the rule that a contrast changing several settings cannot be attributed to one.

If the owner prefers stronger grounding, 2–3 short interviews (about 20 minutes) with model developers in the group can confirm the tasks before the expert sessions; the experts of §2 can be asked the same questions at the end of their session instead.
