#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects.application_group import ApplicationGroupCreateModel

DOCUMENTATION = r"""
---
module: application_group
short_description: Manage application groups in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete application groups in Strata Cloud Manager using pan-scm-sdk.
    - Supports both static and dynamic application groups with robust idempotency.
    - Application groups must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the application group.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the application group.
        type: str
        required: false
    tag:
        description:
            - Tags associated with the application group.
        type: list
        elements: str
        required: false
    group_type:
        description:
            - Type of application group to create.
            - Required for state=present.
            - Will be inferred from static_applications or dynamic_filter if not specified.
        type: str
        choices: ['static', 'dynamic']
        required: false
    static_applications:
        description:
            - List of application object names to include in the static application group.
            - Required when group_type is 'static'.
            - Mutually exclusive with I(dynamic_filter).
        type: list
        elements: str
        required: false
    dynamic_filter:
        description:
            - Filter expression for dynamic application groups.
            - Required when group_type is 'dynamic'.
            - Mutually exclusive with I(static_applications).
            - Format should follow SCM's dynamic application group filter syntax.
            - Use single-quoted paths for tag matching, e.g., "'app.category.business-systems'".
            - Example: "'app.category.business-systems'" or "'app.risk=3' or 'app.risk=4'"
        type: str
        required: false
    folder:
        description:
            - The folder in which the application group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the application group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the application group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the application group (UUID).
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
            - Desired state of the application group.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Application groups must be associated with exactly one container (folder, snippet, or device).
    - Either static_applications or dynamic_filter must be provided for creation.
"""

