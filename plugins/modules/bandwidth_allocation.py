#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: bandwidth_allocation
short_description: Manage bandwidth allocations in Strata Cloud Manager
description:
  - Manages bandwidth allocation objects for SD-WAN QoS in SCM.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  name:
    description: Name of the aggregated bandwidth region
    required: true
    type: str
  allocated_bandwidth:
    description: Bandwidth to allocate in Mbps
    required: false
    type: float
  spn_name_list:
    description: List of SPN names for this region
    required: false
    type: list
    elements: str
  qos:
    description: QoS configuration
    required: false
    type: dict
    suboptions:
      enabled:
        description: Enable QoS
        type: bool
      customized:
        description: Use customized QoS
        type: bool
      profile:
        description: QoS profile name
        type: str
      guaranteed_ratio:
        description: Guaranteed ratio
        type: float
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
  state:
    description: Desired state
    required: false
    type: str
    choices: [present, absent]
    default: present
"""

EXAMPLES = r"""
- name: Create bandwidth allocation
  cdot65.scm.bandwidth_allocation:
    name: "region-us-east"
    allocated_bandwidth: 1000.0
    spn_name_list:
      - "spn-east-1"
    scm_access_token: "{{ scm_access_token }}"
    state: present
"""

RETURN = r"""
changed:
  description: Whether changed
  returned: always
  type: bool
allocation:
  description: Bandwidth allocation details
  returned: when present
  type: dict
msg:
  description: Status message
  returned: always
  type: str
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
        name=dict(type="str", required=True),
        allocated_bandwidth=dict(type="float", required=False),
        spn_name_list=dict(type="list", elements="str", required=False),
        qos=dict(type="dict", required=False),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk required")

    params = module.params
    name = params["name"]
    state = params["state"]

    try:
        client = ScmClient(
            api_base_url=params.get("api_url") or "https://api.strata.paloaltonetworks.com",
            access_token=params["scm_access_token"],
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize client: {str(e)}")

    result = {"changed": False, "msg": ""}

    try:
        if state == "absent":
            if params.get("spn_name_list"):
                spn_str = ",".join(params["spn_name_list"])
                try:
                    client.bandwidth_allocation.delete(name, spn_str)
                    result["changed"] = True
                    result["msg"] = f"Bandwidth allocation '{name}' deleted"
                except (ObjectNotPresentError, APIError):
                    result["msg"] = f"Bandwidth allocation '{name}' not found"
            else:
                result["msg"] = "spn_name_list required for deletion"
            module.exit_json(**result)

        # Create or update
        if not params.get("allocated_bandwidth"):
            module.fail_json(msg="allocated_bandwidth required for state=present")

        data = {"name": name, "allocated_bandwidth": params["allocated_bandwidth"]}

        if params.get("spn_name_list"):
            data["spn_name_list"] = params["spn_name_list"]
        if params.get("qos"):
            data["qos"] = params["qos"]

        # Check if exists
        existing = None
        try:
            all_allocations = client.bandwidth_allocation.list()
            for alloc in all_allocations:
                if alloc.name == name:
                    existing = alloc
                    break
        except Exception as e:
            # If listing fails, proceed with create (will fail with better error)
            module.warn(f"Unable to check existing allocations: {str(e)}")

        if existing:
            # Update if changed
            needs_update = False
            if abs(existing.allocated_bandwidth - params["allocated_bandwidth"]) > 0.01:
                needs_update = True
            if params.get("spn_name_list") and set(params.get("spn_name_list", [])) != set(existing.spn_name_list or []):
                needs_update = True

            if needs_update:
                updated = client.bandwidth_allocation.update(data)
                result["changed"] = True
                result["msg"] = f"Bandwidth allocation '{name}' updated"
                result["allocation"] = updated.model_dump(exclude_unset=True)
            else:
                result["msg"] = f"Bandwidth allocation '{name}' unchanged"
                result["allocation"] = existing.model_dump(exclude_unset=True)
        else:
            # Create
            created = client.bandwidth_allocation.create(data)
            result["changed"] = True
            result["msg"] = f"Bandwidth allocation '{name}' created"
            result["allocation"] = created.model_dump(exclude_unset=True)

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
