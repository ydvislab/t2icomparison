#!/bin/zsh
# Remaining local pipeline: label klein + turbo, wait for SD1.5 generation, then embed + label SD1.5.
cd "$(dirname "$0")"
D=${T2IC_DATA:-~/va4ext}; PY=${T2IC_PY:-$D/env/bin/python}; H=$D/hidden_or_lost
for m in klein4b sdxl_turbo; do $PY label.py $m > $H/label_$m.log 2>&1; echo "label $m exit $?"; done
while pgrep -f "gen.py sd15" >/dev/null; do sleep 15; done
echo "sd15 gen: $(tr '\r' '\n' < $H/gen_sd15.log | grep -E 'done|Traceback' | tail -1)"
$PY embed.py sd15 > $H/embed_sd15.log 2>&1; echo "embed sd15 exit $?"
$PY label.py sd15 > $H/label_sd15.log 2>&1; echo "label sd15 exit $?"
