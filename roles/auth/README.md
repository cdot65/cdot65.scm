# SCM Authentication Role

This role handles OAuth 2.0 authentication with Strata Cloud Manager (SCM) and makes 
the authentication token available to other tasks in your playbook.

## Benefits

- **Single Authentication Point** - Authenticate once per playbook, not once per module call
- **Credential Reuse** - Store and reuse the auth token across multiple tasks
- **Environment Variable Support** - Use environment variables for credentials
- **Flexible Configuration** - Override any parameter as needed
- **Secure** - No credentials are logged or exposed in playbook output

## Usage

```yaml
- name: Authenticate with SCM
  hosts: localhost
  vars_files:
    - ../vault.yml  # Store secrets here (can be encrypted with Ansible Vault)
  roles:
    - cdot65.scm.auth
  
- name: Use the authenticated session
  hosts: localhost
  tasks:
    - name: Create a folder in SCM
      cdot65.scm.folder:
        name: "My Folder"
        # No authentication parameters needed
      # The role has already set scm_access_token and other auth facts
```

## Providing Secrets
- **vault.yml**: Store `scm_client_id`, `scm_client_secret`, and `scm_tsg_id` here. Encrypt with `ansible-vault` for security.
- **.env file**: If you use a `.env` file, source it before running Ansible. Example:
  ```sh
  set -a; source .env; set +a
  poetry run ansible-playbook playbooks/auth_role_example.yml
  ```
- **Environment Variables**: You can export secrets directly in your shell.

## Security Notes
- This role never logs secrets (`no_log: true` is enforced).
- Never commit unencrypted secrets or .env files to version control.
- See WINDSURF_RULES.md for security and usage standards.

## Variables

| Variable          | Description                     | Default                                                       |
|-------------------|---------------------------------|---------------------------------------------------------------|
| scm_client_id     | OAuth client ID                 | CLIENT_ID or SCM_CLIENT_ID env var                            |
| scm_client_secret | OAuth client secret             | CLIENT_SECRET or SCM_CLIENT_SECRET env var                    |
| scm_tsg_id        | Tenant Service Group ID         | TSG_ID or SCM_TSG_ID env var                                  |
| scm_api_base_url  | Base URL for SCM API            | https://api.strata.paloaltonetworks.com                       |
| scm_token_url     | OAuth token URL                 | https://auth.apps.paloaltonetworks.com/am/oauth2/access_token |
| scm_log_level     | Logging level                   | ERROR                                                         |
| scm_save_token    | Whether to save token to a file | false                                                         |
| scm_token_path    | Path to save token file         | ~/.scm_token.json                                             |

## Facts Set by the Role

The role sets these Ansible facts that can be used by subsequent tasks:

- `scm_access_token`: The OAuth access token
- `scm_token_type`: Token type (Bearer)
- `scm_token_expires_in`: Expiration time in seconds
- `scm_token_scope`: Token scope
- `scm_auth_header`: Complete Authorization header value (e.g., "Bearer abc123...")

## Environment Variables

You can use any of these environment variables instead of setting role variables:

- `CLIENT_ID` or `SCM_CLIENT_ID`: OAuth client ID
- `CLIENT_SECRET` or `SCM_CLIENT_SECRET`: OAuth client secret
- `TSG_ID` or `SCM_TSG_ID`: Tenant Service Group ID
- `API_BASE_URL` or `SCM_API_BASE_URL`: Base URL for SCM API
- `TOKEN_URL` or `SCM_TOKEN_URL`: OAuth token URL
- `LOG_LEVEL` or `SCM_LOG_LEVEL`: Logging level

## Complete Playbook Example

```yaml
---
# File: scm_folder_management.yml

- name: Authenticate with SCM
  hosts: localhost
  gather_facts: no
  roles:
    - cdot65.scm.auth
  vars:
    # Variables can be provided here or via environment variables
    scm_client_id: "{{ lookup('env', 'CLIENT_ID') }}"
    scm_client_secret: "{{ lookup('env', 'CLIENT_SECRET') }}"
    scm_tsg_id: "{{ lookup('env', 'TSG_ID') }}"
    # Optional: debug logging
    scm_log_level: "DEBUG"

- name: Manage SCM resources
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Create a folder
      cdot65.scm.folder:
        name: "Network Objects"
        description: "Folder for network objects"
        state: present
      register: folder_result
      
    - name: Display created folder
      debug:
        var: folder_result
```

## Token Persistence (Optional)

You can save the token to a file for use in subsequent playbooks:

```yaml
- name: Authenticate with SCM
  hosts: localhost
  roles:
    - role: cdot65.scm.auth
      vars:
        scm_save_token: true
        scm_token_path: "/path/to/token.json"
```

This creates a JSON file with the token information that can be loaded in other playbooks.

## Token Expiration

SCM tokens typically expire after 15 minutes. If you have a long-running playbook, you may need to refresh the token. To handle this:

1. Call the auth role again in your playbook
2. The role will obtain a new token and update the facts

## Troubleshooting

### Common Issues

1. **Missing Credentials**:
   - Ensure `CLIENT_ID`, `CLIENT_SECRET`, and `TSG_ID` are set either as environment variables or role variables
   - Check for typos in environment variable names

2. **Connection Problems**:
   - Use `scm_log_level: "DEBUG"` to get more verbose output
   - Check that the `scm_api_base_url` and `scm_token_url` are correct

3. **Authentication Errors**:
   - Verify that your credentials are correct
   - Make sure your account has the necessary permissions
   - Check that your TSG ID is valid

### Debugging

To see detailed debug information, run your playbook with verbosity:

```bash
ansible-playbook your_playbook.yml -vvv
