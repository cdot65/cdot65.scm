#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.setup.snippet import SnippetUpdateModel

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
        state=dict(type="str", default="present", choices=["present", "absent"]),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    result = {"changed": False, "msg": ""}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    params = module.params
    state = params["state"]
    snippet_id = params.get("id")
    name = params.get("name")
    scm_access_token = params["scm_access_token"]

    # Initialize SDK client
    try:
        client = ScmClient(access_token=scm_access_token)
        snippets = client.snippet
    except Exception as e:
        result["msg"] = f"Failed to initialize SCM client: {e}"
        module.fail_json(**result)

    try:
        if state == "present":
            # Try to fetch existing
            existing = None
            if snippet_id:
                try:
                    existing = snippets.get(snippet_id)
                except ObjectNotPresentError:
                    existing = None
            elif name:
                existing = snippets.fetch(name)
            # Prepare data
            snippet_data = dict(
                name=name,
                description=params.get("description"),
                labels=params.get("labels"),
                enable_prefix=params.get("enable_prefix"),
                type=params.get("snippet_type"),  # API expects 'type' even though we use 'snippet_type' in the module
                display_name=params.get("display_name"),
            )
            # Remove unset keys and keys with value None
            snippet_data = {k: v for k, v in snippet_data.items() if v is not None}
            # Remove invalid/empty string fields
            snippet_data = {k: v for k, v in snippet_data.items() if v != ""}
            if not existing:
                if module.check_mode:
                    result["changed"] = True
                    result["msg"] = "Would create snippet."
                    module.exit_json(**result)
                created = snippets.create(snippet_data)
                result["changed"] = True
                result["snippet"] = json.loads(created.model_dump_json())
                result["msg"] = "Snippet created."
            else:
                # Compare for idempotency
                update_needed = False
                for k, v in snippet_data.items():
                    if getattr(existing, k, None) != v:
                        update_needed = True
                        break
                if update_needed:
                    if module.check_mode:
                        result["changed"] = True
                        result["msg"] = "Would update snippet."
                        module.exit_json(**result)
                    update_model = SnippetUpdateModel(id=existing.id, **snippet_data)
                    updated = snippets.update(update_model)
                    result["changed"] = True
                    result["snippet"] = json.loads(updated.model_dump_json())
                    result["msg"] = "Snippet updated."
                else:
                    result["snippet"] = json.loads(existing.model_dump_json())
                    result["msg"] = "Snippet already present and up to date."
        elif state == "absent":
            # Try to fetch existing
            existing = None
            if snippet_id:
                try:
                    existing = snippets.get(snippet_id)
                except ObjectNotPresentError:
                    existing = None
            elif name:
                existing = snippets.fetch(name)
            if existing:
                if module.check_mode:
                    result["changed"] = True
                    result["msg"] = "Would delete snippet."
                    module.exit_json(**result)
                snippets.delete(existing.id)
                result["changed"] = True
                result["msg"] = "Snippet deleted."
            else:
                result["msg"] = "Snippet already absent."
    except InvalidObjectError as e:
        result["msg"] = f"Invalid object data: {e}"
        module.fail_json(**result)
    except APIError as e:
        result["msg"] = f"API error: {e}"
        module.fail_json(**result)
    except Exception as e:
        result["msg"] = f"Error: {e}"
        module.fail_json(**result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
