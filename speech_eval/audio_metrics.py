"""Acoustic metrics from waveform (no LLM)."""

from __future__ import annotations

import numpy as np
import librosa

from .denoise import load_audio


SILENCE_THRESHOLD_DB = 35  # frames below peak-RMS by this dB count as silent
MIN_PAUSE_SEC = 0.2
FRAME_LENGTH = 2048
HOP_LENGTH = 512


def _rms_frames(y: np.ndarray, sr: int) -> tuple[np.ndarray, float]:
    rms = librosa.feature.rms(y=y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP_LENGTH)
    return rms, float(times[1] - times[0]) if len(times) > 1 else FRAME_LENGTH / sr


def _silent_mask(rms: np.ndarray) -> np.ndarray:
    peak = np.max(rms) if np.max(rms) > 0 else 1e-10
    threshold = peak * (10 ** (-SILENCE_THRESHOLD_DB / 20))
    return rms < threshold


def _pause_segments(mask: np.ndarray, frame_dt: float) -> list[tuple[float, float]]:
    segments: list[tuple[float, float]] = []
    start: int | None = None
    for i, is_silent in enumerate(mask):
        if is_silent and start is None:
            start = i
        elif not is_silent and start is not None:
            dur = (i - start) * frame_dt
            if dur >= MIN_PAUSE_SEC:
                segments.append((start * frame_dt, i * frame_dt))
            start = None
    if start is not None:
        end = len(mask)
        dur = (end - start) * frame_dt
        if dur >= MIN_PAUSE_SEC:
            segments.append((start * frame_dt, end * frame_dt))
    return segments


def silent_pause_ratio(y: np.ndarray, sr: int) -> float:
    """Share of total duration in silent pauses longer than 0.2s."""
    total_dur = len(y) / sr
    if total_dur <= 0:
        return 0.0
    rms, frame_dt = _rms_frames(y, sr)
    pauses = _pause_segments(_silent_mask(rms), frame_dt)
    pause_time = sum(end - start for start, end in pauses)
    return float(min(1.0, pause_time / total_dur))


def speech_duration(y: np.ndarray, sr: int) -> float:
    """Total duration minus long silent pauses (for articulation rate)."""
    total_dur = len(y) / sr
    rms, frame_dt = _rms_frames(y, sr)
    pauses = _pause_segments(_silent_mask(rms), frame_dt)
    pause_time = sum(end - start for start, end in pauses)
    return max(total_dur - pause_time, 0.01)


def articulation_rate(syllable_count: int, y: np.ndarray, sr: int) -> float:
    """Syllables per second in speech-only regions."""
    dur = speech_duration(y, sr)
    return syllable_count / dur


def pitch_sd(y: np.ndarray, sr: int) -> float:
    """Standard deviation of F0 (Hz) on voiced frames."""
    f0 = librosa.yin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        frame_length=FRAME_LENGTH,
    )
    voiced = f0[(f0 > 0) & np.isfinite(f0)]
    if len(voiced) < 3:
        return 0.0
    return float(np.std(voiced))


def intensity_sd(y: np.ndarray, sr: int) -> float:
    """Standard deviation of RMS energy (linear scale)."""
    rms, _ = _rms_frames(y, sr)
    if len(rms) < 2:
        return 0.0
    return float(np.std(rms))


def extract_audio_metrics_from_array(
    y: np.ndarray, sr: int, syllable_count: int
) -> dict[str, float]:
    return {
        "articulation_rate": articulation_rate(syllable_count, y, sr),
        "silent_pause_ratio": silent_pause_ratio(y, sr),
        "pitch_sd": pitch_sd(y, sr),
        "intensity_sd": intensity_sd(y, sr),
        "duration_sec": len(y) / sr,
        "speech_duration_sec": speech_duration(y, sr),
    }


def extract_audio_metrics(
    path: str,
    syllable_count: int,
    *,
    denoise: bool = True,
    denoise_strength: float = 0.75,
) -> dict[str, float]:
    y, sr = load_audio(path, denoise=denoise, denoise_strength=denoise_strength)
    return extract_audio_metrics_from_array(y, sr, syllable_count)
