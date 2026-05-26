"""Local speech-to-text via faster-whisper (no cloud LLM API)."""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=2)
def _get_model(model_size: str, device: str):
    from faster_whisper import WhisperModel

    compute_type = "int8" if device == "cpu" else "float16"
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def transcribe(
    audio_path: str,
    model_size: str = "base",
    device: str = "cpu",
    language: str = "zh",
) -> str:
    model = _get_model(model_size, device)
    segments, _ = model.transcribe(
        audio_path,
        language=language,
        vad_filter=True,
        beam_size=5,
    )
    return "".join(seg.text.strip() for seg in segments).strip()
