#!/usr/bin/env python3
"""Build norms.yaml (mean/std) from many audio files — required for valid Z-scores."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from speech_eval.norms import compute_norms_from_rows, save_norms
from speech_eval.paths import default_norms_path
from speech_eval.scoring import extract_raw_metrics

AUDIO_GLOB = ("*.wav", "*.mp3", "*.m4a", "*.flac", "*.ogg", "*.aac", "*.wma")


def _collect_audio_files(folder: Path, recursive: bool) -> list[Path]:
    files: list[Path] = []
    for pattern in AUDIO_GLOB:
        files.extend(folder.rglob(pattern) if recursive else folder.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "从多条录音计算各指标均值/标准差，写入 norms.yaml。"
            "单条录音无法得到总体标准差，不能对单文件做 Z 分常模。"
        )
    )
    parser.add_argument(
        "audio_dir",
        type=Path,
        help="包含多条口语录音的文件夹",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出的 norms YAML（默认: speech_eval/norms.yaml）",
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="包含子文件夹")
    parser.add_argument("--whisper-model", default="base")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--no-denoise", action="store_true")
    args = parser.parse_args()

    if not args.audio_dir.is_dir():
        print(f"文件夹不存在: {args.audio_dir}", file=sys.stderr)
        return 1

    paths = _collect_audio_files(args.audio_dir, args.recursive)
    if not paths:
        print(f"未找到音频文件: {args.audio_dir}", file=sys.stderr)
        return 1

    print(f"找到 {len(paths)} 个文件，正在提取原始指标…")
    rows: list[dict[str, float]] = []
    for i, path in enumerate(paths, 1):
        print(f"  [{i}/{len(paths)}] {path.name}")
        try:
            metrics, _ = extract_raw_metrics(
                str(path),
                whisper_model=args.whisper_model,
                device=args.device,
                denoise=not args.no_denoise,
            )
            rows.append(metrics)
        except Exception as exc:
            print(f"    跳过（出错）: {exc}", file=sys.stderr)

    if len(rows) < 2:
        print(
            f"成功处理 {len(rows)} 条，至少需要 2 条才能计算标准差。",
            file=sys.stderr,
        )
        return 1

    norms = compute_norms_from_rows(rows, source=str(args.audio_dir.resolve()))
    out = args.output or default_norms_path()
    save_norms(norms, out)
    print(f"\n已写入常模: {out}")
    print(f"  样本数: {norms['_meta']['n_samples']}")
    print("之后评估单条录音时请使用: python evaluate.py 录音.wav --norms", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
