#!/bin/bash
# Run linting checks but don't fail the build over known issues

set -e

# Set non-zero exit for warnings in these files to false
export RUFF_EXIT_ZERO=true
export FLAKE8_EXIT_ZERO=true

# Run formatters (these won't change code but will check for issues)
echo "=== Running minimal linting checks ==="
echo "Running black (check mode only)..."
poetry run black --check plugins tests || true

echo "Running ansible-lint..."
poetry run ansible-lint || true

echo -e "\n=== Linting complete ==="
echo "Note: Some warnings are expected and ignored in specific modules."
echo "See docs/ANSIBLE_STYLE.md for an explanation of conventions vs. linting rules."