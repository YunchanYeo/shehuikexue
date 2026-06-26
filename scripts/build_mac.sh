#!/usr/bin/env bash
# Mac 本地生成 SpeechEval.dmg（使用 flet pack，含桌面运行时）
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname)" != "Darwin" ]]; then
  echo "请在 macOS 上运行。"
  exit 1
fi

PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3; do
  if command -v "$cmd" &>/dev/null; then
    if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
      PYTHON="$cmd"
      break
    fi
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo "需要 Python 3.10+: https://www.python.org/downloads/"
  exit 1
fi

echo "使用: $($PYTHON --version)"

rm -rf dist/SpeechEval.app dist/SpeechEval dist/SpeechEval.dmg build 2>/dev/null || true
[[ -d .venv-build ]] || rm -rf .venv-build 2>/dev/null || true
deactivate 2>/dev/null || true
rm -rf .venv-build
"$PYTHON" -m venv .venv-build
source .venv-build/bin/activate
pip install -U pip wheel -q
pip install -r requirements.txt "flet[all]" pyinstaller -q

echo ""
echo ">>> 正在打包（约 15–25 分钟）…"
flet pack app_gui.py \
  -n SpeechEval \
  --product-name "中文口语评估" \
  --bundle-id com.kouyu.speecheval \
  --add-data "speech_eval/norms.yaml:speech_eval" \
  --hidden-import speech_eval \
  --hidden-import speech_eval.scoring \
  --hidden-import speech_eval.asr \
  --hidden-import speech_eval.audio_metrics \
  --hidden-import speech_eval.text_metrics \
  --hidden-import speech_eval.formatting \
  --hidden-import speech_eval.paths \
  --hidden-import speech_eval.denoise \
  --hidden-import speech_eval.formatting \
  --hidden-import faster_whisper \
  --hidden-import jieba \
  --hidden-import noisereduce \
  --hidden-import zhconv \
  --hidden-import speech_eval.zh_convert \
  -y

APP_PATH="dist/SpeechEval.app"
if [[ ! -d "$APP_PATH" ]]; then
  # flet pack 有时使用产品名作为 .app 名称
  ALT=$(find dist -maxdepth 1 -name "*.app" -print -quit 2>/dev/null || true)
  if [[ -n "$ALT" && -d "$ALT" ]]; then
    APP_PATH="$ALT"
    echo "使用: $APP_PATH"
  else
    echo "错误：未找到 .app，请检查 dist/ 目录"
    exit 1
  fi
fi

echo ">>> 正在制作 DMG …"
STAGE="dist/dmg-staging"
rm -rf "$STAGE" dist/SpeechEval.dmg
mkdir -p "$STAGE"
cp -R "$APP_PATH" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "中文口语评估" -srcfolder "$STAGE" -ov -format UDZO dist/SpeechEval.dmg >/dev/null
rm -rf "$STAGE"

DESKTOP_DMG="$HOME/Desktop/SpeechEval.dmg"
cp -f dist/SpeechEval.dmg "$DESKTOP_DMG"

echo ""
echo "=========================================="
echo " 完成！"
echo "  桌面: $DESKTOP_DMG"
echo "=========================================="
open -R "$DESKTOP_DMG" 2>/dev/null || true
