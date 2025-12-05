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
for DIR in "${TARGET_DIRS[@]}"; do
    [ -d "$DIR" ] && autoflake --in-place --remove-unused-variables \
        --remove-all-unused-imports --recursive "$DIR"
done

echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    [ -d "$DIR" ] && black "$DIR"
done

echo "=============================="
echo "Running Pylint for static analysis..."
echo "=============================="
for DIR in "${TARGET_DIRS[@]}"; do
    if [ -d "$DIR" ]; then
        # Use xargs to handle large file lists and avoid word splitting issues
        find "$DIR" -name "*.py" -print0 | xargs -0 pylint || true
    fi
done

echo "=============================="
echo "Running Pytest..."
echo "=============================="

# If the user passed a specific target, run only that
if [ "$TARGET" != "." ]; then
    pytest "$TARGET"
else
    pytest "${TARGET_DIRS[@]}"
fi
