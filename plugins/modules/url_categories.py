#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.security import URLCategoriesCreateModel

DOCUMENTATION = r"""
---
module: url_categories
short_description: Manage custom URL categories in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete custom URL categories in Strata Cloud Manager using pan-scm-sdk.
    - Supports URL lists and category matching for custom URL filtering.
    - Provides robust idempotency and container validation.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the URL category.
            - Required for both state=present and state=absent.
        type: str
        required: false
    description:
        description:
            - Description of the URL category.
        type: str
        required: false
    list:
        description:
            - List of URLs or category names.
            - For URL List type, provide URLs/domains to match.
            - For Category Match type, provide built-in category names to match.
        type: list
        elements: str
        required: false
    type:
        description:
            - Type of URL category.
            - C(URL List) for custom URL/domain lists.
            - C(Category Match) for matching against built-in categories.
        type: str
        choices: ['URL List', 'Category Match']
        default: 'URL List'
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
            - Unique identifier for the URL category (UUID).
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
            - Desired state of the URL category.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Exactly one container type (folder, snippet, or device) must be provided for state=present.
"""

EXAMPLES = r"""
- name: Create a custom URL category with URL list
  cdot65.scm.url_categories:
    name: "blocked-sites"
    description: "Sites to block"
    type: "URL List"
    list:
      - "*.badsite.com"
      - "malicious.example.com"
      - "phishing-site.org"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Create URL category matching built-in categories
  cdot65.scm.url_categories:
    name: "high-risk-categories"
    description: "High risk content categories"
    type: "Category Match"
    list:
      - "gambling"
      - "adult"
      - "malware"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Create social media URL category
  cdot65.scm.url_categories:
    name: "social-media-custom"
    description: "Custom social media sites"
    type: "URL List"
    list:
      - "*.facebook.com"
      - "*.twitter.com"
      - "*.instagram.com"
      - "*.linkedin.com"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Update URL category list
  cdot65.scm.url_categories:
    name: "blocked-sites"
    description: "Updated blocked sites list"
    type: "URL List"
    list:
      - "*.badsite.com"
      - "malicious.example.com"
      - "phishing-site.org"
      - "new-threat.com"
    folder: "Texas"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Create URL category in snippet
  cdot65.scm.url_categories:
    name: "corporate-allowed"
    description: "Corporate approved sites"
    type: "URL List"
    list:
      - "*.company.com"
      - "*.partner-site.com"
    snippet: "Security-Policy"
    state: present
    scm_access_token: "{{ scm_access_token }}"

- name: Delete a URL category
  cdot65.scm.url_categories:
    name: "obsolete-category"
    folder: "Texas"
    state: absent
    scm_access_token: "{{ scm_access_token }}"
"""

RETURN = r"""
url_category:
    description: Information about the URL category that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The URL category ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The URL category name
            type: str
            returned: always
            sample: "blocked-sites"
        description:
            description: The URL category description
            type: str
            returned: when applicable
            sample: "Sites to block"
        list:
            description: List of URLs or categories
            type: list
            returned: always
            sample: ["*.badsite.com", "malicious.example.com"]
        type:
            description: Type of URL category
            type: str
            returned: always
            sample: "URL List"
        folder:
            description: The folder containing the URL category
            type: str
            returned: when applicable
            sample: "Texas"
        snippet:
            description: The snippet containing the URL category
            type: str
            returned: when applicable
            sample: "Security-Policy"
        device:
            description: The device containing the URL category
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        description=dict(type="str", required=False),
        list=dict(type="list", elements="str", required=False),
        type=dict(type="str", required=False, choices=["URL List", "Category Match"], default="URL List"),
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
            ["state", "present", ["name"]],
            ["state", "absent", ["name", "id"], True],  # At least one of name or id required
        ],
        mutually_exclusive=[
            ["folder", "snippet", "device"],
        ],
        supports_check_mode=True,
    )

    # Get parameters
    params = module.params

    # Initialize results
    result = {"changed": False, "url_category": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize url_category_exists boolean
        url_category_exists = False
        url_category_obj = None

        # Fetch URL category by name
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

                # For any container type, fetch the URL category object
                if container_type and container_name:
                    url_category_obj = client.url_categories.fetch(name=params.get("name"), **{container_type: container_name})
                    if url_category_obj:
                        url_category_exists = True
            except ObjectNotPresentError:
                url_category_exists = False
                url_category_obj = None

        # Create or update or delete a URL category
        if params.get("state") == "present":
            if url_category_exists:
                # Determine which fields differ and need to be updated
                update_fields = {
                    k: params[k]
                    for k in [
                        "description",
                        "list",
                        "type",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params[k] is not None and getattr(url_category_obj, k, None) != params[k]
                }

                # Update the URL category if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = url_category_obj.model_copy(update=update_fields)
                        updated = client.url_categories.update(update_model)
                        result["url_category"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["url_category"] = json.loads(url_category_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["url_category"] = json.loads(url_category_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new URL category object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "description",
                        "list",
                        "type",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a URL category object
                if not module.check_mode:
                    # Create a URL category object
                    created = client.url_categories.create(create_payload)

                    # Return the created URL category object
                    result["url_category"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created URL category object (minimal info)
                    simulated = URLCategoriesCreateModel(**create_payload)
                    result["url_category"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a URL category object
        elif params.get("state") == "absent":
            if url_category_exists:
                if not module.check_mode:
                    client.url_categories.delete(url_category_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["url_category"] = json.loads(url_category_obj.model_dump_json(exclude_unset=True))
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
