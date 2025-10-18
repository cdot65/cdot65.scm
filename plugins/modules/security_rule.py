#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.security import SecurityRuleCreateModel

DOCUMENTATION = r"""
---
module: security_rule
short_description: Manage security rules in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete security rules in Strata Cloud Manager using pan-scm-sdk.
    - Supports all security rule attributes including zones, addresses, applications, services, and actions.
    - Provides robust idempotency and supports both pre-rulebase and post-rulebase rule management.
    - Security rules must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the security rule.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the security rule.
        type: str
        required: false
    disabled:
        description:
            - Whether the security rule is disabled.
        type: bool
        required: false
        default: false
    tag:
        description:
            - Tags associated with the security rule.
        type: list
        elements: str
        required: false
    from_:
        description:
            - Source security zones.
        type: list
        elements: str
        required: false
        default: ['any']
    source:
        description:
            - Source addresses.
        type: list
        elements: str
        required: false
        default: ['any']
    negate_source:
        description:
            - Negate the source addresses.
        type: bool
        required: false
        default: false
    source_user:
        description:
            - Source users and/or groups.
        type: list
        elements: str
        required: false
        default: ['any']
    source_hip:
        description:
            - Source Host Integrity Profiles (HIP).
        type: list
        elements: str
        required: false
        default: ['any']
    to_:
        description:
            - Destination security zones.
        type: list
        elements: str
        required: false
        default: ['any']
    destination:
        description:
            - Destination addresses.
        type: list
        elements: str
        required: false
        default: ['any']
    negate_destination:
        description:
            - Negate the destination addresses.
        type: bool
        required: false
        default: false
    destination_hip:
        description:
            - Destination Host Integrity Profiles (HIP).
        type: list
        elements: str
        required: false
        default: ['any']
    application:
        description:
            - Applications being accessed.
        type: list
        elements: str
        required: false
        default: ['any']
    service:
        description:
            - Services being accessed.
        type: list
        elements: str
        required: false
        default: ['any']
    category:
        description:
            - URL categories being accessed.
        type: list
        elements: str
        required: false
        default: ['any']
    action:
        description:
            - Action to take when the rule is matched.
        type: str
        choices: ['allow', 'deny', 'drop', 'reset-client', 'reset-server', 'reset-both']
        required: false
        default: 'allow'
    profile_setting:
        description:
            - Security profile settings.
            - This is a dictionary with a 'group' key containing a list of profile group names.
        type: dict
        required: false
    log_setting:
        description:
            - Log forwarding profile name.
        type: str
        required: false
    schedule:
        description:
            - Schedule name.
        type: str
        required: false
    log_start:
        description:
            - Log at session start.
        type: bool
        required: false
    log_end:
        description:
            - Log at session end.
        type: bool
        required: false
    rulebase:
        description:
            - Which rulebase to use (pre or post).
        type: str
        choices: ['pre', 'post']
        required: false
        default: 'pre'
    folder:
        description:
            - The folder in which the security rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the security rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the security rule is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the security rule (UUID).
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
            - Desired state of the security rule.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Security rules must be associated with exactly one container (folder, snippet, or device).
    - The 'from_' and 'to_' parameters map to 'from' and 'to' in the API (required for proper SDK integration).
"""

