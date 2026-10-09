# Project: t2icomparison

Visual comparison of "generation defaults" across text-to-image models and generation settings, for model developers and evaluators. Target: IEEE Computer Graphics and Applications (regular feature article), submission mid-November 2026.

## Where to resume
`docs/STATUS.md` (current state) → `docs/PLAN.md` (requirements, timeline, open decisions) → `docs/OUTLINE.md` (paper outline, 20 references).

## Conventions
- The owner writes in Chinese; reports must be plain language, conclusion first. Docs are in Chinese; code and the paper are in English.
- Visualization standards from the owner: established visual encodings (distributions, scatter + contours), little text inside views (details on interaction), no duplicated encodings across views, and the visualization must be indispensable.
- Scope: offline multi-group comparison only. Interactive in-the-loop tools for creators are a separate project and do not belong in this repository.
- Large files (models, images, features, annotation pages) live in `$T2IC_DATA` (default `~/va4ext`), never in git. Record how to regenerate them in `docs/RUNBOOK.md`.
- CG&A limits: ≤20 references (hard), abstract ≤150 words, ≤14 pages including bios. Only cite papers whose identifiers have been verified.
- Labeller for background experiments: Qwen3.5-4B, bf16, thinking disabled, constrained multiple choice. Human double annotation is the only ground truth.
- When using new diffusers/transformers features, check the installed version's docs and run the code before committing.
- This repository is public: never commit keys, tokens, server addresses or raw personal annotation exports.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
