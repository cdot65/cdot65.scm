#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup import VariableCreateModel

DOCUMENTATION = r"""
---
module: variable
short_description: Manage variables in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete variables in Strata Cloud Manager using pan-scm-sdk.
    - Supports all variable attributes and robust idempotency.
    - Variables must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the variable.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    type:
        description:
            - Type of the variable.
            - Required for state=present.
            - Valid types include percent, count, ip-netmask, zone, ip-range, ip-wildcard,
              device-priority, device-id, egress-max, as-number, fqdn, port, link-tag,
              group-id, rate, router-id, qos-profile, timer.
        type: str
        required: false
        choices:
            - percent
            - count
            - ip-netmask
            - zone
            - ip-range
            - ip-wildcard
            - device-priority
            - device-id
            - egress-max
            - as-number
            - fqdn
            - port
            - link-tag
            - group-id
            - rate
            - router-id
            - qos-profile
            - timer
    value:
        description:
            - Value of the variable.
            - Required for state=present.
        type: str
        required: false
    description:
        description:
            - Description of the variable.
        type: str
        required: false
    folder:
        description:
            - The folder in which the variable is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the variable is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the variable is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the variable (UUID).
            - Used for lookup/deletion if provided.
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token for authenticating API calls, provided by the auth role.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
            - If not specified, the value of the SCM_API_URL environment variable will be used.
        type: str
        required: false
    state:
        description:
            - Desired state of the variable.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Variables must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Create a folder-based variable
  cdot65.scm.variable:
    name: "subnet-variable"
    type: "ip-netmask"
    value: "192.168.1.0/24"
    description: "Network subnet for department A"
    folder: "department-a"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based variable
  cdot65.scm.variable:
    name: "web-port"
    type: "port"
    value: "8080"
    description: "Web server port"
    snippet: "web-servers"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a device-based variable
  cdot65.scm.variable:
    name: "device-ip"
    type: "ip-netmask"
    value: "10.0.0.1/32"
    description: "Device management IP"
    device: "001122334455"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a variable's value
  cdot65.scm.variable:
    name: "subnet-variable"
    type: "ip-netmask"
    value: "10.0.0.0/16"
    folder: "department-a"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a variable by name
  cdot65.scm.variable:
    name: "subnet-variable"
    folder: "department-a"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a variable by ID
  cdot65.scm.variable:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
variable:
    description: Information about the variable that was managed
    returned: on success
    type: dict
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
    module_args = dict(
        name=dict(type="str", required=False),
        type=dict(
            type="str",
            required=False,
            choices=[
                "percent",
                "count",
                "ip-netmask",
                "zone",
                "ip-range",
                "ip-wildcard",
                "device-priority",
                "device-id",
                "egress-max",
                "as-number",
                "fqdn",
                "port",
                "link-tag",
                "group-id",
                "rate",
                "router-id",
                "qos-profile",
                "timer",
            ],
        ),
        value=dict(type="str", required=False),
        description=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "type", "value"]],
            ["state", "absent", ["name"]],
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "variable": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize variable_exists boolean
        variable_exists = False
        variable_obj = None

        # Fetch variable by name
        if params.get("name"):
            try:
                # Handle different container types (folder, snippet, device)
                container_type = None
                container_name = None

                if params.get("folder"):
                    container_type = "folder"
                    container_name = params.get("folder")
                elif params.get("snippet"):
                    container_type = "snippet"
                    container_name = params.get("snippet")
                elif params.get("device"):
                    container_type = "device"
                    container_name = params.get("device")

                # Get all variables and filter client-side if needed
                if container_type == "folder" and container_name:
                    # The fetch method works directly with folders
                    variable_obj = client.variable.fetch(folder=container_name, name=params.get("name"))
                elif container_type and container_name:
                    # For snippet and device, filter using the list API with the container parameter
                    # Get only variables in the specific container
                    variables = client.variable.list(**{container_type: container_name})
                    # Filter for exact name match
                    for var in variables:
                        if var.name == params.get("name"):
                            variable_obj = var
                            break

                if variable_obj:
                    variable_exists = True
            except ObjectNotPresentError:
                variable_exists = False
                variable_obj = None

        # Create or update or delete a variable
        if params.get("state") == "present":
            if variable_exists:
                # Only update fields that differ
                update_fields = {
                    k: params[k]
                    for k in [
                        "type",
                        "value",
                        "description",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(variable_obj, k, None) != params[k]
                }

                # Update a variable if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = variable_obj.model_copy(update=update_fields)
                        updated = client.variable.update(update_model)
                        result["variable"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["variable"] = json.loads(variable_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["variable"] = json.loads(variable_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "type",
                        "value",
                        "description",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a variable
                if not module.check_mode:
                    # Create a variable
                    created = client.variable.create(create_payload)

                    # Return a created variable
                    result["variable"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created variable (minimal info)
                    simulated = VariableCreateModel(**create_payload)
                    result["variable"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a variable
        elif params.get("state") == "absent":
            if variable_exists:
                if not module.check_mode:
                    client.variable.delete(variable_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["variable"] = json.loads(variable_obj.model_dump_json(exclude_unset=True))
                module.exit_json(**result)
            else:
                # Already absent
                result["changed"] = False
                module.exit_json(**result)

    # Handle errors
    except (ObjectNotPresentError, InvalidObjectError) as e:
        module.fail_json(msg=str(e), error_code=getattr(e, "error_code", None), details=getattr(e, "details", None))
    except APIError as e:
        module.fail_json(
            msg="API error: " + str(e), error_code=getattr(e, "error_code", None), details=getattr(e, "details", None)
        )
    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
