#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.network import NatRuleCreateModel

DOCUMENTATION = r"""
---
module: nat_rule
short_description: Manage NAT rules in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete NAT rules in Strata Cloud Manager using pan-scm-sdk.
    - NAT rules define Network Address Translation policies for traffic flowing through firewalls.
    - Supports all NAT rule attributes including source and destination translation.
    - NAT rules must be associated with exactly one container (folder, snippet, or device).
    - Supports both pre-rulebase and post-rulebase positioning.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the NAT rule.
            - Required for state=present and for absent if id is not provided.
            - Must match pattern ^[a-zA-Z0-9_ \\.-]+$
        type: str
        required: false
    description:
        description:
            - Description of the NAT rule.
        type: str
        required: false
    tag:
        description:
            - List of tags associated with the NAT rule.
        type: list
        elements: str
        required: false
        default: []
    disabled:
        description:
            - Whether the NAT rule is disabled.
        type: bool
        required: false
        default: false
    nat_type:
        description:
            - The type of NAT operation.
        type: str
        required: false
        choices: ['ipv4', 'nat64', 'nptv6']
        default: 'ipv4'
    from:
        description:
            - List of source zones.
        type: list
        elements: str
        required: false
        default: ['any']
    to:
        description:
            - List of destination zones.
        type: list
        elements: str
        required: false
        default: ['any']
    to_interface:
        description:
            - Destination interface of the original packet.
        type: str
        required: false
    source:
        description:
            - List of source addresses.
        type: list
        elements: str
        required: false
        default: ['any']
    destination:
        description:
            - List of destination addresses.
        type: list
        elements: str
        required: false
        default: ['any']
    service:
        description:
            - The TCP/UDP service.
        type: str
        required: false
        default: 'any'
    source_translation:
        description:
            - Source translation configuration.
            - Can specify dynamic_ip_and_port, dynamic_ip, or static_ip.
        type: dict
        required: false
        suboptions:
            dynamic_ip_and_port:
                description:
                    - Dynamic IP and port translation.
                type: dict
                required: false
                suboptions:
                    translated_address:
                        description:
                            - List of translated source IP addresses.
                        type: list
                        elements: str
                        required: false
                    interface_address:
                        description:
                            - Translated source interface configuration.
                        type: dict
                        required: false
                        suboptions:
                            interface:
                                description:
                                    - Interface name.
                                type: str
                                required: true
                            ip:
                                description:
                                    - IP address.
                                type: str
                                required: false
                            floating_ip:
                                description:
                                    - Floating IP address.
                                type: str
                                required: false
            dynamic_ip:
                description:
                    - Dynamic IP translation.
                type: dict
                required: false
                suboptions:
                    translated_address:
                        description:
                            - List of translated IP addresses.
                        type: list
                        elements: str
                        required: true
                    fallback_type:
                        description:
                            - Type of fallback configuration.
                        type: str
                        required: false
                        choices: ['translated_address', 'interface_address']
                    fallback_address:
                        description:
                            - Fallback IP addresses (when fallback_type is translated_address).
                        type: list
                        elements: str
                        required: false
                    fallback_interface:
                        description:
                            - Fallback interface name (when fallback_type is interface_address).
                        type: str
                        required: false
                    fallback_ip:
                        description:
                            - Fallback IP address (when fallback_type is interface_address).
                        type: str
                        required: false
            static_ip:
                description:
                    - Static IP translation.
                type: dict
                required: false
                suboptions:
                    translated_address:
                        description:
                            - Translated IP address.
                        type: str
                        required: true
                    bi_directional:
                        description:
                            - Enable bi-directional translation.
                        type: bool
                        required: false
    destination_translation:
        description:
            - Destination translation configuration.
        type: dict
        required: false
        suboptions:
            translated_address:
                description:
                    - Translated destination IP address.
                type: str
                required: false
            translated_port:
                description:
                    - Translated destination port (1-65535).
                type: int
                required: false
            dns_rewrite:
                description:
                    - DNS rewrite configuration.
                type: dict
                required: false
                suboptions:
                    direction:
                        description:
                            - DNS rewrite direction.
                        type: str
                        required: true
                        choices: ['reverse', 'forward']
    active_active_device_binding:
        description:
            - Active/Active device binding.
        type: str
        required: false
    position:
        description:
            - Rule position in the rulebase (pre or post).
        type: str
        required: false
        choices: ['pre', 'post']
        default: 'pre'
    folder:
        description:
            - The folder in which the NAT rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the NAT rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the NAT rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the NAT rule (UUID).
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
            - Desired state of the NAT rule.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - NAT rules must be associated with exactly one container (folder, snippet, or device).
    - The 'from' and 'to' parameters map to 'from_' and 'to_' in the SDK.
"""

