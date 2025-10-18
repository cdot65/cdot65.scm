#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: url_categories_info
short_description: Get information about custom URL categories in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about custom URL categories in Strata Cloud Manager.
    - It can be used to get details about a specific URL category by ID or name, or to list all categories.
    - Supports filtering by container (folder, snippet, device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the URL category to retrieve.
            - If specified, the module will return information about this specific category.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the URL category to retrieve.
            - If specified, the module will search for categories with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    folder:
        description:
            - Filter URL categories by folder name.
            - Required when retrieving categories by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter URL categories by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter URL categories by device identifier.
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
    - URL categories must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all URL categories in a folder
  cdot65.scm.url_categories_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: all_url_categories

- name: Get a specific URL category by ID
  cdot65.scm.url_categories_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: url_category_details

- name: Get URL category with a specific name
  cdot65.scm.url_categories_info:
    name: "blocked-sites"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: named_category

- name: Get URL categories in a specific snippet
  cdot65.scm.url_categories_info:
    snippet: "Security-Policy"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_categories

- name: Get URL categories for a specific device
  cdot65.scm.url_categories_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_categories

- name: Display URL category names
  ansible.builtin.debug:
    msg: "{{ item.name }}: {{ item.list | length }} entries"
  loop: "{{ all_url_categories.url_categories }}"
  loop_control:
    label: "{{ item.name }}"
"""

RETURN = r"""
url_categories:
    description: List of URL category objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The URL category ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The URL category name
            type: str
            returned: always
            sample: "blocked-sites"
        description:
            description: The URL category description
            type: str
            returned: when applicable
            sample: "Sites to block"
        list:
            description: List of URLs or categories
            type: list
            returned: always
            sample: ["*.badsite.com", "malicious.example.com"]
        type:
            description: Type of URL category
            type: str
            returned: always
            sample: "URL List"
        folder:
            description: The folder containing the URL category
            type: str
            returned: when applicable
            sample: "Texas"
        snippet:
            description: The snippet containing the URL category
            type: str
            returned: when applicable
            sample: "Security-Policy"
        device:
            description: The device containing the URL category
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
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

    result = {"url_categories": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get URL category by ID if specified
        if params.get("id"):
            try:
                url_category_obj = client.url_categories.get(params.get("id"))
                if url_category_obj:
                    result["url_categories"] = [json.loads(url_category_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve URL category info: {e}")
        # Fetch URL category by name
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
                        msg="When retrieving a URL category by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the URL category object
                url_category_obj = client.url_categories.fetch(name=params.get("name"), **{container_type: container_name})
                if url_category_obj:
                    result["url_categories"] = [json.loads(url_category_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve URL category info: {e}")

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
                    msg="At least one container parameter (folder, snippet, or device) is required for listing URL categories"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List URL categories with container filters
            url_categories = client.url_categories.list(**filter_params)

            # Convert to a list of dicts
            url_category_dicts = [json.loads(cat.model_dump_json(exclude_unset=True)) for cat in url_categories]

            # Add to results
            result["url_categories"] = url_category_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve URL category info: {e}")


if __name__ == "__main__":
    main()
