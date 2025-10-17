#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: service_group_info
short_description: Get information about service groups in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about service groups in Strata Cloud Manager.
    - It can be used to get details about a specific service group by ID or name, or to list all service groups.
    - Supports filtering by service group properties like members, tags, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the service group to retrieve.
            - If specified, the module will return information about this specific service group.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the service group to retrieve.
            - If specified, the module will search for service groups with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    member:
        description:
            - Filter service groups that contain the specified member service.
            - This is a substring search on the members list.
        type: str
        required: false
    tag:
        description:
            - Filter service groups by tags.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter service groups by folder name.
            - Required when retrieving service groups by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter service groups by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter service groups by device identifier.
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
    - Service groups must be associated with exactly one container (folder, snippet, or device).
    - Service groups contain a list of service members for organizing and managing service objects.
"""

EXAMPLES = r"""
- name: Get all service groups
  cdot65.scm.service_group_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_service_groups

- name: Get a specific service group by ID
  cdot65.scm.service_group_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: service_group_details

- name: Get service group with a specific name
  cdot65.scm.service_group_info:
    name: "web-services"
    folder: "Network-Services"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_service_group

- name: Get service groups containing a specific member
  cdot65.scm.service_group_info:
    member: "custom-http"
    scm_access_token: "{{ scm_access_token }}"
  register: member_service_groups

- name: Get service groups with specific tags
  cdot65.scm.service_group_info:
    tag:
      - "web"
      - "production"
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_service_groups

- name: Get service groups in a specific folder
  cdot65.scm.service_group_info:
    folder: "Network-Services"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_service_groups

- name: Get service groups in a specific snippet
  cdot65.scm.service_group_info:
    snippet: "web-config"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_service_groups

- name: Get service groups for a specific device
  cdot65.scm.service_group_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_service_groups
"""

RETURN = r"""
service_groups:
    description: List of service groups
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The service group ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The service group name
            type: str
            returned: always
            sample: "web-services"
        members:
            description: List of service members in the group
            type: list
            returned: always
            sample: ["custom-http", "custom-https"]
        tag:
            description: Tags associated with the service group
            type: list
            returned: when applicable
            sample: ["web", "production"]
        folder:
            description: The folder containing the service group
            type: str
            returned: when applicable
            sample: "Network-Services"
        snippet:
            description: The snippet containing the service group
            type: str
            returned: when applicable
            sample: "web-config"
        device:
            description: The device containing the service group
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        member=dict(type="str", required=False),
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
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"service_groups": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get service group by ID if specified
        if params.get("id"):
            try:
                service_group_obj = client.service_group.get(params.get("id"))
                if service_group_obj:
                    result["service_groups"] = [json.loads(service_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve service group info: {e}")
        # Fetch service group by name
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
                        msg="When retrieving a service group by name, exactly one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the service group object
                service_group_obj = client.service_group.fetch(name=params.get("name"), **{container_type: container_name})
                if service_group_obj:
                    result["service_groups"] = [json.loads(service_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve service group info: {e}")

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
                    msg="Exactly one container parameter (folder, snippet, or device) is required for listing service groups"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List service groups with container filters
            service_groups = client.service_group.list(**filter_params)

            # Apply additional client-side filtering
            filtered_groups = []

            for group in service_groups:
                # Filter by member
                if params.get("member") and hasattr(group, "members"):
                    if params.get("member") not in getattr(group, "members", []):
                        continue

                # Filter by tags
                if params.get("tag") and hasattr(group, "tag"):
                    group_tags = getattr(group, "tag", [])
                    if not all(tag in group_tags for tag in params.get("tag")):
                        continue

                # Add to filtered results
                filtered_groups.append(group)

            # Convert to a list of dicts
            service_group_dicts = [json.loads(g.model_dump_json(exclude_unset=True)) for g in filtered_groups]

            # Add to results
            result["service_groups"] = service_group_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve service group info: {e}")


if __name__ == "__main__":
    main()
