#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
DATA_ROOT="${DATA_ROOT:-$HOME/data}"
DATASET="${1:-sleepedf}"

python -m n1_uncertainty.inspect_data --data-root "$DATA_ROOT" --dataset "$DATASET"
