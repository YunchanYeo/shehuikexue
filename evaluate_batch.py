#!/usr/bin/env python3
"""Batch-evaluate all speech audio files in a folder."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from speech_eval import evaluate_speech
from speech_eval.formatting import (
    batch_csv_headers,
    format_batch_summary_report,
    result_to_batch_csv_row,
    write_batch_excel,
)
from speech_eval.norms import cohort_size, load_norms
from speech_eval.paths import default_norms_path

AUDIO_GLOB = ("*.wav", "*.mp3", "*.m4a", "*.flac", "*.ogg", "*.aac", "*.wma")
DEFAULT_CSV_NAME = "评估汇总表.csv"
DEFAULT_XLSX_NAME = "评估汇总表.xlsx"
DEFAULT_REPORT_NAME = "评估汇总说明.txt"
DEFAULT_JSON_DIR_NAME = "结果_json"


def _collect_audio_files(folder: Path, recursive: bool) -> list[Path]:
    files: list[Path] = []
    for pattern in AUDIO_GLOB:
        files.extend(folder.rglob(pattern) if recursive else folder.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="批量评估文件夹内的口语录音（本地，无云端 LLM）。"
    )
    parser.add_argument(
        "audio_dir",
        type=Path,
        help="包含多条口语录音的文件夹",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help=f"为每个文件保存 JSON 的目录（默认: <audio_dir>/{DEFAULT_JSON_DIR_NAME}）",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help=f"汇总 CSV 路径（默认: <audio_dir>/{DEFAULT_CSV_NAME}）",
    )
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=None,
        help=f"汇总 Excel 路径（默认: <audio_dir>/{DEFAULT_XLSX_NAME}）",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help=f"可读文字汇总（默认: <audio_dir>/{DEFAULT_REPORT_NAME}）",
    )
    parser.add_argument(
        "--combined",
        type=Path,
        default=None,
        help="可选：将所有结果写入一个 JSON 文件",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="包含子文件夹",
    )
    parser.add_argument(
        "--norms",
        type=Path,
        default=None,
        help="Z 分常模 YAML（默认: speech_eval/norms.yaml）",
    )
    parser.add_argument("--whisper-model", default="base")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--no-denoise", action="store_true")
    parser.add_argument(
        "--denoise-strength",
        type=float,
        default=0.75,
        help="降噪强度 0.0–1.0（默认 0.75）",
    )
    args = parser.parse_args()

    if not args.audio_dir.is_dir():
        print(f"文件夹不存在: {args.audio_dir}", file=sys.stderr)
        return 1

    paths = _collect_audio_files(args.audio_dir, args.recursive)
    if not paths:
        print(f"未找到音频文件: {args.audio_dir}", file=sys.stderr)
        return 1

    norms_path = args.norms or default_norms_path()
    norms = load_norms(norms_path)
    csv_path = args.csv or (args.audio_dir / DEFAULT_CSV_NAME)
    xlsx_path = args.xlsx or (args.audio_dir / DEFAULT_XLSX_NAME)
    report_path = args.report or (args.audio_dir / DEFAULT_REPORT_NAME)
    output_dir = args.output_dir or (args.audio_dir / DEFAULT_JSON_DIR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    denoise_strength = max(0.0, min(1.0, args.denoise_strength))
    print(f"找到 {len(paths)} 个文件，开始评估…")
    print(f"常模: {norms_path}")

    rows: list[dict[str, str]] = []
    combined: list[dict] = []
    ok_count = 0
    err_count = 0

    for i, path in enumerate(paths, 1):
        print(f"  [{i}/{len(paths)}] {path.name}", end="", flush=True)
        try:
            result = evaluate_speech(
                str(path),
                norms_path=norms_path,
                whisper_model=args.whisper_model,
                device=args.device,
                denoise=not args.no_denoise,
                denoise_strength=denoise_strength,
            )
            rows.append(result_to_batch_csv_row(result, path, index=i))
            combined.append(result)
            ok_count += 1
            s = result["scores"]
            print(f"  → 总分 {s['total']:.3f}")

            out_json = output_dir / f"{path.stem}.json"
            out_json.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            err_count += 1
            rows.append(result_to_batch_csv_row(None, path, index=i, error=str(exc)))
            combined.append(
                {
                    "audio_path": str(path),
                    "status": "error",
                    "error": str(exc),
                }
            )
            print(f"  → 失败: {exc}", file=sys.stderr)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    headers = batch_csv_headers()
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    report_text = format_batch_summary_report(
        rows,
        audio_dir=str(args.audio_dir.resolve()),
        norms_path=str(norms_path),
        cohort_n=cohort_size(norms),
        ok_count=ok_count,
        err_count=err_count,
    )
    report_path.write_text(report_text, encoding="utf-8")

    write_batch_excel(
        rows,
        xlsx_path,
        audio_dir=str(args.audio_dir.resolve()),
        norms_path=str(norms_path),
        cohort_n=cohort_size(norms),
        ok_count=ok_count,
        err_count=err_count,
    )

    if args.combined is not None:
        args.combined.parent.mkdir(parents=True, exist_ok=True)
        args.combined.write_text(
            json.dumps(combined, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print()
    print(f"完成: 成功 {ok_count}，失败 {err_count}")
    print(f"汇总 Excel: {xlsx_path}")
    print(f"汇总 CSV:   {csv_path}")
    print(f"可读说明:   {report_path}")
    print(f"单文件 JSON: {output_dir}/")
    if args.combined is not None:
        print(f"合并 JSON:  {args.combined}")

    return 1 if err_count and not ok_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
