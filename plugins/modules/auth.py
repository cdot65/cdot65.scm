#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <cremsburg.dev@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: auth
short_description: Authenticate with Strata Cloud Manager (SCM)
description:
    - This module allows authenticating with the Palo Alto Networks Strata Cloud Manager API.
    - It validates credentials and establishes a connection to the SCM API.
    - This module is typically used to verify credentials before proceeding with other SCM operations.
author:
    - Calvin Remsburg (@cdot65)
options:
    client_id:
        description: OAuth client ID for authentication. If not specified, the value of the SCM_CLIENT_ID environment variable will be used.
        type: str
        required: false
    client_secret:
        description: OAuth client secret for authentication. If not specified, the value of the SCM_CLIENT_SECRET environment variable will be used.
        type: str
        required: false
        no_log: true
    tsg_id:
        description: Tenant Service Group ID for scope construction. If not specified, the value of the SCM_TSG_ID environment variable will be used.
        type: str
        required: false
    api_key:
        description: API key for authentication. If not specified, the value of the SCM_API_KEY environment variable will be used. Note that API key authentication is not currently supported by the SDK and is provided for future compatibility.
        type: str
        required: false
        no_log: true
    api_base_url:
        description: Base URL for the SCM API. If not specified, the value of the SCM_API_BASE_URL environment variable will be used.
        type: str
        required: false
        default: "https://api.strata.paloaltonetworks.com"
    token_url:
        description: URL for obtaining OAuth tokens. If not specified, the value of the SCM_TOKEN_URL environment variable will be used.
        type: str
        required: false
        default: "https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"
    log_level:
        description: Logging level for the SDK client. If not specified, the value of the SCM_LOG_LEVEL environment variable will be used.
        type: str
        required: false
        default: "ERROR"
        choices: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    return_token:
        description: Whether to return the access token in the result. Setting this to true can be useful for debugging but may expose sensitive information.
        type: bool
        required: false
        default: false
requirements:
    - scm
'''

EXAMPLES = r'''
- name: Verify SCM authentication with OAuth2
  cdot65.scm.auth:
    client_id: "client_id_example"
    client_secret: "client_secret_example"
    tsg_id: "tsg_id_example"
  register: auth_result

- name: Verify SCM authentication using environment variables
  cdot65.scm.auth:
  register: auth_result
  # Uses SCM_CLIENT_ID, SCM_CLIENT_SECRET, and SCM_TSG_ID from environment variables

- name: Verify SCM authentication with custom API URL
  cdot65.scm.auth:
    client_id: "client_id_example"
    client_secret: "client_secret_example"
    tsg_id: "tsg_id_example"
    api_base_url: "https://custom-api.strata.paloaltonetworks.com"
  register: auth_result
'''

RETURN = r'''
authorized:
    description: Whether authentication was successful
    returned: always
    type: bool
    sample: true
token_info:
    description: Information about the token (only if return_token is true)
    returned: when return_token is true
    type: dict
    contains:
        access_token:
            description: The OAuth access token
            returned: always
            type: str
            sample: "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ..."
        token_type:
            description: The token type
            returned: always
            type: str
            sample: "Bearer"
        expires_at:
            description: The token expiration timestamp
            returned: always
            type: float
            sample: 1617123456.789
        scope:
            description: The token scope
            returned: always
            type: list
            sample: ["tsg_id:123456"]
message:
    description: Additional information about the authentication process
    returned: always
    type: str
    sample: "Successfully authenticated with SCM API"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cdot65.scm.plugins.module_utils.client import (
    get_scm_client_argument_spec,
    get_scm_client,
    handle_scm_error,
)


def main():
    """Run the module."""
    # Define the module argument specification
    module_args = get_scm_client_argument_spec()
    module_args.update(
        return_token=dict(type='bool', required=False, default=False),
    )

    # Create the module object
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Define result dictionary
    result = dict(
        changed=False,
        authorized=False,
        message='',
    )

    # If in check mode, return without making changes
    if module.check_mode:
        result['message'] = 'Check mode is enabled, no authentication test performed'
        module.exit_json(**result)

    try:
        # Initialize SCM client - this will validate credentials
        client = get_scm_client(module)
        
        # If we get here, authentication was successful
        result['authorized'] = True
        result['message'] = 'Successfully authenticated with SCM API'
        
        # Add token info if requested
        if module.params.get('return_token', False) and hasattr(client, 'oauth_client') and hasattr(client.oauth_client, 'session'):
            token = client.oauth_client.session.token
            if token:
                result['token_info'] = {
                    'access_token': token.get('access_token'),
                    'token_type': token.get('token_type'),
                    'expires_at': token.get('expires_at'),
                    'scope': token.get('scope', []),
                }
        
        # Return successful result
        module.exit_json(**result)
    
    except Exception as e:
        # Handle authentication error
        result['authorized'] = False
        result['message'] = f'Authentication failed: {str(e)}'
        module.fail_json(msg=result['message'])


if __name__ == '__main__':
    main()
