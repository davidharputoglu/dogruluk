#!/usr/bin/env bash
# Lancement local sans Docker (Windows via Git Bash / WSL, Linux, Raspberry Pi).
# Usage : ./scripts/run.sh [public|prive] [nom-de-app]
set -e
cd "$(dirname "$0")/.."

export VDF_EDITION="${1:-public}"
[ -n "${2:-}" ] && export VDF_APP_NAME="$2"

python3 -m venv .venv 2>/dev/null || true
if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -q -r requirements.txt
fi

echo "==> ${VDF_APP_NAME:-auto} (edition ${VDF_EDITION}) sur http://localhost:${VDF_PORT:-8000}"
python3 -m uvicorn app.main:app --host "${VDF_HOST:-0.0.0.0}" --port "${VDF_PORT:-8000}"