EXAMPLES = r"""
- name: Create a static application group in a folder (explicitly specifying group_type)
  cdot65.scm.application_group:
    name: "web-apps"
    description: "Web application group"
    group_type: "static"
    static_applications:
      - "http"
      - "https"
    folder: "Application-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a dynamic application group in a snippet (explicitly specifying group_type)
  cdot65.scm.application_group:
    name: "dynamic-apps"
    description: "Dynamic application group"
    group_type: "dynamic"
    dynamic_filter: "'app.category.business-systems'"  # Proper SCM filter syntax
    snippet: "web-acl"
    tag:
      - "web"
      - "dynamic"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a static application group with inferred group_type
  cdot65.scm.application_group:
    name: "inferred-static-group"
    description: "Static group with inferred type"
    static_applications:
      - "smtp"
      - "pop3"
    folder: "Application-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a static application group
  cdot65.scm.application_group:
    name: "web-apps"
    description: "Updated web application group"
    static_applications:
      - "http"
      - "https"
      - "http2"
    folder: "Application-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a dynamic application group
  cdot65.scm.application_group:
    name: "dynamic-apps"
    description: "Updated dynamic application group"
    dynamic_filter: "'app.category.business-systems' or 'app.category.collaboration'"
    snippet: "web-acl"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an application group by name
  cdot65.scm.application_group:
    name: "web-apps"
    folder: "Application-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an application group by ID
  cdot65.scm.application_group:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
application_group:
    description: Information about the application group that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The application group ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The application group name
            type: str
            returned: always
            sample: "web-apps"
        description:
            description: The application group description
            type: str
            returned: when applicable
            sample: "Web application group"
        members:
            description: List of application objects (for static groups) or filter expressions (for dynamic groups)
            type: list
            returned: always
            sample: ["http", "https"] or ["'app.category.business-systems'"]
        tag:
            description: Tags associated with the application group
            type: list
            returned: when applicable
            sample: ["web", "dynamic"]
        folder:
            description: The folder containing the application group
            type: str
            returned: when applicable
            sample: "Application-Objects"
        snippet:
            description: The snippet containing the application group
            type: str
            returned: when applicable
            sample: "web-acl"
        device:
            description: The device containing the application group
            type: str
            returned: when applicable
            sample: "firewall-01"
        type:
            description: The type of application group (static or dynamic)
            type: str
            returned: always
            sample: "static"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        group_type=dict(type="str", required=False, choices=["static", "dynamic"]),
        static_applications=dict(type="list", elements="str", required=False),
        dynamic_filter=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
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
            ["folder", "snippet", "device"],
            ["static_applications", "dynamic_filter"],
        ],
        supports_check_mode=True,
    )

    # Custom validation for group type parameters
    params = module.params
    if params.get("state") == "present":
        # Handle group_type validation
        group_type = params.get("group_type")
        has_static = params.get("static_applications") is not None
        has_dynamic = params.get("dynamic_filter") is not None

        # If group_type is not specified, try to infer it
        if not group_type:
            if has_static and not has_dynamic:
                group_type = "static"
            elif has_dynamic and not has_static:
                group_type = "dynamic"
            else:
                module.fail_json(
                    msg="When state=present, either specify group_type or provide exactly one of: static_applications, dynamic_filter"
                )

        # Validate correct parameters based on group_type
        if group_type == "static" and not has_static:
            module.fail_json(msg="When group_type=static, static_applications parameter is required")
        elif group_type == "dynamic" and not has_dynamic:
            module.fail_json(msg="When group_type=dynamic, dynamic_filter parameter is required")

        # Add group_type to params for use in API payload
        params["group_type"] = group_type

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "application_group": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize application_group_exists boolean
        application_group_exists = False
        application_group_obj = None

        # Fetch application group by name
        if params.get("name"):
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

                # For any container type, fetch the application group
                if container_type and container_name:
                    application_group_obj = client.application_group.fetch(name=params.get("name"), **{container_type: container_name})
                    if application_group_obj:
                        application_group_exists = True
            except ObjectNotPresentError:
                application_group_exists = False
                application_group_obj = None

        # Create or update or delete an application group
        if params.get("state") == "present":
            if application_group_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "tag",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(application_group_obj, k, None) != params[k]
                }

                # Handle group_type specific updates
                if params.get("group_type") == "static" and params.get("static_applications"):
                    # Check if static_applications need updating
                    if getattr(application_group_obj, "members", None) != params.get("static_applications"):
                        update_fields["members"] = params.get("static_applications")

                elif params.get("group_type") == "dynamic" and params.get("dynamic_filter"):
                    # Get the current dynamic filter if it exists
                    current_filter = None
                    if hasattr(application_group_obj, "members") and len(application_group_obj.members) > 0:
                        # Assuming the first member is the filter expression for dynamic groups
                        current_filter = application_group_obj.members[0]

                    # Check if it needs updating
                    if current_filter != params.get("dynamic_filter"):
                        # Update with the new filter expression as a single-item list
                        update_fields["members"] = [params.get("dynamic_filter")]

                # Update the application group if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = application_group_obj.model_copy(update=update_fields)
                        updated = client.application_group.update(update_model)
                        result["application_group"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["application_group"] = json.loads(application_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["application_group"] = json.loads(application_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new application group
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "tag",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # The SDK uses a common 'members' field for all applications
                # For static groups, we just use the list of applications directly
                if params.get("group_type") == "static":
                    create_payload["members"] = params.get("static_applications")
                # For dynamic groups, we create a list with the filter expression
                elif params.get("group_type") == "dynamic":
                    create_payload["members"] = [params.get("dynamic_filter")]

                # Create an application group
                if not module.check_mode:
                    try:
                        # Create an application group
                        created = client.application_group.create(create_payload)
                        # Return the created application group
                        result["application_group"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error creating application group: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error creating application group: {str(e)}", payload=create_payload)
                else:
                    # Simulate a created application group (minimal info)
                    simulated = ApplicationGroupCreateModel(**create_payload)
                    result["application_group"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete an application group
        elif params.get("state") == "absent":
            if application_group_exists:
                if not module.check_mode:
                    client.application_group.delete(application_group_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["application_group"] = json.loads(application_group_obj.model_dump_json(exclude_unset=True))
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