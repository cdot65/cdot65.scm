#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects.syslog_server_profiles import (
    SyslogServerProfileCreateModel,
)

DOCUMENTATION = r"""
---
module: syslog_server_profile
short_description: Manage syslog server profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete syslog server profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports all syslog server profile attributes and robust idempotency.
    - Syslog server profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the syslog server profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
        type: str
        required: false
    server:
        description:
            - List of syslog server configurations.
            - Required for state=present.
            - Each server must contain name, server, transport, port, format, and facility.
        type: list
        elements: dict
        required: false
        suboptions:
            name:
                description:
                    - Name of the syslog server.
                type: str
                required: true
            server:
                description:
                    - IP address or hostname of the syslog server.
                type: str
                required: true
            transport:
                description:
                    - Transport protocol for the syslog server.
                type: str
                required: true
                choices: ['UDP', 'TCP']
            port:
                description:
                    - Port number for the syslog server.
                    - Must be between 1 and 65535.
                type: int
                required: true
            format:
                description:
                    - Syslog message format.
                type: str
                required: true
                choices: ['BSD', 'IETF']
            facility:
                description:
                    - Syslog facility.
                type: str
                required: true
                choices: ['LOG_USER', 'LOG_LOCAL0', 'LOG_LOCAL1', 'LOG_LOCAL2', 'LOG_LOCAL3', 'LOG_LOCAL4', 'LOG_LOCAL5', 'LOG_LOCAL6', 'LOG_LOCAL7']
    format:
        description:
            - Format settings for different log types.
            - Optional configuration for log formatting and character escaping.
        type: dict
        required: false
        suboptions:
            escaping:
                description:
                    - Character escaping configuration.
                type: dict
                required: false
                suboptions:
                    escape_character:
                        description:
                            - Escape sequence delimiter.
                            - Maximum length is 1 character.
                        type: str
                        required: false
                    escaped_characters:
                        description:
                            - List of all characters to be escaped (without spaces).
                            - Maximum length is 255 characters.
                        type: str
                        required: false
            traffic:
                description:
                    - Format string for traffic logs.
                type: str
                required: false
            threat:
                description:
                    - Format string for threat logs.
                type: str
                required: false
            wildfire:
                description:
                    - Format string for wildfire logs.
                type: str
                required: false
            url:
                description:
                    - Format string for URL logs.
                type: str
                required: false
            data:
                description:
                    - Format string for data logs.
                type: str
                required: false
            gtp:
                description:
                    - Format string for GTP logs.
                type: str
                required: false
            sctp:
                description:
                    - Format string for SCTP logs.
                type: str
                required: false
            tunnel:
                description:
                    - Format string for tunnel logs.
                type: str
                required: false
            auth:
                description:
                    - Format string for authentication logs.
                type: str
                required: false
            userid:
                description:
                    - Format string for user ID logs.
                type: str
                required: false
            iptag:
                description:
                    - Format string for IP tag logs.
                type: str
                required: false
            decryption:
                description:
                    - Format string for decryption logs.
                type: str
                required: false
            config:
                description:
                    - Format string for configuration logs.
                type: str
                required: false
            system:
                description:
                    - Format string for system logs.
                type: str
                required: false
            globalprotect:
                description:
                    - Format string for GlobalProtect logs.
                type: str
                required: false
            hip_match:
                description:
                    - Format string for HIP match logs.
                type: str
                required: false
            correlation:
                description:
                    - Format string for correlation logs.
                type: str
                required: false
    folder:
        description:
            - The folder in which the syslog server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the syslog server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the syslog server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the syslog server profile (UUID).
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
            - Desired state of the syslog server profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Syslog server profiles must be associated with exactly one container (folder, snippet, or device).
    - At least one server must be provided when state=present.
"""

