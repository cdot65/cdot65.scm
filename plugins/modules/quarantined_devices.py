#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import QuarantinedDevicesCreateModel

DOCUMENTATION = r"""
---
module: quarantined_devices
short_description: Manage quarantined devices in Strata Cloud Manager (SCM)
description:
    - Create or delete quarantined devices in Strata Cloud Manager using pan-scm-sdk.
    - Supports all quarantined device attributes and robust idempotency.
    - Quarantined devices are managed at the SCM level and do not require container association.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    host_id:
        description:
            - Device host ID.
            - Required for both create and delete operations.
        type: str
        required: true
    serial_number:
        description:
            - Device serial number.
            - Optional field for providing additional device identification.
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
            - Desired state of the quarantined device.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Quarantined devices are identified by their host_id for deletion operations.
    - The update operation is not supported as the API only allows create/delete operations.
"""

EXAMPLES = r"""
- name: Create a quarantined device with host ID only
  cdot65.scm.quarantined_devices:
    host_id: "device-1234"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a quarantined device with both host ID and serial number
  cdot65.scm.quarantined_devices:
    host_id: "device-5678"
    serial_number: "PA-987654321"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a quarantined device by host ID
  cdot65.scm.quarantined_devices:
    host_id: "device-1234"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
quarantined_device:
    description: Information about the quarantined device that was managed
    returned: on success when state=present
    type: dict
    contains:
        host_id:
            description: The device host ID
            type: str
            returned: always
            sample: "device-1234"
        serial_number:
            description: The device serial number
            type: str
            returned: when configured
            sample: "PA-987654321"
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

        # Initialize device_exists boolean
        device_exists = False
        device_obj = None

        # Check if a quarantined device exists by host_id
        if params.get("host_id"):
            try:
                # List all quarantined devices filtered by host_id
                devices = client.quarantined_device.list(host_id=params.get("host_id"))
                if devices:
                    device_exists = True
                    device_obj = devices[0]  # Get the first matching device
            except (ObjectNotPresentError, InvalidObjectError):
                device_exists = False
                device_obj = None

        # Create or delete a quarantined device
        if params.get("state") == "present":
            if device_exists:
                # Device already exists, check if properties match
                needs_update = False

                # Check if serial_number differs
                if params.get("serial_number") is not None and getattr(device_obj, "serial_number", None) != params.get(
                    "serial_number"
                ):
                    needs_update = True

                if needs_update:
                    # Since update is not supported, we need to recreate
                    if not module.check_mode:
                        try:
                            # Delete existing device
                            client.quarantined_device.delete(params.get("host_id"))

                            # Create new device with updated properties
                            create_payload = {
                                "host_id": params.get("host_id"),
                            }
                            if params.get("serial_number") is not None:
                                create_payload["serial_number"] = params.get("serial_number")

                            created = client.quarantined_device.create(create_payload)
                            result["quarantined_device"] = json.loads(created.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid quarantined device object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error managing quarantined device: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, return what would be created
                        result["quarantined_device"] = {
                            "host_id": params.get("host_id"),
                            "serial_number": params.get("serial_number"),
                        }

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["quarantined_device"] = json.loads(device_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)
            else:
                # Create payload for new quarantined device
                create_payload = {
                    "host_id": params.get("host_id"),
                }
                if params.get("serial_number") is not None:
                    create_payload["serial_number"] = params.get("serial_number")

                # Create a quarantined device
                if not module.check_mode:
                    try:
                        # Create device
                        created = client.quarantined_device.create(create_payload)

                        # Return the created device
                        result["quarantined_device"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid quarantined device object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating quarantined device: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = QuarantinedDevicesCreateModel(**create_payload)
                    result["quarantined_device"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True
                module.exit_json(**result)

        # Delete a quarantined device
        elif params.get("state") == "absent":
            if device_exists:
                if not module.check_mode:
                    try:
                        # Delete using host_id
                        client.quarantined_device.delete(params.get("host_id"))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting quarantined device: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["quarantined_device"] = json.loads(device_obj.model_dump_json(exclude_unset=True))
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
    except Exception as e:  # noqa: BLE001
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
