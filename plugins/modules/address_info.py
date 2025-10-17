#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: address_info
short_description: Get information about address objects in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about address objects in Strata Cloud Manager.
    - It can be used to get details about a specific address by ID or name, or to list all addresses.
    - Supports filtering by address properties like types, values, tags, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the address object to retrieve.
            - If specified, the module will return information about this specific address.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the address object to retrieve.
            - If specified, the module will search for addresses with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    types:
        description:
            - Filter addresses by type.
            - Supported types are 'netmask', 'range', 'wildcard', 'fqdn'.
        type: list
        elements: str
        required: false
        choices: ['netmask', 'range', 'wildcard', 'fqdn']
    values:
        description:
            - Filter addresses by value.
            - This is the actual content of the address (e.g., '192.168.1.0/24', 'example.com').
        type: list
        elements: str
        required: false
    tags:
        description:
            - Filter addresses by tags.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Filter addresses by folder name.
            - Required when retrieving addresses by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter addresses by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter addresses by device identifier.
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
    - Address objects must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all address objects
  cdot65.scm.address_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_addresses

- name: Get a specific address by ID
  cdot65.scm.address_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: address_details

- name: Get address with a specific name
  cdot65.scm.address_info:
    name: "web-server"
    folder: "Network-Objects"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_address

- name: Get IP address objects
  cdot65.scm.address_info:
    types: ["netmask"]
    scm_access_token: "{{ scm_access_token }}"
  register: ip_addresses

- name: Get addresses with specific tags
  cdot65.scm.address_info:
    tags: ["web", "external"]
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_addresses

- name: Get addresses in a specific folder
  cdot65.scm.address_info:
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_addresses

- name: Get addresses in a specific snippet
  cdot65.scm.address_info:
    snippet: "web-acl"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_addresses

- name: Get addresses for a specific device
  cdot65.scm.address_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_addresses
"""

RETURN = r"""
addresses:
    description: List of address objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The address object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The address object name
            type: str
            returned: always
            sample: "web-server"
        description:
            description: The address object description
            type: str
            returned: when applicable
            sample: "Web server IP address"
        ip_netmask:
            description: The IP address with CIDR notation
            type: str
            returned: when applicable
            sample: "192.168.1.100/32"
        ip_range:
            description: The IP address range
            type: str
            returned: when applicable
            sample: "10.0.0.100-10.0.0.200"
        ip_wildcard:
            description: The IP wildcard mask
            type: str
            returned: when applicable
            sample: "10.0.0.0/0.0.255.255"
        fqdn:
            description: The fully qualified domain name
            type: str
            returned: when applicable
            sample: "example.com"
        tag:
            description: Tags associated with the address object
            type: list
            returned: when applicable
            sample: ["web", "external"]
        folder:
            description: The folder containing the address object
            type: str
            returned: when applicable
            sample: "Network-Objects"
        snippet:
            description: The snippet containing the address object
            type: str
            returned: when applicable
            sample: "web-acl"
        device:
            description: The device containing the address object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        types=dict(type="list", elements="str", required=False, choices=["netmask", "range", "wildcard", "fqdn"]),
        values=dict(type="list", elements="str", required=False),
        tags=dict(type="list", elements="str", required=False),
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

    result = {"addresses": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get address by ID if specified
        if params.get("id"):
            try:
                address_obj = client.address.get(params.get("id"))
                if address_obj:
                    result["addresses"] = [json.loads(address_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve address info: {e}")
        # Fetch address by name
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
                        msg="When retrieving an address by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the address object
                address_obj = client.address.fetch(name=params.get("name"), **{container_type: container_name})
                if address_obj:
                    result["addresses"] = [json.loads(address_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve address info: {e}")

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
                    msg="At least one container parameter (folder, snippet, or device) is required for listing addresses"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List addresses with container filters
            addresses = client.address.list(**filter_params)

            # Apply additional client-side filtering
            # For types, values, and tags, we'll use the address._apply_filters method
            # that's already been called by the time we get the results
            if params.get("types") or params.get("values") or params.get("tags"):
                additional_filters = {}

                if params.get("types"):
                    additional_filters["types"] = params.get("types")

                if params.get("values"):
                    additional_filters["values"] = params.get("values")

                if params.get("tags"):
                    additional_filters["tags"] = params.get("tags")

                # Apply client-side filtering
                addresses = client.address._apply_filters(addresses, additional_filters)

            # Convert to a list of dicts
            address_dicts = [json.loads(a.model_dump_json(exclude_unset=True)) for a in addresses]

            # Add to results
            result["addresses"] = address_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve address info: {e}")


if __name__ == "__main__":
    main()
