#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import LogForwardingProfileCreateModel

DOCUMENTATION = r"""
---
module: log_forwarding_profile
short_description: Manage log forwarding profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete log forwarding profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports all log forwarding profile attributes and robust idempotency.
    - Log forwarding profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the log forwarding profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the log forwarding profile.
            - Maximum length is 255 characters.
        type: str
        required: false
    match_list:
        description:
            - List of match profile configurations.
            - Each match profile can handle a specific log type with custom filters and forwarding destinations.
        type: list
        elements: dict
        required: false
        suboptions:
            name:
                description:
                    - Name of the match profile.
                    - Maximum length is 63 characters.
                type: str
                required: true
            action_desc:
                description:
                    - Match profile description.
                    - Maximum length is 255 characters.
                type: str
                required: false
            log_type:
                description:
                    - Log type for matching.
                type: str
                required: true
                choices: ["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption"]
            filter:
                description:
                    - Filter match criteria.
                    - Used to define which logs of the specified type should be forwarded.
                    - Maximum length is 65535 characters.
                type: str
                required: false
            send_http:
                description:
                    - A list of HTTP server profile names to forward logs to.
                type: list
                elements: str
                required: false
            send_syslog:
                description:
                    - A list of syslog server profile names to forward logs to.
                type: list
                elements: str
                required: false
            send_to_panorama:
                description:
                    - Flag to send logs to Panorama.
                type: bool
                required: false
            quarantine:
                description:
                    - Flag to quarantine matching logs.
                    - Default is False.
                type: bool
                required: false
                default: false
    enhanced_application_logging:
        description:
            - Flag for enhanced application logging.
            - Enables more detailed application information in logs.
        type: bool
        required: false
    folder:
        description:
            - The folder in which the log forwarding profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the log forwarding profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the log forwarding profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the log forwarding profile (UUID).
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
            - Desired state of the log forwarding profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Log forwarding profiles must be associated with exactly one container (folder, snippet, or device).
    - Match list configurations are required when creating a new log forwarding profile.
"""

