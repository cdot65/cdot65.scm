#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import ScheduleCreateModel

DOCUMENTATION = r"""
---
module: schedule
short_description: Manage schedule objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete schedule objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports both recurring (weekly/daily) and non-recurring schedule types.
    - Schedule objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the schedule object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 31 characters.
            - Pattern must match ^[ a-zA-Z\d._-]+$
        type: str
        required: false
    schedule_type:
        description:
            - The type and configuration of the schedule.
            - Must contain exactly one of 'recurring' or 'non_recurring'.
            - Required for state=present.
        type: dict
        required: false
        suboptions:
            recurring:
                description:
                    - Configuration for recurring schedules.
                    - Must contain exactly one of 'weekly' or 'daily'.
                type: dict
                required: false
                suboptions:
                    weekly:
                        description:
                            - Weekly schedule configuration with time ranges for specific days.
                            - At least one day must have time ranges defined.
                        type: dict
                        required: false
                        suboptions:
                            sunday:
                                description: List of time ranges for Sunday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            monday:
                                description: List of time ranges for Monday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            tuesday:
                                description: List of time ranges for Tuesday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            wednesday:
                                description: List of time ranges for Wednesday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            thursday:
                                description: List of time ranges for Thursday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            friday:
                                description: List of time ranges for Friday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                            saturday:
                                description: List of time ranges for Saturday (HH:MM-HH:MM format).
                                type: list
                                elements: str
                                required: false
                    daily:
                        description:
                            - Daily schedule configuration with time ranges applied to every day.
                            - Must contain at least one time range in HH:MM-HH:MM format.
                        type: list
                        elements: str
                        required: false
            non_recurring:
                description:
                    - Configuration for non-recurring (one-time) schedules.
                    - Must contain at least one datetime range.
                    - Format YYYY/MM/DD@HH:MM-YYYY/MM/DD@HH:MM with leading zeros required.
                type: list
                elements: str
                required: false
    folder:
        description:
            - The folder in which the schedule object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the schedule object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the schedule object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the schedule object (UUID).
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
            - Desired state of the schedule object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Schedule objects must be associated with exactly one container (folder, snippet, or device).
    - schedule_type must contain exactly one of 'recurring' or 'non_recurring'.
    - For recurring schedules, exactly one of 'weekly' or 'daily' must be provided.
    - Time ranges must follow HH:MM-HH:MM format (00:00-23:59).
    - Non-recurring datetime ranges must follow YYYY/MM/DD@HH:MM-YYYY/MM/DD@HH:MM format with leading zeros.
"""

