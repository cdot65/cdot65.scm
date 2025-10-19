#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError

DOCUMENTATION = r"""
---
module: bgp_routing
short_description: Manage BGP routing settings in Strata Cloud Manager (SCM)
description:
    - Configure or reset BGP routing settings for Service Connections in Strata Cloud Manager using pan-scm-sdk.
    - BGP routing is a singleton configuration object that applies globally to Service Connections.
    - Supports configuring routing preference, backbone routing, route acceptance, and other BGP parameters.
    - This module does not support traditional state=absent deletion; use state=reset to restore defaults.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    routing_preference:
        description:
            - The routing preference configuration.
            - Must be either 'default' or 'hot_potato_routing'.
        type: str
        required: false
        choices: ['default', 'hot_potato_routing']
    backbone_routing:
        description:
            - Backbone routing configuration for asymmetric routing options.
            - Required when state=present.
        type: str
        required: false
        choices:
            - "no-asymmetric-routing"
            - "asymmetric-routing-only"
            - "asymmetric-routing-with-load-share"
    accept_route_over_sc:
        description:
            - Whether to accept routes over Service Connections.
            - Maps to accept_route_over_SC in the API.
        type: bool
        required: false
        default: false
    outbound_routes_for_services:
        description:
            - List of outbound routes for services in CIDR notation.
        type: list
        elements: str
        required: false
        default: []
    add_host_route_to_ike_peer:
        description:
            - Whether to add host route to IKE peer.
        type: bool
        required: false
        default: false
    withdraw_static_route:
        description:
            - Whether to withdraw static routes.
        type: bool
        required: false
        default: false
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
            - Desired state of the BGP routing configuration.
            - Use 'present' to configure BGP routing settings.
            - Use 'reset' to restore default BGP routing settings.
        type: str
        choices: ['present', 'reset']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - BGP routing is a singleton object - there is only one configuration per SCM instance.
    - This configuration does not belong to a folder, snippet, or device container.
    - When state=reset, the configuration is restored to default values, not deleted.
"""

EXAMPLES = r"""
---
- name: Configure basic BGP routing with default preference
  cdot65.scm.bgp_routing:
    routing_preference: "default"
    backbone_routing: "no-asymmetric-routing"
    accept_route_over_sc: false
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Configure BGP routing with hot potato routing
  cdot65.scm.bgp_routing:
    routing_preference: "hot_potato_routing"
    backbone_routing: "asymmetric-routing-only"
    accept_route_over_sc: true
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Configure BGP routing with outbound routes
  cdot65.scm.bgp_routing:
    routing_preference: "default"
    backbone_routing: "asymmetric-routing-with-load-share"
    accept_route_over_sc: true
    outbound_routes_for_services:
      - "10.0.0.0/8"
      - "172.16.0.0/12"
    add_host_route_to_ike_peer: true
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Configure BGP routing with static route withdrawal
  cdot65.scm.bgp_routing:
    routing_preference: "default"
    backbone_routing: "no-asymmetric-routing"
    withdraw_static_route: true
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Reset BGP routing to defaults
  cdot65.scm.bgp_routing:
    scm_access_token: "{{ scm_access_token }}"
    state: reset

- name: Get current BGP routing configuration (idempotent check)
  cdot65.scm.bgp_routing_info:
    scm_access_token: "{{ scm_access_token }}"
  register: current_bgp
"""

RETURN = r"""
bgp_routing:
    description: Information about the BGP routing configuration
    returned: on success
    type: dict
    contains:
        routing_preference:
            description: The routing preference configuration
            type: dict
            returned: always
            sample: {"default": {}}
        backbone_routing:
            description: Backbone routing configuration
            type: str
            returned: always
            sample: "no-asymmetric-routing"
        accept_route_over_SC:
            description: Whether routes are accepted over Service Connections
            type: bool
            returned: always
            sample: false
        outbound_routes_for_services:
            description: List of outbound routes for services
            type: list
            returned: always
            sample: ["10.0.0.0/8"]
        add_host_route_to_ike_peer:
            description: Whether host route to IKE peer is added
            type: bool
            returned: always
            sample: false
        withdraw_static_route:
            description: Whether static routes are withdrawn
            type: bool
            returned: always
            sample: false
"""


