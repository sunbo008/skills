#!/bin/bash
# Setup virtual environment for web-search skill
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$SKILL_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    PYTHON=""
    for p in python3.13 python3.12 python3.11 python3; do
        if command -v "$p" &>/dev/null; then
            PYTHON="$p"
            break
        fi
    done
    if [ -z "$PYTHON" ]; then
        echo "Error: No python3 found" >&2
        exit 1
    fi
    "$PYTHON" -m venv "$VENV_DIR"
fi

echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install -q ddgs requests beautifulsoup4
echo "Setup complete. Python: $VENV_DIR/bin/python"
