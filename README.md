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

- Ansible Core 2.12 or higher
- Python 3.12 or higher
- `pan-scm-sdk` version 0.3.25 (installed automatically as a dependency)

## Authentication

The collection supports API key authentication. You can provide credentials in the following ways:

1. **Module Parameters**:
   ```yaml
   - name: Create a folder
     cdot65.scm.folder:
       api_key: "your-api-key"
       api_url: "https://api.strata.paloaltonetworks.com"
       name: "My Folder"
       state: present
   ```

2. **Environment Variables**:
   ```bash
   export SCM_API_KEY="your-api-key"
   export SCM_API_URL="https://api.strata.paloaltonetworks.com"
   ```

## Available Modules

This collection includes the following modules:

### Resource Modules

- `folder`, `folder_info`: Manage and retrieve folders
- `snippet`, `snippet_info`: Manage and retrieve snippets
- `config_scope`, `config_scope_info`: Manage and retrieve configuration scopes
- `device`, `device_info`: Manage and retrieve devices
- `address_object`, `address_object_info`: Manage and retrieve address objects
- `address_group`, `address_group_info`: Manage and retrieve address groups
- `service_object`, `service_object_info`: Manage and retrieve service objects
- `service_group`, `service_group_info`: Manage and retrieve service groups

### Action Modules

- `deployment`: Trigger configuration push/deployment
- `job_info`: Check job status

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

## Development

This collection is built using [poetry](https://python-poetry.org/) version 2.1.1.

```bash
# Install dependencies
poetry install

# Build the collection
poetry run ansible-galaxy collection build

# Install the collection locally
poetry run ansible-galaxy collection install cdot65-scm-*.tar.gz -f
```

## License

GNU General Public License v3.0 or later

## Author

- Calvin Remsburg (@cdot65)
