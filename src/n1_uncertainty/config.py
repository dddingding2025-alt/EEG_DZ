from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    expanded = os.path.expandvars(text)
    data = yaml.safe_load(expanded)
    if not isinstance(data, dict):
        raise ValueError(f"config must be a mapping: {path}")
    return data
