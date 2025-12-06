#!/bin/bash
set -e

# Optional argument: specific module or test folder
TARGET=${1:-.}

TARGET_DIRS=("backend" "test_modules")

echo "=============================="
echo "Cleaning up backup files (*~)..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    [ -d "$DIR" ] && find "$DIR" -type f -name '*~' -delete
done

echo "=============================="
echo "Running Autoflake to remove unused imports/variables..."
echo "=============================="
# Run once on all directories
autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive "${TARGET_DIRS[@]}"

echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
# Run once on all directories
black "${TARGET_DIRS[@]}"

echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
# Find all Python files under target directories and run Pylint once
find "${TARGET_DIRS[@]}" -name "*.py" -print0 | xargs -0 pylint || true

echo "=============================="
echo "Running Pytest..."
echo "=============================="
# If the user passed a specific target, run only that
if [ "$TARGET" != "." ]; then
    pytest "$TARGET"
else
    pytest "${TARGET_DIRS[@]}"
fi
