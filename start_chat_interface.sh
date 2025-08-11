#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Start API
./scripts/start_api.sh &
API_PID=$!

# Start GUI
(
	cd llama-gui
	npm run start:react
) &
GUI_PID=$!

trap 'kill $API_PID $GUI_PID || true' INT TERM EXIT

wait

