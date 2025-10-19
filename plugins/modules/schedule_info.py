#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: schedule_info
short_description: Get information about schedule objects in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about schedule objects in Strata Cloud Manager.
    - It can be used to get details about a specific schedule by ID or name, or to list all schedules.
    - Supports filtering by folder, snippet, or device container.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the schedule object to retrieve.
            - If specified, the module will return information about this specific schedule.
            - Mutually exclusive with I(name).
            - When using id, no container parameter is required.
        type: str
        required: false
    name:
        description:
            - The name of the schedule object to retrieve.
            - If specified, the module will search for schedules with this name.
            - When using name, one of the container parameters (folder, snippet, device) is required.
            - Mutually exclusive with I(id).
        type: str
        required: false
    folder:
        description:
            - Filter schedules by folder name.
            - Required when retrieving schedules by name or listing schedules.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - Filter schedules by snippet name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - Filter schedules by device identifier.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - If False, the search might include objects in subcontainers.
        type: bool
        default: False
        required: false
    scm_access_token:
        description:
            - The access token for SCM authentication.
        type: str
        required: true
    api_url:
        description:
            - The URL for the SCM API.
        type: str
        required: false
notes:
    - Check mode is supported but does not change behavior since this is a read-only module.
    - Schedule objects must be associated with exactly one container (folder, snippet, or device).
    - When retrieving by name, a container parameter must be provided.
    - When retrieving by ID, no container parameter is needed.
"""

EXAMPLES = r"""
- name: Get all schedule objects in a folder
  cdot65.scm.schedule_info:
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
  register: all_schedules

- name: Get a specific schedule by ID
  cdot65.scm.schedule_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
  register: schedule_details

- name: Get schedule with a specific name
  cdot65.scm.schedule_info:
    name: "business-hours"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
  register: named_schedule

- name: Get schedules in a specific snippet
  cdot65.scm.schedule_info:
    snippet: "security-snippet"
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_schedules

- name: Get schedules for a specific device
  cdot65.scm.schedule_info:
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
  register: device_schedules

- name: Get schedules with exact container match
  cdot65.scm.schedule_info:
    folder: "Security-Policies"
    exact_match: true
    scm_access_token: "{{ scm_access_token }}"
  register: exact_match_schedules
"""

RETURN = r"""
schedules:
    description: List of schedule objects
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: The schedule object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The schedule object name
            type: str
            returned: always
            sample: "business-hours"
        schedule_type:
            description: The schedule type configuration
            type: dict
            returned: always
            contains:
                recurring:
                    description: Recurring schedule configuration
                    type: dict
                    returned: when applicable
                    contains:
                        daily:
                            description: Daily time ranges
                            type: list
                            returned: when applicable
                            sample: ["08:00-17:00"]
                        weekly:
                            description: Weekly schedule with day-specific time ranges
                            type: dict
                            returned: when applicable
                            sample: {"monday": ["08:00-17:00"], "friday": ["08:00-15:00"]}
                non_recurring:
                    description: Non-recurring datetime ranges
                    type: list
                    returned: when applicable
                    sample: ["2025/12/24@00:00-2025/12/26@23:59"]
        folder:
            description: The folder containing the schedule object
            type: str
            returned: when applicable
            sample: "Security-Policies"
        snippet:
            description: The snippet containing the schedule object
            type: str
            returned: when applicable
            sample: "security-snippet"
        device:
            description: The device containing the schedule object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        exact_match=dict(type="bool", required=False, default=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["id", "name"],
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"schedules": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get schedule by ID if specified
        if params.get("id"):
            try:
                schedule_obj = client.schedule.get(params.get("id"))
                if schedule_obj:
                    result["schedules"] = [json.loads(schedule_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve schedule info: {e}")
        # Fetch schedule by name
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

                # We need a container for the fetch operation
                if not container_type or not container_name:
                    module.fail_json(
                        msg="When retrieving a schedule by name, one of 'folder', 'snippet', or 'device' parameter is required"
                    )

                # For any container type, fetch the schedule object
                schedule_obj = client.schedule.fetch(name=params.get("name"), **{container_type: container_name})
                if schedule_obj:
                    result["schedules"] = [json.loads(schedule_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve schedule info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}

            # Add container filters (folder, snippet, device) - at least one is required
            if params.get("folder"):
                filter_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                filter_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                filter_params["device"] = params.get("device")
            else:
                module.fail_json(
                    msg="At least one container parameter (folder, snippet, or device) is required for listing schedules"
                )

            # Add exact_match parameter if specified
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")

            # List schedules with container filters
            schedules = client.schedule.list(**filter_params)

            # Convert to a list of dicts
            schedule_dicts = [json.loads(s.model_dump_json(exclude_unset=True)) for s in schedules]

            # Add to results
            result["schedules"] = schedule_dicts

        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve schedule info: {e}")


if __name__ == "__main__":
    main()
