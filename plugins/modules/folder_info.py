#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient

DOCUMENTATION = r"""
---
module: folder_info
short_description: Get information about folders in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about folders in Strata Cloud Manager.
    - It can be used to get details about a specific folder by ID or name, or to list all folders.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the folder to retrieve.
            - If specified, the module will return information about this specific folder.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the folder to retrieve.
            - If specified, the module will search for folders with this name.
            - Mutually exclusive with I(id).
        type: str
        required: false
    parent:
        description:
            - If specified, only folders under this parent folder will be returned.
            - Ignored if I(id) is specified.
        type: str
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
    - For authentication, you can set the C(SCM_ACCESS_TOKEN) environment variable
      instead of providing it as a module option.
"""

EXAMPLES = r"""
- name: Get all folders
  cdot65.scm.folder_info:
  register: all_folders

- name: Get a specific folder by ID
  cdot65.scm.folder_info:
    id: "12345678-1234-1234-1234-123456789012"
  register: folder_details

- name: Get folders with a specific name
  cdot65.scm.folder_info:
    name: "Network Objects"
  register: named_folders

- name: Get folders under a specific parent
  cdot65.scm.folder_info:
    parent: "87654321-4321-4321-4321-210987654321"
  register: child_folders
"""

RETURN = r"""
folders:
    description: List of folder resources
    returned: always
    type: list
    elements: dict
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
            description: The ID of the parent folder
            type: str
            returned: when applicable
            sample: "87654321-4321-4321-4321-210987654321"
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
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        parent=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(argument_spec=module_args, mutually_exclusive=[["id", "name"]], supports_check_mode=True)

    # Get parameters
    params = module.params
    folder_id = params.get("id")
    name = params.get("name")
    parent = params.get("parent")

    result = {"folders": []}

    try:
        # Initialize SCM client
        client = ScmClient(
            access_token=params["scm_access_token"],
        )
        folders_service = client.folder

        # Get folder by ID if specified
        if folder_id:
            folder = folders_service.get(folder_id)
            if folder:
                result["folders"] = [json.loads(folder.model_dump_json(exclude_unset=True))]
        else:
            # List all folders
            folders = folders_service.list()
            folder_dicts = [json.loads(f.model_dump_json(exclude_unset=True)) for f in folders]
            # Filter by name if specified
            if name:
                folder_dicts = [f for f in folder_dicts if f.get("name") == name]
            # Filter by parent if specified
            if parent:
                folder_dicts = [f for f in folder_dicts if f.get("parent") == parent]
            result["folders"] = folder_dicts
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve folder info: {e}")


if __name__ == "__main__":
    main()
