#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.security import AntiSpywareProfileCreateModel

DOCUMENTATION = r"""
---
module: anti_spyware_profile
short_description: Manage Anti-Spyware profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete Anti-Spyware security profiles in Strata Cloud Manager using pan-scm-sdk.
    - Anti-Spyware profiles define protection against spyware threats.
    - Supports rules, threat exceptions, and MICA engine configuration.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the Anti-Spyware profile.
            - Required for both state=present and state=absent.
        type: str
        required: false
    description:
        description:
            - Description of the Anti-Spyware profile.
        type: str
        required: false
    rules:
        description:
            - List of anti-spyware rules.
            - Each rule is a dictionary with severity, category, threat_name, packet_capture, and action.
            - At least one rule is required when creating a profile.
        type: list
        elements: dict
        required: false
    cloud_inline_analysis:
        description:
            - Enable cloud inline analysis.
        type: bool
        required: false
        default: false
    inline_exception_edl_url:
        description:
            - List of inline exception EDL URLs.
        type: list
        elements: str
        required: false
    inline_exception_ip_address:
        description:
            - List of inline exception IP addresses.
        type: list
        elements: str
        required: false
    mica_engine_spyware_enabled:
        description:
            - List of MICA engine spyware enabled entries.
            - Each entry is a dictionary with 'name' and 'inline_policy_action'.
        type: list
        elements: dict
        required: false
    threat_exception:
        description:
            - List of threat exceptions.
            - Each exception is a dictionary defining threat-specific overrides.
        type: list
        elements: dict
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
            - Unique identifier for the Anti-Spyware profile (UUID).
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
            - Desired state of the Anti-Spyware profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided for state=present.
    - Rules structure is complex - see examples for proper formatting.
"""

EXAMPLES = r"""
- name: Create a basic Anti-Spyware profile
  cdot65.scm.anti_spyware_profile:
    name: "Strict-Anti-Spyware"
    description: "Strict anti-spyware protection profile"
    rules:
      - name: "block-critical-high-medium"
        severity:
          - "critical"
          - "high"
          - "medium"
        category: "any"
        action:
          reset_both: {}
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create Anti-Spyware profile with multiple rules
  cdot65.scm.anti_spyware_profile:
    name: "Balanced-Anti-Spyware"
    description: "Balanced anti-spyware profile"
    rules:
      - name: "block-critical-high"
        severity:
          - "critical"
          - "high"
        category: "any"
        action:
          reset_both: {}
      - name: "alert-medium"
        severity:
          - "medium"
        category: "any"
        action:
          alert: {}
      - name: "allow-low-info"
        severity:
          - "low"
          - "informational"
        category: "any"
        action:
          default: {}
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with cloud inline analysis
  cdot65.scm.anti_spyware_profile:
    name: "Cloud-Enhanced-Protection"
    description: "Anti-spyware with cloud analysis"
    cloud_inline_analysis: true
    rules:
      - name: "block-critical"
        severity:
          - "critical"
        category: "any"
        action:
          reset_both: {}
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update Anti-Spyware profile description
  cdot65.scm.anti_spyware_profile:
    name: "Strict-Anti-Spyware"
    description: "Updated strict anti-spyware protection"
    rules:
      - name: "block-critical-high-medium"
        severity:
          - "critical"
          - "high"
          - "medium"
        category: "any"
        action:
          reset_both: {}
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an Anti-Spyware profile
  cdot65.scm.anti_spyware_profile:
    name: "Old-Profile"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
anti_spyware_profile:
    description: Information about the Anti-Spyware profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The profile ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The profile name
            type: str
            returned: always
            sample: "Strict-Anti-Spyware"
        description:
            description: The profile description
            type: str
            returned: when applicable
            sample: "Strict anti-spyware protection profile"
        rules:
            description: List of anti-spyware rules
            type: list
            returned: always
            sample: [{"name": "block-critical-high-medium", "severity": ["critical", "high", "medium"]}]
        cloud_inline_analysis:
            description: Cloud inline analysis enabled
            type: bool
            returned: when applicable
            sample: false
        folder:
            description: The folder containing the profile
            type: str
            returned: when applicable
            sample: "Texas"
        snippet:
            description: The snippet containing the profile
            type: str
            returned: when applicable
            sample: "Security-Profiles"
        device:
            description: The device containing the profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        rules=dict(type="list", elements="dict", required=False),
        cloud_inline_analysis=dict(type="bool", required=False, default=False),
        inline_exception_edl_url=dict(type="list", elements="str", required=False),
        inline_exception_ip_address=dict(type="list", elements="str", required=False),
        mica_engine_spyware_enabled=dict(type="list", elements="dict", required=False),
        threat_exception=dict(type="list", elements="dict", required=False),
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
            ["state", "present", ["name", "rules"], True],  # name and rules required for present
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
    result = {"changed": False, "anti_spyware_profile": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize profile_exists boolean
        profile_exists = False
        profile_obj = None

        # Fetch profile by name
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

                # For any container type, fetch the profile object
                if container_type and container_name:
                    profile_obj = client.anti_spyware_profile.fetch(name=params.get("name"), **{container_type: container_name})
                    if profile_obj:
                        profile_exists = True
            except ObjectNotPresentError:
                profile_exists = False
                profile_obj = None

        # Create or update or delete a profile
        if params.get("state") == "present":
            if profile_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "rules",
                        "cloud_inline_analysis",
                        "inline_exception_edl_url",
                        "inline_exception_ip_address",
                        "mica_engine_spyware_enabled",
                        "threat_exception",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(profile_obj, k, None) != params[k]
                }

                # Update the profile if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = profile_obj.model_copy(update=update_fields)
                        updated = client.anti_spyware_profile.update(update_model)
                        result["anti_spyware_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["anti_spyware_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["anti_spyware_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new profile object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "rules",
                        "cloud_inline_analysis",
                        "inline_exception_edl_url",
                        "inline_exception_ip_address",
                        "mica_engine_spyware_enabled",
                        "threat_exception",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a profile object
                if not module.check_mode:
                    # Create a profile object
                    created = client.anti_spyware_profile.create(create_payload)

                    # Return the created profile object
                    result["anti_spyware_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created profile object (minimal info)
                    simulated = AntiSpywareProfileCreateModel(**create_payload)
                    result["anti_spyware_profile"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a profile object
        elif params.get("state") == "absent":
            if profile_exists:
                if not module.check_mode:
                    client.anti_spyware_profile.delete(profile_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["anti_spyware_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
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