EXAMPLES = r"""
- name: Create a daily recurring schedule
  cdot65.scm.schedule:
    name: "business-hours"
    schedule_type:
      recurring:
        daily:
          - "08:00-17:00"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a weekly recurring schedule
  cdot65.scm.schedule:
    name: "weekend-maintenance"
    schedule_type:
      recurring:
        weekly:
          saturday:
            - "02:00-06:00"
          sunday:
            - "02:00-06:00"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a complex weekly schedule
  cdot65.scm.schedule:
    name: "weekday-schedule"
    schedule_type:
      recurring:
        weekly:
          monday:
            - "08:00-12:00"
            - "13:00-17:00"
          tuesday:
            - "08:00-12:00"
            - "13:00-17:00"
          wednesday:
            - "08:00-12:00"
            - "13:00-17:00"
          thursday:
            - "08:00-12:00"
            - "13:00-17:00"
          friday:
            - "08:00-12:00"
            - "13:00-15:00"
    snippet: "security-snippet"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a non-recurring schedule
  cdot65.scm.schedule:
    name: "holiday-blackout"
    schedule_type:
      non_recurring:
        - "2025/12/24@00:00-2025/12/26@23:59"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a multi-date non-recurring schedule
  cdot65.scm.schedule:
    name: "maintenance-windows"
    schedule_type:
      non_recurring:
        - "2025/01/15@02:00-2025/01/15@06:00"
        - "2025/02/15@02:00-2025/02/15@06:00"
        - "2025/03/15@02:00-2025/03/15@06:00"
    device: "firewall-01"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a schedule's time ranges
  cdot65.scm.schedule:
    name: "business-hours"
    schedule_type:
      recurring:
        daily:
          - "09:00-18:00"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a schedule by name
  cdot65.scm.schedule:
    name: "business-hours"
    folder: "Security-Policies"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a schedule by ID
  cdot65.scm.schedule:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
schedule:
    description: Information about the schedule object that was managed
    returned: on success
    type: dict
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


def validate_schedule_type(schedule_type):
    """Validate the schedule_type structure.

    Args:
        schedule_type: The schedule_type dictionary to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(schedule_type, dict):
        return False, "schedule_type must be a dictionary"

    # Check that exactly one of recurring or non_recurring is provided
    has_recurring = "recurring" in schedule_type and schedule_type["recurring"] is not None
    has_non_recurring = "non_recurring" in schedule_type and schedule_type["non_recurring"] is not None

    if has_recurring and has_non_recurring:
        return False, "schedule_type must contain exactly one of 'recurring' or 'non_recurring'"
    if not has_recurring and not has_non_recurring:
        return False, "schedule_type must contain either 'recurring' or 'non_recurring'"

    # Validate recurring structure
    if has_recurring:
        recurring = schedule_type["recurring"]
        if not isinstance(recurring, dict):
            return False, "schedule_type.recurring must be a dictionary"

        has_weekly = "weekly" in recurring and recurring["weekly"] is not None
        has_daily = "daily" in recurring and recurring["daily"] is not None

        if has_weekly and has_daily:
            return False, "recurring schedule must contain exactly one of 'weekly' or 'daily'"
        if not has_weekly and not has_daily:
            return False, "recurring schedule must contain either 'weekly' or 'daily'"

        # Validate weekly structure
        if has_weekly:
            weekly = recurring["weekly"]
            if not isinstance(weekly, dict):
                return False, "schedule_type.recurring.weekly must be a dictionary"

            valid_days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
            for day in weekly:
                if day not in valid_days:
                    return False, f"Invalid day '{day}' in weekly schedule. Must be one of {valid_days}"
                if not isinstance(weekly[day], list):
                    return False, f"weekly.{day} must be a list of time ranges"

        # Validate daily structure
        if has_daily:
            daily = recurring["daily"]
            if not isinstance(daily, list):
                return False, "schedule_type.recurring.daily must be a list of time ranges"
            if len(daily) == 0:
                return False, "schedule_type.recurring.daily must contain at least one time range"

    # Validate non_recurring structure
    if has_non_recurring:
        non_recurring = schedule_type["non_recurring"]
        if not isinstance(non_recurring, list):
            return False, "schedule_type.non_recurring must be a list of datetime ranges"
        if len(non_recurring) == 0:
            return False, "schedule_type.non_recurring must contain at least one datetime range"

    return True, None


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        schedule_type=dict(type="dict", required=False),
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
            ["state", "present", ["name", "schedule_type"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Custom validation for schedule_type structure
    if params.get("state") == "present":
        if not params.get("schedule_type"):
            module.fail_json(msg="schedule_type is required when state=present")

        is_valid, error_msg = validate_schedule_type(params.get("schedule_type"))
        if not is_valid:
            module.fail_json(msg=f"Invalid schedule_type: {error_msg}")

        # Validate that container is provided
        if not any(params.get(container) for container in ["folder", "snippet", "device"]):
            module.fail_json(msg="When state=present, one of the following is required: folder, snippet, device")

    # Initialize results
    result = {"changed": False, "schedule": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize schedule_exists boolean
        schedule_exists = False
        schedule_obj = None

        # Fetch schedule by name
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

                # For any container type, fetch the schedule object
                if container_type and container_name:
                    schedule_obj = client.schedule.fetch(name=params.get("name"), **{container_type: container_name})
                    if schedule_obj:
                        schedule_exists = True
            except ObjectNotPresentError:
                schedule_exists = False
                schedule_obj = None

        # Create or update or delete a schedule
        if params.get("state") == "present":
            if schedule_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Compare schedule_type
                if params.get("schedule_type"):
                    current_schedule_type = schedule_obj.schedule_type.model_dump(exclude_unset=True)
                    new_schedule_type = params.get("schedule_type")

                    # Deep comparison of schedule_type
                    if json.dumps(current_schedule_type, sort_keys=True) != json.dumps(new_schedule_type, sort_keys=True):
                        update_fields["schedule_type"] = new_schedule_type

                # Compare container fields
                for container in ["folder", "snippet", "device"]:
                    if params.get(container) is not None and getattr(schedule_obj, container, None) != params.get(container):
                        update_fields[container] = params.get(container)

                # Update the schedule if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = schedule_obj.model_copy(update=update_fields)
                        updated = client.schedule.update(update_model)
                        result["schedule"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["schedule"] = json.loads(schedule_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["schedule"] = json.loads(schedule_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new schedule object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "schedule_type",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a schedule object
                if not module.check_mode:
                    # Create a schedule object
                    created = client.schedule.create(create_payload)

                    # Return the created schedule object
                    result["schedule"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created schedule object (minimal info)
                    simulated = ScheduleCreateModel(**create_payload)
                    result["schedule"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a schedule object
        elif params.get("state") == "absent":
            if schedule_exists:
                if not module.check_mode:
                    client.schedule.delete(schedule_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["schedule"] = json.loads(schedule_obj.model_dump_json(exclude_unset=True))
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
