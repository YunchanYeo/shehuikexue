"""Resource paths for dev and PyInstaller bundles."""

from __future__ import annotations

import sys
from pathlib import Path


def package_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "speech_eval"
    return Path(__file__).resolve().parent


def default_norms_path() -> Path:
    return package_dir() / "norms.yaml"
