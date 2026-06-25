#!/usr/bin/env bash
# Run GUI in dev (no build)
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
source .venv/bin/activate
if [[ "${1:-}" == "web" ]]; then
  python app_gui.py --web
else
  python app_gui.py || {
    echo ""
    echo "데스크톱 클라이언트 다운로드 실패 시 브라우저 모드로 재시도합니다…"
    python app_gui.py --web
  }
fi