EXAMPLES = r"""
---
- name: Create a log forwarding profile for traffic logs
  cdot65.scm.log_forwarding_profile:
    name: "traffic-log-profile"
    description: "Profile for traffic logs"
    match_list:
      - name: "internal-traffic"
        log_type: "traffic"
        filter: "addr.src in 192.168.0.0/24"
        send_http: ["http-profile-1"]
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a profile with multiple match items
  cdot65.scm.log_forwarding_profile:
    name: "security-logs-profile"
    description: "Profile for security-related logs"
    match_list:
      - name: "critical-threats"
        log_type: "threat"
        filter: "severity eq critical"
        send_http: ["security-http-profile"]
        send_syslog: ["security-syslog-profile"]
      - name: "malware-logs"
        log_type: "wildfire"
        filter: "verdict eq malware"
        send_http: ["malware-http-profile"]
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a profile with enhanced application logging
  cdot65.scm.log_forwarding_profile:
    name: "enhanced-app-logs"
    description: "Profile with enhanced application logging"
    enhanced_application_logging: true
    match_list:
      - name: "app-traffic"
        log_type: "traffic"
        send_http: ["app-http-profile"]
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an existing log forwarding profile
  cdot65.scm.log_forwarding_profile:P
    name: "traffic-log-profile"
    description: "Updated profile for traffic logs"
    match_list:
      - name: "updated-match"
        log_type: "traffic"
        filter: "addr.src in 10.0.0.0/8"
        send_http: ["updated-http-profile"]
      - name: "new-match"
        log_type: "url"
        filter: "category eq social-networking"
        send_syslog: ["url-syslog-profile"]
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a log forwarding profile by name
  cdot65.scm.log_forwarding_profile:
    name: "traffic-log-profile"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a log forwarding profile by ID
  cdot65.scm.log_forwarding_profile:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
log_forwarding_profile:
    description: Information about the log forwarding profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The log forwarding profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The log forwarding profile name
            type: str
            returned: always
            sample: "traffic-log-profile"
        description:
            description: Profile description
            type: str
            returned: when configured
            sample: "Profile for traffic logs"
        match_list:
            description: List of match profile configurations
            type: list
            returned: when configured
            contains:
                name:
                    description: Match profile name
                    type: str
                    returned: always
                    sample: "internal-traffic"
                action_desc:
                    description: Match profile description
                    type: str
                    returned: when configured
                    sample: "Internal traffic logging config"
                log_type:
                    description: Log type for matching
                    type: str
                    returned: always
                    sample: "traffic"
                filter:
                    description: Filter match criteria
                    type: str
                    returned: when configured
                    sample: "addr.src in 192.168.0.0/24"
                send_http:
                    description: HTTP server profiles for forwarding
                    type: list
                    returned: when configured
                    sample: ["http-profile-1"]
                send_syslog:
                    description: Syslog server profiles for forwarding
                    type: list
                    returned: when configured
                    sample: ["syslog-profile-1"]
                send_to_panorama:
                    description: Flag to send logs to Panorama
                    type: bool
                    returned: when configured
                    sample: true
                quarantine:
                    description: Flag to quarantine matching logs
                    type: bool
                    returned: when configured
                    sample: false
        enhanced_application_logging:
            description: Flag for enhanced application logging
            type: bool
            returned: when configured
            sample: true
        folder:
            description: The folder containing the log forwarding profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the log forwarding profile
            type: str
            returned: when applicable
            sample: "log-forwarding"
        device:
            description: The device containing the log forwarding profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        match_list=dict(
            type="list",
            elements="dict",
            required=False,
            options=dict(
                name=dict(type="str", required=True),
                action_desc=dict(type="str", required=False),
                log_type=dict(
                    type="str",
                    required=True,
                    choices=[
                        "traffic",
                        "threat",
                        "wildfire",
                        "url",
                        "data",
                        "tunnel",
                        "auth",
                        "decryption",
                        "dns-security",
                    ],
                ),
                filter=dict(type="str", required=False),
                send_http=dict(type="list", elements="str", required=False),
                send_syslog=dict(type="list", elements="str", required=False),
                send_to_panorama=dict(type="bool", required=False),
                quarantine=dict(type="bool", required=False, default=False),
            ),
        ),
        enhanced_application_logging=dict(type="bool", required=False),
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
            ["state", "absent", ["name"]],
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for a match_list parameter
    if params.get("state") == "present":
        # For creation/update, validate match_list parameter
        if not params.get("match_list"):
            module.fail_json(msg="When state=present, the match_list parameter is required")

        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False, "log_forwarding_profile": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize profile_exists boolean
        profile_exists = False
        profile_obj = None

        # Check if a log_forwarding_profile exists by name
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

                # For any container type, fetch the log forwarding profile
                if container_type and container_name:
                    try:
                        profile_obj = client.log_forwarding_profile.fetch(
                            name=params.get("name"),
                            **{container_type: container_name},
                        )
                    except ObjectNotPresentError:
                        profile_obj = None
                    except InvalidObjectError:
                        profile_obj = None

                if profile_obj:
                    profile_exists = True
            except ObjectNotPresentError:
                profile_exists = False
                profile_obj = None

        # Create or update or delete a log_forwarding_profile
        if params.get("state") == "present":
            if profile_exists:
                # Process match list for comparison
                match_list = None
                if params.get("match_list"):
                    match_list = []
                    for match_item in params.get("match_list"):
                        # Filter out None values
                        match_dict = {k: v for k, v in match_item.items() if v is not None}
                        match_list.append(match_dict)

                    # Sort for consistent comparison
                    match_list.sort(key=lambda x: x.get("name", ""))

                # Get the current match list for comparison
                current_match_list = None
                if hasattr(profile_obj, "match_list") and profile_obj.match_list:
                    current_match_list = []
                    for match in profile_obj.match_list:
                        match_dict = match.model_dump(exclude_unset=True)
                        current_match_list.append(match_dict)

                    # Sort for consistent comparison
                    current_match_list.sort(key=lambda x: x.get("name", ""))

                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "enhanced_application_logging",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(profile_obj, k, None) != params[k]
                }

                # Add match_list if it differs
                if match_list is not None and current_match_list != match_list:
                    update_fields["match_list"] = match_list

                # Update the profile if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = profile_obj.model_copy(update=update_fields)
                            updated = client.log_forwarding_profile.update(update_model)
                            result["log_forwarding_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid log forwarding profile object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating log forwarding profile: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, return the existing object with projected changes
                        result["log_forwarding_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["log_forwarding_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create a payload for a new log forwarding profile object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "enhanced_application_logging",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Process match_list configuration
                if params.get("match_list"):
                    match_list = []
                    for match_item in params.get("match_list"):
                        # Filter out None values
                        match_dict = {k: v for k, v in match_item.items() if v is not None}
                        match_list.append(match_dict)
                    create_payload["match_list"] = match_list

                # Create a log_forwarding_profile object
                if not module.check_mode:
                    try:
                        # Create profile
                        created = client.log_forwarding_profile.create(create_payload)

                        # Return the created profile object
                        result["log_forwarding_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid log forwarding profile object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating log forwarding profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = LogForwardingProfileCreateModel(**create_payload)
                    result["log_forwarding_profile"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        # Handle absent state - delete the profile
        elif params.get("state") == "absent":
            if profile_exists:
                if not module.check_mode:
                    try:
                        # We can only delete using the ID from the fetched profile
                        client.log_forwarding_profile.delete(profile_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting log forwarding profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["log_forwarding_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                module.exit_json(**result)
            else:
                # Already absent - this means it wasn't found by name in the container
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
