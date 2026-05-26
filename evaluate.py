#!/usr/bin/env python3
"""CLI for Chinese speech evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from speech_eval import evaluate_speech
from speech_eval.formatting import format_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate Chinese speech: fluency, richness, vividness (local, no cloud LLM)."
    )
    parser.add_argument("audio", type=Path, help="Path to speech audio file")
    parser.add_argument(
        "--norms",
        type=Path,
        default=None,
        help="YAML file with population mean/std for Z-scores (default: speech_eval/norms.yaml)",
    )
    parser.add_argument(
        "--transcript",
        type=str,
        default=None,
        help="Skip ASR if you already have the transcript",
    )
    parser.add_argument(
        "--whisper-model",
        default="base",
        help="faster-whisper model size: tiny, base, small, medium, large-v3",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Inference device for ASR",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full result as JSON",
    )
    args = parser.parse_args()

    if not args.audio.is_file():
        print(f"File not found: {args.audio}", file=sys.stderr)
        return 1

    result = evaluate_speech(
        str(args.audio),
        norms_path=args.norms,
        whisper_model=args.whisper_model,
        device=args.device,
        transcript=args.transcript,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(format_result(result, lang="zh"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
