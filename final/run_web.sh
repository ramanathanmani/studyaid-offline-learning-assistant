#!/bin/bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv/bin/python"

HOST="${1:-127.0.0.1}"
PORT="${2:-8080}"

echo "=========================================================="
echo " Starting StudyAid Offline Web App (Class 9 Tamil Nadu) "
echo "=========================================================="
echo "Host:    $HOST"
echo "Port:    $PORT"
echo "Python:  $($VENV --version)"
echo "App URL: http://$HOST:$PORT/"
echo "=========================================================="

exec $VENV "$ROOT/final/server.py" "$HOST" "$PORT"
