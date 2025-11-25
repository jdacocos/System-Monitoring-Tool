#!/bin/bash
# Exit if any command fails
set -e

echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
black .

echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
pylint $(find . -name "*.py") || true

echo "=============================="
echo "Running Pytest..."
echo "=============================="

# If no arguments provided, run with -s
if [ $# -eq 0 ]; then
    pytest -s
else
    pytest "$@"
fi
