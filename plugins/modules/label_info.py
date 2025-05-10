#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import json

__metaclass__ = type

DOCUMENTATION = r'''
---
module: label_info
short_description: Get information about labels in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about labels in Strata Cloud Manager.
    - It can be used to get details about a specific label by ID or name, or to list all labels.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the label to retrieve.
            - If specified, the module will return information about this specific label.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the label to retrieve.
            - If specified, the module will search for labels with this name.
            - Mutually exclusive with I(id).
        type: str
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
    - For authentication, you can set the C(SCM_ACCESS_TOKEN) environment variable instead of providing it as a module option.
'''

EXAMPLES = r'''
- name: Get all labels
  cdot65.scm.label_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_labels

- name: Get a specific label by ID
  cdot65.scm.label_info:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"
  register: label_details

- name: Get a specific label by name
  cdot65.scm.label_info:
    name: "environment"
    scm_access_token: "{{ scm_access_token }}"
  register: named_label
'''

RETURN = r'''
labels:
    description: List of label resources
    returned: always
    type: list
    elements: dict
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
'''

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient


def main():
    module_args = dict(
        id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        scm_access_token=dict(type='str', required=True, no_log=True),
        api_url=dict(type='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[['id', 'name']],
        supports_check_mode=True
    )

    params = module.params
    label_id = params.get('id')
    name = params.get('name')
    scm_access_token = params.get('scm_access_token')
    api_url = params.get('api_url')

    result = dict(
        changed=False,
        labels=[]
    )

    try:
        sdk_args = dict(access_token=scm_access_token)
        if api_url:
            sdk_args['base_url'] = api_url
        client = ScmClient(**sdk_args)
        label_service = client.label

        if label_id:
            label_obj = label_service.get(label_id)
            if label_obj:
                result['labels'] = [json.loads(label_obj.model_dump_json(exclude_unset=True))]
        elif name:
            label_obj = label_service.fetch(name=name)
            if label_obj:
                result['labels'] = [json.loads(label_obj.model_dump_json(exclude_unset=True))]
        else:
            labels = label_service.list()
            result['labels'] = [json.loads(l.model_dump_json(exclude_unset=True)) for l in labels]
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve label info: {e}")


if __name__ == '__main__':
    main()
