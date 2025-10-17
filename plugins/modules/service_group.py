#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects.service_group import ServiceGroupCreateModel

DOCUMENTATION = r"""
---
module: service_group
short_description: Manage service groups in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete service groups in Strata Cloud Manager using pan-scm-sdk.
    - Service groups contain a list of service members for organizing and managing service objects.
    - Service groups must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the service group.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    members:
        description:
            - List of service member names to include in the service group.
            - Required for state=present.
            - Each member must be an existing service or service group object name.
            - Minimum 1 member, maximum 1024 members.
        type: list
        elements: str
        required: false
    tag:
        description:
            - Tags associated with the service group.
            - These must be references to existing tag objects.
        type: list
        elements: str
        required: false
    folder:
        description:
            - The folder in which the service group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the service group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the service group is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the service group (UUID).
            - Used for lookup/deletion if provided.
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token for authenticating API calls, provided by the auth role.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
            - If not specified, the value of the SCM_API_URL environment variable will be used.
        type: str
        required: false
    state:
        description:
            - Desired state of the service group.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Service groups must be associated with exactly one container (folder, snippet, or device).
    - Members list is required for service group creation and must contain at least one member.
"""

EXAMPLES = r"""
- name: Create a service group in a folder
  cdot65.scm.service_group:
    name: "web-services"
    members:
      - "custom-http"
      - "custom-https"
    folder: "Network-Services"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a service group with tags in a snippet
  cdot65.scm.service_group:
    name: "database-services"
    members:
      - "mysql-service"
      - "postgres-service"
      - "mongodb-service"
    snippet: "db-config"
    tag:
      - "database"
      - "production"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a service group
  cdot65.scm.service_group:
    name: "web-services"
    members:
      - "custom-http"
      - "custom-https"
      - "custom-http8080"
    folder: "Network-Services"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a service group by name
  cdot65.scm.service_group:
    name: "web-services"
    folder: "Network-Services"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a service group by ID
  cdot65.scm.service_group:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
service_group:
    description: Information about the service group that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The service group ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The service group name
            type: str
            returned: always
            sample: "web-services"
        members:
            description: List of service members in the group
            type: list
            returned: always
            sample: ["custom-http", "custom-https"]
        tag:
            description: Tags associated with the service group
            type: list
            returned: when applicable
            sample: ["web", "production"]
        folder:
            description: The folder containing the service group
            type: str
            returned: when applicable
            sample: "Network-Services"
        snippet:
            description: The snippet containing the service group
            type: str
            returned: when applicable
            sample: "web-config"
        device:
            description: The device containing the service group
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        members=dict(type="list", elements="str", required=False),
        tag=dict(type="list", elements="str", required=False),
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
            ["state", "present", ["name", "members"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Validate name parameter
    if params.get("name"):
        name = params.get("name")
        if len(name) > 63:
            module.fail_json(msg=f"Parameter 'name' exceeds maximum length of 63 characters (got {len(name)})")
        # Validate name pattern to match SDK requirements
        import re

        if not re.match(r"^[a-zA-Z0-9_ \.-]+$", name):
            module.fail_json(msg="Parameter 'name' contains invalid characters. Must match pattern: ^[a-zA-Z0-9_ \\.-]+$")

    # Initialize results
    result = {"changed": False, "service_group": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize service_group_exists boolean
        service_group_exists = False
        service_group_obj = None

        # Fetch service group by name
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

                # For any container type, fetch the service group
                if container_type and container_name:
                    service_group_obj = client.service_group.fetch(name=params.get("name"), **{container_type: container_name})
                    if service_group_obj:
                        service_group_exists = True
            except ObjectNotPresentError:
                service_group_exists = False
                service_group_obj = None

        # Create or update or delete a service group
        if params.get("state") == "present":
            if service_group_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "members",
                        "tag",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(service_group_obj, k, None) != params[k]
                }

                # Update the service group if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = service_group_obj.model_copy(update=update_fields)
                        updated = client.service_group.update(update_model)
                        result["service_group"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["service_group"] = json.loads(service_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["service_group"] = json.loads(service_group_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new service group
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "members",
                        "tag",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a service group
                if not module.check_mode:
                    try:
                        # Create a service group
                        created = client.service_group.create(create_payload)
                        # Return the created service group
                        result["service_group"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error creating service group: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error creating service group: {str(e)}", payload=create_payload)
                else:
                    # Simulate a created service group (minimal info)
                    simulated = ServiceGroupCreateModel(**create_payload)
                    result["service_group"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a service group
        elif params.get("state") == "absent":
            if service_group_exists:
                if not module.check_mode:
                    client.service_group.delete(service_group_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["service_group"] = json.loads(service_group_obj.model_dump_json(exclude_unset=True))
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