def main():
    module_args = dict(
        routing_preference=dict(
            type="str",
            required=False,
            choices=["default", "hot_potato_routing"],
        ),
        backbone_routing=dict(
            type="str",
            required=False,
            choices=[
                "no-asymmetric-routing",
                "asymmetric-routing-only",
                "asymmetric-routing-with-load-share",
            ],
        ),
        accept_route_over_sc=dict(type="bool", required=False, default=False),
        outbound_routes_for_services=dict(
            type="list",
            elements="str",
            required=False,
            default=[],
        ),
        add_host_route_to_ike_peer=dict(type="bool", required=False, default=False),
        withdraw_static_route=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "reset"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["backbone_routing"]],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "bgp_routing": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get current BGP routing configuration
        try:
            current_config = client.bgp_routing.get()
        except Exception as e:
            module.fail_json(
                msg=f"Error retrieving current BGP routing configuration: {str(e)}",
                error_code=getattr(e, "error_code", None),
                details=getattr(e, "details", None),
            )

        # Handle reset state - restore defaults
        if params.get("state") == "reset":
            # Check if already at defaults
            is_default = (
                current_config.backbone_routing == "no-asymmetric-routing"
                and current_config.accept_route_over_SC is False
                and (not current_config.outbound_routes_for_services or len(current_config.outbound_routes_for_services) == 0)
                and current_config.add_host_route_to_ike_peer is False
                and current_config.withdraw_static_route is False
            )

            if not is_default:
                if not module.check_mode:
                    try:
                        client.bgp_routing.delete()
                        # Get the updated configuration after reset
                        updated_config = client.bgp_routing.get()
                        result["bgp_routing"] = json.loads(updated_config.model_dump_json(exclude_unset=True))
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error resetting BGP routing configuration: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )
                else:
                    # In check mode, show what defaults would be
                    result["bgp_routing"] = {
                        "routing_preference": {"default": {}},
                        "backbone_routing": "no-asymmetric-routing",
                        "accept_route_over_SC": False,
                        "outbound_routes_for_services": [],
                        "add_host_route_to_ike_peer": False,
                        "withdraw_static_route": False,
                    }

                result["changed"] = True
                module.exit_json(**result)
            else:
                # Already at defaults
                result["bgp_routing"] = json.loads(current_config.model_dump_json(exclude_unset=True))
                result["changed"] = False
                module.exit_json(**result)

        # Handle present state - configure BGP routing
        elif params.get("state") == "present":
            # Build update payload
            update_fields = {}

            # Handle routing_preference
            if params.get("routing_preference") is not None:
                if params.get("routing_preference") == "default":
                    update_fields["routing_preference"] = {"default": {}}
                elif params.get("routing_preference") == "hot_potato_routing":
                    update_fields["routing_preference"] = {"hot_potato_routing": {}}

            # Add backbone_routing
            if params.get("backbone_routing") is not None:
                update_fields["backbone_routing"] = params.get("backbone_routing")

            # Add other fields
            for field in [
                "accept_route_over_sc",
                "outbound_routes_for_services",
                "add_host_route_to_ike_peer",
                "withdraw_static_route",
            ]:
                if params.get(field) is not None:
                    # Map accept_route_over_sc to API field name
                    api_field = "accept_route_over_SC" if field == "accept_route_over_sc" else field
                    update_fields[api_field] = params.get(field)

            # Check if update is needed by comparing with current config
            needs_update = False

            # Compare routing_preference
            if "routing_preference" in update_fields:
                current_pref = current_config.routing_preference
                if hasattr(current_pref, "default"):
                    current_pref_type = "default"
                elif hasattr(current_pref, "hot_potato_routing"):
                    current_pref_type = "hot_potato_routing"
                else:
                    current_pref_type = None

                if params.get("routing_preference") and params.get("routing_preference") != current_pref_type:
                    needs_update = True

            # Compare backbone_routing
            if "backbone_routing" in update_fields:
                if str(current_config.backbone_routing) != update_fields["backbone_routing"]:
                    needs_update = True

            # Compare boolean and list fields
            for api_field, param_field in [
                ("accept_route_over_SC", "accept_route_over_sc"),
                ("outbound_routes_for_services", "outbound_routes_for_services"),
                ("add_host_route_to_ike_peer", "add_host_route_to_ike_peer"),
                ("withdraw_static_route", "withdraw_static_route"),
            ]:
                if api_field in update_fields:
                    current_value = getattr(current_config, api_field, None)
                    if isinstance(update_fields[api_field], list):
                        # Sort lists for comparison
                        current_sorted = sorted(current_value) if current_value else []
                        new_sorted = sorted(update_fields[api_field]) if update_fields[api_field] else []
                        if current_sorted != new_sorted:
                            needs_update = True
                    elif current_value != update_fields[api_field]:
                        needs_update = True

            # Update if needed
            if needs_update:
                if not module.check_mode:
                    try:
                        updated = client.bgp_routing.update(update_fields)
                        result["bgp_routing"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid BGP routing configuration: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=update_fields,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error updating BGP routing configuration: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=update_fields,
                        )
                else:
                    # In check mode, return current config
                    result["bgp_routing"] = json.loads(current_config.model_dump_json(exclude_unset=True))

                result["changed"] = True
                module.exit_json(**result)
            else:
                # No update needed
                result["bgp_routing"] = json.loads(current_config.model_dump_json(exclude_unset=True))
                result["changed"] = False
                module.exit_json(**result)

    # Handle errors
    except (InvalidObjectError, APIError) as e:
        module.fail_json(msg=str(e), error_code=getattr(e, "error_code", None), details=getattr(e, "details", None))
    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
