#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: security_rule_info
short_description: Get information about security rules in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about security rules in Strata Cloud Manager.
    - It can be used to get details about a specific rule by ID or name, or to list all rules.
    - Supports filtering by rule properties like action, zones, addresses, applications, services, tags, and more.
    - Supports both pre-rulebase and post-rulebase rules.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the security rule to retrieve.
            - If specified, the module will return information about this specific rule.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the security rule to retrieve.
            - If specified, the module will search for rules with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    action:
        description:
            - Filter rules by action.
            - Supported actions are 'allow', 'deny', 'drop', 'reset-client', 'reset-server', 'reset-both'.
        type: list
        elements: str
        required: false
    category:
        description:
            - Filter rules by URL categories.
        type: list
        elements: str
        required: false
    service:
        description:
            - Filter rules by services.
        type: list
        elements: str
        required: false
    application:
        description:
            - Filter rules by applications.
        type: list
        elements: str
        required: false
    destination:
        description:
            - Filter rules by destination addresses.
        type: list
        elements: str
        required: false
    to_:
        description:
            - Filter rules by destination zones.
        type: list
        elements: str
        required: false
    source:
        description:
            - Filter rules by source addresses.
        type: list
        elements: str
        required: false
    from_:
        description:
            - Filter rules by source zones.
        type: list
        elements: str
        required: false
    tags:
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
    profile_setting:
        description:
            - Filter rules by security profile groups.
        type: list
        elements: str
        required: false
    log_setting:
        description:
            - Filter rules by log forwarding profile.
        type: list
        elements: str
        required: false
    rulebase:
        description:
            - Which rulebase to query (pre or post).
        type: str
        choices: ['pre', 'post']
        default: 'pre'
        required: false
    folder:
        description:
            - Filter rules by folder name.
            - Required when retrieving rules by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter rules by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter rules by device identifier.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: False
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Security rules must be associated with exactly one container (folder, snippet, or device).
    - The 'from_' and 'to_' parameters map to 'from' and 'to' in the API.
"""

EXAMPLES = r"""
- name: Get all security rules in pre-rulebase
  cdot65.scm.security_rule_info:
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: all_pre_rules

- name: Get all security rules in post-rulebase
  cdot65.scm.security_rule_info:
    folder: "Security-Rules"
    rulebase: "post"
    scm_access_token: "{{ scm_access_token }}"
  register: all_post_rules

- name: Get a specific security rule by ID
  cdot65.scm.security_rule_info:
    id: "12345678-1234-1234-1234-123456789012"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: rule_details

- name: Get security rule with a specific name
  cdot65.scm.security_rule_info:
    name: "Allow-Web-Traffic"
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: named_rule

- name: Get all allow rules
  cdot65.scm.security_rule_info:
    action: ["allow"]
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: allow_rules

- name: Get rules with specific tags
  cdot65.scm.security_rule_info:
    tags: ["web", "external"]
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: tagged_rules

- name: Get rules matching specific source zone
  cdot65.scm.security_rule_info:
    from_: ["trust"]
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: trust_zone_rules

- name: Get rules matching specific destination zone
  cdot65.scm.security_rule_info:
    to_: ["untrust"]
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: untrust_zone_rules

- name: Get disabled rules
  cdot65.scm.security_rule_info:
    disabled: true
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: disabled_rules

- name: Get rules for specific application
  cdot65.scm.security_rule_info:
    application: ["web-browsing", "ssl"]
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: web_rules

- name: Get rules in a specific snippet
  cdot65.scm.security_rule_info:
    snippet: "security-policy"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_rules

- name: Get rules for a specific device
  cdot65.scm.security_rule_info:
    device: "firewall-01"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
  register: device_rules
