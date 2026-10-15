# Outline for the C&G special issue "Bridging Language and Vision: LLM and Visual Analytics" (2026-10-15)

Supersedes the CG&A structure of `paper_en.md` v1. Most v1 text is reused; what changes is the frame and the new study.

## Working title
**Grounding Language in Images: Visual Auditing of Appearance Defaults and Their LLM-Driven Shifts in Text-to-Image Models**
(alternative: *Language Sets the Defaults, Images Hold the Evidence: …*)

## Thesis
In text-to-image generation, language plays three roles:
- it **specifies** what the user wants (the prompt);
- it **intervenes** when an LLM rewrites prompts before generation;
- it **explains**, as VLMs describe how image sets differ, and as text poles define the axes along which images are measured.

Each role produces claims about images that can be wrong in characteristic ways:
- an axis defined in words can be reversed;
- a rewriter can move outputs instead of diversifying them;
- a VLM can call a narrowing a shift, or report a pooled change that is false for many subjects.

A visual audit method grounds every language-derived claim in aligned, validated and traceable image evidence.

## Contributions
1. **Audit method.** Language-defined appearance axes validated per configuration set; displacement vs concentration under pre-registered margins; per-subject structure; validity conditions.
2. **Visual audit system** with linked views for the audit tasks, extended with:
   - a rewrite view (original vs. rewritten prompt, text-side vs. image-side shift);
   - a statement view that links each VLM statement to its evidence (scatter, trajectories, images).
3. **Audit of 12 open configurations.** Q1 guidance, Q2 cross-configuration structure, Q3 distillation.
4. **LLM study** (pre-registered; `experiments/llm_study/PREREG.md`):
   - **Q4:** official FLUX.2 prompt upsampling (and a second LLM) as an intervention on defaults;
   - **Q5:** accuracy and characteristic errors of two VLMs describing set differences, against the audit;
   - **Q6:** VLM-proposed axes passed through the same human validation.
5. **Expert evaluation** with five experts, including a task in which they verify VLM statements, plus lessons.

## Sections (Elsevier, ~10,000–12,000 words)
1. **Introduction:** the three roles of language; the three open questions (displacement or concentration; pooled or per subject; is the claim right); contributions.
2. **Related work:**
   - diversity and default measurement;
   - LLM prompt rewriting/expansion (Prompt Expansion, arXiv 2312.16720; LLM prompt modifiers, arXiv 2504.11104; FLUX.2 upsampling);
   - describing set differences with language (VisDiff, CompCon, VisDiffBench-style evaluation);
   - VLM-as-evaluator;
   - visual analytics of generated images;
   - visual comparison.
3. **Audit method:** tasks T1–T3 plus **T4: verify a language claim**; material; axes and validation (rounds 1–3, Table 1); measures; validity conditions.
4. **Visual audit system:** as v1, plus the rewrite and statement views.
5. **Audit of open configurations:** Q1, Q3, Q2 (compressed from v1).
6. **Language as intervention and explanation:** Q4, Q5, Q6.
7. **Expert evaluation.**
8. **Discussion:** lessons, limitations, implications for LLM-assisted visual analytics (LLMs propose, the visual audit verifies).
9. **Conclusion.**

## Figures (planned)
1. Teaser: the three roles of language, each with one audited example.
2. Method pipeline.
3. Interface.
4. Q1 guidance.
5. Q2 hidden opposite shifts.
6. Q4 rewrite: text-side vs. image-side shift, with images.
7. Q5 VLM accuracy by error type, with one traced wrong statement.
8. Expert results.

## Timeline (target: submission by 2026-11-20)
| Dates | Work |
|---|---|
| 10-15 → 10-17 | Q4 generation and scoring; Q5 runs; Q6 candidates |
| 10-18 → 10-21 | human check round 3; Q4/Q5 analysis; system views for rewrite and statements |
| 10-22 → 11-03 | expert sessions (5 experts), with the new task |
| in parallel | manuscript v2 in the new frame, Chinese version in step |
| 11-04 → 11-15 | figures, SigLIP 2 check, closed-model sidebar or appendix, internal review |
| by 11-20 | submission |
