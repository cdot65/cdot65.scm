#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: label
short_description: Manage labels in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete labels in Strata Cloud Manager using pan-scm-sdk.
    - Supports all label attributes and robust idempotency.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the label (max 63 chars).
            - Required for state=present and for absent if id is not provided.
        type: str
        required: false
    description:
        description:
            - Description of the label.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the label (UUID).
            - Used for lookup/deletion if provided.
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token for authenticating API calls, provided by the auth role.
        type: str
        required: true
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
            - If not specified, the value of the SCM_API_URL environment variable will be used.
        type: str
        required: false
    state:
        description:
            - Desired state of the label.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
'''

EXAMPLES = r'''
- name: Create a label
  cdot65.scm.label:
    name: "environment"
    description: "Environment classification label"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Delete a label by name
  cdot65.scm.label:
    name: "environment"
    state: absent
    scm_access_token: "{{ scm_access_token }}"
'''

RETURN = r'''
label:
    description: Information about the label that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The label ID
            type: str
            returned: always
            sample: "123e4567-e89b-12d3-a456-426655440000"
        name:
            description: The label name
            type: str
            returned: always
            sample: "environment"
        description:
            description: The label description
            type: str
            returned: always
            sample: "Environment classification label"
changed:
    description: Whether any change was made.
    returned: always
    type: bool
    sample: true
msg:
    description: Informational message.
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import ObjectNotPresentError, InvalidObjectError, APIError


def main():
    module_args = dict(
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        id=dict(type='str', required=False),
        scm_access_token=dict(type='str', required=True, no_log=True),
        api_url=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    result = dict(
        changed=False,
        label=None,
        msg=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    name = module.params.get('name')
    description = module.params.get('description')
    label_id = module.params.get('id')
    scm_access_token = module.params.get('scm_access_token')
    api_url = module.params.get('api_url')
    state = module.params.get('state')

    try:
        sdk_args = dict(
            access_token=scm_access_token
        )
        if api_url:
            sdk_args['base_url'] = api_url
        client = ScmClient(**sdk_args)
        label_service = client.label

        if state == 'present':
            # Check if label exists by name
            existing = label_service.fetch(name=name) if name else None
            if existing:
                changed = False
                update_needed = False
                if description is not None and existing.description != description:
                    existing.description = description
                    update_needed = True
                if update_needed:
                    if not module.check_mode:
                        updated = label_service.update(existing)
                        result['label'] = json.loads(updated.model_dump_json(exclude_unset=True))
                    changed = True
                    result['msg'] = f"Label '{name}' updated."
                else:
                    result['label'] = json.loads(existing.model_dump_json(exclude_unset=True))
                    result['msg'] = f"Label '{name}' already up to date."
                result['changed'] = changed
            else:
                if not name:
                    module.fail_json(msg="'name' is required to create a label.")
                label_config = dict(name=name)
                if description:
                    label_config['description'] = description
                if not module.check_mode:
                    new_label = label_service.create(label_config)
                    result['label'] = json.loads(new_label.model_dump_json(exclude_unset=True))
                result['changed'] = True
                result['msg'] = f"Label '{name}' created."
        elif state == 'absent':
            obj = None
            if label_id:
                obj = label_service.get(label_id)
            elif name:
                obj = label_service.fetch(name=name)
            if obj:
                if not module.check_mode:
                    label_service.delete(obj.id)
                result['changed'] = True
                result['msg'] = f"Label '{obj.name}' deleted."
            else:
                result['msg'] = "Label not found; nothing to do."
        module.exit_json(**result)
    except (ObjectNotPresentError, InvalidObjectError) as e:
        module.fail_json(msg=str(e), error_code=getattr(e, 'error_code', None), details=getattr(e, 'details', None))
    except APIError as e:
        module.fail_json(msg="API error: " + str(e), error_code=getattr(e, 'error_code', None), details=getattr(e, 'details', None))
    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == '__main__':
    main()
