#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import DynamicUserGroupCreateModel

DOCUMENTATION = r"""
---
module: dynamic_user_group
short_description: Manage dynamic user group objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete dynamic user group objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all dynamic user group attributes and robust idempotency.
    - Dynamic user group objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the dynamic user group object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the dynamic user group object.
        type: str
        required: false
    tag:
        description:
            - Tags associated with the dynamic user group object.
        type: list
        elements: str
        required: false
    filter:
        description:
            - The tag-based filter expression for the dynamic user group.
            - Required for state=present.
            - Maximum length is 2047 characters.
        type: str
        required: false
    folder:
        description:
            - The folder in which the dynamic user group object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the dynamic user group object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the dynamic user group object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the dynamic user group object (UUID).
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
            - Desired state of the dynamic user group object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Dynamic user group objects must be associated with exactly one container (folder, snippet, or device).
    - Filter expression is required for creating or updating dynamic user groups.
"""

EXAMPLES = r"""
- name: Create a folder-based dynamic user group
  cdot65.scm.dynamic_user_group:
    name: "high-risk-users"
    description: "Users with high risk profile"
    filter: "tag.criticality.high"
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based dynamic user group with tags
  cdot65.scm.dynamic_user_group:
    name: "marketing-users"
    description: "Users from marketing department"
    filter: "tag.department.marketing"
    snippet: "user-acl"
    tag:
      - "marketing"
      - "external"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a device-based dynamic user group with complex filter
  cdot65.scm.dynamic_user_group:
    name: "temporary-contractors"
    description: "Temporary contractors with limited access"
    filter: "tag.role.contractor and tag.status.active"
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a dynamic user group's filter expression
  cdot65.scm.dynamic_user_group:
    name: "high-risk-users"
    description: "Users with high risk profile - updated"
    filter: "tag.criticality.high or tag.status.compromised"
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a dynamic user group by name
  cdot65.scm.dynamic_user_group:
    name: "high-risk-users"
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a dynamic user group by ID
  cdot65.scm.dynamic_user_group:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
dynamic_user_group:
    description: Information about the dynamic user group object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The dynamic user group object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The dynamic user group object name
            type: str
            returned: always
            sample: "high-risk-users"
        description:
            description: The dynamic user group object description
            type: str
            returned: when applicable
            sample: "Users with high risk profile"
        filter:
            description: The tag-based filter expression
            type: str
            returned: always
            sample: "tag.criticality.high"
        tag:
            description: Tags associated with the dynamic user group object
            type: list
            returned: when applicable
            sample: ["marketing", "external"]
        folder:
            description: The folder containing the dynamic user group object
            type: str
            returned: when applicable
            sample: "User-Groups"
        snippet:
            description: The snippet containing the dynamic user group object
            type: str
            returned: when applicable
            sample: "user-acl"
        device:
            description: The device containing the dynamic user group object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        filter=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "filter"]],  # Both name and filter required for present
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for container parameters
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False, "dynamic_user_group": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize dynamic_user_group_exists boolean
        dynamic_user_group_exists = False
        dynamic_user_group_obj = None

        # Fetch a dynamic user group by name
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

                # For any container type, fetch the dynamic user group object
                if container_type and container_name:
                    dynamic_user_group_obj = client.dynamic_user_group.fetch(
                        name=params.get("name"), **{container_type: container_name}
                    )
                    if dynamic_user_group_obj:
                        dynamic_user_group_exists = True
            except ObjectNotPresentError:
                dynamic_user_group_exists = False
                dynamic_user_group_obj = None

        # Create or update or delete a dynamic_user_group
        if params.get("state") == "present":
            if dynamic_user_group_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "tag",
                        "filter",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(dynamic_user_group_obj, k, None) != params[k]
                }

                # Update the dynamic user group if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = dynamic_user_group_obj.model_copy(update=update_fields)
                        updated = client.dynamic_user_group.update(update_model)
                        result["dynamic_user_group"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["dynamic_user_group"] = json.loads(dynamic_user_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["dynamic_user_group"] = json.loads(dynamic_user_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create a payload for a new dynamic user group object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "tag",
                        "filter",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a dynamic user group object
                if not module.check_mode:
                    # Create a dynamic user group object
                    created = client.dynamic_user_group.create(create_payload)

                    # Return the created dynamic user group object
                    result["dynamic_user_group"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created dynamic user group object (minimal info)
                    simulated = DynamicUserGroupCreateModel(**create_payload)
                    result["dynamic_user_group"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a dynamic user group object
        elif params.get("state") == "absent":
            if dynamic_user_group_exists:
                if not module.check_mode:
                    client.dynamic_user_group.delete(dynamic_user_group_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["dynamic_user_group"] = json.loads(dynamic_user_group_obj.model_dump_json(exclude_unset=True))
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
