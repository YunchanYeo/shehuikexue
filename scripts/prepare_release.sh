#!/usr/bin/env bash
# Copy built installers to website/releases/ for the download page
set -euo pipefail
cd "$(dirname "$0")/.."

DEST="website/releases"
mkdir -p "$DEST"

if [[ -f dist/SpeechEval.dmg ]]; then
  cp -f dist/SpeechEval.dmg "$DEST/"
  echo "已复制: $DEST/SpeechEval.dmg"
else
  echo "跳过: dist/SpeechEval.dmg 不存在（请先运行 ./scripts/build_mac.sh）"
fi

if [[ -f dist/SpeechEval-Setup.exe ]]; then
  cp -f dist/SpeechEval-Setup.exe "$DEST/"
  echo "已复制: $DEST/SpeechEval-Setup.exe"
else
  echo "跳过: dist/SpeechEval-Setup.exe 不存在（请在 Windows 上构建）"
fi

echo ""
echo "下载页: 用浏览器打开 website/index.html"
echo "或运行: ./scripts/serve_download.sh"
