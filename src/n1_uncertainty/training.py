from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler

from .metrics import compute_metrics
from .soft_labels import soft_targets
from .status import append_metrics
from .transitions import transition_mask_by_subject


class TinyCnn(nn.Module):
    def __init__(self, in_channels: int, n_classes: int = 5) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(in_channels, 32, kernel_size=15, padding=7),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(4),
            nn.Conv1d(32, 64, kernel_size=9, padding=4),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Linear(64, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.net(x).squeeze(-1)
        return self.head(feat)


def run_training_variants(cfg: dict, data_path: Path, run_dir: Path) -> dict:
    data = np.load(data_path, allow_pickle=True)
    x = np.asarray(data["x"], dtype=np.float32)
    y = np.asarray(data["y"], dtype=np.int64)
    subject = np.asarray(data["subject"])
    if x.ndim == 2:
        x = x[:, None, :]
    if x.ndim != 3:
        raise ValueError("x must have shape (epochs, channels, samples) or (epochs, samples)")

    splits = subject_independent_split(subject, seed=int(cfg.get("training", {}).get("seed", 42)))
    transition = transition_mask_by_subject(y, subject, k=int(cfg.get("transition", {}).get("k", 2)))
    variants = cfg.get("variants", [{"id": "hard_ce", "loss": "hard_ce"}])
    best: dict[str, float | str | dict] = {"best_n1_f1": 0.0, "best_transition_n1_f1": 0.0}
    for variant in variants:
        ensure_variant_supported(variant)
        metrics = train_one_variant(cfg, variant, x, y, transition, splits, run_dir)
        if metrics["n1_f1"] > float(best["best_n1_f1"]):
            best.update(
                best_variant=variant["id"],
                best_n1_f1=metrics["n1_f1"],
                best_transition_n1_f1=metrics["transition_n1_f1"],
                metrics=metrics,
            )
    return {"mode": "npz_training", "epoch": int(cfg.get("training", {}).get("epochs", 1)), **best}


def ensure_variant_supported(variant: dict) -> None:
    if variant.get("context") or variant.get("context_gate") or variant.get("transition_head"):
        raise NotImplementedError(
            "TGCM/context variants are phase-4 placeholders. Run baseline/softlabel configs first, "
            "then implement TGCM before executing tgcm_sleepedf."
        )


def train_one_variant(
    cfg: dict,
    variant: dict,
    x: np.ndarray,
    y: np.ndarray,
    transition: np.ndarray,
    splits: dict[str, np.ndarray],
    run_dir: Path,
) -> dict[str, float]:
    seed = int(cfg.get("training", {}).get("seed", 42))
    torch.manual_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TinyCnn(in_channels=x.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg.get("training", {}).get("lr", 1e-3)))
    epochs = int(cfg.get("training", {}).get("epochs", 10))
    batch_size = int(cfg.get("training", {}).get("batch_size", 128))
    train_idx = splits["train"]
    loader = make_loader(x, y, train_idx, batch_size, variant)
    target_soft = maybe_soft_targets(y, transition, variant)
    for epoch in range(1, epochs + 1):
        model.train()
        losses: list[float] = []
        class_weights = make_class_weights(y[train_idx], device)
        for xb, yb, ib in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            logits = model(xb)
            trans_flags = torch.as_tensor(transition[ib.numpy()], dtype=torch.float32, device=device)
            loss = compute_loss(
                logits,
                yb,
                target_soft[ib.numpy()] if target_soft is not None else None,
                variant,
                device,
                class_weights=class_weights,
                transition_flags=trans_flags,
            )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu()))
        metrics = evaluate(model, x, y, transition, splits["val"], device)
        append_metrics(run_dir, {"epoch": epoch, "variant": variant["id"], "split": "val", "loss": np.mean(losses), **metrics})
    test_metrics = evaluate(model, x, y, transition, splits["test"], device)
    append_metrics(run_dir, {"epoch": epochs, "variant": variant["id"], "split": "test", "loss": 0.0, **test_metrics})
    return test_metrics


