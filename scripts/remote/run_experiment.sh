#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"

CONFIG_NAME=""
RESUME_ID=""
SMOKE_FLAG=""
GPU_ID="${GPU_ID:-}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/remote/run_experiment.sh [--gpu GPU_ID] <baseline_sleepedf|softlabel_sleepedf|replicate_isruc|tgcm_sleepedf|--smoke>
  bash scripts/remote/run_experiment.sh [--gpu GPU_ID] --resume <run_id> [config_name]

Examples:
  bash scripts/remote/run_experiment.sh --gpu 0 baseline_sleepedf
  GPU_ID=1 bash scripts/remote/run_experiment.sh softlabel_sleepedf
  CUDA_VISIBLE_DEVICES=2 bash scripts/remote/run_experiment.sh --smoke
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpu|--cuda-device)
      GPU_ID="${2:?missing gpu id for $1}"
      shift 2
      ;;
    --cpu)
      GPU_ID=""
      export CUDA_VISIBLE_DEVICES=""
      shift
      ;;
    --resume)
      RESUME_ID="${2:?missing run_id for --resume}"
      shift 2
      if [[ $# -gt 0 && "${1:-}" != --* ]]; then
        CONFIG_NAME="$1"
        shift
      fi
      ;;
    --smoke)
      CONFIG_NAME="smoke_synthetic"
      SMOKE_FLAG="--smoke"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -n "$CONFIG_NAME" ]]; then
        echo "Unexpected argument: $1"
        usage
        exit 2
      fi
      CONFIG_NAME="$1"
      shift
      ;;
  esac
done

if [[ -z "$CONFIG_NAME" && -n "$RESUME_ID" ]]; then
  CONFIG_NAME="baseline_sleepedf"
fi

if [[ -z "$CONFIG_NAME" ]]; then
  usage
  exit 2
fi

if [[ -n "$GPU_ID" ]]; then
  export CUDA_VISIBLE_DEVICES="$GPU_ID"
fi

if [[ "${CUDA_VISIBLE_DEVICES+x}" == "x" ]]; then
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-<empty; CPU mode>}"
else
  echo "CUDA_VISIBLE_DEVICES is not set; PyTorch may use the default visible GPU set."
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
