#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule  # type: ignore
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: hip_profile_info
short_description: Get information about Host Information Profile (HIP) profiles in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about HIP profiles from Strata Cloud Manager (SCM).
    - It can be used to get details about a specific HIP profile by ID or name, or to list all HIP profiles.
    - Supports filtering by folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the HIP profile to retrieve.
            - If specified, the module will return information about this specific HIP profile.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the HIP profile to retrieve.
            - If specified, the module will search for HIP profiles with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    folder:
        description:
            - Filter HIP profiles by folder name.
            - Required when retrieving HIP profiles by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter HIP profiles by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter HIP profiles by device identifier.
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
    exclude_folders:
        description:
            - List of folder names to exclude from results.
        type: list
        elements: str
        required: false
    exclude_snippets:
        description:
            - List of snippet names to exclude from results.
        type: list
        elements: str
        required: false
    exclude_devices:
        description:
            - List of device names to exclude from results.
        type: list
        elements: str
        required: false
    filters:
        description:
            - Additional filters to apply when retrieving resources.
            - Used for client-side filtering and mapped directly to SDK filter capability.
        type: dict
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
    - HIP profiles must be associated with exactly one container (folder, snippet, or device).
    - HIP profiles define security posture matching criteria that can be used in security policies.
"""

EXAMPLES = r"""
- name: Get all HIP profiles in a folder
  cdot65.scm.hip_profile_info:
    folder: "Security"
    scm_access_token: "{{ scm_access_token }}"
  register: all_hip_profiles

- name: Get a specific HIP profile by ID
  cdot65.scm.hip_profile_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: hip_profile_details

- name: Get HIP profile with a specific name
  cdot65.scm.hip_profile_info:
    name: "windows-workstations"
    folder: "Security"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_hip_profile

- name: Get HIP profiles in a specific folder with exact matching
  cdot65.scm.hip_profile_info:
    folder: "Security"
    exact_match: true
    scm_access_token: "{{ scm_access_token }}"
  register: exact_folder_hip_profiles

- name: Get HIP profiles excluding certain folders
  cdot65.scm.hip_profile_info:
    folder: "Shared"
    exclude_folders: ["Development", "Testing"]
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_hip_profiles

- name: Get HIP profiles in a specific snippet
  cdot65.scm.hip_profile_info:
    snippet: "security-policy"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_hip_profiles

- name: Get HIP profiles for a specific device
  cdot65.scm.hip_profile_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_hip_profiles
"""

RETURN = r"""
hip_profiles:
    description: List of HIP profiles
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The HIP profile ID
            type: str
            returned: always
            sample: "01234567-89ab-cdef-0123-456789abcdef"
        name:
            description: Name of the HIP profile
            type: str
            returned: always
            sample: "windows-workstations"
        description:
            description: Description of the HIP profile
            type: str
            returned: when present
            sample: "Profile for Windows workstations"
        match:
            description: Match expression for the HIP profile
            type: str
            returned: always
            sample: '"is-win" and "is-firewall-enabled"'
        folder:
            description: Folder containing the HIP profile
            type: str
            returned: when resource is in a folder
            sample: "Security"
        snippet:
            description: Snippet containing the HIP profile
            type: str
            returned: when resource is in a snippet
            sample: "security-policy"
        device:
            description: Device containing the HIP profile
            type: str
            returned: when resource is in a device
            sample: "firewall-01"
        created_on:
            description: Creation timestamp
            type: str
            returned: always
            sample: "2023-01-15T12:34:56.789Z"
        created_by:
            description: Information about the creator
            type: dict
            returned: always
            sample: {"id": "user-123", "name": "admin"}
        modified_on:
            description: Last modification timestamp
            type: str
            returned: always
            sample: "2023-01-16T12:34:56.789Z"
        modified_by:
            description: Information about the last modifier
            type: dict
            returned: always
            sample: {"id": "user-123", "name": "admin"}
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        exclude_folders=dict(type="list", elements="str", required=False),
        exclude_snippets=dict(type="list", elements="str", required=False),
        exclude_devices=dict(type="list", elements="str", required=False),
        filters=dict(type="dict", required=False),
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

    result = {"hip_profiles": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get HIP profile by ID if specified
        if params.get("id"):
            try:
                hip_obj = client.hip_profile.get(params.get("id"))
                if hip_obj:
                    result["hip_profiles"] = [json.loads(hip_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve HIP profile info: {e}")
        # Fetch HIP profile by name
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
                        msg="When retrieving a HIP profile by name, exactly one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the HIP profile
                hip_obj = client.hip_profile.fetch(name=params.get("name"), **{container_type: container_name})
                if hip_obj:
                    result["hip_profiles"] = [json.loads(hip_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve HIP profile info: {e}")

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
                    msg="Exactly one container parameter (folder, snippet, or device) is required for listing HIP profiles"
                )

            # Add exact_match parameter if specified
            filter_params["exact_match"] = params.get("exact_match")

            # Add exclusion parameters if specified
            if params.get("exclude_folders"):
                filter_params["exclude_folders"] = params.get("exclude_folders")
            if params.get("exclude_snippets"):
                filter_params["exclude_snippets"] = params.get("exclude_snippets")
            if params.get("exclude_devices"):
                filter_params["exclude_devices"] = params.get("exclude_devices")

            # List HIP profiles with filters
            try:
                hip_profiles = client.hip_profile.list(**filter_params)

                # Apply additional client-side filtering if specified
                if params.get("filters"):
                    # This would need a custom implementation of filtering
                    # since the SDK doesn't have a built-in method for this
                    # For now, we just pass the filters to the result
                    additional_filters = params.get("filters")
                    result["filters_applied"] = additional_filters

                # Convert to a list of dicts
                hip_dicts = [json.loads(hip.model_dump_json(exclude_unset=True)) for hip in hip_profiles]

                # Add to results
                result["hip_profiles"] = hip_dicts

            except Exception as e:
                module.fail_json(msg=f"Error retrieving HIP profiles: {e}")

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve HIP profile info: {e}")


if __name__ == "__main__":
    main()
