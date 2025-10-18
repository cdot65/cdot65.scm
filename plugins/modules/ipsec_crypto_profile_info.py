#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: ipsec_crypto_profile_info
short_description: Retrieve information about IPsec crypto profiles in Strata Cloud Manager (SCM)
description:
    - Retrieve information about IPsec crypto profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single profile by ID or name, or listing multiple profiles.
    - IPsec crypto profiles are associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IPsec crypto profile to retrieve.
            - Used for exact match lookup.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IPsec crypto profile (UUID).
            - Used for exact match lookup.
            - Mutually exclusive with I(name).
        type: str
        required: false
    folder:
        description:
            - The folder in which to look for IPsec crypto profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for IPsec crypto profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to look for IPsec crypto profiles.
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
- name: Get all IPsec crypto profiles in a folder
  cdot65.scm.ipsec_crypto_profile_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ipsec_profiles

- name: Get IPsec crypto profile by ID
  cdot65.scm.ipsec_crypto_profile_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ipsec_profile

- name: Get IPsec crypto profile by name
  cdot65.scm.ipsec_crypto_profile_info:
    name: "ipsec-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ipsec_profile

- name: Display profile information
  debug:
    msg: "Profile {{ item.name }} uses {{ item.dh_group }} DH group"
  loop: "{{ ipsec_profiles.ipsec_crypto_profiles }}"
"""

RETURN = r"""
ipsec_crypto_profiles:
    description: List of IPsec crypto profiles when multiple profiles are retrieved
    returned: when no id or name is specified
    type: list
    elements: dict
    contains:
        id:
            description: The IPsec crypto profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IPsec crypto profile name
            type: str
            returned: always
            sample: "ipsec-crypto-default"
        dh_group:
            description: Diffie-Hellman group
            type: str
            returned: always
            sample: "group14"
        lifetime:
            description: IPsec SA lifetime configuration
            type: dict
            returned: always
            sample: {"hours": 1}
        lifesize:
            description: IPsec SA lifesize configuration
            type: dict
            returned: when configured
            sample: {"gb": 10}
        esp:
            description: ESP configuration
            type: dict
            returned: when configured
        ah:
            description: AH configuration
            type: dict
            returned: when configured
        folder:
            description: The folder containing the IPsec crypto profile
            type: str
            returned: when applicable
            sample: "Shared"
ipsec_crypto_profile:
    description: Information about a specific IPsec crypto profile
    returned: when id or name is specified and profile exists
    type: dict
    contains:
        id:
            description: The IPsec crypto profile ID
            type: str
            returned: always
        name:
            description: The IPsec crypto profile name
            type: str
            returned: always
        dh_group:
            description: Diffie-Hellman group
            type: str
            returned: always
        lifetime:
            description: IPsec SA lifetime configuration
            type: dict
            returned: always
        lifesize:
            description: IPsec SA lifesize configuration
            type: dict
            returned: when configured
        esp:
            description: ESP configuration
            type: dict
            returned: when configured
        ah:
            description: AH configuration
            type: dict
            returned: when configured
        folder:
            description: The folder containing the IPsec crypto profile
            type: str
            returned: when applicable
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

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["name", "id"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    params = module.params
    profile_name = params.get("name")
    profile_id = params.get("id")

    if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
        module.fail_json(msg="One of the following is required: folder, snippet, device")

    result = {"changed": False}

    try:
        client = ScmClient(access_token=params.get("scm_access_token"))

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

        if profile_id or profile_name:
            try:
                if profile_id:
                    profile = client.ipsec_crypto_profile.get(profile_id)
                elif profile_name:
                    profile = client.ipsec_crypto_profile.fetch(name=profile_name, **{container_type: container_value})

                profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))
                result["ipsec_crypto_profile"] = profile_dict
            except ObjectNotPresentError:
                if profile_id:
                    module.fail_json(msg=f"IPsec crypto profile with ID '{profile_id}' not found")
                else:
                    module.fail_json(msg=f"IPsec crypto profile with name '{profile_name}' not found in the specified container")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )
        else:
            try:
                filter_params = {container_type: container_value}
                profiles = client.ipsec_crypto_profile.list(**filter_params)

                profiles_list = []
                for profile in profiles:
                    profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))
                    profiles_list.append(profile_dict)

                result["ipsec_crypto_profiles"] = profiles_list
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
