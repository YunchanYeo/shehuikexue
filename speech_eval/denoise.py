"""Local noise reduction before analysis (no cloud API)."""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import butter, filtfilt

TARGET_SR = 16000
HIGHPASS_HZ = 80.0


def _highpass(y: np.ndarray, sr: int, cutoff: float = HIGHPASS_HZ) -> np.ndarray:
    if len(y) < 32:
        return y
    nyq = sr / 2.0
    freq = min(cutoff / nyq, 0.99)
    b, a = butter(2, freq, btype="high")
    return filtfilt(b, a, y).astype(np.float32)


def _normalize_peak(y: np.ndarray, peak: float = 0.95) -> np.ndarray:
    max_val = float(np.max(np.abs(y)))
    if max_val < 1e-8:
        return y
    return (y / max_val * peak).astype(np.float32)


def denoise_waveform(
    y: np.ndarray,
    sr: int,
    *,
    strength: float = 0.75,
) -> np.ndarray:
    """
    Reduce background noise while preserving speech.

    strength: 0.0 = no reduction, 1.0 = strongest (default 0.75).
    """
    strength = float(np.clip(strength, 0.0, 1.0))
    if strength <= 0.0 or len(y) < sr // 10:
        return y.astype(np.float32)

    y = _highpass(y, sr)

    import noisereduce as nr

    # Use a short leading segment as noise profile when it is relatively quiet.
    n_noise = min(len(y), int(0.4 * sr))
    noise_clip = y[:n_noise] if n_noise > 0 else None
    rms_head = float(np.sqrt(np.mean(noise_clip**2))) if noise_clip is not None else 0.0
    rms_all = float(np.sqrt(np.mean(y**2)))
    use_stationary = noise_clip is not None and rms_head < rms_all * 0.6

    if use_stationary:
        reduced = nr.reduce_noise(
            y=y,
            sr=sr,
            y_noise=noise_clip,
            stationary=True,
            prop_decrease=strength,
        )
    else:
        reduced = nr.reduce_noise(
            y=y,
            sr=sr,
            stationary=False,
            prop_decrease=strength,
        )

    return _normalize_peak(np.asarray(reduced, dtype=np.float32))


def load_audio(
    path: str | Path,
    *,
    sr: int = TARGET_SR,
    denoise: bool = True,
    denoise_strength: float = 0.75,
) -> tuple[np.ndarray, int]:
    y, sr_out = librosa.load(str(path), sr=sr, mono=True)
    y = y.astype(np.float32)
    if denoise:
        y = denoise_waveform(y, sr_out, strength=denoise_strength)
    return y, sr_out


def write_temp_wav(y: np.ndarray, sr: int) -> str:
    fd, path = tempfile.mkstemp(suffix=".wav", prefix="speech_eval_")
    os.close(fd)
    sf.write(path, y, sr, subtype="PCM_16")
    return path


@contextmanager
def temp_wav_path(y: np.ndarray, sr: int):
    path = write_temp_wav(y, sr)
    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
