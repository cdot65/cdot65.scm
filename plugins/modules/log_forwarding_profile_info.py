#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: log_forwarding_profile_info
short_description: Retrieve information about log forwarding profiles in Strata Cloud Manager (SCM)
description:
    - Retrieve information about log forwarding profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single profile by ID or name, or listing multiple profiles with optional filtering.
    - Log forwarding profiles are associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the log forwarding profile to retrieve.
            - Used for exact match lookup.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the log forwarding profile (UUID).
            - Used for exact match lookup.
            - Mutually exclusive with I(name).
        type: str
        required: false
    log_type:
        description:
            - Filter log forwarding profiles by log type.
            - Only applied when retrieving multiple profiles.
            - Can be a single log type or a list of log types.
        type: str
        required: false
        choices: ["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption"]
    log_types:
        description:
            - Filter log forwarding profiles by multiple log types.
            - Only applied when retrieving multiple profiles.
        type: list
        elements: str
        required: false
    folder:
        description:
            - The folder in which to look for log forwarding profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for log forwarding profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to look for log forwarding profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(snippet).
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
notes:
    - When retrieving a single profile, either name or id must be provided.
    - When retrieving multiple profiles, additional filters can be used.
    - Exactly one container parameter (folder, snippet, or device) must be provided.
    - Check mode is supported but makes no changes.
"""

EXAMPLES = r"""
---
- name: Get all log forwarding profiles in a folder
  cdot65.scm.log_forwarding_profile_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: log_profiles

- name: Get log forwarding profile by ID
  cdot65.scm.log_forwarding_profile_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: log_profile

- name: Get log forwarding profile by name
  cdot65.scm.log_forwarding_profile_info:
    name: "traffic-log-profile"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: log_profile

- name: Get all traffic log profiles
  cdot65.scm.log_forwarding_profile_info:
    folder: "Shared"
    log_type: traffic
    scm_access_token: "{{ scm_access_token }}"
  register: traffic_profiles

- name: Get security log profiles (multiple log types)
  cdot65.scm.log_forwarding_profile_info:
    folder: "Shared"
    log_types: ["threat", "wildfire"]
    scm_access_token: "{{ scm_access_token }}"
  register: security_profiles

- name: Get all profiles in a snippet
  cdot65.scm.log_forwarding_profile_info:
    snippet: "logging-config"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_profiles
"""

RETURN = r"""
log_forwarding_profiles:
    description: List of log forwarding profiles when multiple profiles are retrieved
    returned: when no id or name is specified
    type: list
    elements: dict
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
log_forwarding_profile:
    description: Information about a specific log forwarding profile
    returned: when id or name is specified and profile exists
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
        id=dict(type="str", required=False),
        log_type=dict(
            type="str",
            required=False,
            choices=["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption", "dns-security"],
        ),
        log_types=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["name", "id"],
            ["folder", "snippet", "device"],
            ["log_type", "log_types"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params
    profile_name = params.get("name")
    profile_id = params.get("id")

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

        # Retrieve a specific profile by ID or name
        if profile_id or profile_name:
            try:
                if profile_id:
                    # Fetch by ID
                    profile = client.log_forwarding_profile.get(profile_id)
                elif profile_name:
                    # Fetch by name within the specified container
                    profile = client.log_forwarding_profile.fetch(name=profile_name, **{container_type: container_value})

                # Get the profile data and convert it to a dictionary
                profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))

                # Return the profile information
                result["log_forwarding_profile"] = profile_dict
            except ObjectNotPresentError:
                if profile_id:
                    module.fail_json(msg=f"Log forwarding profile with ID '{profile_id}' not found")
                else:
                    module.fail_json(msg=f"Log forwarding profile with name '{profile_name}' not found in the specified container")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )
        else:
            # Retrieve multiple profiles with optional filtering
            try:
                # Build filter parameters for API call
                filter_params = {container_type: container_value}

                # Save the user's filter values for client-side filtering
                user_log_type = params.get("log_type")
                user_log_types = params.get("log_types")

                # Build log_type filter for API call if client supports it
                if user_log_type:
                    filter_params["log_type"] = user_log_type
                elif user_log_types:
                    filter_params["log_types"] = user_log_types

                try:
                    # Fetch profiles
                    profiles = client.log_forwarding_profile.list(**filter_params)
                    
                    # Convert to list of dictionaries
                    profiles_list = [json.loads(profile.model_dump_json(exclude_unset=True)) for profile in profiles]
                    result["log_forwarding_profiles"] = profiles_list
                except Exception as e:
                    # Report the error but return an empty list
                    module.warn(f"Warning: Error listing log forwarding profiles: {str(e)}")
                    result["log_forwarding_profiles"] = []
                    result["warning"] = f"Error listing log forwarding profiles: {str(e)}"
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
