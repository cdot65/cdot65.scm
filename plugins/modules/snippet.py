#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup import SnippetCreateModel

DOCUMENTATION = r"""
---
module: snippet
short_description: Manage snippets in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete snippets in Strata Cloud Manager using pan-scm-sdk.
    - Supports all snippet attributes and robust idempotency.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the snippet.
            - Required for state=present and for absent if id is not provided.
        type: str
        required: false
    description:
        description:
            - Description of the snippet.
        type: str
        required: false
    labels:
        description:
            - List of labels to apply to the snippet.
        type: list
        elements: str
        required: false
    enable_prefix:
        description:
            - Whether to enable prefix for this snippet.
        type: bool
        required: false
    snippet_type:
        description:
            - Snippet type - predefined, custom, or readonly.
        type: str
        required: false
    display_name:
        description:
            - Display name for the snippet.
        type: str
        required: false
    id:
        description:
            - Unique identifier for the snippet (UUID).
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
            - Desired state of the snippet.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
"""

EXAMPLES = r"""
- name: Create a snippet
  cdot65.scm.snippet:
    name: "Security Policy Snippet"
    description: "Common security policy configurations"
    labels:
      - security
      - policy
    enable_prefix: true
    snippet_type: "custom"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Delete a snippet
  cdot65.scm.snippet:
    id: "12345678-1234-1234-1234-123456789012"
    state: absent
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
snippet:
    description: Information about the snippet that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The snippet ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The snippet name
            type: str
            returned: always
            sample: "Security Policy Snippet"
        description:
            description: The snippet description
            type: str
            returned: when applicable
            sample: "Common security policy configurations"
        labels:
            description: Labels applied to the snippet
            type: list
            elements: str
            returned: when applicable
            sample: ["security", "policy"]
        enable_prefix:
            description: Whether prefix is enabled
            type: bool
            returned: when applicable
            sample: true
        snippet_type:
            description: The type of snippet
            type: str
            returned: when applicable
            sample: "custom"
        display_name:
            description: The display name
            type: str
            returned: when applicable
            sample: "Security Policy Snippet"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        labels=dict(type="list", elements="str", required=False),
        enable_prefix=dict(type="bool", required=False),
        snippet_type=dict(type="str", required=False),
        display_name=dict(type="str", required=False),
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
            ["state", "absent", ["name"]],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "snippet": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize snippet_exists boolean
        snippet_exists = False
        snippet_obj = None

        # Fetch snippet by name
        if params.get("name"):
            try:
                snippet_obj = client.snippet.fetch(params.get("name"))
                if snippet_obj:
                    snippet_exists = True
            except ObjectNotPresentError:
                snippet_exists = False
                snippet_obj = None

        # Create or update or delete a folder
        if params.get("state") == "present":
            if snippet_exists:
                # Only update fields that differ
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "labels",
                        "enable_prefix",
                        "snippet_type",
                        "display_name",
                    ]
                    if params.get(k) is not None and getattr(snippet_obj, k, None) != params[k]
                }

                # Map 'snippet_type' to 'type' for SDK/model
                if "snippet_type" in update_fields:
                    update_fields["type"] = update_fields.pop("snippet_type")

                # Update snippet if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = snippet_obj.model_copy(update=update_fields)
                        updated = client.snippet.update(update_model)
                        result["snippet"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["snippet"] = json.loads(
                            snippet_obj.model_copy(update=update_fields).model_dump_json(exclude_unset=True)
                        )
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["snippet"] = json.loads(snippet_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)
            else:
                # Create payload
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "labels",
                        "enable_prefix",
                        "snippet_type",
                        "display_name",
                    ]
                    if params.get(k) is not None
                }

                # Create a new snippet
                if not module.check_mode:
                    # Map 'snippet_type' to 'type' for SDK/model
                    if "snippet_type" in create_payload:
                        create_payload["type"] = create_payload.pop("snippet_type")

                    # Create snippet
                    created = client.snippet.create(create_payload)

                    # Return created snippet
                    result["snippet"] = json.loads(created.model_dump_json(exclude_unset=True))

                else:
                    # Simulate created snippet (minimal info)
                    simulated = SnippetCreateModel(**create_payload)
                    result["snippet"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a snippet
        elif params.get("state") == "absent":
            if snippet_exists:
                if not module.check_mode:
                    client.snippet.delete(snippet_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["snippet"] = json.loads(snippet_obj.model_dump_json(exclude_unset=True))
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
