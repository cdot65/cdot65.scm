#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: external_dynamic_list_info
short_description: Get information about external dynamic lists in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about external dynamic lists from Strata Cloud Manager (SCM).
    - It can be used to get details about a specific external dynamic list by ID or name, or to list all external dynamic lists.
    - Supports filtering by external dynamic list properties like list types, folder, snippet, or device.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the external dynamic list to retrieve.
            - If specified, the module will return information about this specific external dynamic list.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the external dynamic list to retrieve.
            - If specified, the module will search for external dynamic lists with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    list_types:
        description:
            - Filter external dynamic lists by type.
            - Supported types are 'predefined_ip', 'predefined_url', 'ip', 'domain', 'url', 'imsi', 'imei'.
        type: list
        elements: str
        required: false
        choices: ['predefined_ip', 'predefined_url', 'ip', 'domain', 'url', 'imsi', 'imei']
    folder:
        description:
            - Filter external dynamic lists by folder name.
            - Required when retrieving external dynamic lists by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter external dynamic lists by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter external dynamic lists by device identifier.
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
    filters:
        description:
            - Additional filters to apply when retrieving resources.
            - Used for client-side filtering and mapped directly to SDK filter capability.
        type: dict
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - External dynamic list objects must be associated with exactly one container (folder, snippet, or device).
    - External dynamic lists can be of various types (predefined_ip, predefined_url, ip, domain, url, imsi, imei).
"""

EXAMPLES = r"""
- name: Get all external dynamic lists
  cdot65.scm.external_dynamic_list_info:
    folder: "Security-Objects"  # container parameter is required
    scm_access_token: "{{ scm_access_token }}"
  register: all_edls

- name: Get a specific external dynamic list by ID
  cdot65.scm.external_dynamic_list_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: edl_details

- name: Get external dynamic list with a specific name
  cdot65.scm.external_dynamic_list_info:
    name: "malicious-domains"
    folder: "Security-Objects"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_edl

- name: Get IP type external dynamic lists
  cdot65.scm.external_dynamic_list_info:
    list_types: ["ip", "predefined_ip"]
    folder: "Security-Objects"  # container parameter is required
    scm_access_token: "{{ scm_access_token }}"
  register: ip_edls

- name: Get external dynamic lists in a specific folder
  cdot65.scm.external_dynamic_list_info:
    folder: "Security-Objects"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_edls

- name: Get external dynamic lists in a specific snippet
  cdot65.scm.external_dynamic_list_info:
    snippet: "threat-feeds"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_edls

- name: Get external dynamic lists for a specific device
  cdot65.scm.external_dynamic_list_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_edls

- name: Get domain and URL type external dynamic lists in a folder
  cdot65.scm.external_dynamic_list_info:
    folder: "Security-Objects"
    list_types: ["domain", "url"]
    scm_access_token: "{{ scm_access_token }}"
  register: domain_url_edls
"""

RETURN = r"""
external_dynamic_lists:
    description: List of external dynamic lists
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The external dynamic list ID
            type: str
            returned: always
            sample: "01234567-89ab-cdef-0123-456789abcdef"
        name:
            description: Name of the external dynamic list
            type: str
            returned: always
            sample: "malicious-domains"
        description:
            description: Description of the external dynamic list
            type: str
            returned: when present
            sample: "Known malicious domains from threat intelligence"
        folder:
            description: Folder containing the external dynamic list
            type: dict
            returned: when resource is in a folder
            sample: {"id": "folder-123", "name": "security-objects"}
        snippet:
            description: Snippet containing the external dynamic list
            type: dict
            returned: when resource is in a snippet
            sample: {"id": "snippet-123", "name": "security-snippet"}
        device:
            description: Device containing the external dynamic list
            type: dict
            returned: when resource is in a device
            sample: {"id": "device-123", "name": "fw-device"}
        type:
            description: Type of the external dynamic list
            type: dict
            returned: always
            sample: {"predefined_ip": {"url": "panw-blocklist"}}
        created_on:
            description: Creation timestamp
            type: str
            returned: always
            sample: "2023-01-15T12:34:56.789Z"
        created_by:
            description: Information about the creator
            type: dict
            returned: always
            sample: {"id": "user-123", "name": "admin"}
        modified_on:
            description: Last modification timestamp
            type: str
            returned: always
            sample: "2023-01-16T12:34:56.789Z"
        modified_by:
            description: Information about the last modifier
            type: dict
            returned: always
            sample: {"id": "user-123", "name": "admin"}
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        list_types=dict(
            type="list",
            elements="str",
            required=False,
            choices=["predefined_ip", "predefined_url", "ip", "domain", "url", "imsi", "imei"],
        ),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        filters=dict(type="dict", required=False),
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

    result = {"external_dynamic_lists": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get external dynamic list by ID if specified
        if params.get("id"):
            try:
                edl_obj = client.external_dynamic_list.get(params.get("id"))
                if edl_obj:
                    result["external_dynamic_lists"] = [json.loads(edl_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve external dynamic list info: {e}")
        # Fetch external dynamic list by name
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
                        msg="When retrieving an external dynamic list by name, exactly one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the external dynamic list object
                edl_obj = client.external_dynamic_list.fetch(name=params.get("name"), **{container_type: container_name})
                if edl_obj:
                    result["external_dynamic_lists"] = [json.loads(edl_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve external dynamic list info: {e}")

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
                    msg="Exactly one container parameter (folder, snippet, or device) is required for listing external dynamic lists"
                )

            # Add exact_match parameter if specified
            filter_params["exact_match"] = params.get("exact_match")

            # List external dynamic lists with container filters
            try:
                edls = client.external_dynamic_list.list(**filter_params)

                # Apply list_types filtering if specified
                if params.get("list_types"):
                    filtered_edls = []
                    list_types = params.get("list_types")

                    for edl in edls:
                        # Check if the EDL's type matches any of the specified types
                        if hasattr(edl, "type") and edl.type and hasattr(edl.type, "model_dump_json"):
                            # Safer way to check type existence - convert to dict first
                            edl_type_dict = json.loads(edl.type.model_dump_json(exclude_unset=True))
                            if any(list_type in edl_type_dict for list_type in list_types):
                                filtered_edls.append(edl)
                    edls = filtered_edls

                # Apply additional client-side filtering if specified
                if params.get("filters"):
                    additional_filters = {"filters": params.get("filters")}
                    edls = client.external_dynamic_list._apply_filters(edls, additional_filters)

                # Convert to a list of dicts
                edl_dicts = [json.loads(edl.model_dump_json(exclude_unset=True)) for edl in edls]

                # Add to results
                result["external_dynamic_lists"] = edl_dicts

            except Exception as e:
                module.fail_json(msg=f"Error retrieving external dynamic lists: {e}")

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve external dynamic list info: {e}")


if __name__ == "__main__":
    main()
