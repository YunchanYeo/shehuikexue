"""Population norms (mean/std) for per-metric Z-scores."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import yaml

from .paths import default_norms_path

# Metrics that participate in Z-scoring (order stable for reports).
NORM_METRIC_KEYS = (
    "articulation_rate",
    "silent_pause_ratio",
    "filled_pause_density",
    "repetition_repair_density",
    "type_token_ratio",
    "mean_utterance_length",
    "connective_density",
    "pitch_sd",
    "intensity_sd",
)

MIN_COHORT_FOR_NORMS = 2
MIN_STD = 1e-6


def load_norms(norms_path: str | Path | None = None) -> dict[str, Any]:
    if norms_path is None:
        norms_path = default_norms_path()
    with open(norms_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def cohort_size(norms: dict[str, Any]) -> int:
    meta = norms.get("_meta") or {}
    return int(meta.get("n_samples", 0))


def is_calibrated(norms: dict[str, Any]) -> bool:
    return cohort_size(norms) >= MIN_COHORT_FOR_NORMS


def metric_norms(norms: dict[str, Any], metric: str) -> dict[str, float]:
    return norms[metric]


def compute_norms_from_rows(
    rows: list[dict[str, float]],
    *,
    source: str | None = None,
) -> dict[str, Any]:
    """
    Estimate population mean/std from many speakers' raw metrics.

    Requires at least MIN_COHORT_FOR_NORMS rows; otherwise std would be 0
  for a single sample.
    """
    if len(rows) < MIN_COHORT_FOR_NORMS:
        raise ValueError(
            f"Z 分常模至少需要 {MIN_COHORT_FOR_NORMS} 条录音；当前只有 {len(rows)} 条。"
            "请先收集多个样本再标定 norms.yaml。"
        )

    out: dict[str, Any] = {
        "_meta": {
            "n_samples": len(rows),
            "source": source or "",
            "note": "由 calibrate_norms.py 根据样本均值/标准差生成，用于 (值−mean)/std",
        }
    }
    for key in NORM_METRIC_KEYS:
        vals = np.array([float(r[key]) for r in rows], dtype=np.float64)
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1))
        if std < MIN_STD:
            std = MIN_STD
        out[key] = {"mean": mean, "std": std}
    return out


def save_norms(norms: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Population mean/std for Z = (value - mean) / std.\n"
        "# Do not Z-score a single file alone — calibrate on many recordings first.\n"
    )
    body = yaml.dump(
        norms,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    path.write_text(header + body, encoding="utf-8")
