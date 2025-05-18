# Ansible Collection Styling & Contribution Guide

This guide provides standards and best practices for developing and maintaining the `cdot65.scm` Ansible Collection, which integrates with the pan-scm-sdk to manage Strata Cloud Manager resources.

---

## Quick Start

1. **Clone and set up:**
   - Use Poetry for all Python dependencies: `poetry install`
   - Use `make dev-setup` to prepare your environment
2. **Create new modules/services/models:**
   - Use existing files in `plugins/modules/` and `scm/` as templates
   - Follow naming and structure conventions below
3. **Lint and format:**
   - Run `poetry run ruff check --fix` and `poetry run ruff format`
4. **Test:**
   - Use `pytest` for all tests: `make test` or `make unit-test`
5. **Document:**
   - Add/extend docstrings, usage examples, and update docs as needed

---

## Directory & File Organization

- **Ansible Modules:** `plugins/modules/`
  - Each file implements a single resource module (e.g., `address.py`, `address_group.py`)
  - Module filenames use snake_case and match the resource name
  - Each module contains:
    - A complete DOCUMENTATION string (YAML format)
    - EXAMPLES and RETURN docstrings
    - Argument spec covering all supported options, types, and constraints
    - Idempotent logic for create, update, delete
    - Integration with pan-scm-sdk via `ScmClient`
- **Example Playbooks:** `examples/`
  - Each YAML file demonstrates real-world usage of a module (e.g., `address.yml`)
  - Examples should show authentication, resource creation, update, and cleanup
  - Use variable files and roles for secrets (e.g., `vars_files: ../vault.yml`)
- **SDK Logic:** `scm/`
  - Service classes: `scm/config/<category>/<resource>.py`
  - Models: `scm/models/<category>/<resource>.py`
  - Auth, client, exceptions: `scm/auth.py`, `scm/client.py`, etc.
- **Tests:** `tests/` (mirrors `plugins/modules/` and `scm/`)
- **Documentation:** `docs/`
- **Dependency Management:** `pyproject.toml` (Poetry)

---

## Naming & Code Style

- **PEP 8:** Strictly enforced (via ruff)
- **Line length:** 88 characters
- **Snake_case:** for functions, methods, variables
- **PascalCase:** for classes
- **UPPER_CASE:** for constants
- **Imports:** Use absolute imports within `scm/`
- **Type hints:** Python 3.10+ for all function/method parameters and return values
- **Typing:** Use standard types from `typing` (`Optional`, `List`, etc.)
- **Docstrings:** Google-style for all public classes, methods, and modules
- **Ruff:** Use `ruff` for linting and formatting (see `pyproject.toml`)

---

## Ansible Module Structure

Each module in `plugins/modules/` must follow this structure:

- **Shebang and Copyright:**
  - Start with `#!/usr/bin/python` and copyright/license info
- **Imports:**
  - Import `AnsibleModule`, relevant SDK classes, and exceptions
- **DOCUMENTATION String:**
  - YAML docstring block describing the module, options, usage, and notes
  - Example (from `address.py`):
    ```yaml
    ---
    module: address
    short_description: Manage address objects in Strata Cloud Manager (SCM)
    description:
      - Create, update, or delete address objects in Strata Cloud Manager using pan-scm-sdk.
      - Address objects must be associated with exactly one container (folder, snippet, or device).
    options:
      name:
        description:
          - Name of the address object.
        type: str
        required: false
      ip_netmask:
        description:
          - IP address with CIDR notation.
        type: str
        required: false
      ...
    notes:
      - Check mode is supported.
      - All operations are idempotent.
      - Uses pan-scm-sdk via unified client and bearer token from the auth role.
      - Address objects must be associated with exactly one container (folder, snippet, or device).
      - Exactly one address type (ip_netmask, ip_range, ip_wildcard, or fqdn) must be provided.
    ```
- **EXAMPLES String:**
  - Provide at least three usage scenarios (create, update, delete)
  - Use real parameters and show variable interpolation
  - Example:
    ```yaml
    - name: Create a folder-based IP address object
      cdot65.scm.address:
        name: "web-server"
        ip_netmask: "192.168.1.100/32"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: present
    - name: Delete an address object by name
      cdot65.scm.address:
        name: "web-server"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: absent
    ```
- **RETURN String:**
  - Document all returned fields, including nested dicts and sample values
