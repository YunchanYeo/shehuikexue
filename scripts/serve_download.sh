#!/usr/bin/env bash
# Local preview of the download page (http://localhost:8080)
set -euo pipefail
cd "$(dirname "$0")/../website"
echo "下载页: http://127.0.0.1:8080"
echo "按 Ctrl+C 停止"
python3 -m http.server 8080
