# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Collection Overview

The `cdot65.scm` collection provides Ansible modules to automate operations with Palo Alto Networks' Strata Cloud Manager (SCM) platform. It enables infrastructure-as-code practices for managing SCM resources like folders, snippets, labels, and security objects through Ansible playbooks.

## Development Environment

This collection is built using [poetry](https://python-poetry.org/) for dependency management and build tooling. All commands should be run through poetry to ensure consistent environments.

**SDK Source Code Location:**
- The pan-scm-sdk source code (for all core client, model, and service logic) is located at:
  ```
  ../pan-scm-sdk/scm
  ```
  Use this path to inspect, extend, or debug the SDK directly from the collection.

```bash
# Initial setup
poetry install

# Run a specific command
poetry run <command>

# Setup development environment with all dependencies
make dev-setup
```

## Common Commands

### Build and Install

```bash
# Build the collection
poetry run ansible-galaxy collection build --force
# OR use make
make build

# Install the collection locally
poetry run ansible-galaxy collection install cdot65-scm-*.tar.gz -f
# OR use make
make install

# Build and install in one step
make all

# Clean up (remove built tarballs and installed collections)
make clean
```

### Testing

```bash
# Run all tests
make test

# Run only sanity tests
make sanity
# OR
poetry run tox -e sanity

# Run only unit tests
make unit-test
# OR
poetry run tox -e py312-ansible2.14

# Run integration tests
make integration-test
# OR
poetry run tox -e integration

# Run a specific unit test (note: unit tests for module_utils need to be reimplemented)
cd ~/.ansible/collections/ansible_collections/cdot65/scm/ && \
poetry run ansible-test units --docker default tests/unit/YOUR_TEST_PATH.py
```

### Linting and Formatting

```bash
# Run all linting and formatting checks
make lint-all

# Run only ansible-lint
make lint

# Format code with black and isort
make format

# Fix linting issues with ruff, black, and isort
make lint-fix

# Run pre-commit hooks on all files
pre-commit run --all-files
```

### Running Example Playbooks

```bash
# Run an example playbook
poetry run ansible-playbook examples/folder.yml
```

## Authentication

The collection supports OAuth2 authentication with SCM. Credentials must be stored in an Ansible Vault-encrypted file (never in plain text or committed to source control).

Example `vault.yml` structure:
```yaml
scm_client_id: "your-client-id"
scm_client_secret: "your-client-secret"
scm_tsg_id: "your-tsg-id"
```

Authentication is managed via the `cdot65.scm.auth` role which sets up the token for use by other modules.

## Module Architecture

This collection follows a consistent pattern for all resource types:
- Each resource has a standard module for CRUD operations (e.g., `folder.py`) supporting `state: present` (Create/Update) and `state: absent` (Delete)
- Each resource has a corresponding information module for retrieval (e.g., `folder_info.py`)
- Shared functionality is in `plugins/module_utils/`
- The `client.py` module handles authentication and API interactions using OAuth2
- All modules must be idempotent and support check mode

When developing new modules, use the existing `folder` and `folder_info` modules as a template for structure and best practices. Always use direct SDK imports and OAuth2 authentication via access token.

## Module Design Patterns

- Each module in `plugins/modules/` must:
  - Use a comprehensive DOCUMENTATION string (YAML format) with options, notes, and examples
  - Map parameters directly to SCM resource attributes using `snake_case`
  - Clearly distinguish identifier/lookup parameters (e.g., `name`, `id`, `folder`, `snippet`)
  - Return standard Ansible results: `changed`, `failed`, `msg`, and resource dicts
  - `_info` modules must return results under a consistent key (e.g., `resources`)
  - Handle all SDK and API errors with informative, actionable error messages (use `module.fail_json`)
  - Enforce idempotency and check mode support
  - Validate mutually exclusive and required argument groups
  - Use direct SDK imports and OAuth2 authentication via access token
  - Integrate with `ScmClient` for all resource operations
  - Document all mutually exclusive and required argument groups in the docstring

## Resource Modules Status

### Completed Modules
- Folder management (`folder`, `folder_info`) - Complete ✅
- Label management (`label`, `label_info`) - Complete ✅
- Snippet management (`snippet`, `snippet_info`) - Complete ✅
- Device Info (`device_info`) - Complete ✅
- Variable management (`variable`, `variable_info`) - Complete ✅
- Address Objects (`address`, `address_info`) - Complete ✅
- Address Groups (`address_group`, `address_group_info`) - Complete ✅
- Application Objects (`application`, `application_info`) - Complete ✅
- Application Groups (`application_group`, `application_group_info`) - Complete ✅
- Application Filters (`application_filter`, `application_filter_info`) - Complete ✅
- Dynamic User Groups (`dynamic_user_group`, `dynamic_user_group_info`) - Complete ✅
- External Dynamic Lists (`external_dynamic_list`, `external_dynamic_list_info`) - Complete ✅
- Host Information Profiles (`hip_object`, `hip_object_info`) - Complete ✅
- HIP Profiles (`hip_profile`, `hip_profile_info`) - Complete ✅
- HTTP Server Profiles (`http_server_profile`, `http_server_profile_info`) - Complete ✅
- Log Forwarding Profiles (`log_forwarding_profile`, `log_forwarding_profile_info`) - Complete ✅
- Service Objects (`service`, `service_info`) - Complete ✅
- Service Groups (`service_group`, `service_group_info`) - Complete ✅
- Tags (`tag`, `tag_info`) - Complete ✅
- Regions (`region`, `region_info`) - Complete ✅
- Schedules (`schedule`, `schedule_info`) - Complete ✅
- Syslog Server Profiles (`syslog_server_profile`, `syslog_server_profile_info`) - Implemented ⚠️ (API limitations)

### Planned Modules (See DEVELOPMENT_TODO.md)
- Quarantined Devices (Priority 7)

**Note**: Syslog Server Profile modules are fully implemented and production-ready, but the SCM API endpoint returns HTTP 500 errors in some environments. The modules may work in future API versions.

## Code Style and Quality Standards

- Follow Python best practices (PEP 8) and project linting/formatting rules (see `pyproject.toml`)
- All SDK model and service files must strictly follow:
  - [WINDSURF_RULES.md](WINDSURF_RULES.md) (see SDK and module standards)
  - [COLLECTION_STYLING_GUIDE.md](COLLECTION_STYLING_GUIDE.md)
  - [SDK_MODELS_TEMPLATE.py](../pan-scm-sdk/SDK_MODELS_TEMPLATE.py)
  - [SDK_MODELS_STYLING_GUIDE.md](../pan-scm-sdk/SDK_MODELS_STYLING_GUIDE.md)
  - [CLAUDE_MODELS.md](CLAUDE_MODELS.md)
- All code generation, manual coding, and reviews must enforce these conventions for all new and existing models and modules
- Use `ruff`, `ansible-lint`, `black`, and `isort` for code quality (see `Makefile` targets)
- **Minimum Python 3.11 required** - This is enforced by pan-scm-sdk dependency and for modern Python features
- Use Python 3.11+ type hints for all SDK/service/model code; Ansible modules may omit for compatibility
- All public functions and classes must have Google-style docstrings; Ansible modules must have full YAML docstrings with synopsis, parameters, examples, and return values
- Ensure argument spec covers all options, types, required/optional, mutually exclusive, required_one_of, and no_log for secrets
- Use absolute imports within `scm/`; follow Ansible import conventions in modules
- Line length: 128 characters (see `pyproject.toml`)

## Linting Configuration

The project uses multiple linting and formatting tools (configured in `pyproject.toml`):

1. **ruff**: Comprehensive Python linter (run with `make lint` or `poetry run ruff check --fix`)
2. **black**: Code formatting (run with `make format`)
3. **isort**: Import sorting (integrated with black)
4. **ansible-lint**: Checks Ansible-specific best practices (run with `make lint`)
5. **mypy**: Static type checking for Python SDK code (run with `poetry run mypy`)

All linting/formatting is enforced via pre-commit hooks and CI. See `Makefile` for targets.

## Security Best Practices

- Never commit secrets or credentials to source control
- Always use Ansible Vault for secret storage; store API credentials in `vault.yml` (never in `.env`)
- Use `no_log: true` for all sensitive parameters in argument specs
- Authentication must use OAuth2 and be handled securely, following the pattern in `client.py`
- All modules must accept tokens via secure variables and never log secrets
- Review and follow all security recommendations in `WINDSURF_RULES.md`

## SDK Integration

- Use the latest version of the SCM Python SDK (`pan-scm-sdk`) for all API interactions
- All modules must use direct SDK imports and the unified `ScmClient` interface for resource CRUD
- Validate all container arguments (`folder`, `snippet`, `device`) and enforce exclusivity
- Use Pydantic models for payload validation and serialization; use `.model_dump(exclude_unset=True)` for API payloads
- Catch and handle SDK exceptions, mapping them to Ansible module failures
- Abstract repetitive SDK usage in `module_utils` if needed, but keep orchestration logic in modules
- See `WINDSURF_RULES.md` and `COLLECTION_STYLING_GUIDE.md` for canonical integration patterns
- Properly handle API errors and translate them to informative Ansible failure messages