#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import Scm as ScmClient
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.security import DecryptionProfileCreateModel

DOCUMENTATION = r"""
---
module: decryption_profile
short_description: Manage Decryption profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete Decryption security profiles in Strata Cloud Manager using pan-scm-sdk.
    - Decryption profiles define SSL/TLS decryption settings for forward proxy, inbound proxy, and no proxy scenarios.
    - Supports SSL protocol settings, certificate validation, and cipher suite configuration.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the Decryption profile.
            - Required for both state=present and state=absent.
        type: str
        required: false
    ssl_forward_proxy:
        description:
            - SSL Forward Proxy settings as a dictionary.
            - Controls certificate handling and TLS options for forward proxy.
        type: dict
        required: false
    ssl_inbound_proxy:
        description:
            - SSL Inbound Proxy settings as a dictionary.
            - Controls certificate handling for inbound proxy connections.
        type: dict
        required: false
    ssl_no_proxy:
        description:
            - SSL No Proxy settings as a dictionary.
            - Controls certificate validation when not proxying.
        type: dict
        required: false
    ssl_protocol_settings:
        description:
            - SSL Protocol settings as a dictionary.
            - Controls allowed TLS versions, cipher suites, and algorithms.
        type: dict
        required: false
    folder:
        description:
            - The folder in which the resource is defined.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the resource is defined.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the resource is defined.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the Decryption profile (UUID).
            - Used for lookup/deletion if provided.
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
            - Desired state of the Decryption profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided for state=present.
    - Complex nested structures are supported via dictionary parameters.
"""

EXAMPLES = r"""
- name: Create a basic Decryption profile with SSL Forward Proxy
  cdot65.scm.decryption_profile:
    name: "Example-Basic-Decryption"
    ssl_forward_proxy:
      auto_include_altname: false
      block_client_cert: false
      block_expired_certificate: true
      block_untrusted_issuer: true
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with SSL protocol settings
  cdot65.scm.decryption_profile:
    name: "Example-Protocol-Settings"
    ssl_protocol_settings:
      min_version: "tls1-2"
      max_version: "tls1-3"
      auth_algo_md5: false
      auth_algo_sha1: false
      auth_algo_sha256: true
      auth_algo_sha384: true
      enc_algo_3des: false
      enc_algo_rc4: false
      enc_algo_aes_128_cbc: true
      enc_algo_aes_256_cbc: true
      enc_algo_aes_128_gcm: true
      enc_algo_aes_256_gcm: true
      enc_algo_chacha20_poly1305: true
      keyxchg_algo_rsa: true
      keyxchg_algo_dhe: true
      keyxchg_algo_ecdhe: true
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with SSL Inbound Proxy
  cdot65.scm.decryption_profile:
    name: "Example-Inbound-Proxy"
    ssl_inbound_proxy:
      block_if_no_resource: true
      block_unsupported_cipher: true
      block_unsupported_version: true
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with SSL No Proxy
  cdot65.scm.decryption_profile:
    name: "Example-No-Proxy"
    ssl_no_proxy:
      block_expired_certificate: true
      block_untrusted_issuer: true
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete Decryption profile
  cdot65.scm.decryption_profile:
    name: "Old-Profile"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
changed:
    description: A boolean that indicates if a change was made.
    returned: always
    type: bool
msg:
    description: A message describing the change, if any.
    returned: always
    type: str
decryption_profile:
    description: The created, updated, or deleted Decryption profile.
    returned: when state=present
    type: dict
    sample:
        id: "123e4567-e89b-12d3-a456-426655440000"
        name: "Example-Basic-Decryption"
        folder: "Texas"
        ssl_forward_proxy:
          auto_include_altname: false
          block_client_cert: false
          block_expired_certificate: true
          block_untrusted_issuer: true
"""


