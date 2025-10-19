#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects.quarantined_devices import QuarantinedDevicesCreateModel

DOCUMENTATION = r"""
---
module: quarantined_device
short_description: Manage quarantined devices in Strata Cloud Manager (SCM)
description:
    - Add or remove devices from quarantine in Strata Cloud Manager using pan-scm-sdk.
    - Quarantined devices are identified by their host_id.
    - This is a global resource without folder/snippet/device containers.
    - No update operation is supported; quarantine is binary (present or absent).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    host_id:
        description:
            - Device host ID (primary identifier).
            - Required for all operations.
        type: str
        required: true
    serial_number:
        description:
            - Device serial number.
            - Optional field for additional device information.
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
            - Desired state of the quarantined device.
            - C(present) adds the device to quarantine.
            - C(absent) removes the device from quarantine.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - This is a global resource without folder/snippet/device containers.
    - No update operation is supported; quarantine is binary (present or absent).
    - Deletion uses host_id, not ID field.
"""

EXAMPLES = r"""
- name: Quarantine a device by host_id
  cdot65.scm.quarantined_device:
    host_id: "00000000-0000-0000-0000-000000000001"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Quarantine a device with serial number
  cdot65.scm.quarantined_device:
    host_id: "00000000-0000-0000-0000-000000000002"
    serial_number: "12345678"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Remove a device from quarantine
  cdot65.scm.quarantined_device:
    host_id: "00000000-0000-0000-0000-000000000001"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Ensure multiple devices are quarantined
  cdot65.scm.quarantined_device:
    host_id: "{{ item }}"
    scm_access_token: "{{ scm_access_token }}"
    state: present
  loop:
    - "00000000-0000-0000-0000-000000000003"
    - "00000000-0000-0000-0000-000000000004"
    - "00000000-0000-0000-0000-000000000005"
"""

RETURN = r"""
quarantined_device:
    description: Information about the quarantined device that was managed
    returned: on success
    type: dict
    contains:
        host_id:
            description: The device host ID
            type: str
            returned: always
            sample: "00000000-0000-0000-0000-000000000001"
        serial_number:
            description: The device serial number
            type: str
            returned: when applicable
            sample: "12345678"
"""


def main():
    module_args = dict(
        host_id=dict(type="str", required=True),
        serial_number=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "quarantined_device": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize device_quarantined boolean
        device_quarantined = False
        quarantined_obj = None

        # Check if device is already quarantined by host_id
        try:
            # List all quarantined devices with host_id filter
            quarantined_devices = client.quarantined_device.list(host_id=params.get("host_id"))

            # Check if we found the device
            if quarantined_devices:
                device_quarantined = True
                quarantined_obj = quarantined_devices[0]  # Should only be one match for a specific host_id
        except (ObjectNotPresentError, APIError):
            device_quarantined = False
            quarantined_obj = None

        # Add device to quarantine
        if params.get("state") == "present":
            if device_quarantined:
                # Device is already quarantined - no change needed
                result["quarantined_device"] = json.loads(quarantined_obj.model_dump_json(exclude_unset=True))
                result["changed"] = False
                module.exit_json(**result)
            else:
                # Create payload for quarantining the device
                create_payload = {k: params[k] for k in ["host_id", "serial_number"] if params.get(k) is not None}

                # Add device to quarantine
                if not module.check_mode:
                    # Quarantine the device
                    created = client.quarantined_device.create(create_payload)

                    # Return the quarantined device object
                    result["quarantined_device"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a quarantined device object (minimal info)
                    simulated = QuarantinedDevicesCreateModel(**create_payload)
                    result["quarantined_device"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Remove device from quarantine
        elif params.get("state") == "absent":
            if device_quarantined:
                if not module.check_mode:
                    # Delete by host_id (not by ID)
                    client.quarantined_device.delete(params.get("host_id"))

                # Mark as changed
                result["changed"] = True

                # Return the device info that was removed
                result["quarantined_device"] = json.loads(quarantined_obj.model_dump_json(exclude_unset=True))
                module.exit_json(**result)
            else:
                # Device is already not quarantined
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
