# External review of the audit-tool interface, rev12 (2026-10-25)

**Reviewer:** Codex, **gpt-6-astra, reasoning effort low** (the owner's standing choice from 2026-10-25), read-only. It was prompted as a strict adversarial reviewer of the interface design only.
- **Prompt:** `.aris/review-requests/interface_rev12_2026-10-25.md` (not tracked).
- **Read:** `system/audit/INTERFACE.md`, `index.html`, `README.md`, `baseline.html` and ten screenshots (synthetic scores).
- **Earlier attempt:** gpt-6-astra ultra failed the same day on the account's usage limit (trace in `.aris/traces/research-review/2026-10-25_run01/`).

## Verdict
| Design soundness | Multi-configuration support | Encoding consistency | Linking | Scalability | Visual clarity |
|---|---|---|---|---|---|
| 4 | 5 | 4 | 4 | 3 | 4 |

"Rev12 remains a pairwise audit workflow with set-wide displays attached; inconsistent reference semantics, incomplete linking, and collapsing layouts prevent multi-configuration comparison from being first-class."

## Problems, ranked by the reviewer (executor's check in brackets)
1. **Critical: views use different origins after the reference changes.** The parallel coordinates and the image lanes subtract the median of the first set member, not of the reference. The set distributions use the reference. [Confirmed in code: `drawParallel` and `drawLanes` use `rows[0]`.]
2. **Validity is tied to the reference–focus pair.**
   - E fades a whole card when the focus pair is not validated, even for members that are validated.
   - The set distributions filter retained aspects, not member validity.
   - C carries one validity mark for all lanes.
   - Missing validity metadata counts as validated.
3. **T5 is not a complete workflow.**
   - Sorting, reversal stepping, subject brushing and the settings chips stay pairwise.
   - Brushed-subject summaries do not reach the other members' diamonds.
   - Set rows are interleaved with the designed contrasts in the overview.
   - Saved trails omit the set, its order, selections, mode and margins.
4. **K = 6 exceeds the layout.** The reviewer estimates these limits:
   - **Header:** chips do not wrap.
   - **Matrix:** five shift columns plus twelve configuration columns.
   - **Shift columns:** ±2, clamped without overflow marks.
   - **Lanes:** thumbnails near the 16 px floor.
   - **Distributions:** about 9 px rows.
   - **Parallel coordinates:** up to 160 segments.
   - **Small multiples:** panels move when K changes.
   - **Scatters:** labels collide.
5. **"Identity by position" is applied inconsistently.**
   - In E and on the map, position encodes a measurement, so the label carries identity, and the labels have no collision handling.
   - Matrix columns follow a fixed order, while shift columns follow set order.
   - Rewritten configurations have no matrix column.
6. **Linking is incomplete.**
   - The trail seed is not linked to C or D.
   - Hovering another subject clears the seed selection.
   - C's range brush disappears for K > 2.
   - Seed selections do not show in E.
   - Distribution rows cannot make a member the focus.
7. **Correspondence changes with K.** At K = 2, configurations with different starting noise are matched by rank. At K > 2, the parallel coordinates join seed IDs and dash them. The ▶ animation follows seed IDs in both cases.
8. **The trail can detach a statement from its subject.** A selected statement stays while the pair matches, even after the subject changes. Margin changes do not redraw the trail.
9. **The rewrite view does not require the other side to be the rewrite's own base.**
10. **The indispensability and non-redundancy claims contradict the interface.**
    - The trail redraws a scatter and the subject distributions.
    - "Only view of all aspects" is false next to E and ▦.
    - Eight modes give 16 A × D combinations.
11. **Semantics are hidden, overloaded or clipped.**
    - No numeric scales outside figure mode.
    - E's pole words describe appearance, while its x axis is a change.
    - The overview glyph has no persistent key.
    - Opacity has four meanings.
    - Statement verdicts depend on colour alone.
    - Zoomed-out configurations are not turned into edge triangles.
12. **The evaluation argument is unsupported.**
    - "Indispensable", "every view compares a set" and six-member scalability are not demonstrated.
    - The baseline has no set operations, so a comparison would confound set capability with visual design.
    - The baseline truncates rewrite text to eight entries.

## Reviewer's exceptions (keep pairwise) and cuts
- **Keep pairwise:**
  - E's per-subject detail scatter, next to a set-wide pooled summary;
  - map contours for two labelled members;
  - a statement's trail, with its scope locked;
  - the original-versus-rewrite view, bound to the rewrite's base.
- **Make set-aware:**
  - member summaries;
  - validity;
  - settings differences;
  - cohort summaries;
  - reversal navigation;
  - seed selection;
  - saved findings.
- **Cuts:**
  - the mini scatter and distributions inside the trail;
  - the ▶ animation, until correspondence is consistent;
  - rewrite controls when no rewrite is selected;
  - unselected configuration columns in B's default set layout;
  - the absolute wording of principles 2 and 4 and "every view compares a set".
