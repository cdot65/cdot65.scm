#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
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
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
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
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[["id", "name"]],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"labels": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get label by ID if specified
        if params.get("id"):
            try:
                label_obj = client.label.get(params.get("id"))
                if label_obj:
                    result["labels"] = [json.loads(label_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve label info: {e}")
        # Fetch a label by name
        elif params.get("name"):
            try:
                label_obj = client.label.fetch(name=params.get("name"))
                if label_obj:
                    result["labels"] = [json.loads(label_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve label info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}
            # Add more filters here if applicable to the label API

            # List labels with filters
            if filter_params:
                labels = client.label.list(**filter_params)
            else:
                labels = client.label.list()

            label_dicts = [json.loads(each.model_dump_json(exclude_unset=True)) for each in labels]
            result["labels"] = label_dicts
        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve label info: {e}")


if __name__ == "__main__":
    main()
