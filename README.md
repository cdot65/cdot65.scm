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

---

### Objects Modules
| Module | Description | Status |
|--------|-------------|--------|
| [address](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address.py) | Address object management | ✅ |
| [address_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_info.py) | Retrieve address object information | ✅ |
| [address_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_group.py) | Address group management | ✅ |
| [address_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/address_group_info.py) | Retrieve address group information | ✅ |
| [application](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application.py) | Application object management | ✅ |
| [application_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_info.py) | Retrieve application object information | ✅ |
| [application_filter](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_filter.py) | Application filters management | ✅ |
| [application_filter_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_filter_info.py) | Retrieve application filters information | ✅ |
| [application_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_group.py) | Application group management | ✅ |
| [application_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/application_group_info.py) | Retrieve application group information | ✅ |
| [auto_tag_actions](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/auto_tag_actions.py) | Auto tag actions management | 📝 |
| [auto_tag_actions_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/auto_tag_actions_info.py) | Retrieve auto tag actions information | 📝 |
| [dynamic_user_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dynamic_user_group.py) | Dynamic user group management | ✅ |
| [dynamic_user_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dynamic_user_group_info.py) | Retrieve dynamic user group information | ✅ |
| [external_dynamic_list](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/external_dynamic_list.py) | External dynamic lists management | ✅ |
| [external_dynamic_list_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/external_dynamic_list_info.py) | Retrieve external dynamic lists information | ✅ |
| [hip_object](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_object.py) | HIP object management | ✅ |
| [hip_object_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_object_info.py) | Retrieve HIP object information | ✅ |
| [hip_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_profile.py) | HIP profile management | ✅ |
| [hip_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/hip_profile_info.py) | Retrieve HIP profile information | ✅ |
| [http_server_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/http_server_profile.py) | HTTP server profiles management | ✅ |
| [http_server_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/http_server_profile_info.py) | Retrieve HTTP server profiles information | ✅ |
| [log_forwarding_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/log_forwarding_profile.py) | Log forwarding profile management | ✅ |
| [log_forwarding_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/log_forwarding_profile_info.py) | Retrieve log forwarding profile information | ✅ |
| [quarantined_devices](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/quarantined_devices.py) | Quarantined devices management | ✅ |
| [quarantined_devices_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/quarantined_devices_info.py) | Retrieve quarantined devices information | ✅ |
| [region](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/region.py) | Region object management | ✅ |
| [region_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/region_info.py) | Retrieve region object information | ✅ |
| [schedules](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/schedules.py) | Schedules management | 📝 |
| [schedules_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/schedules_info.py) | Retrieve schedules information | 📝 |
| [service](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service.py) | Service object management | 📝 |
| [service_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_info.py) | Retrieve service object information | 📝 |
| [service_group](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_group.py) | Service group management | 📝 |
| [service_group_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_group_info.py) | Retrieve service group information | 📝 |
| [syslog_server_profiles](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/syslog_server_profiles.py) | Syslog server profiles management | 📝 |
| [syslog_server_profiles_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/syslog_server_profiles_info.py) | Retrieve syslog server profiles information | 📝 |
| [tag](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/tag.py) | Tag management | 📝 |
| [tag_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/tag_info.py) | Retrieve tag information | 📝 |

### Network Modules
| Module | Description | Status |
|--------|-------------|--------|
| [ike_crypto_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ike_crypto_profile.py) | IKE crypto profile management | 📝 |
| [ike_crypto_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ike_crypto_profile_info.py) | Retrieve IKE crypto profile information | 📝 |
| [ike_gateway](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ike_gateway.py) | IKE gateway management | 📝 |
| [ike_gateway_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ike_gateway_info.py) | Retrieve IKE gateway information | 📝 |
| [ipsec_crypto_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ipsec_crypto_profile.py) | IPsec crypto profile management | 📝 |
| [ipsec_crypto_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/ipsec_crypto_profile_info.py) | Retrieve IPsec crypto profile information | 📝 |
| [nat_rules](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/nat_rules.py) | NAT rules management | 📝 |
| [nat_rules_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/nat_rules_info.py) | Retrieve NAT rules information | 📝 |
| [security_zone](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/security_zone.py) | Security zone management | 📝 |
| [security_zone_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/security_zone_info.py) | Retrieve security zone information | 📝 |

