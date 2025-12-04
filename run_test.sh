#!/bin/bash
# Exit immediately if any command fails
set -e

# Optional argument: specific module or test
TARGET=${1:-.}  # Default to current directory

AUTOFLAKE="$HOME/.local/bin/autoflake"
BLACK="$HOME/.local/bin/black"
PYLINT="$HOME/.local/bin/pylint"
PYTEST="$HOME/.local/bin/pytest"

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
# Autoflake: remove unused imports & variables
# ---------------------------
echo "=============================="
echo "Running Autoflake to remove unused imports/variables..."
echo "=============================="
if [ -x "$AUTOFLAKE" ]; then
    if [ -d "$TARGET" ]; then
        $AUTOFLAKE --in-place --remove-unused-variables --remove-all-unused-imports --recursive "$TARGET"
    else
        $AUTOFLAKE --in-place --remove-unused-variables --remove-all-unused-imports "$TARGET"
    fi
else
    echo "Autoflake not found — skipping"
fi
# ---------------------------
# Black formatting
# ---------------------------
echo "=============================="
echo "Running Black for code formatting..."
echo "=============================="
if [ -x "$BLACK" ]; then
    $BLACK "$TARGET"
else
    echo "Black not found — skipping formatting"
fi

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
if [ -x "$PYLINT" ]; then
    $PYLINT $PY_FILES || true
else
    echo "Pylint not found — skipping linting"
fi

# ---------------------------
# Pytest normal
# ---------------------------
echo "=============================="
echo "Running Pytest (normal output)..."
echo "=============================="
if [ -x "$PYTEST" ]; then
    $PYTEST "$TARGET"
else
    echo "Pytest not found — skipping tests"
fi
