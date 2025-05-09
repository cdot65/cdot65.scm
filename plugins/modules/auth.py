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
        required: true
        no_log: true
    client_secret:
        description: OAuth client secret for authentication. If not specified, the value of the SCM_CLIENT_SECRET environment variable will be used.
        type: str
        required: true
        no_log: true
    tsg_id:
        description: Tenant Service Group ID for scope construction. If not specified, the value of the SCM_TSG_ID environment variable will be used.
        type: str
        required: true
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
    scopes:
        description: List of scopes for the OAuth token. If not specified, a default scope will be used.
        type: list
        elements: str
        required: false
        default: null
    log_level:
        description: Logging level for the SDK client. If not specified, the value of the SCM_LOG_LEVEL environment variable will be used.
        type: str
        required: false
        default: "ERROR"
        choices: ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cdot65.scm.plugins.module_utils import client as scm_client_utils # noqa

def main():
    module_args = dict(
        client_id=dict(type="str", required=True, no_log=True),
        client_secret=dict(type="str", required=True, no_log=True),
        tsg_id=dict(type="str", required=True),
        api_base_url=dict(type="str", required=False, default="https://api.strata.paloaltonetworks.com"),
        token_url=dict(type="str", required=False, default="https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"),
        scopes=dict(type="list", elements="str", required=False, default=None),
        log_level=dict(type="str", required=False, default="ERROR"),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    result = dict(
        changed=False
    )

    try:
        token_info = scm_client_utils.get_oauth2_token(
            client_id=module.params["client_id"],
            client_secret=module.params["client_secret"],
            tsg_id=module.params["tsg_id"],
            token_url=module.params["token_url"],
            scopes=module.params["scopes"],
            log_level=module.params["log_level"],
        )
        result.update(token_info)
    except Exception as e:
        module.fail_json(msg=str(e), **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
