#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== Running Offline Study Aid Demo ==="
python3 -m studyaid run --passage samples/optics.txt --mock
