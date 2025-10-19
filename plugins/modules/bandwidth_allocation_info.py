#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: bandwidth_allocation_info
short_description: Retrieve bandwidth allocations from Strata Cloud Manager
description:
  - Retrieves bandwidth allocation information for SD-WAN QoS from SCM.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  name:
    description: Name of the aggregated bandwidth region to retrieve
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
- name: List all bandwidth allocations
  cdot65.scm.bandwidth_allocation_info:
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific bandwidth allocation
  cdot65.scm.bandwidth_allocation_info:
    name: "region-us-east"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
allocations:
  description: List of bandwidth allocations
  returned: always
  type: list
  elements: dict
  sample:
    - name: "region-us-east"
      allocated_bandwidth: 1000.0
      spn_name_list:
        - "spn-east-1"
      qos:
        enabled: true
        customized: false
        profile: "default"
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk required")

    params = module.params
    name = params.get("name")

    try:
        client = ScmClient(
            api_base_url=params.get("api_url") or "https://api.strata.paloaltonetworks.com",
            access_token=params["scm_access_token"],
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize client: {str(e)}")

    result = {"changed": False, "allocations": []}

    try:
        if name:
            # Get specific allocation
            all_allocations = client.bandwidth_allocation.list()
            for alloc in all_allocations:
                if alloc.name == name:
                    result["allocations"].append(alloc.model_dump(exclude_unset=True))
                    break
        else:
            # List all allocations
            allocations = client.bandwidth_allocation.list()
            for alloc in allocations:
                result["allocations"].append(alloc.model_dump(exclude_unset=True))

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
