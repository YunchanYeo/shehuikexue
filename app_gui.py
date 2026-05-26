#!/usr/bin/env python3
"""Desktop app for Chinese speech evaluation (local, no server)."""

from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import flet as ft

from speech_eval import evaluate_speech
from speech_eval.formatting import format_result


APP_TITLE = "中文口语评估"
WHISPER_OPTIONS = ["tiny", "base", "small", "medium"]


def _detect_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def main(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.window.width = 760
    page.window.height = 820
    page.window.min_width = 640
    page.window.min_height = 680
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.AUTO

    audio_path: list[Path | None] = [None]
    last_result: list[dict[str, Any] | None] = [None]
    busy = [False]
    device = _detect_device()
    device_label = "GPU (CUDA)" if device == "cuda" else "CPU"

    file_label = ft.Text("未选择文件", selectable=True)
    status = ft.Text("就绪", color=ft.Colors.ON_SURFACE_VARIANT)
    progress = ft.ProgressBar(visible=False)
    result_field = ft.TextField(
        value=(
            "使用说明：\n"
            "1. 点击「选择文件」，选择您的录音（支持 wav、mp3、m4a 等）。\n"
            "2. 点击「开始评估」。首次运行可能需要下载语音识别模型。\n"
            "3. 在下方查看流利度、丰富性、生动性与总分。\n\n"
            "所有分析均在本地完成，不会上传到服务器。"
        ),
        multiline=True,
        read_only=True,
        min_lines=18,
        max_lines=24,
        expand=True,
        text_size=14,
    )
    model_dd = ft.Dropdown(
        value="base",
        options=[ft.dropdown.Option(m) for m in WHISPER_OPTIONS],
        width=140,
        label="识别模型",
    )
    manual_cb = ft.Checkbox(label="手动输入转写文本（跳过自动识别）", value=False)
    transcript_field = ft.TextField(
        label="转写文本",
        multiline=True,
        min_lines=3,
        max_lines=4,
        disabled=True,
    )

    def set_result_text(text: str) -> None:
        result_field.value = text
        page.update()

    def set_busy(on: bool, msg: str) -> None:
        busy[0] = on
        run_btn.disabled = on
        pick_btn.disabled = on
        status.value = msg
        progress.visible = on
        page.update()

    def on_pick_result(e: ft.FilePickerResultEvent) -> None:
        if e.files:
            audio_path[0] = Path(e.files[0].path)
            file_label.value = str(audio_path[0])
            page.update()

    def on_save_result(e: ft.FilePickerResultEvent) -> None:
        if e.path and last_result[0]:
            with open(e.path, "w", encoding="utf-8") as f:
                json.dump(last_result[0], f, ensure_ascii=False, indent=2)
            page.open(ft.SnackBar(ft.Text(f"已保存：{e.path}")))

    file_picker = ft.FilePicker(on_result=on_pick_result)
    save_picker = ft.FilePicker(on_result=on_save_result)
    page.overlay.extend([file_picker, save_picker])

    def on_pick_file(_: ft.ControlEvent) -> None:
        file_picker.pick_files(
            dialog_title="选择音频文件",
            allowed_extensions=["wav", "mp3", "m4a", "flac", "ogg", "aac", "wma"],
            allow_multiple=False,
        )

    def on_manual_toggle(_: ft.ControlEvent) -> None:
        transcript_field.disabled = not manual_cb.value
        page.update()

    def on_copy(_: ft.ControlEvent) -> None:
        if result_field.value:
            page.set_clipboard(result_field.value)
            status.value = "已复制到剪贴板"
            page.update()

    def on_save_json(_: ft.ControlEvent) -> None:
        if not last_result[0]:
            page.open(ft.SnackBar(ft.Text("请先完成评估")))
            return
        save_picker.save_file(
            file_name="口语评估结果.json",
            allowed_extensions=["json"],
        )

    def run_eval_job() -> dict[str, Any]:
        path_str = str(audio_path[0])
        whisper_model = model_dd.value or "base"
        transcript: str | None = None
        if manual_cb.value:
            transcript = (transcript_field.value or "").strip()
        return evaluate_speech(
            path_str,
            whisper_model=whisper_model,
            device=device,
            transcript=transcript,
        )

    def on_eval_done(result: dict[str, Any]) -> None:
        last_result[0] = result
        set_result_text(format_result(result, lang="zh"))
        set_busy(False, "完成")

    def on_eval_error(exc: BaseException) -> None:
        set_busy(False, "出错")
        page.open(ft.SnackBar(ft.Text(str(exc))))

    def on_run(_: ft.ControlEvent) -> None:
        if busy[0]:
            return
        if not audio_path[0] or not audio_path[0].is_file():
            page.open(ft.SnackBar(ft.Text("请先选择音频文件")))
            return
        if manual_cb.value and not (transcript_field.value or "").strip():
            page.open(ft.SnackBar(ft.Text("请输入转写文本，或取消「手动输入」")))
            return

        set_busy(True, "正在分析（语音识别与指标计算）…")

        def _done(result: dict[str, Any]) -> None:
            on_eval_done(result)

        def _wrap() -> dict[str, Any]:
            return run_eval_job()

        try:
            page.run_thread(_wrap, _done)
        except TypeError:
            import threading

            def worker() -> None:
                try:
                    r = run_eval_job()
                    page.invoke_async(lambda: on_eval_done(r))
                except Exception as ex:
                    page.invoke_async(lambda: on_eval_error(ex))

            threading.Thread(target=worker, daemon=True).start()

    manual_cb.on_change = on_manual_toggle

    pick_btn = ft.ElevatedButton(
        "选择文件",
        icon=ft.Icons.AUDIO_FILE,
        on_click=on_pick_file,
    )
    run_btn = ft.FilledButton(
        "开始评估",
        icon=ft.Icons.PLAY_ARROW,
        on_click=on_run,
        height=48,
    )

    page.add(
        ft.Text(APP_TITLE, size=24, weight=ft.FontWeight.BOLD),
        ft.Text(
            "选择录音即可评估。全部在本机运行，无需联网服务器。",
            size=13,
            color=ft.Colors.ON_SURFACE_VARIANT,
        ),
        ft.Divider(),
        ft.Row([ft.Column([file_label], expand=True), pick_btn]),
        ft.Row(
            [
                model_dd,
                ft.Text(f"计算设备：{device_label}"),
            ],
            wrap=True,
            spacing=16,
        ),
        manual_cb,
        transcript_field,
        run_btn,
        status,
        progress,
        ft.Row(
            [
                ft.OutlinedButton("保存 JSON", icon=ft.Icons.SAVE, on_click=on_save_json),
                ft.OutlinedButton("复制结果", icon=ft.Icons.COPY, on_click=on_copy),
            ]
        ),
        result_field,
        ft.Text(f"{platform.system()} · 本地运行", size=11, color=ft.Colors.OUTLINE),
    )


if __name__ == "__main__":
    ft.app(main)
