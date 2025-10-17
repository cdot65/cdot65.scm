#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: application_info
short_description: Get information about applications in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about applications in Strata Cloud Manager.
    - It can be used to get details about a specific application by ID or name, or to list all applications.
    - Supports filtering by application properties like category, subcategory, risk, folder, or snippet.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the application to retrieve.
            - If specified, the module will return information about this specific application.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the application to retrieve.
            - If specified, the module will search for applications with this name.
            - When using name, one of the container parameters (folder or snippet) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    category:
        description:
            - Filter applications by category.
            - Accepts a list of categories to match.
        type: list
        elements: str
        required: false
    subcategory:
        description:
            - Filter applications by subcategory.
            - Accepts a list of subcategories to match.
        type: list
        elements: str
        required: false
    technology:
        description:
            - Filter applications by technology.
            - Accepts a list of technologies to match.
        type: list
        elements: str
        required: false
    risk:
        description:
            - Filter applications by risk level.
            - Accepts a list of risk levels to match.
        type: list
        elements: int
        required: false
    folder:
        description:
            - Filter applications by folder name.
            - Required when retrieving applications by name.
            - Mutually exclusive with I(snippet).
        type: str
        required: false
    snippet:
        description:
            - Filter applications by snippet name.
            - Mutually exclusive with I(folder).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: False
        required: false
    exclude_folders:
        description:
            - List of folder names to exclude from results.
        type: list
        elements: str
        required: false
    exclude_snippets:
        description:
            - List of snippet values to exclude from results.
        type: list
        elements: str
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
    - Applications must be associated with exactly one container (folder or snippet).
"""

EXAMPLES = r"""
- name: Get all applications in a specific folder
  cdot65.scm.application_info:
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: folder_applications

- name: Get a specific application by ID
  cdot65.scm.application_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: application_details

- name: Get application with a specific name
  cdot65.scm.application_info:
    name: "my-custom-app"
    folder: "Custom-Applications"  # container parameter is required when using name
    scm_access_token: "{{ scm_access_token }}"
  register: named_application

- name: Get applications by category
  cdot65.scm.application_info:
    category: ["business-systems"]
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: business_applications

- name: Get applications by subcategory
  cdot65.scm.application_info:
    subcategory: ["file-sharing", "management"]
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: applications_by_subcategory

- name: Get applications by technology
  cdot65.scm.application_info:
    technology: ["client-server"]
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: client_server_applications

- name: Get high-risk applications (risk levels 4 and 5)
  cdot65.scm.application_info:
    risk: [4, 5]
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: high_risk_applications

- name: Get applications in a specific snippet
  cdot65.scm.application_info:
    snippet: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_applications

- name: Get applications excluding specific folders
  cdot65.scm.application_info:
    folder: "Parent-Folder"
    exclude_folders: ["Ignored-Subfolder"]
    exact_match: false
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_applications
"""

RETURN = r"""
applications:
    description: List of application resources
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The application ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The application name
            type: str
            returned: always
            sample: "my-custom-app"
        description:
            description: The application description
            type: str
            returned: when applicable
            sample: "Custom application for internal services"
        category:
            description: The application category
            type: str
            returned: always
            sample: "business-systems"
        subcategory:
            description: The application subcategory
            type: str
            returned: when applicable
            sample: "management"
        technology:
            description: The application technology
            type: str
            returned: when applicable
            sample: "client-server"
        risk:
            description: The risk level of the application
            type: int
            returned: always
            sample: 3
        ports:
            description: TCP/UDP ports associated with the application
            type: list
            returned: when applicable
            sample: ["tcp/8080", "udp/5000"]
        folder:
            description: The folder containing the application
            type: str
            returned: when applicable
            sample: "Custom-Applications"
        snippet:
            description: The snippet containing the application
            type: str
            returned: when applicable
            sample: "Custom-Applications"
        evasive:
            description: Whether the application uses evasive techniques
            type: bool
            returned: when applicable
            sample: false
        pervasive:
            description: Whether the application is widely used
            type: bool
            returned: when applicable
            sample: false
        excessive_bandwidth_use:
            description: Whether the application uses excessive bandwidth
            type: bool
            returned: when applicable
            sample: false
        used_by_malware:
            description: Whether the application is used by malware
            type: bool
            returned: when applicable
            sample: false
        transfers_files:
            description: Whether the application transfers files
            type: bool
            returned: when applicable
            sample: true
        has_known_vulnerabilities:
            description: Whether the application has known vulnerabilities
            type: bool
            returned: when applicable
            sample: true
        tunnels_other_apps:
            description: Whether the application tunnels other applications
            type: bool
            returned: when applicable
            sample: false
        prone_to_misuse:
            description: Whether the application is prone to misuse
            type: bool
            returned: when applicable
            sample: false
        no_certifications:
            description: Whether the application lacks certifications
            type: bool
            returned: when applicable
            sample: false
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
        exact_match=dict(type="bool", required=False, default=False),
        exclude_folders=dict(type="list", elements="str", required=False),
        exclude_snippets=dict(type="list", elements="str", required=False),
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

    result = {"applications": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get application by ID if specified
        if params.get("id"):
            try:
                application_obj = client.application.get(params.get("id"))
                if application_obj:
                    result["applications"] = [json.loads(application_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application info: {e}")
        # Fetch application by name
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
                        msg="When retrieving an application by name, exactly one of 'folder' or 'snippet' parameter is required"
                    )

                # For any container type, fetch the application object
                application_obj = client.application.fetch(name=params.get("name"), **{container_type: container_name})
                if application_obj:
                    result["applications"] = [json.loads(application_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve application info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            else:
                module.fail_json(msg="Exactly one container parameter (folder or snippet) is required for listing applications")

            # Add exact_match parameter if specified
            if params.get("exact_match") is not None:
                filter_params["exact_match"] = params.get("exact_match")

            # Add exclude parameters if specified
            if params.get("exclude_folders"):
                filter_params["exclude_folders"] = params.get("exclude_folders")

            if params.get("exclude_snippets"):
                filter_params["exclude_snippets"] = params.get("exclude_snippets")

            # List applications with container filters
            applications = client.application.list(**filter_params)

            # Apply additional client-side filtering
            filtered_apps = []

            for app in applications:
                # Filter by category
                if params.get("category") and app.category not in params.get("category"):
                    continue

                # Filter by subcategory
                if params.get("subcategory") and app.subcategory not in params.get("subcategory"):
                    continue

                # Filter by technology
                if params.get("technology") and app.technology not in params.get("technology"):
                    continue

                # Filter by risk
                if params.get("risk") and app.risk not in params.get("risk"):
                    continue

                # Add to filtered results
                filtered_apps.append(app)

            # Convert to a list of dicts
            application_dicts = [json.loads(app.model_dump_json(exclude_unset=True)) for app in filtered_apps]

            # Add to results
            result["applications"] = application_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve application info: {e}")


if __name__ == "__main__":
    main()
