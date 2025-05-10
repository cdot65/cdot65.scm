#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: snippet
short_description: Manage snippets in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete snippets in Strata Cloud Manager using pan-scm-sdk.
    - Supports all snippet attributes and robust idempotency.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the snippet.
            - Required for state=present and for absent if id is not provided.
        type: str
        required: false
    description:
        description:
            - Description of the snippet.
        type: str
        required: false
    labels:
        description:
            - List of labels to apply to the snippet.
        type: list
        elements: str
        required: false
    enable_prefix:
        description:
            - Whether to enable prefix for this snippet.
        type: bool
        required: false
    type:
        description:
            - Snippet type: 'predefined', 'custom', 'readonly'.
        type: str
        required: false
    display_name:
        description:
            - Display name for the snippet.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the snippet.
        type: str
        required: false
    state:
        description:
            - Desired state of the snippet.
        type: str
        choices: [present, absent]
        default: present
    scm_access_token:
        description:
            - Access token for authenticating with SCM.
        type: str
        required: true
        no_log: true
'''

EXAMPLES = r'''
- name: Create a snippet
  snippet:
    name: "Security Policy Snippet"
    description: "Common security policy configurations"
    labels:
      - security
      - policy
    enable_prefix: true
    state: present
    scm_access_token: "{{ lookup('env', 'SCM_ACCESS_TOKEN') }}"

- name: Delete a snippet
  snippet:
    id: "12345678-1234-1234-1234-123456789012"
    state: absent
    scm_access_token: "{{ lookup('env', 'SCM_ACCESS_TOKEN') }}"
'''

RETURN = r'''
snippet:
    description: Details about the managed snippet.
    returned: always
    type: dict
    sample: {
        "id": "12345678-1234-1234-1234-123456789012",
        "name": "Security Policy Snippet",
        "description": "Common security policy configurations",
        "labels": ["security", "policy"],
        "enable_prefix": true,
        "type": "custom",
        "display_name": "Security Policy Snippet"
    }
changed:
    description: Whether any change was made.
    returned: always
    type: bool
failed:
    description: Whether the task failed.
    returned: always
    type: bool
msg:
    description: Informational or error message.
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import ScmClient
    from scm.exceptions import ObjectNotPresentError, InvalidObjectError, APIError
    from scm.models.setup.snippet import SnippetUpdateModel
except ImportError:
    # Will fail in Ansible runtime if requirements are missing
    pass

def main():
    module_args = dict(
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        labels=dict(type='list', elements='str', required=False),
        enable_prefix=dict(type='bool', required=False),
        type=dict(type='str', required=False),
        display_name=dict(type='str', required=False),
        id=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        scm_access_token=dict(type='str', required=True, no_log=True),
    )

    result = dict(
        changed=False,
        failed=False,
        msg='',
        snippet=None,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    params = module.params
    state = params['state']
    snippet_id = params.get('id')
    name = params.get('name')
    scm_access_token = params['scm_access_token']

    # Initialize SDK client
    try:
        client = ScmClient(access_token=scm_access_token)
        snippets = client.snippet
    except Exception as e:
        result['msg'] = f"Failed to initialize SCM client: {e}"
        module.fail_json(**result)

    try:
        if state == 'present':
            # Try to fetch existing
            existing = None
            if snippet_id:
                try:
                    existing = snippets.get(snippet_id)
                except ObjectNotPresentError:
                    existing = None
            elif name:
                existing = snippets.fetch(name)
            # Prepare data
            snippet_data = dict(
                name=name,
                description=params.get('description'),
                labels=params.get('labels'),
                enable_prefix=params.get('enable_prefix'),
            )
            # Remove unset keys and keys with value None
            snippet_data = {k: v for k, v in snippet_data.items() if v is not None}
            # Remove invalid/empty string fields
            snippet_data = {k: v for k, v in snippet_data.items() if v != ''}
            if not existing:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Would create snippet.'
                    module.exit_json(**result)
                created = snippets.create(snippet_data)
                result['changed'] = True
                result['snippet'] = json.loads(created.model_dump_json())
                result['msg'] = 'Snippet created.'
            else:
                # Compare for idempotency
                update_needed = False
                for k, v in snippet_data.items():
                    if getattr(existing, k, None) != v:
                        update_needed = True
                        break
                if update_needed:
                    if module.check_mode:
                        result['changed'] = True
                        result['msg'] = 'Would update snippet.'
                        module.exit_json(**result)
                    update_model = SnippetUpdateModel(id=existing.id, **snippet_data)
                    updated = snippets.update(update_model)
                    result['changed'] = True
                    result['snippet'] = json.loads(updated.model_dump_json())
                    result['msg'] = 'Snippet updated.'
                else:
                    result['snippet'] = json.loads(existing.model_dump_json())
                    result['msg'] = 'Snippet already present and up to date.'
        elif state == 'absent':
            # Try to fetch existing
            existing = None
            if snippet_id:
                try:
                    existing = snippets.get(snippet_id)
                except ObjectNotPresentError:
                    existing = None
            elif name:
                existing = snippets.fetch(name)
            if not existing:
                result['msg'] = 'Snippet already absent.'
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Would delete snippet.'
                    module.exit_json(**result)
                snippets.delete(existing.id)
                result['changed'] = True
                result['msg'] = 'Snippet deleted.'
    except InvalidObjectError as e:
        result['msg'] = f"Invalid snippet data: {e}"
        module.fail_json(**result)
    except ObjectNotPresentError:
        result['msg'] = 'Snippet not found.'
        module.exit_json(**result)
    except APIError as e:
        result['msg'] = f"API error: {e}"
        module.fail_json(**result)
    except Exception as e:
        result['msg'] = f"Unexpected error: {e}"
        module.fail_json(**result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
