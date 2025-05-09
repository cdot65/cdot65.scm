#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: folder
short_description: Manage folders in Strata Cloud Manager (SCM)
description:
    - This module creates, updates, and deletes folders in Strata Cloud Manager.
    - Folders are used to organize objects within the SCM hierarchy.
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
            - The ID of the folder to manage.
            - Required when I(state=absent) if I(name) is not specified.
            - Mutually exclusive with I(name) when used for identification.
        type: str
        required: false
    name:
        description:
            - The name of the folder.
            - Required when I(state=present).
            - Can be used for folder identification when I(state=absent) instead of I(folder_id).
        type: str
        required: false
    description:
        description:
            - A description for the folder.
        type: str
        required: false
    parent_folder_id:
        description:
            - The ID of the parent folder.
            - If not specified, the folder will be created at the root level.
        type: str
        required: false
    state:
        description:
            - The desired state of the folder.
        type: str
        required: false
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - For authentication, you can set the C(SCM_API_KEY) and C(SCM_API_URL) environment variables
      instead of providing them as module options.
'''

EXAMPLES = r'''
- name: Create a folder
  cdot65.scm.folder:
    name: "Network Objects"
    description: "Folder for network objects"
    state: present

- name: Create a subfolder
  cdot65.scm.folder:
    name: "Address Objects"
    description: "Folder for address objects"
    parent_folder_id: "{{ parent_folder_id }}"
    state: present

- name: Delete a folder by name
  cdot65.scm.folder:
    name: "Network Objects"
    state: absent

- name: Delete a folder by ID
  cdot65.scm.folder:
    folder_id: "12345678-1234-1234-1234-123456789012"
    state: absent
'''

RETURN = r'''
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
    handle_scm_error,
    is_resource_exists
)


def main():
    # Define the module argument specification
    module_args = scm_argument_spec()
    module_args.update(
        folder_id=dict(type='str', required=False),
        name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        parent_folder_id=dict(type='str', required=False),
        state=dict(type='str', required=False, choices=['present', 'absent'], default='present')
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[['name', 'folder_id']],
        required_if=[
            ['state', 'present', ['name']],
        ],
        supports_check_mode=True
    )

    # Get parameters
    state = module.params.get('state')
    folder_id = module.params.get('folder_id')
    name = module.params.get('name')
    description = module.params.get('description')
    parent_folder_id = module.params.get('parent_folder_id')
    
    result = {
        'changed': False,
        'folder': {}
    }

    try:
        # Initialize SCM client
        client = get_scm_client(module)
        
        # Check if folder exists
        exists, folder_data = is_resource_exists(client, 'folder', folder_id, name)
        
        if state == 'present':
            # Create or update folder
            if exists:
                # Folder exists, check if update is needed
                if folder_data:
                    need_update = False
                    
                    # Capture current folder ID
                    folder_id = folder_data.get('id')
                    
                    # Build update payload
                    update_payload = {}
                    
                    # Check if description needs to be updated
                    if description is not None and description != folder_data.get('description'):
                        update_payload['description'] = description
                        need_update = True
                    
                    # Check if parent_folder_id needs to be updated
                    current_parent = folder_data.get('parent_folder_id')
                    if parent_folder_id is not None and parent_folder_id != current_parent:
                        update_payload['parent_folder_id'] = parent_folder_id
                        need_update = True
                        
                    # Update folder if needed
                    if need_update:
                        if not module.check_mode:
                            updated_folder = client.folder.update(folder_id, **update_payload)
                            result['folder'] = updated_folder
                        result['changed'] = True
                    else:
                        result['folder'] = folder_data
            else:
                # Folder doesn't exist, create it
                if not module.check_mode:
                    create_payload = {
                        'name': name,
                    }
                    
                    if description is not None:
                        create_payload['description'] = description
                        
                    if parent_folder_id is not None:
                        create_payload['parent_folder_id'] = parent_folder_id
                        
                    new_folder = client.folder.create(**create_payload)
                    result['folder'] = new_folder
                
                result['changed'] = True
        
        elif state == 'absent':
            # Delete folder if it exists
            if exists:
                if not module.check_mode:
                    client.folder.delete(folder_data.get('id'))
                result['changed'] = True
                result['folder'] = folder_data
    
    except Exception as e:
        handle_scm_error(module, e)
    
    module.exit_json(**result)


if __name__ == '__main__':
    main()
