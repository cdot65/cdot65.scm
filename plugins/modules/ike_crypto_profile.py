#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.network import IKECryptoProfileCreateModel

DOCUMENTATION = r"""
---
module: ike_crypto_profile
short_description: Manage IKE crypto profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete IKE crypto profiles in Strata Cloud Manager using pan-scm-sdk.
    - IKE crypto profiles define encryption, authentication, and key exchange parameters for IKE phase 1.
    - Supports all IKE crypto profile attributes and robust idempotency.
    - IKE crypto profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IKE crypto profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
            - Must match pattern ^[0-9a-zA-Z._-]+$
        type: str
        required: false
    hash:
        description:
            - List of hash algorithms for IKE authentication.
            - Required for state=present.
        type: list
        elements: str
        required: false
        choices: ["md5", "sha1", "sha256", "sha384", "sha512"]
    encryption:
        description:
            - List of encryption algorithms for IKE.
            - Required for state=present.
        type: list
        elements: str
        required: false
        choices:
            - "des"
            - "3des"
            - "aes-128-cbc"
            - "aes-192-cbc"
            - "aes-256-cbc"
            - "aes-128-gcm"
            - "aes-256-gcm"
    dh_group:
        description:
            - List of Diffie-Hellman groups for key exchange.
            - Required for state=present.
        type: list
        elements: str
        required: false
        choices: ["group1", "group2", "group5", "group14", "group19", "group20"]
    lifetime:
        description:
            - IKE SA lifetime configuration.
            - Can specify in seconds, minutes, hours, or days.
            - Only one time unit should be specified.
        type: dict
        required: false
        suboptions:
            seconds:
                description:
                    - Lifetime in seconds (180-65535).
                type: int
                required: false
            minutes:
                description:
                    - Lifetime in minutes (3-65535).
                type: int
                required: false
            hours:
                description:
                    - Lifetime in hours (1-65535).
                type: int
                required: false
            days:
                description:
                    - Lifetime in days (1-365).
                type: int
                required: false
    authentication_multiple:
        description:
            - IKEv2 SA reauthentication interval (0-50).
            - Default is 0 (disabled).
        type: int
        required: false
        default: 0
    folder:
        description:
            - The folder in which the IKE crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the IKE crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the IKE crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IKE crypto profile (UUID).
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
            - Desired state of the IKE crypto profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - IKE crypto profiles must be associated with exactly one container (folder, snippet, or device).
    - Hash, encryption, and DH group algorithms are required when creating a new profile.
"""

