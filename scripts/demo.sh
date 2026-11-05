#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="python3"
if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
fi

if [ -f "models/llama1b/Llama-3.2-1B-Instruct-SpinQuant_INT4_EO8.pte" ]; then
    echo "=== Running Offline Study Aid via ExecuTorch (Real Model) ==="
    "$PYTHON_BIN" -m studyaid run --passage samples/optics.txt
else
    echo "=== Running Offline Study Aid Demo (Mock Mode) ==="
    "$PYTHON_BIN" -m studyaid run --passage samples/optics.txt --mock
fi
