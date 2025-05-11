# Ansible Collection for Strata Cloud Manager (SCM)

This Ansible collection (`cdot65.scm`) provides modules to automate Palo Alto Networks' Strata Cloud Manager (SCM) platform operations. It enables infrastructure-as-code practices for managing SCM resources like folders, snippets, labels, variables, and security objects.

## Installation

```bash
# Install collection from Ansible Galaxy
ansible-galaxy collection install cdot65.scm

# Install directly from GitHub
ansible-galaxy collection install git+https://github.com/cdot65/cdot65.scm.git
```

If you're using Poetry for dependency management:

```bash
# Install using Poetry
poetry run ansible-galaxy collection install cdot65.scm
```

## Requirements

- Ansible Core 2.17 or higher
- Python 3.11 or higher
- `pan-scm-sdk` version 0.3.33 (installed automatically as a dependency)

## Authentication

The collection uses OAuth2 authentication with the SCM API. **All secrets (client ID, client secret, TSG ID) must be provided via Ansible Vault-encrypted variable files.**

### Authentication Example

```yaml
- name: Authenticate with SCM
  hosts: localhost
  vars_files:
    - vault.yml  # Store secrets here (encrypted with Ansible Vault)
  roles:
    - cdot65.scm.auth
```

A typical `vault.yml` file should contain:

```yaml
scm_client_id: "your-client-id"
scm_client_secret: "your-client-secret"
scm_tsg_id: "your-tsg-id"
```

See `examples/auth.yml` for a full authentication example.

> **Security Note:** Environment variables may be used for development only, but are NOT recommended for production. Always use Ansible Vault for secrets.

## Available Modules

| Module | Type | Description | Status |
|--------|------|-------------|--------|
| `folder` | Resource | Create, update, or delete folders | ✅ Complete |
| `folder_info` | Info | Retrieve folder information with filtering | ✅ Complete |
| `label` | Resource | Create, update, or delete labels | ✅ Complete |
| `label_info` | Info | Retrieve label information with filtering | ✅ Complete |
| `snippet` | Resource | Create, update, or delete configuration snippets | ✅ Complete |
| `snippet_info` | Info | Retrieve snippet information with filtering | ✅ Complete |
| `variable` | Resource | Create, update, or delete variables | ✅ Complete |
| `variable_info` | Info | Retrieve variable information with filtering | ✅ Complete |
| `device_info` | Info | Retrieve device information with filtering by model, type, etc. | ✅ Complete |
| `config_scope` | Resource | Manage configuration scopes | 🔄 Planned |
| `config_scope_info` | Info | Retrieve configuration scope information | 🔄 Planned |
| `address_object` | Resource | Manage address objects | 🔄 Planned |
| `address_object_info` | Info | Retrieve address object information | 🔄 Planned |
| `address_group` | Resource | Manage address groups | 🔄 Planned |
| `address_group_info` | Info | Retrieve address group information | 🔄 Planned |
| `service_object` | Resource | Manage service objects | 🔄 Planned |
| `service_object_info` | Info | Retrieve service object information | 🔄 Planned |
| `service_group` | Resource | Manage service groups | 🔄 Planned |
| `service_group_info` | Info | Retrieve service group information | 🔄 Planned |
| `deployment` | Action | Trigger configuration push/deployment | 🔄 Planned |
| `job_info` | Info | Check job status | 🔄 Planned |

## Module Usage

### Resource and Info Module Pattern

The collection follows a consistent pattern:
- **Resource modules**: Perform CRUD operations (e.g., `folder`, `label`, `snippet`, `variable`)
- **Info modules**: Retrieve information about resources (e.g., `folder_info`, `label_info`, `snippet_info`, `variable_info`)

All modules support:
- Idempotent operations
- Check mode
- Detailed error handling
- Authentication via SCM access token

### Common Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `name` | Resource name | Yes (for most operations) |
| `state` | Desired state (`present` or `absent`) | No (default: `present`) |
| `scm_access_token` | Authentication token | Yes |
| `description` | Resource description | No |

## Examples

### Creating a Folder

```yaml
- name: Create a folder
  cdot65.scm.folder:
    name: "Network Objects"
    description: "Folder for network objects"
    state: present
    scm_access_token: "{{ scm_access_token }}"
```

### Creating a Variable in a Folder

```yaml
- name: Create a variable
  cdot65.scm.variable:
    name: "subnet-variable"
    folder: "Network Objects"
    value: "10.1.1.0/24"
    type: "ip-netmask"
    description: "Network subnet for department A"
    scm_access_token: "{{ scm_access_token }}"
```

### Getting Variables in a Folder

```yaml
- name: Get all variables in a folder
  cdot65.scm.variable_info:
    folder: "Network Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_variables
```

### Getting a Specific Variable

```yaml
- name: Get a specific variable
  cdot65.scm.variable_info:
    name: "subnet-variable"
    folder: "Network Objects"  # folder is required when getting a variable by name
    scm_access_token: "{{ scm_access_token }}"
  register: specific_variable
```

### Filtering Devices by Model

```yaml
- name: Get VM-series firewalls
  cdot65.scm.device_info:
    model: "PA-VM"
    scm_access_token: "{{ scm_access_token }}"
  register: vm_devices
```

## Example Playbooks

The collection includes several example playbooks in the `examples/` directory:

- `auth.yml` - Authentication example
- `folder.yml` - Create and manage folders
- `folder_info.yml` - Retrieve folder information
- `label.yml` - Create and manage labels
- `label_info.yml` - Retrieve label information
- `snippet.yml` - Create and manage snippets
- `snippet_info.yml` - Retrieve snippet information
- `variable.yml` - Create and manage variables
- `variable_info.yml` - Retrieve variable information
- `device_info.yml` - Retrieve device information

## Development

This collection is built using [poetry](https://python-poetry.org/) for dependency management.

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

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

GNU General Public License v3.0 or later

## Author

- Calvin Remsburg (@cdot65)