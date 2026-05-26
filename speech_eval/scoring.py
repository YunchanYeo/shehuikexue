"""Composite scores with Z-normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .asr import transcribe
from .audio_metrics import extract_audio_metrics
from .paths import default_norms_path
from .text_metrics import count_syllables_chinese, extract_text_metrics


def _load_norms(norms_path: str | Path | None) -> dict[str, dict[str, float]]:
    if norms_path is None:
        norms_path = default_norms_path()
    with open(norms_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def z_score(value: float, mean: float, std: float) -> float:
    if std <= 0:
        return 0.0
    return (value - mean) / std


def _z(metric: str, value: float, norms: dict) -> float:
    cfg = norms[metric]
    return z_score(value, cfg["mean"], cfg["std"])


def compute_dimension_scores(metrics: dict[str, float], norms: dict) -> dict[str, Any]:
    z_art = _z("articulation_rate", metrics["articulation_rate"], norms)
    z_pause = _z("silent_pause_ratio", metrics["silent_pause_ratio"], norms)
    z_fill = _z("filled_pause_density", metrics["filled_pause_density"], norms)
    z_rep = _z("repetition_repair_density", metrics["repetition_repair_density"], norms)
    z_ttr = _z("type_token_ratio", metrics["type_token_ratio"], norms)
    z_mlu = _z("mean_utterance_length", metrics["mean_utterance_length"], norms)
    z_conn = _z("connective_density", metrics["connective_density"], norms)
    z_pitch = _z("pitch_sd", metrics["pitch_sd"], norms)
    z_int = _z("intensity_sd", metrics["intensity_sd"], norms)

    fluency = 0.25 * (z_art - z_pause - z_fill - z_rep)
    richness = (z_ttr + z_mlu + z_conn) / 3.0
    vividness = 0.5 * (z_pitch + z_int)
    total = (fluency + richness + vividness) / 3.0

    return {
        "fluency": fluency,
        "richness": richness,
        "vividness": vividness,
        "total": total,
        "z_scores": {
            "articulation_rate": z_art,
            "silent_pause_ratio": z_pause,
            "filled_pause_density": z_fill,
            "repetition_repair_density": z_rep,
            "type_token_ratio": z_ttr,
            "mean_utterance_length": z_mlu,
            "connective_density": z_conn,
            "pitch_sd": z_pitch,
            "intensity_sd": z_int,
        },
    }


def evaluate_speech(
    audio_path: str,
    *,
    norms_path: str | Path | None = None,
    whisper_model: str = "base",
    device: str = "cpu",
    transcript: str | None = None,
    skip_asr: bool = False,
) -> dict[str, Any]:
    """
    Evaluate one speech audio file.

    Parameters
    ----------
    audio_path : path to wav/mp3/flac etc.
    transcript : if provided, skip ASR
    skip_asr : use empty transcript (audio-only metrics + zeros for text)
    """
    norms = _load_norms(norms_path)

    if transcript is None and not skip_asr:
        transcript = transcribe(audio_path, model_size=whisper_model, device=device)
    elif transcript is None:
        transcript = ""

    syllables = count_syllables_chinese(transcript)
    audio = extract_audio_metrics(audio_path, syllable_count=syllables)
    text = extract_text_metrics(transcript)

    metrics = {
        "articulation_rate": audio["articulation_rate"],
        "silent_pause_ratio": audio["silent_pause_ratio"],
        "pitch_sd": audio["pitch_sd"],
        "intensity_sd": audio["intensity_sd"],
        "filled_pause_density": text["filled_pause_density"],
        "repetition_repair_density": text["repetition_repair_density"],
        "type_token_ratio": text["type_token_ratio"],
        "mean_utterance_length": text["mean_utterance_length"],
        "connective_density": text["connective_density"],
        "duration_sec": audio["duration_sec"],
        "speech_duration_sec": audio["speech_duration_sec"],
        "syllable_count": float(syllables),
    }

    scores = compute_dimension_scores(metrics, norms)

    return {
        "audio_path": str(audio_path),
        "transcript": transcript,
        "raw_metrics": metrics,
        "scores": {
            "fluency": scores["fluency"],
            "richness": scores["richness"],
            "vividness": scores["vividness"],
            "total": scores["total"],
        },
        "z_scores": scores["z_scores"],
    }
