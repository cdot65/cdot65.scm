#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

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
            - Required for state=present and for absent if id is not provided.
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
    id:
        description:
            - Unique identifier for the folder (UUID).
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

- name: Delete a folder by name
  cdot65.scm.folder:
    name: "Network Objects"
    state: absent

- name: Delete a folder by ID
  cdot65.scm.folder:
    id: "12345678-1234-1234-1234-123456789012"
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
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "parent"]],
            ["state", "absent", ["name"]],
        ],
        supports_check_mode=True,
    )

    params = module.params
    state = params["state"]
    folder_id = params.get("id")
    name = params.get("name")
    parent = params.get("parent")
    scm_access_token = params.get("scm_access_token")

    result = {"changed": False, "folder": None}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=scm_access_token)

        # Fetch folder by name (preferred) or id
        folder_obj = None
        if folder_id:
            try:
                folder_obj = client.folder.get(folder_id)
                if folder_obj:
                    result["folders"] = [json.loads(folder_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError:
                folder_obj = None
        elif name:
            folder_obj = client.folder.fetch(name)

        if state == "present":
            if folder_obj:
                # Compare all updatable fields
                update_fields = {}
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
                ]:
                    v = params.get(k)
                    if v is not None and getattr(folder_obj, k, None) != v:
                        update_fields[k] = v
                if update_fields:
                    if not module.check_mode:
                        from scm.models.setup.folder import FolderUpdateModel

                        update_model = FolderUpdateModel(
                            id=folder_obj.id, name=folder_obj.name, parent=parent or folder_obj.parent, **update_fields
                        )
                        updated = client.folder.update(update_model)
                        result["folder"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                else:
                    result["folder"] = json.loads(folder_obj.model_dump_json(exclude_unset=True))
            else:
                # Create new folder
                if not module.check_mode:
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
                    created = client.folder.create(create_payload)
                    result["folder"] = json.loads(created.model_dump_json(exclude_unset=True))
                result["changed"] = True
        elif state == "absent":
            if folder_obj:
                if not module.check_mode:
                    client.folder.delete(folder_obj.id)
                result["changed"] = True
                result["folder"] = json.loads(folder_obj.model_dump_json(exclude_unset=True))
        module.exit_json(**result)
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