def compute_loss(
    logits: torch.Tensor,
    y: torch.Tensor,
    soft: np.ndarray | None,
    variant: dict,
    device: torch.device,
    class_weights: torch.Tensor | None = None,
    transition_flags: torch.Tensor | None = None,
) -> torch.Tensor:
    loss_name = variant.get("loss", "hard_ce")
    if soft is not None:
        target = torch.as_tensor(soft, dtype=torch.float32, device=device)
        log_probs = torch.log_softmax(logits, dim=1)
        per_sample = -(target * log_probs).sum(dim=1)
        if loss_name == "hybrid" and transition_flags is not None:
            weight = torch.where(transition_flags > 0, torch.full_like(transition_flags, 0.7), torch.ones_like(transition_flags))
            per_sample = per_sample * weight
        return per_sample.mean()
    if loss_name == "focal":
        ce = nn.functional.cross_entropy(logits, y, reduction="none")
        pt = torch.exp(-ce)
        gamma = float(variant.get("gamma", 2.0))
        return (((1 - pt) ** gamma) * ce).mean()
    if loss_name == "class_weighted":
        return nn.functional.cross_entropy(logits, y, weight=class_weights)
    return nn.functional.cross_entropy(logits, y)


def maybe_soft_targets(y: np.ndarray, transition: np.ndarray, variant: dict) -> np.ndarray | None:
    loss_name = variant.get("loss", "")
    if loss_name == "uniform_smoothing":
        epsilon = float(variant.get("epsilon", 0.1))
        out = np.full((len(y), 5), epsilon / 4, dtype=np.float32)
        out[np.arange(len(y)), y] = 1.0 - epsilon
        return out
    if loss_name in {"stage_adjacent", "transition_smoothing", "hybrid"}:
        epsilon = float(variant.get("epsilon", 0.1))
        transition_epsilon = float(variant.get("transition_epsilon", epsilon))
        return soft_targets(y, epsilon=epsilon, transition_mask=transition, transition_epsilon=transition_epsilon)
    return None


def make_loader(x: np.ndarray, y: np.ndarray, idx: np.ndarray, batch_size: int, variant: dict) -> DataLoader:
    xt = torch.as_tensor(x[idx], dtype=torch.float32)
    yt = torch.as_tensor(y[idx], dtype=torch.long)
    it = torch.as_tensor(idx, dtype=torch.long)
    dataset = TensorDataset(xt, yt, it)
    if variant.get("sampler") == "balanced":
        counts = np.bincount(y[idx], minlength=5).astype(float)
        weights = 1.0 / np.maximum(counts[y[idx]], 1.0)
        sampler = WeightedRandomSampler(torch.as_tensor(weights, dtype=torch.double), len(weights), replacement=True)
        return DataLoader(dataset, batch_size=batch_size, sampler=sampler)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def make_class_weights(y_train: np.ndarray, device: torch.device) -> torch.Tensor:
    counts = np.bincount(y_train, minlength=5).astype(np.float32)
    inv = 1.0 / np.maximum(counts, 1.0)
    weights = inv / inv.mean()
    return torch.as_tensor(weights, dtype=torch.float32, device=device)


def evaluate(model: nn.Module, x: np.ndarray, y: np.ndarray, transition: np.ndarray, idx: np.ndarray, device: torch.device) -> dict[str, float]:
    model.eval()
    probs: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(idx), 512):
            batch_idx = idx[start : start + 512]
            xb = torch.as_tensor(x[batch_idx], dtype=torch.float32, device=device)
            probs.append(torch.softmax(model(xb), dim=1).cpu().numpy())
    return compute_metrics(y[idx], np.concatenate(probs, axis=0), transition_mask=transition[idx])


def subject_independent_split(subject: np.ndarray, seed: int = 42) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    subjects = np.unique(subject)
    rng.shuffle(subjects)
    n = len(subjects)
    n_test = max(1, int(round(n * 0.2)))
    n_val = max(1, int(round(n * 0.1))) if n >= 5 else 1
    test_subjects = set(subjects[:n_test])
    val_subjects = set(subjects[n_test : n_test + n_val])
    train_subjects = set(subjects[n_test + n_val :])
    if not train_subjects:
        train_subjects = set(subjects[n_test:])
    return {
        "train": np.flatnonzero(np.isin(subject, list(train_subjects))),
        "val": np.flatnonzero(np.isin(subject, list(val_subjects))),
        "test": np.flatnonzero(np.isin(subject, list(test_subjects))),
    }
