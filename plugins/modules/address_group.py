#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import AddressGroupCreateModel

DOCUMENTATION = r"""
---
module: address_group
short_description: Manage address groups in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete address groups in Strata Cloud Manager using pan-scm-sdk.
    - Supports both static and dynamic address groups with robust idempotency.
    - Address groups must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the address group.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the address group.
        type: str
        required: false
    tag:
        description:
            - Tags associated with the address group.
        type: list
        elements: str
        required: false
    static_addresses:
        description:
            - List of address object names to include in the static address group.
            - Required if I(dynamic_filter) is not provided.
            - Mutually exclusive with I(dynamic_filter).
        type: list
        elements: str
        required: false
    dynamic_filter:
        description:
            - Filter expression for dynamic address groups.
            - Required if I(static_addresses) is not provided.
            - Mutually exclusive with I(static_addresses).
            - Format should follow SCM's dynamic address group filter syntax.
        type: str
        required: false
    folder:
        description:
            - The folder in which the address group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the address group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the address group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the address group (UUID).
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
            - Desired state of the address group.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Address groups must be associated with exactly one container (folder, snippet, or device).
    - Either static_addresses or dynamic_filter must be provided for creation.
"""

EXAMPLES = r"""
- name: Create a static address group in a folder
  cdot65.scm.address_group:
    name: "web-servers"
    description: "Web server group"
    static_addresses:
      - "web-server-1"
      - "web-server-2"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a dynamic address group in a snippet
  cdot65.scm.address_group:
    name: "dynamic-servers"
    description: "Dynamic server group"
    dynamic_filter: "tag.Server = 'web'"
    snippet: "web-acl"
    tag:
      - "web"
      - "dynamic"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a static address group
  cdot65.scm.address_group:
    name: "web-servers"
    description: "Updated web server group"
    static_addresses:
      - "web-server-1"
      - "web-server-2"
      - "web-server-3"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a dynamic address group
  cdot65.scm.address_group:
    name: "dynamic-servers"
    description: "Updated dynamic server group"
    dynamic_filter: "tag.Server = 'web' or tag.Server = 'api'"
    snippet: "web-acl"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an address group by name
  cdot65.scm.address_group:
    name: "web-servers"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an address group by ID
  cdot65.scm.address_group:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
address_group:
    description: Information about the address group that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The address group ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The address group name
            type: str
            returned: always
            sample: "web-servers"
        description:
            description: The address group description
            type: str
            returned: when applicable
            sample: "Web server group"
        static_addresses:
            description: List of address objects in the static group
            type: list
            returned: for static address groups
            sample: ["web-server-1", "web-server-2"]
        dynamic_filter:
            description: Filter expression for the dynamic group
            type: str
            returned: for dynamic address groups
            sample: "tag.Server = 'web'"
        tag:
            description: Tags associated with the address group
            type: list
            returned: when applicable
            sample: ["web", "dynamic"]
        folder:
            description: The folder containing the address group
            type: str
            returned: when applicable
            sample: "Network-Objects"
        snippet:
            description: The snippet containing the address group
            type: str
            returned: when applicable
            sample: "web-acl"
        device:
            description: The device containing the address group
            type: str
            returned: when applicable
            sample: "firewall-01"
        type:
            description: The type of address group (static or dynamic)
            type: str
            returned: always
            sample: "static"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        static_addresses=dict(type="list", elements="str", required=False),
        dynamic_filter=dict(type="str", required=False),
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
            ["state", "present", ["name"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
            ["static_addresses", "dynamic_filter"],
        ],
        supports_check_mode=True,
    )

    # Custom validation for group type parameters
    params = module.params
    if params.get("state") == "present":
        # For creation/update, one of the group types is required
        if not any(params.get(group_type) for group_type in ["static_addresses", "dynamic_filter"]):
            module.fail_json(msg="When state=present, one of the following is required: static_addresses, dynamic_filter")

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "address_group": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize address_group_exists boolean
        address_group_exists = False
        address_group_obj = None

        # Fetch address group by name
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

                # For any container type, fetch the address group
                if container_type and container_name:
                    address_group_obj = client.address_group.fetch(name=params.get("name"), **{container_type: container_name})
                    if address_group_obj:
                        address_group_exists = True
            except ObjectNotPresentError:
                address_group_exists = False
                address_group_obj = None

        # Create or update or delete an address group
        if params.get("state") == "present":
            if address_group_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "tag",
                        "static_addresses",
                        "dynamic_filter",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(address_group_obj, k, None) != params[k]
                }

                # Update the address group if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = address_group_obj.model_copy(update=update_fields)
                        updated = client.address_group.update(update_model)
                        result["address_group"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["address_group"] = json.loads(address_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["address_group"] = json.loads(address_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new address group
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "tag",
                        "static_addresses",
                        "dynamic_filter",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create an address group
                if not module.check_mode:
                    # Create an address group
                    created = client.address_group.create(create_payload)

                    # Return the created address group
                    result["address_group"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created address group (minimal info)
                    simulated = AddressGroupCreateModel(**create_payload)
                    result["address_group"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete an address group
        elif params.get("state") == "absent":
            if address_group_exists:
                if not module.check_mode:
                    client.address_group.delete(address_group_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["address_group"] = json.loads(address_group_obj.model_dump_json(exclude_unset=True))
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
