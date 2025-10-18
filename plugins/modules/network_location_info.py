#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: network_location_info
short_description: Retrieve network location information from Strata Cloud Manager
description:
  - Retrieves network location information from SCM.
  - Network locations are read-only resources representing geographic locations.
  - Useful for SD-WAN and policy-based routing configurations.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  value:
    description: Filter by location value (e.g., 'us-west-1')
    required: false
    type: str
  display:
    description: Filter by display name
    required: false
    type: str
  region:
    description: Filter by region code
    required: false
    type: str
  continent:
    description: Filter by continent name
    required: false
    type: str
  aggregate_region:
    description: Filter by aggregate region identifier
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
notes:
  - Network locations are read-only resources (no create/update/delete operations).
  - These locations are used for SD-WAN and policy-based routing configurations.
"""

EXAMPLES = r"""
- name: List all network locations
  cdot65.scm.network_location_info:
    scm_access_token: "{{ scm_access_token }}"

- name: Get locations in North America
  cdot65.scm.network_location_info:
    continent: "North America"
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific location by value
  cdot65.scm.network_location_info:
    value: "us-west-1"
    scm_access_token: "{{ scm_access_token }}"

- name: Get locations in a specific region
  cdot65.scm.network_location_info:
    region: "us-west-1"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
locations:
  description: List of network locations
  returned: always
  type: list
  elements: dict
  sample:
    - value: "us-west-1"
      display: "US West"
      continent: "North America"
      latitude: 37.38314
      longitude: -121.98306
      region: "us-west-1"
      aggregate_region: "us-southwest"
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
        value=dict(type="str", required=False),
        display=dict(type="str", required=False),
        region=dict(type="str", required=False),
        continent=dict(type="str", required=False),
        aggregate_region=dict(type="str", required=False),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

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

    result = {"changed": False, "locations": []}

    # Build filter dict from provided parameters
    filters = {}
    for filter_key in ["value", "display", "region", "continent", "aggregate_region"]:
        if params.get(filter_key):
            filters[filter_key] = params[filter_key]

    try:
        # List locations with filters
        locations = client.network_location.list(**filters)
        for loc in locations:
            result["locations"].append(loc.model_dump(exclude_unset=True))

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
