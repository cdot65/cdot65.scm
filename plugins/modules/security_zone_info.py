#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = r"""
---
module: security_zone_info
short_description: Retrieve security zone information from Strata Cloud Manager
description:
  - Retrieves information about security zone objects in Palo Alto Networks Strata Cloud Manager.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
requirements:
  - pan-scm-sdk>=0.3.44
options:
  name:
    description:
      - The name of a specific security zone to retrieve.
    required: false
    type: str
  folder:
    description:
      - The folder to search in.
    required: false
    type: str
  snippet:
    description:
      - The snippet to search in.
    required: false
    type: str
  device:
    description:
      - The device to search in.
    required: false
    type: str
  api_url:
    description:
      - The base URL for the Strata Cloud Manager API.
    required: false
    type: str
    default: "https://api.strata.paloaltonetworks.com"
  scm_access_token:
    description:
      - The OAuth2 access token for authenticating to the SCM API.
    required: true
    type: str
    no_log: true
"""

EXAMPLES = r"""
---
# Retrieve all security zones in a folder
- name: Get all zones in Texas folder
  cdot65.scm.security_zone_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: all_zones

# Retrieve a specific zone by name
- name: Get trust zone
  cdot65.scm.security_zone_info:
    name: "trust"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: trust_zone
"""

RETURN = r"""
zones:
  description: List of security zone objects
  returned: always
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    """Main execution path for the security_zone_info module."""
    module_args = dict(
        name=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        api_url=dict(type="str", required=False, default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[["folder", "snippet", "device"]],
        mutually_exclusive=[["folder", "snippet", "device"]],
    )

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk is required for this module. Install: pip install pan-scm-sdk")

    params = module.params
    zone_name = params.get("name")

    # Determine container
    container_type = None
    container_name = None
    for c in ["folder", "snippet", "device"]:
        if params.get(c):
            container_type = c
            container_name = params[c]
            break

    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"
    scm_access_token = params["scm_access_token"]

    try:
        client = ScmClient(api_base_url=api_url, access_token=scm_access_token)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {str(e)}")

    result = {"zones": []}
    lookup_params = {container_type: container_name}

    try:
        if zone_name:
            # Get specific zone
            try:
                zone = client.security_zone.fetch(name=zone_name, **lookup_params)
                zone_dict = zone.model_dump(exclude_unset=True)
                zone_dict["id"] = str(zone_dict["id"])
                result["zones"].append(zone_dict)
            except ObjectNotPresentError:
                module.warn(f"Security zone '{zone_name}' not found")
        else:
            # Get all zones
            zones = client.security_zone.list(**lookup_params)
            for zone in zones:
                zone_dict = zone.model_dump(exclude_unset=True)
                zone_dict["id"] = str(zone_dict["id"])
                result["zones"].append(zone_dict)

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
