#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Strata Cloud Manager API client module utilities."""

import logging

# Import Python libs

HAS_SCM_SDK = False
SCM_SDK_IMPORT_ERROR = None
try:
    from scm.client import ScmClient
    from scm.exceptions import APIError
    from scm.exceptions import AuthenticationError
    from scm.exceptions import BadRequestError
    from scm.exceptions import NotFoundError

    HAS_SCM_SDK = True
except ImportError as e:
    ScmClient = None
    APIError = Exception
    AuthenticationError = Exception
    BadRequestError = Exception
    NotFoundError = Exception
    SCM_SDK_IMPORT_ERROR = e

from ansible.module_utils.basic import missing_required_lib


def get_scm_client_argument_spec():
    """Return common SCM authentication and connection argument spec for modules.

    Returns:
        dict: Standard SCM module argument spec for authentication parameters
    """
    return dict(
        client_id=dict(type="str", required=True, no_log=True),
        client_secret=dict(type="str", required=True, no_log=True),
        tsg_id=dict(type="str", required=True),
        scopes=dict(type="list", elements="str", required=False, default=None),
        log_level=dict(type="str", required=False, default="ERROR"),
    )


def get_scm_client(module):
    """Initialize and return a SCM client using credentials from module parameters or environment variables.

    Args:
        module: Ansible module object

    Returns:
        ScmClient: Initialized SCM client object

    Raises:
        APIError: If SDK is not installed or client cannot be initialized
    """
    if not HAS_SCM_SDK:
        module.fail_json(msg=missing_required_lib("pan-scm-sdk"))
    try:
        return ScmClient(
            client_id=module.params["client_id"],
            client_secret=module.params["client_secret"],
            tsg_id=module.params["tsg_id"],
            log_level=module.params.get("log_level", "ERROR"),
        )
    except (
        APIError,
        AuthenticationError,
        BadRequestError,
        NotFoundError,
    ) as exc:
        module.fail_json(msg=f"Failed to initialize SCM client: {exc}")
    return None


def handle_scm_error(module, error):
    """Handle SCM API errors and translate them to Ansible module failures.

    Args:
        module: Ansible module object
        error: Exception raised by SCM API call

    Returns:
        None
    """
    module.fail_json(msg=str(error))


def get_oauth2_token(
    client_id: str,
    client_secret: str,
    tsg_id: str,
    scopes: list | None = None,
    log_level: str = "ERROR",
) -> dict:
    """Obtain an OAuth2 token from Strata Cloud Manager using the SDK.

    Returns:
        dict: {
            "access_token": str,
            "expires_in": int,
            "token_type": str,
            "scope": str,
            "raw": dict,  # Full token response
        }

    Raises:
        APIError: On authentication failure or SDK errors.
    """
    if not HAS_SCM_SDK:
        raise ImportError(f"pan-scm-sdk is not available: {SCM_SDK_IMPORT_ERROR}")

    # Set logging level for debugging if needed
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.ERROR))

    try:
        from scm.models.auth import AuthRequestModel

        # AuthRequestModel expects 'scope' (string), not 'scopes' (list)
        scope = None
        if scopes is not None:
            # If provided as list, join as space-separated per OAuth spec
            scope = " ".join([str(s) for s in scopes])
        if scope is not None and not isinstance(scope, str):
            scope = str(scope)
        auth_request = AuthRequestModel(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            scope=scope if scope is not None else None,
        )
        from scm.auth import OAuth2Client

        oauth_client = OAuth2Client(auth_request)
        token_data = oauth_client.session.token

        # Ensure we're returning a serializable dict that Ansible can handle
        if not isinstance(token_data, dict):
            # Convert to dict if it's not already
            token_data = dict(token_data)

        return {
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in"),
            "token_type": token_data.get("token_type", "Bearer"),
            "scope": token_data.get("scope", ""),
            "raw": dict(token_data),  # Ensure raw is also a plain dict
        }
    except (
        APIError,
        AuthenticationError,
        BadRequestError,
        NotFoundError,
    ) as exc:
        raise APIError(f"Failed to obtain OAuth2 token: {exc}")


def is_resource_exists(client, resource_type, resource_id=None, resource_name=None):
    """Check if a resource exists in SCM by ID or name.

    Args:
        client: SCM client object
        resource_type: Type of resource to check (e.g., 'folder', 'device', etc.)
        resource_id: Resource ID to check
        resource_name: Resource name to check

    Returns:
        bool, dict: Tuple containing (exists, resource_data)
    """
    if not resource_id and not resource_name:
        return False, None

    try:
        # Map resource types to service attributes
        resource_mapping = {
            "address": "address",
            "address_group": "address_group",
            "agent_version": "agent_version",
            "application": "application",
            "application_filter": "application_filter",
            "application_group": "application_group",
            "device": "device",
            "folder": "folder",
            "service": "service",
            "service_group": "service_group",
            "tag": "tag",
        }

        service_name = resource_mapping.get(resource_type)
        if not service_name:
            return False, None

        service = getattr(client, service_name, None)
        if not service:
            return False, None

        # Check by ID first if provided
        if resource_id:
            try:
                response = service.get(resource_id)
                return True, response
            except (
                APIError,
                AuthenticationError,
                BadRequestError,
                NotFoundError,
            ):
                # handle or re-raise
                raise
        # If not found by ID or ID not provided, check by name
        if resource_name:
            # List all resources and filter by name
            response = service.list()
            if hasattr(response, "data") and response.data is not None:
                for res in response.data:
                    if res.get("name") == resource_name:
                        return True, res

        return False, None
    except (
        APIError,
        AuthenticationError,
        BadRequestError,
        NotFoundError,
    ):
        raise