- **Argument Spec:**
  - Define all arguments, types, required/optional, mutually exclusive, etc.
  - Example:
    ```python
    argument_spec = dict(
        name=dict(type='str', required=False),
        ip_netmask=dict(type='str', required=False),
        folder=dict(type='str', required=False),
        snippet=dict(type='str', required=False),
        device=dict(type='str', required=False),
        scm_access_token=dict(type='str', required=True, no_log=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
    )
    mutually_exclusive=[['folder', 'snippet', 'device']]
    required_one_of=[['ip_netmask', 'ip_range', 'ip_wildcard', 'fqdn']]
    ```
- **Idempotent Logic:**
  - Ensure operations are repeatable and safe
  - Use SDK client for all API calls
  - Handle check mode and dry-run scenarios
- **Error Handling:**
  - Catch SDK exceptions and fail with informative messages
  - Example:
    ```python
    try:
        ...
    except (APIError, InvalidObjectError) as exc:
        module.fail_json(msg=str(exc), details=exc.details)
    ```
- **Return Values:**
  - Return changed status and resource dict
  - Example:
    ```python
    result = dict(changed=changed, address=address_data)
    module.exit_json(**result)
    ```

---

## SDK Integration Patterns

- All modules interact with the pan-scm-sdk using the unified `ScmClient` interface
- Import `ScmClient` from `scm.client` and use it for all resource operations
- Use the appropriate service class (e.g., `client.address`) for resource CRUD
- Always validate container arguments (folder, snippet, device) and enforce exclusivity
- Use Pydantic models for payload validation and serialization
- Example integration (from `address.py`):
  ```python
  client = ScmClient(api_url=api_url, token=scm_access_token)
  # Create or update address object
  address = client.address.create(AddressCreateModel(**params))
  ```
- Catch and handle SDK exceptions, mapping them to Ansible module failures
- Use `.model_dump(exclude_unset=True)` for API payloads
- Place all SDK-related logic in `scm/` and keep modules focused on orchestration

---

## Testing & CI

- **Framework:** Use `pytest`
- **Coverage:** >80% required (tracked via `coverage.py`)
- **Unit tests:**
  - Validate models, auth, client, service logic, error handling
- **Integration tests:**
  - Mock or use test tenant for real API interactions
- **Fixtures:** Use `pytest` fixtures for setup
- **Makefile targets:**
  - `make test`, `make lint`, `make format`, `make build`, etc.
- **Pre-commit hooks:**
  - Enforce linting/formatting before commit

---

## Documentation & Examples

- **Module Documentation:**
  - Each module must have a comprehensive DOCUMENTATION string, EXAMPLES, and RETURN block
  - Document all arguments, mutually exclusive and required groups, and return values
  - Use Google-style docstrings in all SDK Python files
- **Example Playbooks:**
  - Place runnable examples in `examples/` (e.g., `address.yml`)
  - Show authentication, resource creation, update, and cleanup
  - Demonstrate use of variables, roles, and idempotency
  - Example (from `examples/address.yml`):
    ```yaml
    - name: Create a folder-based IP address object
      cdot65.scm.address:
        name: "web-server"
        ip_netmask: "192.168.1.100/32"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: present

    - name: Update the web-server address object
      cdot65.scm.address:
        name: "web-server"
        description: "Updated web server description"
        ip_netmask: "192.168.1.100/32"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: present

    - name: Delete the address object
      cdot65.scm.address:
        name: "web-server"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: absent
    ```
- **User Documentation:**
  - Maintain README, Getting Started, and Troubleshooting guides in `docs/`
  - Add resource-specific documentation as needed
- **API Documentation:**
  - Generate with MkDocs and mkdocstrings for SDK Python APIs

---

## Contribution Workflow

- **Branching:** Use feature branches; PRs required for `main`
- **Reviews:** All PRs require review
- **Poetry:** Use for all dependency management
- **Semantic versioning:** Follow SemVer for releases
- **Changelog:** Maintain `CHANGELOG.md` or `release-notes.md`
- **CI/CD:** Use GitHub Actions for tests, lint, docs, release

---

## References

- See `SDK_STYLING_GUIDE.md` in pan-scm-sdk for SDK-specific patterns
- See `CLAUDE_MODELS.md` for model conventions
- See Makefile for available developer workflows

---

For questions or clarifications, refer to the docs or contact the maintainers.
