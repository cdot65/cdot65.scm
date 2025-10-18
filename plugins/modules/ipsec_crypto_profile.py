#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.network import IPsecCryptoProfileCreateModel

DOCUMENTATION = r"""
---
module: ipsec_crypto_profile
short_description: Manage IPsec crypto profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete IPsec crypto profiles in Strata Cloud Manager using pan-scm-sdk.
    - IPsec crypto profiles define encryption, authentication, and key exchange parameters for IPsec phase 2.
    - Supports all IPsec crypto profile attributes and robust idempotency.
    - IPsec crypto profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IPsec crypto profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
            - Must match pattern ^[0-9a-zA-Z._-]+$
        type: str
        required: false
    dh_group:
        description:
            - Diffie-Hellman group for perfect forward secrecy.
            - Default is group2.
        type: str
        required: false
        choices: ["no-pfs", "group1", "group2", "group5", "group14", "group19", "group20"]
        default: "group2"
    lifetime:
        description:
            - IPsec SA lifetime configuration.
            - Can specify in seconds, minutes, hours, or days.
            - Only one time unit should be specified.
            - Required for state=present.
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
    lifesize:
        description:
            - IPsec SA lifesize (data volume) configuration.
            - Can specify in KB, MB, GB, or TB.
            - Only one size unit should be specified.
        type: dict
        required: false
        suboptions:
            kb:
                description:
                    - Lifesize in kilobytes (1-65535).
                type: int
                required: false
            mb:
                description:
                    - Lifesize in megabytes (1-65535).
                type: int
                required: false
            gb:
                description:
                    - Lifesize in gigabytes (1-65535).
                type: int
                required: false
            tb:
                description:
                    - Lifesize in terabytes (1-65535).
                type: int
                required: false
    esp:
        description:
            - ESP (Encapsulating Security Payload) configuration.
            - Exactly one of esp or ah must be specified.
        type: dict
        required: false
        suboptions:
            encryption:
                description:
                    - List of ESP encryption algorithms.
                    - Required when esp is specified.
                type: list
                elements: str
                required: true
                choices:
                    - "des"
                    - "3des"
                    - "aes-128-cbc"
                    - "aes-192-cbc"
                    - "aes-256-cbc"
                    - "aes-128-gcm"
                    - "aes-256-gcm"
                    - "null"
            authentication:
                description:
                    - List of ESP authentication algorithms.
                    - Required when esp is specified.
                type: list
                elements: str
                required: true
                choices: ["md5", "sha1", "sha256", "sha384", "sha512"]
    ah:
        description:
            - AH (Authentication Header) configuration.
            - Exactly one of esp or ah must be specified.
        type: dict
        required: false
        suboptions:
            authentication:
                description:
                    - List of AH authentication algorithms.
                    - Required when ah is specified.
                type: list
                elements: str
                required: true
                choices: ["md5", "sha1", "sha256", "sha384", "sha512"]
    folder:
        description:
            - The folder in which the IPsec crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the IPsec crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the IPsec crypto profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IPsec crypto profile (UUID).
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
            - Desired state of the IPsec crypto profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - IPsec crypto profiles must be associated with exactly one container (folder, snippet, or device).
    - Exactly one security protocol (ESP or AH) must be specified for state=present.
    - Lifetime is required when creating a new profile.
"""

