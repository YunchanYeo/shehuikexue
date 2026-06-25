"""Traditional → simplified Chinese normalization for transcripts."""

from __future__ import annotations


def to_simplified(text: str) -> str:
    """Convert Chinese text to simplified characters (Whisper often outputs 繁体)."""
    if not text or not text.strip():
        return text
    try:
        import zhconv
    except ImportError:
        return text
    return zhconv.convert(text, "zh-cn")
