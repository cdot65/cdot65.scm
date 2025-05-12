#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects.application import ApplicationCreateModel

DOCUMENTATION = r"""
---
module: application
short_description: Manage application objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete application objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all application attributes and robust idempotency.
    - Application objects must be associated with exactly one container (folder or snippet).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the application object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    category:
        description:
            - High-level category to which the application belongs.
            - Required when creating a new application.
            - Not required for updates.
        type: str
        required: false
    subcategory:
        description:
            - Specific sub-category within the high-level category.
            - Required when creating a new application.
            - Not required for updates.
        type: str
        required: false
    technology:
        description:
            - The underlying technology utilized by the application.
            - Required when creating a new application.
            - Not required for updates.
        type: str
        required: false
    risk:
        description:
            - The risk level associated with the application.
            - Required when creating a new application.
            - Not required for updates.
        type: int
        required: false
    description:
        description:
            - Description of the application object.
        type: str
        required: false
    ports:
        description:
            - List of TCP/UDP ports associated with the application.
        type: list
        elements: str
        required: false
    folder:
        description:
            - The folder in which the application is defined.
            - Exactly one of folder or snippet must be provided for state=present.
            - Mutually exclusive with I(snippet).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the application is defined.
            - Exactly one of folder or snippet must be provided for state=present.
            - Mutually exclusive with I(folder).
        type: str
        required: false
    evasive:
        description:
            - Indicates if the application uses evasive techniques.
        type: bool
        required: false
        default: false
    pervasive:
        description:
            - Indicates if the application is widely used.
        type: bool
        required: false
        default: false
    excessive_bandwidth_use:
        description:
            - Indicates if the application uses excessive bandwidth.
        type: bool
        required: false
        default: false
    used_by_malware:
        description:
            - Indicates if the application is commonly used by malware.
        type: bool
        required: false
        default: false
    transfers_files:
        description:
            - Indicates if the application transfers files.
        type: bool
        required: false
        default: false
    has_known_vulnerabilities:
        description:
            - Indicates if the application has known vulnerabilities.
        type: bool
        required: false
        default: false
    tunnels_other_apps:
        description:
            - Indicates if the application tunnels other applications.
        type: bool
        required: false
        default: false
    prone_to_misuse:
        description:
            - Indicates if the application is prone to misuse.
        type: bool
        required: false
        default: false
    no_certifications:
        description:
            - Indicates if the application lacks certifications.
        type: bool
        required: false
        default: false
    id:
        description:
            - Unique identifier for the application (UUID).
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
            - Desired state of the application.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Application objects must be associated with exactly one container (folder or snippet).
"""

EXAMPLES = r"""
- name: Create a folder-based application
  cdot65.scm.application:
    name: "my-custom-app"
    description: "Custom application for internal services"
    category: "business-systems"
    subcategory: "management"
    technology: "client-server"
    risk: 3
    ports:
      - "tcp/8080"
      - "udp/5000"
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based application with risk flags
  cdot65.scm.application:
    name: "internal-file-sharing"
    description: "Internal file sharing application"
    category: "collaboration"
    subcategory: "file-sharing"
    technology: "peer-to-peer"
    risk: 4
    ports:
      - "tcp/8000"
    snippet: "Custom-Applications"
    transfers_files: true
    has_known_vulnerabilities: true
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an application's description and risk level (only specify fields to update)
  cdot65.scm.application:
    name: "my-custom-app"
    description: "Updated custom application description"
    risk: 2
    folder: "Custom-Applications"  # Container parameter is still required
    scm_access_token: "{{ scm_access_token }}"
    state: present
    # Note: category, subcategory, and technology are not required for updates

- name: Delete an application by name
  cdot65.scm.application:
    name: "my-custom-app"
    folder: "Custom-Applications"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an application by ID
  cdot65.scm.application:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
application:
    description: Information about the application that was managed
    returned: on success
    type: dict
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
            returned: always
            sample: "management"
        technology:
            description: The application technology
            type: str
            returned: always
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
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        category=dict(type="str", required=False),
        subcategory=dict(type="str", required=False),
        technology=dict(type="str", required=False),
        risk=dict(type="int", required=False),
        ports=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        evasive=dict(type="bool", required=False, default=False),
        pervasive=dict(type="bool", required=False, default=False),
        excessive_bandwidth_use=dict(type="bool", required=False, default=False),
        used_by_malware=dict(type="bool", required=False, default=False),
        transfers_files=dict(type="bool", required=False, default=False),
        has_known_vulnerabilities=dict(type="bool", required=False, default=False),
        tunnels_other_apps=dict(type="bool", required=False, default=False),
        prone_to_misuse=dict(type="bool", required=False, default=False),
        no_certifications=dict(type="bool", required=False, default=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
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

        # Check if name is provided
        if not params.get("name"):
            module.fail_json(msg="When state=present, the name parameter is required")

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "application": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize application_exists boolean
        application_exists = False
        application_obj = None

        # Fetch application by name
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

                # For any container type, fetch the application object
                if container_type and container_name:
                    application_obj = client.application.fetch(name=params.get("name"), **{container_type: container_name})
                    if application_obj:
                        application_exists = True
            except ObjectNotPresentError:
                application_exists = False
                application_obj = None

        # Create or update or delete an application
        if params.get("state") == "present":
            if application_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "category",
                        "subcategory",
                        "technology",
                        "risk",
                        "ports",
                        "folder",
                        "snippet",
                        "evasive",
                        "pervasive",
                        "excessive_bandwidth_use",
                        "used_by_malware",
                        "transfers_files",
                        "has_known_vulnerabilities",
                        "tunnels_other_apps",
                        "prone_to_misuse",
                        "no_certifications",
                    ]
                    if params[k] is not None and getattr(application_obj, k, None) != params[k]
                }

                # Update the application if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = application_obj.model_copy(update=update_fields)
                        updated = client.application.update(update_model)
                        result["application"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["application"] = json.loads(application_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["application"] = json.loads(application_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Validate required fields for creation
                required_fields = ["name", "category", "subcategory", "technology", "risk"]
                missing_fields = [field for field in required_fields if params.get(field) is None]
                if missing_fields:
                    module.fail_json(
                        msg=f"When creating a new application, the following fields are required: {', '.join(missing_fields)}"
                    )

                # Create payload for new application object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "category",
                        "subcategory",
                        "technology",
                        "risk",
                        "ports",
                        "folder",
                        "snippet",
                        "evasive",
                        "pervasive",
                        "excessive_bandwidth_use",
                        "used_by_malware",
                        "transfers_files",
                        "has_known_vulnerabilities",
                        "tunnels_other_apps",
                        "prone_to_misuse",
                        "no_certifications",
                    ]
                    if params.get(k) is not None
                }

                # Create an application object
                if not module.check_mode:
                    # Create an application object
                    created = client.application.create(create_payload)

                    # Return the created application object
                    result["application"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created application object (minimal info)
                    simulated = ApplicationCreateModel(**create_payload)
                    result["application"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete an application object
        elif params.get("state") == "absent":
            if application_exists:
                if not module.check_mode:
                    client.application.delete(application_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["application"] = json.loads(application_obj.model_dump_json(exclude_unset=True))
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
