# Expert study: session materials (fixed 2026-10-19, before any session)

Protocol: `EXPERT_STUDY.md` (sections 1–8 and the T4 addendum).
- **Tool:** `system/audit/index.html` (rev6).
- **Baseline:** `system/audit/baseline.html`. It contains the same numbers, images, settings, validation status, rewrites and VLM statements, but no visual encoding beyond tables and an unsorted grid, and no linking.

The expected answers below come from the frozen analyses. They are fixed before the first session and are not shown to the experts.

## 1. Cases and expected answers
| Task | Question to the expert | Case a | Case b | Expected answer (source) |
|---|---|---|---|---|
| **T1** displacement vs concentration | "When klein-base 4B guidance goes from 1 to 4, does [aspect] move, tighten, or both? Show the images that convince you." | saturation | medium | **a:** moves toward vivid (+0.65) **and** tightens (×0.51). **b:** tightens (×0.53) **in place** (−0.03). (`results/q1/`) |
| **T2** pooled vs per subject | "Overall, does [contrast] change [aspect]? Is that true for every subject? Name subjects that go each way." | SDXL → SDXL-Turbo, saturation | SD 1.5 → klein-base 4B CFG 4, saturation | **a:** no clear pooled change, but opposite shifts: 9 subjects more vivid, 6 more muted. **b:** pooled −0.16, but 6 subjects more vivid and 9 more muted. Correct = says "no pooled change", says "not true for every subject", and names at least one subject per direction. (`results/q3/reversals.csv`, `results/q2/hidden_opposite.csv`) |
| **T3** can this reading be trusted? | "Here is a reading: [claim]. Can it be trusted? Why or why not?" | "Raising Qwen-Image's guidance from 1 to 4 makes its tone more modern." | "Distilling SDXL into SDXL-Turbo makes backgrounds busier for some subjects and plainer for others." | **a:** not trustworthy as stated. Tone is **not validated by people on the Qwen-Image configurations** (round 2), so the measurement cannot support the claim. **b:** the per-subject pattern is real, but it **cannot be attributed to distillation**, because five declared settings differ (checkpoint, scheduler, steps, guidance, resolution). (`annotation/PROTOCOL.md` §7; `docs/PROVENANCE.md`) |
| **T4** verify a language claim | "A VLM looked at 8 images of A and 8 of B and said: [statement]. Is it correct? Show the evidence." | SDXL → Turbo, "a restaurant": *"Set B images include more detailed architectural elements such as arched windows and ornate moldings, which are less prominent in set A."* | SDXL → Turbo, "a car": *"Set B images have a more sepia tone and muted color palette."* | **a:** **incorrect.** The restaurant backgrounds become much plainer (−1.68) and less varied (×0.12). **b:** **correct.** Tone moves toward vintage (+1.44) and saturation toward muted (−1.47). (`results/q5/truth.csv`) |

**Training case** (not scored; one per condition, at most 8 minutes each): klein 4B, original prompt → FLUX.2 rewrite, background, "a kitchen". It shows the image axis, scatter, matrix and statements in the tool, and the tables, grid and texts in the baseline.

## 2. Counterbalancing (five experts)
- Each expert does every task twice: once with the tool and once with the baseline, on different cases.
- "Tool cases" lists the case used with the tool for T1, T2, T3 and T4; the baseline uses the other case of each task.

| Expert | First condition | Tool cases (T1, T2, T3, T4) | Baseline cases |
|---|---|---|---|
| E1 | tool | a, a, a, a | b, b, b, b |
| E2 | baseline | b, b, b, b | a, a, a, a |
| E3 | tool | b, a, b, a | a, b, a, b |
| E4 | baseline | a, b, a, b | b, a, b, a |
| E5 | tool | a, a, b, b | b, b, a, a |

Within a condition, the tasks run in the order T1, T2, T3, T4.

## 3. Session script (about 55 minutes)
1. **Consent and background (3 min):** role, years with generative models, experience with CLIP-based metrics. Record as E1–E5 only.
2. **Training (up to 8 min per condition)** on the training case, directly before that condition's tasks.
3. **Tasks (about 6 min each), with think-aloud.** For each trial, record:
   - the answer;
   - the evidence cited (views, images);
   - confidence (1–5);
   - the time.
4. **Interview (8 min):**
   - Which reading would you have got wrong with the table and grid alone? Why?
   - When did you go to the images, and did that change your answer?
   - Would you trust a VLM's description of how two models differ? What would you need to check?
   - What would you need to audit your own model or setting changes?
   - What in the tool is unclear or misleading?

## 4. Recording sheet
`results/expert_study/sessions.csv` is filled during the sessions. It contains no names; screen recordings stay outside the repository.

```
expert,condition,order,task,case,answer,correct,evidence,confidence,seconds,notes
```

**Correctness rules** (applied after the sessions, by the rules above):
- **T1:** both components right (move yes/no, tighten yes/no).
- **T2:** all three parts (no pooled change; not true for every subject; one subject per direction).
- **T3:** the reason named (not validated; several settings differ).
- **T4:** the right verdict plus evidence on the matching aspect.

## 5. What the owner needs to arrange
- dates for the five sessions (from 2026-10-22);
- the room or video call;
- the tool and the baseline on the session computer: SSH tunnel to the server, port 8772; the tool at `/`, the baseline at `/baseline.html`;
- consent forms under the approved ethics protocol.
