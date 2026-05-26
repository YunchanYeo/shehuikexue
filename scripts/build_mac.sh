#!/usr/bin/env bash
# Mac 本地一键生成 SpeechEval.dmg（无需 GitHub）
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname)" != "Darwin" ]]; then
  echo "请在 macOS 上运行。"
  exit 1
fi

# 优先使用 3.10–3.12（PyInstaller 兼容更好）
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
  echo "需要 Python 3.10 或更高: https://www.python.org/downloads/"
  exit 1
fi

echo "使用: $($PYTHON --version)"

rm -rf .venv-build
"$PYTHON" -m venv .venv-build
source .venv-build/bin/activate
pip install -U pip wheel -q
pip install -r requirements.txt pyinstaller -q

echo ""
echo ">>> 正在打包应用（约 10–20 分钟，请耐心等待）…"
pyinstaller speech_eval.spec --noconfirm --clean

APP_PATH="dist/SpeechEval.app"
DMG_PATH="dist/SpeechEval.dmg"
if [[ ! -d "$APP_PATH" ]]; then
  echo "错误：未生成 $APP_PATH"
  exit 1
fi

echo ">>> 正在制作 DMG …"
STAGE="dist/dmg-staging"
rm -rf "$STAGE" "$DMG_PATH"
mkdir -p "$STAGE"
cp -R "$APP_PATH" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "中文口语评估" -srcfolder "$STAGE" -ov -format UDZO "$DMG_PATH" >/dev/null
rm -rf "$STAGE"

DESKTOP_DMG="$HOME/Desktop/SpeechEval.dmg"
cp -f "$DMG_PATH" "$DESKTOP_DMG"

echo ""
echo "=========================================="
echo " 完成！"
echo "  安装包: $DMG_PATH"
echo "  已复制到桌面: $DESKTOP_DMG"
echo "=========================================="
echo "双击桌面上的 SpeechEval.dmg 即可安装。"

open -R "$DESKTOP_DMG" 2>/dev/null || open dist
