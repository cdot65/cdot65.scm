#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule  # type: ignore
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import HIPProfileCreateModel

DOCUMENTATION = r"""
---
module: hip_profile
short_description: Manage Host Information Profile (HIP) profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete HIP profiles in Strata Cloud Manager using pan-scm-sdk.
    - HIP profiles define security posture matching criteria that can be used in security policies.
    - Profiles reference HIP objects using match expressions with boolean logic (AND, OR, NOT).
    - HIP profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the HIP profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the HIP profile (UUID).
            - Used for lookup/deletion if provided.
        type: str
        required: false
    description:
        description:
            - Description for the HIP profile.
            - Maximum length is 255 characters.
        type: str
        required: false
    match:
        description:
            - Match expression for the HIP profile.
            - Uses boolean logic to reference HIP objects (e.g., '"is-win" and "is-firewall-enabled"').
            - Supports AND, OR, and NOT operators.
            - HIP object names must be enclosed in quotes within the expression.
            - Maximum length is 2048 characters.
        type: str
        required: false
    folder:
        description:
            - The folder in which the HIP profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the HIP profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the HIP profile is defined.
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
            - Desired state of the HIP profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - HIP profiles must be associated with exactly one container (folder, snippet, or device).
    - Match expressions must refer to existing HIP objects.
    - HIP object names in match expressions must be enclosed in quotes (e.g., '"object-name"').
    - Boolean operators (and, or, not) and parentheses can be used in match expressions.
"""

EXAMPLES = r"""
- name: Create a basic HIP profile with a simple match expression
  cdot65.scm.hip_profile:
    name: "windows-workstations"
    description: "Profile for Windows workstations"
    folder: "Security"
    match: '"is-win"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile with a complex match expression using AND logic
  cdot65.scm.hip_profile:
    name: "secure-workstations"
    description: "Profile for secured workstations"
    folder: "Security"
    match: '"is-win" and "is-firewall-enabled"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile with a complex match expression using OR logic
  cdot65.scm.hip_profile:
    name: "all-workstations"
    description: "Profile for all workstations"
    folder: "Security"
    match: '"is-win" or "is-mac"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile with a complex match expression using NOT logic
  cdot65.scm.hip_profile:
    name: "non-windows-devices"
    description: "All devices except Windows workstations"
    folder: "Security"
    match: 'not ("is-win")'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile with a complex match expression using parentheses
  cdot65.scm.hip_profile:
    name: "complex-security-profile"
    description: "Complex security profile with multiple conditions"
    folder: "Security"
    match: '("is-win" and "is-firewall-enabled") or ("is-mac" and "is-disk-encrypted")'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile in a snippet
  cdot65.scm.hip_profile:
    name: "snippet-profile"
    description: "Profile defined in a snippet"
    snippet: "Security"
    match: '"is-win" and "is-firewall-enabled"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a HIP profile on a device
  cdot65.scm.hip_profile:
    name: "device-profile"
    description: "Profile defined on a device"
    device: "firewall-01"
    match: '"is-win" and "is-firewall-enabled"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an existing HIP profile's match expression
  cdot65.scm.hip_profile:
    name: "secure-workstations"
    description: "Updated profile for secured workstations"
    folder: "Security"
    match: '"is-win" and "is-firewall-enabled" and "is-disk-encrypted"'
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a HIP profile by name
  cdot65.scm.hip_profile:
    name: "windows-workstations"
    folder: "Security"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a HIP profile by ID
  cdot65.scm.hip_profile:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
hip_profile:
    description: Information about the HIP profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The HIP profile ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The HIP profile name
            type: str
            returned: always
            sample: "windows-workstations"
        description:
            description: The HIP profile description
            type: str
            returned: when applicable
            sample: "Profile for Windows workstations"
        match:
            description: The match expression
            type: str
            returned: always
            sample: '"is-win" and "is-firewall-enabled"'
        folder:
            description: The folder containing the HIP profile
            type: str
            returned: when applicable
            sample: "Security"
        snippet:
            description: The snippet containing the HIP profile
            type: str
            returned: when applicable
            sample: "security-policy"
        device:
            description: The device containing the HIP profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        description=dict(type="str", required=False),
        match=dict(type="str", required=False),
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
            ["state", "present", ["name", "match"]],
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

    # Initialize results
    result = {"changed": False, "hip_profile": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize hip_exists boolean
        hip_exists = False
        hip_obj = None

        # Fetch a hip profile by ID if provided
        if params.get("id"):
            try:
                hip_obj = client.hip_profile.get(params.get("id"))
                if hip_obj:
                    hip_exists = True
            except ObjectNotPresentError:
                hip_exists = False
                hip_obj = None

        # Fetch hip profile by name if provided
        elif params.get("name"):
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
                    hip_obj = client.hip_profile.fetch(name=params.get("name"), **{container_type: container_name})
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

                # Check fields to update
                for field in ["description", "match", "folder", "snippet", "device"]:
                    if params.get(field) is not None and getattr(hip_obj, field, None) != params.get(field):
                        update_fields[field] = params.get(field)

                # Update if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            # Use model_copy for updates
                            update_model = hip_obj.model_copy(update=update_fields)
                            updated = client.hip_profile.update(update_model)
                            result["hip_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except (APIError, InvalidObjectError) as e:
                            module.fail_json(
                                msg=f"API Error updating HIP profile: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                                payload=update_fields,
                            )
                        except Exception as e:
                            module.fail_json(msg=f"Error updating HIP profile: {str(e)}", payload=update_fields)
                    else:
                        # In check mode, just show what would be updated
                        result["hip_profile"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["hip_profile"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload
                create_payload = {
                    "name": params.get("name"),
                    "match": params.get("match"),
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

                # Create a HIP profile
                if not module.check_mode:
                    try:
                        # Create a HIP profile
                        created = client.hip_profile.create(create_payload)
                        # Return the created HIP profile
                        result["hip_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error creating HIP profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error creating HIP profile: {str(e)}", payload=create_payload)
                else:
                    # Simulate a created object (minimal info)
                    simulated = HIPProfileCreateModel(**create_payload)
                    result["hip_profile"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete
        elif params.get("state") == "absent":
            if hip_exists:
                if not module.check_mode:
                    try:
                        client.hip_profile.delete(hip_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting HIP profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            id=hip_obj.id,
                        )
                    except Exception as e:
                        module.fail_json(msg=f"Error deleting HIP profile: {str(e)}", id=hip_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["hip_profile"] = json.loads(hip_obj.model_dump_json(exclude_unset=True))
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
