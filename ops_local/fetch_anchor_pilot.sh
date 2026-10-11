#!/usr/bin/env bash
# Run on the local machine after the anchor pilot finished on the server.
# Copies the pilot result tables into results/anchors_pilot/ (tracked) and the contact sheets into
# $T2IC_DATA/model_study/anchors_pilot/sheets/ (local data folder, not tracked).
# Usage: T2IC_REMOTE=<project folder on the server> ops_local/fetch_anchor_pilot.sh
set -euo pipefail
: "${T2IC_REMOTE:?set T2IC_REMOTE to the project folder on the server}"
HOST="${T2IC_HOST:-h200}"
LOCAL_DATA="${T2IC_DATA:-$HOME/va4ext}"
cd "$(dirname "$0")/.."
mkdir -p results/anchors_pilot "$LOCAL_DATA/model_study/anchors_pilot/sheets"
scp -q "$HOST:$T2IC_REMOTE/code/results/anchors_pilot/*.csv" results/anchors_pilot/
scp -q "$HOST:$T2IC_REMOTE/data/model_study/anchors_pilot/sheets/*.jpg" "$LOCAL_DATA/model_study/anchors_pilot/sheets/"
ls results/anchors_pilot "$LOCAL_DATA/model_study/anchors_pilot/sheets"
echo "next: git add results/anchors_pilot && git commit -m 'Anchor pilot results' && git push"
