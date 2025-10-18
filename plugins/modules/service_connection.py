#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

from contextlib import suppress

DOCUMENTATION = r"""
---
module: service_connection
short_description: Manage service connections in Strata Cloud Manager
description:
  - Manage Prisma Access service connections for connecting to cloud services.
  - Configure IPSec tunnels, BGP routing, and QoS for service connectivity.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  id:
    description: UUID of the service connection (for updates/deletes)
    required: false
    type: str
  name:
    description: Name of the service connection
    required: true
    type: str
  region:
    description: Region for the service connection
    required: true
    type: str
  ipsec_tunnel:
    description: IPSec tunnel for the service connection
    required: true
    type: str
  folder:
    description: Folder containing the service connection
    required: false
    type: str
    default: "Service Connections"
  onboarding_type:
    description: Onboarding type for the service connection
    required: false
    type: str
    choices: ['classic']
    default: 'classic'
  backup_SC:
    description: Backup service connection name
    required: false
    type: str
  secondary_ipsec_tunnel:
    description: Secondary IPSec tunnel for redundancy
    required: false
    type: str
  subnets:
    description: List of subnets for the service connection
    required: false
    type: list
    elements: str
  source_nat:
    description: Enable source NAT
    required: false
    type: bool
  nat_pool:
    description: NAT pool name
    required: false
    type: str
  no_export_community:
    description: No export community configuration
    required: false
    type: str
    choices: ['Disabled', 'Enabled-In', 'Enabled-Out', 'Enabled-Both']
  bgp_peer:
    description: BGP peer configuration
    required: false
    type: dict
    suboptions:
      local_ip_address:
        description: Local IPv4 address for BGP peering
        required: false
        type: str
      local_ipv6_address:
        description: Local IPv6 address for BGP peering
        required: false
        type: str
      peer_ip_address:
        description: Peer IPv4 address for BGP peering
        required: false
        type: str
      peer_ipv6_address:
        description: Peer IPv6 address for BGP peering
        required: false
        type: str
      secret:
        description: BGP authentication secret
        required: false
        type: str
        no_log: true
  protocol:
    description: Protocol configuration
    required: false
    type: dict
    suboptions:
      bgp:
        description: BGP protocol configuration
        required: false
        type: dict
        suboptions:
          enable:
            description: Enable BGP
            required: false
            type: bool
          local_ip_address:
            description: Local IP address for BGP
            required: false
            type: str
          peer_ip_address:
            description: Peer IP address for BGP
            required: false
            type: str
          peer_as:
            description: Peer AS number
            required: false
            type: str
          secret:
            description: BGP authentication secret
            required: false
            type: str
            no_log: true
          do_not_export_routes:
            description: Do not export routes
            required: false
            type: bool
          originate_default_route:
            description: Originate default route
            required: false
            type: bool
          summarize_mobile_user_routes:
            description: Summarize mobile user routes
            required: false
            type: bool
          fast_failover:
            description: Enable fast failover
            required: false
            type: bool
  qos:
    description: QoS configuration
    required: false
    type: dict
    suboptions:
      enable:
        description: Enable QoS
        required: false
        type: bool
      qos_profile:
        description: QoS profile name
        required: false
        type: str
  state:
    description: Desired state of the service connection
    required: false
    type: str
    choices: ['present', 'absent']
    default: 'present'
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
- name: Create basic service connection
  cdot65.scm.service_connection:
    name: "aws-east-connection"
    region: "us-east-1"
    ipsec_tunnel: "aws-tunnel-1"
    subnets:
      - "10.50.0.0/24"
    folder: "Service Connections"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create service connection with BGP
  cdot65.scm.service_connection:
    name: "azure-west-connection"
    region: "us-west-1"
    ipsec_tunnel: "azure-tunnel-1"
    subnets:
      - "10.51.0.0/24"
    protocol:
      bgp:
        enable: true
        local_ip_address: "169.254.21.1"
        peer_ip_address: "169.254.21.2"
        peer_as: "65100"
    folder: "Service Connections"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create service connection with redundancy
  cdot65.scm.service_connection:
    name: "gcp-central-connection"
    region: "us-central-1"
    ipsec_tunnel: "gcp-tunnel-1"
    secondary_ipsec_tunnel: "gcp-tunnel-2"
    subnets:
      - "10.52.0.0/24"
    source_nat: true
    folder: "Service Connections"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete service connection
  cdot65.scm.service_connection:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
service_connection:
  description: The service connection object
  returned: always
  type: dict
  sample:
    id: "123e4567-e89b-12d3-a456-426655440000"
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
        region=dict(type="str", required=False),
        ipsec_tunnel=dict(type="str", required=False),
        folder=dict(type="str", default="Service Connections"),
        onboarding_type=dict(type="str", choices=["classic"], default="classic"),
        backup_SC=dict(type="str", required=False),
        secondary_ipsec_tunnel=dict(type="str", required=False),
        subnets=dict(type="list", elements="str", required=False),
        source_nat=dict(type="bool", required=False),
        nat_pool=dict(type="str", required=False),
        no_export_community=dict(
            type="str",
            choices=["Disabled", "Enabled-In", "Enabled-Out", "Enabled-Both"],
            required=False,
        ),
        bgp_peer=dict(type="dict", required=False),
        protocol=dict(type="dict", required=False),
        qos=dict(type="dict", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk required")

    params = module.params
    state = params["state"]

    try:
        client = ScmClient(
            api_base_url=params.get("api_url") or "https://api.strata.paloaltonetworks.com",
            access_token=params["scm_access_token"],
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize client: {str(e)}")

    result = {"changed": False}

    try:
        if state == "absent":
            if not params.get("id"):
                module.fail_json(msg="id is required for state=absent")

            if module.check_mode:
                result["changed"] = True
                result["msg"] = f"Service connection with ID '{params['id']}' would be deleted"
            else:
                try:
                    client.service_connection.delete(params["id"])
                    result["changed"] = True
                    result["msg"] = f"Service connection with ID '{params['id']}' deleted"
                except ObjectNotPresentError:
                    result["msg"] = f"Service connection with ID '{params['id']}' not found"

            module.exit_json(**result)

        # Create or update
        if not params.get("name") or not params.get("region") or not params.get("ipsec_tunnel"):
            module.fail_json(msg="name, region, and ipsec_tunnel are required for state=present")

        # Build data dict
        data = {
            "name": params["name"],
            "region": params["region"],
            "ipsec_tunnel": params["ipsec_tunnel"],
            "folder": params["folder"],
            "onboarding_type": params["onboarding_type"],
        }

        # Optional fields
        if params.get("backup_SC"):
            data["backup_SC"] = params["backup_SC"]
        if params.get("secondary_ipsec_tunnel"):
            data["secondary_ipsec_tunnel"] = params["secondary_ipsec_tunnel"]
        if params.get("subnets"):
            data["subnets"] = params["subnets"]
        if params.get("source_nat") is not None:
            data["source_nat"] = params["source_nat"]
        if params.get("nat_pool"):
            data["nat_pool"] = params["nat_pool"]
        if params.get("no_export_community"):
            data["no_export_community"] = params["no_export_community"]
        if params.get("bgp_peer"):
            data["bgp_peer"] = params["bgp_peer"]
        if params.get("protocol"):
            data["protocol"] = params["protocol"]
        if params.get("qos"):
            data["qos"] = params["qos"]

        # Check if exists
        existing = None
        if params.get("id"):
            with suppress(ObjectNotPresentError):
                existing = client.service_connection.get(params["id"])
        else:
            # Try to find by name in folder
            try:
                all_connections = client.service_connection.list(folder=params["folder"])
                for conn in all_connections:
                    if conn.name == params["name"]:
                        existing = conn
                        break
            except Exception as e:
                module.warn(f"Unable to check existing connections: {str(e)}")

        if existing:
            # Update
            data["id"] = str(existing.id)
            if module.check_mode:
                result["changed"] = True
                result["msg"] = f"Service connection '{params['name']}' would be updated"
            else:
                updated = client.service_connection.update(data)
                result["changed"] = True
                result["msg"] = f"Service connection '{params['name']}' updated"
                result_dict = updated.model_dump(exclude_unset=True)
                result_dict["id"] = str(result_dict["id"])
                result["service_connection"] = result_dict
        else:
            # Create
            if module.check_mode:
                result["changed"] = True
                result["msg"] = f"Service connection '{params['name']}' would be created"
            else:
                created = client.service_connection.create(data)
                result["changed"] = True
                result["msg"] = f"Service connection '{params['name']}' created"
                result_dict = created.model_dump(exclude_unset=True)
                result_dict["id"] = str(result_dict["id"])
                result["service_connection"] = result_dict

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
