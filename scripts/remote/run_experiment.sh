#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

CONFIG_NAME="${1:-}"
RESUME_ID=""
SMOKE_FLAG=""

if [[ "$CONFIG_NAME" == "--resume" ]]; then
  RESUME_ID="${2:?missing run_id for --resume}"
  CONFIG_NAME="${3:-baseline_sleepedf}"
fi

if [[ "$CONFIG_NAME" == "--smoke" ]]; then
  CONFIG_NAME="smoke_synthetic"
  SMOKE_FLAG="--smoke"
fi

if [[ -z "$CONFIG_NAME" ]]; then
  echo "Usage: bash scripts/remote/run_experiment.sh <baseline_sleepedf|softlabel_sleepedf|replicate_isruc|tgcm_sleepedf|--smoke>"
  echo "       bash scripts/remote/run_experiment.sh --resume <run_id> [config_name]"
  exit 2
fi

CONFIG_PATH="experiments/transition_uncertainty_guided_n1/configs/${CONFIG_NAME}.yaml"
if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Config not found: $CONFIG_PATH"
  exit 2
fi

mkdir -p experiments/transition_uncertainty_guided_n1/runs

if [[ -n "$RESUME_ID" ]]; then
  python -m n1_uncertainty.run_experiment --config "$CONFIG_PATH" --resume "$RESUME_ID" $SMOKE_FLAG
else
  python -m n1_uncertainty.run_experiment --config "$CONFIG_PATH" $SMOKE_FLAG
fi
