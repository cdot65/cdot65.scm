# Strata Cloud Manager Ansible Collection

![Banner Image](https://raw.githubusercontent.com/cdot65/pan-scm-sdk/main/docs/images/logo.svg)
[![License](https://img.shields.io/badge/license-GPL--3.0-brightgreen.svg)](https://github.com/cdot65/cdot65.scm/blob/main/LICENSE)
[![Python versions](https://img.shields.io/badge/python-3.10--3.13-blue.svg)](https://www.python.org/)
[![Ansible versions](https://img.shields.io/badge/ansible-2.18%2B-black.svg)](https://www.ansible.com/)

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
- **Network Objects**: Manage address objects, address groups, application objects, and application groups.
- **Comprehensive Module Set**: 18 production-ready modules with 17+ additional modules planned (see [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md)).
- **Idempotent Operations**: All modules are designed to be idempotent, ensuring consistent and predictable results.
- **Detailed Information Modules**: Companion "info" modules for retrieving detailed information about resources.
- **OAuth2 Authentication**: Securely authenticate with the Strata Cloud Manager API using OAuth2 client credentials.
- **Role-Based Automation**: Ready-to-use roles for common operational tasks.
- **SDK Integration**: Built on the official `pan-scm-sdk` library for reliable API interactions.

## Requirements

- Python 3.10 or higher (Python 3.13 fully supported)
- Ansible Core 2.18 or higher
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

**Current Status**: 18 production-ready modules (9 resource modules + 9 info modules)

**Roadmap**: 17+ additional resource types planned ([DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md))

### Module Status Legend

| Symbol | Status |
|--------|--------|
| ✅ | Complete and available for use |
| 📝 | Planned for future release |

### Authentication Module

| Module | Description | Status |
|--------|-------------|--------|
| [auth](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/auth.py) | Authenticate and obtain OAuth2 access token | ✅ |

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

### Service Objects Modules (Planned)

| Module | Description | Status |
|--------|-------------|--------|
| [service](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service.py) | Manage service objects | 📝 |
| [service_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_info.py) | Retrieve service object information | 📝 |
| [service_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_group.py) | Manage service groups | 📝 |
| [service_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_group_info.py) | Retrieve service group information | 📝 |

### Additional Modules (Planned)

The following modules are planned for future releases. See [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md) for detailed roadmap and priorities.

#### Priority 1: Core Network Objects

| Module | Description | Status |
|--------|-------------|--------|
| [tag](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/tag.py) | Manage tags | 📝 |
| [tag_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/tag_info.py) | Retrieve tag information | 📝 |

#### Priority 2+: Advanced Features

| Module Category | Status | Details |
|-----------------|--------|---------|
| Application Filters | 📝 | See [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md) |
| User & Device Management | 📝 | Dynamic User Groups, HIP Objects, HIP Profiles |
| External Resources | 📝 | External Dynamic Lists, Regions |
| Scheduling | 📝 | Schedule objects |
| Logging & Monitoring | 📝 | HTTP Server Profiles, Syslog, Log Forwarding |
| Device Management | 📝 | Quarantined Devices |

**Total Planned Modules**: 17 additional modules (34 including info modules)

For complete details on planned features, priorities, and estimated effort, see [DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md).

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

### Authentication Methods

You can authenticate using either the `auth` module or the `auth` role:

#### Option 1: Using the auth module

```yaml
- name: Get OAuth2 token
  cdot65.scm.auth:
    client_id: "{{ scm_client_id }}"
    client_secret: "{{ scm_client_secret }}"
    tsg_id: "{{ scm_tsg_id }}"
  register: auth_result
  no_log: true

- name: Set access token fact
  set_fact:
    scm_access_token: "{{ auth_result.access_token }}"
```

#### Option 2: Using the auth role

```yaml
- name: Authenticate with SCM
  hosts: localhost
  gather_facts: no
  vars_files:
    - vault.yml  # Store secrets here (encrypted with Ansible Vault)
  roles:
    - cdot65.scm.auth
```

### Vault Configuration

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

## Development

This collection is built using [poetry](https://python-poetry.org/) for dependency management.

### Quick Start

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

### Development Resources

- **[CLAUDE.md](CLAUDE.md)** - Complete development guide and collection overview
- **[MODULE_DEVELOPMENT_WORKFLOW.md](MODULE_DEVELOPMENT_WORKFLOW.md)** - Quick reference for building new modules
- **[DEVELOPMENT_TODO.md](DEVELOPMENT_TODO.md)** - Prioritized roadmap for future modules

### Creating New Modules

To create a new module, follow the workflow documented in [MODULE_DEVELOPMENT_WORKFLOW.md](MODULE_DEVELOPMENT_WORKFLOW.md). The process involves:

1. Choose an appropriate template module based on complexity
2. Copy the template to a new module file
3. Update documentation, parameters, and SDK client calls
4. Test thoroughly with example playbooks
5. Run linting and quality checks

All modules must:
- Use the `pan-scm-sdk` library for API operations
- Support idempotent operations
- Include check mode support
- Follow consistent parameter naming conventions
- Include comprehensive documentation

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
