#!/usr/bin/env bash
set -euo pipefail
set -m

root="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -x "$root/apps/api/.venv/bin/uvicorn" || ! -d "$root/apps/web/node_modules" ]]; then
  "$root/scripts/deps.sh"
fi

cleanup() {
  trap - EXIT INT TERM

  if [[ -n "${api_pid:-}" ]]; then
    kill -- "-$api_pid" 2>/dev/null || kill "$api_pid" 2>/dev/null || true
  fi

  if [[ -n "${web_pid:-}" ]]; then
    kill -- "-$web_pid" 2>/dev/null || kill "$web_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

echo "API  http://127.0.0.1:8000"
echo "Web  http://127.0.0.1:5173"

"$root/scripts/api-local.sh" &
api_pid=$!

(
  cd "$root/apps/web"
  exec pnpm dev
) &
web_pid=$!

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$web_pid" 2>/dev/null; do
  sleep 1
done

exit 1
