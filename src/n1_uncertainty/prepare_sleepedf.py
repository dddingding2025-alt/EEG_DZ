from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from .labels import STAGE_NAMES


RAW_EVENT_ID = {
    "Sleep stage W": 1,
    "Sleep stage 1": 2,
    "Sleep stage 2": 3,
    "Sleep stage 3": 4,
    "Sleep stage 4": 5,
    "Sleep stage R": 6,
}

EVENT_TO_LABEL = {
    1: 0,  # W
    2: 1,  # N1
    3: 2,  # N2
    4: 3,  # N3
    5: 3,  # N3, merge R&K stage 4 into AASM N3
    6: 4,  # REM
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert raw Sleep-EDF EDF files to preprocessed.npz.")
    parser.add_argument("--data-root", default="~/data")
    parser.add_argument("--raw-dir", default=None, help="Directory containing Sleep-EDF EDF files.")
    parser.add_argument("--output", default=None, help="Output NPZ path.")
    parser.add_argument("--channel", default="Fpz-Cz", help="EEG channel to extract, default Fpz-Cz.")
    parser.add_argument("--epoch-seconds", type=float, default=30.0)
    parser.add_argument("--target-sfreq", type=float, default=100.0)
    parser.add_argument("--trim-wake-minutes", type=float, default=30.0)
    parser.add_argument("--max-pairs", type=int, default=None, help="Limit pairs for server smoke conversion.")
    parser.add_argument("--no-compress", action="store_true")
    args = parser.parse_args()

    data_root = Path(args.data_root).expanduser()
    raw_dir = Path(args.raw_dir).expanduser() if args.raw_dir else find_sleepedf_raw_dir(data_root)
    output = Path(args.output).expanduser() if args.output else data_root / "sleepedf" / "preprocessed.npz"
    output.parent.mkdir(parents=True, exist_ok=True)

    pairs = find_pairs(raw_dir)
    if args.max_pairs is not None:
        pairs = pairs[: args.max_pairs]
    if not pairs:
        raise FileNotFoundError(f"No PSG/Hypnogram EDF pairs found under {raw_dir}")

    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    subjects: list[np.ndarray] = []
    nights: list[np.ndarray] = []
    files: list[str] = []
    per_file: list[dict[str, Any]] = []

    for idx, pair in enumerate(pairs, start=1):
        print(f"[{idx}/{len(pairs)}] {pair['night_id']} {pair['psg'].name}")
        x, y, meta = convert_pair(
            pair["psg"],
            pair["hyp"],
            channel_query=args.channel,
            epoch_seconds=args.epoch_seconds,
            target_sfreq=args.target_sfreq,
            trim_wake_minutes=args.trim_wake_minutes,
        )
        if len(y) == 0:
            print(f"  skipped: no valid epochs after filtering")
            continue
        subject_id = pair["subject_id"]
        night_id = pair["night_id"]
        xs.append(x.astype(np.float32, copy=False))
        ys.append(y.astype(np.int64, copy=False))
        subjects.append(np.full(len(y), subject_id, dtype=object))
        nights.append(np.full(len(y), night_id, dtype=object))
        files.append(str(pair["psg"]))
        meta.update({"night_id": night_id, "subject_id": subject_id, "epochs": int(len(y))})
        per_file.append(meta)
        print(f"  epochs={len(y)} channel={meta['channel']} sfreq={meta['sfreq']}")

    if not xs:
        raise RuntimeError("No valid epochs were produced from the selected Sleep-EDF files.")

    x_all = np.concatenate(xs, axis=0)
    y_all = np.concatenate(ys, axis=0)
    subject_all = np.concatenate(subjects, axis=0)
    night_all = np.concatenate(nights, axis=0)
    metadata = {
        "source": "Sleep-EDF Expanded",
        "raw_dir": str(raw_dir),
        "channel_query": args.channel,
        "target_sfreq": args.target_sfreq,
        "epoch_seconds": args.epoch_seconds,
        "trim_wake_minutes": args.trim_wake_minutes,
        "stage_names": STAGE_NAMES,
        "n_epochs": int(len(y_all)),
        "n_subjects": int(len(set(subject_all.tolist()))),
        "n_nights": int(len(set(night_all.tolist()))),
        "label_counts": {STAGE_NAMES[i]: int((y_all == i).sum()) for i in range(len(STAGE_NAMES))},
        "files": files,
        "per_file": per_file,
    }

    save = np.savez if args.no_compress else np.savez_compressed
    save(
        output,
        x=x_all,
        y=y_all,
        subject=subject_all,
        night=night_all,
        stage_names=np.asarray(STAGE_NAMES, dtype=object),
        metadata=json.dumps(metadata, ensure_ascii=False),
    )
    print("")
    print(f"wrote: {output}")
    print(f"x shape: {x_all.shape}")
    print(f"y shape: {y_all.shape}")
    print(f"subjects: {metadata['n_subjects']} nights: {metadata['n_nights']}")
    print(f"label_counts: {metadata['label_counts']}")
    return 0


def find_sleepedf_raw_dir(data_root: Path) -> Path:
    candidates = [
        data_root / "raw" / "sleep-edf" / "sleep-cassette",
        data_root / "raw" / "sleep-edf",
        data_root / "sleep-edf" / "sleep-cassette",
        data_root / "sleep-edf",
        data_root / "sleepedf",
        data_root,
    ]
    for candidate in candidates:
        if candidate.exists() and list(candidate.rglob("*PSG.edf")):
            return candidate
    return data_root


def find_pairs(raw_dir: Path) -> list[dict[str, Any]]:
    psg_files = sorted(raw_dir.rglob("*PSG.edf"))
    hyp_files = sorted(raw_dir.rglob("*Hypnogram.edf"))
    hyp_by_key = {night_key(path): path for path in hyp_files if night_key(path)}
    pairs: list[dict[str, Any]] = []
    for psg in psg_files:
        key = night_key(psg)
        if not key:
            continue
        hyp = hyp_by_key.get(key)
        if hyp is None:
            continue
        pairs.append({"night_id": key, "subject_id": subject_key(key), "psg": psg, "hyp": hyp})
    return pairs


def night_key(path: Path) -> str | None:
    match = re.search(r"([A-Z]{2}\d{4})", path.name)
    return match.group(1) if match else None


def subject_key(night_id: str) -> str:
    return night_id[:5]


def convert_pair(
    psg_path: Path,
    hyp_path: Path,
    channel_query: str,
    epoch_seconds: float,
    target_sfreq: float,
    trim_wake_minutes: float,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    try:
        import mne
    except ImportError as exc:
        raise RuntimeError("Sleep-EDF conversion requires mne and edfio. Run `pip install -r requirements.txt`.") from exc

    raw = mne.io.read_raw_edf(psg_path, preload=False, verbose="ERROR")
    channel = pick_channel(raw.ch_names, channel_query)
    raw.pick([channel])
    raw.load_data(verbose="ERROR")
    if abs(float(raw.info["sfreq"]) - target_sfreq) > 1e-6:
        raw.resample(target_sfreq, npad="auto", verbose="ERROR")

    annotations = mne.read_annotations(hyp_path)
    raw.set_annotations(annotations, emit_warning=False)
    events, _ = mne.events_from_annotations(
        raw,
        event_id=RAW_EVENT_ID,
        chunk_duration=epoch_seconds,
        verbose="ERROR",
    )
    if len(events) == 0:
        return np.empty((0, 1, int(target_sfreq * epoch_seconds)), dtype=np.float32), np.empty(0, dtype=np.int64), {
            "channel": channel,
            "sfreq": float(raw.info["sfreq"]),
            "reason": "no_events",
        }

    present_event_ids = {int(code) for code in events[:, 2]}
    present_event_id = {name: code for name, code in RAW_EVENT_ID.items() if code in present_event_ids}
    tmax = epoch_seconds - 1.0 / float(raw.info["sfreq"])
    epochs = mne.Epochs(
        raw,
        events,
        event_id=present_event_id,
        tmin=0,
        tmax=tmax,
        baseline=None,
        preload=True,
        picks=[channel],
        on_missing="ignore",
        verbose="ERROR",
    )
    x = epochs.get_data().astype(np.float32, copy=False)
    y = np.asarray([EVENT_TO_LABEL[int(code)] for code in epochs.events[:, 2]], dtype=np.int64)
    keep = trim_wake(y, trim_wake_minutes=trim_wake_minutes, epoch_seconds=epoch_seconds)
    x = x[keep]
    y = y[keep]
    meta = {
        "channel": channel,
        "sfreq": float(raw.info["sfreq"]),
        "psg": str(psg_path),
        "hypnogram": str(hyp_path),
        "present_stages": sorted(present_event_id),
        "label_counts": {STAGE_NAMES[i]: int((y == i).sum()) for i in range(len(STAGE_NAMES))},
    }
    return x, y, meta


def pick_channel(ch_names: list[str], query: str) -> str:
    normalized_query = normalize_channel(query)
    for name in ch_names:
        if normalize_channel(name) == normalized_query:
            return name
    for name in ch_names:
        if normalized_query in normalize_channel(name):
            return name
    raise ValueError(f"Channel {query!r} not found. Available channels: {ch_names}")


def normalize_channel(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("eeg", ""))


def trim_wake(y: np.ndarray, trim_wake_minutes: float, epoch_seconds: float) -> np.ndarray:
    if trim_wake_minutes < 0:
        return np.ones(len(y), dtype=bool)
    non_wake = np.flatnonzero(y != 0)
    if len(non_wake) == 0:
        return np.ones(len(y), dtype=bool)
    margin = int(round((trim_wake_minutes * 60.0) / epoch_seconds))
    start = max(0, int(non_wake[0]) - margin)
    end = min(len(y), int(non_wake[-1]) + margin + 1)
    keep = np.zeros(len(y), dtype=bool)
    keep[start:end] = True
    return keep


if __name__ == "__main__":
    raise SystemExit(main())
