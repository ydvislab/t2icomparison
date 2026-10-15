#!/bin/bash
# Q4 generation chain on one GPU (PREREG.md). Run inside tmux after `source ops/env.sh`; stops at the first error.
set -euo pipefail
cd "$(dirname "$0")"
L=$T2IC_DATA/llm_study
[ -f $L/rewrites_mistral.csv ] || python rewrite.py mistral
[ -f $L/rewrites_qwen.csv ] || python rewrite.py qwen
for c in mistral mistral_fixed qwen; do python gen_rewritten.py G08_klein4b $c; done
python ../../aspects/score.py $L/G08_klein4b__mistral $L/G08_klein4b__mistral_fixed $L/G08_klein4b__qwen
python gen_rewritten.py G05_flux2_dev mistral
python ../../aspects/score.py $L/G05_flux2_dev__mistral
echo Q4 chain done
