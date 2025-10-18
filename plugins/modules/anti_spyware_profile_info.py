#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: anti_spyware_profile_info
short_description: Get information about Anti-Spyware profiles in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about Anti-Spyware security profiles in Strata Cloud Manager.
    - It can be used to get details about a specific profile by ID or name, or to list all profiles.
    - Supports filtering by container (folder, snippet, device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the Anti-Spyware profile to retrieve.
            - If specified, the module will return information about this specific profile.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the Anti-Spyware profile to retrieve.
            - If specified, the module will search for profiles with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    folder:
        description:
            - Filter profiles by folder name.
            - Required when retrieving profiles by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter profiles by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter profiles by device identifier.
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
    - Anti-Spyware profiles must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all Anti-Spyware profiles in a folder
  cdot65.scm.anti_spyware_profile_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: all_profiles

- name: Get a specific Anti-Spyware profile by ID
  cdot65.scm.anti_spyware_profile_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: profile_details

- name: Get Anti-Spyware profile with a specific name
  cdot65.scm.anti_spyware_profile_info:
    name: "Strict-Anti-Spyware"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: named_profile

- name: Get Anti-Spyware profiles in a specific snippet
  cdot65.scm.anti_spyware_profile_info:
    snippet: "Security-Profiles"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_profiles

- name: Get Anti-Spyware profiles for a specific device
  cdot65.scm.anti_spyware_profile_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_profiles

- name: Display profile names and rule counts
  ansible.builtin.debug:
    msg: "{{ item.name }}: {{ item.rules | length }} rules"
  loop: "{{ all_profiles.anti_spyware_profiles }}"
  loop_control:
    label: "{{ item.name }}"
"""

RETURN = r"""
anti_spyware_profiles:
    description: List of Anti-Spyware profile objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The profile ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The profile name
            type: str
            returned: always
            sample: "Strict-Anti-Spyware"
        description:
            description: The profile description
            type: str
            returned: when applicable
            sample: "Strict anti-spyware protection profile"
        rules:
            description: List of anti-spyware rules
            type: list
            returned: always
            sample: [{"name": "block-critical-high-medium", "severity": ["critical", "high", "medium"]}]
        cloud_inline_analysis:
            description: Cloud inline analysis enabled
            type: bool
            returned: when applicable
            sample: false
        folder:
            description: The folder containing the profile
            type: str
            returned: when applicable
            sample: "Texas"
        snippet:
            description: The snippet containing the profile
            type: str
            returned: when applicable
            sample: "Security-Profiles"
        device:
            description: The device containing the profile
            type: str
            returned: when applicable
            sample: "firewall-01"
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

    result = {"anti_spyware_profiles": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get profile by ID if specified
        if params.get("id"):
            try:
                profile_obj = client.anti_spyware_profile.get(params.get("id"))
                if profile_obj:
                    result["anti_spyware_profiles"] = [json.loads(profile_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve Anti-Spyware profile info: {e}")
        # Fetch profile by name
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
                        msg="When retrieving an Anti-Spyware profile by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the profile object
                profile_obj = client.anti_spyware_profile.fetch(name=params.get("name"), **{container_type: container_name})
                if profile_obj:
                    result["anti_spyware_profiles"] = [json.loads(profile_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve Anti-Spyware profile info: {e}")

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
                    msg="At least one container parameter (folder, snippet, or device) is required for listing Anti-Spyware profiles"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List profiles with container filters
            profiles = client.anti_spyware_profile.list(**filter_params)

            # Convert to a list of dicts
            profile_dicts = [json.loads(p.model_dump_json(exclude_unset=True)) for p in profiles]

            # Add to results
            result["anti_spyware_profiles"] = profile_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve Anti-Spyware profile info: {e}")


if __name__ == "__main__":
    main()
