#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import ExternalDynamicListsCreateModel

DOCUMENTATION = r"""
---
module: external_dynamic_list
short_description: Manage external dynamic list objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete external dynamic list objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all EDL types (predefined_ip, predefined_url, ip, domain, url, imsi, imei) and attributes.
    - External dynamic list objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the external dynamic list object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 63 characters.
        type: str
        required: false
    type:
        description:
            - The type of external dynamic list.
            - One of predefined_ip, predefined_url, ip, domain, url, imsi, imei.
            - Required for state=present.
        type: str
        required: false
        choices: ['predefined_ip', 'predefined_url', 'ip', 'domain', 'url', 'imsi', 'imei']
    url:
        description:
            - URL for the external dynamic list source.
            - Required for all types except those in the 'predefined' category.
        type: str
        required: false
    description:
        description:
            - Description for the external dynamic list object.
        type: str
        required: false
    exception_list:
        description:
            - List of entries to exclude from the external dynamic list.
        type: list
        elements: str
        required: false
    recurring:
        description:
            - Recurring update schedule for the external dynamic list.
            - Required for non-predefined types.
            - Must be a dict containing one of five_minute, hourly, daily, weekly, or monthly.
        type: dict
        required: false
    auth:
        description:
            - Authentication credentials for accessing the external dynamic list.
            - A dict containing username and password.
        type: dict
        required: false
    certificate_profile:
        description:
            - Profile for authenticating client certificates.
        type: str
        required: false
    expand_domain:
        description:
            - Enable domain expansion for domain type lists.
            - Only applicable for domain type.
        type: bool
        required: false
    folder:
        description:
            - The folder in which the external dynamic list object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the external dynamic list object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the external dynamic list object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the external dynamic list object (UUID).
            - Used for lookup/deletion if provided.
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
    state:
        description:
            - Desired state of the external dynamic list object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - External dynamic list objects must be associated with exactly one container (folder, snippet, or device).
    - Different types of external dynamic lists require different configurations.
    - The "predefined_ip" and "predefined_url" types don't require recurring schedule configuration.
"""

