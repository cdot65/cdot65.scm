#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import Scm as ScmClient
from scm.exceptions import APIError, ObjectNotPresentError
from scm.models.security import DNSSecurityProfileCreateModel

DOCUMENTATION = r"""
---
module: dns_security_profile
short_description: Manage DNS Security profiles in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete DNS Security profiles in Strata Cloud Manager using pan-scm-sdk.
    - DNS Security profiles protect against DNS-based threats including botnet domains.
    - Supports botnet domain categories, custom lists, sinkhole settings, and whitelists.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the DNS Security profile.
        type: str
        required: false
    description:
        description:
            - Description of the DNS Security profile.
        type: str
        required: false
    botnet_domains:
        description:
            - Botnet domains configuration as a dictionary.
            - Includes dns_security_categories, lists, sinkhole, and whitelist.
        type: dict
        required: false
    folder:
        description:
            - The folder in which the resource is defined.
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the resource is defined.
        type: str
        required: false
    device:
        description:
            - The device in which the resource is defined.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the DNS Security profile (UUID).
        type: str
        required: false
    scm_access_token:
        description:
            - Bearer access token for authenticating API calls.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
    state:
        description:
            - Desired state of the DNS Security profile.
        type: str
        choices: ['present', 'absent']
        default: present
"""

EXAMPLES = r"""
- name: Create DNS Security profile
  cdot65.scm.dns_security_profile:
    name: "Example-DNS-Security"
    description: "DNS security profile"
    botnet_domains:
      dns_security_categories:
        - name: "pan-dns-sec-benign"
          action: "allow"
          log_level: "default"
        - name: "pan-dns-sec-cc"
          action: "sinkhole"
          log_level: "medium"
      sinkhole:
        ipv4_address: "pan-sinkhole-default-ip"
        ipv6_address: "::1"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
    state: present
"""

RETURN = r"""
changed:
    description: Whether changes were made.
    returned: always
    type: bool
dns_security_profile:
    description: The DNS Security profile data.
    returned: when state=present
    type: dict
"""


def main():
    """Main module execution."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=False),
            description=dict(type="str", required=False),
            botnet_domains=dict(type="dict", required=False),
            folder=dict(type="str", required=False),
            snippet=dict(type="str", required=False),
            device=dict(type="str", required=False),
            id=dict(type="str", required=False),
            scm_access_token=dict(type="str", required=True, no_log=True),
            api_url=dict(type="str", required=False),
            state=dict(type="str", choices=["present", "absent"], default="present"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["folder", "snippet", "device"]],
    )

    result = {"changed": False, "msg": "", "dns_security_profile": {}}
    params = module.params
    state = params["state"]
    api_url = params.get("api_url") or "https://api.strata.paloaltonetworks.com"

    try:
        client = ScmClient(access_token=params["scm_access_token"], api_base_url=api_url)
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize SCM client: {e!s}")

    container_type = next((ct for ct in ["folder", "snippet", "device"] if params.get(ct)), None)
    container_name = params.get(container_type) if container_type else None
    lookup_params = {container_type: container_name} if container_type else {}

    existing_profile = None
    profile_id = params.get("id")
    profile_name = params.get("name")

    if profile_id:
        try:
            existing_profile = client.dns_security_profile.fetch(profile_id)
        except ObjectNotPresentError:
            pass
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by ID: {e!s}")
    elif profile_name and container_type:
        try:
            existing_profile = client.dns_security_profile.fetch(name=profile_name, **lookup_params)
        except ObjectNotPresentError:
            pass
        except APIError as e:
            module.fail_json(msg=f"Failed to fetch profile by name: {e!s}")

    if state == "absent":
        if existing_profile:
            if not module.check_mode:
                try:
                    client.dns_security_profile.delete(str(existing_profile.id))
                    result["msg"] = f"DNS Security profile '{profile_name or profile_id}' deleted"
                except APIError as e:
                    module.fail_json(msg=f"Failed to delete profile: {e!s}")
            result["changed"] = True
        else:
            result["msg"] = f"DNS Security profile '{profile_name or profile_id}' not found"
        module.exit_json(**result)

    if not container_type or not profile_name:
        module.fail_json(msg="'name' and one container (folder/snippet/device) required for state=present")

    profile_data = {"name": profile_name, container_type: container_name}
    if params.get("description"):
        profile_data["description"] = params["description"]
    if params.get("botnet_domains"):
        profile_data["botnet_domains"] = params["botnet_domains"]

    try:
        DNSSecurityProfileCreateModel(**profile_data)
    except Exception as e:
        module.fail_json(msg=f"Failed to validate profile data: {e!s}")

    if existing_profile:
        result["dns_security_profile"] = json.loads(existing_profile.model_dump_json())
        result["msg"] = f"DNS Security profile '{profile_name}' exists (update not implemented)"
    else:
        if not module.check_mode:
            try:
                created = client.dns_security_profile.create(profile_data)
                result["dns_security_profile"] = json.loads(created.model_dump_json())
                result["msg"] = f"DNS Security profile '{profile_name}' created"
            except APIError as e:
                module.fail_json(msg=f"Failed to create profile: {e!s}")
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()
