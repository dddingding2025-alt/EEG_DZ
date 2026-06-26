from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect latest lightweight run status.")
    parser.add_argument("--runs-root", default="experiments/transition_uncertainty_guided_n1/runs")
    parser.add_argument("--stale-minutes", type=float, default=60.0)
    args = parser.parse_args()

    latest_path = Path(args.runs_root) / "latest.json"
    if not latest_path.exists():
        print("decision=no_results reason=latest.json_missing")
        return 0
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    state = latest.get("state", "unknown")
    last_update = latest.get("last_update_time")
    stale = False
    if last_update:
        dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
        stale = (datetime.now(timezone.utc) - dt).total_seconds() > args.stale_minutes * 60
    if state == "running" and stale:
        print(f"decision=check_server state={state} run_id={latest.get('run_id')} stale=true")
    elif state == "failed":
        print(f"decision=fix_code state=failed run_id={latest.get('run_id')} error={latest.get('last_error', '')}")
    elif state == "completed":
        print(f"decision=analyze_results state=completed run_id={latest.get('run_id')}")
    else:
        print(f"decision=wait state={state} run_id={latest.get('run_id')} stale={str(stale).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
