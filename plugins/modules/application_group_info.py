#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: application_group_info
short_description: Get information about application groups in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about application groups in Strata Cloud Manager.
    - It can be used to get details about a specific application group by ID or name, or to list all application groups.
    - Supports filtering by application group properties like type, members, tags, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the application group to retrieve.
            - If specified, the module will return information about this specific application group.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the application group to retrieve.
            - If specified, the module will search for application groups with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    type:
        description:
            - Filter application groups by type.
            - Supported types are 'static' and 'dynamic'.
        type: str
        required: false
        choices: ['static', 'dynamic']
    member:
        description:
            - Filter static application groups that contain the specified member application.
            - Only applies to static application groups.
        type: str
        required: false
    filter_pattern:
        description:
            - Filter dynamic application groups by filter pattern.
            - Only applies to dynamic application groups.
            - This is a substring search on the dynamic_filter field.
            - For example, to find filters containing app.category.business-systems, use filter_pattern="app.category.business-systems"
        type: str
        required: false
    tag:
        description:
            - Filter application groups by tags.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter application groups by folder name.
            - Required when retrieving application groups by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter application groups by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter application groups by device identifier.
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
    - Application groups must be associated with exactly one container (folder, snippet, or device).
    - 'Application groups are of two types: static (containing a list of application objects) or dynamic (defined by a filter expression).'
"""

EXAMPLES = r"""
- name: Get all application groups
  cdot65.scm.application_group_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_application_groups

- name: Get a specific application group by ID
  cdot65.scm.application_group_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: application_group_details

- name: Get application group with a specific name
  cdot65.scm.application_group_info:
    name: "web-apps"
    folder: "Application-Objects"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_application_group

- name: Get static application groups
  cdot65.scm.application_group_info:
    type: "static"
    scm_access_token: "{{ scm_access_token }}"
  register: static_application_groups

- name: Get dynamic application groups
  cdot65.scm.application_group_info:
    type: "dynamic"
    scm_access_token: "{{ scm_access_token }}"
  register: dynamic_application_groups

- name: Get static application groups containing a specific member
  cdot65.scm.application_group_info:
    member: "http"
    scm_access_token: "{{ scm_access_token }}"
  register: member_application_groups

- name: Get dynamic application groups with filter matching a pattern
  cdot65.scm.application_group_info:
    filter_pattern: "'app.category.business-systems"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_application_groups

- name: Get application groups with specific tags
  cdot65.scm.application_group_info:
    tag: ["web", "dynamic"]
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_application_groups

- name: Get application groups in a specific folder
  cdot65.scm.application_group_info:
    folder: "Application-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_application_groups

- name: Get application groups in a specific snippet
  cdot65.scm.application_group_info:
    snippet: "web-acl"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_application_groups

- name: Get application groups for a specific device
  cdot65.scm.application_group_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_application_groups
"""

RETURN = r"""
application_groups:
    description: List of application groups
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The application group ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The application group name
            type: str
            returned: always
            sample: "web-apps"
        description:
            description: The application group description
            type: str
            returned: when applicable
            sample: "Web application group"
        members:
            description: List of application objects (for static groups) or filter expressions (for dynamic groups)
            type: list
            returned: always
            sample:
                - ["http", "https"]
                - ["app.category.business-systems"]
        tag:
            description: Tags associated with the application group
            type: list
            returned: when applicable
            sample: ["web", "dynamic"]
        folder:
            description: The folder containing the application group
            type: str
            returned: when applicable
            sample: "Application-Objects"
        snippet:
            description: The snippet containing the application group
            type: str
            returned: when applicable
            sample: "web-acl"
        device:
            description: The device containing the application group
            type: str
            returned: when applicable
            sample: "firewall-01"
        type:
            description: The type of application group (static or dynamic)
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

    result = {"application_groups": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get application group by ID if specified
        if params.get("id"):
            try:
                application_group_obj = client.application_group.get(params.get("id"))
                if application_group_obj:
                    result["application_groups"] = [json.loads(application_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application group info: {e}")
        # Fetch application group by name
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
                        msg="When retrieving an application group by name, exactly one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the application group object
                application_group_obj = client.application_group.fetch(
                    name=params.get("name"), **{container_type: container_name}
                )
                if application_group_obj:
                    result["application_groups"] = [json.loads(application_group_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application group info: {e}")

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
                    msg="Exactly one container parameter (folder, snippet, or device) is required for listing application groups"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List application groups with container filters
            application_groups = client.application_group.list(**filter_params)

            # Apply additional client-side filtering
            filtered_groups = []

            for group in application_groups:
                # Filter by type (static or dynamic)
                if params.get("type"):
                    # For SCM application groups, we infer type based on the content of members
                    # If the first member starts with a quote, it's likely a filter expression (dynamic)
                    is_dynamic = False
                    if hasattr(group, "members") and len(group.members) > 0:
                        # Simple heuristic: if first member starts with a quote, it's likely a filter
                        is_dynamic = group.members[0].startswith("'") or group.members[0].startswith('"')

                    if params.get("type") == "static" and is_dynamic:
                        continue
                    if params.get("type") == "dynamic" and not is_dynamic:
                        continue

                # Filter by member (for static groups)
                if params.get("member") and hasattr(group, "members"):
                    # Skip filter expressions (which start with quotes)
                    if len(group.members) > 0 and not group.members[0].startswith("'") and not group.members[0].startswith('"'):
                        if params.get("member") not in group.members:
                            continue

                # Filter by filter pattern (for dynamic groups)
                if params.get("filter_pattern") and hasattr(group, "members"):
                    # Only consider the first member if it starts with a quote (dynamic filter)
                    if len(group.members) > 0 and (group.members[0].startswith("'") or group.members[0].startswith('"')):
                        if params.get("filter_pattern") not in group.members[0]:
                            continue

                # Filter by tags
                if params.get("tag") and hasattr(group, "tag"):
                    group_tags = getattr(group, "tag", [])
                    if not all(tag in group_tags for tag in params.get("tag")):
                        continue

                # Add to filtered results
                filtered_groups.append(group)

            # Convert to a list of dicts
            application_group_dicts = [json.loads(g.model_dump_json(exclude_unset=True)) for g in filtered_groups]

            # Add to results
            result["application_groups"] = application_group_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve application group info: {e}")


if __name__ == "__main__":
    main()
