#!/bin/bash
# Exit immediately if any command fails
set -e

# Optional argument: specific module or test
TARGET=${1:-.}  # Default to current directory

echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
black "$TARGET"

echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
# Find only Python files in the target directory or file
if [ -d "$TARGET" ]; then
    PY_FILES=$(find "$TARGET" -name "*.py")
else
    PY_FILES="$TARGET"
fi
pylint $PY_FILES || true

echo "=============================="
echo "Running Pytest (normal output)..."
echo "=============================="
pytest "$TARGET"

echo "=============================="
echo "Running Pytest with -s (show print statements)..."
echo "=============================="
pytest -s "$TARGET"