EXAMPLES = r"""
---
- name: Create basic IPsec crypto profile with ESP
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-default"
    dh_group: "group14"
    lifetime:
      hours: 1
    esp:
      encryption:
        - "aes-256-cbc"
        - "aes-128-cbc"
      authentication:
        - "sha256"
        - "sha384"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IPsec crypto profile with ESP-GCM
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-gcm"
    dh_group: "group20"
    lifetime:
      hours: 8
    esp:
      encryption:
        - "aes-256-gcm"
        - "aes-128-gcm"
      authentication:
        - "sha512"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IPsec crypto profile with AH
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-ah"
    dh_group: "group19"
    lifetime:
      minutes: 60
    ah:
      authentication:
        - "sha256"
        - "sha384"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IPsec crypto profile with lifesize limit
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-lifesize"
    dh_group: "group14"
    lifetime:
      hours: 24
    lifesize:
      gb: 10
    esp:
      encryption:
        - "aes-256-cbc"
      authentication:
        - "sha256"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IPsec crypto profile with no PFS
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-no-pfs"
    dh_group: "no-pfs"
    lifetime:
      hours: 1
    esp:
      encryption:
        - "aes-128-cbc"
      authentication:
        - "sha1"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update existing IPsec crypto profile
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-default"
    dh_group: "group20"
    lifetime:
      days: 1
    esp:
      encryption:
        - "aes-256-gcm"
      authentication:
        - "sha512"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete IPsec crypto profile by name
  cdot65.scm.ipsec_crypto_profile:
    name: "ipsec-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete IPsec crypto profile by ID
  cdot65.scm.ipsec_crypto_profile:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
ipsec_crypto_profile:
    description: Information about the IPsec crypto profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The IPsec crypto profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IPsec crypto profile name
            type: str
            returned: always
            sample: "ipsec-crypto-default"
        dh_group:
            description: Diffie-Hellman group
            type: str
            returned: always
            sample: "group14"
        lifetime:
            description: IPsec SA lifetime configuration
            type: dict
            returned: always
            sample: {"hours": 1}
        lifesize:
            description: IPsec SA lifesize configuration
            type: dict
            returned: when configured
            sample: {"gb": 10}
        esp:
            description: ESP configuration
            type: dict
            returned: when configured
            contains:
                encryption:
                    description: ESP encryption algorithms
                    type: list
                    sample: ["aes-256-cbc", "aes-128-cbc"]
                authentication:
                    description: ESP authentication algorithms
                    type: list
                    sample: ["sha256", "sha384"]
        ah:
            description: AH configuration
            type: dict
            returned: when configured
            contains:
                authentication:
                    description: AH authentication algorithms
                    type: list
                    sample: ["sha256", "sha384"]
        folder:
            description: The folder containing the IPsec crypto profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the IPsec crypto profile
            type: str
            returned: when applicable
            sample: "VPN-Config"
        device:
            description: The device containing the IPsec crypto profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        dh_group=dict(
            type="str",
            required=False,
            choices=["no-pfs", "group1", "group2", "group5", "group14", "group19", "group20"],
            default="group2",
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
        lifesize=dict(
            type="dict",
            required=False,
            options=dict(
                kb=dict(type="int", required=False),
                mb=dict(type="int", required=False),
                gb=dict(type="int", required=False),
                tb=dict(type="int", required=False),
            ),
        ),
        esp=dict(
            type="dict",
            required=False,
            options=dict(
                encryption=dict(
                    type="list",
                    elements="str",
                    required=True,
                    choices=[
                        "des",
                        "3des",
                        "aes-128-cbc",
                        "aes-192-cbc",
                        "aes-256-cbc",
                        "aes-128-gcm",
                        "aes-256-gcm",
                        "null",
                    ],
                ),
                authentication=dict(
                    type="list",
                    elements="str",
                    required=True,
                    choices=["md5", "sha1", "sha256", "sha384", "sha512"],
                ),
            ),
        ),
        ah=dict(
            type="dict",
            required=False,
            options=dict(
                authentication=dict(
                    type="list",
                    elements="str",
                    required=True,
                    choices=["md5", "sha1", "sha256", "sha384", "sha512"],
                ),
            ),
        ),
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
            ["state", "present", ["name", "lifetime"]],
            ["state", "absent", ["name", "id"], True],
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
            ["esp", "ah"],
        ],
        supports_check_mode=True,
    )

    # Custom validation
    params = module.params
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

        # Validate exactly one security protocol is specified
        if not params.get("esp") and not params.get("ah"):
            module.fail_json(msg="When state=present, exactly one of esp or ah must be specified")

        # Validate lifetime has only one time unit
        if params.get("lifetime"):
            lifetime_keys = [k for k, v in params["lifetime"].items() if v is not None]
            if len(lifetime_keys) > 1:
                module.fail_json(msg="Lifetime can only specify one time unit (seconds, minutes, hours, or days)")
            if len(lifetime_keys) == 0:
                module.fail_json(msg="Lifetime must specify at least one time unit")

        # Validate lifesize has only one size unit (if specified)
        if params.get("lifesize"):
            lifesize_keys = [k for k, v in params["lifesize"].items() if v is not None]
            if len(lifesize_keys) > 1:
                module.fail_json(msg="Lifesize can only specify one size unit (kb, mb, gb, or tb)")

    # Initialize results
    result = {"changed": False, "ipsec_crypto_profile": None}

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
                        profiles = client.ipsec_crypto_profile.list(folder=container_name)
                    elif container_type == "snippet":
                        profiles = client.ipsec_crypto_profile.list(snippet=container_name)
                    elif container_type == "device":
                        profiles = client.ipsec_crypto_profile.list(device=container_name)

                    # Find matching profile by name
                    for profile in profiles:
                        if profile.name == params.get("name"):
                            profile_obj = profile
                            profile_exists = True
                            break
                except Exception as e:
                    module.fail_json(
                        msg=f"Error listing IPsec crypto profiles: {str(e)}",
                        error_code=getattr(e, "error_code", None),
                        details=getattr(e, "details", None),
                    )

            # If specified by ID, try to get it directly
            elif params.get("id"):
                try:
                    profile_obj = client.ipsec_crypto_profile.get(params.get("id"))
                    if profile_obj:
                        profile_exists = True
                except Exception as e:
                    # Skip if object not found, but fail on other errors
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error retrieving IPsec crypto profile by ID: {str(e)}",
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
                    "dh_group",
                    "lifetime",
                    "lifesize",
                    "esp",
                    "ah",
                    "folder",
                    "snippet",
                    "device",
                ]:
                    if params.get(field) is not None:
                        current_value = getattr(profile_obj, field, None)
                        # Handle dict comparisons
                        if field in ["lifetime", "lifesize", "esp", "ah"]:
                            if params.get(field) != current_value:
                                update_fields[field] = params.get(field)
                        # Handle simple field comparisons
                        elif current_value != params.get(field):
                            update_fields[field] = params.get(field)

                # Update the profile if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = profile_obj.model_copy(update=update_fields)
                            updated = client.ipsec_crypto_profile.update(update_model)
                            result["ipsec_crypto_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid IPsec crypto profile object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating IPsec crypto profile: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, return existing object with projected changes
                        result["ipsec_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["ipsec_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new profile
                create_payload = {}

                # Add parameters
                for k in ["name", "dh_group", "lifetime", "lifesize", "esp", "ah"]:
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
                        created = client.ipsec_crypto_profile.create(create_payload)
                        result["ipsec_crypto_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid IPsec crypto profile object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating IPsec crypto profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = IPsecCryptoProfileCreateModel(**create_payload)
                    result["ipsec_crypto_profile"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        # Handle absent state - delete the profile
        elif params.get("state") == "absent":
            if profile_exists:
                if not module.check_mode:
                    try:
                        client.ipsec_crypto_profile.delete(profile_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting IPsec crypto profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["ipsec_crypto_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
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
