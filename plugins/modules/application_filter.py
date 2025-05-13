#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import ApplicationFiltersCreateModel

DOCUMENTATION = r"""
---
module: application_filter
short_description: Manage application filter objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete application filter objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all application filter attributes and robust idempotency.
    - Application filter objects must be associated with exactly one container (folder or snippet).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the application filter object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
        type: str
        required: false
    category:
        description:
            - List of categories to include in the application filter.
        type: list
        elements: str
        required: false
    sub_category:
        description:
            - List of subcategories to include in the application filter.
        type: list
        elements: str
        required: false
    technology:
        description:
            - List of technologies to include in the application filter.
        type: list
        elements: str
        required: false
    risk:
        description:
            - List of risk levels (integers) to include in the application filter.
        type: list
        elements: int
        required: false
    evasive:
        description:
            - Whether the filter should include applications that use evasive techniques.
        type: bool
        required: false
        default: false
    pervasive:
        description:
            - Whether the filter should include pervasive applications.
        type: bool
        required: false
        default: false
    used_by_malware:
        description:
            - Whether the filter should include applications used by malware.
        type: bool
        required: false
        default: false
    transfers_files:
        description:
            - Whether the filter should include applications that transfer files.
        type: bool
        required: false
        default: false
    has_known_vulnerabilities:
        description:
            - Whether the filter should include applications with known vulnerabilities.
        type: bool
        required: false
        default: false
    tunnels_other_apps:
        description:
            - Whether the filter should include applications that tunnel other applications.
        type: bool
        required: false
        default: false
    prone_to_misuse:
        description:
            - Whether the filter should include applications prone to misuse.
        type: bool
        required: false
        default: false
    is_saas:
        description:
            - Whether the filter should include SaaS applications.
        type: bool
        required: false
        default: false
    new_appid:
        description:
            - Whether the filter should include applications with new AppIDs.
        type: bool
        required: false
        default: false
    saas_certifications:
        description:
            - List of SaaS certifications to include in the filter.
        type: list
        elements: str
        required: false
    saas_risk:
        description:
            - List of SaaS risk levels to include in the filter.
        type: list
        elements: str
        required: false
    folder:
        description:
            - The folder in which the application filter is defined.
            - Exactly one of folder or snippet must be provided for state=present.
            - Mutually exclusive with I(snippet).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the application filter is defined.
            - Exactly one of folder or snippet must be provided for state=present.
            - Mutually exclusive with I(folder).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the application filter (UUID).
            - Used for lookup/deletion if provided.
        type: str
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
    state:
        description:
            - Desired state of the application filter object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Application filter objects must be associated with exactly one container (folder or snippet).
"""

