#!/bin/bash
# wait for the FLUX.2 dev rewrite generation (tmux q4flux) to finish, then run the remaining Q5/Q6 queries
source /mnt/data/yd/t2icomparison/ops/env.sh
while tmux has-session -t q4flux 2>/dev/null; do sleep 120; done
cd experiments/llm_study
python vlm_describe.py qwen --contrasts rw_klein,rw_flux
python vlm_describe.py mistral
echo Q5 after-chain done
