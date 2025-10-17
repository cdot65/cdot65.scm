#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

DOCUMENTATION = r"""
---
module: tag_info
short_description: Get information about tags in Strata Cloud Manager (SCM)
description:
    - This module retrieves information about tags in Strata Cloud Manager.
    - It can be used to get details about a specific tag by ID or name, or to list all tags.
    - Supports filtering by container (folder, snippet, or device) and color.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    id:
        description:
            - The ID of the tag to retrieve.
            - If specified, the module will return information about this specific tag.
            - Mutually exclusive with I(name).
        type: str
        required: false
    name:
        description:
            - The name of the tag to retrieve.
            - If specified, the module will search for tags with this name.
            - Mutually exclusive with I(id).
            - Requires one of I(folder), I(snippet), or I(device) to be specified.
        type: str
        required: false
    folder:
        description:
            - The folder in which to search for tags.
            - Required when listing all tags or fetching by name.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which to search for tags.
            - Required when listing all tags or fetching by name.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which to search for tags.
            - Required when listing all tags or fetching by name.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    colors:
        description:
            - Filter tags by color.
            - Must be a list of valid color names.
            - Only used when listing tags (not when fetching by ID or name).
        type: list
        elements: str
        required: false
    exact_match:
        description:
            - If True, only return objects whose container exactly matches the provided container parameter.
            - Only applicable when listing tags.
        type: bool
        default: false
        required: false
    exclude_folders:
        description:
            - List of folder names to exclude from results.
            - Only applicable when listing tags.
        type: list
        elements: str
        required: false
    exclude_snippets:
        description:
            - List of snippet values to exclude from results.
            - Only applicable when listing tags.
        type: list
        elements: str
        required: false
    exclude_devices:
        description:
            - List of device values to exclude from results.
            - Only applicable when listing tags.
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
    - For authentication, you can set the C(SCM_ACCESS_TOKEN) environment variable instead of providing it as a module option.
    - When fetching by name or listing tags, exactly one container type (folder, snippet, or device) must be provided.
    - Available colors include Azure Blue, Black, Blue, Blue Gray, Blue Violet, Brown, Burnt Sienna,
      Cerulean Blue, Chestnut, Cobalt Blue, Copper, Cyan, Forest Green, Gold, Gray, Green, Lavender,
      Light Gray, Light Green, Lime, Magenta, Mahogany, Maroon, Medium Blue, Medium Rose, Medium Violet,
      Midnight Blue, Olive, Orange, Orchid, Peach, Purple, Red, Red Violet, Red-Orange, Salmon, Thistle,
      Turquoise Blue, Violet Blue, Yellow, and Yellow-Orange.
"""

EXAMPLES = r"""
- name: Get all tags in a folder
  cdot65.scm.tag_info:
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: all_tags

- name: Get a specific tag by ID
  cdot65.scm.tag_info:
    id: "123e4567-e89b-12d3-a456-426655440000"
    scm_access_token: "{{ scm_access_token }}"
  register: tag_details

- name: Get a specific tag by name
  cdot65.scm.tag_info:
    name: "production"
    folder: "Texas"
    scm_access_token: "{{ scm_access_token }}"
  register: named_tag

- name: Get tags filtered by color
  cdot65.scm.tag_info:
    folder: "Texas"
    colors:
      - "Red"
      - "Yellow"
    scm_access_token: "{{ scm_access_token }}"
  register: colored_tags

- name: Get tags in snippet with exact match
  cdot65.scm.tag_info:
    snippet: "Security Tags"
    exact_match: true
    scm_access_token: "{{ scm_access_token }}"
  register: snippet_tags

- name: Get tags excluding certain folders
  cdot65.scm.tag_info:
    folder: "Texas"
    exclude_folders:
      - "Archive"
      - "Old"
    scm_access_token: "{{ scm_access_token }}"
  register: filtered_tags
"""

RETURN = r"""
tags:
    description: List of tag resources
    returned: always
    type: list
    elements: dict
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
"""


def main():
    # Define the module argument specification
    module_args = dict(
        name=dict(type="str", required=False),
        id=dict(type="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        colors=dict(type="list", elements="str", required=False),
        exact_match=dict(type="bool", default=False, required=False),
        exclude_folders=dict(type="list", elements="str", required=False),
        exclude_snippets=dict(type="list", elements="str", required=False),
        exclude_devices=dict(type="list", elements="str", required=False),
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
        required_one_of=[
            ["id", "name", "folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    result = {"tags": []}

    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Get tag by ID if specified
        if params.get("id"):
            try:
                tag_obj = client.tag.get(params.get("id"))
                if tag_obj:
                    result["tags"] = [json.loads(tag_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve tag info: {e}")
        # Fetch a tag by name
        elif params.get("name"):
            # Ensure container is provided for fetch
            container_params = {}
            if params.get("folder"):
                container_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                container_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                container_params["device"] = params.get("device")
            else:
                module.fail_json(msg="One of 'folder', 'snippet', or 'device' must be provided when fetching by name")

            try:
                tag_obj = client.tag.fetch(name=params.get("name"), **container_params)
                if tag_obj:
                    result["tags"] = [json.loads(tag_obj.model_dump_json(exclude_unset=True))]
            except ObjectNotPresentError as e:
                module.fail_json(msg=f"Failed to retrieve tag info: {e}")

        else:
            # List tags with filters
            # Build container parameters
            container_params = {}
            if params.get("folder"):
                container_params["folder"] = params.get("folder")
            elif params.get("snippet"):
                container_params["snippet"] = params.get("snippet")
            elif params.get("device"):
                container_params["device"] = params.get("device")
            else:
                module.fail_json(msg="One of 'folder', 'snippet', or 'device' must be provided when listing tags")

            # Build filter parameters
            filter_params = container_params.copy()

            # Add optional filters
            if params.get("colors"):
                filter_params["colors"] = params.get("colors")
            if params.get("exact_match"):
                filter_params["exact_match"] = params.get("exact_match")
            if params.get("exclude_folders"):
                filter_params["exclude_folders"] = params.get("exclude_folders")
            if params.get("exclude_snippets"):
                filter_params["exclude_snippets"] = params.get("exclude_snippets")
            if params.get("exclude_devices"):
                filter_params["exclude_devices"] = params.get("exclude_devices")

            # List tags with filters
            tags = client.tag.list(**filter_params)

            tag_dicts = [json.loads(tag.model_dump_json(exclude_unset=True)) for tag in tags]
            result["tags"] = tag_dicts
        module.exit_json(**result)
    except (InvalidObjectError, APIError) as e:
        module.fail_json(
            msg=f"API error: {e}",
            error_code=getattr(e, "error_code", None),
            details=getattr(e, "details", None),
        )
    except Exception as e:
        module.fail_json(msg=f"Failed to retrieve tag info: {e}")


if __name__ == "__main__":
    main()
