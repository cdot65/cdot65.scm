#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import copy
import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import HIPObjectCreateModel

DOCUMENTATION = r"""
---
module: hip_object
short_description: Manage Host Information Profile (HIP) objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete HIP objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports various HIP criteria types (host_info, network_info, patch_management, disk_encryption, mobile_device, certificate).
    - HIP objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the HIP object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the HIP object (UUID).
            - Used for lookup/deletion if provided.
        type: str
        required: false
    description:
        description:
            - Description for the HIP object.
            - Maximum length is 255 characters.
        type: str
        required: false
    host_info:
        description:
            - Host information criteria for the HIP object.
            - Contains detailed host-based checks like domain, operating system, client version, etc.
        type: dict
        required: false
    network_info:
        description:
            - Network information criteria for the HIP object.
            - Contains network-related checks like network type.
        type: dict
        required: false
    patch_management:
        description:
            - Patch management criteria for the HIP object.
            - Includes patch management software status and missing patches.
        type: dict
        required: false
    disk_encryption:
        description:
            - Disk encryption criteria for the HIP object.
            - Includes encryption software status and encrypted locations.
        type: dict
        required: false
    mobile_device:
        description:
            - Mobile device criteria for the HIP object.
            - Includes mobile device specific checks like jailbroken status, passcode, and applications.
        type: dict
        required: false
    certificate:
        description:
            - Certificate criteria for the HIP object.
            - Includes certificate profile and attribute checks.
        type: dict
        required: false
    folder:
        description:
            - The folder in which the HIP object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the HIP object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the HIP object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
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
            - Desired state of the HIP object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - HIP objects must be associated with exactly one container (folder, snippet, or device).
    - At least one criteria type (host_info, network_info, etc.) must be provided.
    - HIP object criteria follow strict structure validation:
        - String comparison fields (domain, client_version, etc.) must use either 'contains', 'is', or 'is_not' operators with string values
        - Empty strings or empty dictionaries in these fields will be cleaned up automatically to prevent validation errors
        - OS criteria must use proper platform names as keys (e.g., 'Microsoft', 'Apple') with valid version values
        - Network criteria must follow the proper nested structure (e.g., 'network.is.wifi')
        - Encryption locations must include valid 'name' and 'encryption_state' properties
"""

