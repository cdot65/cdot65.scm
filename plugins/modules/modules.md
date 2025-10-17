# Ansible Module Implementation Overview

This document provides a high-level summary of the structure and workflow patterns used in the current Ansible modules under `plugins/modules/`. It is intended to help you compare, evaluate, and decide on your preferred standard for module implementation.

---

## Module Inventory

- `auth.py`
- `device_info.py`
- `folder.py`
- `folder_info.py`
- `label.py`
- `label_info.py`
- `snippet.py`
- `snippet_info.py`
- `variable.py`
- `variable_info.py`
- `address.py`
- `address_info.py`
- `address_group.py`
- `address_group_info.py`
- `application.py`
- `application_info.py`
- `application_group.py`
- `application_group_info.py`
- `application_filter.py`
- `application_filter_info.py`
- `dynamic_user_group.py`
- `dynamic_user_group_info.py`
- `external_dynamic_list.py`
- `external_dynamic_list_info.py`
- `hip_object.py`
- `hip_object_info.py`
- `hip_profile.py`
- `hip_profile_info.py`
- `http_server_profile.py`
- `http_server_profile_info.py`
- `log_forwarding_profile.py`
- `log_forwarding_profile_info.py`

---

## Common Structure

All modules generally follow this structure:

1. **Shebang & Metadata**
   - `#!/usr/bin/python`, encoding, copyright, license
2. **Imports**
   - `from ansible.module_utils.basic import AnsibleModule`
   - SDK imports: `from scm.client import ScmClient`, exceptions, models
3. **DOCUMENTATION Block**
   - YAML docstring: module name, description, options, notes, examples, return values
4. **Main Function**
   - `def main():` defines argument spec, creates `AnsibleModule`, processes logic
5. **Argument Spec**
   - `module_args = dict(...)` with option types, required, choices, defaults
   - Use of `mutually_exclusive` and `supports_check_mode` where relevant
6. **Result Dict**
   - `result = dict(changed=False, ...)` initialized
7. **SDK/Client Usage**
   - Instantiate `ScmClient` or use helper/service classes
   - Resource CRUD or info logic
8. **Error Handling**
   - Try/except with `module.fail_json` for API/validation errors
   - Custom error messages, error_code, details
9. **Exit**
   - `module.exit_json(**result)`
10. **Module Entrypoint**
    - `if __name__ == '__main__': main()`

---

## Workflow Patterns

- **Stateful Modules** (`variable.py`, `snippet.py`, `folder.py`, `label.py`, `address.py`, `address_group.py`, `application.py`, `application_group.py`, `application_filter.py`, `dynamic_user_group.py`, `external_dynamic_list.py`, `hip_object.py`, `hip_profile.py`, `http_server_profile.py`):
  - Support `state: present/absent` for idempotent create/update/delete
  - Require resource identifiers (name/id) and container context
  - Validate mutually exclusive container args (e.g., folder/snippet/device)
  - Use `.model_dump(exclude_unset=True)` for serialization
  - Return managed resource dict and `changed` flag
  - Address module supports different address types (ip_netmask, ip_range, etc.)
  - Address Group module supports both static and dynamic group types
  - Application module supports application categorization and risk attributes
  - Application Group module supports static groups and dynamic groups that reference other groups
  - Application Filter module supports complex filtering of applications based on risk, behaviors, and characteristics
  - Application Filter module handles boolean fields carefully, only including True values in API requests
  - Dynamic User Group module supports tag-based filter expressions for user matching
  - External Dynamic List module supports URL-based and predefined external lists
  - HIP Object module supports complex criteria specifications for host posture assessment (host_info, network_info, patch_management, disk_encryption, mobile_device, certificate)
  - HIP Profile module supports match expressions using boolean logic (AND, OR, NOT) to reference HIP objects for security policy use
  - HTTP Server Profile module supports configuration of HTTP and HTTPS servers with various security options
  - Log Forwarding Profile module supports configuration of log forwarding profiles with match lists for various log types

- **Info/Query Modules** (`*_info.py`):
  - Read-only: no `state` param, always `changed: False`
  - Support filters by id, name, label, etc.
  - Return list(s) of resource dicts
  - Support `mutually_exclusive` for id/name
  - Device_info uses display_name for name searches (matching the UI name)
  - Device_info supports proper pagination with SCM API structure (data, limit, offset, total)
  - Address_info supports filtering by address type
  - Address_group_info supports filtering by group type (static or dynamic) and member contents
  - Application_info supports filtering by category, subcategory, technology, and risk level
  - Application_group_info supports filtering by group type, members, and filter patterns
  - Application_filter_info supports filtering by various criteria including risk level, category, subcategory, and technology
  - Dynamic_user_group_info supports filtering by filter expression content and tags
  - External_dynamic_list_info supports filtering by list type (predefined_ip, predefined_url, ip, domain, url, imsi, imei) and container context
  - Hip_object_info supports filtering by criteria types (host_info, network_info, patch_management, disk_encryption, mobile_device, certificate) and container context
  - Hip_profile_info supports filtering by container context and supports exact matching
  - Http_server_profile_info supports filtering by server protocol (HTTP, HTTPS), tag registration status, and container context
  - Log_forwarding_profile_info supports filtering by log type, profile name, and container context

- **Auth Module** (`auth.py`):
  - Validates credentials, returns token info
  - Uses `no_log=True` for secrets

- **Error Handling**
  - Consistent use of `module.fail_json` with detailed messages
  - Handles custom exceptions from SDK

- **Check Mode**
  - All stateful modules support check mode
  - Info modules note check mode but no effect

---

## Observed Consistencies

- All modules have:
  - Structured DOCUMENTATION/EXAMPLES/RETURN blocks
  - Type-hinted, explicit argument specs
  - Use of `AnsibleModule` pattern
  - Try/except for error handling
  - Consistent naming for params and return keys
- Info modules always return lists (e.g., `variables`, `folders`, `labels`)
- Use of `no_log=True` for secrets/tokens

## Observed Inconsistencies

- Some modules use inline import error handling (`try/except ImportError`), others do not
- Minor differences in result dict keys (e.g., `msg`, `failed`)
- Some modules include more detailed `RETURN`/`EXAMPLES` than others
- Not all modules use `mutually_exclusive` for id/name when possible

---

## Example: Minimal Module Skeleton

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError

def main():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        scm_access_token=dict(type='str', required=True, no_log=True),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    result = dict(changed=False)
    try:
        # SDK logic here
        result['changed'] = True
    except APIError as e:
        module.fail_json(msg=str(e), **result)
    module.exit_json(**result)

if __name__ == '__main__':
    main()
```

---

## Next Steps

- Implement `service_object` and `service_object_info` modules
- Implement `service_group` and `service_group_info` modules
- Add integration tests for the log_forwarding_profile modules
- Continue improving comprehensive example playbooks for all modules
- Standardize all modules to match the current best practices:
  - Direct SDK imports vs module_utils abstraction
  - Consistent error handling with specific exception types
  - Unified serialization with model_dump_json and json.loads
  - Comprehensive container parameter handling
- Create integration tests for new modules
- Continue to improve error handling for edge cases
- Polish documentation and examples

---

This document can be updated as you refine your module standards.
