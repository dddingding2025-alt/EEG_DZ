from __future__ import annotations

import numpy as np

from .labels import STAGE_TO_ID


def stage_adjacent_matrix(epsilon: float = 0.1, rem_soft: bool = False) -> np.ndarray:
    """Build the W/N1/N2/N3/REM adjacency-aware smoothing matrix."""

    if not 0 <= epsilon < 1:
        raise ValueError("epsilon must be in [0, 1)")

    n = len(STAGE_TO_ID)
    matrix = np.eye(n, dtype=np.float32)

    def set_row(stage: str, neighbors: list[str], eps: float = epsilon) -> None:
        row = np.zeros(n, dtype=np.float32)
        row[STAGE_TO_ID[stage]] = 1.0 - eps
        if neighbors:
            share = eps / len(neighbors)
            for neighbor in neighbors:
                row[STAGE_TO_ID[neighbor]] = share
        matrix[STAGE_TO_ID[stage]] = row

    set_row("W", ["N1"])
    set_row("N1", ["W", "N2"])
    set_row("N2", ["N1", "N3"])
    set_row("N3", ["N2"])
    if rem_soft:
        set_row("REM", ["W", "N1"])
    return matrix


def soft_targets(
    labels: np.ndarray,
    epsilon: float = 0.1,
    transition_mask: np.ndarray | None = None,
    transition_epsilon: float | None = None,
) -> np.ndarray:
    y = np.asarray(labels, dtype=np.int64)
    base = stage_adjacent_matrix(epsilon=epsilon)
    targets = base[y].copy()
    if transition_mask is not None and transition_epsilon is not None:
        trans = np.asarray(transition_mask, dtype=bool)
        stronger = stage_adjacent_matrix(epsilon=transition_epsilon)
        targets[trans] = stronger[y[trans]]
    return targets.astype(np.float32)