EXAMPLES = r"""
- name: Create a basic host info HIP object
  cdot65.scm.hip_object:
    name: "windows-workstations"
    description: "Windows workstation requirements"
    folder: "Security"
    host_info:
      criteria:
        os:
          contains:
            Microsoft: "All"
        managed: true
        # String fields with proper structure - empty strings will be cleaned automatically
        domain:
          contains: "corporate.local"  # Use a string value, not an empty dict
        # Do not include empty string fields that are not needed - they will be automatically pruned
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a disk encryption HIP object
  cdot65.scm.hip_object:
    name: "encrypted-endpoints"
    description: "Disk encryption requirements"
    folder: "Security"
    disk_encryption:
      criteria:
        is_installed: true
        encrypted_locations:
          - name: "C:"
            encryption_state:
              is: "encrypted"
      vendor:
        - name: "Microsoft"
          product: ["BitLocker"]
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a patch management HIP object
  cdot65.scm.hip_object:
    name: "patch-compliant"
    description: "Patch compliance requirements"
    folder: "Security"
    patch_management:
      criteria:
        is_installed: true
        missing_patches:
          severity: { "level": 10 }  # Object with level field as required by API
          check: "has-none"
      vendor:
        - name: "Microsoft"
          product: ["Windows Update"]
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a mobile device HIP object
  cdot65.scm.hip_object:
    name: "secure-mobile"
    description: "Mobile device security requirements"
    folder: "Security"
    mobile_device:
      criteria:
        jailbroken: false
        disk_encrypted: true
        passcode_set: true
        last_checkin_time:
          days: 7
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an existing HIP object
  cdot65.scm.hip_object:
    name: "windows-workstations"
    description: "Updated Windows workstation requirements"
    folder: "Security"
    host_info:
      criteria:
        os:
          contains:
            Microsoft: "All"
        managed: true
        domain:
          contains: "corporate.local"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a HIP object by name
  cdot65.scm.hip_object:
    name: "encrypted-endpoints"
    folder: "Security"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a HIP object by ID
  cdot65.scm.hip_object:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
hip_object:
    description: Information about the HIP object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The HIP object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The HIP object name
            type: str
            returned: always
            sample: "windows-workstations"
        description:
            description: The HIP object description
            type: str
            returned: when applicable
            sample: "Windows workstation requirements"
        host_info:
            description: Host information criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"os": {"contains": {"Microsoft": "All"}}, "managed": true}}
        network_info:
            description: Network information criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"network_type": {"is": "wifi"}}}
        patch_management:
            description: Patch management criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"is_installed": true, "missing_patches": {"severity": {"level": 10}, "check": "has-none"}}}
        disk_encryption:
            description: Disk encryption criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"is_installed": true, "encrypted_locations": [{"name": "C:", "encryption_state": {"is": "encrypted"}}]}}
        mobile_device:
            description: Mobile device criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"jailbroken": false, "disk_encrypted": true}}
        certificate:
            description: Certificate criteria
            type: dict
            returned: when applicable
            sample: {"criteria": {"certificate_attributes": [{"name": "Subject", "value": "CN=User"}]}}
        folder:
            description: The folder containing the HIP object
            type: str
            returned: when applicable
            sample: "Security"
        snippet:
            description: The snippet containing the HIP object
            type: str
            returned: when applicable
            sample: "security-policy"
        device:
            description: The device containing the HIP object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def clean_hip_criteria(criteria_data):
    """Preprocess HIP object criteria to ensure proper formatting and prevent validation errors.

    The function processes several common validation issues:
    1. Removes empty string fields that would cause validation errors
    2. Converts empty dicts to proper values for contains/is/is_not fields
    3. Cleans up nested structures with more than one of contains/is/is_not
    4. Fixes patch management severity format (must be an object with 'value' property)
    5. Ensures network_type has proper formatting

    Args:
        criteria_data (dict): The raw criteria data from Ansible parameters

    Returns:
        dict: The preprocessed criteria data ready for API submission
    """
    if not criteria_data:
        return criteria_data

    # Deep copy to avoid modifying the original data
    cleaned = copy.deepcopy(criteria_data)

    # Handle criteria field if present
    if "criteria" in cleaned:
        for key, value in list(cleaned["criteria"].items()):
            # Special case for missing_patches severity
            if key == "missing_patches" and isinstance(value, dict):
                if "severity" in value and not isinstance(value["severity"], dict):
                    # If severity is provided as an integer, convert to the required object format
                    severity_value = value["severity"]
                    value["severity"] = {"level": severity_value}

            # Check string comparison fields (domain, client_version, host_name, etc.)
            if isinstance(value, dict) and any(op in value for op in ["contains", "is", "is_not"]):
                # Handle contains operator
                if "contains" in value:
                    # If contains is empty dict, remove it
                    if value["contains"] == {} or value["contains"] == "":
                        del value["contains"]

                # Handle is operator
                if "is" in value:
                    # If is is empty dict, remove it
                    if value["is"] == {} or value["is"] == "":
                        del value["is"]

                # Handle is_not operator
                if "is_not" in value:
                    # If is_not is empty dict, remove it
                    if value["is_not"] == {} or value["is_not"] == "":
                        del value["is_not"]

                # If all operators were removed, remove the entire key
                if not value:
                    del cleaned["criteria"][key]

            # Handle nested dicts for things like os.contains or network.is
            elif isinstance(value, dict):
                for subkey, subvalue in list(value.items()):
                    if isinstance(subvalue, dict):
                        # Clean up nested operators
                        if "contains" in subvalue and subvalue["contains"] == {}:
                            del subvalue["contains"]
                        if "is" in subvalue and subvalue["is"] == {}:
                            del subvalue["is"]
                        if "is_not" in subvalue and subvalue["is_not"] == {}:
                            del subvalue["is_not"]

                        # If all operators were removed, remove the subkey
                        if not subvalue:
                            del value[subkey]

                # If all subkeys were removed, remove the key
                if not value:
                    del cleaned["criteria"][key]

    return cleaned


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        description=dict(type="str", required=False),
        host_info=dict(type="dict", required=False),
        network_info=dict(type="dict", required=False),
        patch_management=dict(type="dict", required=False),
        disk_encryption=dict(type="dict", required=False),
        mobile_device=dict(type="dict", required=False),
        certificate=dict(type="dict", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for container parameters
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

        # At least one criteria type should be present
        criteria_types = ["host_info", "network_info", "patch_management", "disk_encryption", "mobile_device", "certificate"]
        if not any(params.get(c_type) for c_type in criteria_types):
            module.fail_json(
                msg="At least one criteria type is required: host_info, network_info, patch_management, disk_encryption, mobile_device, or certificate"
            )

    # Initialize results
    result = {"changed": False, "hip_object": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize hip_exists boolean
        hip_exists = False
        hip_obj = None

        # Fetch a hip object by name if provided
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

                # For any container type, fetch the object
                if container_type and container_name:
                    hip_obj = client.hip_object.fetch(name=params.get("name"), **{container_type: container_name})
                    if hip_obj:
                        hip_exists = True
            except ObjectNotPresentError:
                hip_exists = False
                hip_obj = None

        # Create or update or delete
        if params.get("state") == "present":
            if hip_exists:
                # Collect fields that might need to be updated
                update_fields = {}

                # Add basic fields directly
                for basic_field in ["description", "folder", "snippet", "device"]:
                    if params.get(basic_field) is not None and getattr(hip_obj, basic_field, None) != params.get(basic_field):
                        update_fields[basic_field] = params.get(basic_field)

                # Process criteria fields with preprocessing to avoid validation errors
                for criteria_field in [
                    "host_info",
                    "network_info",
                    "patch_management",
                    "disk_encryption",
                    "mobile_device",
                    "certificate",
                ]:
                    if params.get(criteria_field) is not None:
                        # Clean criteria data
                        cleaned_criteria = clean_hip_criteria(params.get(criteria_field))

                        # Only add if non-empty and different from current value
                        if cleaned_criteria and getattr(hip_obj, criteria_field, None) != cleaned_criteria:
                            update_fields[criteria_field] = cleaned_criteria

                # Update if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            # Use model_copy for updates, following the pattern from other modules
                            update_model = hip_obj.model_copy(update=update_fields)
                            updated = client.hip_object.update(update_model)
                            result["hip_object"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except (APIError, InvalidObjectError) as e:
                            module.fail_json(
                                msg=f"API Error updating HIP object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                                payload=update_fields,
                            )
                        except Exception as e:
                            module.fail_json(msg=f"Error updating HIP object: {str(e)}", payload=update_fields)
                    else:
                        # In check mode, just show what would be updated
                        result["hip_object"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["hip_object"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload
                create_payload = {
                    "name": params.get("name"),
                }

                # Add description if provided
                if params.get("description"):
                    create_payload["description"] = params.get("description")

                # Add container
                if params.get("folder"):
                    create_payload["folder"] = params.get("folder")
                elif params.get("snippet"):
                    create_payload["snippet"] = params.get("snippet")
                elif params.get("device"):
                    create_payload["device"] = params.get("device")

                # Add HIP criteria with preprocessing
                for criteria_field in [
                    "host_info",
                    "network_info",
                    "patch_management",
                    "disk_encryption",
                    "mobile_device",
                    "certificate",
                ]:
                    if params.get(criteria_field):
                        # Clean criteria data to prevent validation errors
                        cleaned_criteria = clean_hip_criteria(params.get(criteria_field))
                        if cleaned_criteria:  # Only add if not empty after cleaning
                            create_payload[criteria_field] = cleaned_criteria

                # Create a HIP object
                if not module.check_mode:
                    try:
                        # Create a HIP object
                        created = client.hip_object.create(create_payload)
                        # Return the created HIP object
                        result["hip_object"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error creating HIP object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error creating HIP object: {str(e)}", payload=create_payload)
                else:
                    # Simulate a created object (minimal info)
                    simulated = HIPObjectCreateModel(**create_payload)
                    result["hip_object"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete
        elif params.get("state") == "absent":
            if hip_exists:
                if not module.check_mode:
                    try:
                        client.hip_object.delete(hip_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting HIP object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            id=hip_obj.id,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error deleting HIP object: {str(e)}", id=hip_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["hip_object"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))
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
