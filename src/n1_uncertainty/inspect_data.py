from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


REQUIRED_NPZ_KEYS = ("x", "y", "subject")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Sleep-EDF/ISRUC data layout for this project.")
    parser.add_argument("--data-root", default=os.environ.get("DATA_ROOT", "~/data"))
    parser.add_argument("--dataset", default="sleepedf", choices=["sleepedf", "isruc"])
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    report = inspect_dataset(Path(args.data_root).expanduser(), args.dataset)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_report(report)
    if args.fail_on_invalid and report["verdict"] != "ready_npz":
        return 1
    return 0


def inspect_dataset(data_root: Path, dataset: str) -> dict[str, Any]:
    candidate_dirs = candidate_dataset_dirs(data_root, dataset)
    existing_dirs = [path for path in candidate_dirs if path.exists()]
    search_root = existing_dirs[0] if existing_dirs else data_root
    npz_candidates = sorted(search_root.rglob("*.npz")) if search_root.exists() else []
    preferred_npz = preferred_npz_path(search_root, dataset)
    edf_files = sorted(search_root.rglob("*.edf")) if search_root.exists() else []
    psg_files = [p for p in edf_files if "psg" in p.name.lower()]
    hyp_files = [p for p in edf_files if "hyp" in p.name.lower() or "hypnogram" in p.name.lower()]

    report: dict[str, Any] = {
        "data_root": str(data_root),
        "dataset": dataset,
        "searched_dir": str(search_root),
        "existing_candidate_dirs": [str(path) for path in existing_dirs],
        "preferred_npz": str(preferred_npz),
        "npz_files": [str(path) for path in npz_candidates[:20]],
        "edf_count": len(edf_files),
        "psg_edf_count": len(psg_files),
        "hypnogram_edf_count": len(hyp_files),
        "sample_edf_files": [str(path) for path in edf_files[:10]],
        "verdict": "missing",
        "messages": [],
    }

    if preferred_npz.exists():
        report.update(inspect_npz(preferred_npz))
        return report
    if npz_candidates:
        report["messages"].append(
            "Found NPZ files, but not the expected preprocessed.npz path. Move or point config to the right file."
        )
        report.update(inspect_npz(npz_candidates[0]))
        if report["verdict"] == "ready_npz":
            report["verdict"] = "npz_at_nonstandard_path"
        return report
    if edf_files:
        report["verdict"] = "raw_edf_needs_conversion"
        report["messages"].append("Raw EDF files detected. Training expects a preprocessed NPZ with x/y/subject arrays.")
        if not psg_files or not hyp_files:
            report["messages"].append("EDF files found, but PSG/Hypnogram pairing is incomplete or file names are unusual.")
        return report
    if not search_root.exists():
        report["messages"].append("Data root does not exist on this machine/server.")
    else:
        report["messages"].append("No NPZ or EDF files found under the searched directory.")
    return report


def candidate_dataset_dirs(data_root: Path, dataset: str) -> list[Path]:
    if dataset == "sleepedf":
        names = ["sleepedf", "sleep-edf", "sleep-edf-expanded", "sleep-edfx", "Sleep-EDF", "SleepEDF"]
    else:
        names = ["isruc", "ISRUC", "ISRUC-Sleep", "isruc-sleep"]
    return [data_root / name for name in names] + [data_root]


def preferred_npz_path(search_root: Path, dataset: str) -> Path:
    if search_root.name.lower().replace("-", "") in {dataset, "sleepedfexpanded", "sleepedfx", "isrucsleep"}:
        return search_root / "preprocessed.npz"
    return search_root / dataset / "preprocessed.npz"


def inspect_npz(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"inspected_npz": str(path), "verdict": "invalid_npz", "npz": {}, "messages": []}
    try:
        data = np.load(path, allow_pickle=True)
    except Exception as exc:  # noqa: BLE001 - this is an inspector.
        out["messages"].append(f"Failed to load NPZ: {type(exc).__name__}: {exc}")
        return out

    keys = sorted(data.files)
    out["npz"]["keys"] = keys
    missing = [key for key in REQUIRED_NPZ_KEYS if key not in data.files]
    if missing:
        out["messages"].append(f"Missing required NPZ keys: {missing}. Required keys are x, y, subject.")
        return out

    x = np.asarray(data["x"])
    y = np.asarray(data["y"])
    subject = np.asarray(data["subject"])
    out["npz"].update(
        {
            "x_shape": list(x.shape),
            "y_shape": list(y.shape),
            "subject_shape": list(subject.shape),
            "x_dtype": str(x.dtype),
            "y_dtype": str(y.dtype),
            "subject_count": int(len(np.unique(subject))),
            "label_values": sorted(int(v) for v in np.unique(y) if np.issubdtype(y.dtype, np.integer)),
        }
    )

    problems: list[str] = []
    if x.ndim not in {2, 3}:
        problems.append("x must have shape (epochs, samples) or (epochs, channels, samples).")
    if len(y) != len(x) or len(subject) != len(x):
        problems.append("x, y, subject must have the same first dimension.")
    if not np.issubdtype(y.dtype, np.integer):
        problems.append("y must be integer encoded as 0=W, 1=N1, 2=N2, 3=N3, 4=REM.")
    elif np.any((y < 0) | (y > 4)):
        problems.append("y contains labels outside 0..4.")

    if problems:
        out["messages"].extend(problems)
        return out

    counts = {str(int(label)): int((y == label).sum()) for label in np.unique(y)}
    out["npz"]["label_counts"] = counts
    out["verdict"] = "ready_npz"
    out["messages"].append("NPZ format is compatible with the current training entrypoint.")
    return out


def print_human_report(report: dict[str, Any]) -> None:
    print("=== EEG data inspection ===")
    print(f"dataset: {report['dataset']}")
    print(f"data_root: {report['data_root']}")
    print(f"searched_dir: {report['searched_dir']}")
    print(f"verdict: {report['verdict']}")
    print("")
    if report.get("npz"):
        print("NPZ:")
        for key, value in report["npz"].items():
            print(f"  {key}: {value}")
    print(f"edf_count: {report['edf_count']}")
    print(f"psg_edf_count: {report['psg_edf_count']}")
    print(f"hypnogram_edf_count: {report['hypnogram_edf_count']}")
    if report["sample_edf_files"]:
        print("sample_edf_files:")
        for path in report["sample_edf_files"]:
            print(f"  - {path}")
    print("")
    print("messages:")
    for msg in report["messages"]:
        print(f"  - {msg}")


if __name__ == "__main__":
    raise SystemExit(main())
