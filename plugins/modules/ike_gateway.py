#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.network import IKEGatewayCreateModel

DOCUMENTATION = r"""
---
module: ike_gateway
short_description: Manage IKE gateways in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete IKE gateways in Strata Cloud Manager using pan-scm-sdk.
    - IKE gateways define VPN tunnel endpoints and authentication parameters.
    - Supports all IKE gateway attributes including authentication, protocol configuration, and peer addressing.
    - IKE gateways must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the IKE gateway.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
            - Must match pattern ^[0-9a-zA-Z._-]+$
        type: str
        required: false
    authentication:
        description:
            - Authentication configuration for the IKE gateway.
            - Required for state=present.
        type: dict
        required: false
        suboptions:
            pre_shared_key:
                description:
                    - Pre-shared key configuration.
                    - Mutually exclusive with certificate.
                type: dict
                required: false
                suboptions:
                    key:
                        description:
                            - The pre-shared key string.
                        type: str
                        required: true
                        no_log: true
            certificate:
                description:
                    - Certificate-based authentication configuration.
                    - Mutually exclusive with pre_shared_key.
                type: dict
                required: false
                suboptions:
                    allow_id_payload_mismatch:
                        description:
                            - Allow ID payload mismatch.
                        type: bool
                        required: false
                    certificate_profile:
                        description:
                            - Certificate profile name.
                        type: str
                        required: false
                    local_certificate:
                        description:
                            - Local certificate configuration.
                        type: dict
                        required: false
                    strict_validation_revocation:
                        description:
                            - Enable strict certificate revocation validation.
                        type: bool
                        required: false
                    use_management_as_source:
                        description:
                            - Use management interface as source.
                        type: bool
                        required: false
    peer_address:
        description:
            - Peer address configuration.
            - Required for state=present.
            - Exactly one of ip, fqdn, or dynamic must be specified.
        type: dict
        required: false
        suboptions:
            ip:
                description:
                    - Static peer IP address.
                type: str
                required: false
            fqdn:
                description:
                    - Fully qualified domain name of peer.
                type: str
                required: false
            dynamic:
                description:
                    - Empty dict to indicate dynamic peer address.
                type: dict
                required: false
    protocol:
        description:
            - IKE protocol configuration.
            - Required for state=present.
        type: dict
        required: false
        suboptions:
            version:
                description:
                    - IKE protocol version preference.
                type: str
                required: false
                choices: ["ikev1", "ikev2", "ikev2-preferred"]
                default: "ikev2-preferred"
            ikev1:
                description:
                    - IKEv1 specific configuration.
                type: dict
                required: false
                suboptions:
                    ike_crypto_profile:
                        description:
                            - IKE crypto profile name for IKEv1.
                        type: str
                        required: false
                    dpd:
                        description:
                            - Dead peer detection configuration.
                        type: dict
                        required: false
            ikev2:
                description:
                    - IKEv2 specific configuration.
                type: dict
                required: false
                suboptions:
                    ike_crypto_profile:
                        description:
                            - IKE crypto profile name for IKEv2.
                        type: str
                        required: false
                    dpd:
                        description:
                            - Dead peer detection configuration.
                        type: dict
                        required: false
    protocol_common:
        description:
            - Common protocol settings.
        type: dict
        required: false
        suboptions:
            nat_traversal:
                description:
                    - NAT traversal configuration.
                type: dict
                required: false
                suboptions:
                    enable:
                        description:
                            - Enable NAT traversal.
                        type: bool
                        required: false
            passive_mode:
                description:
                    - Enable passive mode.
                type: bool
                required: false
            fragmentation:
                description:
                    - Fragmentation configuration.
                type: dict
                required: false
                suboptions:
                    enable:
                        description:
                            - Enable fragmentation.
                        type: bool
                        required: false
                        default: false
    peer_id:
        description:
            - Peer ID configuration.
        type: dict
        required: false
        suboptions:
            type:
                description:
                    - Peer ID type.
                type: str
                required: true
                choices: ["ipaddr", "keyid", "fqdn", "ufqdn"]
            id:
                description:
                    - Peer ID value.
                type: str
                required: true
    local_id:
        description:
            - Local ID configuration.
        type: dict
        required: false
        suboptions:
            type:
                description:
                    - Local ID type.
                type: str
                required: true
                choices: ["ipaddr", "keyid", "fqdn", "ufqdn"]
            id:
                description:
                    - Local ID value.
                type: str
                required: true
    folder:
        description:
            - The folder in which the IKE gateway is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the IKE gateway is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the IKE gateway is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the IKE gateway (UUID).
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
            - Desired state of the IKE gateway.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - IKE gateways must be associated with exactly one container (folder, snippet, or device).
    - Authentication, peer_address, and protocol are required when creating a new gateway.
"""

