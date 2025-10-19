# Ansible Playbook Styling Guide

This guide outlines best practices and project conventions for writing playbooks for the `cdot65.scm` collection, based on real examples in the `examples/` directory.

---

## General Principles

- Use YAML syntax with clear indentation (spaces, never tabs)
- Use descriptive `name` fields for plays and tasks
- Group related tasks in logical play blocks
- Use variables and roles for secrets and authentication
- Prefer explicit resource state (`state: present`/`absent`) for idempotency
- Register results for later use or debugging
- Use `debug` tasks to output important variables or results
- Clean up resources at the end of the playbook for testability

---

## Playbook Structure

- **Authentication:**
  - Always start by authenticating with SCM using the `cdot65.scm.auth` role
  - Load secrets from an Ansible Vault-encrypted file (e.g., `vars_files: ../vault.yml`)
- **Session Separation:**
  - Use separate plays for authentication and resource operations
- **Task Naming:**
  - Each task should have a descriptive `name` for clarity and troubleshooting
- **Resource Operations:**
  - Use the appropriate `cdot65.scm.<resource>` module for CRUD
  - Always specify the `scm_access_token` variable
  - Use `state: present` for create/update, `state: absent` for delete
- **Result Registration:**
  - Use `register:` to capture module output for later use
- **Debugging:**
  - Use `debug:` to print key variables or results, especially after authentication or resource creation
- **Cleanup:**
  - Include cleanup tasks (deletion) at the end for repeatable tests

---

## Example Pattern

```yaml
---
- name: Authenticate with SCM using the auth role
  hosts: localhost
  gather_facts: no
  roles:
    - cdot65.scm.auth
  vars_files:
    - ../vault.yml

- name: Perform SCM address object operations using the established session
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Display authentication info
      debug:
        msg: "Authenticated with token: {{ scm_access_token | default('No token available!', true) | truncate(15, true, '...') }}"

    - name: Create a test folder
      cdot65.scm.folder:
        name: "Network-Objects"
        parent: "Texas"
        scm_access_token: "{{ scm_access_token }}"
        state: present

    - name: Create a folder-based address object
      cdot65.scm.address:
        name: "web-server"
        ip_netmask: "192.168.1.100/32"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: present
      register: address_object

    - name: Display created address object information
      debug:
        var: address_object.address

    # Cleanup
    - name: Delete the address object
      cdot65.scm.address:
        name: "web-server"
        folder: "Network-Objects"
        scm_access_token: "{{ scm_access_token }}"
        state: absent
```

---

## Best Practices

- Always use `roles` for authentication and `vars_files` for secrets
- Use `register` and `debug` to trace important outputs
- Clean up resources to keep environments tidy and tests repeatable
- Use consistent naming and structure across all playbooks
- Document any required variables or secrets at the top of the playbook
- Prefer explicit over implicit: always specify `hosts`, `gather_facts`, and key parameters

---

## References

- See the `examples/` directory for more real-world patterns
- See `CLAUDE.md` and `COLLECTION_STYLING_GUIDE.md` for overall project standards
- See `WINDSURF_RULES.md` for SDK and module rules

---

For questions or clarifications, refer to the docs or contact the maintainers.