EXAMPLES = r"""
- name: Create a folder-based application filter
  cdot65.scm.application_filter:
    name: "high-risk-apps"
    category:
      - "business-systems"
      - "collaboration"
    risk:
      - 4
      - 5
    has_known_vulnerabilities: true
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based application filter with technology criteria
  cdot65.scm.application_filter:
    name: "peer-to-peer-apps"
    technology:
      - "peer-to-peer"
    sub_category:
      - "file-sharing"
    transfers_files: true
    snippet: "Security-Filters"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an application filter's criteria
  cdot65.scm.application_filter:
    name: "high-risk-apps"
    category:
      - "business-systems"
      - "collaboration"
      - "general-internet"
    risk:
      - 3
      - 4
      - 5
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an application filter by name
  cdot65.scm.application_filter:
    name: "high-risk-apps"
    folder: "Application-Filters"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an application filter by ID
  cdot65.scm.application_filter:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
application_filter:
    description: Information about the application filter that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The application filter ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The application filter name
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
    module_args = dict(
        name=dict(type="str", required=False),
        category=dict(type="list", elements="str", required=False),
        sub_category=dict(type="list", elements="str", required=False),
        technology=dict(type="list", elements="str", required=False),
        risk=dict(type="list", elements="int", required=False),
        evasive=dict(type="bool", required=False, default=False),
        pervasive=dict(type="bool", required=False, default=False),
        used_by_malware=dict(type="bool", required=False, default=False),
        transfers_files=dict(type="bool", required=False, default=False),
        has_known_vulnerabilities=dict(type="bool", required=False, default=False),
        tunnels_other_apps=dict(type="bool", required=False, default=False),
        prone_to_misuse=dict(type="bool", required=False, default=False),
        is_saas=dict(type="bool", required=False, default=False),
        new_appid=dict(type="bool", required=False, default=False),
        saas_certifications=dict(type="list", elements="str", required=False),
        saas_risk=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet"],
        ],
        supports_check_mode=True,
    )

    # Custom validation for container parameters
    params = module.params
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet")

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "application_filter": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize application_filter_exists boolean
        application_filter_exists = False
        application_filter_obj = None

        # Fetch application filter by name
        if params.get("name"):
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

                # For any container type, fetch the application filter object
                if container_type and container_name:
                    application_filter_obj = client.application_filter.fetch(
                        name=params.get("name"), **{container_type: container_name}
                    )
                    if application_filter_obj:
                        application_filter_exists = True
            except ObjectNotPresentError:
                application_filter_exists = False
                application_filter_obj = None

        # Create or update or delete an application filter
        if params.get("state") == "present":
            if application_filter_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}
                
                # Handle non-boolean fields
                for k in [
                    "category",
                    "sub_category",
                    "technology",
                    "risk",
                    "saas_certifications",
                    "saas_risk",
                    "folder",
                    "snippet",
                ]:
                    if params.get(k) is not None and getattr(application_filter_obj, k, None) != params[k]:
                        update_fields[k] = params[k]
                
                # Boolean fields in SCM require special handling
                # Only include true values, don't try to explicitly set false values
                bool_fields = [
                    "evasive",
                    "pervasive",
                    "used_by_malware",
                    "transfers_files",
                    "has_known_vulnerabilities",
                    "tunnels_other_apps",
                    "prone_to_misuse",
                    "is_saas",
                    "new_appid",
                ]
                
                for k in bool_fields:
                    # Only consider boolean fields that were explicitly provided
                    if k in params and params[k] is not None:
                        current_value = getattr(application_filter_obj, k, False) 
                        new_value = params[k]
                        
                        # If changing to True, update field
                        if new_value is True and current_value is not True:
                            update_fields[k] = True
                        # We don't handle setting to False here - it can only be "unset"
                        # through the API by removing the field completely

                # Update the application filter if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = application_filter_obj.model_copy(update=update_fields)
                        updated = client.application_filter.update(update_model)
                        result["application_filter"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["application_filter"] = json.loads(application_filter_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["application_filter"] = json.loads(application_filter_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new application filter object
                create_payload = {}
                
                # Handle non-boolean fields
                for k in [
                    "name",
                    "category",
                    "sub_category",
                    "technology",
                    "risk",
                    "saas_certifications",
                    "saas_risk",
                    "folder",
                    "snippet",
                ]:
                    if params.get(k) is not None:
                        create_payload[k] = params[k]
                
                # Handle boolean fields - only add if they are True
                # This avoids sending 'False' which gets converted to 'no' in the API
                for k in [
                    "evasive",
                    "pervasive",
                    "used_by_malware",
                    "transfers_files",
                    "has_known_vulnerabilities",
                    "tunnels_other_apps",
                    "prone_to_misuse",
                    "is_saas",
                    "new_appid",
                ]:
                    if params.get(k) is True:
                        create_payload[k] = True

                # Create an application filter object
                if not module.check_mode:
                    # Create an application filter object
                    created = client.application_filter.create(create_payload)

                    # Return the created application filter object
                    result["application_filter"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created application filter object (minimal info)
                    simulated = ApplicationFiltersCreateModel(**create_payload)
                    result["application_filter"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete an application filter object
        elif params.get("state") == "absent":
            if application_filter_exists:
                if not module.check_mode:
                    client.application_filter.delete(application_filter_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["application_filter"] = json.loads(application_filter_obj.model_dump_json(exclude_unset=True))
                module.exit_json(**result)
            else:
                # Already absent
                result["changed"] = False
                module.exit_json(**result)

    # Handle errors
    except (ObjectNotPresentError, InvalidObjectError) as e:
        module.fail_json(msg=str(e), error_code=getattr(e, "error_code", None), details=getattr(e, "details", None))
    except APIError as e:
        module.fail_json(
            msg="API error: " + str(e), error_code=getattr(e, "error_code", None), details=getattr(e, "details", None)
        )
    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
