#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 &> /dev/null; then
    python3 "$SCRIPT_DIR/notify.py" "$@"
elif command -v python &> /dev/null; then
    python "$SCRIPT_DIR/notify.py" "$@"
else
    echo "Error: Neither python nor python3 found"
    exit 1
fi
