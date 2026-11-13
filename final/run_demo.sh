#!/usr/bin/env bash
set -e

# Find script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ]; then
    ROOT_DIR="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../pyproject.toml" ]; then
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    ROOT_DIR="$SCRIPT_DIR"
fi

cd "$ROOT_DIR"

# Activate virtual environment if present
if [ -f "$ROOT_DIR/.venv/bin/activate" ]; then
    source "$ROOT_DIR/.venv/bin/activate"
fi

# Ensure 4 execution threads for stable CPU inference
export OMP_NUM_THREADS=4
export TORCH_NUM_THREADS=4

# Handle arguments
if [ "$#" -eq 0 ]; then
    # Interactive passage entry by default
    python3 -m studyaid run --interactive
elif [ -f "$1" ]; then
    # Passage file path passed as first positional argument
    PASSAGE="$1"
    shift
    python3 -m studyaid run --passage "$PASSAGE" "$@"
else
    # Forward flags directly (e.g., --passage, --interactive, --mock)
    python3 -m studyaid run "$@"
fi
