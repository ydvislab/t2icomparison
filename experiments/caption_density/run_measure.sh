#!/bin/zsh
# DINOv2 Vendi + VLM dimensions for every generated condition (reuses ../hidden_or_lost scripts via HOL_DATA).
cd "$(dirname "$0")/../hidden_or_lost"
D=${T2IC_DATA:-~/va4ext}
export HOL_DATA=$D/caption_density
PY=${T2IC_PY:-$D/env/bin/python}
for c in "$@"; do
  $PY embed.py $c > $HOL_DATA/embed_$c.log 2>&1; echo "embed $c exit $?"
  $PY label.py $c > $HOL_DATA/label_$c.log 2>&1; echo "label $c exit $?"
done
