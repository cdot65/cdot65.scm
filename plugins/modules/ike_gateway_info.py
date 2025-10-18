#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: ike_gateway_info
short_description: Retrieve information about IKE gateways in Strata Cloud Manager (SCM)
description:
    - Retrieve information about IKE gateways in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single gateway by ID or name, or listing multiple gateways.
    - IKE gateways are associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IKE gateway to retrieve.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IKE gateway (UUID).
            - Mutually exclusive with I(name).
        type: str
        required: false
    folder:
        description:
            - The folder in which to look for IKE gateways.
            - Exactly one of folder, snippet, or device must be provided.
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for IKE gateways.
        type: str
        required: false
    device:
        description:
            - The device in which to look for IKE gateways.
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token for authenticating API calls.
        type: str
        required: true
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
"""

EXAMPLES = r"""
---
- name: Get all IKE gateways in a folder
  cdot65.scm.ike_gateway_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_gateways

- name: Get IKE gateway by name
  cdot65.scm.ike_gateway_info:
    name: "ike-gateway-psk"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_gateway

- name: Get IKE gateway by ID
  cdot65.scm.ike_gateway_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: ike_gateway
"""

RETURN = r"""
ike_gateways:
    description: List of IKE gateways
    returned: when no id or name is specified
    type: list
    elements: dict
ike_gateway:
    description: Information about a specific IKE gateway
    returned: when id or name is specified
    type: dict
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
        mutually_exclusive=[["name", "id"], ["folder", "snippet", "device"]],
        supports_check_mode=True,
    )

    params = module.params
    if not any(params.get(c) for c in ["folder", "snippet", "device"]):
        module.fail_json(msg="One of the following is required: folder, snippet, device")

    result = {"changed": False}

    try:
        client = ScmClient(access_token=params.get("scm_access_token"))

        container_type = "folder" if params.get("folder") else "snippet" if params.get("snippet") else "device"
        container_value = params.get(container_type)

        if params.get("id") or params.get("name"):
            try:
                if params.get("id"):
                    gateway = client.ike_gateway.get(params["id"])
                else:
                    gateway = client.ike_gateway.fetch(name=params["name"], **{container_type: container_value})
                result["ike_gateway"] = json.loads(gateway.model_dump_json(exclude_unset=True))
            except ObjectNotPresentError:
                module.fail_json(msg=f"IKE gateway not found")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(msg=f"API error: {e}")
        else:
            try:
                gateways = client.ike_gateway.list(**{container_type: container_value})
                result["ike_gateways"] = [json.loads(g.model_dump_json(exclude_unset=True)) for g in gateways]
            except (APIError, InvalidObjectError) as e:
                module.fail_json(msg=f"API error: {e}")

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
