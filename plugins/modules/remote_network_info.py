#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: remote_network_info
short_description: Retrieve remote network information from Strata Cloud Manager
description:
  - Retrieves Prisma Access remote network configurations.
  - List all remote networks or get a specific one by ID or name.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  id:
    description: UUID of the remote network to retrieve
    required: false
    type: str
  name:
    description: Name of the remote network to retrieve
    required: false
    type: str
  folder:
    description: Filter by folder
    required: false
    type: str
  snippet:
    description: Filter by snippet
    required: false
    type: str
  device:
    description: Filter by device
    required: false
    type: str
  api_url:
    description: SCM API base URL
    required: false
    type: str
    default: "https://api.strata.paloaltonetworks.com"
  scm_access_token:
    description: OAuth2 access token
    required: true
    type: str
    no_log: true
"""

EXAMPLES = r"""
- name: List all remote networks in a folder
  cdot65.scm.remote_network_info:
    folder: "Remote Networks"
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific remote network by ID
  cdot65.scm.remote_network_info:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific remote network by name
  cdot65.scm.remote_network_info:
    name: "branch-office-1"
    folder: "Remote Networks"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
remote_networks:
  description: List of remote networks
  returned: always
  type: list
  elements: dict
  sample:
    - id: "123e4567-e89b-12d3-a456-426655440000"
      name: "branch-office-1"
      region: "us-east-1"
      license_type: "FWAAS-AGGREGATE"
      spn_name: "my-spn"
      subnets:
        - "10.1.0.0/24"
      ipsec_tunnel: "tunnel-1"
      folder: "Remote Networks"
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    module_args = dict(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["folder", "snippet", "device"]],
    )

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk required")

    params = module.params

    try:
        client = ScmClient(
            api_base_url=params.get("api_url") or "https://api.strata.paloaltonetworks.com",
            access_token=params["scm_access_token"],
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize client: {str(e)}")

    result = {"changed": False, "remote_networks": []}

    try:
        if params.get("id"):
            # Get by ID
            try:
                network = client.remote_network.get(params["id"])
                network_dict = network.model_dump(exclude_unset=True)
                network_dict["id"] = str(network_dict["id"])
                result["remote_networks"].append(network_dict)
            except ObjectNotPresentError:
                pass
        else:
            # Build filter dict
            filters = {}
            for container in ["folder", "snippet", "device"]:
                if params.get(container):
                    filters[container] = params[container]
                    break

            # List networks
            networks = client.remote_network.list(**filters)
            for net in networks:
                # Filter by name if specified
                if params.get("name") and net.name != params["name"]:
                    continue

                network_dict = net.model_dump(exclude_unset=True)
                network_dict["id"] = str(network_dict["id"])
                result["remote_networks"].append(network_dict)

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
