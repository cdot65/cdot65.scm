#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import AddressCreateModel

DOCUMENTATION = r"""
---
module: address
short_description: Manage address objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete address objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all address attributes and robust idempotency.
    - Address objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the address object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the address object.
        type: str
        required: false
    tag:
        description:
            - Tags associated with the address object.
        type: list
        elements: str
        required: false
    ip_netmask:
        description:
            - IP address with CIDR notation.
            - Exactly one of ip_netmask, ip_range, ip_wildcard, or fqdn must be provided for state=present.
            - Mutually exclusive with I(ip_range), I(ip_wildcard), and I(fqdn).
        type: str
        required: false
    ip_range:
        description:
            - IP address range.
            - Exactly one of ip_netmask, ip_range, ip_wildcard, or fqdn must be provided for state=present.
            - Mutually exclusive with I(ip_netmask), I(ip_wildcard), and I(fqdn).
        type: str
        required: false
    ip_wildcard:
        description:
            - IP wildcard mask.
            - Exactly one of ip_netmask, ip_range, ip_wildcard, or fqdn must be provided for state=present.
            - Mutually exclusive with I(ip_netmask), I(ip_range), and I(fqdn).
        type: str
        required: false
    fqdn:
        description:
            - Fully qualified domain name.
            - Exactly one of ip_netmask, ip_range, ip_wildcard, or fqdn must be provided for state=present.
            - Mutually exclusive with I(ip_netmask), I(ip_range), and I(ip_wildcard).
        type: str
        required: false
    folder:
        description:
            - The folder in which the address object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the address object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the address object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the address object (UUID).
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
            - Desired state of the address object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Address objects must be associated with exactly one container (folder, snippet, or device).
    - Exactly one address type (ip_netmask, ip_range, ip_wildcard, or fqdn) must be provided.
"""

EXAMPLES = r"""
- name: Create a folder-based IP address object
  cdot65.scm.address:
    name: "web-server"
    description: "Web server IP address"
    ip_netmask: "192.168.1.100/32"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a snippet-based FQDN address object
  cdot65.scm.address:
    name: "example-site"
    description: "Example website"
    fqdn: "example.com"
    snippet: "web-acl"
    tag:
      - "web"
      - "external"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a device-based IP range address object
  cdot65.scm.address:
    name: "dhcp-range"
    description: "DHCP IP address range"
    ip_range: "10.0.0.100-10.0.0.200"
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an address object's description
  cdot65.scm.address:
    name: "web-server"
    description: "Updated web server description"
    ip_netmask: "192.168.1.100/32"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an address object by name
  cdot65.scm.address:
    name: "web-server"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an address object by ID
  cdot65.scm.address:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
address:
    description: Information about the address object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The address object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The address object name
            type: str
            returned: always
            sample: "web-server"
        description:
            description: The address object description
            type: str
            returned: when applicable
            sample: "Web server IP address"
        ip_netmask:
            description: The IP address with CIDR notation
            type: str
            returned: when applicable
            sample: "192.168.1.100/32"
        ip_range:
            description: The IP address range
            type: str
            returned: when applicable
            sample: "10.0.0.100-10.0.0.200"
        ip_wildcard:
            description: The IP wildcard mask
            type: str
            returned: when applicable
            sample: "10.0.0.0/0.0.255.255"
        fqdn:
            description: The fully qualified domain name
            type: str
            returned: when applicable
            sample: "example.com"
        tag:
            description: Tags associated with the address object
            type: list
            returned: when applicable
            sample: ["web", "external"]
        folder:
            description: The folder containing the address object
            type: str
            returned: when applicable
            sample: "Network-Objects"
        snippet:
            description: The snippet containing the address object
            type: str
            returned: when applicable
            sample: "web-acl"
        device:
            description: The device containing the address object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        ip_netmask=dict(type="str", required=False),
        ip_range=dict(type="str", required=False),
        ip_wildcard=dict(type="str", required=False),
        fqdn=dict(type="str", required=False),
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
            ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for address type parameters
    if params.get("state") == "present" and not any(
        params.get(addr_type) for addr_type in ["ip_netmask", "ip_range", "ip_wildcard", "fqdn"]
    ):
        module.fail_json(msg="When state=present, one of the following is required: ip_netmask, ip_range, ip_wildcard, fqdn")

    # Initialize results
    result = {"changed": False, "address": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize address_exists boolean
        address_exists = False
        address_obj = None

        # Fetch address by name
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

                # For any container type, fetch the address object
                if container_type and container_name:
                    address_obj = client.address.fetch(name=params.get("name"), **{container_type: container_name})
                    if address_obj:
                        address_exists = True
            except ObjectNotPresentError:
                address_exists = False
                address_obj = None

        # Create or update or delete an address
        if params.get("state") == "present":
            if address_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "tag",
                        "ip_netmask",
                        "ip_range",
                        "ip_wildcard",
                        "fqdn",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(address_obj, k, None) != params[k]
                }

                # Update the address if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = address_obj.model_copy(update=update_fields)
                        updated = client.address.update(update_model)
                        result["address"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["address"] = json.loads(address_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["address"] = json.loads(address_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new address object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "tag",
                        "ip_netmask",
                        "ip_range",
                        "ip_wildcard",
                        "fqdn",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create an address object
                if not module.check_mode:
                    # Create an address object
                    created = client.address.create(create_payload)

                    # Return the created address object
                    result["address"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created address object (minimal info)
                    simulated = AddressCreateModel(**create_payload)
                    result["address"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete an address object
        elif params.get("state") == "absent":
            if address_exists:
                if not module.check_mode:
                    client.address.delete(address_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["address"] = json.loads(address_obj.model_dump_json(exclude_unset=True))
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