### Deployment Modules
| Module | Description | Status |
|--------|-------------|--------|
| [bandwidth_allocations](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/bandwidth_allocations.py) | Bandwidth allocations management | 📝 |
| [bandwidth_allocations_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/bandwidth_allocations_info.py) | Retrieve bandwidth allocations information | 📝 |
| [bgp_routing](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/bgp_routing.py) | BGP routing management | 📝 |
| [bgp_routing_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/bgp_routing_info.py) | Retrieve BGP routing information | 📝 |
| [internal_dns_servers](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/internal_dns_servers.py) | Internal DNS servers management | 📝 |
| [internal_dns_servers_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/internal_dns_servers_info.py) | Retrieve internal DNS servers information | 📝 |
| [network_locations](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/network_locations.py) | Network locations management | 📝 |
| [network_locations_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/network_locations_info.py) | Retrieve network locations information | 📝 |
| [remote_networks](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/remote_networks.py) | Remote networks management | 📝 |
| [remote_networks_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/remote_networks_info.py) | Retrieve remote networks information | 📝 |
| [service_connections](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_connections.py) | Service connections management | 📝 |
| [service_connections_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/service_connections_info.py) | Retrieve service connections information | 📝 |

### Security Modules
| Module | Description | Status |
|--------|-------------|--------|
| [anti_spyware_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/anti_spyware_profile.py) | Anti-spyware profile management | 📝 |
| [anti_spyware_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/anti_spyware_profile_info.py) | Retrieve anti-spyware profile information | 📝 |
| [decryption_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/decryption_profile.py) | Decryption profile management | 📝 |
| [decryption_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/decryption_profile_info.py) | Retrieve decryption profile information | 📝 |
| [dns_security_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dns_security_profile.py) | DNS security profile management | 📝 |
| [dns_security_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/dns_security_profile_info.py) | Retrieve DNS security profile information | 📝 |
| [security_rule](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/security_rule.py) | Security rule management | 📝 |
| [security_rule_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/security_rule_info.py) | Retrieve security rule information | 📝 |
| [url_categories](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/url_categories.py) | URL categories management | 📝 |
| [url_categories_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/url_categories_info.py) | Retrieve URL categories information | 📝 |
| [vulnerability_protection_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/vulnerability_protection_profile.py) | Vulnerability protection profile management | 📝 |
| [vulnerability_protection_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/vulnerability_protection_profile_info.py) | Retrieve vulnerability protection profile information | 📝 |
| [wildfire_antivirus_profile](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/wildfire_antivirus_profile.py) | WildFire antivirus profile management | 📝 |
| [wildfire_antivirus_profile_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/wildfire_antivirus_profile_info.py) | Retrieve WildFire antivirus profile information | 📝 |

### Setup Modules
| Module | Description | Status |
|--------|-------------|--------|
| [device](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/device.py) | Device management | 📝 |
| [device_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/device_info.py) | Retrieve device information | ✅ |
| [folder](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/folder.py) | Folder management | ✅ |
| [folder_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/folder_info.py) | Retrieve folder information | ✅ |
| [label](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/label.py) | Label management | ✅ |
| [label_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/label_info.py) | Retrieve label information | ✅ |
| [snippet](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/snippet.py) | Snippet management | ✅ |
| [snippet_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/snippet_info.py) | Retrieve snippet information | ✅ |
| [variable](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/variable.py) | Variable management | ✅ |
| [variable_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/variable_info.py) | Retrieve variable information | ✅ |

### Mobile Agent Modules
| Module | Description | Status |
|--------|-------------|--------|
| [agent_versions](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/agent_versions.py) | Agent versions management | 📝 |
| [agent_versions_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/agent_versions_info.py) | Retrieve agent versions information | 📝 |
| [auth_settings](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/auth_settings.py) | Auth settings management | 📝 |
| [auth_settings_info](https://github.com/cdot65/cdot65.scm/blob/main/plugins/modules/auth_settings_info.py) | Retrieve auth settings information | 📝 |

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
- `quarantined_devices.yml` - Create and manage quarantined devices
- `quarantined_devices_info.yml` - Retrieve quarantined device information

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