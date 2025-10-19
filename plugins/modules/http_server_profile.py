#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import HTTPServerProfileCreateModel

DOCUMENTATION = r"""
---
module: http_server_profile
short_description: Manage HTTP server profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete HTTP server profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports all HTTP server profile attributes and robust idempotency.
    - HTTP server profiles must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the HTTP server profile.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the HTTP server profile.
        type: str
        required: false
    protocol:
        description:
            - The protocol used for communication with the server.
            - Default is HTTPS.
        type: str
        required: false
        choices: ["HTTPS", "HTTP"]
        default: "HTTPS"
    server:
        description:
            - List of server configurations for the HTTP server profile.
            - Required for state=present.
        type: list
        elements: dict
        required: false
        suboptions:
            name:
                description:
                    - Name of the server.
                type: str
                required: true
            address:
                description:
                    - IP address or hostname of the server.
                type: str
                required: true
            port:
                description:
                    - Port used to communicate with the server.
                    - Default is 443.
                type: int
                required: false
                default: 443
            http_method:
                description:
                    - HTTP method to use for sending logs.
                    - Default is POST.
                type: str
                required: false
                choices: ["GET", "POST", "PUT"]
                default: "POST"
            uri_format:
                description:
                    - URI path for sending logs.
                    - Default is /.
                    - This maps to 'url_format' in the SCM API - we maintain uri_format for consistency with Ansible naming conventions.
                type: str
                required: false
                default: "/"
            certificate_profile:
                description:
                    - Certificate profile for HTTPS connections.
                    - Used only when protocol is HTTPS.
                    - Must reference an existing certificate profile in SCM, not a default string value.
                type: str
                required: false
            tls_version:
                description:
                    - TLS version to use for HTTPS connections.
                    - Used only when protocol is HTTPS.
                    - Default is 1.2.
                type: str
                required: false
                choices: ["1.0", "1.1", "1.2", "1.3"]
                default: "1.2"
    payload_format:
        description:
            - Format of the HTTP payload.
            - Default is STANDARD.
        type: str
        required: false
        choices: ["STANDARD", "IETF"]
        default: "STANDARD"
    tag_registration:
        description:
            - Whether to enable tag registration for the HTTP server profile.
            - Default is false.
        type: bool
        required: false
        default: false
    timeout:
        description:
            - Connection timeout in seconds.
            - Default is 60 seconds.
        type: int
        required: false
        default: 60
    folder:
        description:
            - The folder in which the HTTP server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the HTTP server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the HTTP server profile is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the HTTP server profile (UUID).
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
            - Desired state of the HTTP server profile.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - HTTP server profiles must be associated with exactly one container (folder, snippet, or device).
    - Server configurations are required when creating a new HTTP server profile.
"""

