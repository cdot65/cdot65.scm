# TODO: cdot65.scm Ansible Collection (Strata Cloud Manager)

_Last updated: 2025-04-16_

## Immediate Tasks

- [x] Implement authentication role (`roles/auth`)
    - [x] Example playbook at `playbooks/auth.yml`
- [ ] Implement folder management module:
    - [ ] `plugins/modules/folder.py` (CRUD operations for SCM folders)
- [ ] Complete/fix unit tests for module_utils components (client, authentication, error handling)
- [ ] Implement folder_info module
- [ ] Implement address object modules:
    - [ ] `address_object`
    - [ ] `address_object_info`
- [ ] Implement service object modules:
    - [ ] `service_object`
    - [ ] `service_object_info`
- [ ] Enhance error handling for edge cases
- [ ] Create integration tests for first modules

## Short-term Goals (MVP)

- [ ] Complete all MVP modules listed in PRD scope
- [ ] Develop comprehensive test coverage (unit + integration)
- [ ] Create example playbooks for common SCM workflows
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