#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

PYTORCH_REQUIREMENTS="${PYTORCH_REQUIREMENTS:-requirements-cu121.txt}"

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
