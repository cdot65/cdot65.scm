#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Palo Alto Networks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License  at
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
module: internal_dns_server
short_description: Manage internal DNS server objects in Strata Cloud Manager
description:
  - Manages internal DNS server objects in Palo Alto Networks Strata Cloud Manager.
  - This module allows for the creation, modification, and deletion of internal DNS server configurations.
  - Internal DNS servers are used to specify domain-specific DNS resolution settings for the firewall.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
requirements:
  - pan-scm-sdk>=0.3.33
options:
  name:
    description:
      - The name of the internal DNS server resource.
      - Must match pattern ^[0-9a-zA-Z._\- ]+$ and be max 63 characters.
    required: true
    type: str
  domain_name:
    description:
      - List of DNS domain names to be resolved by this server.
      - At least one domain name is required.
    required: false
    type: list
    elements: str
  primary:
    description:
      - The IP address of the primary DNS server.
      - Can be IPv4 or IPv6 address.
    required: false
    type: str
  secondary:
    description:
      - The IP address of the secondary DNS server (optional).
      - Can be IPv4 or IPv6 address.
    required: false
    type: str
  object_id:
    description:
      - UUID of the internal DNS server object (required for updates and deletes).
      - Used to identify an existing object.
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
  state:
    description:
      - The desired state of the internal DNS server object.
      - Use C(present) to create or update an object.
      - Use C(absent) to delete an object.
    required: false
    type: str
    choices:
      - present
      - absent
    default: present
"""

EXAMPLES = r"""
---
# Create a basic internal DNS server
- name: Create internal DNS server
  cdot65.scm.internal_dns_server:
    name: "corporate-dns"
    domain_name:
      - "example.com"
      - "internal.local"
    primary: "10.0.0.10"
    secondary: "10.0.0.11"
    scm_access_token: "{{ scm_access_token }}"
    state: present

# Create internal DNS server with IPv6
- name: Create internal DNS server with IPv6
  cdot65.scm.internal_dns_server:
    name: "ipv6-dns"
    domain_name:
      - "ipv6.example.com"
    primary: "2001:db8::1"
    secondary: "2001:db8::2"
    scm_access_token: "{{ scm_access_token }}"
    state: present

# Update an existing internal DNS server
- name: Update internal DNS server
  cdot65.scm.internal_dns_server:
    name: "corporate-dns"
    object_id: "12345678-1234-1234-1234-123456789012"
    domain_name:
      - "example.com"
      - "internal.local"
      - "vpn.example.com"
    primary: "10.0.0.10"
    scm_access_token: "{{ scm_access_token }}"
    state: present

# Delete an internal DNS server
- name: Delete internal DNS server
  cdot65.scm.internal_dns_server:
    name: "corporate-dns"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the object was changed
  returned: always
  type: bool
  sample: true
server:
  description: The internal DNS server object details
  returned: when state is present
  type: dict
  sample:
    id: "12345678-1234-1234-1234-123456789012"
    name: "corporate-dns"
    domain_name:
      - "example.com"
      - "internal.local"
    primary: "10.0.0.10"
    secondary: "10.0.0.11"
msg:
  description: Operation status message
  returned: always
  type: str
  sample: "Internal DNS server 'corporate-dns' created successfully"
