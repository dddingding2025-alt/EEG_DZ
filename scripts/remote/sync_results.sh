#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${BRANCH:-codex/n1-label-uncertainty}"
RUNS_DIR="experiments/transition_uncertainty_guided_n1/runs"

git add "$RUNS_DIR" || true
if git diff --cached --quiet; then
  echo "No result changes to sync."
  exit 0
fi

RUN_ID="$(python - <<'PY'
import json
from pathlib import Path
p = Path("experiments/transition_uncertainty_guided_n1/runs/latest.json")
print(json.loads(p.read_text(encoding="utf-8")).get("run_id", "unknown") if p.exists() else "unknown")
PY
)"

git commit -m "research(results): sync ${RUN_ID}"
git push origin "$BRANCH"
