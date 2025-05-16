# Strata Cloud Manager Ansible Collection

![Banner Image](https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg)
[![License](https://img.shields.io/badge/license-GPL--3.0-brightgreen.svg)](https://github.com/cdot65/cdot65.scm/blob/main/LICENSE)
[![Python versions](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Ansible versions](https://img.shields.io/badge/ansible-2.17%2B-black.svg)](https://www.ansible.com/)

Ansible Collection for managing Palo Alto Networks Strata Cloud Manager (SCM) configurations.

> **NOTE**: This collection is designed to provide infrastructure-as-code capabilities for the Strata Cloud Manager platform, enabling efficient management of folders, labels, snippets, variables, and other SCM resources.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Available Modules](#available-modules)
- [Example Usage](#example-usage)
- [Authentication](#authentication)
- [Example Playbooks](#example-playbooks)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Features

- **Configuration Management**: Create, read, update, and delete SCM configuration objects such as folders, labels, snippets, and variables.
- **Comprehensive Module Set**: Collection includes modules for organizational elements, configuration management, and future support for security objects.
- **Idempotent Operations**: All modules are designed to be idempotent, ensuring consistent and predictable results.
- **Detailed Information Modules**: Companion "info" modules for retrieving detailed information about resources.
- **OAuth2 Authentication**: Securely authenticate with the Strata Cloud Manager API using OAuth2 client credentials.
- **Role-Based Automation**: Ready-to-use roles for common operational tasks.

## Requirements

- Python 3.11 or higher
- Ansible Core 2.17 or higher
- pan-scm-sdk 0.3.33 or higher (installed automatically as a dependency)

## Installation

1. Install the collection from Ansible Galaxy:

   ```bash
   ansible-galaxy collection install cdot65.scm
   ```

2. Or install directly from GitHub:

   ```bash
   ansible-galaxy collection install git+https://github.com/cdot65/cdot65.scm.git
   ```

3. If you're using Poetry for dependency management:

   ```bash
   poetry run ansible-galaxy collection install cdot65.scm
   ```

## Available Modules

### Module Status Legend

| Symbol | Status |
|--------|--------|
| ✅ | Complete and available for use |
| 📝 | Planned for future release |

### Core Management Modules

| Module | Description | Status |
|--------|-------------|--------|
| [folder](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/folder.py) | Create, update, or delete folders | ✅ |
| [folder_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/folder_info.py) | Retrieve folder information with filtering | ✅ |
| [label](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/label.py) | Create, update, or delete labels | ✅ |
| [label_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/label_info.py) | Retrieve label information with filtering | ✅ |
| [snippet](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/snippet.py) | Create, update, or delete configuration snippets | ✅ |
| [snippet_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/snippet_info.py) | Retrieve snippet information with filtering | ✅ |
| [variable](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/variable.py) | Create, update, or delete variables | ✅ |
| [variable_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/variable_info.py) | Retrieve variable information with filtering | ✅ |
| [device_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/device_info.py) | Retrieve device information with filtering | ✅ |

### Network Objects Modules

| Module | Description | Status |
|--------|-------------|--------|
| [address](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address.py) | Manage address objects | ✅ |
| [address_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_info.py) | Retrieve address object information | ✅ |
| [address_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_group.py) | Manage address groups | ✅ |
| [address_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_group_info.py) | Retrieve address group information | ✅ |
| [application](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application.py) | Manage application objects | ✅ |
| [application_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_info.py) | Retrieve application information | ✅ |
| [application_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_group.py) | Manage application groups | ✅ |
| [application_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_group_info.py) | Retrieve application group information | ✅ |
| [application_filter](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_filter.py) | Manage application filters | ✅ |
| [application_filter_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_filter_info.py) | Retrieve application filter information | ✅ |

### User and Security Modules

| Module | Description | Status |
|--------|-------------|--------|
| [dynamic_user_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dynamic_user_group.py) | Manage dynamic user groups | ✅ |
| [dynamic_user_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dynamic_user_group_info.py) | Retrieve dynamic user group information | ✅ |
| [external_dynamic_list](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/external_dynamic_list.py) | Manage external dynamic lists | ✅ |
| [external_dynamic_list_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/external_dynamic_list_info.py) | Retrieve external dynamic list information | ✅ |
| [hip_object](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_object.py) | Manage host information profile objects | ✅ |
| [hip_object_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_object_info.py) | Retrieve host information profile object information | ✅ |
| [hip_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_profile.py) | Manage host information profiles | ✅ |
| [hip_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_profile_info.py) | Retrieve host information profile information | ✅ |
| [http_server_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/http_server_profile.py) | Manage HTTP server profiles | ✅ |
| [http_server_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/http_server_profile_info.py) | Retrieve HTTP server profile information | ✅ |
| [log_forwarding_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/log_forwarding_profile.py) | Manage log forwarding profiles | ✅ |
| [log_forwarding_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/log_forwarding_profile_info.py) | Retrieve log forwarding profile information | ✅ |

### Configuration and Deployment Modules (Planned)

| Module | Description | Status |
|--------|-------------|--------|
| [deployment](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/deployment.py) | Trigger configuration push/deployment | 📝 |
| [job_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/job_info.py) | Check job status | 📝 |

## Example Usage

### Creating a Folder Structure

```yaml
- name: Create parent folder
  cdot65.scm.folder:
    name: "Network-Objects"
    description: "Parent folder for network objects"
    parent: ""  # Root level folder
    scm_access_token: "{{ scm_access_token }}"
  register: parent_folder

- name: Create a subfolder
  cdot65.scm.folder:
    name: "Address-Objects"
    description: "Folder for address objects"
    parent: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
```

### Creating a Variable in a Folder

```yaml
- name: Create a network variable
  cdot65.scm.variable:
    name: "subnet-variable"
    folder: "Network-Objects"
    value: "10.1.1.0/24"
    type: "ip-netmask"
    description: "Network subnet for department A"
    scm_access_token: "{{ scm_access_token }}"
  register: subnet_variable
```

### Retrieving Folder Information

```yaml
- name: Get all folders
  cdot65.scm.folder_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_folders

- name: Get specific folder by name
  cdot65.scm.folder_info:
    name: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: network_folder
```

### Filtering Devices by Model

```yaml
- name: Get VM-series firewalls
  cdot65.scm.device_info:
    model: "PA-VM"
    scm_access_token: "{{ scm_access_token }}"
  register: vm_devices
```

## Authentication

The collection uses OAuth2 authentication with the SCM API. All secrets must be provided via Ansible Vault-encrypted variable files.

### Authentication Example

```yaml
- name: Authenticate with SCM
  hosts: localhost
  gather_facts: no
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

> **Security Note:** Always use Ansible Vault for storing credentials. Environment variables may be used for development only but are not recommended for production.

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
- `address.yml` - Create and manage address objects
- `address_info.yml` - Retrieve address information
- `address_group.yml` - Create and manage address groups
- `address_group_info.yml` - Retrieve address group information
- `application.yml` - Create and manage application objects
- `application_info.yml` - Retrieve application information
- `application_group.yml` - Create and manage application groups
- `application_group_info.yml` - Retrieve application group information
- `application_filter.yml` - Create and manage application filters
- `application_filter_info.yml` - Retrieve application filter information
- `dynamic_user_group.yml` - Create and manage dynamic user groups
- `dynamic_user_group_info.yml` - Retrieve dynamic user group information
- `external_dynamic_list.yml` - Create and manage external dynamic lists
- `external_dynamic_list_info.yml` - Retrieve external dynamic list information
- `hip_object.yml` - Create and manage host information profile objects 
- `hip_object_info.yml` - Retrieve host information profile object information
- `hip_profile.yml` - Create and manage host information profiles
- `hip_profile_info.yml` - Retrieve host information profile information
- `http_server_profile.yml` - Create and manage HTTP server profiles
- `http_server_profile_info.yml` - Retrieve HTTP server profile information
- `log_forwarding_profile.yml` - Create and manage log forwarding profiles
- `log_forwarding_profile_info.yml` - Retrieve log forwarding profile information
- `log_forwarding_profile_minimal.yml` - Minimal example for log forwarding profiles

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

## Module Design Patterns

The collection follows consistent design patterns:

- **Resource Modules**: Perform CRUD operations with idempotent behavior
- **Info Modules**: Retrieve detailed information with optional filtering
- **Standard Parameters**: Consistent parameter naming across all modules
- **Error Handling**: Detailed error reporting with specific error codes
- **Check Mode Support**: Preview changes without applying them

All modules support:
- Check mode
- Detailed error messages
- Consistent return structures
- Authentication via SCM access token

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

GNU General Public License v3.0 or later

## Author

- Calvin Remsburg (@cdot65)