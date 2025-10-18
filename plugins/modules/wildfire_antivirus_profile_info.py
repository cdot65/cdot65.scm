#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import Scm as ScmClient
from scm.exceptions import APIError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: wildfire_antivirus_profile_info
short_description: Retrieve WildFire Antivirus profiles from Strata Cloud Manager (SCM)
description:
    - Retrieve WildFire Antivirus security profiles from Strata Cloud Manager using pan-scm-sdk.
    - Allows lookup by name or retrieval of all profiles within a container.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the WildFire Antivirus profile to retrieve.
            - If not provided, all profiles in the specified container will be returned.
        type: str
        required: false
    folder:
        description:
            - The folder in which to search for the resource.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to search for the resource.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to search for the resource.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the WildFire Antivirus profile (UUID).
            - If provided, lookup will be performed by ID.
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
notes:
    - Check mode is supported.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided.
"""

EXAMPLES = r"""
- name: Get all WildFire Antivirus profiles in a folder
  cdot65.scm.wildfire_antivirus_profile_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: all_profiles

- name: Get a specific WildFire Antivirus profile by name
  cdot65.scm.wildfire_antivirus_profile_info:
    name: "Example-Basic-WildFire"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: profile_info

- name: Get a specific WildFire Antivirus profile by ID
  cdot65.scm.wildfire_antivirus_profile_info:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"
  register: profile_by_id
"""

RETURN = r"""
wildfire_antivirus_profiles:
    description: List of WildFire Antivirus profiles retrieved.
    returned: always
    type: list
    elements: dict
    sample:
        - id: "123e4567-e89b-12d3-a456-426655440000"
          name: "Example-Basic-WildFire"
          description: "Basic WildFire antivirus profile"
          folder: "Texas"
          packet_capture: false
          rules:
            - name: "rule1"
              direction: "both"
              analysis: "public-cloud"
              application:
                - "any"
              file_type:
                - "any"
"""


def main():
    """Main module execution."""
    module_args = dict(
        name=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
    )

    result = {
        "changed": False,
        "wildfire_antivirus_profiles": [],
    }

    # Get module parameters
    params = module.params
    scm_access_token = params["scm_access_token"]
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"

    # Initialize the SCM client with bearer token
    try:
        client = ScmClient(access_token=scm_access_token, api_base_url=api_url)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {e!s}")

    # Determine container type and name
    container_type = None
    container_name = None
    for ctype in ["folder", "snippet", "device"]:
        if params.get(ctype):
            container_type = ctype
            container_name = params[ctype]
            break

    # Get profile ID and name if provided
    profile_id = params.get("id")
    profile_name = params.get("name")

    try:
        if profile_id:
            # Lookup by ID
            try:
                profile = client.wildfire_antivirus_profile.fetch(profile_id)
                result["wildfire_antivirus_profiles"] = [json.loads(profile.model_dump_json())]
            except ObjectNotPresentError:
                result["wildfire_antivirus_profiles"] = []
        elif profile_name and container_type:
            # Lookup by name and container
            try:
                profile = client.wildfire_antivirus_profile.fetch(name=profile_name, **{container_type: container_name})
                result["wildfire_antivirus_profiles"] = [json.loads(profile.model_dump_json())]
            except ObjectNotPresentError:
                result["wildfire_antivirus_profiles"] = []
        elif container_type:
            # List all profiles in the container
            profiles = client.wildfire_antivirus_profile.list(**{container_type: container_name})
            result["wildfire_antivirus_profiles"] = [json.loads(p.model_dump_json()) for p in profiles]
        else:
            module.fail_json(msg="One of 'id', 'name' (with container), or a container type must be provided")

    except APIError as e:
        module.fail_json(msg=f"Failed to retrieve WildFire Antivirus profiles: {e!s}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