"""

import contextlib

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError
    from scm.models.deployment import InternalDnsServersUpdateModel

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    """Main execution path for the internal_dns_server module."""
    module_args = dict(
        name=dict(type="str", required=True),
        domain_name=dict(type="list", elements="str", required=False),
        primary=dict(type="str", required=False),
        secondary=dict(type="str", required=False),
        object_id=dict(type="str", required=False),
        api_url=dict(type="str", required=False, default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_SCM_SDK:
        module.fail_json(msg="The pan-scm-sdk library is required for this module. Install it using: pip install pan-scm-sdk")

    # Extract module parameters
    params = module.params
    server_name = params["name"]
    state = params["state"]
    object_id = params.get("object_id")

    # Initialize API client
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"
    scm_access_token = params["scm_access_token"]

    try:
        client = ScmClient(api_base_url=api_url, access_token=scm_access_token)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {str(e)}")

    result = {"changed": False, "msg": ""}

    try:
        # =====================================================================
        # STATE: absent - Delete the internal DNS server
        # =====================================================================
        if state == "absent":
            try:
                if object_id:
                    # Delete by ID if provided
                    client.internal_dns_server.delete(object_id)
                    result["changed"] = True
                    result["msg"] = f"Internal DNS server with ID '{object_id}' deleted successfully"
                else:
                    # Try to find and delete by name
                    try:
                        existing_server = client.internal_dns_server.fetch(name=server_name)
                        if existing_server:
                            client.internal_dns_server.delete(str(existing_server.id))
                            result["changed"] = True
                            result["msg"] = f"Internal DNS server '{server_name}' deleted successfully"
                    except ObjectNotPresentError:
                        result["msg"] = f"Internal DNS server '{server_name}' not found (already absent)"
            except ObjectNotPresentError:
                result["msg"] = f"Internal DNS server '{server_name}' not found (already absent)"
            except Exception as e:
                module.fail_json(msg=f"Failed to delete internal DNS server: {str(e)}")

            module.exit_json(**result)

        # =====================================================================
        # STATE: present - Create or update the internal DNS server
        # =====================================================================
        # Check if the server already exists
        existing_server = None
        if object_id:
            with contextlib.suppress(ObjectNotPresentError):
                existing_server = client.internal_dns_server.get(object_id)
        else:
            with contextlib.suppress(ObjectNotPresentError):
                existing_server = client.internal_dns_server.fetch(name=server_name)

        # Build the server data dictionary
        server_data = {"name": server_name}

        if params.get("domain_name"):
            server_data["domain_name"] = params["domain_name"]
        if params.get("primary"):
            server_data["primary"] = params["primary"]
        if params.get("secondary"):
            server_data["secondary"] = params["secondary"]

        if existing_server:
            # Server exists - update if necessary
            needs_update = False

            # Compare each field
            if params.get("domain_name") and set(params["domain_name"]) != set(existing_server.domain_name):
                needs_update = True
            if params.get("primary") and str(params["primary"]) != str(existing_server.primary):
                needs_update = True
            if params.get("secondary"):
                if str(params["secondary"]) != str(existing_server.secondary or ""):
                    needs_update = True

            if needs_update:
                server_data["id"] = str(existing_server.id)
                update_model = InternalDnsServersUpdateModel(**server_data)
                updated_server = client.internal_dns_server.update(update_model)
                result["changed"] = True
                result["msg"] = f"Internal DNS server '{server_name}' updated successfully"
                result["server"] = {
                    "id": str(updated_server.id),
                    "name": updated_server.name,
                    "domain_name": updated_server.domain_name,
                    "primary": str(updated_server.primary),
                    "secondary": str(updated_server.secondary) if updated_server.secondary else None,
                }
            else:
                result["msg"] = f"Internal DNS server '{server_name}' already exists with correct configuration"
                result["server"] = {
                    "id": str(existing_server.id),
                    "name": existing_server.name,
                    "domain_name": existing_server.domain_name,
                    "primary": str(existing_server.primary),
                    "secondary": str(existing_server.secondary) if existing_server.secondary else None,
                }
        else:
            # Server doesn't exist - create it
            if not all([params.get("domain_name"), params.get("primary")]):
                module.fail_json(msg="domain_name and primary are required when creating a new internal DNS server")

            created_server = client.internal_dns_server.create(server_data)
            result["changed"] = True
            result["msg"] = f"Internal DNS server '{server_name}' created successfully"
            result["server"] = {
                "id": str(created_server.id),
                "name": created_server.name,
                "domain_name": created_server.domain_name,
                "primary": str(created_server.primary),
                "secondary": str(created_server.secondary) if created_server.secondary else None,
            }

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
