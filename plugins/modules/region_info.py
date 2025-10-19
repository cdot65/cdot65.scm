#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: region_info
short_description: Get information about region objects in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about region objects in Strata Cloud Manager.
    - It can be used to get details about a specific region by ID or name, or to list all regions.
    - Supports filtering by address associations, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the region object to retrieve.
            - If specified, the module will return information about this specific region.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the region object to retrieve.
            - If specified, the module will search for regions with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    address:
        description:
            - Filter regions by associated addresses.
            - Returns regions that contain any of the specified addresses.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter regions by folder name.
            - Required when retrieving regions by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter regions by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter regions by device identifier.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: False
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Region objects must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all region objects in a folder
  cdot65.scm.region_info:
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: all_regions

- name: Get a specific region by ID
  cdot65.scm.region_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: region_details

- name: Get region with a specific name
  cdot65.scm.region_info:
    name: "North-America-East"
    folder: "Network-Objects"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_region

- name: Get regions associated with specific addresses
  cdot65.scm.region_info:
    address:
      - "london-office"
      - "paris-office"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_regions

- name: Get regions in a specific snippet
  cdot65.scm.region_info:
    snippet: "global-regions"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_regions

- name: Get regions for a specific device
  cdot65.scm.region_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_regions
"""

RETURN = r"""
regions:
    description: List of region objects
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
            description: The region object name
            type: str
            returned: always
            sample: "North-America-East"
        geo_location:
            description: Geographic location of the region
            type: dict
            returned: when applicable
            contains:
                latitude:
                    description: Latitudinal position
                    type: float
                    sample: 40.7128
                longitude:
                    description: Longitudinal position
                    type: float
                    sample: -74.0060
        address:
            description: List of addresses associated with the region
            type: list
            returned: when applicable
            sample: ["london-office", "paris-office"]
        folder:
            description: The folder containing the region object
            type: str
            returned: when applicable
            sample: "Network-Objects"
        snippet:
            description: The snippet containing the region object
            type: str
            returned: when applicable
            sample: "global-regions"
        device:
            description: The device containing the region object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        address=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"regions": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get region by ID if specified
        if params.get("id"):
            try:
                region_obj = client.region.get(params.get("id"))
                if region_obj:
                    result["regions"] = [json.loads(region_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve region info: {e}")
        # Fetch region by name
        elif params.get("name"):
            try:
                # Handle different container types (folder, snippet, device)
                container_type = None
                container_name = None

                if params.get("folder"):
                    container_type = "folder"
                    container_name = params.get("folder")
                elif params.get("snippet"):
                    container_type = "snippet"
                    container_name = params.get("snippet")
                elif params.get("device"):
                    container_type = "device"
                    container_name = params.get("device")

                # We need a container for the fetch operation
                if not container_type or not container_name:
                    module.fail_json(
                        msg="When retrieving a region by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the region object
                region_obj = client.region.fetch(name=params.get("name"), **{container_type: container_name})
                if region_obj:
                    result["regions"] = [json.loads(region_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve region info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet, device) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                filter_params["device"] = params.get("device")
            else:
                module.fail_json(
                    msg="At least one container parameter (folder, snippet, or device) is required for listing regions"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List regions with container filters
            regions = client.region.list(**filter_params)

            # Apply additional client-side filtering for address
            if params.get("address"):
                filter_addresses = set(params.get("address"))
                filtered_regions = []

                for region in regions:
                    # Check if region has any of the specified addresses
                    if region.address:
                        region_addresses = set(region.address)
                        if filter_addresses & region_addresses:  # If there's any intersection
                            filtered_regions.append(region)

                regions = filtered_regions

            # Convert to a list of dicts
            region_dicts = [json.loads(r.model_dump_json(exclude_unset=True)) for r in regions]

            # Add to results
            result["regions"] = region_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve region info: {e}")


if __name__ == "__main__":
    main()
