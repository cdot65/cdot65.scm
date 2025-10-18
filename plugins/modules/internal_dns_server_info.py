#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Palo Alto Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = r"""
---
module: internal_dns_server_info
short_description: Retrieve internal DNS server information from Strata Cloud Manager
description:
  - Retrieves information about internal DNS server objects configured in Palo Alto Networks Strata Cloud Manager.
  - Can retrieve a specific server by name or ID, or list all servers.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
requirements:
  - pan-scm-sdk>=0.3.33
options:
  name:
    description:
      - The name of a specific internal DNS server to retrieve.
      - Mutually exclusive with C(object_id).
    required: false
    type: str
  object_id:
    description:
      - The UUID of a specific internal DNS server to retrieve.
      - Mutually exclusive with C(name).
    required: false
    type: str
  api_url:
    description:
      - The base URL for the Strata Cloud Manager API.
    required: false
    type: str
    default: "https://api.strata.paloaltonetworks.com"
  scm_access_token:
    description:
      - The OAuth2 access token for authenticating to the SCM API.
    required: true
    type: str
    no_log: true
"""

EXAMPLES = r"""
---
# Retrieve all internal DNS servers
- name: Get all internal DNS servers
  cdot65.scm.internal_dns_server_info:
    scm_access_token: "{{ scm_access_token }}"
  register: all_servers

- name: Display all servers
  ansible.builtin.debug:
    var: all_servers.servers

# Retrieve a specific internal DNS server by name
- name: Get specific internal DNS server by name
  cdot65.scm.internal_dns_server_info:
    name: "corporate-dns"
    scm_access_token: "{{ scm_access_token }}"
  register: specific_server

- name: Display specific server
  ansible.builtin.debug:
    var: specific_server.servers

# Retrieve a specific internal DNS server by ID
- name: Get specific internal DNS server by ID
  cdot65.scm.internal_dns_server_info:
    object_id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: server_by_id

- name: Display server by ID
  ansible.builtin.debug:
    var: server_by_id.servers
"""

RETURN = r"""
servers:
  description: List of internal DNS server objects
  returned: always
  type: list
  elements: dict
  sample:
    - id: "12345678-1234-1234-1234-123456789012"
      name: "corporate-dns"
      domain_name:
        - "example.com"
        - "internal.local"
      primary: "10.0.0.10"
      secondary: "10.0.0.11"
    - id: "87654321-4321-4321-4321-210987654321"
      name: "backup-dns"
      domain_name:
        - "backup.example.com"
      primary: "10.0.1.10"
      secondary: null
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    """Main execution path for the internal_dns_server_info module."""
    module_args = dict(
        name=dict(type="str", required=False),
        object_id=dict(type="str", required=False),
        api_url=dict(type="str", required=False, default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ["name", "object_id"],
        ],
    )

    if not HAS_SCM_SDK:
        module.fail_json(msg="The pan-scm-sdk library is required for this module. Install it using: pip install pan-scm-sdk")

    # Extract module parameters
    params = module.params
    server_name = params.get("name")
    object_id = params.get("object_id")

    # Initialize API client
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"
    scm_access_token = params["scm_access_token"]

    try:
        client = ScmClient(api_base_url=api_url, access_token=scm_access_token)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {str(e)}")

    result = {"servers": []}

    try:
        if object_id:
            # Retrieve specific server by ID
            try:
                server = client.internal_dns_server.get(object_id)
                result["servers"].append(
                    {
                        "id": str(server.id),
                        "name": server.name,
                        "domain_name": server.domain_name,
                        "primary": str(server.primary),
                        "secondary": str(server.secondary) if server.secondary else None,
                    }
                )
            except ObjectNotPresentError:
                module.warn(f"Internal DNS server with ID '{object_id}' not found")
        elif server_name:
            # Retrieve specific server by name
            try:
                server = client.internal_dns_server.fetch(name=server_name)
                result["servers"].append(
                    {
                        "id": str(server.id),
                        "name": server.name,
                        "domain_name": server.domain_name,
                        "primary": str(server.primary),
                        "secondary": str(server.secondary) if server.secondary else None,
                    }
                )
            except ObjectNotPresentError:
                module.warn(f"Internal DNS server '{server_name}' not found")
        else:
            # Retrieve all servers
            servers = client.internal_dns_server.list()
            for server in servers:
                result["servers"].append(
                    {
                        "id": str(server.id),
                        "name": server.name,
                        "domain_name": server.domain_name,
                        "primary": str(server.primary),
                        "secondary": str(server.secondary) if server.secondary else None,
                    }
                )

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
