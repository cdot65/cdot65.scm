#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
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
    api_key:
        description:
            - The API key for SCM authentication.
            - If not specified, the value of the SCM_API_KEY environment variable will be used.
        type: str
        required: false
    api_url:
        description:
            - The URL for the SCM API.
            - If not specified, the value of the SCM_API_URL environment variable will be used.
        type: str
        required: false
    folder_id:
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
            - Mutually exclusive with I(folder_id).
        type: str
        required: false
    parent_folder_id:
        description:
            - If specified, only folders under this parent folder will be returned.
            - Ignored if I(folder_id) is specified.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - For authentication, you can set the C(SCM_API_KEY) and C(SCM_API_URL) environment variables
      instead of providing them as module options.
'''

EXAMPLES = r'''
- name: Get all folders
  cdot65.scm.folder_info:
  register: all_folders

- name: Get a specific folder by ID
  cdot65.scm.folder_info:
    folder_id: "12345678-1234-1234-1234-123456789012"
  register: folder_details

- name: Get folders with a specific name
  cdot65.scm.folder_info:
    name: "Network Objects"
  register: named_folders

- name: Get folders under a specific parent
  cdot65.scm.folder_info:
    parent_folder_id: "87654321-4321-4321-4321-210987654321"
  register: child_folders
'''

RETURN = r'''
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
        parent_folder_id:
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cdot65.scm.plugins.module_utils.scm import (
    scm_argument_spec,
    get_scm_client,
    handle_scm_error
)


def main():
    # Define the module argument specification
    module_args = scm_argument_spec()
    module_args.update(
        folder_id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        parent_folder_id=dict(type='str', required=False)
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[['folder_id', 'name']],
        supports_check_mode=True
    )

    # Get parameters
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    parent_folder_id = module.params.get('parent_folder_id')
    
    result = {
        'folders': []
    }

    try:
        # Initialize SCM client
        client = get_scm_client(module)
        
        # Get folder by ID if specified
        if folder_id:
            try:
                folder = client.folder.get_by_id(folder_id)
                if folder:
                    result['folders'] = [folder]
            except Exception as e:
                handle_scm_error(module, e)
        else:
            # List all folders
            folders = client.folder.list()
            
            # Filter by name if specified
            if name:
                folders = [f for f in folders if f.get('name') == name]
                
            # Filter by parent_folder_id if specified
            if parent_folder_id:
                folders = [f for f in folders if f.get('parent_folder_id') == parent_folder_id]
                
            result['folders'] = folders
    
    except Exception as e:
        handle_scm_error(module, e)
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()
