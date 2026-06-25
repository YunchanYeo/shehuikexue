# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('speech_eval/norms.yaml', 'speech_eval')],
    hiddenimports=['speech_eval', 'speech_eval.scoring', 'speech_eval.asr', 'speech_eval.audio_metrics', 'speech_eval.text_metrics', 'speech_eval.formatting', 'speech_eval.paths', 'speech_eval.denoise', 'speech_eval.formatting', 'faster_whisper', 'jieba', 'noisereduce'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SpeechEval',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='SpeechEval.app',
    icon=None,
    bundle_identifier='com.shehuikexue.speecheval',
)
