#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: snippet_info
short_description: Get information about snippets in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about snippets in Strata Cloud Manager.
    - It can be used to get details about a specific snippet by ID or name, or to list all snippets.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the snippet to retrieve.
            - If specified, the module will return information about this specific snippet.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the snippet to retrieve.
            - If specified, the module will search for snippets with this name.
            - Mutually exclusive with I(id).
        type: str
        required: false
    labels:
        description:
            - List of labels to filter snippets by.
        type: list
        elements: str
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - For authentication, you can set the C(SCM_ACCESS_TOKEN) environment variable
      instead of providing it as a module option.
'''

EXAMPLES = r'''
- name: Get all snippets
  snippet_info:
    scm_access_token: "{{ scm_access_token }}"

- name: Get a snippet by name
  snippet_info:
    name: "Security Policy Snippet"
    scm_access_token: "{{ scm_access_token }}"

- name: Get a snippet by ID
  snippet_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
'''

RETURN = r'''
snippets:
    description: List of snippets returned by the query.
    returned: always
    type: list
    elements: dict
    sample:
      - id: "12345678-1234-1234-1234-123456789012"
        name: "Security Policy Snippet"
        description: "Common security policy configurations"
        labels: ["security", "policy"]
        enable_prefix: true
        type: "custom"
        display_name: "Security Policy Snippet"
        last_update: "2025-04-10T12:34:56Z"
        created_in: "2025-04-01T09:00:00Z"
        folders: []
        shared_in: "local"
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import ScmClient
    from scm.exceptions import ObjectNotPresentError, APIError
except ImportError:
    pass

def main():
    module_args = dict(
        id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        labels=dict(type='list', elements='str', required=False),
        scm_access_token=dict(type='str', required=True, no_log=True),
        api_url=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        failed=False,
        msg='',
        snippets=[],
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    params = module.params
    snippet_id = params.get('id')
    name = params.get('name')
    labels = params.get('labels')
    scm_access_token = params['scm_access_token']

    # Validate mutually exclusive arguments
    if snippet_id and name:
        result['msg'] = 'id and name are mutually exclusive.'
        module.fail_json(**result)

    try:
        client = ScmClient(access_token=scm_access_token)
        snippets_service = client.snippet
    except Exception as e:
        result['msg'] = f"Failed to initialize SCM client: {e}"
        module.fail_json(**result)

    try:
        if snippet_id:
            snippet = snippets_service.get(snippet_id)
            result['snippets'] = [json.loads(snippet.model_dump_json())]
        elif name:
            snippet = snippets_service.fetch(name)
            if snippet:
                result['snippets'] = [json.loads(snippet.model_dump_json())]
            else:
                result['snippets'] = []
        else:
            filters = {}
            if labels:
                filters['labels'] = labels
            all_snippets = snippets_service.list(**filters)
            result['snippets'] = [json.loads(s.model_dump_json()) for s in all_snippets]
        result['msg'] = 'Query successful.'
    except ObjectNotPresentError:
        result['msg'] = 'Snippet not found.'
        result['snippets'] = []
    except APIError as e:
        result['msg'] = f"API error: {e}"
        module.fail_json(**result)
    except Exception as e:
        result['msg'] = f"Unexpected error: {e}"
        module.fail_json(**result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
