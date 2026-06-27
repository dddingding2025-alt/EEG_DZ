#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ -z "${PYTORCH_REQUIREMENTS:-}" ]]; then
  GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
  if [[ "$GPU_NAME" =~ RTX[[:space:]]50|5060|5070|5080|5090|Blackwell ]]; then
    PYTORCH_REQUIREMENTS="requirements-cu128.txt"
  else
    PYTORCH_REQUIREMENTS="requirements-cu121.txt"
  fi
fi

echo "Using PyTorch requirements: $PYTORCH_REQUIREMENTS"

python -m pip install --upgrade pip
python -m pip install -r "$PYTORCH_REQUIREMENTS"

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("torch cuda runtime:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("cuda device:", torch.cuda.get_device_name(0))
else:
    print("warning: torch installed, but CUDA is not available to PyTorch")
PY
