#!/usr/bin/env bash
# Run on the local machine that can reach the GPU server (alias h200 in ~/.ssh/config).
# Copies the code folders of this repository to the server's working copy; the server cannot reach GitHub.
# Usage: T2IC_REMOTE=<project folder on the server> ops_local/sync_up.sh
set -euo pipefail
: "${T2IC_REMOTE:?set T2IC_REMOTE to the project folder on the server (the folder that holds code/, data/, ops/, logs/)}"
HOST="${T2IC_HOST:-h200}"
cd "$(dirname "$0")/.."
git pull --rebase -q || echo "warning: git pull failed; syncing the local state as it is"
tar --exclude='__pycache__' -cf - experiments aspects annotation system docs | ssh "$HOST" "tar -C '$T2IC_REMOTE/code' -xf -"
echo "synced $(git log --oneline -1) to $HOST:$T2IC_REMOTE/code"
