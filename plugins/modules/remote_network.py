#!/usr/bin/python

# Copyright 2025 Palo Alto Networks
# Licensed under the Apache License, Version 2.0

DOCUMENTATION = r"""
---
module: remote_network
short_description: Manage remote network configurations in Strata Cloud Manager
description:
  - Manage Prisma Access remote network configurations for branch office connectivity.
  - Configure IPSec tunnels, BGP routing, and ECMP load balancing.
  - Remote networks connect branch offices to Prisma Access via IPSec tunnels.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
options:
  id:
    description: UUID of the remote network (for updates/deletes)
    required: false
    type: str
  name:
    description: Name of the remote network
    required: true
    type: str
  region:
    description: Region for the remote network
    required: true
    type: str
  license_type:
    description: License type (new customers use aggregate licensing)
    required: false
    type: str
    default: "FWAAS-AGGREGATE"
  spn_name:
    description: SPN name (required when license_type is FWAAS-AGGREGATE)
    required: false
    type: str
  description:
    description: Description of the remote network
    required: false
    type: str
  subnets:
    description: List of subnets behind the remote network
    required: false
    type: list
    elements: str
  ecmp_load_balancing:
    description: Enable or disable ECMP load balancing
    required: false
    type: str
    choices: ['enable', 'disable']
    default: 'disable'
  ecmp_tunnels:
    description: ECMP tunnel configurations (required when ecmp_load_balancing is enable)
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description: Tunnel name
        required: true
        type: str
      ipsec_tunnel:
        description: IPSec tunnel name
        required: true
        type: str
      local_ip_address:
        description: Local IP address for BGP
        required: false
        type: str
      peer_as:
        description: Peer AS number
        required: false
        type: str
      peer_ip_address:
        description: Peer IP address for BGP
        required: false
        type: str
      peering_type:
        description: BGP peering type
        required: false
        type: str
        choices:
          - exchange-v4-over-v4
          - exchange-v4-v6-over-v4
          - exchange-v4-over-v4-v6-over-v6
          - exchange-v6-over-v6
      secret:
        description: BGP secret
        required: false
        type: str
        no_log: true
      summarize_mobile_user_routes:
        description: Summarize mobile user routes
        required: false
        type: bool
      do_not_export_routes:
        description: Do not export routes
        required: false
        type: bool
      originate_default_route:
        description: Originate default route
        required: false
        type: bool
  ipsec_tunnel:
    description: IPSec tunnel name (required when ecmp_load_balancing is disable)
    required: false
    type: str
  secondary_ipsec_tunnel:
    description: Secondary IPSec tunnel name
    required: false
    type: str
  protocol:
    description: Protocol configuration (BGP)
    required: false
    type: dict
    suboptions:
      bgp:
        description: BGP configuration
        required: false
        type: dict
        suboptions:
          enable:
            description: Enable BGP
            required: false
            type: bool
          local_ip_address:
            description: Local IP address
            required: false
            type: str
          peer_as:
            description: Peer AS number
            required: false
            type: str
          peer_ip_address:
            description: Peer IP address
            required: false
            type: str
          peering_type:
            description: BGP peering type
            required: false
            type: str
          secret:
            description: BGP secret
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
      bgp_peer:
        description: BGP peer configuration
        required: false
        type: dict
        suboptions:
          local_ip_address:
            description: Local IP address
            required: false
            type: str
          peer_ip_address:
            description: Peer IP address
            required: false
            type: str
          secret:
            description: BGP secret
            required: false
            type: str
            no_log: true
  folder:
    description: Folder where the remote network is defined
    required: false
    type: str
  snippet:
    description: Snippet where the remote network is defined
    required: false
    type: str
  device:
    description: Device where the remote network is defined
    required: false
    type: str
  state:
    description: Desired state of the remote network
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
notes:
  - Exactly one of folder, snippet, or device must be specified.
  - When ecmp_load_balancing is enable, ecmp_tunnels is required.
  - When ecmp_load_balancing is disable, ipsec_tunnel is required.
  - When license_type is FWAAS-AGGREGATE, spn_name is required.
"""

