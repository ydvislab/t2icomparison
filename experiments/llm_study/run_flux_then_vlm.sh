#!/bin/bash
# FLUX.2 dev rewrite images (alone on the shared GPU), scoring, then the remaining VLM queries (one at a time)
source /mnt/data/yd/t2icomparison/ops/env.sh
cd experiments/llm_study
python gen_rewritten.py G05_flux2_dev mistral --two-stage || exit 1
python ../../aspects/score.py $T2IC_DATA/llm_study/G05_flux2_dev__mistral || exit 1
python vlm_describe.py qwen --contrasts rw_flux,null_klein4b,null_sdxl
python vlm_describe.py mistral --contrasts rw_flux,null_klein4b,null_sdxl
echo FLUX and VLM chain done
