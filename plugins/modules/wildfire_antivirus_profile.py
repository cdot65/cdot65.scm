#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import Scm as ScmClient
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.security import WildfireAvProfileCreateModel

DOCUMENTATION = r"""
---
module: wildfire_antivirus_profile
short_description: Manage WildFire Antivirus profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete WildFire Antivirus security profiles in Strata Cloud Manager using pan-scm-sdk.
    - WildFire Antivirus profiles define malware analysis and prevention settings.
    - Supports rules with file type matching, analysis types, and MLAV exceptions.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the WildFire Antivirus profile.
            - Required for both state=present and state=absent.
        type: str
        required: false
    description:
        description:
            - Description of the WildFire Antivirus profile.
        type: str
        required: false
    packet_capture:
        description:
            - Enable packet capture for the profile.
        type: bool
        required: false
        default: false
    rules:
        description:
            - List of WildFire antivirus rules.
            - Each rule defines analysis settings for specific applications and file types.
            - At least one rule is required when creating a profile.
        type: list
        elements: dict
        required: false
    mlav_exception:
        description:
            - List of Machine Learning Antivirus (MLAV) exceptions.
            - Each exception is a dictionary with name, description, and filename.
        type: list
        elements: dict
        required: false
    threat_exception:
        description:
            - List of threat exceptions.
            - Each exception is a dictionary with name and notes.
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
            - Unique identifier for the WildFire Antivirus profile (UUID).
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
            - Desired state of the WildFire Antivirus profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided for state=present.
    - Rules structure requires name, direction, and optionally analysis, application, and file_type.
"""

EXAMPLES = r"""
- name: Create a basic WildFire Antivirus profile
  cdot65.scm.wildfire_antivirus_profile:
    name: "Example-Basic-WildFire"
    description: "Basic WildFire antivirus profile"
    packet_capture: false
    rules:
      - name: "rule1"
        direction: "both"
        analysis: "public-cloud"
        application:
          - "any"
        file_type:
          - "any"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create advanced WildFire profile with multiple rules
  cdot65.scm.wildfire_antivirus_profile:
    name: "Example-Advanced-WildFire"
    description: "Advanced WildFire with multiple rules"
    packet_capture: true
    rules:
      - name: "download-rule"
        direction: "download"
        analysis: "public-cloud"
        application:
          - "web-browsing"
          - "ssl"
        file_type:
          - "pe"
          - "pdf"
      - name: "upload-rule"
        direction: "upload"
        analysis: "public-cloud"
        application:
          - "any"
        file_type:
          - "any"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with MLAV exceptions
  cdot65.scm.wildfire_antivirus_profile:
    name: "Example-MLAV-Exceptions"
    description: "Profile with MLAV exceptions"
    packet_capture: false
    rules:
      - name: "rule1"
        direction: "both"
        analysis: "public-cloud"
        application:
          - "any"
        file_type:
          - "any"
    mlav_exception:
      - name: "trusted-app"
        description: "Trusted application exception"
        filename: "trusted_app.exe"
      - name: "internal-tool"
        description: "Internal tool exception"
        filename: "internal_tool.dll"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create profile with threat exceptions
  cdot65.scm.wildfire_antivirus_profile:
    name: "Example-Threat-Exceptions"
    description: "Profile with threat exceptions"
    packet_capture: false
    rules:
      - name: "rule1"
        direction: "both"
        analysis: "public-cloud"
        application:
          - "any"
        file_type:
          - "any"
    threat_exception:
      - name: "known-false-positive"
        notes: "Known false positive from vendor software"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete WildFire Antivirus profile
  cdot65.scm.wildfire_antivirus_profile:
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
wildfire_antivirus_profile:
    description: The created, updated, or deleted WildFire Antivirus profile.
    returned: when state=present
    type: dict
    sample:
        id: "123e4567-e89b-12d3-a456-426655440000"
        name: "Example-Basic-WildFire"
        description: "Basic WildFire antivirus profile"
        folder: "Texas"
        packet_capture: false
        rules:
          - name: "rule1"
            direction: "both"
            analysis: "public-cloud"
            application:
              - "any"
            file_type:
              - "any"
"""


