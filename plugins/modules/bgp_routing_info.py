#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError

DOCUMENTATION = r"""
---
module: bgp_routing_info
short_description: Retrieve BGP routing settings in Strata Cloud Manager (SCM)
description:
    - Retrieve the current BGP routing settings for Service Connections in Strata Cloud Manager using pan-scm-sdk.
    - BGP routing is a singleton configuration object that applies globally to Service Connections.
    - This module only retrieves information and does not modify any configuration.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
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
notes:
    - Check mode is supported but makes no changes.
    - BGP routing is a singleton object - there is only one configuration per SCM instance.
    - This configuration does not belong to a folder, snippet, or device container.
"""

EXAMPLES = r"""
---
- name: Get current BGP routing configuration
  cdot65.scm.bgp_routing_info:
    scm_access_token: "{{ scm_access_token }}"
  register: bgp_config

- name: Display BGP routing configuration
  debug:
    msg: "Backbone routing: {{ bgp_config.bgp_routing.backbone_routing }}"

- name: Check if routes are accepted over Service Connections
  debug:
    msg: "Accept routes over SC: {{ bgp_config.bgp_routing.accept_route_over_SC }}"

- name: Display outbound routes for services
  debug:
    msg: "Outbound routes: {{ bgp_config.bgp_routing.outbound_routes_for_services }}"
"""

RETURN = r"""
bgp_routing:
    description: Information about the BGP routing configuration
    returned: always
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
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
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

        # Get BGP routing configuration
        try:
            bgp_config = client.bgp_routing.get()
            result["bgp_routing"] = json.loads(bgp_config.model_dump_json(exclude_unset=True))
        except (APIError, InvalidObjectError) as e:
            module.fail_json(
                msg=f"API error retrieving BGP routing configuration: {str(e)}",
                error_code=getattr(e, "error_code", None),
                details=getattr(e, "details", None),
            )

        # Return results
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