EXAMPLES = r"""
- name: Create basic remote network with single tunnel
  cdot65.scm.remote_network:
    name: "branch-office-1"
    region: "us-east-1"
    license_type: "FWAAS-AGGREGATE"
    spn_name: "my-spn"
    subnets:
      - "10.1.0.0/24"
      - "10.1.1.0/24"
    ipsec_tunnel: "tunnel-1"
    folder: "Remote Networks"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create remote network with ECMP tunnels
  cdot65.scm.remote_network:
    name: "branch-office-2"
    region: "us-west-1"
    license_type: "FWAAS-AGGREGATE"
    spn_name: "my-spn"
    subnets:
      - "10.2.0.0/24"
    ecmp_load_balancing: "enable"
    ecmp_tunnels:
      - name: "tunnel-1"
        ipsec_tunnel: "ipsec-tunnel-1"
        local_ip_address: "10.2.1.1"
        peer_ip_address: "10.2.1.2"
        peer_as: "65001"
      - name: "tunnel-2"
        ipsec_tunnel: "ipsec-tunnel-2"
        local_ip_address: "10.2.2.1"
        peer_ip_address: "10.2.2.2"
        peer_as: "65001"
    folder: "Remote Networks"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create remote network with BGP
  cdot65.scm.remote_network:
    name: "branch-office-3"
    region: "us-central-1"
    license_type: "FWAAS-AGGREGATE"
    spn_name: "my-spn"
    subnets:
      - "10.3.0.0/24"
    ipsec_tunnel: "tunnel-3"
    protocol:
      bgp:
        enable: true
        local_ip_address: "169.254.1.1"
        peer_ip_address: "169.254.1.2"
        peer_as: "65002"
        peering_type: "exchange-v4-over-v4"
    folder: "Remote Networks"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete remote network
  cdot65.scm.remote_network:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
remote_network:
  description: The remote network object
  returned: always
  type: dict
  sample:
    id: "123e4567-e89b-12d3-a456-426655440000"
    name: "branch-office-1"
    region: "us-east-1"
    license_type: "FWAAS-AGGREGATE"
    spn_name: "my-spn"
    subnets:
      - "10.1.0.0/24"
    ipsec_tunnel: "tunnel-1"
    folder: "Remote Networks"
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
        license_type=dict(type="str", default="FWAAS-AGGREGATE"),
        spn_name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        subnets=dict(type="list", elements="str", required=False),
        ecmp_load_balancing=dict(type="str", choices=["enable", "disable"], default="disable"),
        ecmp_tunnels=dict(type="list", elements="dict", required=False),
        ipsec_tunnel=dict(type="str", required=False),
        secondary_ipsec_tunnel=dict(type="str", required=False),
        protocol=dict(type="dict", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        api_url=dict(type="str", default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["folder", "snippet", "device"]],
        required_one_of=[["folder", "snippet", "device"]] if module_args.get("state") == "present" else None,
    )

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
                result["msg"] = f"Remote network with ID '{params['id']}' would be deleted"
            else:
                try:
                    client.remote_network.delete(params["id"])
                    result["changed"] = True
                    result["msg"] = f"Remote network with ID '{params['id']}' deleted"
                except ObjectNotPresentError:
                    result["msg"] = f"Remote network with ID '{params['id']}' not found"

            module.exit_json(**result)

        # Create or update
        if not params.get("name") or not params.get("region"):
            module.fail_json(msg="name and region are required for state=present")

        # Build data dict
        data = {
            "name": params["name"],
            "region": params["region"],
            "license_type": params["license_type"],
        }

        # Add container
        for container in ["folder", "snippet", "device"]:
            if params.get(container):
                data[container] = params[container]
                break

        # Optional fields
        if params.get("description"):
            data["description"] = params["description"]
        if params.get("subnets"):
            data["subnets"] = params["subnets"]
        if params.get("spn_name"):
            data["spn_name"] = params["spn_name"]
        if params.get("ecmp_load_balancing"):
            data["ecmp_load_balancing"] = params["ecmp_load_balancing"]
        if params.get("ecmp_tunnels"):
            data["ecmp_tunnels"] = params["ecmp_tunnels"]
        if params.get("ipsec_tunnel"):
            data["ipsec_tunnel"] = params["ipsec_tunnel"]
        if params.get("secondary_ipsec_tunnel"):
            data["secondary_ipsec_tunnel"] = params["secondary_ipsec_tunnel"]
        if params.get("protocol"):
            data["protocol"] = params["protocol"]

        # Check if exists by name
        existing = None
        if params.get("id"):
            try:
                existing = client.remote_network.get(params["id"])
            except ObjectNotPresentError:  # noqa: SIM105
                # Network not found, will create
                pass
        else:
            # Try to find by name
            container_type = next((c for c in ["folder", "snippet", "device"] if params.get(c)), None)
            if container_type:
                try:
                    all_networks = client.remote_network.list(**{container_type: params[container_type]})
                    for net in all_networks:
                        if net.name == params["name"]:
                            existing = net
                            break
                except Exception as e:
                    module.warn(f"Unable to check existing networks: {str(e)}")

        if existing:
            # Update
            data["id"] = str(existing.id)
            if module.check_mode:
                result["changed"] = True
                result["msg"] = f"Remote network '{params['name']}' would be updated"
            else:
                updated = client.remote_network.update(data)
                result["changed"] = True
                result["msg"] = f"Remote network '{params['name']}' updated"
                result_dict = updated.model_dump(exclude_unset=True)
                result_dict["id"] = str(result_dict["id"])
                result["remote_network"] = result_dict
        else:
            # Create
            if module.check_mode:
                result["changed"] = True
                result["msg"] = f"Remote network '{params['name']}' would be created"
            else:
                created = client.remote_network.create(data)
                result["changed"] = True
                result["msg"] = f"Remote network '{params['name']}' created"
                result_dict = created.model_dump(exclude_unset=True)
                result_dict["id"] = str(result_dict["id"])
                result["remote_network"] = result_dict

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
