#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import ServiceCreateModel

DOCUMENTATION = r"""
---
module: service
short_description: Manage service objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete service objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all service attributes including TCP and UDP protocols with timeout overrides.
    - Service objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the service object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    description:
        description:
            - Description of the service object.
            - Maximum length is 1023 characters.
        type: str
        required: false
    tag:
        description:
            - Tags associated with the service object.
        type: list
        elements: str
        required: false
    protocol:
        description:
            - Protocol configuration for the service.
            - Must contain either 'tcp' or 'udp' key with port configuration.
            - Required for state=present.
        type: dict
        required: false
        suboptions:
            tcp:
                description:
                    - TCP protocol configuration.
                    - Mutually exclusive with I(udp).
                type: dict
                suboptions:
                    port:
                        description:
                            - TCP port(s) associated with the service.
                            - Can be a single port, comma-separated ports, or port range.
                        type: str
                        required: true
                    override:
                        description:
                            - Override settings for TCP protocol timeouts.
                        type: dict
                        suboptions:
                            timeout:
                                description:
                                    - Timeout in seconds.
                                type: int
                            halfclose_timeout:
                                description:
                                    - Half-close timeout in seconds.
                                type: int
                            timewait_timeout:
                                description:
                                    - Time-wait timeout in seconds.
                                type: int
            udp:
                description:
                    - UDP protocol configuration.
                    - Mutually exclusive with I(tcp).
                type: dict
                suboptions:
                    port:
                        description:
                            - UDP port(s) associated with the service.
                            - Can be a single port, comma-separated ports, or port range.
                        type: str
                        required: true
                    override:
                        description:
                            - Override settings for UDP protocol timeouts.
                        type: dict
                        suboptions:
                            timeout:
                                description:
                                    - Timeout in seconds.
                                type: int
    folder:
        description:
            - The folder in which the service object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the service object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the service object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the service object (UUID).
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
            - Desired state of the service object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Service objects must be associated with exactly one container (folder, snippet, or device).
    - Protocol configuration must contain exactly one of tcp or udp.
"""

EXAMPLES = r"""
- name: Create a TCP service object
  cdot65.scm.service:
    name: "service-http"
    description: "HTTP service"
    protocol:
      tcp:
        port: "80"
    folder: "Services"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a TCP service with timeout overrides
  cdot65.scm.service:
    name: "service-https"
    description: "HTTPS service with custom timeouts"
    protocol:
      tcp:
        port: "443"
        override:
          timeout: 30
          halfclose_timeout: 15
          timewait_timeout: 10
    folder: "Services"
    tag:
      - "web"
      - "secure"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a UDP service object
  cdot65.scm.service:
    name: "service-dns"
    description: "DNS service"
    protocol:
      udp:
        port: "53"
    snippet: "network-services"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a service with multiple ports
  cdot65.scm.service:
    name: "service-web-alt"
    description: "Alternative web ports"
    protocol:
      tcp:
        port: "8080,8443"
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a service object's description
  cdot65.scm.service:
    name: "service-http"
    description: "Updated HTTP service description"
    protocol:
      tcp:
        port: "80"
    folder: "Services"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a service object by name
  cdot65.scm.service:
    name: "service-http"
    folder: "Services"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a service object by ID
  cdot65.scm.service:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
service:
    description: Information about the service object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The service object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The service object name
            type: str
            returned: always
            sample: "service-http"
        description:
            description: The service object description
            type: str
            returned: when applicable
            sample: "HTTP service"
        protocol:
            description: The protocol configuration
            type: dict
            returned: always
            sample: {"tcp": {"port": "80"}}
        tag:
            description: Tags associated with the service object
            type: list
            returned: when applicable
            sample: ["web", "secure"]
        folder:
            description: The folder containing the service object
            type: str
            returned: when applicable
            sample: "Services"
        snippet:
            description: The snippet containing the service object
            type: str
            returned: when applicable
            sample: "network-services"
        device:
            description: The device containing the service object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tag=dict(type="list", elements="str", required=False),
        protocol=dict(type="dict", required=False),
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
            ["state", "present", ["name", "protocol"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Validate name parameter
    if params.get("name"):
        name = params.get("name")
        if len(name) > 63:
            module.fail_json(msg=f"Parameter 'name' exceeds maximum length of 63 characters (got {len(name)})")
        # Validate name pattern to match SDK requirements
        import re

        if not re.match(r"^[a-zA-Z0-9_ \.-]+$", name):
            module.fail_json(msg="Parameter 'name' contains invalid characters. Must match pattern: ^[a-zA-Z0-9_ \\.-]+$")

    # Custom validation for protocol
    if params.get("state") == "present":
        if not params.get("protocol"):
            module.fail_json(msg="When state=present, 'protocol' is required")

        protocol = params.get("protocol")
        if not isinstance(protocol, dict):
            module.fail_json(msg="'protocol' must be a dictionary")

        if "tcp" not in protocol and "udp" not in protocol:
            module.fail_json(msg="'protocol' must contain either 'tcp' or 'udp' key")

        if "tcp" in protocol and "udp" in protocol:
            module.fail_json(msg="'protocol' cannot contain both 'tcp' and 'udp' keys")

    # Initialize results
    result = {"changed": False, "service": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize service_exists boolean
        service_exists = False
        service_obj = None

        # Fetch service by name
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

                # For any container type, fetch the service object
                if container_type and container_name:
                    service_obj = client.service.fetch(name=params.get("name"), **{container_type: container_name})
                    if service_obj:
                        service_exists = True
            except ObjectNotPresentError:
                service_exists = False
                service_obj = None

        # Create or update or delete a service
        if params.get("state") == "present":
            if service_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Check simple fields
                for field in ["description", "tag", "folder", "snippet", "device"]:
                    if params.get(field) is not None and getattr(service_obj, field, None) != params.get(field):
                        update_fields[field] = params[field]

                # Check protocol field
                if params.get("protocol") is not None:
                    # Compare protocol dictionaries
                    current_protocol = service_obj.protocol.model_dump(exclude_unset=True) if service_obj.protocol else {}
                    if current_protocol != params.get("protocol"):
                        update_fields["protocol"] = params["protocol"]

                # Update the service if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = service_obj.model_copy(update=update_fields)
                        updated = client.service.update(update_model)
                        result["service"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["service"] = json.loads(service_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["service"] = json.loads(service_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new service object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "tag",
                        "protocol",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a service object
                if not module.check_mode:
                    # Create a service object
                    created = client.service.create(create_payload)

                    # Return the created service object
                    result["service"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created service object (minimal info)
                    simulated = ServiceCreateModel(**create_payload)
                    result["service"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a service object
        elif params.get("state") == "absent":
            if service_exists:
                if not module.check_mode:
                    client.service.delete(service_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["service"] = json.loads(service_obj.model_dump_json(exclude_unset=True))
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
