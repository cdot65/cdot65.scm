#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: syslog_server_profile_info
short_description: Get information about syslog server profiles in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about syslog server profiles in Strata Cloud Manager.
    - It can be used to get details about a specific syslog server profile by ID or name, or to list all profiles.
    - Supports filtering by folder, snippet, or device container.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the syslog server profile to retrieve.
            - If specified, the module will return information about this specific profile.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the syslog server profile to retrieve.
            - If specified, the module will search for profiles with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    folder:
        description:
            - Filter syslog server profiles by folder name.
            - Required when retrieving profiles by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter syslog server profiles by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter syslog server profiles by device identifier.
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
        no_log: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Syslog server profile objects must be associated with exactly one container (folder, snippet, or device).
"""

EXAMPLES = r"""
- name: Get all syslog server profiles in a folder
  cdot65.scm.syslog_server_profile_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: all_profiles

- name: Get a specific syslog server profile by ID
  cdot65.scm.syslog_server_profile_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: profile_details

- name: Get syslog server profile with a specific name
  cdot65.scm.syslog_server_profile_info:
    name: "production-syslog"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: named_profile

- name: Get syslog server profiles in a specific snippet
  cdot65.scm.syslog_server_profile_info:
    snippet: "security-logging"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_profiles

- name: Get syslog server profiles for a specific device
  cdot65.scm.syslog_server_profile_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_profiles

- name: Get syslog server profile with exact container match
  cdot65.scm.syslog_server_profile_info:
    folder: "Shared"
    exact_match: true
    scm_access_token: "{{ scm_access_token }}"
  register: exact_profiles
"""

RETURN = r"""
syslog_server_profiles:
    description: List of syslog server profile objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The syslog server profile object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The syslog server profile name
            type: str
            returned: always
            sample: "production-syslog"
        server:
            description: List of syslog server configurations
            type: list
            returned: always
            elements: dict
            contains:
                name:
                    description: Syslog server name
                    type: str
                    returned: always
                    sample: "syslog-server-1"
                server:
                    description: Syslog server address
                    type: str
                    returned: always
                    sample: "192.168.1.100"
                transport:
                    description: Transport protocol for the syslog server
                    type: str
                    returned: always
                    sample: "UDP"
                port:
                    description: Syslog server port
                    type: int
                    returned: always
                    sample: 514
                format:
                    description: Syslog format
                    type: str
                    returned: always
                    sample: "BSD"
                facility:
                    description: Syslog facility
                    type: str
                    returned: always
                    sample: "LOG_USER"
        format:
            description: Format settings for different log types
            type: dict
            returned: when applicable
            contains:
                escaping:
                    description: Character escaping configuration
                    type: dict
                    returned: when applicable
                    contains:
                        escape_character:
                            description: Escape sequence delimiter
                            type: str
                            returned: when applicable
                            sample: "\\"
                        escaped_characters:
                            description: List of characters to be escaped
                            type: str
                            returned: when applicable
                            sample: "\\n\\t"
                traffic:
                    description: Format for traffic logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $src $dst"
                threat:
                    description: Format for threat logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $threatid"
                wildfire:
                    description: Format for wildfire logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $filedigest"
                url:
                    description: Format for URL logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $url"
                data:
                    description: Format for data logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $data"
                gtp:
                    description: Format for GTP logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $gtp"
                sctp:
                    description: Format for SCTP logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $sctp"
                tunnel:
                    description: Format for tunnel logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $tunnel"
                auth:
                    description: Format for authentication logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $user"
                userid:
                    description: Format for user ID logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $userid"
                iptag:
                    description: Format for IP tag logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $iptag"
                decryption:
                    description: Format for decryption logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $sessionid"
                config:
                    description: Format for configuration logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $cmd"
                system:
                    description: Format for system logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $module"
                globalprotect:
                    description: Format for GlobalProtect logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $user"
                hip_match:
                    description: Format for HIP match logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $matchname"
                correlation:
                    description: Format for correlation logs
                    type: str
                    returned: when applicable
                    sample: "$time_generated $object"
        folder:
            description: The folder containing the syslog server profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the syslog server profile
            type: str
            returned: when applicable
            sample: "security-logging"
        device:
            description: The device containing the syslog server profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
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

    result = {"syslog_server_profiles": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get syslog server profile by ID if specified
        if params.get("id"):
            try:
                profile_obj = client.syslog_server_profile.get(params.get("id"))
                if profile_obj:
                    result["syslog_server_profiles"] = [json.loads(profile_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve syslog server profile info: {e}")
        # Fetch syslog server profile by name
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
                        msg="When retrieving a syslog server profile by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the syslog server profile object
                profile_obj = client.syslog_server_profile.fetch(name=params.get("name"), **{container_type: container_name})
                if profile_obj:
                    result["syslog_server_profiles"] = [json.loads(profile_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve syslog server profile info: {e}")

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
                    msg="At least one container parameter (folder, snippet, or device) is required for listing syslog server profiles"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List syslog server profiles with container filters
            profiles = client.syslog_server_profile.list(**filter_params)

            # Convert to a list of dicts
            profile_dicts = [json.loads(p.model_dump_json(exclude_unset=True)) for p in profiles]

            # Add to results
            result["syslog_server_profiles"] = profile_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve syslog server profile info: {e}")


if __name__ == "__main__":
    main()
