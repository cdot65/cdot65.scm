#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import Scm as ScmClient
from scm.exceptions import APIError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: dns_security_profile_info
short_description: Retrieve DNS Security profiles from SCM
description:
    - Retrieve DNS Security profiles from Strata Cloud Manager.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the DNS Security profile to retrieve.
        type: str
        required: false
    folder:
        description:
            - The folder to search.
        type: str
        required: false
    snippet:
        description:
            - The snippet to search.
        type: str
        required: false
    device:
        description:
            - The device to search.
        type: str
        required: false
    id:
        description:
            - UUID of the profile.
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token.
        type: str
        required: true
    api_url:
        description:
            - SCM API URL.
        type: str
        required: false
"""

EXAMPLES = r"""
- name: Get all DNS Security profiles
  cdot65.scm.dns_security_profile_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
dns_security_profiles:
    description: List of DNS Security profiles.
    returned: always
    type: list
"""


def main():
    """Main module execution."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False),
            folder=dict(type="str", required=False),
            snippet=dict(type="str", required=False),
            device=dict(type="str", required=False),
            id=dict(type="str", required=False),
            scm_access_token=dict(type="str", required=True, no_log=True),
            api_url=dict(type="str", required=False),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["folder", "snippet", "device"]],
    )

    result = {"changed": False, "dns_security_profiles": []}
    params = module.params
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"

    try:
        client = ScmClient(access_token=params["scm_access_token"], api_base_url=api_url)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {e!s}")

    container_type = next((ct for ct in ["folder", "snippet", "device"] if params.get(ct)), None)
    container_name = params.get(container_type) if container_type else None

    try:
        if params.get("id"):
            try:
                profile = client.dns_security_profile.fetch(params["id"])
                result["dns_security_profiles"] = [json.loads(profile.model_dump_json())]
            except ObjectNotPresentError:
                pass
        elif params.get("name") and container_type:
            try:
                profile = client.dns_security_profile.fetch(name=params["name"], **{container_type: container_name})
                result["dns_security_profiles"] = [json.loads(profile.model_dump_json())]
            except ObjectNotPresentError:
                pass
        elif container_type:
            profiles = client.dns_security_profile.list(**{container_type: container_name})
            result["dns_security_profiles"] = [json.loads(p.model_dump_json()) for p in profiles]
        else:
            module.fail_json(msg="Provide id, name with container, or container")
    except APIError as e:
        module.fail_json(msg=f"Failed to retrieve profiles: {e!s}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
