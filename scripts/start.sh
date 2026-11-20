#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose --profile app up -d --build --wait

echo "App  http://127.0.0.1:8080"