EXAMPLES = r"""
---
- name: Create basic IKE crypto profile
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-default"
    hash:
      - "sha256"
      - "sha384"
    encryption:
      - "aes-256-cbc"
      - "aes-128-cbc"
    dh_group:
      - "group14"
      - "group19"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE crypto profile with custom lifetime
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-8hours"
    hash:
      - "sha256"
    encryption:
      - "aes-256-gcm"
    dh_group:
      - "group20"
    lifetime:
      hours: 8
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE crypto profile with reauthentication
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-reauth"
    hash:
      - "sha384"
      - "sha512"
    encryption:
      - "aes-256-gcm"
    dh_group:
      - "group19"
      - "group20"
    lifetime:
      hours: 24
    authentication_multiple: 3
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE crypto profile in snippet
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-snippet"
    hash:
      - "sha256"
    encryption:
      - "aes-128-gcm"
    dh_group:
      - "group14"
    snippet: "VPN-Config"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update existing IKE crypto profile
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-default"
    hash:
      - "sha512"
    encryption:
      - "aes-256-gcm"
    dh_group:
      - "group20"
    lifetime:
      days: 1
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete IKE crypto profile by name
  cdot65.scm.ike_crypto_profile:
    name: "ike-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete IKE crypto profile by ID
  cdot65.scm.ike_crypto_profile:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
ike_crypto_profile:
    description: Information about the IKE crypto profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The IKE crypto profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IKE crypto profile name
            type: str
            returned: always
            sample: "ike-crypto-default"
        hash:
            description: List of hash algorithms
            type: list
            returned: always
            sample: ["sha256", "sha384"]
        encryption:
            description: List of encryption algorithms
            type: list
            returned: always
            sample: ["aes-256-cbc", "aes-128-cbc"]
        dh_group:
            description: List of Diffie-Hellman groups
            type: list
            returned: always
            sample: ["group14", "group19"]
        lifetime:
            description: IKE SA lifetime configuration
            type: dict
            returned: when configured
            sample: {"hours": 8}
        authentication_multiple:
            description: IKEv2 SA reauthentication interval
            type: int
            returned: always
            sample: 0
        folder:
            description: The folder containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "VPN-Config"
        device:
            description: The device containing the IKE crypto profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        hash=dict(
            type="list",
            elements="str",
            required=False,
            choices=["md5", "sha1", "sha256", "sha384", "sha512"],
        ),
        encryption=dict(
            type="list",
            elements="str",
            required=False,
            choices=[
                "des",
                "3des",
                "aes-128-cbc",
                "aes-192-cbc",
                "aes-256-cbc",
                "aes-128-gcm",
                "aes-256-gcm",
            ],
        ),
        dh_group=dict(
            type="list",
            elements="str",
            required=False,
            choices=["group1", "group2", "group5", "group14", "group19", "group20"],
        ),
        lifetime=dict(
            type="dict",
            required=False,
            options=dict(
                seconds=dict(type="int", required=False),
                minutes=dict(type="int", required=False),
                hours=dict(type="int", required=False),
                days=dict(type="int", required=False),
            ),
        ),
        authentication_multiple=dict(type="int", required=False, default=0),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "hash", "encryption", "dh_group"]],
            ["state", "absent", ["name", "id"], True],
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Custom validation
    params = module.params
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

        # Validate lifetime has only one time unit
        if params.get("lifetime"):
            lifetime_keys = [k for k, v in params["lifetime"].items() if v is not None]
            if len(lifetime_keys) > 1:
                module.fail_json(msg="Lifetime can only specify one time unit (seconds, minutes, hours, or days)")

    # Initialize results
    result = {"changed": False, "ike_crypto_profile": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize profile_exists boolean
        profile_exists = False
        profile_obj = None

        # Fetch profile by name or id
        if params.get("name") or params.get("id"):
            # Determine container type and name
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

            # Attempt to find the profile by listing and filtering
            if params.get("name") and container_type and container_name:
                try:
                    # Use list method
                    if container_type == "folder":
                        profiles = client.ike_crypto_profile.list(folder=container_name)
                    elif container_type == "snippet":
                        profiles = client.ike_crypto_profile.list(snippet=container_name)
                    elif container_type == "device":
                        profiles = client.ike_crypto_profile.list(device=container_name)

                    # Find matching profile by name
                    for profile in profiles:
                        if profile.name == params.get("name"):
                            profile_obj = profile
                            profile_exists = True
                            break
                except Exception as e:
                    module.fail_json(
                        msg=f"Error listing IKE crypto profiles: {str(e)}",
                        error_code=getattr(e, "error_code", None),
                        details=getattr(e, "details", None),
                    )

            # If specified by ID, try to get it directly
            elif params.get("id"):
                try:
                    profile_obj = client.ike_crypto_profile.get(params.get("id"))
                    if profile_obj:
                        profile_exists = True
                except Exception as e:
                    # Skip if object not found, but fail on other errors
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error retrieving IKE crypto profile by ID: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

        # Create or update or delete profile
        if params.get("state") == "present":
            if profile_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Basic fields
                for field in [
                    "name",
                    "hash",
                    "encryption",
                    "dh_group",
                    "lifetime",
                    "authentication_multiple",
                    "folder",
                    "snippet",
                    "device",
                ]:
                    if params.get(field) is not None:
                        current_value = getattr(profile_obj, field, None)
                        # Handle lifetime comparison (dict)
                        if field == "lifetime":
                            if params.get(field) != current_value:
                                update_fields[field] = params.get(field)
                        # Handle list comparisons (sort for consistent comparison)
                        elif field in ["hash", "encryption", "dh_group"]:
                            current_sorted = sorted(current_value) if current_value else []
                            new_sorted = sorted(params.get(field)) if params.get(field) else []
                            if current_sorted != new_sorted:
                                update_fields[field] = params.get(field)
                        # Handle simple field comparisons
                        elif current_value != params.get(field):
                            update_fields[field] = params.get(field)

                # Update the profile if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = profile_obj.model_copy(update=update_fields)
                            updated = client.ike_crypto_profile.update(update_model)
                            result["ike_crypto_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid IKE crypto profile object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating IKE crypto profile: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, return existing object with projected changes
                        result["ike_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["ike_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new profile
                create_payload = {}

                # Add parameters
                for k in ["name", "hash", "encryption", "dh_group", "lifetime", "authentication_multiple"]:
                    if params.get(k) is not None:
                        create_payload[k] = params[k]

                # Add container parameter
                if params.get("folder"):
                    create_payload["folder"] = params["folder"]
                elif params.get("snippet"):
                    create_payload["snippet"] = params["snippet"]
                elif params.get("device"):
                    create_payload["device"] = params["device"]

                # Create profile object
                if not module.check_mode:
                    try:
                        created = client.ike_crypto_profile.create(create_payload)
                        result["ike_crypto_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid IKE crypto profile object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating IKE crypto profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = IKECryptoProfileCreateModel(**create_payload)
                    result["ike_crypto_profile"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        # Handle absent state - delete the profile
        elif params.get("state") == "absent":
            if profile_exists:
                if not module.check_mode:
                    try:
                        client.ike_crypto_profile.delete(profile_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting IKE crypto profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["ike_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
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
