#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: variable_info
short_description: Get information about variables in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about variables in Strata Cloud Manager.
    - It can be used to get details about a specific variable by ID or name, or to list all variables.
    - Supports filtering by variable properties like type, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the variable to retrieve.
            - If specified, the module will return information about this specific variable.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the variable to retrieve.
            - If specified, the module will search for variables with this name.
            - Mutually exclusive with I(id).
        type: str
        required: false
    type:
        description:
            - Filter variables by type (e.g., 'ip-netmask', 'port', 'count').
        type: str
        required: false
    folder:
        description:
            - Filter variables by folder name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter variables by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter variables by device identifier.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    labels:
        description:
            - Filter variables by labels.
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
    - Variables must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all variables
  cdot65.scm.variable_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_variables

- name: Get a specific variable by ID
  cdot65.scm.variable_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: variable_details

- name: Get variable with a specific name
  cdot65.scm.variable_info:
    name: "subnet-variable"
    scm_access_token: "{{ scm_access_token }}"
  register: named_variable

- name: Get variables by type
  cdot65.scm.variable_info:
    type: "ip-netmask"
    scm_access_token: "{{ scm_access_token }}"
  register: ip_variables

- name: Get variables in a specific folder
  cdot65.scm.variable_info:
    folder: "department-a"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_variables

- name: Get variables in a specific snippet
  cdot65.scm.variable_info:
    snippet: "web-servers"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_variables

- name: Get variables for a specific device
  cdot65.scm.variable_info:
    device: "001122334455"
    scm_access_token: "{{ scm_access_token }}"
  register: device_variables
"""

RETURN = r"""
variables:
    description: List of variable resources
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The variable ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The variable name
            type: str
            returned: always
            sample: "subnet-variable"
        type:
            description: The variable type
            type: str
            returned: always
            sample: "ip-netmask"
        value:
            description: The variable value
            type: str
            returned: always
            sample: "192.168.1.0/24"
        description:
            description: The variable description
            type: str
            returned: when applicable
            sample: "Network subnet for department A"
        folder:
            description: The folder containing the variable
            type: str
            returned: when applicable
            sample: "department-a"
        snippet:
            description: The snippet containing the variable
            type: str
            returned: when applicable
            sample: "web-servers"
        device:
            description: The device containing the variable
            type: str
            returned: when applicable
            sample: "001122334455"
        overridden:
            description: Whether the variable is overridden
            type: bool
            returned: when applicable
            sample: false
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        type=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        labels=dict(type="list", elements="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params
    variable_id = params.get("id")
    name = params.get("name")
    variable_type = params.get("type")
    folder = params.get("folder")
    snippet = params.get("snippet")
    device = params.get("device")
    labels = params.get("labels")

    result = {"variables": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params["scm_access_token"])
        variables_service = client.variable

        # Get variable by ID if specified
        if variable_id:
            try:
                variable = variables_service.get(variable_id)
                if variable:
                    result["variables"] = [json.loads(variable.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError:
                # Return empty list if variable not found
                result["variables"] = []
        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add SDK-supported server-side filters
            if variable_type:
                filter_params["type"] = variable_type

            # List variables with appropriate filters
            variables = variables_service.list(**filter_params)
            variable_dicts = [json.loads(v.model_dump_json(exclude_unset=True)) for v in variables]

            # Apply additional client-side filtering
            # Filter by name if specified (exact match)
            if name:
                variable_dicts = [v for v in variable_dicts if v.get("name") == name]

            # Filter by container (folder, snippet, or device)
            if folder:
                variable_dicts = [v for v in variable_dicts if v.get("folder") == folder]
            elif snippet:
                variable_dicts = [v for v in variable_dicts if v.get("snippet") == snippet]
            elif device:
                variable_dicts = [v for v in variable_dicts if v.get("device") == device]

            # Filter by labels if specified (any match)
            if labels:
                labels_set = set(labels)
                filtered_vars = []
                for v in variable_dicts:
                    var_labels = v.get("labels", [])
                    if var_labels and labels_set.intersection(set(var_labels)):
                        filtered_vars.append(v)
                variable_dicts = filtered_vars

            result["variables"] = variable_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(msg=f"API error: {e}", error_code=getattr(e, "error_code", None), details=getattr(e, "details", None))
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve variable info: {e}")


if __name__ == "__main__":
    main()
