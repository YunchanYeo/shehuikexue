#!/bin/bash
# 双击此文件即可在 Mac 上生成 SpeechEval.dmg（无需 GitHub）
cd "$(dirname "$0")"
chmod +x scripts/build_mac.sh
./scripts/build_mac.sh
echo ""
read -p "按回车键关闭窗口…"
