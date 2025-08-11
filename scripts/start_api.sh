#!/usr/bin/env bash
set -euo pipefail

# Ensure we run from repo root
cd "$(dirname "$0")/.."

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
export ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost:3000}

if [[ -d venv ]]; then
  source venv/bin/activate
fi

exec python3 -m uvicorn src.api_server:app --host "$HOST" --port "$PORT" --reload
