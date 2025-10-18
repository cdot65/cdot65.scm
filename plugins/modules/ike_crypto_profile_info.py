#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: ike_crypto_profile_info
short_description: Retrieve information about IKE crypto profiles in Strata Cloud Manager (SCM)
description:
    - Retrieve information about IKE crypto profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single profile by ID or name, or listing multiple profiles with optional filtering.
    - IKE crypto profiles are associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IKE crypto profile to retrieve.
            - Used for exact match lookup.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IKE crypto profile (UUID).
            - Used for exact match lookup.
            - Mutually exclusive with I(name).
        type: str
        required: false
    folder:
        description:
            - The folder in which to look for IKE crypto profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for IKE crypto profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to look for IKE crypto profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(snippet).
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
notes:
    - When retrieving a single profile, either name or id must be provided.
    - When retrieving multiple profiles, all profiles in the specified container will be returned.
    - Exactly one container parameter (folder, snippet, or device) must be provided.
    - Check mode is supported but makes no changes.
"""

EXAMPLES = r"""
---
- name: Get all IKE crypto profiles in a folder
  cdot65.scm.ike_crypto_profile_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_profiles

- name: Get IKE crypto profile by ID
  cdot65.scm.ike_crypto_profile_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_profile

- name: Get IKE crypto profile by name
  cdot65.scm.ike_crypto_profile_info:
    name: "ike-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_profile

- name: Get all IKE crypto profiles in a snippet
  cdot65.scm.ike_crypto_profile_info:
    snippet: "VPN-Config"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_profiles

- name: Display profile information
  debug:
    msg: "Profile {{ item.name }} uses {{ item.encryption | join(', ') }} encryption"
  loop: "{{ ike_profiles.ike_crypto_profiles }}"
"""

RETURN = r"""
ike_crypto_profiles:
    description: List of IKE crypto profiles when multiple profiles are retrieved
    returned: when no id or name is specified
    type: list
    elements: dict
    contains:
        id:
            description: The IKE crypto profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IKE crypto profile name
            type: str
            returned: always
            sample: "ike-crypto-default"
        hash:
            description: List of hash algorithms
            type: list
            returned: always
            sample: ["sha256", "sha384"]
        encryption:
            description: List of encryption algorithms
            type: list
            returned: always
            sample: ["aes-256-cbc", "aes-128-cbc"]
        dh_group:
            description: List of Diffie-Hellman groups
            type: list
            returned: always
            sample: ["group14", "group19"]
        lifetime:
            description: IKE SA lifetime configuration
            type: dict
            returned: when configured
            sample: {"hours": 8}
        authentication_multiple:
            description: IKEv2 SA reauthentication interval
            type: int
            returned: always
            sample: 0
        folder:
            description: The folder containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "VPN-Config"
        device:
            description: The device containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "firewall-01"
ike_crypto_profile:
    description: Information about a specific IKE crypto profile
    returned: when id or name is specified and profile exists
    type: dict
    contains:
        id:
            description: The IKE crypto profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IKE crypto profile name
            type: str
            returned: always
            sample: "ike-crypto-default"
        hash:
            description: List of hash algorithms
            type: list
            returned: always
            sample: ["sha256", "sha384"]
        encryption:
            description: List of encryption algorithms
            type: list
            returned: always
            sample: ["aes-256-cbc", "aes-128-cbc"]
        dh_group:
            description: List of Diffie-Hellman groups
            type: list
            returned: always
            sample: ["group14", "group19"]
        lifetime:
            description: IKE SA lifetime configuration
            type: dict
            returned: when configured
            sample: {"hours": 8}
        authentication_multiple:
            description: IKEv2 SA reauthentication interval
            type: int
            returned: always
            sample: 0
        folder:
            description: The folder containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "VPN-Config"
        device:
            description: The device containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["name", "id"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params
    profile_name = params.get("name")
    profile_id = params.get("id")

    # Custom validation for container parameters
    if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
        module.fail_json(msg="One of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Determine the container type and value
        container_type = None
        container_value = None

        if params.get("folder"):
            container_type = "folder"
            container_value = params.get("folder")
        elif params.get("snippet"):
            container_type = "snippet"
            container_value = params.get("snippet")
        elif params.get("device"):
            container_type = "device"
            container_value = params.get("device")

        # Retrieve a specific profile by ID or name
        if profile_id or profile_name:
            try:
                if profile_id:
                    # Fetch by ID
                    profile = client.ike_crypto_profile.get(profile_id)
                elif profile_name:
                    # Fetch by name within the specified container
                    profile = client.ike_crypto_profile.fetch(name=profile_name, **{container_type: container_value})

                # Get the profile data and convert it to a dictionary
                profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))

                # Return the profile information
                result["ike_crypto_profile"] = profile_dict
            except ObjectNotPresentError:
                if profile_id:
                    module.fail_json(msg=f"IKE crypto profile with ID '{profile_id}' not found")
                else:
                    module.fail_json(msg=f"IKE crypto profile with name '{profile_name}' not found in the specified container")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )
        else:
            # Retrieve multiple profiles
            try:
                # Build filter parameters
                filter_params = {container_type: container_value}

                # Fetch all profiles in the container
                profiles = client.ike_crypto_profile.list(**filter_params)

                # Convert to list of dictionaries
                profiles_list = []
                for profile in profiles:
                    profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))
                    profiles_list.append(profile_dict)

                result["ike_crypto_profiles"] = profiles_list
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )

        # Return results
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
