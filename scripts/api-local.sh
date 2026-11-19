#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"

"$root/scripts/db-up.sh"

uvicorn="$root/apps/api/.venv/bin/uvicorn"

if [[ ! -x "$uvicorn" ]]; then
  echo "Сначала скачайте зависимости: pnpm deps" >&2
  exit 1
fi

cd "$root/apps/api"
exec "$uvicorn" app.main:app --reload --host 127.0.0.1 --port 8000
