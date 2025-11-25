#!/bin/bash
# Exit immediately if any command fails
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
echo "Running Pytest (normal output)..."
echo "=============================="
pytest

echo "=============================="
echo "Running Pytest with -s (show print statements)..."
echo "=============================="
pytest -s
