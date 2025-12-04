#!/bin/bash
# Exit immediately if any command fails
set -e

# Optional argument: specific module or test
TARGET=${1:-.}  # Default to current directory

# Define the directories to target
TARGET_DIRS=("backend" "test_modules")

# Clean out backup files (*~)
echo "=============================="
echo "Cleaning up backup files (*~)..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        find "$DIR" -type f -name '*~' -delete
    fi
done

# Autoflake: remove unused imports & variables
echo "=============================="
echo "Running Autoflake to remove unused imports/variables..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive "$DIR"
    fi
done

# Black formatting
echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        black "$DIR"
    fi
done

# Pylint static analysis
echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        pylint $(find "$DIR" -name "*.py") || true
    fi
done

# Pytest normal
echo "=============================="
echo "Running Pytest (normal output)..."
echo "=============================="
pytest "${TARGET_DIRS[@]}"