EXAMPLES = r"""
---
- name: Create a simple HTTP server profile
  cdot65.scm.http_server_profile:
    name: "http-server-profile"
    protocol: HTTP
    server:
      - name: "http-server-1"
        address: "192.168.1.1"
        port: 80
        http_method: "POST"
        uri_format: "/"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create an HTTPS server profile with TLS configuration
  cdot65.scm.http_server_profile:
    name: "https-server-profile"
    protocol: HTTPS
    server:
      - name: "https-server-1"
        address: "192.168.1.2"
        port: 443
        http_method: "POST"
        uri_format: "/logs"
        # Note: certificate_profile should reference an existing valid certificate profile
        tls_version: "1.2"
    timeout: 120
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create an HTTP server profile with multiple servers
  cdot65.scm.http_server_profile:
    name: "multi-server-profile"
    protocol: HTTP
    server:
      - name: "primary-server"
        address: "192.168.1.10"
        port: 8080
        http_method: "POST"
        uri_format: "/primary"
      - name: "backup-server"
        address: "192.168.1.11"
        port: 8080
        http_method: "POST"
        uri_format: "/backup"
    timeout: 30
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create an HTTP server profile with IETF payload format
  cdot65.scm.http_server_profile:
    name: "ietf-format-profile"
    protocol: HTTP
    server:
      - name: "syslog-server"
        address: "192.168.1.20"
        port: 514
        http_method: "POST"
        uri_format: "/syslog"
    payload_format: IETF
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update existing HTTP server profile
  cdot65.scm.http_server_profile:
    name: "http-server-profile"
    protocol: HTTPS
    server:
      - name: "updated-server"
        address: "192.168.1.30"
        port: 443
        http_method: "PUT"
        uri_format: "/updated"
    timeout: 90
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete HTTP server profile by name
  cdot65.scm.http_server_profile:
    name: "http-server-profile"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete HTTP server profile by ID
  cdot65.scm.http_server_profile:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
http_server_profile:
    description: Information about the HTTP server profile that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The HTTP server profile ID
            type: str
            returned: always
            sample: "12345678-abcd-1234-abcd-1234567890ab"
        name:
            description: The HTTP server profile name
            type: str
            returned: always
            sample: "http-server-profile"
        protocol:
            description: The protocol used for communication
            type: str
            returned: always
            sample: "HTTPS"
        server:
            description: List of server configurations
            type: list
            returned: always
            contains:
                name:
                    description: Server name
                    type: str
                    returned: always
                    sample: "http-server-1"
                address:
                    description: The server address
                    type: str
                    returned: always
                    sample: "192.168.1.1"
                port:
                    description: Server port
                    type: int
                    returned: always
                    sample: 443
                http_method:
                    description: HTTP method used
                    type: str
                    returned: always
                    sample: "POST"
                uri_format:
                    description: URI format for the server
                    type: str
                    returned: always
                    sample: "/"
                certificate_profile:
                    description: Certificate profile for HTTPS connections
                    type: str
                    returned: when configured
                    sample: "default"
                tls_version:
                    description: TLS version for HTTPS connections
                    type: str
                    returned: when configured
                    sample: "1.2"
        payload_format:
            description: The format of the HTTP payload
            type: str
            returned: always
            sample: "STANDARD"
        tag_registration:
            description: Whether tag registration is enabled
            type: bool
            returned: always
            sample: false
        timeout:
            description: Connection timeout in seconds
            type: int
            returned: always
            sample: 60
        folder:
            description: The folder containing the HTTP server profile
            type: str
            returned: when applicable
            sample: "Shared"
        snippet:
            description: The snippet containing the HTTP server profile
            type: str
            returned: when applicable
            sample: "log-forwarding"
        device:
            description: The device containing the HTTP server profile
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        protocol=dict(
            type="str",
            required=False,
            choices=["HTTPS", "HTTP"],
            default="HTTPS",
        ),
        server=dict(
            type="list",
            elements="dict",
            required=False,
            options=dict(
                name=dict(type="str", required=True),
                address=dict(type="str", required=True),
                protocol=dict(type="str", required=False, choices=["HTTP", "HTTPS"]),
                port=dict(type="int", required=False, default=443),
                http_method=dict(
                    type="str",
                    required=False,
                    choices=["GET", "POST", "PUT"],
                    default="POST",
                ),
                uri_format=dict(type="str", required=False, default="/"),
                certificate_profile=dict(type="str", required=False),
                tls_version=dict(
                    type="str",
                    required=False,
                    choices=["1.0", "1.1", "1.2", "1.3"],
                    default="1.2",
                ),
                username=dict(type="str", required=False),
                password=dict(type="str", required=False, no_log=True),
                payload_format=dict(type="str", required=False),
                headers=dict(type="list", elements="dict", required=False),
            ),
        ),
        payload_format=dict(
            type="str",
            required=False,
            choices=["STANDARD", "IETF"],
            default="STANDARD",
        ),
        tag_registration=dict(type="bool", required=False, default=False),
        timeout=dict(type="int", required=False, default=60),
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

    # Custom validation for server parameter
    params = module.params
    if params.get("state") == "present":
        # For creation/update, validate server parameter
        if not params.get("server"):
            module.fail_json(msg="When state=present, the server parameter is required")

        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False, "http_server_profile": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize http_server_profile_exists boolean
        http_server_profile_exists = False
        http_server_profile_obj = None

        # Fetch a http_server_profile by name or id
        if params.get("name") or params.get("id"):
            # Determine container type and name
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

            # Attempt to find the profile by listing and filtering
            if params.get("name") and container_type and container_name:
                try:
                    # Use list method which is more reliable than fetch
                    if container_type == "folder":
                        profiles = client.http_server_profile.list(folder=container_name)
                    elif container_type == "snippet":
                        profiles = client.http_server_profile.list(snippet=container_name)
                    elif container_type == "device":
                        profiles = client.http_server_profile.list(device=container_name)

                    # Find matching profile by name
                    for profile in profiles:
                        if profile.name == params.get("name"):
                            http_server_profile_obj = profile
                            http_server_profile_exists = True
                            break
                except Exception as e:
                    module.fail_json(
                        msg=f"Error listing HTTP server profiles: {str(e)}",
                        error_code=getattr(e, "error_code", None),
                        details=getattr(e, "details", None),
                    )

            # If specified by ID, try to get it directly
            elif params.get("id"):
                try:
                    http_server_profile_obj = client.http_server_profile.get(params.get("id"))
                    if http_server_profile_obj:
                        http_server_profile_exists = True
                except Exception as e:
                    # Skip if object not found, but fail on other errors
                    if "not found" not in str(e).lower() and "not present" not in str(e).lower():
                        module.fail_json(
                            msg=f"Error retrieving HTTP server profile by ID: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

        # Create or update or delete a http_server_profile
        if params.get("state") == "present":
            if http_server_profile_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Basic fields
                for field in [
                    "name",
                    "description",
                    "protocol",
                    "payload_format",
                    "tag_registration",
                    "timeout",
                    "folder",
                    "snippet",
                    "device",
                ]:
                    if params.get(field) is not None and getattr(http_server_profile_obj, field, None) != params.get(field):
                        update_fields[field] = params.get(field)

                # Server configurations
                if params.get("server"):
                    # Get new server configs from params, filter out None/empty values
                    new_servers = []
                    for server_config in params.get("server"):
                        # Filter out None values to match the API's expectations
                        server_dict = {k: v for k, v in server_config.items() if v is not None}

                        # Add protocol field if not present (using the main profile's protocol)
                        if "protocol" not in server_dict and params.get("protocol"):
                            server_dict["protocol"] = params.get("protocol")

                        new_servers.append(server_dict)

                    # Compare current and new server configurations
                    current_servers = []
                    if hasattr(http_server_profile_obj, "server"):
                        for server in http_server_profile_obj.server:
                            # Only include fields that can come from Ansible to ensure fair comparison
                            server_dict = server.model_dump(exclude_unset=True)
                            # Filter to include only keys that could come from Ansible params
                            filtered_dict = {
                                k: v
                                for k, v in server_dict.items()
                                if k
                                in [
                                    "name",
                                    "address",
                                    "protocol",
                                    "port",
                                    "http_method",
                                    "certificate_profile",
                                    "tls_version",
                                    "username",
                                    "payload_format",
                                    "headers",
                                ]
                            }

                            # Map SDK's url_format to Ansible's uri_format for comparison
                            if "url_format" in server_dict:
                                filtered_dict["uri_format"] = server_dict["url_format"]

                            current_servers.append(filtered_dict)

                    # Sort the configs by name to ensure consistent comparison
                    current_servers.sort(key=lambda x: x.get("name", ""))
                    new_servers.sort(key=lambda x: x.get("name", ""))

                    # If server configurations differ, update them
                    if current_servers != new_servers:
                        update_fields["server"] = new_servers

                # Update the http_server_profile if needed
                if update_fields:
                    if not module.check_mode:
                        try:
                            update_model = http_server_profile_obj.model_copy(update=update_fields)
                            updated = client.http_server_profile.update(update_model)
                            result["http_server_profile"] = json.loads(updated.model_dump_json(exclude_unset=True))
                        except InvalidObjectError as e:
                            module.fail_json(
                                msg=f"Invalid HTTP server profile object: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                        except APIError as e:
                            module.fail_json(
                                msg=f"API Error updating HTTP server profile: {str(e)}",
                                error_code=getattr(e, "error_code", None),
                                details=getattr(e, "details", None),
                            )
                    else:
                        # In check mode, just return the existing object with projected changes
                        result["http_server_profile"] = json.loads(http_server_profile_obj.model_dump_json(exclude_unset=True))

                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["http_server_profile"] = json.loads(http_server_profile_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new http_server_profile
                create_payload = {}

                # Add simple parameters directly
                for k in ["name", "description", "protocol", "payload_format", "tag_registration", "timeout"]:
                    if params.get(k) is not None:
                        create_payload[k] = params[k]

                # Add container parameter
                if params.get("folder"):
                    create_payload["folder"] = params["folder"]
                elif params.get("snippet"):
                    create_payload["snippet"] = params["snippet"]
                elif params.get("device"):
                    create_payload["device"] = params["device"]

                # Process server configuration
                if params.get("server"):
                    # Filter out None values to match the API's expectations
                    server_list = []
                    for server_config in params.get("server"):
                        server_dict = {k: v for k, v in server_config.items() if v is not None}

                        # Add protocol field if not present (using the main profile's protocol)
                        if "protocol" not in server_dict and params.get("protocol"):
                            server_dict["protocol"] = params.get("protocol")

                        # Include only fields expected by the API
                        filtered_server = {}
                        for field in [
                            "name",
                            "address",
                            "protocol",
                            "port",
                            "http_method",
                            "certificate_profile",
                            "tls_version",
                            "username",
                            "password",
                            "payload_format",
                            "headers",
                        ]:
                            if field in server_dict and server_dict[field] is not None:
                                filtered_server[field] = server_dict[field]

                        # Special handling for URI/URL format field (map Ansible's uri_format to SCM API's url_format)
                        if "uri_format" in server_dict and server_dict["uri_format"] is not None:
                            filtered_server["url_format"] = server_dict["uri_format"]

                        # Make sure protocol is present (required by API)
                        if "protocol" not in filtered_server:
                            filtered_server["protocol"] = params.get("protocol", "HTTP")

                        server_list.append(filtered_server)
                    create_payload["server"] = server_list

                # Debug the payload
                if not module.check_mode:
                    module.debug(f"Creating HTTP server profile with payload: {json.dumps(create_payload)}")

                # Create a http_server_profile object
                if not module.check_mode:
                    try:
                        # For debugging, print the payload using module's log mechanism
                        result["debug_payload"] = create_payload

                        created = client.http_server_profile.create(create_payload)
                        result["http_server_profile"] = json.loads(created.model_dump_json(exclude_unset=True))
                    except InvalidObjectError as e:
                        module.fail_json(
                            msg=f"Invalid HTTP server profile object: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                    except APIError as e:
                        module.fail_json(
                            msg=f"API Error creating HTTP server profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                            payload=create_payload,
                        )
                else:
                    # In check mode, simulate the creation
                    simulated = HTTPServerProfileCreateModel(**create_payload)
                    result["http_server_profile"] = simulated.model_dump(exclude_unset=True)

                result["changed"] = True
                module.exit_json(**result)

        # Handle absent state - delete the HTTP server profile
        elif params.get("state") == "absent":
            if http_server_profile_exists:
                if not module.check_mode:
                    try:
                        client.http_server_profile.delete(http_server_profile_obj.id)
                    except (APIError, InvalidObjectError) as e:
                        module.fail_json(
                            msg=f"API Error deleting HTTP server profile: {str(e)}",
                            error_code=getattr(e, "error_code", None),
                            details=getattr(e, "details", None),
                        )

                # Mark as changed
                result["changed"] = True
                result["http_server_profile"] = json.loads(http_server_profile_obj.model_dump_json(exclude_unset=True))
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
