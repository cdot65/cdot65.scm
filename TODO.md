# TODO: cdot65.scm Ansible Collection (Strata Cloud Manager)

_Last updated: 2025-05-09_

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
- [ ] Implement device management modules (template: folder modules):
    - [ ] `plugins/modules/device.py`
    - [ ] `plugins/modules/device_info.py`
- [ ] Implement variable management modules (template: folder modules):
    - [ ] `plugins/modules/variable.py`
    - [ ] `plugins/modules/variable_info.py`
- [ ] Complete/fix unit tests for new modules
- [ ] Enhance error handling for edge cases
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
- Follow Ansible module documentation standards

## Open Issues / Watch Items

- Confirm and document minimum supported ansible-core and Python versions
- Monitor for SCM API/SDK changes and update dependencies as needed
- Assess SCM API rate limits and async job handling strategies
- Plan for future: Vault integration, inventory/lookup plugins, CI/CD automation

---

Refer to [PRD.md](./PRD.md) for full requirements, design, and future considerations.