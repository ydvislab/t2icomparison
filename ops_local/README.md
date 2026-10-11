# Local helper scripts for the GPU server

Run these on the computer that can reach the GPU server (host alias `h200` in `~/.ssh/config`; another alias can be set with `T2IC_HOST`). Server login details never go into this repository. Set the project folder on the server once per terminal:

```bash
export T2IC_REMOTE=<project folder on the server>
```

| Script | What it does |
|---|---|
| `sync_up.sh` | Pulls this repository from GitHub and copies `experiments/`, `aspects/`, `annotation/`, `system/` and `docs/` to `$T2IC_REMOTE/code/` (the server cannot reach GitHub) |
| `fetch_anchor_pilot.sh` | Copies the anchor-pilot tables to `results/anchors_pilot/` and the contact sheets to the local `$T2IC_DATA` |

Server-side steps are in `docs/RUNBOOK.md` §5 and, for the anchor pilot, `experiments/model_study/anchors/README.md`.
