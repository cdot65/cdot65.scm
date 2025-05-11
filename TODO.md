# TODO: cdot65.scm Ansible Collection (Strata Cloud Manager)

_Last updated: 2025-05-15_

## Immediate Tasks

- [x] Implement authentication role (`roles/auth`)
    - [x] Example playbook at `playbooks/auth.yml`
- [x] Implement folder management module:
    - [x] `plugins/modules/folder.py` (CRUD operations for SCM folders)
    - [x] `plugins/modules/folder_info.py` (query/info for SCM folders)
- [x] Example playbooks for folder and folder_info modules
- [x] Resolve serialization issues (UUIDs, Pydantic)
- [x] Implement label management modules (template: folder modules):
    - [x] `plugins/modules/label.py`
    - [x] `plugins/modules/label_info.py`
- [x] Implement snippet management modules (template: folder modules):
    - [x] `plugins/modules/snippet.py`
    - [x] `plugins/modules/snippet_info.py`
- [x] Implement device management modules:
    - [x] `plugins/modules/device_info.py` (read-only operations for SCM devices)
- [x] Implement variable management modules (template: folder modules):
    - [x] `plugins/modules/variable.py`
    - [x] `plugins/modules/variable_info.py`
- [x] Update README documentation with module matrix and examples
- [ ] Implement address object management modules:
    - [ ] `plugins/modules/address.py`
    - [ ] `plugins/modules/address_info.py`
- [ ] Implement address group management modules:
    - [ ] `plugins/modules/address_group.py`
    - [ ] `plugins/modules/address_group_info.py`
- [ ] Implement application management modules:
    - [ ] `plugins/modules/application.py`
    - [ ] `plugins/modules/application_info.py`
- [ ] Enhance error handling for all modules with consistent patterns
- [ ] Create integration tests for all resource modules

## Short-term Goals (MVP)

- [ ] Complete all MVP modules listed in PRD scope (using folder/folder_info as template)
- [ ] Develop comprehensive test coverage (unit + integration)
- [ ] Create example playbooks for all resource types
- [ ] Enhance documentation with real-world usage patterns
- [ ] Ensure all modules support idempotency and check_mode

## Process & Quality Reminders

- Use `poetry run` for all build, test, and lint commands (see Makefile)
- Maintain dependency management with Poetry (pyproject.toml)
- Use ruff, ansible-lint, yamllint, and isort for code quality
- All sensitive parameters must use `no_log: true`
- All info modules should follow consistent error handling pattern
- Use Pydantic's model_dump_json(exclude_unset=True) for serialization
- Follow standardized parameter naming and usage across all modules
- Update examples directory with each new module implementation

## Open Issues / Watch Items

- Confirm and document minimum supported ansible-core and Python versions
- Monitor for SCM API/SDK changes and update dependencies as needed
- Assess SCM API rate limits and async job handling strategies
- Plan for future: Vault integration, inventory/lookup plugins, CI/CD automation

## [2025-05-15] Info Modules - Standardized Error Handling and Client Usage

- All info modules now follow a consistent pattern for client initialization, error handling, and result formatting
- Standardized approach for getting resources by ID versus list filtering
- Unified exception handling with specific patterns for different error types
- Consistent serialization using `model_dump_json(exclude_unset=True)` + `json.loads()` for all SCM objects
- Added folder parameter requirement validation for variable modules when getting by name
- All example playbooks updated to demonstrate proper usage patterns
- Comprehensive README documentation with module matrix and usage examples

## [2025-05-10] plugins/modules/folder.py - Workflow & Serialization Improvements

- Refactored the module to keep Pydantic model objects (`folder_obj`) native throughout workflow, only serializing for Ansible output.
- Switched all result serialization to use `model_dump_json(exclude_unset=True)` + `json.loads()` for folder objects.
    - This ensures UUIDs and other non-JSON-serializable types are always safely converted to strings for Ansible.
    - Prevents fatal errors from UUID serialization when returning results.
- Removed previous manual UUID conversion logic and unnecessary uses of `serialize_as_any`.
- Improved code maintainability and robustness by leveraging Pydantic's JSON encoder for all output.
- This pattern should be adopted for other modules returning Pydantic models to Ansible.

---

Refer to [PRD.md](./PRD.md) for full requirements, design, and future considerations.