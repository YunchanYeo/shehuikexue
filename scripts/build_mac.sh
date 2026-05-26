#!/usr/bin/env bash
# Build macOS SpeechEval.app + SpeechEval.dmg (run on macOS, Python 3.10–3.12)
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname)" != "Darwin" ]]; then
  echo "错误：请在 macOS 上运行此脚本。"
  exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python 版本: $PY_VER"
if python3 -c "import sys; exit(0 if (3,10) <= sys.version_info[:2] <= (3,12) else 1)"; then
  :
else
  echo "警告：建议使用 Python 3.10–3.12。当前版本可能导致打包失败。"
fi

python3 -m venv .venv-build
source .venv-build/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
pip install pyinstaller

echo ">>> PyInstaller 打包 .app …"
pyinstaller speech_eval.spec --noconfirm --clean

APP_PATH="dist/SpeechEval.app"
DMG_PATH="dist/SpeechEval.dmg"
if [[ ! -d "$APP_PATH" ]]; then
  echo "错误：未找到 $APP_PATH"
  exit 1
fi

echo ">>> 制作 DMG 安装镜像 …"
STAGE="dist/dmg-staging"
rm -rf "$STAGE" "$DMG_PATH"
mkdir -p "$STAGE"
cp -R "$APP_PATH" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

hdiutil create \
  -volname "中文口语评估" \
  -srcfolder "$STAGE" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

rm -rf "$STAGE"

echo ""
echo "=========================================="
echo " 完成"
echo "  - 应用程序: $APP_PATH"
echo "  - 安装镜像: $DMG_PATH   ← 分发给用户"
echo "=========================================="
echo ""
echo "用户安装：双击 DMG → 将「SpeechEval」拖入「应用程序」"
echo "若提示无法打开：系统设置 → 隐私与安全性 → 仍要打开"
echo "（正式发布建议 Apple 开发者账号代码签名与公证）"
echo ""
echo "分发: 将 dist/SpeechEval.dmg 发给用户（网盘 / 邮件 / GitHub Releases 等）"
