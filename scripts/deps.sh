#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! -d "$root/apps/api/.venv" ]]; then
  python3 -m venv "$root/apps/api/.venv"
fi

(
  cd "$root/apps/api"
  .venv/bin/pip install -e ".[dev]"
)

(
  cd "$root/apps/web"
  pnpm install
)