EXAMPLES = r"""
- name: Create a folder-based syslog server profile
  cdot65.scm.syslog_server_profile:
    name: "syslog-profile-01"
    server:
      - name: "primary-syslog"
        server: "192.168.1.100"
        transport: "UDP"
        port: 514
        format: "BSD"
        facility: "LOG_LOCAL0"
      - name: "secondary-syslog"
        server: "192.168.1.101"
        transport: "TCP"
        port: 514
        format: "IETF"
        facility: "LOG_LOCAL1"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a syslog server profile with custom log formatting
  cdot65.scm.syslog_server_profile:
    name: "syslog-profile-custom"
    server:
      - name: "syslog-server"
        server: "10.0.0.50"
        transport: "TCP"
        port: 6514
        format: "IETF"
        facility: "LOG_USER"
    format:
      escaping:
        escape_character: "\\"
        escaped_characters: "[]"
      traffic: "$time_generated $src $dst"
      threat: "$time_generated $threatid $severity"
      system: "$time_generated $eventid"
    folder: "Security"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based syslog server profile
  cdot65.scm.syslog_server_profile:
    name: "syslog-snippet-profile"
    server:
      - name: "syslog-01"
        server: "syslog.example.com"
        transport: "UDP"
        port: 514
        format: "BSD"
        facility: "LOG_LOCAL7"
    snippet: "logging-config"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a syslog server profile
  cdot65.scm.syslog_server_profile:
    name: "syslog-profile-01"
    server:
      - name: "primary-syslog"
        server: "192.168.1.100"
        transport: "TCP"
        port: 514
        format: "IETF"
        facility: "LOG_LOCAL0"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a syslog server profile by name
  cdot65.scm.syslog_server_profile:
    name: "syslog-profile-01"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a syslog server profile by ID
  cdot65.scm.syslog_server_profile:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
syslog_server_profile:
    description: Information about the syslog server profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The syslog server profile ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The syslog server profile name
            type: str
            returned: always
            sample: "syslog-profile-01"
        server:
            description: List of syslog server configurations
            type: list
            returned: always
            sample:
                - name: "primary-syslog"
                  server: "192.168.1.100"
                  transport: "UDP"
                  port: 514
                  format: "BSD"
                  facility: "LOG_LOCAL0"
        format:
            description: Format settings for different log types
            type: dict
            returned: when applicable
            sample:
                escaping:
                    escape_character: "\\"
                    escaped_characters: "[]"
                traffic: "$time_generated $src $dst"
                threat: "$time_generated $threatid $severity"
        folder:
            description: The folder containing the syslog server profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the syslog server profile
            type: str
            returned: when applicable
            sample: "logging-config"
        device:
            description: The device containing the syslog server profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        server=dict(type="list", elements="dict", required=False),
        format=dict(type="dict", required=False),
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
            ["state", "present", ["name", "server"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for container type
    if params.get("state") == "present" and not any(params.get(container) for container in ["folder", "snippet", "device"]):
        module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    # Custom validation for server list
    if params.get("state") == "present":
        if not params.get("server") or len(params.get("server", [])) == 0:
            module.fail_json(msg="When state=present, at least one server must be provided")

        # Validate each server entry
        for idx, server in enumerate(params.get("server", [])):
            required_fields = ["name", "server", "transport", "port", "format", "facility"]
            for field in required_fields:
                if field not in server:
                    module.fail_json(msg=f"Server at index {idx} is missing required field: {field}")

            # Validate port range
            if not (1 <= server.get("port", 0) <= 65535):
                module.fail_json(
                    msg=f"Server at index {idx} has invalid port: {server.get('port')}. Port must be between 1 and 65535"
                )

            # Validate transport
            if server.get("transport") not in ["UDP", "TCP"]:
                module.fail_json(
                    msg=f"Server at index {idx} has invalid transport: {server.get('transport')}. Must be UDP or TCP"
                )

            # Validate format
            if server.get("format") not in ["BSD", "IETF"]:
                module.fail_json(msg=f"Server at index {idx} has invalid format: {server.get('format')}. Must be BSD or IETF")

            # Validate facility
            valid_facilities = [
                "LOG_USER",
                "LOG_LOCAL0",
                "LOG_LOCAL1",
                "LOG_LOCAL2",
                "LOG_LOCAL3",
                "LOG_LOCAL4",
                "LOG_LOCAL5",
                "LOG_LOCAL6",
                "LOG_LOCAL7",
            ]
            if server.get("facility") not in valid_facilities:
                module.fail_json(
                    msg=f"Server at index {idx} has invalid facility: {server.get('facility')}. Must be one of {valid_facilities}"
                )

    # Custom validation for name length
    if params.get("name") and len(params.get("name")) > 31:
        module.fail_json(msg="Name must be 31 characters or less")

    # Initialize results
    result = {"changed": False, "syslog_server_profile": None}

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
                    profile_obj = client.syslog_server_profile.fetch(
                        name=params.get("name"), **{container_type: container_name}
                    )
                    if profile_obj:
                        profile_exists = True
            except ObjectNotPresentError:
                profile_exists = False
                profile_obj = None

        # Create or update or delete a profile
        if params.get("state") == "present":
            if profile_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Check server list
                if params.get("server") is not None:
                    # Compare server lists (convert to dict for comparison)
                    existing_servers = [s.model_dump() if hasattr(s, "model_dump") else s for s in profile_obj.server]
                    new_servers = params.get("server")
                    if existing_servers != new_servers:
                        update_fields["server"] = new_servers

                # Check format
                if params.get("format") is not None:
                    existing_format = profile_obj.format.model_dump() if profile_obj.format else None
                    if existing_format != params.get("format"):
                        update_fields["format"] = params.get("format")

                # Check container fields
                for field in ["folder", "snippet", "device"]:
                    if params.get(field) is not None and getattr(profile_obj, field, None) != params.get(field):
                        update_fields[field] = params.get(field)

                # Update the profile if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = profile_obj.model_copy(update=update_fields)
                        updated = client.syslog_server_profile.update(update_model)
                        result["syslog_server_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["syslog_server_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["syslog_server_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new profile object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "server",
                        "format",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a profile object
                if not module.check_mode:
                    # Create a profile object
                    created = client.syslog_server_profile.create(create_payload)

                    # Return the created profile object
                    result["syslog_server_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created profile object (minimal info)
                    simulated = SyslogServerProfileCreateModel(**create_payload)
                    result["syslog_server_profile"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a profile object
        elif params.get("state") == "absent":
            if profile_exists:
                if not module.check_mode:
                    client.syslog_server_profile.delete(profile_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["syslog_server_profile"] = json.loads(profile_obj.model_dump_json(exclude_unset=True))
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