EXAMPLES = r"""
- name: Create a predefined IP external dynamic list
  cdot65.scm.external_dynamic_list:
    name: "blocklist-ips"
    type: "predefined_ip"
    url: "panw-blocklist-ip"
    description: "Predefined IP blocklist"
    folder: "EDL-Folder"
    exception_list:
      - "192.168.1.100"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a custom IP external dynamic list with hourly update
  cdot65.scm.external_dynamic_list:
    name: "custom-ips"
    type: "ip"
    url: "https://example.com/ip-list.txt"
    description: "Custom IP list"
    folder: "EDL-Folder"
    recurring:
      hourly: {}
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a domain external dynamic list with daily update and authentication
  cdot65.scm.external_dynamic_list:
    name: "malicious-domains"
    type: "domain"
    url: "https://example.com/domains.txt"
    description: "Malicious domains list"
    folder: "EDL-Folder"
    recurring:
      daily:
        at: "01"  # Update at 1am
    auth:
      username: "user"
      password: "password"
    expand_domain: true
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a url external dynamic list with weekly update
  cdot65.scm.external_dynamic_list:
    name: "url-list"
    type: "url"
    url: "https://example.com/urls.txt"
    snippet: "EDL-Snippet"
    recurring:
      weekly:
        day_of_week: "monday"
        at: "04"  # Update at 4am
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update an existing external dynamic list
  cdot65.scm.external_dynamic_list:
    name: "blocklist-ips"
    type: "predefined_ip"
    url: "panw-blocklist-ip"
    description: "Updated predefined IP blocklist"
    folder: "EDL-Folder"
    exception_list:
      - "192.168.1.100"
      - "192.168.1.101"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete an external dynamic list by name
  cdot65.scm.external_dynamic_list:
    name: "blocklist-ips"
    folder: "EDL-Folder"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete an external dynamic list by ID
  cdot65.scm.external_dynamic_list:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
external_dynamic_list:
    description: Information about the external dynamic list object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The external dynamic list object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The external dynamic list object name
            type: str
            returned: always
            sample: "blocklist-ips"
        type:
            description: The type configuration of the external dynamic list
            type: dict
            returned: always
            sample: {"predefined_ip": {"url": "panw-blocklist-ip", "description": "Predefined IP blocklist"}}
        description:
            description: The external dynamic list object description (inside type dict)
            type: str
            returned: when applicable
            sample: "Predefined IP blocklist"
        url:
            description: The URL for the external dynamic list (inside type dict)
            type: str
            returned: always
            sample: "panw-blocklist-ip"
        exception_list:
            description: Entries excluded from the external dynamic list (inside type dict)
            type: list
            returned: when applicable
            sample: ["192.168.1.100"]
        recurring:
            description: Recurring update schedule configuration (inside type dict)
            type: dict
            returned: for non-predefined types
            sample: {"hourly": {}}
        folder:
            description: The folder containing the external dynamic list object
            type: str
            returned: when applicable
            sample: "EDL-Folder"
        snippet:
            description: The snippet containing the external dynamic list object
            type: str
            returned: when applicable
            sample: "EDL-Snippet"
        device:
            description: The device containing the external dynamic list object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def build_edl_type_config(params):
    """Build the type configuration based on the specified type."""
    edl_type = params.get("type")
    if not edl_type:
        return None

    type_config = {}

    # Common fields for all types
    type_fields = {
        "url": params.get("url"),
        "description": params.get("description"),
        "exception_list": params.get("exception_list"),
    }

    # Remove None values
    type_fields = {k: v for k, v in type_fields.items() if v is not None}

    # Add type-specific fields
    if edl_type in ["predefined_ip", "predefined_url"]:
        # Predefined types only need url, description, and exception_list
        type_config[edl_type] = type_fields
    else:
        # Other types need recurring and can have auth and certificate_profile
        type_fields["recurring"] = params.get("recurring")

        if params.get("auth"):
            type_fields["auth"] = params.get("auth")

        if params.get("certificate_profile"):
            type_fields["certificate_profile"] = params.get("certificate_profile")

        # Domain type can have expand_domain
        if edl_type == "domain" and params.get("expand_domain") is not None:
            type_fields["expand_domain"] = params.get("expand_domain")

        type_config[edl_type] = type_fields

    return type_config


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        type=dict(
            type="str", required=False, choices=["predefined_ip", "predefined_url", "ip", "domain", "url", "imsi", "imei"]
        ),
        url=dict(type="str", required=False),
        description=dict(type="str", required=False),
        exception_list=dict(type="list", elements="str", required=False),
        recurring=dict(type="dict", required=False),
        auth=dict(type="dict", required=False, no_log=True),
        certificate_profile=dict(type="str", required=False),
        expand_domain=dict(type="bool", required=False),
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
            ["state", "present", ["name", "type"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for container parameters
    if params.get("state") == "present":
        # For creation/update, one of the container types is required
        if not any(params.get(container_type) for container_type in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

        # Validate URL is provided for all types
        if not params.get("url"):
            module.fail_json(msg="The 'url' parameter is required for all external dynamic list types")

        # Validate recurring is provided for non-predefined types
        edl_type = params.get("type")
        if edl_type not in ["predefined_ip", "predefined_url"] and not params.get("recurring"):
            module.fail_json(msg=f"The 'recurring' parameter is required for '{edl_type}' type")

        # Validate recurring configuration
        recurring = params.get("recurring")
        if recurring:
            if len(recurring) != 1:
                module.fail_json(
                    msg="The 'recurring' must contain exactly one key (five_minute, hourly, daily, weekly, or monthly)"
                )

            valid_keys = ["five_minute", "hourly", "daily", "weekly", "monthly"]
            recurring_key = list(recurring.keys())[0]

            if recurring_key not in valid_keys:
                module.fail_json(msg=f"Invalid 'recurring' key: {recurring_key}. Must be one of: {', '.join(valid_keys)}")

            # Validate time format for daily, weekly, monthly
            if recurring_key in ["daily", "weekly", "monthly"]:
                recurring_value = recurring[recurring_key]

                if "at" in recurring_value:
                    at_value = recurring_value["at"]
                    if not isinstance(at_value, str) or not at_value.isdigit() or int(at_value) < 0 or int(at_value) > 23:
                        module.fail_json(
                            msg=f"Invalid 'at' value in {recurring_key}: {at_value}. Must be a string representing an hour (00-23)"
                        )

                if recurring_key == "weekly" and "day_of_week" in recurring_value:
                    valid_days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
                    day = recurring_value["day_of_week"]
                    if day not in valid_days:
                        module.fail_json(msg=f"Invalid 'day_of_week' value: {day}. Must be one of: {', '.join(valid_days)}")

                if recurring_key == "monthly" and "day_of_month" in recurring_value:
                    day = recurring_value["day_of_month"]
                    if not isinstance(day, int) or day < 1 or day > 31:
                        module.fail_json(msg=f"Invalid 'day_of_month' value: {day}. Must be an integer between 1 and 31")

    # Initialize results
    result = {"changed": False, "external_dynamic_list": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize edl_exists boolean
        edl_exists = False
        edl_obj = None

        # Fetch by ID or name+container
        if params.get("id"):
            try:
                edl_obj = client.external_dynamic_list.get(params.get("id"))
                if edl_obj:
                    edl_exists = True
            except ObjectNotPresentError:
                edl_exists = False
                edl_obj = None

        # Fetch by name
        elif params.get("name"):
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

                # For any container type, fetch the object
                if container_type and container_name:
                    edl_obj = client.external_dynamic_list.fetch(name=params.get("name"), **{container_type: container_name})
                    if edl_obj:
                        edl_exists = True
            except ObjectNotPresentError:
                edl_exists = False
                edl_obj = None

        # Create or update or delete
        if params.get("state") == "present":
            if edl_exists:
                # Build the type configuration
                type_config = build_edl_type_config(params)

                # Determine the updates needed
                update_fields = {}

                # Basic fields
                if params.get("name") and params.get("name") != edl_obj.name:
                    update_fields["name"] = params.get("name")

                # Container fields - only one should be set
                if params.get("folder") and getattr(edl_obj, "folder", None) != params.get("folder"):
                    update_fields["folder"] = params.get("folder")
                elif params.get("snippet") and getattr(edl_obj, "snippet", None) != params.get("snippet"):
                    update_fields["snippet"] = params.get("snippet")
                elif params.get("device") and getattr(edl_obj, "device", None) != params.get("device"):
                    update_fields["device"] = params.get("device")

                # Type configuration
                if type_config and type_config != getattr(edl_obj, "type", None):
                    update_fields["type"] = type_config

                # Update if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = edl_obj.model_copy(update=update_fields)
                        updated = client.external_dynamic_list.update(update_model)
                        result["external_dynamic_list"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["external_dynamic_list"] = json.loads(edl_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["external_dynamic_list"] = json.loads(edl_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Build the type configuration
                type_config = build_edl_type_config(params)

                # Create payload
                create_payload = {
                    "name": params.get("name"),
                    "type": type_config,
                }

                # Add container
                if params.get("folder"):
                    create_payload["folder"] = params.get("folder")
                elif params.get("snippet"):
                    create_payload["snippet"] = params.get("snippet")
                elif params.get("device"):
                    create_payload["device"] = params.get("device")

                # Create an external dynamic list object
                if not module.check_mode:
                    created = client.external_dynamic_list.create(create_payload)
                    result["external_dynamic_list"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created object
                    simulated = ExternalDynamicListsCreateModel(**create_payload)
                    result["external_dynamic_list"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete
        elif params.get("state") == "absent":
            if edl_exists:
                if not module.check_mode:
                    client.external_dynamic_list.delete(edl_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["external_dynamic_list"] = json.loads(edl_obj.model_dump_json(exclude_unset=True))
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
