#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: snippet_info
short_description: Get information about snippets in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about snippets in Strata Cloud Manager.
    - It can be used to get details about a specific snippet by ID or name, or to list all snippets.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the snippet to retrieve.
            - If specified, the module will return information about this specific snippet.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the snippet to retrieve.
            - If specified, the module will search for snippets with this name.
            - Mutually exclusive with I(id).
        type: str
        required: false
    labels:
        description:
            - List of labels to filter snippets by.
        type: list
        elements: str
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
    - For authentication, you can set the C(SCM_ACCESS_TOKEN) environment variable
      instead of providing it as a module option.
"""

EXAMPLES = r"""
- name: Get all snippets
  snippet_info:
    scm_access_token: "{{ scm_access_token }}"

- name: Get a snippet by name
  snippet_info:
    name: "Security Policy Snippet"
    scm_access_token: "{{ scm_access_token }}"

- name: Get a snippet by ID
  snippet_info:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
snippets:
    description: List of snippets returned by the query.
    returned: always
    type: list
    elements: dict
    sample:
      - id: "12345678-1234-1234-1234-123456789012"
        name: "Security Policy Snippet"
        description: "Common security policy configurations"
        labels: ["security", "policy"]
        enable_prefix: true
        type: "custom"
        display_name: "Security Policy Snippet"
        last_update: "2025-04-10T12:34:56Z"
        created_in: "2025-04-01T09:00:00Z"
        folders: []
        shared_in: "local"
"""


def main():
    module_args = dict(
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
        labels=dict(type="list", elements="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
    )

    # Initialize results
    result = {"snippets": []}

    # Create the module
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[["id", "name"]],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get a snippet by id
        if params.get("id"):
            try:
                snippet_obj = client.snippet.get(params.get("id"))
                if snippet_obj:
                    result["snippets"] = [json.loads(snippet_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve snippet info: {e}")

        # Fetch a snippet by name
        elif params.get("name"):
            try:
                snippet_obj = client.snippet.fetch(name=params.get("name"))
                if snippet_obj:
                    result["snippets"] = [json.loads(snippet_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve snippet info: {e}")

        else:
            # Prepare filter parameters for the SDK
            filter_params = {}
            if params.get("labels"):
                filter_params["labels"] = params.get("labels")

            # List snippets with filters
            snippets = client.snippet.list(**filter_params) if filter_params else client.snippet.list()

            # Convert to a list of dicts
            snippet_dicts = [json.loads(s.model_dump_json(exclude_unset=True)) for s in snippets]

            # Add to results
            result["snippets"] = snippet_dicts

        # Return results
        module.exit_json(**result)

    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve snippet info: {e}")


if __name__ == "__main__":
    main()
