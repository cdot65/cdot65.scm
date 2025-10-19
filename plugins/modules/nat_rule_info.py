#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: nat_rule_info
short_description: Retrieve information about NAT rules in Strata Cloud Manager (SCM)
description:
    - Retrieve information about NAT rules in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single rule by ID or name, or listing multiple rules with optional filtering.
    - NAT rules are associated with exactly one container (folder, snippet, or device).
    - Supports both pre-rulebase and post-rulebase queries.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the NAT rule to retrieve.
            - Used for exact match lookup.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the NAT rule (UUID).
            - Used for exact match lookup.
            - Mutually exclusive with I(name).
        type: str
        required: false
    nat_type:
        description:
            - Filter rules by NAT type.
        type: list
        elements: str
        required: false
    service:
        description:
            - Filter rules by service.
        type: list
        elements: str
        required: false
    destination:
        description:
            - Filter rules by destination addresses.
        type: list
        elements: str
        required: false
    source:
        description:
            - Filter rules by source addresses.
        type: list
        elements: str
        required: false
    tag:
        description:
            - Filter rules by tags.
        type: list
        elements: str
        required: false
    disabled:
        description:
            - Filter rules by disabled status.
        type: bool
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
            - The folder in which to look for NAT rules.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for NAT rules.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to look for NAT rules.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: false
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
notes:
    - When retrieving a single rule, either name or id must be provided.
    - When retrieving multiple rules, all rules in the specified container will be returned.
    - Exactly one container parameter (folder, snippet, or device) must be provided.
    - Check mode is supported but makes no changes.
"""

EXAMPLES = r"""
---
- name: Get all NAT rules in a folder (pre-rulebase)
  cdot65.scm.nat_rule_info:
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: nat_rules

- name: Get all NAT rules in post-rulebase
  cdot65.scm.nat_rule_info:
    folder: "Shared"
    position: "post"
    scm_access_token: "{{ scm_access_token }}"
  register: nat_rules_post

- name: Get NAT rule by ID
  cdot65.scm.nat_rule_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
  register: nat_rule

- name: Get NAT rule by name
  cdot65.scm.nat_rule_info:
    name: "SNAT-Trust-to-Untrust"
    folder: "Shared"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: nat_rule

- name: Get all NAT rules in a snippet
  cdot65.scm.nat_rule_info:
    snippet: "NAT-Config"
    position: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_rules

- name: Get NAT rules filtered by service
  cdot65.scm.nat_rule_info:
    folder: "Shared"
    position: "pre"
    service:
      - "service-http"
      - "service-https"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_rules

- name: Get NAT rules filtered by tag
  cdot65.scm.nat_rule_info:
    folder: "Shared"
    position: "pre"
    tag:
      - "production"
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_rules

- name: Get disabled NAT rules
  cdot65.scm.nat_rule_info:
    folder: "Shared"
    position: "pre"
    disabled: true
    scm_access_token: "{{ scm_access_token }}"
  register: disabled_rules

- name: Display rule information
  debug:
    msg: "Rule {{ item.name }} translates {{ item.source | join(', ') }} to {{ item.destination | join(', ') }}"
  loop: "{{ nat_rules.nat_rules }}"
"""

RETURN = r"""
nat_rules:
    description: List of NAT rules when multiple rules are retrieved
    returned: when no id or name is specified
    type: list
    elements: dict
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
nat_rule:
    description: Information about a specific NAT rule
    returned: when id or name is specified and rule exists
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
        id=dict(type="str", required=False),
        nat_type=dict(type="list", elements="str", required=False),
        service=dict(type="list", elements="str", required=False),
        destination=dict(type="list", elements="str", required=False),
        source=dict(type="list", elements="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        disabled=dict(type="bool", required=False),
        position=dict(type="str", required=False, choices=["pre", "post"], default="pre"),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["name", "id"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params
    rule_name = params.get("name")
    rule_id = params.get("id")

    # Custom validation for container parameters
    if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
        module.fail_json(msg="One of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Determine the container type and value
        container_type = None
        container_value = None

        if params.get("folder"):
            container_type = "folder"
            container_value = params.get("folder")
        elif params.get("snippet"):
            container_type = "snippet"
            container_value = params.get("snippet")
        elif params.get("device"):
            container_type = "device"
            container_value = params.get("device")

        # Retrieve a specific rule by ID or name
        if rule_id or rule_name:
            try:
                if rule_id:
                    # Fetch by ID
                    rule = client.nat_rule.get(rule_id)
                elif rule_name:
                    # Fetch by name within the specified container
                    rule = client.nat_rule.fetch(
                        name=rule_name, position=params.get("position", "pre"), **{container_type: container_value}
                    )

                # Get the rule data and convert it to a dictionary
                rule_dict = json.loads(rule.model_dump_json(exclude_unset=True))

                # Return the rule information
                result["nat_rule"] = rule_dict
            except ObjectNotPresentError:
                if rule_id:
                    module.fail_json(msg=f"NAT rule with ID '{rule_id}' not found")
                else:
                    module.fail_json(msg=f"NAT rule with name '{rule_name}' not found in the specified container")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )
        else:
            # Retrieve multiple rules
            try:
                # Build filter parameters
                filter_params = {container_type: container_value}
                filter_params["position"] = params.get("position", "pre")

                # Add exact_match parameter if specified
                if params.get("exact_match"):
                    filter_params["exact_match"] = params.get("exact_match")

                # Add additional filter parameters
                if params.get("nat_type"):
                    filter_params["nat_type"] = params.get("nat_type")
                if params.get("service"):
                    filter_params["service"] = params.get("service")
                if params.get("destination"):
                    filter_params["destination"] = params.get("destination")
                if params.get("source"):
                    filter_params["source"] = params.get("source")
                if params.get("tag"):
                    filter_params["tag"] = params.get("tag")
                if params.get("disabled") is not None:
                    filter_params["disabled"] = params.get("disabled")

                # Fetch all rules in the container with filters
                rules = client.nat_rule.list(**filter_params)

                # Convert to list of dictionaries
                rules_list = []
                for rule in rules:
                    rule_dict = json.loads(rule.model_dump_json(exclude_unset=True))
                    rules_list.append(rule_dict)

                result["nat_rules"] = rules_list
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )

        # Return results
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg="Unexpected error: " + str(e))


if __name__ == "__main__":
    main()
