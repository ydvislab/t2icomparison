#!/usr/bin/env bash
# Run ON THE GPU SERVER, inside tmux, after `source ops/env.sh` in the project folder.
# Generates the anchor pilot for the given reference groups, scores the images and analyses them.
# Usage: experiments/model_study/anchors/run_pilot.sh [G08_klein4b] [G09_qwen_image_cfg4]
#        (default: both groups; give one group to run it alone, e.g. only G08 while the study still needs the GPU)
# Set DRY_RUN=1 to print the commands without running them.
set -euo pipefail
: "${T2IC_DATA:?T2IC_DATA is not set: run 'source ops/env.sh' in the project folder first}"
GROUPS_TO_RUN=("$@")
[ ${#GROUPS_TO_RUN[@]} -eq 0 ] && GROUPS_TO_RUN=(G08_klein4b G09_qwen_image_cfg4)
MS="$(cd "$(dirname "$0")/.." && pwd)"       # experiments/model_study
REPO="$(cd "$MS/../.." && pwd)"
run() { echo "+ $*"; [ "${DRY_RUN:-0}" = 1 ] || "$@"; }

nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv || true
for g in "${GROUPS_TO_RUN[@]}"; do
  run python "$MS/open/gen.py" "$g" --jobset anchor_pilot --batch 4
done
dirs=()
for g in G08_klein4b G09_qwen_image_cfg4; do
  [ -f "$T2IC_DATA/model_study/anchors_pilot/$g/meta.csv" ] && dirs+=("$T2IC_DATA/model_study/anchors_pilot/$g")
  # score the study images of the same group too, if that group has finished, so that x can be computed
  [ -f "$T2IC_DATA/model_study/open/$g/meta.csv" ] && dirs+=("$T2IC_DATA/model_study/open/$g")
done
[ "${DRY_RUN:-0}" = 1 ] && dirs+=("<pilot and study dirs found at run time>")
[ ${#dirs[@]} -gt 0 ] && run python "$REPO/aspects/score.py" "${dirs[@]}"
run python "$MS/anchors/analyze_pilot.py"
echo "done: results in $REPO/results/anchors_pilot/, contact sheets in $T2IC_DATA/model_study/anchors_pilot/sheets/"
