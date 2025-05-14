#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: dynamic_user_group_info
short_description: Get information about dynamic user group objects in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about dynamic user group objects in Strata Cloud Manager.
    - It can be used to get details about a specific dynamic user group by ID or name, or to list all dynamic user groups.
    - Supports filtering by properties like filter expressions, tags, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the dynamic user group object to retrieve.
            - If specified, the module will return information about this specific dynamic user group.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the dynamic user group object to retrieve.
            - If specified, the module will search for dynamic user groups with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    filters:
        description:
            - Filter dynamic user groups by filter expression content.
            - This will match any dynamic user group whose filter contains the provided string.
        type: list
        elements: str
        required: false
    tags:
        description:
            - Filter dynamic user groups by tags.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter dynamic user groups by folder name.
            - Required when retrieving dynamic user groups by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter dynamic user groups by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter dynamic user groups by device identifier.
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
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Dynamic user group objects must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all dynamic user group objects
  cdot65.scm.dynamic_user_group_info:
    folder: "User-Groups"  # container parameter is required for listing
    scm_access_token: "{{ scm_access_token }}"
  register: all_dynamic_user_groups

- name: Get a specific dynamic user group by ID
  cdot65.scm.dynamic_user_group_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: dynamic_user_group_details

- name: Get dynamic user group with a specific name
  cdot65.scm.dynamic_user_group_info:
    name: "high-risk-users"
    folder: "User-Groups"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_dynamic_user_group

- name: Get dynamic user groups with specific filter content
  cdot65.scm.dynamic_user_group_info:
    filters: ["tag.criticality.high"]
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_dynamic_user_groups

- name: Get dynamic user groups with specific tags
  cdot65.scm.dynamic_user_group_info:
    tags: ["marketing", "external"]
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_dynamic_user_groups

- name: Get dynamic user groups in a specific folder
  cdot65.scm.dynamic_user_group_info:
    folder: "User-Groups"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_dynamic_user_groups

- name: Get dynamic user groups in a specific snippet
  cdot65.scm.dynamic_user_group_info:
    snippet: "user-acl"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_dynamic_user_groups

- name: Get dynamic user groups for a specific device
  cdot65.scm.dynamic_user_group_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_dynamic_user_groups
"""

RETURN = r"""
dynamic_user_groups:
    description: List of dynamic user group objects
    returned: always
    type: list
    elements: dict
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
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        filters=dict(type="list", elements="str", required=False),
        tags=dict(type="list", elements="str", required=False),
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
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"dynamic_user_groups": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get a dynamic user group by ID if specified
        if params.get("id"):
            try:
                dynamic_user_group_obj = client.dynamic_user_group.get(params.get("id"))
                if dynamic_user_group_obj:
                    result["dynamic_user_groups"] = [json.loads(dynamic_user_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve dynamic user group info: {e}")
        # Fetch a dynamic user group by name
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
                        msg="When retrieving a dynamic user group by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the dynamic user group object
                dynamic_user_group_obj = client.dynamic_user_group.fetch(
                    name=params.get("name"), **{container_type: container_name}
                )
                if dynamic_user_group_obj:
                    result["dynamic_user_groups"] = [json.loads(dynamic_user_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve dynamic user group info: {e}")

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
                    msg="At least one container parameter (folder, snippet, or device) is required for listing dynamic user groups"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List dynamic user groups with container filters
            dynamic_user_groups = client.dynamic_user_group.list(**filter_params)

            # Apply additional client-side filtering
            if params.get("filters") or params.get("tags"):
                additional_filters = {}

                if params.get("filters"):
                    additional_filters["filters"] = params.get("filters")

                if params.get("tags"):
                    additional_filters["tags"] = params.get("tags")

                # Apply client-side filtering
                dynamic_user_groups = client.dynamic_user_group._apply_filters(dynamic_user_groups, additional_filters)

            # Convert to a list of dicts
            dynamic_user_group_dicts = [json.loads(g.model_dump_json(exclude_unset=True)) for g in dynamic_user_groups]

            # Add to results
            result["dynamic_user_groups"] = dynamic_user_group_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve dynamic user group info: {e}")


if __name__ == "__main__":
    main()
