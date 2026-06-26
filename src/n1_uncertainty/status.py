from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_status(run_dir: str | Path, status: dict[str, Any]) -> None:
    path = Path(run_dir)
    status = dict(status)
    status["last_update_time"] = utc_now()
    write_json(path / "status.json", status)
    latest = path.parent / "latest.json"
    write_json(latest, {"run_id": path.name, "status_path": str(path / "status.json"), **status})


def append_metrics(run_dir: str | Path, row: dict[str, Any]) -> None:
    path = Path(run_dir) / "metrics.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    fields = [
        "epoch",
        "variant",
        "split",
        "loss",
        "accuracy",
        "macro_f1",
        "kappa",
        "n1_f1",
        "n1_precision",
        "n1_recall",
        "transition_n1_f1",
        "ece",
        "n1_overprediction_rate",
    ]
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def write_summary(run_dir: str | Path, summary: dict[str, Any]) -> None:
    write_json(Path(run_dir) / "summary.json", summary)


def write_analysis(run_dir: str | Path, title: str, summary: dict[str, Any]) -> None:
    lines = [f"# {title}", "", "## Summary", ""]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    Path(run_dir, "analysis.md").write_text("\n".join(lines), encoding="utf-8")
