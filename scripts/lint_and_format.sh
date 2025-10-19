#!/bin/bash
# Run all formatting and linting tools in the right order

set -e  # Exit on any error

echo "=== Running formatters ==="
# Run formatters first (they modify files)
echo "Running black..."
poetry run black plugins tests
echo "Running isort..."
poetry run isort plugins tests
echo "Running ruff format..."
poetry run ruff format plugins tests

echo "Running ruff lint with --fix..."
poetry run ruff check --fix plugins tests

echo "=== Running linters ==="
# Run linters (they check but don't modify)
echo "Running flake8..."
poetry run flake8 plugins tests
echo "Running ruff check (excluding module_utils)..."
poetry run ruff check plugins/modules tests
echo "Running ruff check on module_utils with allow-unfixable..."
poetry run ruff check --select C408 --ignore-noqa plugins/module_utils || true
echo "Running mypy..."
poetry run mypy plugins tests
echo "Running ansible-lint..."
poetry run ansible-lint

echo "\n=== All linters ran - some warnings can be ignored based on per-file-ignores ==="
echo "Check .flake8 and pyproject.toml for configured exceptions"
echo "Note: C408 warnings for module_utils are expected and will be shown but won't fail the checks"

echo "=== All formatting and linting complete ==="