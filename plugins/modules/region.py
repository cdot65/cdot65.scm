#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import RegionCreateModel

DOCUMENTATION = r"""
---
module: region
short_description: Manage region objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete region objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all region attributes including geographic location and addresses.
    - Region objects must be associated with exactly one container (folder, snippet, or device).
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the region object.
            - Required for state=present and for absent if id is not provided.
            - Maximum length is 64 characters.
            - Must match pattern '^[\w .:/\-]+$'.
        type: str
        required: false
    geo_location:
        description:
            - Geographic location of the region.
            - Contains latitude and longitude coordinates.
        type: dict
        required: false
        suboptions:
            latitude:
                description:
                    - Latitudinal position of the region.
                    - Valid range is -90 to 90.
                type: float
                required: true
            longitude:
                description:
                    - Longitudinal position of the region.
                    - Valid range is -180 to 180.
                type: float
                required: true
    address:
        description:
            - List of addresses associated with the region.
            - Each address is a string reference.
        type: list
        elements: str
        required: false
    folder:
        description:
            - The folder in which the region object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(snippet) and I(device).
        type: str
        required: false
    snippet:
        description:
            - The snippet in which the region object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(device).
        type: str
        required: false
    device:
        description:
            - The device in which the region object is defined.
            - Exactly one of folder, snippet, or device must be provided for state=present.
            - Mutually exclusive with I(folder) and I(snippet).
        type: str
        required: false
    id:
        description:
            - Unique identifier for the region object (UUID).
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
            - Desired state of the region object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Region objects must be associated with exactly one container (folder, snippet, or device).
    - The name field has a maximum length of 64 characters and must match pattern '^[\w .:/\-]+$'.
    - Geographic location coordinates must be within valid ranges (latitude -90 to 90, longitude -180 to 180).
    - Although the SDK supports description and tag fields, these are NOT sent to the API and should not be used.
"""

EXAMPLES = r"""
- name: Create a folder-based region object
  cdot65.scm.region:
    name: "North-America-East"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a region with geographic location
  cdot65.scm.region:
    name: "NYC-Region"
    geo_location:
      latitude: 40.7128
      longitude: -74.0060
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a region with addresses
  cdot65.scm.region:
    name: "Europe-West"
    address:
      - "london-office"
      - "paris-office"
      - "berlin-office"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Create a comprehensive region object
  cdot65.scm.region:
    name: "Asia-Pacific"
    geo_location:
      latitude: 1.3521
      longitude: 103.8198
    address:
      - "singapore-dc"
      - "tokyo-dc"
      - "sydney-dc"
    snippet: "global-regions"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Update a region's geographic location
  cdot65.scm.region:
    name: "NYC-Region"
    geo_location:
      latitude: 40.7580
      longitude: -73.9855
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: present

- name: Delete a region object by name
  cdot65.scm.region:
    name: "NYC-Region"
    folder: "Network-Objects"
    scm_access_token: "{{ scm_access_token }}"
    state: absent

- name: Delete a region object by ID
  cdot65.scm.region:
    id: "12345678-1234-1234-1234-123456789012"
    scm_access_token: "{{ scm_access_token }}"
    state: absent
"""

