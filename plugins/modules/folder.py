#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup import FolderCreateModel

DOCUMENTATION = r"""
---
module: folder
short_description: Manage folders in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete folders in Strata Cloud Manager using pan-scm-sdk.
    - Supports all folder attributes and robust idempotency.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the folder.
            - Required for both state=present and state=absent.
        type: str
        required: false
    parent:
        description:
            - Name of the parent folder (empty string for root).
            - Required for state=present.
        type: str
        required: false
    description:
        description:
            - Description of the folder.
        type: str
        required: false
    labels:
        description:
            - List of labels to apply to the folder.
        type: list
        elements: str
        required: false
    snippets:
        description:
            - List of snippet IDs associated with the folder.
        type: list
        elements: str
        required: false
    display_name:
        description:
            - Display name for the folder/device, if present.
        type: str
        required: false
    model:
        description:
            - Device model, if present (e.g., 'PA-VM').
        type: str
        required: false
    serial_number:
        description:
            - Device serial number, if present.
        type: str
        required: false
    type:
        description:
            - Type of folder or device (e.g., 'on-prem', 'container', 'cloud').
        type: str
        required: false
    device_only:
        description:
            - True if this is a device-only entry.
        type: bool
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
            - Desired state of the folder.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
"""

EXAMPLES = r"""
- name: Create a folder
  cdot65.scm.folder:
    name: "Network Objects"
    description: "Folder for network objects"
    state: present

- name: Create a subfolder
  cdot65.scm.folder:
    name: "Address Objects"
    description: "Folder for address objects"
    parent: "Network Objects"
    state: present

- name: Delete a folder
  cdot65.scm.folder:
    name: "Network Objects"
    state: absent

"""

RETURN = r"""
folder:
    description: Information about the folder that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The folder ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The folder name
            type: str
            returned: always
            sample: "Network Objects"
        description:
            description: The folder description
            type: str
            returned: always
            sample: "Folder for network objects"
        parent:
            description: The name of the parent folder
            type: str
            returned: when applicable
            sample: "Network Objects"
        created_at:
            description: The creation timestamp
            type: str
            returned: always
            sample: "2025-04-16T13:28:36.000Z"
        updated_at:
            description: The last update timestamp
            type: str
            returned: always
            sample: "2025-04-16T13:28:36.000Z"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        parent=dict(type="str", required=False),
        description=dict(type="str", required=False),
        labels=dict(type="list", elements="str", required=False),
        snippets=dict(type="list", elements="str", required=False),
        display_name=dict(type="str", required=False),
        model=dict(type="str", required=False),
        serial_number=dict(type="str", required=False),
        type=dict(type="str", required=False),
        device_only=dict(type="bool", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "parent"]],
            ["state", "absent", ["name"]],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "folder": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize folder_exists boolean
        folder_exists = False
        folder_obj = None

        # Fetch folder by name
        if params.get("name"):
            try:
                folder_obj = client.folder.fetch(params.get("name"))
                if folder_obj:
                    folder_exists = True
            except ObjectNotPresentError:
                folder_exists = False
                folder_obj = None

        # Create or update or delete a folder
        if params.get("state") == "present":
            if folder_exists:
                # Only update fields that differ
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "labels",
                        "snippets",
                        "display_name",
                        "model",
                        "serial_number",
                        "type",
                        "device_only",
                        "parent",
                    ]
                    if params.get(k) is not None and getattr(folder_obj, k, None) != params[k]
                }

                # Update a folder if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = folder_obj.model_copy(update=update_fields)
                        updated = client.folder.update(update_model)
                        result["folder"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["folder"] = json.loads(
                            folder_obj.model_copy(update=update_fields).model_dump_json(exclude_unset=True)
                        )
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["folder"] = json.loads(folder_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)
            else:
                # Create payload
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "parent",
                        "description",
                        "labels",
                        "snippets",
                        "display_name",
                        "model",
                        "serial_number",
                        "type",
                        "device_only",
                    ]
                    if params.get(k) is not None
                }

                # Create a new folder
                if not module.check_mode:
                    # Create folder
                    created = client.folder.create(create_payload)

                    # Return the created folder
                    result["folder"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate created folder (minimal info)
                    simulated = FolderCreateModel(**create_payload)
                    result["folder"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a folder
        elif params.get("state") == "absent":
            if folder_exists:
                if not module.check_mode:
                    client.folder.delete(folder_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["folder"] = json.loads(folder_obj.model_dump_json(exclude_unset=True))
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
