# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Collection Overview

The `cdot65.scm` collection provides Ansible modules to automate operations with Palo Alto Networks' Strata Cloud Manager (SCM) platform. It enables infrastructure-as-code practices for managing SCM resources like folders, snippets, labels, and security objects through Ansible playbooks.

## Development Environment

This collection is built using [poetry](https://python-poetry.org/) for dependency management and build tooling. All commands should be run through poetry to ensure consistent environments.

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

# Run a specific unit test
cd ~/.ansible/collections/ansible_collections/cdot65/scm/ && \
poetry run ansible-test units --docker default tests/unit/plugins/module_utils/test_scm.py
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
- The `client.py` module handles authentication and API interactions
- All modules must be idempotent and support check mode

When developing new modules, use the existing `folder` and `folder_info` modules as a template for structure and best practices.

## Module Design Patterns

- Parameters should map clearly to SCM resource attributes in `snake_case`
- Be consistent with identifier parameters (e.g., `name`, `folder`, `snippet`, `id`)
- Return standard Ansible results with `changed`, `failed`, `msg` status
- `_info` modules should return found resources under a consistent key (e.g., `resources`)
- Proper error handling for API errors with informative error messages

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

### Planned Modules (See DEVELOPMENT_TODO.md)
- Service Objects (`service`, `service_info`) - Priority 1
- Service Groups (`service_group`, `service_group_info`) - Priority 1
- Tags (`tag`, `tag_info`) - Priority 1
- Application Filters (`application_filter`, `application_filter_info`) - Priority 2
- Dynamic User Groups (`dynamic_user_group`, `dynamic_user_group_info`) - Priority 3
- And 12+ additional resources (see DEVELOPMENT_TODO.md for complete list)

## Code Style and Quality Standards

- Follow Python best practices (PEP 8)
- Use ruff, ansible-lint, black, and isort for code quality
- Use type hints for function parameters and return values
- Functions and classes should have Google-style docstrings
- All Ansible modules should have standard doc strings including synopsis, parameters, examples, and return values

## Linting Configuration

The project uses multiple linting and formatting tools:

1. **black**: Code formatting with 120 character line length
2. **isort**: Import sorting configured to work with black
3. **ruff**: Comprehensive Python linter with multiple rule sets enabled
4. **ansible-lint**: Checks Ansible-specific best practices and rules
5. **mypy**: Static type checking for Python

These are all configured in `pyproject.toml` and can be run with the appropriate make targets.

## Security Best Practices

- Never commit secrets to source control
- Always use Ansible Vault for secret storage
- Use `no_log: true` for all sensitive parameters
- Store API credentials in vault.yml (not .env files)
- Authentication must be handled securely following the pattern in `client.py`

## SDK Integration

- Use the latest version of the SCM Python SDK (pan-scm-sdk) for all API interactions
- Abstract SDK usage within `module_utils` to simplify module code
- Use Pydantic's `.model_dump_json()` method for serialization
- Properly handle API errors and translate them to informative Ansible failure messages