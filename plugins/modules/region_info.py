#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError

DOCUMENTATION = r"""
---
module: region_info
short_description: Retrieve region object information from Strata Cloud Manager (SCM)
description:
    - Retrieve information about region objects from Strata Cloud Manager using pan-scm-sdk.
    - Supports filtering by geographic location and network addresses.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the region to retrieve.
            - If specified, only this region will be returned.
        type: str
        required: false
    geographic_location:
        description:
            - Filter regions by geographic location range.
            - Provide latitude and longitude ranges.
        type: dict
        required: false
        suboptions:
            latitude:
                description:
                    - Latitude range filter.
                type: dict
                required: false
                suboptions:
                    min:
                        description:
                            - Minimum latitude value.
                        type: float
                        required: true
                    max:
                        description:
                            - Maximum latitude value.
                        type: float
                        required: true
            longitude:
                description:
                    - Longitude range filter.
                type: dict
                required: false
                suboptions:
                    min:
                        description:
                            - Minimum longitude value.
                        type: float
                        required: true
                    max:
                        description:
                            - Maximum longitude value.
                        type: float
                        required: true
    addresses:
        description:
            - Filter regions by network addresses.
            - Returns regions containing any of the specified addresses.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Name of the folder containing the region objects.
            - Mutually exclusive with snippet and device.
        type: str
        required: false
    snippet:
        description:
            - Name of the snippet containing the region objects.
            - Mutually exclusive with folder and device.
        type: str
        required: false
    device:
        description:
            - Name of the device containing the region objects.
            - Mutually exclusive with folder and snippet.
        type: str
        required: false
    exact_match:
        description:
            - If true, only return objects whose container exactly matches.
        type: bool
        required: false
        default: false
    exclude_folders:
        description:
            - List of folder names to exclude from results.
        type: list
        elements: str
        required: false
    exclude_snippets:
        description:
            - List of snippet names to exclude from results.
        type: list
        elements: str
        required: false
    exclude_devices:
        description:
            - List of device names to exclude from results.
        type: list
        elements: str
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
    - Check mode is not applicable for information retrieval.
    - Exactly one of folder, snippet, or device must be specified.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
"""

EXAMPLES = r"""
- name: Get all regions in a folder
  cdot65.scm.region_info:
    folder: "Global"
  register: all_regions

- name: Get a specific region by name
  cdot65.scm.region_info:
    name: "us-west-region"
    folder: "Global"
  register: specific_region

- name: Filter regions by geographic location
  cdot65.scm.region_info:
    folder: "Global"
    geographic_location:
      latitude:
        min: 30
        max: 50
      longitude:
        min: -130
        max: -110
  register: west_coast_regions

- name: Filter regions by network addresses
  cdot65.scm.region_info:
    folder: "Global"
    addresses:
      - "10.0.0.0/8"
  register: regions_with_10_network

- name: Get regions excluding specific folders
  cdot65.scm.region_info:
    folder: "Global"
    exclude_folders:
      - "Test"
      - "Development"
  register: production_regions

- name: Combine multiple filters
  cdot65.scm.region_info:
    folder: "Global"
    geographic_location:
      latitude:
        min: 30
        max: 50
    addresses:
      - "10.0.0.0/8"
    exclude_folders:
      - "Test"
  register: filtered_regions
"""

RETURN = r"""
regions:
    description: List of region objects retrieved
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The region object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The region name
            type: str
            returned: always
            sample: "us-west-region"
        geo_location:
            description: The geographic location of the region
            type: dict
            returned: when configured
            sample:
                latitude: 37.7749
                longitude: -122.4194
        address:
            description: List of network addresses
            type: list
            returned: when configured
            sample: ["10.0.0.0/8", "192.168.1.0/24"]
        folder:
            description: The name of the folder containing the region
            type: str
            returned: when applicable
            sample: "Global"
        snippet:
            description: The name of the snippet containing the region
            type: str
            returned: when applicable
            sample: "EU Configs"
        device:
            description: The name of the device containing the region
            type: str
            returned: when applicable
            sample: "fw-01"
total:
    description: Total number of regions retrieved
    returned: always
    type: int
    sample: 5
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        geographic_location=dict(
            type="dict",
            required=False,
            options=dict(
                latitude=dict(
                    type="dict",
                    required=False,
                    options=dict(
                        min=dict(type="float", required=True),
                        max=dict(type="float", required=True),
                    ),
                ),
                longitude=dict(
                    type="dict",
                    required=False,
                    options=dict(
                        min=dict(type="float", required=True),
                        max=dict(type="float", required=True),
                    ),
                ),
            ),
        ),
        addresses=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        exclude_folders=dict(type="list", elements="str", required=False),
        exclude_snippets=dict(type="list", elements="str", required=False),
        exclude_devices=dict(type="list", elements="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        mutually_exclusive=[["folder", "snippet", "device"]],
        required_one_of=[["folder", "snippet", "device"]],
    )

    try:
        # Initialize SCM client
        client = ScmClient(access_token=module.params.get("scm_access_token"))

        # Build query parameters
        query_params = {}
        container_params = {}

        # Add container parameter
        for container in ["folder", "snippet", "device"]:
            if module.params.get(container):
                container_params[container] = module.params[container]

        # Add exact_match parameter
        query_params["exact_match"] = module.params.get("exact_match", False)

        # Add exclusion parameters if provided
        for exclusion in ["exclude_folders", "exclude_snippets", "exclude_devices"]:
            if module.params.get(exclusion):
                query_params[exclusion] = module.params[exclusion]

        # Add filtering parameters
        filters = {}

        # Add geographic location filter if provided (converted to geo_location)
        if module.params.get("geographic_location"):
            filters["geo_location"] = module.params["geographic_location"]

        # Add addresses filter if provided
        if module.params.get("addresses"):
            filters["addresses"] = module.params["addresses"]

        # Fetch regions
        if module.params.get("name"):
            # Get a specific region by name
            try:
                region = client.region.fetch(
                    name=module.params["name"], **container_params
                )
                regions = [region]
            except Exception:  # noqa
                regions = []
        else:
            # List all regions with filters
            regions = client.region.list(
                **container_params, **query_params, **filters
            )

        # Convert to serializable format
        serialized_regions = []
        for region in regions:
            serialized_regions.append(json.loads(region.model_dump_json(exclude_unset=True)))

        # Return results
        module.exit_json(changed=False, regions=serialized_regions, total=len(serialized_regions))

    except InvalidObjectError as e:
        module.fail_json(msg=f"Invalid object: {str(e)}")
    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:  # noqa
        module.fail_json(msg=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