def main():
    """Main module execution."""
    module_args = dict(
        name=dict(type="str", required=False),
        ssl_forward_proxy=dict(type="dict", required=False),
        ssl_inbound_proxy=dict(type="dict", required=False),
        ssl_no_proxy=dict(type="dict", required=False),
        ssl_protocol_settings=dict(type="dict", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
    )

    result = {
        "changed": False,
        "msg": "",
        "decryption_profile": {},
    }

    # Get module parameters
    params = module.params
    state = params["state"]
    scm_access_token = params["scm_access_token"]
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"

    # Initialize the SCM client with bearer token
    try:
        client = ScmClient(access_token=scm_access_token, api_base_url=api_url)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {e!s}")

    # Determine container type and name
    container_type = None
    container_name = None
    for ctype in ["folder", "snippet", "device"]:
        if params.get(ctype):
            container_type = ctype
            container_name = params[ctype]
            break

    # Build the lookup parameters
    lookup_params = {}
    if container_type and container_name:
        lookup_params[container_type] = container_name

    # Check if profile exists
    existing_profile = None
    profile_id = params.get("id")
    profile_name = params.get("name")

    if profile_id:
        # Lookup by ID
        try:
            existing_profile = client.decryption_profile.fetch(profile_id)
        except ObjectNotPresentError:
            existing_profile = None
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by ID: {e!s}")
    elif profile_name and container_type:
        # Lookup by name and container
        try:
            existing_profile = client.decryption_profile.fetch(name=profile_name, **lookup_params)
        except ObjectNotPresentError:
            existing_profile = None
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by name: {e!s}")

    if state == "absent":
        if existing_profile:
            if not module.check_mode:
                try:
                    client.decryption_profile.delete(str(existing_profile.id))
                    result["msg"] = f"Decryption profile '{profile_name or profile_id}' deleted successfully"
                except APIError as e:
                    module.fail_json(msg=f"Failed to delete profile: {e!s}")
            else:
                result["msg"] = f"Would delete Decryption profile '{profile_name or profile_id}'"
            result["changed"] = True
        else:
            result["msg"] = f"Decryption profile '{profile_name or profile_id}' not found, nothing to delete"
        module.exit_json(**result)

    if not container_type:
        module.fail_json(msg="One of 'folder', 'snippet', or 'device' is required when state=present")

    if not profile_name:
        module.fail_json(msg="'name' is required when state=present")

    # Build the profile data
    profile_data = {
        "name": profile_name,
        container_type: container_name,
    }

    if params.get("ssl_forward_proxy"):
        profile_data["ssl_forward_proxy"] = params["ssl_forward_proxy"]

    if params.get("ssl_inbound_proxy"):
        profile_data["ssl_inbound_proxy"] = params["ssl_inbound_proxy"]

    if params.get("ssl_no_proxy"):
        profile_data["ssl_no_proxy"] = params["ssl_no_proxy"]

    if params.get("ssl_protocol_settings"):
        profile_data["ssl_protocol_settings"] = params["ssl_protocol_settings"]

    # Validate and prepare the profile data using SDK models
    try:
        profile_model = DecryptionProfileCreateModel(**profile_data)
    except Exception as e:
        module.fail_json(msg=f"Failed to validate profile data: {e!s}")

    if existing_profile:
        # Check if update is needed
        needs_update = False
        update_fields = []

        # Compare name
        if existing_profile.name != profile_model.name:
            needs_update = True
            update_fields.append("name")

        # Compare ssl_forward_proxy
        existing_forward = getattr(existing_profile, "ssl_forward_proxy", None)
        if existing_forward != profile_data.get("ssl_forward_proxy"):
            needs_update = True
            update_fields.append("ssl_forward_proxy")

        # Compare ssl_inbound_proxy
        existing_inbound = getattr(existing_profile, "ssl_inbound_proxy", None)
        if existing_inbound != profile_data.get("ssl_inbound_proxy"):
            needs_update = True
            update_fields.append("ssl_inbound_proxy")

        # Compare ssl_no_proxy
        existing_no_proxy = getattr(existing_profile, "ssl_no_proxy", None)
        if existing_no_proxy != profile_data.get("ssl_no_proxy"):
            needs_update = True
            update_fields.append("ssl_no_proxy")

        # Compare ssl_protocol_settings
        existing_protocol = getattr(existing_profile, "ssl_protocol_settings", None)
        if existing_protocol != profile_data.get("ssl_protocol_settings"):
            needs_update = True
            update_fields.append("ssl_protocol_settings")

        if needs_update:
            if not module.check_mode:
                try:
                    profile_data["id"] = str(existing_profile.id)
                    updated_profile = client.decryption_profile.update(existing_profile)
                    result["decryption_profile"] = json.loads(updated_profile.model_dump_json())
                    result["msg"] = f"Decryption profile '{profile_name}' updated: {', '.join(update_fields)}"
                except APIError as e:
                    module.fail_json(msg=f"Failed to update profile: {e!s}")
            else:
                result["decryption_profile"] = profile_data
                result["msg"] = f"Would update Decryption profile '{profile_name}': {', '.join(update_fields)}"
            result["changed"] = True
        else:
            result["decryption_profile"] = json.loads(existing_profile.model_dump_json())
            result["msg"] = f"Decryption profile '{profile_name}' already exists with correct configuration"
    else:
        # Create new profile
        if not module.check_mode:
            try:
                created_profile = client.decryption_profile.create(profile_data)
                result["decryption_profile"] = json.loads(created_profile.model_dump_json())
                result["msg"] = f"Decryption profile '{profile_name}' created successfully"
            except APIError as e:
                module.fail_json(msg=f"Failed to create profile: {e!s}")
        else:
            result["decryption_profile"] = profile_data
            result["msg"] = f"Would create Decryption profile '{profile_name}'"
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()
