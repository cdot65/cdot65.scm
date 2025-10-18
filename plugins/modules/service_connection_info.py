#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: service_connection_info
short_description: Retrieve service connection information from Strata Cloud Manager
description:
  - Retrieves Prisma Access service connection configurations.
  - List all service connections or get a specific one by ID or name.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  id:
    description: UUID of the service connection to retrieve
    required: false
    type: str
  name:
    description: Name of the service connection to retrieve
    required: false
    type: str
  folder:
    description: Filter by folder
    required: false
    type: str
    default: "Service Connections"
  api_url:
    description: SCM API base URL
    required: false
    type: str
    default: "https://api.strata.paloaltonetworks.com"
  scm_access_token:
    description: OAuth2 access token
    required: true
    type: str
    no_log: true
"""

EXAMPLES = r"""
- name: List all service connections
  cdot65.scm.service_connection_info:
    folder: "Service Connections"
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific service connection by ID
  cdot65.scm.service_connection_info:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"

- name: Get specific service connection by name
  cdot65.scm.service_connection_info:
    name: "aws-east-connection"
    folder: "Service Connections"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
service_connections:
  description: List of service connections
  returned: always
  type: list
  elements: dict
  sample:
    - id: "123e4567-e89b-12d3-a456-426655440000"
      name: "aws-east-connection"
      region: "us-east-1"
      ipsec_tunnel: "aws-tunnel-1"
      subnets:
        - "10.50.0.0/24"
      folder: "Service Connections"
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    module_args = dict(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        folder=dict(type="str", default="Service Connections"),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk required")

    params = module.params

    try:
        client = ScmClient(
            api_base_url=params.get("api_url") or "https://api.strata.paloaltonetworks.com",
            access_token=params["scm_access_token"],
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize client: {str(e)}")

    result = {"changed": False, "service_connections": []}

    try:
        if params.get("id"):
            # Get by ID
            try:
                connection = client.service_connection.get(params["id"])
                conn_dict = connection.model_dump(exclude_unset=True)
                conn_dict["id"] = str(conn_dict["id"])
                result["service_connections"].append(conn_dict)
            except ObjectNotPresentError:
                pass
        else:
            # List connections in folder
            connections = client.service_connection.list(folder=params["folder"])
            for conn in connections:
                # Filter by name if specified
                if params.get("name") and conn.name != params["name"]:
                    continue

                conn_dict = conn.model_dump(exclude_unset=True)
                conn_dict["id"] = str(conn_dict["id"])
                result["service_connections"].append(conn_dict)

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
