from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
from pathlib import Path

import numpy as np

from .config import load_config
from .metrics import compute_metrics
from .status import append_metrics, write_analysis, write_status, write_summary
from .transitions import transition_mask


def main() -> int:
    parser = argparse.ArgumentParser(description="Run N1 uncertainty experiments or smoke checks.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_id = args.resume or args.run_id or make_run_id(cfg.get("name", "run"))
    runs_root = Path(cfg.get("runs_root", "experiments/transition_uncertainty_guided_n1/runs"))
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    status = {
        "run_id": run_id,
        "git_commit": git_commit(),
        "hostname": socket.gethostname(),
        "cuda_available": cuda_available(),
        "stage": cfg.get("stage", "unknown"),
        "state": "running",
        "epoch": 0,
        "best_n1_f1": 0.0,
        "best_transition_n1_f1": 0.0,
        "last_error": "",
    }
    write_status(run_dir, status)

    try:
        if args.smoke or cfg.get("data", {}).get("synthetic", False):
            summary = run_synthetic(cfg, run_dir)
        else:
            summary = run_npz_training(cfg, run_dir)
        status.update(
            state="completed",
            epoch=int(summary.get("epoch", 0)),
            best_n1_f1=float(summary.get("best_n1_f1", 0.0)),
            best_transition_n1_f1=float(summary.get("best_transition_n1_f1", 0.0)),
        )
        write_status(run_dir, status)
        write_summary(run_dir, summary)
        write_analysis(run_dir, f"Run {run_id}", summary)
        return 0
    except Exception as exc:  # noqa: BLE001 - status files must capture any failure.
        status.update(state="failed", last_error=f"{type(exc).__name__}: {exc}")
        write_status(run_dir, status)
        raise


def run_synthetic(cfg: dict, run_dir: Path) -> dict:
    rng = np.random.default_rng(int(cfg.get("training", {}).get("seed", 42)))
    y_true = np.asarray([0, 0, 1, 1, 2, 2, 1, 0, 4, 4, 2, 3, 3, 2, 1, 1, 0])
    probs = np.full((len(y_true), 5), 0.05, dtype=float)
    for idx, label in enumerate(y_true):
        probs[idx, label] = 0.8
        if label == 1:
            probs[idx, rng.choice([0, 2])] += 0.1
    probs = probs / probs.sum(axis=1, keepdims=True)
    mask = transition_mask(y_true, k=int(cfg.get("transition", {}).get("k", 2)))
    metrics = compute_metrics(y_true, probs, transition_mask=mask)
    row = {"epoch": 0, "variant": "synthetic_smoke", "split": "test", "loss": 0.0, **metrics}
    append_metrics(run_dir, row)
    return {
        "mode": "synthetic_smoke",
        "epoch": 0,
        "best_n1_f1": metrics["n1_f1"],
        "best_transition_n1_f1": metrics["transition_n1_f1"],
        "metrics": metrics,
        "conclusion": "smoke test completed",
    }


def run_npz_training(cfg: dict, run_dir: Path) -> dict:
    # This is an intentionally small baseline trainer. It expects preprocessed NPZ
    # arrays and keeps heavy raw EDF conversion outside the first automation step.
    try:
        from .training import run_training_variants
    except ImportError as exc:  # pragma: no cover - depends on server torch install.
        raise RuntimeError("training requires torch; run `pip install -r requirements.txt`") from exc

    data_path = Path(cfg.get("data", {}).get("path", ""))
    if not data_path.exists():
        raise FileNotFoundError(
            f"preprocessed dataset not found: {data_path}. Expected NPZ with x, y, subject arrays."
        )
    return run_training_variants(cfg, data_path=data_path, run_dir=run_dir)


def make_run_id(name: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in name.lower()).strip("-")
    from datetime import datetime

    return f"{safe}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def cuda_available() -> bool:
    if os.environ.get("CUDA_VISIBLE_DEVICES") == "":
        return False
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
