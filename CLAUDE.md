# Project: t2icomparison

Visual comparison of "generation defaults" across text-to-image models and generation settings, for model developers and evaluators. Target (changed 2026-10-15): Computers & Graphics (Elsevier) special issue "Bridging Language and Vision: Recent Advancements in LLM and Visual Analytics"; the issue closes in December 2026, our own target is submission in November 2026. The earlier target was an IEEE CG&A feature article; `docs/manuscript/` v1 was written to CG&A limits.

## Where to resume
`docs/STATUS.md` (current state) → `docs/PLAN.md` (requirements, timeline, open decisions) → `docs/OUTLINE.md` (paper outline, 20 references).

## Conventions
- The owner writes in Chinese; reports must be plain language, conclusion first. Older docs are in Chinese; new content is in English (see Language below).
- Visualization standards from the owner: established visual encodings (distributions, scatter + contours), little text inside views (details on interaction), no duplicated encodings across views, and the visualization must be indispensable.
- Scope: offline multi-group comparison only. Interactive in-the-loop tools for creators are a separate project and do not belong in this repository.
- Large files (models, images, features, annotation pages) live in `$T2IC_DATA` (default `~/va4ext`), never in git. Record how to regenerate them in `docs/RUNBOOK.md`.
- Venue limits: follow the C&G guide for authors (Elsevier format; check abstract length, highlights and graphical abstract requirements before formatting). The 20-reference cap of CG&A no longer applies. Only cite papers whose identifiers have been verified.
- The LLM study (`experiments/llm_study/PREREG.md`: Q4 prompt rewriting, Q5 VLM difference descriptions, Q6 VLM-proposed axes) carries the special-issue fit; it was pre-registered before any output existed.
- Labeller for background experiments: Qwen3.5-4B, bf16, thinking disabled, constrained multiple choice. Human double annotation is the only ground truth.
- When using new diffusers/transformers features, check the installed version's docs and run the code before committing.
- This repository is public: never commit keys, tokens, server addresses or raw personal annotation exports.
- Commit messages carry no Claude attribution: no `Co-Authored-By` or session trailers. Claude must not appear as a contributor.
- Language: explanations and step-by-step reports to the owner in Chinese; all generated or updated content (code, docs, README, paper) in English.
- The README must not mention the target venue, deadlines or internal plans.
