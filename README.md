# Ansible Collection for Strata Cloud Manager (SCM)

This Ansible collection (`cdot65.scm`) provides modules to automate Palo Alto Networks' Strata Cloud Manager (SCM) platform operations. It enables infrastructure-as-code practices for managing SCM resources like folders, snippets, and security objects.

## Installation

```bash
# Install collection from Ansible Galaxy
poetry run ansible-galaxy collection install cdot65.scm

# Install directly from GitHub
poetry run ansible-galaxy collection install git+https://github.com/cdot65/cdot65.scm.git
```

## Requirements

- Ansible Core 2.17 or higher
- Python 3.11 or higher
- `pan-scm-sdk` version 0.3.32 (installed automatically as a dependency)

## Authentication

The collection supports OAuth2 authentication. **All secrets (client ID, secret, TSG ID, etc.) must be provided via Ansible Vault-encrypted variable files. Do NOT use .env files or commit secrets to source control.**

Example:

```yaml
- name: Authenticate with SCM
  hosts: localhost
  vars_files:
    - ../vault.yml  # Store secrets here (encrypted with Ansible Vault)
  roles:
    - cdot65.scm.auth
```

See `examples/auth.yml` for a full example.

> **Note:** Environment variables may be used for development only, but are NOT recommended or supported for production or in documentation. All examples and defaults require Ansible Vault.

## Best Practices for Secrets
- Use `vault.yml` for secrets and encrypt it with Ansible Vault.
- Never commit unencrypted secrets to version control.
- Use `no_log: true` for tasks handling credentials.

## Available Modules

This collection includes the following modules:

### Resource Modules

- `folder`, `folder_info`: Manage and retrieve folders
- `label`, `label_info`: Manage and retrieve labels
- `snippet`, `snippet_info`: Manage and retrieve snippets
- `device_info`: Retrieve device information
- `variable`, `variable_info`: Manage and retrieve variables
- `config_scope`, `config_scope_info`: Manage and retrieve configuration scopes (planned)
- `address_object`, `address_object_info`: Manage and retrieve address objects (planned)
- `address_group`, `address_group_info`: Manage and retrieve address groups (planned)
- `service_object`, `service_object_info`: Manage and retrieve service objects (planned)
- `service_group`, `service_group_info`: Manage and retrieve service groups (planned)

### Action Modules

- `deployment`: Trigger configuration push/deployment (planned)
- `job_info`: Check job status (planned)

## Examples

### Creating a new folder

```yaml
- name: Create a folder
  cdot65.scm.folder:
    name: "Network Objects"
    description: "Folder for network objects"
    state: present
```

### Retrieving all folders

```yaml
- name: Get all folders
  cdot65.scm.folder_info:
  register: folders_result

- name: Display folders
  debug:
    var: folders_result.resources
```

### Retrieving device information

```yaml
- name: Get all devices
  cdot65.scm.device_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_devices

- name: Get VM-series firewalls
  cdot65.scm.device_info:
    model: "PA-VM"
    scm_access_token: "{{ scm_access_token }}"
  register: vm_devices
```

## Development

This collection is built using [poetry](https://python-poetry.org/) version 2.1.1.

```bash
# Setup development environment
make dev-setup

# Build the collection
make build

# Install the collection locally
make install

# Build and install in one step
make all

# Run all linting and formatting checks
make lint-all

# Format code
make format

# Fix linting issues automatically
make lint-fix

# Run all tests
make test
```

## License

GNU General Public License v3.0 or later

## Author

- Calvin Remsburg (@cdot65)