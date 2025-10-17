# Ansible Style Conventions vs. Python Style Guides

## Overview

This document explains why certain Python linting rules are deliberately ignored in Ansible modules and module utilities, and how our configuration is set up to handle this.

## Ansible-Specific Conventions

Ansible modules follow certain conventions that may conflict with some Python style guides. The most notable are:

### 1. Using `dict()` for Argument Specs

```python
# Ansible convention:
return dict(
    name=dict(type="str", required=True),
    state=dict(type="str", choices=["present", "absent"], default="present"),
)

# Python style guides might prefer:
return {
    "name": {"type": "str", "required": True},
    "state": {"type": "str", "choices": ["present", "absent"], "default": "present"},
}
```

**Why we follow Ansible's convention**: This pattern is used consistently throughout Ansible's core modules and most collections. It enhances readability for Ansible module developers who are familiar with this pattern.

### 2. Documentation Format

Ansible modules use YAML-formatted doc strings that are parsed by Ansible's documentation tools:

```python
DOCUMENTATION = r"""
---
module: my_module
short_description: Does something cool
description:
    - This module does something really cool.
options:
    name:
        description:
            - The name of the thing.
        required: true
        type: str
"""
```

### 3. Result Format

Ansible modules return results in a specific format:

```python
module.exit_json(
    changed=True,
    resource=resource_data,
    msg="Resource created successfully"
)
```

## How Our Linting Configuration Handles This

To accommodate these Ansible-specific patterns while maintaining high code quality, our linting configuration:

1. **Ignores C408 for Ansible Code**: We've configured both ruff and flake8 to ignore the "Unnecessary `dict()` call" warning (C408) in:
   - plugins/modules/*.py
   - plugins/module_utils/*.py

2. **Uses Different Rules for Different Directories**:
   - Stricter rules for tests and other Python code
   - More lenient rules for Ansible module code

3. **Pre-commit Configuration**:
   - Excludes module_utils from some checks
   - Reduces noise from linting output

## Specific Configurations

### pyproject.toml (ruff)

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "S603", "S607", "T201", "ANN", "C408"]
"plugins/modules/*.py" = ["C408"]  # Ansible module convention uses dict() calls
"plugins/module_utils/*.py" = ["C408"]  # Same for module_utils
```

### .flake8

```ini
per-file-ignores =
    # Allow Ansible modules to use dict() for argument specs (Ansible convention)
    plugins/modules/*.py: E501,F821,C408
    plugins/module_utils/*.py: E501,F821,C408
```

### .pre-commit-config.yaml

```yaml
- id: ruff
  args: [check, --fix, --exit-non-zero-on-fix]
  exclude: ^plugins/module_utils/.*\.py$
```

## Conclusion

While we strive for Python best practices throughout our codebase, we deliberately make exceptions for Ansible-specific code to follow established conventions. This approach ensures our modules integrate well with the Ansible ecosystem while maintaining high overall code quality.