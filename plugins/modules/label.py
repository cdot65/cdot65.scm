#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: label
short_description: Manage labels in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete labels in Strata Cloud Manager using pan-scm-sdk.
    - Supports all label attributes and robust idempotency.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the label (max 63 chars).
            - Required for both state=present and state=absent.
        type: str
        required: false
    description:
        description:
            - Description of the label.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the label (UUID).
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
            - Desired state of the label.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
"""

EXAMPLES = r"""
- name: Create a label
  cdot65.scm.label:
    name: "environment"
    description: "Environment classification label"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Delete a label
  cdot65.scm.label:
    name: "environment"
    state: absent
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
label:
    description: Information about the label that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The label ID
            type: str
            returned: always
            sample: "123e4567-e89b-12d3-a456-426655440000"
        name:
            description: The label name
            type: str
            returned: always
            sample: "environment"
        description:
            description: The label description
            type: str
            returned: always
            sample: "Environment classification label"
changed:
    description: Whether any change was made.
    returned: always
    type: bool
    sample: true
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        id=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )

    # Initialize module
    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ["state", "present", ["name"]],
            ["state", "absent", ["name"]],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "label": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize label_exists boolean
        label_exists = False
        label_obj = None

        # Fetch label by name
        if params.get("name"):
            try:
                label_obj = client.label.fetch(params.get("name"))
                if label_obj:
                    label_exists = True
            except ObjectNotPresentError:
                label_exists = False
                label_obj = None

        if params.get("state") == "present":
            if label_exists:
                # Only update fields that differ
                update_fields = {
                    k: params[k]
                    for k in ["description"]
                    if params.get(k) is not None and getattr(label_obj, k, None) != params[k]
                }

                # Update label
                if update_fields:
                    if not module.check_mode:
                        update_model = label_obj.model_copy(update=update_fields)
                        updated = client.label.update(update_model)
                        result["label"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    result["changed"] = True

                # Return existing label
                else:
                    result["label"] = json.loads(label_obj.model_dump_json(exclude_unset=True))
            else:
                # Create a new label
                if not module.check_mode:
                    create_payload = {
                        k: params[k]
                        for k in [
                            "name",
                            "description",
                        ]
                        if params.get(k) is not None
                    }

                    # Create label
                    created = client.label.create(create_payload)

                    # Return created label
                    result["label"] = json.loads(created.model_dump_json(exclude_unset=True))

                # Indicate change
                result["changed"] = True

        # Delete label
        elif params.get("state") == "absent":

            if label_exists:
                if not module.check_mode:
                    client.label.delete(label_obj.id)

                # Indicate change
                result["changed"] = True
                result["label"] = json.loads(label_obj.model_dump_json(exclude_unset=True))

        # Return unchanged
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