def main():
    """Main module execution."""
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        packet_capture=dict(type="bool", required=False, default=False),
        rules=dict(type="list", elements="dict", required=False),
        mlav_exception=dict(type="list", elements="dict", required=False),
        threat_exception=dict(type="list", elements="dict", required=False),
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
        "wildfire_antivirus_profile": {},
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
            existing_profile = client.wildfire_antivirus_profile.fetch(profile_id)
        except ObjectNotPresentError:
            existing_profile = None
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by ID: {e!s}")
    elif profile_name and container_type:
        # Lookup by name and container
        try:
            existing_profile = client.wildfire_antivirus_profile.fetch(name=profile_name, **lookup_params)
        except ObjectNotPresentError:
            existing_profile = None
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by name: {e!s}")

    if state == "absent":
        if existing_profile:
            if not module.check_mode:
                try:
                    client.wildfire_antivirus_profile.delete(str(existing_profile.id))
                    result["msg"] = f"WildFire Antivirus profile '{profile_name or profile_id}' deleted successfully"
                except APIError as e:
                    module.fail_json(msg=f"Failed to delete profile: {e!s}")
            else:
                result["msg"] = f"Would delete WildFire Antivirus profile '{profile_name or profile_id}'"
            result["changed"] = True
        else:
            result["msg"] = f"WildFire Antivirus profile '{profile_name or profile_id}' not found, nothing to delete"
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

    if params.get("description"):
        profile_data["description"] = params["description"]

    if params.get("packet_capture") is not None:
        profile_data["packet_capture"] = params["packet_capture"]

    if params.get("rules"):
        profile_data["rules"] = params["rules"]
    elif not existing_profile:
        # Rules are required when creating a new profile
        module.fail_json(msg="'rules' parameter is required when creating a new WildFire Antivirus profile")

    if params.get("mlav_exception"):
        profile_data["mlav_exception"] = params["mlav_exception"]

    if params.get("threat_exception"):
        profile_data["threat_exception"] = params["threat_exception"]

    # Validate and prepare the profile data using SDK models
    try:
        profile_model = WildfireAvProfileCreateModel(**profile_data)
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

        # Compare description
        if getattr(existing_profile, "description", None) != profile_data.get("description"):
            needs_update = True
            update_fields.append("description")

        # Compare packet_capture
        if getattr(existing_profile, "packet_capture", False) != profile_data.get("packet_capture", False):
            needs_update = True
            update_fields.append("packet_capture")

        # Compare rules
        existing_rules = getattr(existing_profile, "rules", [])
        if existing_rules != profile_data.get("rules", []):
            needs_update = True
            update_fields.append("rules")

        # Compare mlav_exception
        existing_mlav = getattr(existing_profile, "mlav_exception", [])
        if existing_mlav != profile_data.get("mlav_exception", []):
            needs_update = True
            update_fields.append("mlav_exception")

        # Compare threat_exception
        existing_threat = getattr(existing_profile, "threat_exception", [])
        if existing_threat != profile_data.get("threat_exception", []):
            needs_update = True
            update_fields.append("threat_exception")

        if needs_update:
            if not module.check_mode:
                try:
                    profile_data["id"] = str(existing_profile.id)
                    updated_profile = client.wildfire_antivirus_profile.update(existing_profile)
                    result["wildfire_antivirus_profile"] = json.loads(updated_profile.model_dump_json())
                    result["msg"] = f"WildFire Antivirus profile '{profile_name}' updated: {', '.join(update_fields)}"
                except APIError as e:
                    module.fail_json(msg=f"Failed to update profile: {e!s}")
            else:
                result["wildfire_antivirus_profile"] = profile_data
                result["msg"] = f"Would update WildFire Antivirus profile '{profile_name}': {', '.join(update_fields)}"
            result["changed"] = True
        else:
            result["wildfire_antivirus_profile"] = json.loads(existing_profile.model_dump_json())
            result["msg"] = f"WildFire Antivirus profile '{profile_name}' already exists with correct configuration"
    else:
        # Create new profile
        if not module.check_mode:
            try:
                created_profile = client.wildfire_antivirus_profile.create(profile_data)
                result["wildfire_antivirus_profile"] = json.loads(created_profile.model_dump_json())
                result["msg"] = f"WildFire Antivirus profile '{profile_name}' created successfully"
            except APIError as e:
                module.fail_json(msg=f"Failed to create profile: {e!s}")
        else:
            result["wildfire_antivirus_profile"] = profile_data
            result["msg"] = f"Would create WildFire Antivirus profile '{profile_name}'"
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()
