#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import TagCreateModel

DOCUMENTATION = r"""
---
module: tag
short_description: Manage tags in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete tags in Strata Cloud Manager using pan-scm-sdk.
    - Supports all tag attributes including color and comments.
    - Provides robust idempotency and container validation.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the tag (max 127 chars).
            - Required for both state=present and state=absent.
            - Pattern must match C(^[a-zA-Z0-9_ \.-\[\]\-\&\(\)]+$).
        type: str
        required: false
    color:
        description:
            - Color associated with the tag.
            - Must be one of the valid color names from the Colors enumeration.
            - Examples include Azure Blue, Black, Blue, Cyan, Green, Magenta, Orange, Purple, Red, Yellow.
            - Color names are case-insensitive and normalized automatically.
        type: str
        required: false
    comments:
        description:
            - Comments about the tag (max 1023 chars).
        type: str
        required: false
    folder:
        description:
            - The folder in which the resource is defined.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the resource is defined.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the resource is defined.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the tag (UUID).
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
            - Desired state of the tag.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided for state=present.
    - Available colors include Azure Blue, Black, Blue, Blue Gray, Blue Violet, Brown, Burnt Sienna,
      Cerulean Blue, Chestnut, Cobalt Blue, Copper, Cyan, Forest Green, Gold, Gray, Green, Lavender,
      Light Gray, Light Green, Lime, Magenta, Mahogany, Maroon, Medium Blue, Medium Rose, Medium Violet,
      Midnight Blue, Olive, Orange, Orchid, Peach, Purple, Red, Red Violet, Red-Orange, Salmon, Thistle,
      Turquoise Blue, Violet Blue, Yellow, and Yellow-Orange.
"""

EXAMPLES = r"""
- name: Create a tag with color
  cdot65.scm.tag:
    name: "production"
    color: "Red"
    comments: "Production environment tag"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Create a tag without color
  cdot65.scm.tag:
    name: "development"
    comments: "Development environment tag"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Update tag color
  cdot65.scm.tag:
    name: "staging"
    color: "Yellow"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Create tag in snippet
  cdot65.scm.tag:
    name: "critical"
    color: "Magenta"
    comments: "Critical systems"
    snippet: "Security Tags"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Delete a tag
  cdot65.scm.tag:
    name: "obsolete"
    folder: "Texas"
    state: absent
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
tag:
    description: Information about the tag that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The tag ID
            type: str
            returned: always
            sample: "123e4567-e89b-12d3-a456-426655440000"
        name:
            description: The tag name
            type: str
            returned: always
            sample: "production"
        color:
            description: The tag color
            type: str
            returned: when specified
            sample: "Red"
        comments:
            description: The tag comments
            type: str
            returned: when specified
            sample: "Production environment tag"
        folder:
            description: The folder containing the tag
            type: str
            returned: when applicable
            sample: "Texas"
        snippet:
            description: The snippet containing the tag
            type: str
            returned: when applicable
            sample: "Security Tags"
        device:
            description: The device containing the tag
            type: str
            returned: when applicable
            sample: "My Device"
changed:
    description: Whether any change was made.
    returned: always
    type: bool
    sample: true
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        color=dict(type="str", required=False),
        comments=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
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
        required_one_of=[
            ["folder", "snippet", "device"],
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
        if len(name) > 127:
            module.fail_json(msg=f"Parameter 'name' exceeds maximum length of 127 characters (got {len(name)})")
        # Validate name pattern to match SDK requirements
        import re

        if not re.match(r"^[a-zA-Z0-9_ \.-\[\]\-\&\(\)]+$", name):
            module.fail_json(
                msg="Parameter 'name' contains invalid characters. Must match pattern: ^[a-zA-Z0-9_ \\.-\\[\\]\\-\\&\\(\\)]+$"
            )

    # Initialize results
    result = {"changed": False, "tag": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize tag_exists boolean
        tag_exists = False
        tag_obj = None

        # Determine container for fetch operations
        container_params = {}
        if params.get("folder"):
            container_params["folder"] = params.get("folder")
        elif params.get("snippet"):
            container_params["snippet"] = params.get("snippet")
        elif params.get("device"):
            container_params["device"] = params.get("device")

        # Fetch tag by name
        if params.get("name"):
            try:
                tag_obj = client.tag.fetch(name=params.get("name"), **container_params)
                if tag_obj:
                    tag_exists = True
            except ObjectNotPresentError:
                tag_exists = False
                tag_obj = None

        # Create or update or delete a tag
        if params.get("state") == "present":
            if tag_exists:
                # Only update fields that differ
                update_fields = {
                    k: params[k]
                    for k in ["color", "comments"]
                    if params.get(k) is not None and getattr(tag_obj, k, None) != params[k]
                }

                # Update a tag if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = tag_obj.model_copy(update=update_fields)
                        updated = client.tag.update(update_model)
                        result["tag"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["tag"] = json.loads(tag_obj.model_copy(update=update_fields).model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)

                else:
                    # No update needed
                    result["tag"] = json.loads(tag_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "color",
                        "comments",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a new tag
                if not module.check_mode:
                    # Create tag
                    created = client.tag.create(create_payload)

                    # Return the created tag
                    result["tag"] = json.loads(created.model_dump_json(exclude_unset=True))

                else:
                    # Simulate created tag (minimal info)
                    simulated = TagCreateModel(**create_payload)
                    result["tag"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a tag
        elif params.get("state") == "absent":
            if tag_exists:
                if not module.check_mode:
                    client.tag.delete(tag_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["tag"] = json.loads(tag_obj.model_dump_json(exclude_unset=True))
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
