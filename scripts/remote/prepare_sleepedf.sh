#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
DATA_ROOT="${DATA_ROOT:-$HOME/data}"
RAW_DIR="${RAW_DIR:-}"
OUTPUT="${OUTPUT:-$DATA_ROOT/sleepedf/preprocessed.npz}"
CHANNEL="${CHANNEL:-Fpz-Cz}"
MAX_PAIRS="${MAX_PAIRS:-}"

ARGS=(--data-root "$DATA_ROOT" --output "$OUTPUT" --channel "$CHANNEL")
if [[ -n "$RAW_DIR" ]]; then
  ARGS+=(--raw-dir "$RAW_DIR")
fi
if [[ -n "$MAX_PAIRS" ]]; then
  ARGS+=(--max-pairs "$MAX_PAIRS")
fi

python -m n1_uncertainty.prepare_sleepedf "${ARGS[@]}"
