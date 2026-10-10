# Novelty check (2026-10-10)

> **Note (2026-10-10, later the same day):** the owner refocused the paper on the models themselves; the system is the instrument. The verdict below was written for the system-centred framing. The updated research questions are in `PLAN.md` §2, and the novelty summary for the model-centred framing is in `STATUS.md` §2.

Scope: is the generation-defaults comparison system still novel given work published up to October 2026, and what exactly is the research question? Search covered arXiv, IEEE VIS 2026, CHI 2026, ICLR 2026, TVCG and CGF. The planned cross-model reviewer (Codex) could not be started on this machine, so this verdict has not had an independent second opinion yet; the dossier is in `.aris/novelty/NOVELTY_DOSSIER.md` for a later run.

## Verdict
**PROCEED WITH CAUTION — 5.5/10.** No published paper contains this contribution. The delta is real but thin in one specific place: tools that put generated images on CLIP concept axes and link attribute histograms to images already exist (ViBEx, Varif.ai). The paper therefore carries only if its case studies show readings that those tools, a diversity score, or a per-attribute benchmark cannot produce.

**One-sentence delta:** Unlike single-group explorers (ViBEx, Varif.ai, POET) and score-only benchmarks (DIMCIM, the attribute-conditional diversity benchmark, DefaultShift), this system places many models *and generation settings* on the same human-checked aspect axes. It reports separately where each group settles and how tightly, and it refuses to attribute a difference to one setting when more than one setting changed.

## Closest prior work
| Work | Venue | Overlap | Difference |
|---|---|---|---|
| ViBEx (2504.19703) | CGF / EuroVis 2025 | Images placed on CLIP concept axes; inspect images to verify | Explores one model at a time (switching sessions); its goal is bias discovery; cross-model comparison is listed as future work |
| Varif.ai (2506.19644) | DIS 2025 | Attribute histograms linked to images; checks diversity | Built for creators and a single output set; has no location/spread split and no record of settings |
| POET (2504.13392) | UIST 2025 | Automatically finds the dimensions on which outputs are homogeneous | Aims to repair outputs by expanding the prompt, not to compare models |
| **GROVE / Beyond One Output (2604.18724)** [new] | IEEE VIS 2026 | Visualizes and compares *distributions* of generations rather than single outputs; finds that summaries help diversity judgments and raw outputs help with details | Works on language-model text, not images; establishes the problem framing that this paper should cite and extend |
| **Attribute-Conditional Diversity Benchmark (2511.10547)** [new] | ICLR 2026 | Per-attribute diversity across 5 models, with human evaluation | A benchmark with scores and binomial tests; no visual comparison, no settings, no location |
| DefaultShift (2608.21784) | arXiv, Aug 2026 | Audits how defaults shift when an accelerated model replaces its reference (Turbo, DMD2, FLUX) | Closed vocabularies and tables; no interface |
| DIMCIM (2506.05108) | arXiv 2025 | Default-mode diversity falls as models improve | Finding plus a metric |
| DyEval (2411.15509) [new] | TVCG 2026 | Interactive visual assessment of T2I models | Probes for prompt-following failures; does not address defaults or diversity |
| Vipera (2510.05742) [new] | CHI 2026 | Visual auditing of T2I outputs | Organizes audit criteria for one output space |
| Entropic diversity vs human judgement (10.1145/3772318.3791383) [new] | CHI 2026 | Diversity metrics disagree with human ratings | Supports the case for human-checked aspects |
| IMPLICIT-Bench (2609.24228) [new] | arXiv, Sep 2026 | Biases that appear under neutral prompts | Demographic categories; a benchmark |

[new] = not yet in `docs/RELATED_WORK.md`. GROVE and DyEval were identified from search snippets; verify their identifiers before citing.

## Restated research question
**Primary:** When a prompt leaves attributes unspecified, how can model developers and evaluators see, across many models and generation settings at once, *which* attributes each group settles, *what* it settles on, and *which setting change* is responsible, with evidence they can check in the images?

- **RQ1 (representation):** What visual representation separates *where* a group's outputs sit from *how tightly* they cluster, for many groups on shared axes, without hiding prompt-level reversals?
- **RQ2 (validity):** Under what conditions is a difference between two groups attributable to a single setting, and how should a comparison interface expose or enforce those conditions?

Positioning shift: from "visualizing diversity" (crowded) to **comparative auditing of generation defaults across models and settings**, the image-generation counterpart of model diffing. The comparison unit is a group defined as model plus settings, not a prompt or a concept.

## Which components carry novelty
| Component | Status |
|---|---|
| Aligned multi-group comparison (shared axes, one brush across groups, shared projection) | Core, but the alignment alone is not enough. The novelty is in what it reveals; it must be shown by cases |
| Location vs spread vs share kept separate | Core. Nobody else separates them for T2I outputs. Needs one case where two groups have equal spread but different location, and one where location shifts without the group becoming more uniform |
| Validity conditions (declared settings, no attribution when more than one setting changed, duplicates counted once, fixed baseline, per prompt) | Defensible as a design contribution if framed as requirements derived from model-comparison practice, and if one case shows a misleading conclusion the system prevents |
| Image traceability | A requirement shared with ViBEx and Varif.ai. Not a claim of novelty |
| Human-checked aspects | Necessary for rigor, and CHI 2026 shows why. Not a claim of novelty |
| t-SNE image space | Standard. Keep it as a tool for finding images; claim nothing for it |

## What the paper must do for the delta to carry
1. **Related work:** add GROVE (the problem framing), the attribute-conditional benchmark (the closest per-attribute scoring), and DyEval or Vipera (T2I visual analytics). Make room within the 20-reference limit by moving CADS or PrompTHis into a sidebar.
2. **A "why not a score" figure:** two groups with similar Vendi or per-attribute diversity whose defaults differ in location, using real data (e.g. SDXL-Turbo vs klein on "city street").
3. **An attribution case:** a comparison that changes two settings at once and leads to a wrong conclusion, next to a one-factor comparison that gives the correct one.
4. **Per-prompt reversal:** keep the house/kitchen composition reversal as evidence that pooled scores hide structure.
5. **Expert tasks:** add one task that a score table cannot answer ("Are these two settings equally uniform but on different things?"). Optionally, give the same task with a score table as a light baseline.
6. **Name the problem as a VIS problem:** cite DefaultShift as the score-based audit, and present the system as its visual, open-vocabulary, image-checked counterpart.

## Do new models matter?
Yes, for credibility; less for novelty. Only small or distilled models at 512–768 px would invite the objection that "defaults are an artifact of old or small models."
- **FLUX.2 [dev]** completes a one-family ladder (dev → klein-base → klein) along which, where possible, only one factor changes at a time (size, distillation, guidance). This ladder is the cleanest demonstration of RQ2.
- **Qwen-Image** adds a different family with an LLM text encoder at mainstream scale, which answers the question of representativeness.
- Suggested design: per model, its recommended default setting plus one guidance variation; the same 6 prompts; 16 seeds; record every setting in the group metadata so each designed comparison pair differs in exactly one factor.
