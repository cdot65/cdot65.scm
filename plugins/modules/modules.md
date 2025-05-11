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

- **Stateful Modules** (`variable.py`, `snippet.py`, `folder.py`, `label.py`):
  - Support `state: present/absent` for idempotent create/update/delete
  - Require resource identifiers (name/id) and container context
  - Validate mutually exclusive container args (e.g., folder/snippet/device)
  - Use `.model_dump(exclude_unset=True)` for serialization
  - Return managed resource dict and `changed` flag

- **Info/Query Modules** (`*_info.py`):
  - Read-only: no `state` param, always `changed: False`
  - Support filters by id, name, label, etc.
  - Return list(s) of resource dicts
  - Support `mutually_exclusive` for id/name

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

- Decide on your preferred structure for:
  - Argument spec and mutually exclusive handling
  - Error/result dict keys
  - Documentation/return block detail
  - Import error fallback
- Once chosen, standardize all modules to match

---

This document can be updated as you refine your module standards.
