# Code Linting and Formatting Guide

This guide explains how to use the linting and formatting tools configured for the `cdot65.scm` Ansible collection.

## Overview

The collection uses multiple tools to ensure code quality and consistency:

1. **black**: Code formatting with 120 character line length
2. **isort**: Import sorting configured to work with black
3. **ruff**: Comprehensive Python linter with multiple rule sets enabled
4. **flake8**: Traditional Python linter (as an alternative to ruff)
5. **ansible-lint**: Checks Ansible-specific best practices and rules
6. **mypy**: Static type checking for Python
7. **pre-commit**: Git hooks to automatically run checks before commits

## Quick Start

### Running Linting Checks

```bash
# Run all formatting and linting checks (may show warnings)
make lint-all

# Run minimal linting checks (CI-compatible)
make lint-check
```

### Auto-Fixing Issues

```bash
# Automatically fix issues with ruff, black, and isort
make lint-fix
```

### Individual Tools

```bash
# Run individual tools
make format        # Run black and isort formatters
make lint          # Run ansible-lint
make flake8        # Run flake8
make ruff-check    # Run ruff linter
```

## Pre-commit Hooks

Pre-commit hooks automatically run linting and formatting checks before each commit, ensuring code quality standards are maintained.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Set up the hooks
pre-commit install
```

### Usage

The hooks will run automatically when you commit code. You can also run them manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

## Configuration Files

The linting and formatting tools are configured in the following files:

- **pyproject.toml**: Contains configuration for black, isort, ruff, and mypy
- **.flake8**: Contains configuration for flake8
- **.pre-commit-config.yaml**: Configures pre-commit hooks

### Key Configuration Decisions

1. **Line Length**: Set to 128 characters across all tools
2. **Ignored Rules**: Certain rules are disabled where they conflict with Ansible conventions
3. **Per-File Ignores**: Test files have more relaxed rules for print statements and assert-usage
4. **Ansible Modules**: Special handling for Ansible's module argument conventions

## Integrating with CI/CD

Add the linting checks to your CI/CD pipeline by running:

```bash
# In your CI config
python -m pip install poetry
make lint-all
```

## Troubleshooting

### Common Issues

1. **Conflicting Rules**: If different tools give conflicting advice, prefer ruff and ansible-lint for their specific domains
2. **False Positives**: In rare cases where a linter flags something incorrectly, add a specific inline ignore:

   ```python
   # For ruff
   some_code()  # noqa: F401

   # For flake8
   some_code()  # noqa: E501
   ```

3. **Test Files**: Test files have different requirements - if you're getting errors in test files, check the per-file-ignores configuration

4. **CI/CD Compatibility**: For CI pipelines, use `make lint-check` instead of `make lint-all` as it's less strict and won't fail on known violations in module_utils and test files