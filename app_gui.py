#!/usr/bin/env python3
"""Desktop app for Chinese speech evaluation (local, no server)."""

from __future__ import annotations

import json
import platform
import threading
from pathlib import Path
from typing import Any

import flet as ft
from flet.controls.services.file_picker import FilePickerFileType

from speech_eval import evaluate_speech
from speech_eval.formatting import format_filename_display, format_result


APP_TITLE = "中文口语评估"
WHISPER_OPTIONS = ["tiny", "base", "small", "medium"]
AUDIO_EXTENSIONS = ["wav", "mp3", "m4a", "flac", "ogg", "aac", "wma"]


def _detect_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def _section(title: str, *controls: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, size=14, weight=ft.FontWeight.W_600),
                *controls,
            ],
            spacing=12,
        ),
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.ON_SURFACE),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE)),
    )


def _score_card(label: str, value: ft.Text) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                value,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=12,
        border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.PRIMARY),
        expand=True,
    )


async def main(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.window.width = 800
    page.window.height = 880
    page.window.min_width = 680
    page.window.min_height = 720
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 20
    page.spacing = 16

    audio_path: list[Path | None] = [None]
    last_result: list[dict[str, Any] | None] = [None]
    busy = [False]
    device = _detect_device()
    device_label = "GPU" if device == "cuda" else "CPU"

    # —— 状态与结果展示 ——
    file_name_text = ft.Text(
        "尚未选择录音",
        size=15,
        weight=ft.FontWeight.W_500,
    )
    file_hint_text = ft.Text(
        "支持 wav、mp3、m4a、flac 等格式",
        size=12,
        color=ft.Colors.ON_SURFACE_VARIANT,
    )
    status_text = ft.Text("就绪", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
    progress = ft.ProgressBar(visible=False)

    score_fluency = ft.Text("—", size=22, weight=ft.FontWeight.BOLD)
    score_richness = ft.Text("—", size=22, weight=ft.FontWeight.BOLD)
    score_vividness = ft.Text("—", size=22, weight=ft.FontWeight.BOLD)
    score_total = ft.Text("—", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)

    score_row = ft.Row(
        [
            _score_card("流利度", score_fluency),
            _score_card("丰富性", score_richness),
            _score_card("生动性", score_vividness),
            _score_card("总分", score_total),
        ],
        spacing=10,
        visible=False,
    )

    result_field = ft.TextField(
        value="完成评估后，详细指标将显示在这里。",
        multiline=True,
        read_only=True,
        min_lines=12,
        max_lines=16,
        expand=True,
        text_size=13,
        border_radius=8,
    )

    model_dd = ft.Dropdown(
        value="base",
        options=[ft.dropdown.Option(m) for m in WHISPER_OPTIONS],
        width=200,
        label="识别模型",
        dense=True,
    )
    denoise_cb = ft.Checkbox(
        label="降噪处理（减少背景杂音，推荐开启）",
        value=True,
    )
    manual_cb = ft.Checkbox(label="手动输入转写（跳过语音识别）", value=False)
    transcript_field = ft.TextField(
        label="转写文本",
        hint_text="仅在勾选「手动输入」时填写",
        multiline=True,
        min_lines=3,
        max_lines=5,
        disabled=True,
        border_radius=8,
    )

    save_txt_btn = ft.OutlinedButton("下载 TXT", icon=ft.Icons.DESCRIPTION, disabled=True)
    save_btn = ft.OutlinedButton("保存 JSON", icon=ft.Icons.SAVE, disabled=True)
    copy_btn = ft.OutlinedButton("复制报告", icon=ft.Icons.COPY, disabled=True)

    def set_status(msg: str) -> None:
        status_text.value = msg
        page.update()

    def set_busy(on: bool, msg: str) -> None:
        busy[0] = on
        run_btn.disabled = on
        pick_btn.disabled = on
        status_text.value = msg
        progress.visible = on
        page.update()

    def set_has_result(has_result: bool) -> None:
        save_txt_btn.disabled = not has_result
        save_btn.disabled = not has_result
        copy_btn.disabled = not has_result
        score_row.visible = has_result

    def update_file_display() -> None:
        if audio_path[0]:
            file_name_text.value = format_filename_display(str(audio_path[0]))
            file_hint_text.value = str(audio_path[0])
        else:
            file_name_text.value = "尚未选择录音"
            file_hint_text.value = "支持 wav、mp3、m4a、flac 等格式"
        page.update()

    def show_scores(result: dict[str, Any]) -> None:
        s = result["scores"]
        score_fluency.value = f"{s['fluency']:.2f}"
        score_richness.value = f"{s['richness']:.2f}"
        score_vividness.value = f"{s['vividness']:.2f}"
        score_total.value = f"{s['total']:.2f}"
        set_has_result(True)

    async def on_pick_file(_: ft.ControlEvent) -> None:
        files = await ft.FilePicker().pick_files(
            dialog_title="选择中文口语录音",
            file_type=FilePickerFileType.CUSTOM,
            allowed_extensions=AUDIO_EXTENSIONS,
            allow_multiple=False,
        )
        if files and files[0].path:
            audio_path[0] = Path(files[0].path)
            update_file_display()
            set_status("已选择文件，可以开始评估")

    def on_manual_toggle(_: ft.ControlEvent) -> None:
        transcript_field.disabled = not manual_cb.value
        page.update()

    def on_copy(_: ft.ControlEvent) -> None:
        if result_field.value:
            page.set_clipboard(result_field.value)
            set_status("报告已复制到剪贴板")

    async def on_save_txt(_: ft.ControlEvent) -> None:
        if not last_result[0]:
            set_status("请先完成评估")
            return
        path = await ft.FilePicker().save_file(
            dialog_title="保存文本报告",
            file_name="口语评估结果.txt",
            file_type=FilePickerFileType.CUSTOM,
            allowed_extensions=["txt"],
        )
        if path:
            text = format_result(last_result[0], lang="zh")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            set_status(f"已保存 TXT：{path}")

    async def on_save_json(_: ft.ControlEvent) -> None:
        if not last_result[0]:
            set_status("请先完成评估")
            return
        path = await ft.FilePicker().save_file(
            dialog_title="保存 JSON",
            file_name="口语评估结果.json",
            file_type=FilePickerFileType.CUSTOM,
            allowed_extensions=["json"],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(last_result[0], f, ensure_ascii=False, indent=2)
            set_status(f"已保存 JSON：{path}")

    def run_eval_job() -> dict[str, Any]:
        return evaluate_speech(
            str(audio_path[0]),
            whisper_model=model_dd.value or "base",
            device=device,
            transcript=(transcript_field.value or "").strip() if manual_cb.value else None,
            denoise=denoise_cb.value,
        )

    def on_eval_done(result: dict[str, Any]) -> None:
        last_result[0] = result
        result_field.value = format_result(result, lang="zh")
        show_scores(result)
        set_busy(False, "评估完成")
        page.update()

    def on_eval_error(exc: BaseException) -> None:
        set_busy(False, "评估失败")
        result_field.value = f"出错：{exc}\n\n请检查音频文件，或尝试更小的识别模型（tiny）。"
        page.update()

    async def on_run(_: ft.ControlEvent) -> None:
        if busy[0]:
            return
        if not audio_path[0] or not audio_path[0].is_file():
            set_status("请先点击「选择录音文件」")
            return
        if manual_cb.value and not (transcript_field.value or "").strip():
            set_status("请填写转写文本，或取消「手动输入」")
            return

        set_has_result(False)
        score_fluency.value = "…"
        score_richness.value = "…"
        score_vividness.value = "…"
        score_total.value = "…"
        score_row.visible = True
        msg = "正在降噪、识别与分析，请稍候…" if denoise_cb.value else "正在识别与分析，请稍候…"
        set_busy(True, msg)

        def worker() -> None:
            try:
                result = run_eval_job()

                async def done() -> None:
                    on_eval_done(result)

                page.run_task(done)
            except Exception as exc:

                async def fail() -> None:
                    on_eval_error(exc)

                page.run_task(fail)

        threading.Thread(target=worker, daemon=True).start()

    manual_cb.on_change = on_manual_toggle
    save_txt_btn.on_click = on_save_txt
    save_btn.on_click = on_save_json
    copy_btn.on_click = on_copy

    pick_btn = ft.OutlinedButton(
        "选择录音文件",
        icon=ft.Icons.AUDIO_FILE,
        on_click=on_pick_file,
    )
    run_btn = ft.Button(
        "开始评估",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        on_click=on_run,
        height=48,
        expand=True,
    )

    page.add(
        ft.Row(
            [
                ft.Icon(ft.Icons.RECORD_VOICE_OVER, size=32, color=ft.Colors.PRIMARY),
                ft.Column(
                    [
                        ft.Text(APP_TITLE, size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            "本地分析 · 不上传服务器",
                            size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        _section(
            "① 选择录音",
            ft.Row(
                [
                    ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Column(
                        [file_name_text, file_hint_text],
                        expand=True,
                        spacing=2,
                    ),
                    pick_btn,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
        _section(
            "② 评估设置",
            denoise_cb,
            ft.ExpansionTile(
                title="高级选项",
                subtitle=f"识别模型 · 计算设备 {device_label}",
                controls=[
                    model_dd,
                    manual_cb,
                    transcript_field,
                ],
                expanded=False,
            ),
            ft.Row([run_btn], spacing=12),
            status_text,
            progress,
        ),
        score_row,
        _section(
            "③ 评估结果",
            ft.Row(
                [save_txt_btn, save_btn, copy_btn],
                spacing=10,
                wrap=True,
            ),
            result_field,
        ),
        ft.Text(
            "首次使用需下载语音识别模型 · 约需数分钟",
            size=11,
            color=ft.Colors.OUTLINE,
            text_align=ft.TextAlign.CENTER,
        ),
    )


if __name__ == "__main__":
    import sys

    # --web: 브라우저에서 실행（flet-desktop 클라이언트 다운로드 불필요）
    view = (
        ft.AppView.WEB_BROWSER
        if "--web" in sys.argv
        else ft.AppView.FLET_APP
    )
    ft.run(main, view=view)
