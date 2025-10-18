#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError

DOCUMENTATION = r"""
---
module: quarantined_device_info
short_description: Get information about quarantined devices in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about quarantined devices in Strata Cloud Manager.
    - It can be used to get details about all quarantined devices or filter by specific criteria.
    - Supports filtering by host_id or serial_number.
    - This is a global resource with no folder/snippet/device association.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    host_id:
        description:
            - Filter quarantined devices by device host ID.
            - If specified, the module will return only devices matching this host ID.
        type: str
        required: false
    serial_number:
        description:
            - Filter quarantined devices by device serial number.
            - If specified, the module will return only devices matching this serial number.
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
    - Quarantined devices are global resources and do not belong to folders, snippets, or devices.
    - All filter parameters are optional - you can retrieve all quarantined devices by not specifying any filters.
"""

EXAMPLES = r"""
- name: Get all quarantined devices
  cdot65.scm.quarantined_device_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_quarantined

- name: Get quarantined device by host ID
  cdot65.scm.quarantined_device_info:
    host_id: "00000000-0000-0000-0000-000000000000"
    scm_access_token: "{{ scm_access_token }}"
  register: device_by_host_id

- name: Get quarantined devices by serial number
  cdot65.scm.quarantined_device_info:
    serial_number: "012345678900"
    scm_access_token: "{{ scm_access_token }}"
  register: device_by_serial

- name: Filter quarantined devices and display results
  cdot65.scm.quarantined_device_info:
    host_id: "00000000-0000-0000-0000-000000000000"
    scm_access_token: "{{ scm_access_token }}"
  register: result

- name: Display quarantined device information
  ansible.builtin.debug:
    msg: "Found {{ result.quarantined_devices | length }} quarantined device(s)"
"""

RETURN = r"""
quarantined_devices:
    description: List of quarantined device objects
    returned: always
    type: list
    elements: dict
    contains:
        host_id:
            description: The device host ID
            type: str
            returned: always
            sample: "00000000-0000-0000-0000-000000000000"
        serial_number:
            description: The device serial number
            type: str
            returned: when applicable
            sample: "012345678900"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        host_id=dict(type="str", required=False),
        serial_number=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"quarantined_devices": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Prepare filter parameters for the SDK
        filter_params = {}

        # Add optional filters
        if params.get("host_id"):
            filter_params["host_id"] = params.get("host_id")

        if params.get("serial_number"):
            filter_params["serial_number"] = params.get("serial_number")

        # List quarantined devices with filters (or all if no filters)
        quarantined_devices = client.quarantined_device.list(**filter_params)

        # Convert to a list of dicts
        device_dicts = [json.loads(d.model_dump_json(exclude_unset=True)) for d in quarantined_devices]

        # Add to results
        result["quarantined_devices"] = device_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve quarantined device info: {e}")


if __name__ == "__main__":
    main()
