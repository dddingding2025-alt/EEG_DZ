from __future__ import annotations

from typing import Iterable

import numpy as np

STAGE_NAMES = ("W", "N1", "N2", "N3", "REM")
STAGE_TO_ID = {name: idx for idx, name in enumerate(STAGE_NAMES)}
ID_TO_STAGE = {idx: name for name, idx in STAGE_TO_ID.items()}

_ALIASES = {
    "WAKE": "W",
    "SLEEP STAGE W": "W",
    "0": "W",
    "1": "N1",
    "S1": "N1",
    "SLEEP STAGE 1": "N1",
    "2": "N2",
    "S2": "N2",
    "SLEEP STAGE 2": "N2",
    "3": "N3",
    "4": "N3",
    "S3": "N3",
    "S4": "N3",
    "N4": "N3",
    "SLEEP STAGE 3": "N3",
    "SLEEP STAGE 4": "N3",
    "R": "REM",
    "REM": "REM",
    "SLEEP STAGE R": "REM",
}

UNKNOWN_LABELS = {"M", "MOVEMENT", "UNKNOWN", "?", "UNSCORED", "MT"}


def normalize_stage(label: object) -> str | None:
    """Normalize common sleep-stage labels to W/N1/N2/N3/REM.

    Returns None for movement/unknown labels that should be removed.
    """

    if isinstance(label, (np.integer, int)):
        idx = int(label)
        return ID_TO_STAGE.get(idx)
    text = str(label).strip().upper()
    if text in STAGE_TO_ID:
        return text
    if text in UNKNOWN_LABELS:
        return None
    return _ALIASES.get(text)


def encode_labels(labels: Iterable[object]) -> np.ndarray:
    encoded: list[int] = []
    for label in labels:
        stage = normalize_stage(label)
        if stage is None:
            encoded.append(-1)
        else:
            encoded.append(STAGE_TO_ID[stage])
    return np.asarray(encoded, dtype=np.int64)


def valid_label_mask(encoded_labels: np.ndarray) -> np.ndarray:
    labels = np.asarray(encoded_labels)
    return (labels >= 0) & (labels < len(STAGE_NAMES))
