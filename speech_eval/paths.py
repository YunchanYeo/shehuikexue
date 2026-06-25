"""Resource paths for dev and PyInstaller bundles."""

from __future__ import annotations

import sys
from pathlib import Path


def package_dir() -> Path:
    if getattr(sys, "frozen", False):
        bundle_root = getattr(sys, "_MEIPASS", None)
        if bundle_root is None:
            raise RuntimeError("PyInstaller bundle root (_MEIPASS) not found")
        return Path(bundle_root) / "speech_eval"
    return Path(__file__).resolve().parent


def default_norms_path() -> Path:
    return package_dir() / "norms.yaml"
