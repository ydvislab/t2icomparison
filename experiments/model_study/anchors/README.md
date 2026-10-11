# Calibration anchors

Reference-prompt calibration for the aspect scale (`docs/RESEARCH_PROPOSAL.md` §4.2). For each subject and aspect, a reference model is asked explicitly for each pole ("a city street, in warm golden light" / "a city street, in cool blue light"). The median scores of the two request sets, L and R, define the calibrated location x = (median − L) / (R − L) of any group's default images for that subject and aspect. 0 and 1 are request-conditioned reference points in score units, not physical endpoints, and values outside [0, 1] are kept.

## Pilot (decided 2026-10-11)
Purpose: choose the phrasing of the full anchor set on evidence and check that the anchors are usable before the full run.

| | |
|---|---|
| Aspects | `light` (cool blue ↔ warm golden light), `shot` (extreme close-up ↔ wide shot) |
| Subjects | one per category: a doctor, a dog, a cup of coffee, a kitchen, a city street, a market |
| Phrasings | 3 per pole (`anchors.py`); phrasing 0 repeats the CLIP pole text, phrasings 1–2 use other words |
| Reference models | G08 `FLUX.2 klein 4B` and G09 `Qwen-Image-2512, true CFG 4`, recommended settings |
| Seeds | 8 per prompt, paired within a subject; disjoint from the study seeds |
| Images | 576 per reference model, 1,152 in total |

### What the pilot decides
For each aspect, a phrasing is usable if, for both reference models:
1. **Separation:** AUC ≥ 0.9 in every subject, and the 90% interval of the gap R − L excludes 0;
2. **Side effects:** the median off-target |AUC − 0.5| is below 0.3 (the request does not mainly change another aspect);
3. **Stability:** if the default images are scored, the calibrated default position x changes by less than 0.15 across phrasings (the practical margin in the proposal);
4. **Fidelity:** the contact sheets show the requested pole and the subject is preserved (checked by eye; human check round 2 covers it formally).

Among usable phrasings, prefer one that does not repeat the CLIP pole text. If no phrasing passes for an aspect, that aspect is not calibrated and is dropped or reported uncalibrated. The thresholds above are fixed before the pilot is run.

### Steps (copy and run)
Run on the computer that can reach the GPU server (host alias `h200` in `~/.ssh/config`). Set once per terminal the project folder on the server, i.e. the folder that holds `code/`, `data/`, `ops/` and `logs/`:

```bash
export T2IC_REMOTE=<project folder on the server>
```

**1. Send the latest code to the server** (from the root of this repository; it pulls from GitHub first, because the server cannot reach GitHub):

```bash
ops_local/sync_up.sh
```

**2. Log in and open a tmux session** (the run continues if the connection drops; reattach with `tmux attach -t anchors`):

```bash
ssh h200
```

```bash
tmux new -s anchors
```

**3. On the server: load the environment and run the pilot.** `run_pilot.sh` generates, scores (including the study images of G08 and G09 if they are finished) and analyses. It is resumable: rerunning skips finished images.

```bash
cd $T2IC_REMOTE && source ops/env.sh && cd code
```

If the study generation still needs the GPU, run klein 4B first (4 steps, quick):

```bash
experiments/model_study/anchors/run_pilot.sh G08_klein4b
```

Then Qwen-Image (50 steps at 1328², much slower) when GPU 0 is free; check memory with `nvidia-smi` first:

```bash
experiments/model_study/anchors/run_pilot.sh G09_qwen_image_cfg4
```

Or both in one go when the GPU is free:

```bash
experiments/model_study/anchors/run_pilot.sh
```

**4. Back on the local computer: fetch the results** (tables to `results/anchors_pilot/`, contact sheets to `$T2IC_DATA/model_study/anchors_pilot/sheets/`):

```bash
ops_local/fetch_anchor_pilot.sh
```

**5. Commit the tables** so the analysis can continue on any machine (the contact sheets stay local):

```bash
git add results/anchors_pilot && git commit -m "Anchor pilot results" && git push
```

`run_pilot.sh` with `DRY_RUN=1` prints the commands without running them. The individual commands it runs are `open/gen.py <group> --jobset anchor_pilot --batch 4`, `aspects/score.py <dirs>` and `anchors/analyze_pilot.py`.

### Local smoke test (2026-10-11)
`gen.py` with `--jobset anchor_pilot --seeds 1 --limit 24 --batch 1 --device mps` on G08 (klein 4B), then `score.py` and `analyze_pilot.py`, ran end to end on a Mac (about 80 s per 1024² image on MPS). Those images are only a code test and are not used. One seed per prompt is too few for the statistics (every AUC is 0 or 1), but the contact sheet already showed that the close-up phrasing "{s}, filling the whole frame" produced a medium shot, which is the kind of failure the pilot is meant to catch.
