# WINDSURF RULES

## Project Overview

This project is the `cdot65.scm` Ansible Collection, providing automation for Palo Alto Networks' Strata Cloud Manager (SCM) via the pan-scm-sdk. It is designed for robust, idempotent, and highly maintainable Ansible modules, with all resource logic and validation leveraging the SDK. All development follows strict architectural, coding, and workflow standards as outlined below.

---

## Directory & Package Structure

- **Ansible modules:** `plugins/modules/`
  - One resource per file (e.g., `address.py`, `address_group.py`)
- **SDK logic:** `scm/`
  - Service classes: `scm/config/<category>/<resource>.py`
  - Models: `scm/models/<category>/<resource>.py`
  - Auth, client, exceptions: `scm/auth.py`, `scm/client.py`, etc.
- **Examples:** `examples/` (YAML playbooks showing real-world usage)
- **Tests:** `tests/` (mirrors `plugins/modules/` and `scm/`)
- **Documentation:** `docs/`
- **Dependency management:** `pyproject.toml` (Poetry)

---

## Coding Standards

- **Linting/Formatting:** Use `ruff` (see `pyproject.toml`), run with `poetry run ruff check --fix` and `poetry run ruff format`.
- **PEP 8:** Strictly enforced.
  - `snake_case` for functions, methods, variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- **Line Length:** 128 characters (see `pyproject.toml`)
- **Imports:** Use absolute imports within `scm/`; follow Ansible module import conventions in `plugins/modules/`
- **Type Hints:** Python 3.10+ for all SDK/service/model code; Ansible modules may omit for compatibility
- **Docstrings:** Google-style for all public classes, methods, and modules; YAML docstrings for Ansible modules
- **Argument Spec:** All module options must be fully specified, with types, required, choices, mutually exclusive, etc.
- **Idempotency:** All modules must be idempotent and support check mode

---

## Ansible Module File Standards

- **File & Module Structure:**
  - One main module per file, named after the resource (snake_case)
  - **DOCUMENTATION string:** YAML, fully describing module, options, usage, and notes
  - **EXAMPLES string:** At least three real-world scenarios (create, update, delete)
  - **RETURN string:** Document all returned fields, including nested dicts and sample values
  - **Argument spec:** All arguments, types, required/optional, mutually exclusive, required_one_of
  - **Main logic:** Use `AnsibleModule`, integrate with `ScmClient`, enforce idempotency, handle check mode
  - **Error handling:** Catch SDK exceptions and fail with informative messages using `module.fail_json`
  - **Return values:** Return `changed` status and resource dict

---

## SDK Usage Patterns

- All modules interact with the pan-scm-sdk using the unified `ScmClient` interface
- Import `ScmClient` from `scm.client` and use for all resource operations
- Use the appropriate service class (e.g., `client.address`) for CRUD
- Validate container arguments (folder, snippet, device) and enforce exclusivity
- Use Pydantic models for payload validation and serialization
- Use `.model_dump(exclude_unset=True)` for all API payloads
- Catch and handle SDK exceptions, mapping them to Ansible module failures

---

## Error Handling & Validation

- All user input (limits, enums, containers) must be validated; raise custom exceptions as appropriate
- All SDK errors must be mapped to AnsibleModule failures with clear messages and details
- All API data must be validated and serialized via Pydantic models
- Use custom exceptions (`APIError`, `InvalidObjectError`, etc.) for all parameter validation and API response errors

---

## Documentation & Examples

- **Module documentation:** Each module must have a comprehensive DOCUMENTATION string, EXAMPLES, and RETURN block
- **Example playbooks:** Place runnable examples in `examples/` (e.g., `address.yml`)
- **User docs:** Maintain README, Getting Started, and Troubleshooting guides in `docs/`
- **API docs:** Generate with MkDocs and mkdocstrings for SDK Python APIs

---

## Contribution Workflow

- **Branching:** Use feature branches; PRs required for `main`
- **Reviews:** All PRs require review
- **Poetry:** Use for all dependency management
- **Semantic versioning:** Follow SemVer for releases
- **Changelog:** Maintain `CHANGELOG.md` or `release-notes.md`
- **CI/CD:** Use GitHub Actions for tests, lint, docs, release
- **Pre-commit hooks:** Enforce linting/formatting before commit

---

## References

- See `CLAUDE_MODELS.md` for model conventions
- See `COLLECTION_STYLING_GUIDE.md` for module and project style guide
- See Makefile for available developer workflows
- See `pan-scm-sdk/WINDSURF_RULES.md` for SDK-specific rules

---

For questions or clarifications, refer to the docs or contact the maintainers.
