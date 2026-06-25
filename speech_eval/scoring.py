"""Composite scores with Z-normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .asr import transcribe
from .audio_metrics import extract_audio_metrics_from_array
from .denoise import load_audio, temp_wav_path
from .norms import cohort_size, is_calibrated, load_norms, metric_norms
from .paths import default_norms_path
from .text_metrics import count_syllables_chinese, extract_text_metrics
from .zh_convert import to_simplified


def z_score(value: float, mean: float, std: float) -> float:
    if std <= 0:
        return 0.0
    return (value - mean) / std


def _z(metric: str, value: float, norms: dict) -> float:
    cfg = metric_norms(norms, metric)
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


def extract_raw_metrics(
    audio_path: str,
    *,
    whisper_model: str = "base",
    device: str = "cpu",
    transcript: str | None = None,
    skip_asr: bool = False,
    denoise: bool = True,
    denoise_strength: float = 0.75,
) -> tuple[dict[str, float], str]:
    """Run ASR (if needed) and return raw metrics + transcript."""
    y, sr = load_audio(
        audio_path,
        denoise=denoise,
        denoise_strength=denoise_strength,
    )

    if transcript is None and not skip_asr:
        with temp_wav_path(y, sr) as clean_path:
            transcript = transcribe(
                clean_path,
                model_size=whisper_model,
                device=device,
            )
    elif transcript is None:
        transcript = ""

    if transcript:
        transcript = to_simplified(transcript)

    syllables = count_syllables_chinese(transcript)
    audio = extract_audio_metrics_from_array(y, sr, syllable_count=syllables)
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
        "denoise_applied": 1.0 if denoise else 0.0,
    }
    return metrics, transcript


def evaluate_speech(
    audio_path: str,
    *,
    norms_path: str | Path | None = None,
    whisper_model: str = "base",
    device: str = "cpu",
    transcript: str | None = None,
    skip_asr: bool = False,
    denoise: bool = True,
    denoise_strength: float = 0.75,
) -> dict[str, Any]:
    """
    Evaluate one speech audio file.

    Z-scores use population mean/std from norms.yaml (many samples), not from
    this file alone. Calibrate with calibrate_norms.py first.
    """
    if norms_path is None:
        norms_path = default_norms_path()
    norms = load_norms(norms_path)

    metrics, transcript = extract_raw_metrics(
        audio_path,
        whisper_model=whisper_model,
        device=device,
        transcript=transcript,
        skip_asr=skip_asr,
        denoise=denoise,
        denoise_strength=denoise_strength,
    )

    scores = compute_dimension_scores(metrics, norms)

    return {
        "audio_path": str(audio_path),
        "transcript": transcript,
        "denoise": denoise,
        "denoise_strength": denoise_strength if denoise else 0.0,
        "raw_metrics": metrics,
        "scores": {
            "fluency": scores["fluency"],
            "richness": scores["richness"],
            "vividness": scores["vividness"],
            "total": scores["total"],
        },
        "z_scores": scores["z_scores"],
        "norms": {
            "path": str(norms_path),
            "cohort_n": cohort_size(norms),
            "calibrated": is_calibrated(norms),
        },
    }