"""

RETURN = r"""
security_rules:
    description: List of security rule objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The security rule ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The security rule name
            type: str
            returned: always
            sample: "Allow-Web-Traffic"
        description:
            description: The security rule description
            type: str
            returned: when applicable
            sample: "Allow web traffic from trust to untrust"
        disabled:
            description: Whether the rule is disabled
            type: bool
            returned: always
            sample: false
        tag:
            description: Tags associated with the security rule
            type: list
            returned: when applicable
            sample: ["web", "external"]
        from_:
            description: Source security zones
            type: list
            returned: always
            sample: ["trust"]
        source:
            description: Source addresses
            type: list
            returned: always
            sample: ["any"]
        negate_source:
            description: Whether source is negated
            type: bool
            returned: always
            sample: false
        source_user:
            description: Source users/groups
            type: list
            returned: always
            sample: ["any"]
        source_hip:
            description: Source HIP profiles
            type: list
            returned: always
            sample: ["any"]
        to_:
            description: Destination security zones
            type: list
            returned: always
            sample: ["untrust"]
        destination:
            description: Destination addresses
            type: list
            returned: always
            sample: ["any"]
        negate_destination:
            description: Whether destination is negated
            type: bool
            returned: always
            sample: false
        destination_hip:
            description: Destination HIP profiles
            type: list
            returned: always
            sample: ["any"]
        application:
            description: Applications
            type: list
            returned: always
            sample: ["web-browsing", "ssl"]
        service:
            description: Services
            type: list
            returned: always
            sample: ["application-default"]
        category:
            description: URL categories
            type: list
            returned: always
            sample: ["any"]
        action:
            description: Rule action
            type: str
            returned: always
            sample: "allow"
        profile_setting:
            description: Security profile settings
            type: dict
            returned: when applicable
            sample: {"group": ["best-practice"]}
        log_setting:
            description: Log forwarding profile
            type: str
            returned: when applicable
            sample: "default-logging"
        schedule:
            description: Schedule name
            type: str
            returned: when applicable
            sample: "business-hours"
        log_start:
            description: Log at session start
            type: bool
            returned: when applicable
            sample: false
        log_end:
            description: Log at session end
            type: bool
            returned: when applicable
            sample: true
        folder:
            description: The folder containing the security rule
            type: str
            returned: when applicable
            sample: "Security-Rules"
        snippet:
            description: The snippet containing the security rule
            type: str
            returned: when applicable
            sample: "security-policy"
        device:
            description: The device containing the security rule
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        action=dict(type="list", elements="str", required=False),
        category=dict(type="list", elements="str", required=False),
        service=dict(type="list", elements="str", required=False),
        application=dict(type="list", elements="str", required=False),
        destination=dict(type="list", elements="str", required=False),
        to_=dict(type="list", elements="str", required=False),
        source=dict(type="list", elements="str", required=False),
        from_=dict(type="list", elements="str", required=False),
        tags=dict(type="list", elements="str", required=False),
        disabled=dict(type="bool", required=False),
        profile_setting=dict(type="list", elements="str", required=False),
        log_setting=dict(type="list", elements="str", required=False),
        rulebase=dict(type="str", required=False, choices=["pre", "post"], default="pre"),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"security_rules": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get security rule by ID if specified
        if params.get("id"):
            try:
                rule_obj = client.security_rule.get(params.get("id"), rulebase=params.get("rulebase", "pre"))
                if rule_obj:
                    result["security_rules"] = [json.loads(rule_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve security rule info: {e}")
        # Fetch security rule by name
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

                # We need a container for the fetch operation
                if not container_type or not container_name:
                    module.fail_json(
                        msg="When retrieving a security rule by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the security rule object
                rule_obj = client.security_rule.fetch(
                    name=params.get("name"), rulebase=params.get("rulebase", "pre"), **{container_type: container_name}
                )
                if rule_obj:
                    result["security_rules"] = [json.loads(rule_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve security rule info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet, device) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                filter_params["device"] = params.get("device")
            else:
                module.fail_json(
                    msg="At least one container parameter (folder, snippet, or device) is required for listing security rules"
                )

            # Add rulebase parameter
            filter_params["rulebase"] = params.get("rulebase", "pre")

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # Add additional filter parameters from SDK _apply_filters support
            if params.get("action"):
                filter_params["action"] = params.get("action")
            if params.get("category"):
                filter_params["category"] = params.get("category")
            if params.get("service"):
                filter_params["service"] = params.get("service")
            if params.get("application"):
                filter_params["application"] = params.get("application")
            if params.get("destination"):
                filter_params["destination"] = params.get("destination")
            if params.get("to_"):
                filter_params["to_"] = params.get("to_")
            if params.get("source"):
                filter_params["source"] = params.get("source")
            if params.get("from_"):
                filter_params["from_"] = params.get("from_")
            if params.get("tags"):
                filter_params["tag"] = params.get("tags")
            if params.get("disabled") is not None:
                filter_params["disabled"] = params.get("disabled")
            if params.get("profile_setting"):
                filter_params["profile_setting"] = params.get("profile_setting")
            if params.get("log_setting"):
                filter_params["log_setting"] = params.get("log_setting")

            # List security rules with all filters
            rules = client.security_rule.list(**filter_params)

            # Convert to a list of dicts
            rule_dicts = [json.loads(r.model_dump_json(exclude_unset=True)) for r in rules]

            # Add to results
            result["security_rules"] = rule_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve security rule info: {e}")


if __name__ == "__main__":
    main()
