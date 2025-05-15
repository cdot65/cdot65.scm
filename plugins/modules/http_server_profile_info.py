#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: http_server_profile_info
short_description: Retrieve information about HTTP server profiles in Strata Cloud Manager (SCM)
description:
    - Retrieve information about HTTP server profiles in Strata Cloud Manager using pan-scm-sdk.
    - Supports fetching a single profile by ID or name, or listing multiple profiles with optional filtering.
    - HTTP server profiles are associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the HTTP server profile to retrieve.
            - Used for exact match lookup.
            - Mutually exclusive with I(id).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the HTTP server profile (UUID).
            - Used for exact match lookup.
            - Mutually exclusive with I(name).
        type: str
        required: false
    protocol:
        description:
            - Filter HTTP server profiles by protocol.
            - Only applied when retrieving multiple profiles.
        type: str
        required: false
        choices: ["HTTPS", "HTTP"]
    tag_registration:
        description:
            - Filter HTTP server profiles by tag registration status.
            - Only applied when retrieving multiple profiles.
        type: bool
        required: false
    folder:
        description:
            - The folder in which to look for HTTP server profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to look for HTTP server profiles.
            - Exactly one of folder, snippet, or device must be provided.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to look for HTTP server profiles.
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
- name: Get all HTTP server profiles in a folder
  cdot65.scm.http_server_profile_info:
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: http_profiles

- name: Get HTTP server profile by ID
  cdot65.scm.http_server_profile_info:
    id: "12345678-abcd-1234-abcd-1234567890ab"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: http_profile

- name: Get HTTP server profile by name
  cdot65.scm.http_server_profile_info:
    name: "http-server-profile"
    folder: "Shared"
    scm_access_token: "{{ scm_access_token }}"
  register: http_profile

- name: Get all HTTP profiles (protocol filter)
  cdot65.scm.http_server_profile_info:
    folder: "Shared"
    protocol: HTTP
    scm_access_token: "{{ scm_access_token }}"
  register: http_profiles

- name: Get all HTTPS profiles (protocol filter)
  cdot65.scm.http_server_profile_info:
    folder: "Shared"
    protocol: HTTPS
    scm_access_token: "{{ scm_access_token }}"
  register: https_profiles

- name: Get all profiles with tag registration enabled
  cdot65.scm.http_server_profile_info:
    folder: "Shared"
    tag_registration: true
    scm_access_token: "{{ scm_access_token }}"
  register: tag_profiles

- name: Get all profiles in a snippet
  cdot65.scm.http_server_profile_info:
    snippet: "logging-config"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_profiles
"""

RETURN = r"""
http_server_profiles:
    description: List of HTTP server profiles when multiple profiles are retrieved
    returned: when no id or name is specified
    type: list
    elements: dict
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
                    description: URI format for the server (mapped from url_format in the API)
                    type: str
                    returned: always
                    sample: "/"
                certificate_profile:
                    description: Certificate profile for HTTPS connections
                    type: str
                    returned: when configured
                    sample: "GlobalProtect-Factory-Certificate-Profile"
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
http_server_profile:
    description: Information about a specific HTTP server profile
    returned: when id or name is specified and profile exists
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
                    description: URI format for the server (mapped from url_format in the API)
                    type: str
                    returned: always
                    sample: "/"
                certificate_profile:
                    description: Certificate profile for HTTPS connections
                    type: str
                    returned: when configured
                    sample: "GlobalProtect-Factory-Certificate-Profile"
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
        id=dict(type="str", required=False),
        protocol=dict(type="str", required=False, choices=["HTTPS", "HTTP"]),
        tag_registration=dict(type="bool", required=False),
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
                    profile = client.http_server_profile.get(profile_id)
                elif profile_name:
                    # Fetch by name within the specified container
                    profile = client.http_server_profile.fetch(name=profile_name, **{container_type: container_value})

                # Get the profile data and convert it to a dictionary
                profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))
                
                # Map url_format to uri_format for consistency with the Ansible module
                if "server" in profile_dict:
                    for server in profile_dict["server"]:
                        if "url_format" in server:
                            server["uri_format"] = server.pop("url_format")
                
                # Return the profile information
                result["http_server_profile"] = profile_dict
            except ObjectNotPresentError:
                if profile_id:
                    module.fail_json(msg=f"HTTP server profile with ID '{profile_id}' not found")
                else:
                    module.fail_json(msg=f"HTTP server profile with name '{profile_name}' not found in the specified container")
            except (APIError, InvalidObjectError) as e:
                module.fail_json(
                    msg="API error: " + str(e),
                    error_code=getattr(e, "error_code", None),
                    details=getattr(e, "details", None),
                )
        else:
            # Retrieve multiple profiles with optional filtering
            try:
                # Build filter parameters - only include container parameters for API call
                filter_params = {container_type: container_value}
                
                # Save the user's filter values for client-side filtering
                user_protocol = params.get("protocol")
                user_tag_registration = params.get("tag_registration")

                # Fetch all profiles in the container
                profiles = client.http_server_profile.list(**filter_params)

                # Convert to list of dictionaries and map url_format to uri_format
                profiles_list = []
                for profile in profiles:
                    profile_dict = json.loads(profile.model_dump_json(exclude_unset=True))
                    
                    # Map url_format to uri_format for consistency with the Ansible module
                    if "server" in profile_dict:
                        for server in profile_dict["server"]:
                            if "url_format" in server:
                                server["uri_format"] = server.pop("url_format")
                    
                    # Apply client-side filtering
                    should_include = True
                    
                    # Filter by protocol
                    if user_protocol and profile_dict.get("protocol") != user_protocol:
                        should_include = False
                    
                    # Filter by tag_registration
                    if user_tag_registration is not None:
                        if profile_dict.get("tag_registration") != user_tag_registration:
                            should_include = False
                    
                    # Add profile to results if it passes all filters
                    if should_include:
                        profiles_list.append(profile_dict)
                
                result["http_server_profiles"] = profiles_list
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