EXAMPLES = r"""
---
- name: Create IKE gateway with pre-shared key and static IP
  cdot65.scm.ike_gateway:
    name: "ike-gateway-psk"
    authentication:
      pre_shared_key:
        key: "mysecretkey123"
    peer_address:
      ip: "192.0.2.1"
    protocol:
      version: "ikev2-preferred"
      ikev2:
        ike_crypto_profile: "ike-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE gateway with dynamic peer address
  cdot65.scm.ike_gateway:
    name: "ike-gateway-dynamic"
    authentication:
      pre_shared_key:
        key: "anothersecretkey"
    peer_address:
      dynamic: {}
    protocol:
      version: "ikev2"
      ikev2:
        ike_crypto_profile: "ike-crypto-strong"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE gateway with FQDN peer
  cdot65.scm.ike_gateway:
    name: "ike-gateway-fqdn"
    authentication:
      pre_shared_key:
        key: "secretkey"
    peer_address:
      fqdn: "vpn.example.com"
    protocol:
      version: "ikev2-preferred"
      ikev2:
        ike_crypto_profile: "ike-crypto-default"
    protocol_common:
      nat_traversal:
        enable: true
      fragmentation:
        enable: false
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create IKE gateway with peer and local ID
  cdot65.scm.ike_gateway:
    name: "ike-gateway-with-ids"
    authentication:
      pre_shared_key:
        key: "secretkey"
    peer_address:
      ip: "198.51.100.1"
    peer_id:
      type: "fqdn"
      id: "peer.example.com"
    local_id:
      type: "fqdn"
      id: "local.example.com"
    protocol:
      version: "ikev2"
      ikev2:
        ike_crypto_profile: "ike-crypto-default"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update IKE gateway protocol
  cdot65.scm.ike_gateway:
    name: "ike-gateway-psk"
    authentication:
      pre_shared_key:
        key: "newsecretkey"
    peer_address:
      ip: "192.0.2.1"
    protocol:
      version: "ikev2"
      ikev2:
        ike_crypto_profile: "ike-crypto-strong"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete IKE gateway by name
  cdot65.scm.ike_gateway:
    name: "ike-gateway-psk"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete IKE gateway by ID
  cdot65.scm.ike_gateway:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
ike_gateway:
    description: Information about the IKE gateway that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The IKE gateway ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The IKE gateway name
            type: str
            returned: always
            sample: "ike-gateway-psk"
        authentication:
            description: Authentication configuration
            type: dict
            returned: always
        peer_address:
            description: Peer address configuration
            type: dict
            returned: always
        protocol:
            description: IKE protocol configuration
            type: dict
            returned: always
        protocol_common:
            description: Common protocol settings
            type: dict
            returned: when configured
        peer_id:
            description: Peer ID configuration
            type: dict
            returned: when configured
        local_id:
            description: Local ID configuration
            type: dict
            returned: when configured
        folder:
            description: The folder containing the IKE gateway
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the IKE gateway
            type: str
            returned: when applicable
            sample: "VPN-Config"
        device:
            description: The device containing the IKE gateway
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        authentication=dict(type="dict", required=False),
        peer_address=dict(type="dict", required=False),
        protocol=dict(type="dict", required=False),
        protocol_common=dict(type="dict", required=False),
        peer_id=dict(type="dict", required=False),
        local_id=dict(type="dict", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name", "authentication", "peer_address", "protocol"]],
            ["state", "absent", ["name", "id"], True],
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    params = module.params
    if params.get("state") == "present":
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    result = {"changed": False, "ike_gateway": None}

    try:
        client = ScmClient(access_token=params.get("scm_access_token"))

        gateway_exists = False
        gateway_obj = None

        if params.get("name") or params.get("id"):
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

            if params.get("name") and container_type and container_name:
                try:
                    if container_type == "folder":
                        gateways = client.ike_gateway.list(folder=container_name)
                    elif container_type == "snippet":
                        gateways = client.ike_gateway.list(snippet=container_name)
                    elif container_type == "device":
                        gateways = client.ike_gateway.list(device=container_name)

                    for gateway in gateways:
                        if gateway.name == params.get("name"):
                            gateway_obj = gateway
                            gateway_exists = True
                            break
                except Exception as e:
                    module.fail_json(
                        msg=f"Error listing IKE gateways: {str(e)}",
                        error_code=getattr(e, "error_code", None),
                        details=getattr(e, "details", None),
                    )

            elif params.get("id"):
                try:
                    gateway_obj = client.ike_gateway.get(params.get("id"))
                    if gateway_obj:
                        gateway_exists = True
                except Exception as e:
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error retrieving IKE gateway by ID: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

        if params.get("state") == "present":
            if gateway_exists:
                update_fields = {}

                for field in [
                    "name",
                    "authentication",
                    "peer_address",
                    "protocol",
                    "protocol_common",
                    "peer_id",
                    "local_id",
                    "folder",
                    "snippet",
                    "device",
                ]:
                    if params.get(field) is not None:
                        current_value = getattr(gateway_obj, field, None)
                        if current_value != params.get(field):
                            update_fields[field] = params.get(field)

                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = gateway_obj.model_copy(update=update_fields)
                            updated = client.ike_gateway.update(update_model)
                            result["ike_gateway"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid IKE gateway object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating IKE gateway: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        result["ike_gateway"] = json.loads(gateway_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    result["ike_gateway"] = json.loads(gateway_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                create_payload = {}

                for k in ["name", "authentication", "peer_address", "protocol", "protocol_common", "peer_id", "local_id"]:
                    if params.get(k) is not None:
                        create_payload[k] = params[k]

                if params.get("folder"):
                    create_payload["folder"] = params["folder"]
                elif params.get("snippet"):
                    create_payload["snippet"] = params["snippet"]
                elif params.get("device"):
                    create_payload["device"] = params["device"]

                if not module.check_mode:
                    try:
                        created = client.ike_gateway.create(create_payload)
                        result["ike_gateway"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid IKE gateway object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating IKE gateway: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    simulated = IKEGatewayCreateModel(**create_payload)
                    result["ike_gateway"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        elif params.get("state") == "absent":
            if gateway_exists:
                if not module.check_mode:
                    try:
                        client.ike_gateway.delete(gateway_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting IKE gateway: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                result["changed"] = True
                result["ike_gateway"] = json.loads(gateway_obj.model_dump_json(exclude_unset=True))
                module.exit_json(**result)
            else:
                result["changed"] = False
                module.exit_json(**result)

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
