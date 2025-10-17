#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: address_group_info
short_description: Get information about address groups in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about address groups in Strata Cloud Manager.
    - It can be used to get details about a specific address group by ID or name, or to list all address groups.
    - Supports filtering by address group properties like type, members, tags, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the address group to retrieve.
            - If specified, the module will return information about this specific address group.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the address group to retrieve.
            - If specified, the module will search for address groups with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    type:
        description:
            - Filter address groups by type.
            - Supported types are 'static' and 'dynamic'.
        type: str
        required: false
        choices: ['static', 'dynamic']
    member:
        description:
            - Filter static address groups that contain the specified member address.
            - Only applies to static address groups.
        type: str
        required: false
    filter_pattern:
        description:
            - Filter dynamic address groups by filter pattern.
            - Only applies to dynamic address groups.
            - This is a substring search on the dynamic_filter field.
            - For example, to find filters containing aws.ec2.tag.Server, use filter_pattern="aws.ec2.tag.Server"
        type: str
        required: false
    tag:
        description:
            - Filter address groups by tags.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter address groups by folder name.
            - Required when retrieving address groups by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter address groups by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter address groups by device identifier.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: False
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Address groups must be associated with exactly one container (folder, snippet, or device).
    - Address groups are of two types: static (containing a list of address objects) or dynamic (defined by a filter expression).
"""

EXAMPLES = r"""
- name: Get all address groups
  cdot65.scm.address_group_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_address_groups

- name: Get a specific address group by ID
  cdot65.scm.address_group_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: address_group_details

- name: Get address group with a specific name
  cdot65.scm.address_group_info:
    name: "web-servers"
    folder: "Network-Objects"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_address_group

- name: Get static address groups
  cdot65.scm.address_group_info:
    type: "static"
    scm_access_token: "{{ scm_access_token }}"
  register: static_address_groups

- name: Get dynamic address groups
  cdot65.scm.address_group_info:
    type: "dynamic"
    scm_access_token: "{{ scm_access_token }}"
  register: dynamic_address_groups

- name: Get static address groups containing a specific member
  cdot65.scm.address_group_info:
    member: "web-server-1"
    scm_access_token: "{{ scm_access_token }}"
  register: member_address_groups

- name: Get dynamic address groups with filter matching a pattern
  cdot65.scm.address_group_info:
    filter_pattern: "'aws.ec2.tag.Server"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_address_groups

- name: Get address groups with specific tags
  cdot65.scm.address_group_info:
    tag: ["web", "dynamic"]
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_address_groups

- name: Get address groups in a specific folder
  cdot65.scm.address_group_info:
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_address_groups

- name: Get address groups in a specific snippet
  cdot65.scm.address_group_info:
    snippet: "web-acl"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_address_groups

- name: Get address groups for a specific device
  cdot65.scm.address_group_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_address_groups
"""

RETURN = r"""
address_groups:
    description: List of address groups
    returned: always
    type: list
    elements: dict
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
            sample: "'aws.ec2.tag.Server.web'"
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
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        type=dict(type="str", required=False, choices=["static", "dynamic"]),
        member=dict(type="str", required=False),
        filter_pattern=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet", "device"],
            ["member", "filter_pattern"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"address_groups": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get address group by ID if specified
        if params.get("id"):
            try:
                address_group_obj = client.address_group.get(params.get("id"))
                if address_group_obj:
                    result["address_groups"] = [json.loads(address_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve address group info: {e}")
        # Fetch address group by name
        elif params.get("name"):
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

                # We need a container for the fetch operation
                if not container_type or not container_name:
                    module.fail_json(
                        msg="When retrieving an address group by name, exactly one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the address group object
                address_group_obj = client.address_group.fetch(name=params.get("name"), **{container_type: container_name})
                if address_group_obj:
                    result["address_groups"] = [json.loads(address_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve address group info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet, device) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                filter_params["device"] = params.get("device")
            else:
                module.fail_json(
                    msg="Exactly one container parameter (folder, snippet, or device) is required for listing address groups"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List address groups with container filters
            address_groups = client.address_group.list(**filter_params)

            # Apply additional client-side filtering
            filtered_groups = []

            for group in address_groups:
                # Filter by type (static or dynamic)
                if params.get("type"):
                    if params.get("type") == "static" and getattr(group, "dynamic_filter", None) is not None:
                        continue
                    if params.get("type") == "dynamic" and getattr(group, "static_addresses", None) is not None:
                        continue

                # Filter by member (for static groups)
                if params.get("member") and hasattr(group, "static_addresses"):
                    if params.get("member") not in getattr(group, "static_addresses", []):
                        continue

                # Filter by filter pattern (for dynamic groups)
                if params.get("filter_pattern") and hasattr(group, "dynamic_filter"):
                    if params.get("filter_pattern") not in getattr(group, "dynamic_filter", ""):
                        continue

                # Filter by tags
                if params.get("tag") and hasattr(group, "tag"):
                    group_tags = getattr(group, "tag", [])
                    if not all(tag in group_tags for tag in params.get("tag")):
                        continue

                # Add to filtered results
                filtered_groups.append(group)

            # Convert to a list of dicts
            address_group_dicts = [json.loads(g.model_dump_json(exclude_unset=True)) for g in filtered_groups]

            # Add to results
            result["address_groups"] = address_group_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve address group info: {e}")


if __name__ == "__main__":
    main()
