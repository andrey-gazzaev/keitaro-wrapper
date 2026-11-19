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

(
  cd "$root"
  UV_PROJECT_ENVIRONMENT="$root/apps/api/.venv" uvx library-skills --yes --all
)

agents_skills="$root/.agents/skills"
cursor_skills="$root/.cursor/skills"

if [[ -d "$agents_skills" ]]; then
  mkdir -p "$cursor_skills"

  for skill in "$agents_skills"/*; do
    [[ -e "$skill" ]] || continue

    name="$(basename "$skill")"
    dest="$cursor_skills/$name"

    if [[ -e "$dest" && ! -L "$dest" ]]; then
      continue
    fi

    rm -f "$dest"
    mv "$skill" "$dest"
  done

  rmdir "$agents_skills" 2>/dev/null || true
  rmdir "$root/.agents" 2>/dev/null || true
fi

(
  cd "$root/apps/web"
  uvx library-skills --yes --all
)
