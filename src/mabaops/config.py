"""Configuration helpers for MabaOps."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_DATA_DIR = Path("data")
ENV_DATA_DIR = "MABAOPS_DATA_DIR"


def resolve_data_dir(data_dir: str | None = None) -> Path:
    """Resolve the local data directory.

    Priority:
    1. explicit CLI option
    2. MABAOPS_DATA_DIR environment variable
    3. ./data for repo/demo friendly defaults
    """

    raw_path = data_dir or os.getenv(ENV_DATA_DIR)
    if raw_path:
        return Path(raw_path).expanduser().resolve()
    return DEFAULT_DATA_DIR.resolve()
