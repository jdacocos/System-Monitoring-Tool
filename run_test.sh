#!/bin/bash
# Exit immediately if any command fails
set -e

# Optional argument: specific module or test
TARGET=${1:-.}  # Default to current directory

# ---------------------------
# Clean out backup files (*~)
# ---------------------------
echo "=============================="
echo "Cleaning up backup files (*~)..."
echo "=============================="
if [ -d "$TARGET" ]; then
    find "$TARGET" -type f -name '*~' -delete
else
    # If TARGET is a single file, check if it ends with ~ and delete
    if [[ "$TARGET" == *~ ]]; then
        rm -f "$TARGET"
    fi
fi

# ---------------------------
# Black formatting
# ---------------------------
echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
black "$TARGET"

# ---------------------------
# Pylint static analysis
# ---------------------------
echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
if [ -d "$TARGET" ]; then
    PY_FILES=$(find "$TARGET" -name "*.py")
else
    PY_FILES="$TARGET"
fi
pylint $PY_FILES || true

# ---------------------------
# Pytest normal
# ---------------------------
echo "=============================="
echo "Running Pytest (normal output)..."
echo "=============================="
pytest "$TARGET"