EXAMPLES = r"""
- name: Create a basic allow rule
  cdot65.scm.security_rule:
    name: "Allow-Web-Traffic"
    description: "Allow web traffic from trust to untrust"
    from_:
      - "trust"
    to_:
      - "untrust"
    source:
      - "any"
    destination:
      - "any"
    application:
      - "web-browsing"
      - "ssl"
    service:
      - "application-default"
    action: "allow"
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a deny rule with profile settings
  cdot65.scm.security_rule:
    name: "Block-Malicious-Traffic"
    description: "Block known malicious IPs"
    from_:
      - "untrust"
    to_:
      - "trust"
    source:
      - "Malicious-IPs"
    destination:
      - "any"
    application:
      - "any"
    service:
      - "any"
    action: "deny"
    log_end: true
    profile_setting:
      group:
        - "best-practice"
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a rule with multiple zones and applications
  cdot65.scm.security_rule:
    name: "Allow-Internal-Services"
    description: "Allow internal application traffic"
    from_:
      - "trust"
      - "internal"
    to_:
      - "dmz"
    source:
      - "Internal-Networks"
    destination:
      - "DMZ-Servers"
    application:
      - "ssl"
      - "web-browsing"
      - "ssh"
    service:
      - "application-default"
    action: "allow"
    tag:
      - "internal"
      - "production"
    log_end: true
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a post-rulebase rule
  cdot65.scm.security_rule:
    name: "Cleanup-Rule"
    description: "Catch-all deny rule"
    from_:
      - "any"
    to_:
      - "any"
    source:
      - "any"
    destination:
      - "any"
    application:
      - "any"
    service:
      - "any"
    action: "deny"
    log_end: true
    folder: "Security-Rules"
    rulebase: "post"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a security rule's action
  cdot65.scm.security_rule:
    name: "Allow-Web-Traffic"
    description: "Allow web traffic from trust to untrust"
    from_:
      - "trust"
    to_:
      - "untrust"
    source:
      - "any"
    destination:
      - "any"
    application:
      - "web-browsing"
      - "ssl"
    service:
      - "application-default"
    action: "deny"
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a security rule by name
  cdot65.scm.security_rule:
    name: "Allow-Web-Traffic"
    folder: "Security-Rules"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a security rule by ID
  cdot65.scm.security_rule:
    id: "12345678-1234-1234-1234-123456789012"
    rulebase: "pre"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
security_rule:
    description: Information about the security rule that was managed
    returned: on success
    type: dict
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
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        disabled=dict(type="bool", required=False, default=False),
        tag=dict(type="list", elements="str", required=False),
        from_=dict(type="list", elements="str", required=False, default=["any"]),
        source=dict(type="list", elements="str", required=False, default=["any"]),
        negate_source=dict(type="bool", required=False, default=False),
        source_user=dict(type="list", elements="str", required=False, default=["any"]),
        source_hip=dict(type="list", elements="str", required=False, default=["any"]),
        to_=dict(type="list", elements="str", required=False, default=["any"]),
        destination=dict(type="list", elements="str", required=False, default=["any"]),
        negate_destination=dict(type="bool", required=False, default=False),
        destination_hip=dict(type="list", elements="str", required=False, default=["any"]),
        application=dict(type="list", elements="str", required=False, default=["any"]),
        service=dict(type="list", elements="str", required=False, default=["any"]),
        category=dict(type="list", elements="str", required=False, default=["any"]),
        action=dict(
            type="str",
            required=False,
            choices=["allow", "deny", "drop", "reset-client", "reset-server", "reset-both"],
            default="allow",
        ),
        profile_setting=dict(type="dict", required=False),
        log_setting=dict(type="str", required=False),
        schedule=dict(type="str", required=False),
        log_start=dict(type="bool", required=False),
        log_end=dict(type="bool", required=False),
        rulebase=dict(type="str", required=False, choices=["pre", "post"], default="pre"),
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
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "security_rule": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize rule_exists boolean
        rule_exists = False
        rule_obj = None

        # Fetch rule by name
        if params.get("name"):
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

                # For any container type, fetch the security rule object
                if container_type and container_name:
                    rule_obj = client.security_rule.fetch(
                        name=params.get("name"), rulebase=params.get("rulebase", "pre"), **{container_type: container_name}
                    )
                    if rule_obj:
                        rule_exists = True
            except ObjectNotPresentError:
                rule_exists = False
                rule_obj = None

        # Create or update or delete a security rule
        if params.get("state") == "present":
            if rule_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # List of simple fields to check for updates
                simple_fields = [
                    "description",
                    "disabled",
                    "tag",
                    "source",
                    "negate_source",
                    "source_user",
                    "source_hip",
                    "destination",
                    "negate_destination",
                    "destination_hip",
                    "application",
                    "service",
                    "category",
                    "action",
                    "log_setting",
                    "schedule",
                    "log_start",
                    "log_end",
                    "folder",
                    "snippet",
                    "device",
                ]

                for field in simple_fields:
                    if params[field] is not None and getattr(rule_obj, field, None) != params[field]:
                        update_fields[field] = params[field]

                # Handle 'from_' and 'to_' special cases (they use aliases in the SDK)
                if params["from_"] is not None and getattr(rule_obj, "from_", None) != params["from_"]:
                    update_fields["from_"] = params["from_"]

                if params["to_"] is not None and getattr(rule_obj, "to_", None) != params["to_"]:
                    update_fields["to_"] = params["to_"]

                # Handle profile_setting special case (it's a nested dict)
                if params["profile_setting"] is not None:
                    current_profile = getattr(rule_obj, "profile_setting", None)
                    if current_profile is None or (
                        hasattr(current_profile, "group") and current_profile.group != params["profile_setting"].get("group")
                    ):
                        update_fields["profile_setting"] = params["profile_setting"]

                # Update the rule if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = rule_obj.model_copy(update=update_fields)
                        updated = client.security_rule.update(update_model, rulebase=params.get("rulebase", "pre"))
                        result["security_rule"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["security_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["security_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new security rule object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "disabled",
                        "tag",
                        "from_",
                        "source",
                        "negate_source",
                        "source_user",
                        "source_hip",
                        "to_",
                        "destination",
                        "negate_destination",
                        "destination_hip",
                        "application",
                        "service",
                        "category",
                        "action",
                        "profile_setting",
                        "log_setting",
                        "schedule",
                        "log_start",
                        "log_end",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a security rule object
                if not module.check_mode:
                    # Create a security rule object
                    created = client.security_rule.create(create_payload, rulebase=params.get("rulebase", "pre"))

                    # Return the created security rule object
                    result["security_rule"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created security rule object (minimal info)
                    simulated = SecurityRuleCreateModel(**create_payload)
                    result["security_rule"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a security rule object
        elif params.get("state") == "absent":
            if rule_exists:
                if not module.check_mode:
                    client.security_rule.delete(rule_obj.id, rulebase=params.get("rulebase", "pre"))

                # Mark as changed
                result["changed"] = True

                # Exit
                result["security_rule"] = json.loads(rule_obj.model_dump_json(exclude_unset=True))
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
