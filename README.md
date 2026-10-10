# t2icomparison

Visual comparison of *generation defaults* across text-to-image models and generation settings.

When a prompt leaves an attribute unspecified (lighting, framing, palette, medium), the model decides it, and newer models increasingly make the same decision every time. A single diversity score says *how much* outputs have converged, but not *on what*. This project provides a method and a visual comparison system that let model developers and evaluators:

- compare repeated outputs of several models or generation settings on a shared set of human-checked image aspects;
- see separately *where* a group concentrates (location) and *how tightly* (spread);
- trace every reading back to the images, with each group's generation settings always in view.

## Repository layout
| Path | Contents |
|---|---|
| `experiments/` | Generation and measurement code: background studies and the model study (`experiments/model_study/`) |
| `aspects/` | Aspect measurement: CLIP features and bipolar aspect scores |
| `system/` | The comparison system and its data build |
| `annotation/` | Human check of the aspects: protocol, guide, labelling page, analysis |
| `results/` | Figures and screenshots |
| `docs/` | Project notes; `docs/RUNBOOK.md` describes how to reproduce everything |

## Quick start (with existing data)
Images, model weights and intermediate data are not stored in git. They live in a data directory, `~/va4ext` by default, configurable with the `T2IC_DATA` environment variable.

```bash
pip install -r requirements.txt
python3 system/build.py
cd "${T2IC_DATA:-$HOME/va4ext}/proto3" && python3 -m http.server 8771 --bind 127.0.0.1
```

Then open http://127.0.0.1:8771/index.html. To generate the data from scratch, follow `docs/RUNBOOK.md`.

## License
No license has been chosen yet; all rights reserved. Generated images are not included. Each model used is subject to its own license.
