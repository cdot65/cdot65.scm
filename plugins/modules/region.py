#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from ansible.module_utils.basic import AnsibleModule
from scm.client import ScmClient
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError
from scm.models.objects import RegionUpdateModel

DOCUMENTATION = r"""
---
module: region
short_description: Manage region objects in Strata Cloud Manager (SCM)
description:
    - Create, update, or delete region objects in Strata Cloud Manager using pan-scm-sdk.
    - Supports all region attributes including geographic location and network addresses.
version_added: "0.1.0"
author:
    - "Calvin Remsburg (@cdot65)"
options:
    name:
        description:
            - Name of the region.
            - Required for all operations.
        type: str
        required: true
    geographic_location:
        description:
            - Geographic location with latitude and longitude coordinates.
            - Requires both latitude and longitude to be provided.
        type: dict
        required: false
        suboptions:
            latitude:
                description:
                    - Latitude coordinate (-90 to 90).
                type: float
                required: true
            longitude:
                description:
                    - Longitude coordinate (-180 to 180).
                type: float
                required: true
    addresses:
        description:
            - List of network addresses associated with the region.
            - Can include IPv4/IPv6 addresses and subnets.
        type: list
        elements: str
        required: false
    folder:
        description:
            - Name of the folder containing the region object.
            - Mutually exclusive with snippet and device.
        type: str
        required: false
    snippet:
        description:
            - Name of the snippet containing the region object.
            - Mutually exclusive with folder and device.
        type: str
        required: false
    device:
        description:
            - Name of the device containing the region object.
            - Mutually exclusive with folder and snippet.
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
            - Desired state of the region object.
        type: str
        choices: ['present', 'absent']
        default: present
notes:
    - Check mode is supported.
    - All operations are idempotent.
    - Exactly one of folder, snippet, or device must be specified.
    - Uses pan-scm-sdk via unified client and bearer token from the auth role.
    - Although the SDK supports description and tag fields, they are not sent to the API.
"""

EXAMPLES = r"""
- name: Create a region with geographic location
  cdot65.scm.region:
    name: "us-west-region"
    folder: "Global"
    geographic_location:
      latitude: 37.7749
      longitude: -122.4194
    addresses:
      - "10.0.0.0/8"
      - "192.168.1.0/24"
    state: present

- name: Update a region's network addresses
  cdot65.scm.region:
    name: "us-west-region"
    folder: "Global"
    addresses:
      - "10.0.0.0/8"
      - "192.168.1.0/24"
      - "172.16.0.0/16"
    state: present

- name: Create a region in a snippet
  cdot65.scm.region:
    name: "europe-region"
    snippet: "EU Configs"
    geographic_location:
      latitude: 48.8566
      longitude: 2.3522
    state: present

- name: Delete a region
  cdot65.scm.region:
    name: "old-region"
    folder: "Global"
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
            description: The region name
            type: str
            returned: always
            sample: "us-west-region"
        geo_location:
            description: The geographic location of the region
            type: dict
            returned: when configured
            sample:
                latitude: 37.7749
                longitude: -122.4194
        address:
            description: List of network addresses
            type: list
            returned: when configured
            sample: ["10.0.0.0/8", "192.168.1.0/24"]
        folder:
            description: The name of the folder containing the region
            type: str
            returned: when applicable
            sample: "Global"
        snippet:
            description: The name of the snippet containing the region
            type: str
            returned: when applicable
            sample: "EU Configs"
        device:
            description: The name of the device containing the region
            type: str
            returned: when applicable
            sample: "fw-01"
"""


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        geographic_location=dict(
            type="dict",
            required=False,
            options=dict(
                latitude=dict(type="float", required=True),
                longitude=dict(type="float", required=True),
            ),
        ),
        addresses=dict(type="list", elements="str", required=False),
        folder=dict(type="str", required=False),
        snippet=dict(type="str", required=False),
        device=dict(type="str", required=False),
        scm_access_token=dict(type="str", required=True, no_log=True),
        api_url=dict(type="str", required=False),
        state=dict(type="str", required=False, choices=["present", "absent"], default="present"),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["folder", "snippet", "device"]],
        required_one_of=[["folder", "snippet", "device"]],
    )

    try:
        # Initialize SCM client
        client = ScmClient(access_token=module.params.get("scm_access_token"))

        state = module.params["state"]
        name = module.params["name"]
        existing_object = None

        # Determine the container
        container_parameters = {
            k: v
            for k, v in {
                "folder": module.params.get("folder"),
                "snippet": module.params.get("snippet"),
                "device": module.params.get("device"),
            }.items()
            if v is not None
        }

        # Try to fetch existing object by name
        try:
            existing_object = client.region.fetch(name=name, **container_parameters)
        except ObjectNotPresentError:
            existing_object = None
        except APIError as e:
            if e.http_status_code == 404:
                existing_object = None
            else:
                raise

        if state == "present":
            if existing_object is None:
                # Create new region
                if module.check_mode:
                    module.exit_json(changed=True, msg="Region would be created")

                payload = {
                    "name": name,
                    **container_parameters,
                }
                if module.params.get("geographic_location"):
                    payload["geo_location"] = module.params["geographic_location"]
                if module.params.get("addresses"):
                    payload["address"] = module.params["addresses"]

                # Create using direct SDK model
                new_object = client.region.create(data=payload)
                result = json.loads(new_object.model_dump_json(exclude_unset=True))
                module.exit_json(changed=True, region=result)
            else:
                # Update existing region
                # Check if any changes are needed
                changes_needed = False
                update_payload = {"id": existing_object.id, "name": name}

                # Check geo_location
                existing_geo_location = None
                if existing_object.geo_location:
                    existing_geo_location = {
                        "latitude": existing_object.geo_location.latitude,
                        "longitude": existing_object.geo_location.longitude,
                    }
                if module.params.get("geographic_location") != existing_geo_location:
                    changes_needed = True
                    update_payload["geo_location"] = module.params.get("geographic_location")

                # Check addresses
                existing_addresses = existing_object.address or []
                param_addresses = module.params.get("addresses") or []
                if sorted(existing_addresses) != sorted(param_addresses):
                    changes_needed = True
                    update_payload["address"] = param_addresses

                if not changes_needed:
                    result = json.loads(existing_object.model_dump_json(exclude_unset=True))
                    module.exit_json(changed=False, region=result)

                if module.check_mode:
                    module.exit_json(changed=True, msg="Region would be updated")

                # Update the region
                update_model = RegionUpdateModel(**update_payload)
                updated_object = client.region.update(update_model)
                result = json.loads(updated_object.model_dump_json(exclude_unset=True))
                module.exit_json(changed=True, region=result)

        elif state == "absent":
            if existing_object is None:
                module.exit_json(changed=False, msg="Region not found, nothing to delete")

            if module.check_mode:
                module.exit_json(changed=True, msg="Region would be deleted")

            # Delete the region
            client.region.delete(object_id=str(existing_object.id))
            module.exit_json(changed=True, msg=f"Deleted region {name}")

    except InvalidObjectError as e:
        module.fail_json(msg=f"Invalid object: {str(e)}")
    except APIError as e:
        module.fail_json(msg=f"API error: {str(e)}")
    except Exception as e:  # noqa
        module.fail_json(msg=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
