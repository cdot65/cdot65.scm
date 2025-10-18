#!/usr/bin/python

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
module: security_zone
short_description: Manage security zones in Strata Cloud Manager
description:
  - Manages security zone objects in Palo Alto Networks Strata Cloud Manager.
  - Security zones are logical groupings of network interfaces that share security requirements.
author:
  - Calvin Remsburg (@cdot65)
version_added: "0.1.0"
requirements:
  - pan-scm-sdk>=0.3.44
options:
  name:
    description:
      - The name of the security zone.
    required: true
    type: str
  network:
    description:
      - Network configuration for the zone.
    required: false
    type: dict
    suboptions:
      layer3:
        description: List of Layer 3 interfaces
        type: list
        elements: str
      layer2:
        description: List of Layer 2 interfaces
        type: list
        elements: str
      tap:
        description: List of TAP interfaces
        type: list
        elements: str
      virtual_wire:
        description: List of virtual wire interfaces
        type: list
        elements: str
      zone_protection_profile:
        description: Zone protection profile name
        type: str
      log_setting:
        description: Log setting name
        type: str
  enable_user_identification:
    description:
      - Enable user identification in this zone.
    required: false
    type: bool
  enable_device_identification:
    description:
      - Enable device identification in this zone.
    required: false
    type: bool
  folder:
    description:
      - The folder in which the resource is defined.
    required: false
    type: str
  snippet:
    description:
      - The snippet in which the resource is defined.
    required: false
    type: str
  device:
    description:
      - The device in which the resource is defined.
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
      - The desired state of the security zone.
    required: false
    type: str
    choices:
      - present
      - absent
    default: present
"""

EXAMPLES = r"""
---
# Create a basic Layer 3 security zone
- name: Create trust zone
  cdot65.scm.security_zone:
    name: "trust"
    network:
      layer3:
        - "ethernet1/1"
        - "ethernet1/2"
    enable_user_identification: true
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present

# Delete a security zone
- name: Delete trust zone
  cdot65.scm.security_zone:
    name: "trust"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
changed:
  description: Whether the object was changed
  returned: always
  type: bool
zone:
  description: The security zone object details
  returned: when state is present
  type: dict
msg:
  description: Operation status message
  returned: always
  type: str
"""

import contextlib

from ansible.module_utils.basic import AnsibleModule

try:
    from scm.client import Scm as ScmClient
    from scm.exceptions import APIError, ObjectNotPresentError
    from scm.models.network import SecurityZoneUpdateModel

    HAS_SCM_SDK = True
except ImportError:
    HAS_SCM_SDK = False


def main():
    """Main execution path for the security_zone module."""
    module_args = dict(
        name=dict(type="str", required=True),
        network=dict(type="dict", required=False),
        enable_user_identification=dict(type="bool", required=False),
        enable_device_identification=dict(type="bool", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        api_url=dict(type="str", required=False, default="https://api.strata.paloaltonetworks.com"),
        scm_access_token=dict(type="str", required=True, no_log=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_one_of=[["folder", "snippet", "device"]],
        mutually_exclusive=[["folder", "snippet", "device"]],
    )

    if not HAS_SCM_SDK:
        module.fail_json(msg="pan-scm-sdk is required for this module. Install: pip install pan-scm-sdk")

    params = module.params
    zone_name = params["name"]
    state = params["state"]

    # Determine container type
    container_type = None
    container_name = None
    for c in ["folder", "snippet", "device"]:
        if params.get(c):
            container_type = c
            container_name = params[c]
            break

    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"
    scm_access_token = params["scm_access_token"]

    try:
        client = ScmClient(api_base_url=api_url, access_token=scm_access_token)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {str(e)}")

    result = {"changed": False, "msg": ""}
    lookup_params = {container_type: container_name}

    try:
        # STATE: absent
        if state == "absent":
            try:
                existing_zone = client.security_zone.fetch(name=zone_name, **lookup_params)
                if existing_zone:
                    client.security_zone.delete(str(existing_zone.id))
                    result["changed"] = True
                    result["msg"] = f"Security zone '{zone_name}' deleted"
            except ObjectNotPresentError:
                result["msg"] = f"Security zone '{zone_name}' not found (already absent)"
            module.exit_json(**result)

        # STATE: present
        zone_data = {"name": zone_name, container_type: container_name}

        if params.get("network"):
            zone_data["network"] = params["network"]
        if params.get("enable_user_identification") is not None:
            zone_data["enable_user_identification"] = params["enable_user_identification"]
        if params.get("enable_device_identification") is not None:
            zone_data["enable_device_identification"] = params["enable_device_identification"]

        # Check if zone exists
        existing_zone = None
        with contextlib.suppress(ObjectNotPresentError):
            existing_zone = client.security_zone.fetch(name=zone_name, **lookup_params)

        if existing_zone:
            # Update if needed
            needs_update = False
            if params.get("network") and params["network"] != (existing_zone.network.model_dump() if existing_zone.network else None):
                needs_update = True
            if params.get("enable_user_identification") is not None and params["enable_user_identification"] != existing_zone.enable_user_identification:
                needs_update = True
            if params.get("enable_device_identification") is not None and params["enable_device_identification"] != existing_zone.enable_device_identification:
                needs_update = True

            if needs_update:
                zone_data["id"] = str(existing_zone.id)
                update_model = SecurityZoneUpdateModel(**zone_data)
                updated_zone = client.security_zone.update(update_model)
                result["changed"] = True
                result["msg"] = f"Security zone '{zone_name}' updated"
                zone_dict = updated_zone.model_dump(exclude_unset=True)
                zone_dict["id"] = str(zone_dict["id"])
                result["zone"] = zone_dict
            else:
                result["msg"] = f"Security zone '{zone_name}' already exists with correct configuration"
                zone_dict = existing_zone.model_dump(exclude_unset=True)
                zone_dict["id"] = str(zone_dict["id"])
                result["zone"] = zone_dict
        else:
            # Create new zone
            created_zone = client.security_zone.create(zone_data)
            result["changed"] = True
            result["msg"] = f"Security zone '{zone_name}' created"
            zone_dict = created_zone.model_dump(exclude_unset=True)
            zone_dict["id"] = str(zone_dict["id"])
            result["zone"] = zone_dict

    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
