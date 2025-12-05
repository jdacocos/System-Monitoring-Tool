#!/bin/bash
set -e

# Optional argument: target directory (default: frontend)
TARGET=${1:-frontend}

echo "=============================="
echo "Cleaning up backup files (*~)..."
echo "=============================="
if [ -d "$TARGET" ]; then
    find "$TARGET" -type f -name '*~' -delete
fi

echo "=============================="
echo "Running Autoflake to remove unused imports/variables..."
echo "=============================="
if [ -d "$TARGET" ]; then
    autoflake --in-place --remove-unused-variables \
        --remove-all-unused-imports --recursive "$TARGET"
fi

echo "=============================="
echo "Running Black for formatting..."
echo "=============================="
if [ -d "$TARGET" ]; then
    black "$TARGET"
fi

echo "=============================="
echo "Running Pylint (non-blocking)..."
echo "=============================="
if [ -d "$TARGET" ]; then
    # Prevent word-splitting and keep script alive even if pylint finds issues
    find "$TARGET" -name "*.py" -print0 | xargs -0 pylint || true
fi

echo "=============================="
echo "Frontend cleanup complete!"
echo "=============================="
