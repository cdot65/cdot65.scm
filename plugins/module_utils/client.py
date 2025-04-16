#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <cremsburg.dev@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Strata Cloud Manager API client module utilities."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Import Python libs
import os
import sys
from typing import Any, Dict, List, Optional, Union

HAS_SCM_SDK = False
SCM_SDK_IMPORT_ERROR = None
try:
    from scm.client import ScmClient
    from scm.exceptions import (
        APIError,
        AuthenticationError,
        BadRequestError,
        NotFoundError,
        ResourceNotFoundError,
    )
    HAS_SCM_SDK = True
except ImportError as e:
    SCM_SDK_IMPORT_ERROR = e

from ansible.module_utils.basic import missing_required_lib


def get_scm_client_argument_spec():
    """
    Return common SCM authentication and connection argument spec for modules.

    Returns:
        dict: Standard SCM module argument spec for authentication parameters
    """
    return dict(
        client_id=dict(type="str", required=False),
        client_secret=dict(type="str", required=False, no_log=True),
        tsg_id=dict(type="str", required=False),
        api_key=dict(type="str", required=False, no_log=True),
        api_base_url=dict(
            type="str",
            required=False,
            default="https://api.strata.paloaltonetworks.com"
        ),
        token_url=dict(
            type="str",
            required=False,
            default="https://auth.apps.paloaltonetworks.com/am/oauth2/access_token"
        ),
        log_level=dict(
            type="str",
            required=False,
            default="ERROR",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        ),
    )


def get_scm_client(module):
    """
    Initialize and return a SCM client using credentials from module parameters or environment variables.

    Args:
        module: Ansible module object

    Returns:
        ScmClient: Initialized SCM client object

    Raises:
        Exception: If SDK is not installed or client cannot be initialized
    """
    if not HAS_SCM_SDK:
        module.fail_json(msg=missing_required_lib('pan-scm-sdk', exception=SCM_SDK_IMPORT_ERROR))

    # Check if using API key or OAuth2 for authentication
    api_key = module.params.get('api_key') or os.environ.get('SCM_API_KEY')
    
    # OAuth2 credentials
    client_id = module.params.get('client_id') or os.environ.get('SCM_CLIENT_ID')
    client_secret = module.params.get('client_secret') or os.environ.get('SCM_CLIENT_SECRET')
    tsg_id = module.params.get('tsg_id') or os.environ.get('SCM_TSG_ID')
    
    # Common parameters
    api_base_url = module.params.get('api_base_url') or os.environ.get('SCM_API_BASE_URL')
    token_url = module.params.get('token_url') or os.environ.get('SCM_TOKEN_URL')
    log_level = module.params.get('log_level') or os.environ.get('SCM_LOG_LEVEL', 'ERROR')

    # Validate authentication parameters
    if api_key:
        # API key auth is not directly supported by the SDK yet
        module.fail_json(msg="API key authentication is not supported by the current SCM SDK. Use OAuth2 authentication instead.")
    
    if not all([client_id, client_secret, tsg_id]):
        module.fail_json(
            msg="OAuth2 authentication requires client_id, client_secret, and tsg_id. "
            "Provide via parameters or SCM_CLIENT_ID, SCM_CLIENT_SECRET, SCM_TSG_ID environment variables."
        )
    
    try:
        client = ScmClient(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            api_base_url=api_base_url,
            token_url=token_url,
            log_level=log_level
        )
        return client
    except Exception as e:
        handle_scm_error(module, e)


def handle_scm_error(module, error):
    """
    Handle SCM API errors and translate them to Ansible module failures.

    Args:
        module: Ansible module object
        error: Exception raised by SCM API call

    Returns:
        None
    """
    msg = "An error occurred while interacting with SCM API"
    
    if isinstance(error, AuthenticationError):
        msg = f"Authentication error: {str(error)}"
    elif isinstance(error, BadRequestError):
        msg = f"Bad request error: {str(error)}"
    elif isinstance(error, ResourceNotFoundError):
        msg = f"Resource not found: {str(error)}"
    elif isinstance(error, NotFoundError):
        msg = f"Not found error: {str(error)}"
    elif isinstance(error, APIError):
        msg = f"API error: {str(error)}"
    else:
        msg = f"Unknown error occurred: {str(error)}"
    
    module.fail_json(msg=msg)


def is_resource_exists(client, resource_type, resource_id=None, resource_name=None):
    """
    Check if a resource exists in SCM by ID or name.

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
            'address': 'address',
            'address_group': 'address_group',
            'agent_version': 'agent_version',
            'application': 'application',
            'application_filter': 'application_filter',
            'application_group': 'application_group',
            'device': 'device',
            'folder': 'folder',
            'service': 'service',
            'service_group': 'service_group',
            'tag': 'tag',
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
            except ResourceNotFoundError:
                pass

        # If not found by ID or ID not provided, check by name
        if resource_name:
            # List all resources and filter by name
            response = service.list()
            if hasattr(response, 'data') and response.data is not None:
                for res in response.data:
                    if res.get('name') == resource_name:
                        return True, res
                
        return False, None
    except ResourceNotFoundError:
        return False, None
    except Exception:
        # Other errors should be handled by the calling module
        raise
