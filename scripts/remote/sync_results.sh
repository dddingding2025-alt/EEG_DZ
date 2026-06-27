#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

BRANCH="${BRANCH:-codex/n1-label-uncertainty}"
RUNS_DIR="experiments/transition_uncertainty_guided_n1/runs"

USER_NAME="$(git config --get user.name || true)"
USER_EMAIL="$(git config --get user.email || true)"
if [[ -z "$USER_NAME" || -z "$USER_EMAIL" ]]; then
  cat <<'EOF'
Git commit identity is not configured on this server.

Run these once inside the EEG_DZ repository:

  git config user.name "remote-runner"
  git config user.email "remote-runner@example.com"

This only sets the commit author for result-sync commits. If push still fails
after that, configure GitHub authentication with SSH or `gh auth login`.
EOF
  exit 2
fi

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
