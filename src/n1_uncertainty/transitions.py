from __future__ import annotations

from collections import Counter

import numpy as np

from .labels import STAGE_NAMES, STAGE_TO_ID


def transition_mask(labels: np.ndarray, k: int = 2) -> np.ndarray:
    """Return a boolean mask for epochs within +/- k of any label boundary."""

    y = np.asarray(labels, dtype=np.int64)
    mask = np.zeros(len(y), dtype=bool)
    if len(y) <= 1:
        return mask
    boundaries = np.flatnonzero(y[1:] != y[:-1]) + 1
    for boundary in boundaries:
        start = max(0, boundary - k)
        end = min(len(y), boundary + k + 1)
        mask[start:end] = True
    return mask


def transition_mask_by_subject(labels: np.ndarray, subjects: np.ndarray, k: int = 2) -> np.ndarray:
    y = np.asarray(labels, dtype=np.int64)
    s = np.asarray(subjects)
    mask = np.zeros(len(y), dtype=bool)
    for subject in np.unique(s):
        idx = np.flatnonzero(s == subject)
        mask[idx] = transition_mask(y[idx], k=k)
    return mask


def boundary_indices(labels: np.ndarray) -> np.ndarray:
    y = np.asarray(labels, dtype=np.int64)
    if len(y) <= 1:
        return np.asarray([], dtype=np.int64)
    return np.flatnonzero(y[1:] != y[:-1]) + 1


def boundary_type_counts(labels: np.ndarray) -> dict[str, int]:
    y = np.asarray(labels, dtype=np.int64)
    counts: Counter[str] = Counter()
    for idx in boundary_indices(y):
        a, b = int(y[idx - 1]), int(y[idx])
        pair = _boundary_type(a, b)
        counts[pair] += 1
    return dict(counts)


def _boundary_type(a: int, b: int) -> str:
    nrem = {STAGE_TO_ID["N1"], STAGE_TO_ID["N2"], STAGE_TO_ID["N3"]}
    pair = {a, b}
    if pair == {STAGE_TO_ID["W"], STAGE_TO_ID["N1"]}:
        return "W<->N1"
    if pair == {STAGE_TO_ID["N1"], STAGE_TO_ID["N2"]}:
        return "N1<->N2"
    if pair == {STAGE_TO_ID["N2"], STAGE_TO_ID["N3"]}:
        return "N2<->N3"
    if STAGE_TO_ID["REM"] in pair and (pair - {STAGE_TO_ID["REM"]}) & nrem:
        return "NREM<->REM"
    return f"{STAGE_NAMES[a]}<->{STAGE_NAMES[b]}"