RETURN = r"""
region:
    description: Information about the region object that was managed
    returned: on success
    type: dict
    contains:
        id:
            description: The region object ID
            type: str
            returned: always
            sample: "12345678-1234-1234-1234-123456789012"
        name:
            description: The region object name
            type: str
            returned: always
            sample: "North-America-East"
        geo_location:
            description: Geographic location of the region
            type: dict
            returned: when applicable
            contains:
                latitude:
                    description: Latitudinal position
                    type: float
                    sample: 40.7128
                longitude:
                    description: Longitudinal position
                    type: float
                    sample: -74.0060
        address:
            description: List of addresses associated with the region
            type: list
            returned: when applicable
            sample: ["london-office", "paris-office"]
        folder:
            description: The folder containing the region object
            type: str
            returned: when applicable
            sample: "Network-Objects"
        snippet:
            description: The snippet containing the region object
            type: str
            returned: when applicable
            sample: "global-regions"
        device:
            description: The device containing the region object
            type: str
            returned: when applicable
            sample: "firewall-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=False),
        geo_location=dict(
            type="dict",
            required=False,
            options=dict(
                latitude=dict(type="float", required=True),
                longitude=dict(type="float", required=True),
            ),
        ),
        address=dict(type="list", elements="str", required=False),
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

    # Custom validation for name length and pattern
    if params.get("name"):
        import re

        name = params.get("name")
        if len(name) > 64:
            module.fail_json(msg=f"The 'name' field must be 64 characters or less. Current length: {len(name)}")
        if not re.match(r"^[\w .:/\-]+$", name):
            module.fail_json(msg=f"The 'name' field must match pattern '^[\\w .:/\\-]+$'. Got: {name}")

    # Custom validation for geo_location coordinates
    if params.get("geo_location"):
        geo = params.get("geo_location")
        lat = geo.get("latitude")
        lon = geo.get("longitude")

        if lat is not None and (lat < -90 or lat > 90):
            module.fail_json(msg=f"Latitude must be between -90 and 90. Got: {lat}")

        if lon is not None and (lon < -180 or lon > 180):
            module.fail_json(msg=f"Longitude must be between -180 and 180. Got: {lon}")

    # Initialize results
    result = {"changed": False, "region": None}

    # Perform operations
    try:
        # Initialize SCM client
        client = ScmClient(access_token=params.get("scm_access_token"))

        # Initialize region_exists boolean
        region_exists = False
        region_obj = None

        # Fetch region by name
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

                # For any container type, fetch the region object
                if container_type and container_name:
                    region_obj = client.region.fetch(name=params.get("name"), **{container_type: container_name})
                    if region_obj:
                        region_exists = True
            except ObjectNotPresentError:
                region_exists = False
                region_obj = None

        # Create or update or delete a region
        if params.get("state") == "present":
            if region_exists:
                # Determine which fields differ and need to be updated
                update_fields = {}

                # Check simple fields
                for field in ["geo_location", "address", "folder", "snippet", "device"]:
                    if params[field] is not None:
                        current_value = getattr(region_obj, field, None)

                        # Special handling for geo_location dict comparison
                        if field == "geo_location" and current_value is not None:
                            # Convert GeoLocation model to dict for comparison
                            current_geo_dict = {
                                "latitude": current_value.latitude,
                                "longitude": current_value.longitude,
                            }
                            if current_geo_dict != params[field]:
                                update_fields[field] = params[field]
                        elif current_value != params[field]:
                            update_fields[field] = params[field]

                # Update the region if needed
                if update_fields:
                    if not module.check_mode:
                        update_model = region_obj.model_copy(update=update_fields)
                        updated = client.region.update(update_model)
                        result["region"] = json.loads(updated.model_dump_json(exclude_unset=True))
                    else:
                        result["region"] = json.loads(region_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = True
                    module.exit_json(**result)
                else:
                    # No update needed
                    result["region"] = json.loads(region_obj.model_dump_json(exclude_unset=True))
                    result["changed"] = False
                    module.exit_json(**result)

            else:
                # Create payload for new region object
                create_payload = {
                    k: params[k]
                    for k in [
                        "name",
                        "geo_location",
                        "address",
                        "folder",
                        "snippet",
                        "device",
                    ]
                    if params.get(k) is not None
                }

                # Create a region object
                if not module.check_mode:
                    # Create a region object
                    created = client.region.create(create_payload)

                    # Return the created region object
                    result["region"] = json.loads(created.model_dump_json(exclude_unset=True))
                else:
                    # Simulate a created region object (minimal info)
                    simulated = RegionCreateModel(**create_payload)
                    result["region"] = simulated.model_dump(exclude_unset=True)

                # Mark as changed
                result["changed"] = True

                # Exit
                module.exit_json(**result)

        # Delete a region object
        elif params.get("state") == "absent":
            if region_exists:
                if not module.check_mode:
                    client.region.delete(region_obj.id)

                # Mark as changed
                result["changed"] = True

                # Exit
                result["region"] = json.loads(region_obj.model_dump_json(exclude_unset=True))
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
