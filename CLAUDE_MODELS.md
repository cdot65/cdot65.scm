# Claude Code Model Styling Guidelines

> **Canonical template:** See [../pan-scm-sdk/SDK_MODELS_TEMPLATE.py](../pan-scm-sdk/SDK_MODELS_TEMPLATE.py) for the official model skeleton.
> **Markdown style guide:** See [../pan-scm-sdk/SDK_MODELS_STYLING_GUIDE.md](../pan-scm-sdk/SDK_MODELS_STYLING_GUIDE.md) for markdown rules and patterns.

This document provides canonical, code-backed guidance for creating Pydantic models in the SDK and in Ansible modules that use the SDK. These rules are harmonized from real project models, the pan-scm-sdk `SDK_MODELS_TEMPLATE.py`, and the `SDK_MODELS_STYLING_GUIDE.md`. Follow these standards for all new and existing models in this collection.

---

## 1. File & Class Structure
- **One resource per file**, named after the resource (pluralized as needed).
- **File-level docstring**: Google-style, describing the resource and modeling purpose.
- **Import order**: Standard library, then Pydantic, then enums, then typing.
- **Enums**: Defined at the top if needed, with clear docstrings.
- **Model classes**: Always define `BaseModel`, `CreateModel`, `UpdateModel`, `ResponseModel` (and `MoveModel` if needed).
- **Class-level docstrings**: Google-style, with Args/Attributes, Returns, Raises as needed.
- **Model config**: Use `ConfigDict`/`model_config` for settings (`validate_assignment`, `populate_by_name`, `arbitrary_types_allowed`, `extra="forbid"`).

## 2. Field/Attribute Conventions
- **Field definitions**: Always use `Field(...)` with type hints, description, and constraints (`min_length`, `max_length`, `pattern`, `examples`).
- **snake_case** for all fields and models.
- **ID fields**: Always present in `UpdateModel` and `ResponseModel`, type `UUID` (or `str` if legacy).
- **Container fields**: `folder`, `snippet`, `device`—always validated for exclusivity.
- **Tag fields**: List of strings, validated for uniqueness.

## 3. Validation & Logic
- **Custom validators**: Use `@field_validator` and `@model_validator` for:
  - Ensuring exactly one of a set of mutually exclusive fields is set (e.g., address type, container, group type).
  - Ensuring lists are unique and/or always lists of strings.
  - Enum/boolean conversions.
  - Complex resource-specific logic (e.g., NAT/SECURITY move validation).
- **Error handling**: Always raise `ValueError` with clear, actionable messages in validators.

## 4. Docstrings & Documentation
- **Google-style docstrings**: For all models and validators.
- **Attributes section**: Always lists all fields with types and descriptions.
- **Validation logic**: Clearly described in docstrings.

## 5. Formatting & Style
- **Line length**: 88 chars (ruff default).
- **Blank lines**: Between class-level constants, classes, methods.
- **Imports**: Grouped and sorted.
- **No extra fields**: `extra="forbid"` in model config unless otherwise required.

---

## 6. Canonical Example Skeleton

```python
"""<Resource> models for Strata Cloud Manager SDK.

Contains Pydantic models for representing <resource> objects and related data.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class <Resource>BaseModel(BaseModel):
    """Base model for <Resource> objects containing fields common to all CRUD operations.

    Attributes:
        name (str): Name of the <resource>.
        ...
    """
    # ...fields and validators...

class <Resource>CreateModel(<Resource>BaseModel):
    """Model for creating a new <resource>. Inherits all fields and validators."""
    pass

class <Resource>UpdateModel(<Resource>BaseModel):
    """Model for updating an existing <resource>. Requires id field."""
    id: UUID = Field(..., description="UUID of the <resource>")

class <Resource>ResponseModel(<Resource>BaseModel):
    """Model for <resource> API responses. Includes id field."""
    id: UUID = Field(..., description="UUID of the <resource>")
```

---

## 7. Real-World Patterns
- See the pan-scm-sdk models (e.g., `scm/models/objects/address.py`, `scm/models/objects/address_group.py`, `scm/models/network/nat_rules.py`, `scm/models/security/security_rules.py`) for canonical field/validator logic.
- Always validate container exclusivity, tag uniqueness, and mutually exclusive resource types.
- Use `model_dump(exclude_unset=True)` for API payloads.

---

## Reviewer/Contributor Checklist
- [ ] File/class structure matches SDK_MODELS_TEMPLATE.py
- [ ] All fields use `Field(...)` with full type hints, constraints, and descriptions
- [ ] All container/tag fields validated for exclusivity/uniqueness
- [ ] All custom logic uses `@field_validator`/`@model_validator` as required
- [ ] Docstrings are Google-style and complete
- [ ] No extra fields unless explicitly allowed in config
- [ ] All standards in WINDSURF_RULES.md and SDK_MODELS_STYLING_GUIDE.md are followed
