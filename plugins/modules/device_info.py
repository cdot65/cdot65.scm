#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: device_info
short_description: Get information about devices in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about devices in Strata Cloud Manager.
    - It can be used to get details about a specific device by ID or name, or to list all devices.
    - Supports filtering by device properties like type, model, and folder.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the device to retrieve (typically the serial number).
            - If specified, the module will return information about this specific device.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the device to retrieve.
            - If specified, the module will search for devices with this name.
            - Mutually exclusive with I(id).
        type: str
        required: false
    serial_number:
        description:
            - Device serial number.
            - This is typically the same as the ID, but provided as a separate field for clarity.
        type: str
        required: false
    model:
        description:
            - Filter devices by model (e.g., 'PA-VM').
        type: str
        required: false
    type:
        description:
            - Filter devices by type (e.g., 'vm', 'firewall', 'panorama').
        type: str
        required: false
    folder:
        description:
            - Filter devices by folder name.
        type: str
        required: false
    device_only:
        description:
            - If true, only show device-only entries.
        type: bool
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
    - This module uses the pan-scm-sdk for interacting with the SCM API.
    - Pagination is handled internally when retrieving large device lists.
"""

EXAMPLES = r"""
- name: Get all devices
  cdot65.scm.device_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_devices

- name: Get a specific device by ID (serial number)
  cdot65.scm.device_info:
    id: "0123456789"
    scm_access_token: "{{ scm_access_token }}"
  register: device_details

- name: Get a specific device by name
  cdot65.scm.device_info:
    name: "DC-FW01"
    scm_access_token: "{{ scm_access_token }}"
  register: named_device

- name: Get all VM-series firewalls
  cdot65.scm.device_info:
    model: "PA-VM"
    scm_access_token: "{{ scm_access_token }}"
  register: vm_devices

- name: Get devices in a specific folder
  cdot65.scm.device_info:
    folder: "Datacenter"
    scm_access_token: "{{ scm_access_token }}"
  register: datacenter_devices
"""

RETURN = r"""
devices:
    description: List of device resources
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The device ID (typically serial number)
            type: str
            returned: always
            sample: "0123456789"
        name:
            description: The device name
            type: str
            returned: always
            sample: "DC-FW01"
        serial_number:
            description: The device serial number
            type: str
            returned: always
            sample: "0123456789"
        model:
            description: The device model
            type: str
            returned: when applicable
            sample: "PA-VM"
        type:
            description: The device type
            type: str
            returned: when applicable
            sample: "vm"
        folder:
            description: The folder containing the device
            type: str
            returned: when applicable
            sample: "Datacenter"
        description:
            description: The device description
            type: str
            returned: when applicable
            sample: "Datacenter firewall"
        display_name:
            description: The device display name
            type: str
            returned: when applicable
            sample: "Datacenter Firewall"
        hostname:
            description: The device hostname
            type: str
            returned: when applicable
            sample: "fw01.example.com"
        is_connected:
            description: Connection status
            type: bool
            returned: when applicable
            sample: true
        connected_since:
            description: Timestamp when device connected
            type: str
            returned: when applicable
            sample: "2024-05-01T12:00:00.000Z"
        software_version:
            description: PAN-OS software version
            type: str
            returned: when applicable
            sample: "10.2.3"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        id=dict(type="str", required=False),
        serial_number=dict(type="str", required=False),
        model=dict(type="str", required=False),
        type=dict(type="str", required=False),
        device_only=dict(type="bool", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[["id", "name"]],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"devices": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Fetch a device by id
        if params.get("id"):
            try:
                device_obj = client.device.get(params.get("id"))
                if device_obj:
                    result["devices"] = [json.loads(device_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve device info: {e}")

        # Fetch a device by serial number
        elif params.get("serial_number"):
            try:
                device = client.device.fetch(name=params.get("serial_number"))
                if device:
                    result["devices"] = [json.loads(device.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve device info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}
            if params.get("model"):
                filter_params["model"] = params.get("model")
            if params.get("type"):
                filter_params["type"] = params.get("type")
            if params.get("device_only"):
                filter_params["device_only"] = params.get("device_only")

            # List devices with filters
            if filter_params:
                devices = client.device.list(**filter_params)
            else:
                devices = client.device.list()
            device_dicts = [json.loads(d.model_dump_json(exclude_unset=True)) for d in devices]

            result["devices"] = device_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve device info: {e}")


if __name__ == "__main__":
    main()
