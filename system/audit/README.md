# Audit tool (rev5)

One screen, adapting to the window (tested at 1280×760, 1440×900 and 1920×1080): a **main view** (the configuration map, top left, largest) and linked **auxiliary views**: the subject × configuration matrix (top middle), the five contrast scatters stacked on the right, the distributions of one subject (bottom middle) and the image strips (bottom left). The aspect buttons in the header switch every view.

Visual audit of appearance defaults for the model study (`docs/RESEARCH_PROPOSAL.md` §6). It replaces the rev4.1 comparison system in `system/` (kept as design history) for the three audit tasks:
- **T1, displacement vs concentration:** for a contrast A → B, does each subject's output distribution move, tighten or widen?
- **T2, pooled vs per subject:** does the median over subjects hold for every subject?
- **T3, trace to images:** every reading leads back to the images, and the tool shows when a contrast changes more than one declared setting.

## Build and run
On the GPU server, after `source ops/env.sh`:
```bash
python system/audit/build.py
```
It writes `$T2IC_DATA/audit_tool/` (page, `data.js`, 192 px thumbnails). Serve that folder with any static server:
```bash
cd $T2IC_DATA/audit_tool && python -m http.server 8772 --bind 127.0.0.1
```
To use it from another computer, open an SSH tunnel and browse to http://127.0.0.1:8772/:
```bash
ssh -N -L 8772:127.0.0.1:8772 h200
```
Rebuild whenever more groups have been generated and CLIP-scored. The scale is marked provisional (amber dot, top right) until all 12 open configurations are included.

## Views
| View | Encoding | Interaction |
|---|---|---|
| **Main view: configuration map** and auxiliary **matrix** | **Configuration map** for the chosen aspect: each configuration is a point (colour = family) at its typical location (x, median over subjects of the distance from the subjects' cross-configuration median, in scale units) and spread (y, median IQR in scale units). Arrows are the designed contrasts: solid = guidance only, dashed = package (several settings change). The axes cover every configuration and 80% of the per-subject positions; per-subject positions beyond that are drawn at the edge as triangles. **Subject × configuration matrix**: colour = location of that configuration for that subject (diverging between the two poles); a row whose colour flips is a subject-dependent default | aspect buttons; hover a configuration to see its subjects in the map and its matrix column; hover a matrix row (or cell) to see where every configuration puts that subject, linked to each configuration's typical position; click a point, cell or arrow to set the A → B pair for the levels below |
| Header | A and B selectors with their colours (blue, orange); chips for every declared setting that differs; ⚠ n when more than one differs (not attributable to one setting) | swap A and B |
| Auxiliary: five contrast scatters (right column) | one dot per subject: x = location shift Δ = (median_B − median_A) / s_aspect, y = log IQR ratio (spread); shaded bands = frozen practical margins (\|Δ\| < 0.5, ratio within 1/1.5–1.5); diamond = median over subjects with a hierarchical bootstrap 90% interval | hover a dot to highlight the same subject in all five plots and preview it below, click to pin; hover the diamond for the pooled estimate and how many subjects moved each way |
| Auxiliary: distributions of one subject | smooth kernel density curves of A and B per aspect on a common axis (scale units, 0 = A's median); rug ticks are the individual images | click a row to choose the aspect; hover a tick to highlight the image |
| Auxiliary: image strips | all images of A and B for the subject, sorted by the chosen aspect from the left pole to the right pole | hover an image to highlight its tick and enlarge it; the image with the same seed in the other group is highlighted too (seeds are shared by all groups) |

The page is written with D3 v7 (selections, data joins, scales, axes, areas, transitions); `build.py` (Python) only prepares the data. Numbers appear only in tooltips. Intervals are 90% bootstrap intervals with 400 resamples, paired by seed when A and B share the same weights. The display labels ("displaced", "same place") follow the frozen margins; the primary analysis is done separately in a script, not in the tool.
