#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Calvin Remsburg <cremsburg@paloaltonetworks.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import pytest
from unittest.mock import patch, MagicMock

# Import the module being tested
from ansible_collections.cdot65.scm.plugins.module_utils.client import (
    get_scm_client_argument_spec,
    get_scm_client,
    handle_scm_error,
    is_resource_exists
)

# Create mock exceptions for testing
class MockAPIError(Exception):
    pass

class MockAuthenticationError(Exception):
    pass

class MockBadRequestError(Exception):
    pass

class MockNotFoundError(Exception):
    pass

class MockResourceNotFoundError(Exception):
    pass


def test_scm_client_argument_spec():
    """Test that the argument spec contains expected keys"""
    specs = get_scm_client_argument_spec()
    assert 'client_id' in specs
    assert 'client_secret' in specs
    assert 'tsg_id' in specs
    assert 'api_key' in specs
    assert 'api_base_url' in specs
    assert 'token_url' in specs
    assert 'log_level' in specs
    assert specs['client_secret']['no_log'] is True
    assert specs['api_key']['no_log'] is True


@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.ScmClient')
def test_get_scm_client_with_params(mock_scm_client):
    """Test get_scm_client with parameters from the module"""
    module = MagicMock()
    module.params = {
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'tsg_id': 'test_tsg_id',
        'api_key': None,
        'api_base_url': 'https://test.api.url',
        'token_url': 'https://test.token.url',
        'log_level': 'DEBUG'
    }
    
    client = get_scm_client(module)
    
    mock_scm_client.assert_called_once_with(
        client_id='test_client_id',
        client_secret='test_client_secret',
        tsg_id='test_tsg_id',
        api_base_url='https://test.api.url',
        token_url='https://test.token.url',
        log_level='DEBUG'
    )
    assert client is not None


@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.ScmClient')
def test_get_scm_client_with_env_vars(mock_scm_client):
    """Test get_scm_client with environment variables"""
    module = MagicMock()
    module.params = {
        'client_id': None,
        'client_secret': None,
        'tsg_id': None,
        'api_key': None,
        'api_base_url': None,
        'token_url': None,
        'log_level': None
    }
    
    with patch.dict(os.environ, {
        'SCM_CLIENT_ID': 'env_client_id',
        'SCM_CLIENT_SECRET': 'env_client_secret',
        'SCM_TSG_ID': 'env_tsg_id',
        'SCM_API_BASE_URL': 'https://env.api.url',
        'SCM_TOKEN_URL': 'https://env.token.url',
        'SCM_LOG_LEVEL': 'INFO'
    }):
        client = get_scm_client(module)
    
    mock_scm_client.assert_called_once_with(
        client_id='env_client_id',
        client_secret='env_client_secret',
        tsg_id='env_tsg_id',
        api_base_url='https://env.api.url',
        token_url='https://env.token.url',
        log_level='INFO'
    )
    assert client is not None


@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.ScmClient')
def test_get_scm_client_missing_credentials(mock_scm_client):
    """Test get_scm_client fails when credentials are missing"""
    module = MagicMock()
    module.params = {
        'client_id': None,
        'client_secret': None,
        'tsg_id': None,
        'api_key': None,
        'api_base_url': 'https://test.api.url',
        'token_url': 'https://test.token.url',
        'log_level': 'ERROR'
    }
    
    with patch.dict(os.environ, {
        'SCM_CLIENT_ID': '',
        'SCM_CLIENT_SECRET': '',
        'SCM_TSG_ID': '',
        'SCM_API_KEY': '',
    }):
        with pytest.raises(SystemExit):
            get_scm_client(module)
            
    module.fail_json.assert_called_once()
    assert 'OAuth2 authentication requires' in module.fail_json.call_args[1]['msg']


@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.AuthenticationError', MockAuthenticationError)
@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.BadRequestError', MockBadRequestError)
@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.ResourceNotFoundError', MockResourceNotFoundError)
@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.NotFoundError', MockNotFoundError)
@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.APIError', MockAPIError)
def test_handle_scm_error():
    """Test that handle_scm_error translates errors correctly"""
    module = MagicMock()
    
    # Test with generic exception
    handle_scm_error(module, Exception("Test error"))
    module.fail_json.assert_called_with(msg="Unknown error occurred: Test error")
    
    # Reset mock
    module.reset_mock()
    
    # Test with AuthenticationError
    handle_scm_error(module, MockAuthenticationError("Auth failed"))
    module.fail_json.assert_called_with(msg="Authentication error: Auth failed")
    
    # Reset mock
    module.reset_mock()
    
    # Test with BadRequestError
    handle_scm_error(module, MockBadRequestError("Bad request"))
    module.fail_json.assert_called_with(msg="Bad request error: Bad request")
    
    # Reset mock
    module.reset_mock()
    
    # Test with ResourceNotFoundError
    handle_scm_error(module, MockResourceNotFoundError("Resource not found"))
    module.fail_json.assert_called_with(msg="Resource not found: Resource not found")


@patch('ansible_collections.cdot65.scm.plugins.module_utils.client.ResourceNotFoundError', MockResourceNotFoundError)
def test_is_resource_exists():
    """Test is_resource_exists for folder resources"""
    # Setup mock client
    client = MagicMock()
    folder_service = MagicMock()
    client.folder = folder_service
    
    # Test with resource found by ID
    folder_data = {'id': 'folder123', 'name': 'Test Folder'}
    folder_service.get.return_value = folder_data
    
    exists, data = is_resource_exists(client, 'folder', 'folder123')
    assert exists is True
    assert data == folder_data
    folder_service.get.assert_called_once_with('folder123')
    
    # Reset mocks
    folder_service.reset_mock()
    
    # Test with resource found by name
    folder_list_response = MagicMock()
    folder_list_response.data = [
        {'id': 'folder456', 'name': 'Another Folder'},
        {'id': 'folder789', 'name': 'Test Folder'}
    ]
    folder_service.list.return_value = folder_list_response
    
    # Test resource not found by ID, but found by name
    folder_service.get.side_effect = MockResourceNotFoundError("Not found")
    
    exists, data = is_resource_exists(client, 'folder', None, 'Test Folder')
    assert exists is True
    assert data == {'id': 'folder789', 'name': 'Test Folder'}
    
    # Test resource not found by either ID or name
    folder_service.reset_mock()
    folder_service.get.side_effect = MockResourceNotFoundError("Not found")
    
    exists, data = is_resource_exists(client, 'folder', None, 'Non-existent Folder')
    assert exists is False
    assert data is None
