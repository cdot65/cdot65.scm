#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: application_filter_info
short_description: Get information about application filter objects in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about application filter objects in Strata Cloud Manager.
    - It can be used to get details about a specific application filter by ID or name, or to list all application filters.
    - Supports filtering by application filter properties like category, subcategory, technology, risk, and other attributes.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the application filter object to retrieve.
            - If specified, the module will return information about this specific application filter.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the application filter object to retrieve.
            - If specified, the module will search for application filters with this name.
            - When using name, one of the container parameters (folder, snippet) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    category:
        description:
            - Filter application filters by category.
        type: list
        elements: str
        required: false
    subcategory:
        description:
            - Filter application filters by subcategory.
        type: list
        elements: str
        required: false
    technology:
        description:
            - Filter application filters by technology.
        type: list
        elements: str
        required: false
    risk:
        description:
            - Filter application filters by risk level.
        type: list
        elements: int
        required: false
    folder:
        description:
            - Filter application filters by folder name.
            - Required when retrieving application filters by name.
            - Mutually exclusive with I(snippet).
        type: str
        required: false
    snippet:
        description:
            - Filter application filters by snippet name.
            - Mutually exclusive with I(folder).
        type: str
        required: false
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
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Application filter objects must be associated with exactly one container (folder or snippet).
"""

EXAMPLES = r"""
- name: Get all application filters in a folder
  cdot65.scm.application_filter_info:
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
  register: all_filters

- name: Get a specific application filter by ID
  cdot65.scm.application_filter_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: filter_details

- name: Get application filter with a specific name
  cdot65.scm.application_filter_info:
    name: "high-risk-apps"
    folder: "Application-Filters"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_filter

- name: Get application filters by category
  cdot65.scm.application_filter_info:
    category: ["business-systems", "collaboration"]
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
  register: categorized_filters

- name: Get application filters by technology
  cdot65.scm.application_filter_info:
    technology: ["peer-to-peer"]
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
  register: p2p_filters

- name: Get high-risk application filters
  cdot65.scm.application_filter_info:
    risk: [4, 5]
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
  register: high_risk_filters

- name: Get application filters in a specific snippet
  cdot65.scm.application_filter_info:
    snippet: "Security-Filters"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_filters
"""

RETURN = r"""
application_filters:
    description: List of application filter objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The application filter object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The application filter object name
            type: str
            returned: always
            sample: "high-risk-apps"
        category:
            description: List of categories in the filter
            type: list
            returned: when applicable
            sample: ["business-systems", "collaboration"]
        sub_category:
            description: List of subcategories in the filter
            type: list
            returned: when applicable
            sample: ["file-sharing", "management"]
        technology:
            description: List of technologies in the filter
            type: list
            returned: when applicable
            sample: ["peer-to-peer", "client-server"]
        risk:
            description: List of risk levels in the filter
            type: list
            returned: when applicable
            sample: [4, 5]
        evasive:
            description: Whether the filter includes evasive applications
            type: bool
            returned: when applicable
            sample: false
        pervasive:
            description: Whether the filter includes pervasive applications
            type: bool
            returned: when applicable
            sample: false
        used_by_malware:
            description: Whether the filter includes applications used by malware
            type: bool
            returned: when applicable
            sample: false
        transfers_files:
            description: Whether the filter includes applications that transfer files
            type: bool
            returned: when applicable
            sample: true
        has_known_vulnerabilities:
            description: Whether the filter includes applications with known vulnerabilities
            type: bool
            returned: when applicable
            sample: true
        tunnels_other_apps:
            description: Whether the filter includes applications that tunnel other applications
            type: bool
            returned: when applicable
            sample: false
        prone_to_misuse:
            description: Whether the filter includes applications prone to misuse
            type: bool
            returned: when applicable
            sample: false
        folder:
            description: The folder containing the application filter
            type: str
            returned: when applicable
            sample: "Application-Filters"
        snippet:
            description: The snippet containing the application filter
            type: str
            returned: when applicable
            sample: "Security-Filters"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        category=dict(type="list", elements="str", required=False),
        subcategory=dict(type="list", elements="str", required=False),
        technology=dict(type="list", elements="str", required=False),
        risk=dict(type="list", elements="int", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        exclude_folders=dict(type="list", elements="str", required=False),
        exclude_snippets=dict(type="list", elements="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"application_filters": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get application filter by ID if specified
        if params.get("id"):
            try:
                app_filter_obj = client.application_filter.get(params.get("id"))
                if app_filter_obj:
                    result["application_filters"] = [json.loads(app_filter_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application filter info: {e}")
        # Fetch application filter by name
        elif params.get("name"):
            try:
                # Handle different container types (folder, snippet)
                container_type = None
                container_name = None

                if params.get("folder"):
                    container_type = "folder"
                    container_name = params.get("folder")
                elif params.get("snippet"):
                    container_type = "snippet"
                    container_name = params.get("snippet")

                # We need a container for the fetch operation
                if not container_type or not container_name:
                    module.fail_json(
                        msg="When retrieving an application filter by name, one of 'folder' or 'snippet' parameter is required"
                    )

                # For any container type, fetch the application filter object
                app_filter_obj = client.application_filter.fetch(name=params.get("name"), **{container_type: container_name})
                if app_filter_obj:
                    result["application_filters"] = [json.loads(app_filter_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application filter info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            else:
                module.fail_json(
                    msg="At least one container parameter (folder or snippet) is required for listing application filters"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # Add exclude params if specified
            if params.get("exclude_folders"):
                filter_params["exclude_folders"] = params.get("exclude_folders")

            if params.get("exclude_snippets"):
                filter_params["exclude_snippets"] = params.get("exclude_snippets")

            # Add category, subcategory, technology, risk filters
            if params.get("category"):
                filter_params["category"] = params.get("category")

            if params.get("subcategory"):
                filter_params["subcategory"] = params.get("subcategory")

            if params.get("technology"):
                filter_params["technology"] = params.get("technology")

            if params.get("risk"):
                filter_params["risk"] = params.get("risk")

            # List application filters with container filters
            app_filters = client.application_filter.list(**filter_params)

            # Convert to a list of dicts
            app_filter_dicts = [json.loads(a.model_dump_json(exclude_unset=True)) for a in app_filters]

            # Add to results
            result["application_filters"] = app_filter_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve application filter info: {e}")


if __name__ == "__main__":
    main()
