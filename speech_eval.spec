# -*- mode: python ; coding: utf-8 -*-
# PyInstaller: build on the target OS (Mac on Mac, Windows on Windows).
#   macOS:   ./scripts/build_mac.sh
#   Windows: scripts\build_windows.bat

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

root = Path(SPECPATH)

block_cipher = None

jieba_datas = collect_data_files("jieba")
pkg_datas = [(str(root / "speech_eval" / "norms.yaml"), "speech_eval")]

flet_datas, flet_binaries, flet_hidden = collect_all("flet")

hidden = [
    "faster_whisper",
    "ctranslate2",
    "yaml",
    "scipy.special.cython_special",
    "audioread",
    "soundfile",
    "resampy",
    "numba",
    "llvmlite",
]
hidden += flet_hidden
hidden += collect_submodules("librosa")

a = Analysis(
    ["app_gui.py"],
    pathex=[str(root)],
    binaries=flet_binaries,
    datas=jieba_datas + pkg_datas + flet_datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pandas", "tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SpeechEval",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SpeechEval",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="SpeechEval.app",
        icon=None,
        bundle_identifier="com.shehuikexue.speecheval",
        info_plist={
            "CFBundleDisplayName": "中文口语评估",
            "NSHighResolutionCapable": True,
        },
    )
