from __future__ import annotations

import numpy as np

from .labels import STAGE_NAMES, STAGE_TO_ID
from .transitions import boundary_indices


def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = 5) -> np.ndarray:
    cm = np.zeros((n_classes, n_classes), dtype=np.int64)
    for true, pred in zip(np.asarray(y_true, dtype=np.int64), np.asarray(y_pred, dtype=np.int64)):
        if 0 <= true < n_classes and 0 <= pred < n_classes:
            cm[true, pred] += 1
    return cm


def per_class_prf(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = 5) -> dict[str, dict[str, float]]:
    cm = confusion_matrix(y_true, y_pred, n_classes=n_classes)
    out: dict[str, dict[str, float]] = {}
    for idx, name in enumerate(STAGE_NAMES):
        tp = float(cm[idx, idx])
        fp = float(cm[:, idx].sum() - cm[idx, idx])
        fn = float(cm[idx, :].sum() - cm[idx, idx])
        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)
        out[name] = {"precision": precision, "recall": recall, "f1": f1}
    return out


def cohen_kappa(y_true: np.ndarray, y_pred: np.ndarray, n_classes: int = 5) -> float:
    cm = confusion_matrix(y_true, y_pred, n_classes=n_classes).astype(float)
    total = cm.sum()
    if total == 0:
        return 0.0
    po = np.trace(cm) / total
    pe = (cm.sum(axis=0) * cm.sum(axis=1)).sum() / (total * total)
    return float(_safe_div(po - pe, 1.0 - pe))


def expected_calibration_error(probs: np.ndarray, y_true: np.ndarray, n_bins: int = 15) -> float:
    p = np.asarray(probs, dtype=float)
    y = np.asarray(y_true, dtype=np.int64)
    conf = p.max(axis=1)
    pred = p.argmax(axis=1)
    correct = (pred == y).astype(float)
    ece = 0.0
    for lo, hi in zip(np.linspace(0, 1, n_bins, endpoint=False), np.linspace(1 / n_bins, 1, n_bins)):
        mask = (conf > lo) & (conf <= hi)
        if mask.any():
            ece += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return float(ece)


def boundary_delay(y_true: np.ndarray, y_pred: np.ndarray, max_window: int = 5) -> float:
    true_b = boundary_indices(y_true)
    pred_b = boundary_indices(y_pred)
    if len(true_b) == 0 or len(pred_b) == 0:
        return 0.0
    delays: list[int] = []
    for boundary in true_b:
        delta = pred_b - boundary
        nearest = delta[np.argmin(np.abs(delta))]
        if abs(nearest) <= max_window:
            delays.append(int(nearest))
    if not delays:
        return float(max_window + 1)
    return float(np.mean(np.abs(delays)))


def fragmentation_error(y_pred: np.ndarray, min_run: int = 2) -> float:
    y = np.asarray(y_pred, dtype=np.int64)
    if len(y) == 0:
        return 0.0
    run_lengths: list[int] = []
    start = 0
    for idx in range(1, len(y)):
        if y[idx] != y[idx - 1]:
            run_lengths.append(idx - start)
            start = idx
    run_lengths.append(len(y) - start)
    return float(np.mean([length < min_run for length in run_lengths]))


def compute_metrics(
    y_true: np.ndarray,
    probs: np.ndarray,
    transition_mask: np.ndarray | None = None,
) -> dict[str, float]:
    y = np.asarray(y_true, dtype=np.int64)
    p = np.asarray(probs, dtype=float)
    pred = p.argmax(axis=1)
    prf = per_class_prf(y, pred)
    f1s = [prf[name]["f1"] for name in STAGE_NAMES]
    n1 = prf["N1"]
    metrics = {
        "accuracy": float(np.mean(pred == y)) if len(y) else 0.0,
        "macro_f1": float(np.mean(f1s)),
        "kappa": cohen_kappa(y, pred),
        "n1_f1": n1["f1"],
        "n1_precision": n1["precision"],
        "n1_recall": n1["recall"],
        "ece": expected_calibration_error(p, y),
        "n1_overprediction_rate": float(np.mean(pred == STAGE_TO_ID["N1"]) - np.mean(y == STAGE_TO_ID["N1"])),
        "boundary_delay": boundary_delay(y, pred),
        "fragmentation_error": fragmentation_error(pred),
    }
    if transition_mask is not None and np.asarray(transition_mask).any():
        tm = np.asarray(transition_mask, dtype=bool)
        trans = compute_metrics(y[tm], p[tm], transition_mask=None)
        metrics["transition_n1_f1"] = trans["n1_f1"]
        metrics["transition_macro_f1"] = trans["macro_f1"]
        metrics["boundary_adjacent_ece"] = trans["ece"]
        stable = compute_metrics(y[~tm], p[~tm], transition_mask=None) if (~tm).any() else {"macro_f1": 0.0}
        metrics["stable_vs_transition_gap"] = float(stable["macro_f1"] - trans["macro_f1"])
    else:
        metrics["transition_n1_f1"] = 0.0
        metrics["transition_macro_f1"] = 0.0
        metrics["boundary_adjacent_ece"] = 0.0
        metrics["stable_vs_transition_gap"] = 0.0
    return metrics


def _safe_div(num: float, den: float) -> float:
    return float(num / den) if den else 0.0