EXAMPLES = r"""
---
- name: Create basic source NAT rule
  cdot65.scm.nat_rule:
    name: "SNAT-Trust-to-Untrust"
    description: "Source NAT for internal traffic"
    from:
      - "trust"
    to:
      - "untrust"
    source:
      - "10.0.0.0/8"
    destination:
      - "any"
    service: "any"
    source_translation:
      dynamic_ip_and_port:
        translated_address:
          - "203.0.113.10"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create destination NAT rule
  cdot65.scm.nat_rule:
    name: "DNAT-Web-Server"
    description: "Destination NAT for web server"
    from:
      - "untrust"
    to:
      - "dmz"
    source:
      - "any"
    destination:
      - "203.0.113.100"
    service: "service-http"
    destination_translation:
      translated_address: "10.1.1.10"
      translated_port: 8080
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create NAT rule with static IP translation
  cdot65.scm.nat_rule:
    name: "Static-NAT-Server"
    description: "Static NAT for server"
    from:
      - "trust"
    to:
      - "untrust"
    source:
      - "10.1.1.50"
    destination:
      - "any"
    service: "any"
    source_translation:
      static_ip:
        translated_address: "203.0.113.50"
        bi_directional: true
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create NAT rule with interface address
  cdot65.scm.nat_rule:
    name: "SNAT-Interface"
    description: "Source NAT using interface address"
    from:
      - "trust"
    to:
      - "untrust"
    source:
      - "192.168.1.0/24"
    destination:
      - "any"
    service: "any"
    source_translation:
      dynamic_ip_and_port:
        interface_address:
          interface: "ethernet1/1"
          ip: "203.0.113.1"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create NAT rule with tags
  cdot65.scm.nat_rule:
    name: "SNAT-Tagged"
    from:
      - "trust"
    to:
      - "untrust"
    source:
      - "any"
    destination:
      - "any"
    service: "any"
    source_translation:
      dynamic_ip_and_port:
        translated_address:
          - "203.0.113.20"
    tag:
      - "production"
      - "outbound"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update existing NAT rule
  cdot65.scm.nat_rule:
    name: "SNAT-Trust-to-Untrust"
    description: "Updated description"
    from:
      - "trust"
    to:
      - "untrust"
    source:
      - "10.0.0.0/8"
      - "172.16.0.0/12"
    destination:
      - "any"
    service: "any"
    source_translation:
      dynamic_ip_and_port:
        translated_address:
          - "203.0.113.10"
          - "203.0.113.11"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete NAT rule by name
  cdot65.scm.nat_rule:
    name: "SNAT-Trust-to-Untrust"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete NAT rule by ID
  cdot65.scm.nat_rule:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
nat_rule:
    description: Information about the NAT rule that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The NAT rule ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The NAT rule name
            type: str
            returned: always
            sample: "SNAT-Trust-to-Untrust"
        description:
            description: The NAT rule description
            type: str
            returned: when configured
            sample: "Source NAT for internal traffic"
        tag:
            description: Tags associated with the NAT rule
            type: list
            returned: when configured
            sample: ["production", "outbound"]
        disabled:
            description: Whether the NAT rule is disabled
            type: bool
            returned: always
            sample: false
        nat_type:
            description: The type of NAT operation
            type: str
            returned: always
            sample: "ipv4"
        from:
            description: Source zones
            type: list
            returned: always
            sample: ["trust"]
        to:
            description: Destination zones
            type: list
            returned: always
            sample: ["untrust"]
        source:
            description: Source addresses
            type: list
            returned: always
            sample: ["10.0.0.0/8"]
        destination:
            description: Destination addresses
            type: list
            returned: always
            sample: ["any"]
        service:
            description: The TCP/UDP service
            type: str
            returned: always
            sample: "any"
        source_translation:
            description: Source translation configuration
            type: dict
            returned: when configured
            sample: {"dynamic_ip_and_port": {"translated_address": ["203.0.113.10"]}}
        destination_translation:
            description: Destination translation configuration
            type: dict
            returned: when configured
            sample: {"translated_address": "10.1.1.10", "translated_port": 8080}
        folder:
            description: The folder containing the NAT rule
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the NAT rule
            type: str
            returned: when applicable
            sample: "NAT-Config"
        device:
            description: The device containing the NAT rule
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False, default=[]),
        disabled=dict(type="bool", required=False, default=False),
        nat_type=dict(type="str", required=False, choices=["ipv4", "nat64", "nptv6"], default="ipv4"),
        from_=dict(type="list", elements="str", required=False, default=["any"], aliases=["from"]),
        to_=dict(type="list", elements="str", required=False, default=["any"], aliases=["to"]),
        to_interface=dict(type="str", required=False),
        source=dict(type="list", elements="str", required=False, default=["any"]),
        destination=dict(type="list", elements="str", required=False, default=["any"]),
        service=dict(type="str", required=False, default="any"),
        source_translation=dict(type="dict", required=False),
        destination_translation=dict(type="dict", required=False),
        active_active_device_binding=dict(type="str", required=False),
        position=dict(type="str", required=False, choices=["pre", "post"], default="pre"),
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
            ["state", "present", ["name"]],
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

    # Initialize results
    result = {"changed": False, "nat_rule": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize rule_exists boolean
        rule_exists = False
        rule_obj = None

        # Fetch rule by name or id
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

            # Attempt to find the rule by listing and filtering
            if params.get("name") and container_type and container_name:
                try:
                    # Use fetch method
                    rule_obj = client.nat_rule.fetch(
                        name=params.get("name"),
                        position=params.get("position", "pre"),
                        **{container_type: container_name},
                    )
                    if rule_obj:
                        rule_exists = True
                except Exception as e:
                    # Skip if object not found
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error fetching NAT rule: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

            # If specified by ID, try to get it directly
            elif params.get("id"):
                try:
                    rule_obj = client.nat_rule.get(params.get("id"))
                    if rule_obj:
                        rule_exists = True
                except Exception as e:
                    # Skip if object not found, but fail on other errors
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error retrieving NAT rule by ID: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

        # Create or update or delete rule
        if params.get("state") == "present":
            if rule_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Basic fields
                for field in [
                    "name",
                    "description",
                    "tag",
                    "disabled",
                    "nat_type",
                    "to_interface",
                    "service",
                    "source_translation",
                    "destination_translation",
                    "active_active_device_binding",
                    "folder",
                    "snippet",
                    "device",
                ]:
                    if params.get(field) is not None:
                        current_value = getattr(rule_obj, field, None)
                        # Handle list comparisons (sort for consistent comparison)
                        if field in ["tag"]:
                            current_sorted = sorted(current_value) if current_value else []
                            new_sorted = sorted(params.get(field)) if params.get(field) else []
                            if current_sorted != new_sorted:
                                update_fields[field] = params.get(field)
                        # Handle dict comparisons
                        elif field in ["source_translation", "destination_translation"]:
                            if params.get(field) != current_value:
                                update_fields[field] = params.get(field)
                        # Handle simple field comparisons
                        elif current_value != params.get(field):
                            update_fields[field] = params.get(field)

                # Handle from_ and to_ fields
                for field, attr_name in [("from_", "from_"), ("to_", "to_")]:
                    if params.get(field) is not None:
                        current_value = getattr(rule_obj, attr_name, None)
                        current_sorted = sorted(current_value) if current_value else []
                        new_sorted = sorted(params.get(field)) if params.get(field) else []
                        if current_sorted != new_sorted:
                            update_fields[attr_name] = params.get(field)

                # Handle source and destination fields
                for field in ["source", "destination"]:
                    if params.get(field) is not None:
                        current_value = getattr(rule_obj, field, None)
                        current_sorted = sorted(current_value) if current_value else []
                        new_sorted = sorted(params.get(field)) if params.get(field) else []
                        if current_sorted != new_sorted:
                            update_fields[field] = params.get(field)

                # Update the rule if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = rule_obj.model_copy(update=update_fields)
                            updated = client.nat_rule.update(update_model, position=params.get("position", "pre"))
                            result["nat_rule"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid NAT rule object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating NAT rule: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, return existing object with projected changes
                        result["nat_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["nat_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new rule
                create_payload = {}

                # Add parameters - map from_ and to_ to from and to
                for k in [
                    "name",
                    "description",
                    "tag",
                    "disabled",
                    "nat_type",
                    "to_interface",
                    "source",
                    "destination",
                    "service",
                    "source_translation",
                    "destination_translation",
                    "active_active_device_binding",
                ]:
                    if params.get(k) is not None:
                        create_payload[k] = params[k]

                # Handle from_ and to_ parameters
                if params.get("from_") is not None:
                    create_payload["from_"] = params["from_"]
                if params.get("to_") is not None:
                    create_payload["to_"] = params["to_"]

                # Add container parameter
                if params.get("folder"):
                    create_payload["folder"] = params["folder"]
                elif params.get("snippet"):
                    create_payload["snippet"] = params["snippet"]
                elif params.get("device"):
                    create_payload["device"] = params["device"]

                # Create rule object
                if not module.check_mode:
                    try:
                        created = client.nat_rule.create(create_payload, position=params.get("position", "pre"))
                        result["nat_rule"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid NAT rule object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating NAT rule: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = NatRuleCreateModel(**create_payload)
                    result["nat_rule"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        # Handle absent state - delete the rule
        elif params.get("state") == "absent":
            if rule_exists:
                if not module.check_mode:
                    try:
                        client.nat_rule.delete(rule_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting NAT rule: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["nat_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))
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
