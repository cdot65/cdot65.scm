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
from ansible_collections.cdot65.scm.plugins.module_utils.scm import (
    scm_argument_spec,
    get_scm_client,
    handle_scm_error,
    is_resource_exists
)


def test_scm_argument_spec():
    """Test that the argument spec contains expected keys"""
    specs = scm_argument_spec()
    assert 'api_key' in specs
    assert 'api_url' in specs
    assert specs['api_key']['no_log'] is True


@patch('ansible_collections.cdot65.scm.plugins.module_utils.scm.SCMClient')
def test_get_scm_client_with_params(mock_scm_client):
    """Test get_scm_client with parameters from the module"""
    module = MagicMock()
    module.params = {
        'api_key': 'test_key',
        'api_url': 'https://test.api.url'
    }
    
    client = get_scm_client(module)
    
    mock_scm_client.assert_called_once_with(api_key='test_key', base_url='https://test.api.url')
    assert client is not None


@patch('ansible_collections.cdot65.scm.plugins.module_utils.scm.SCMClient')
def test_get_scm_client_with_env_vars(mock_scm_client):
    """Test get_scm_client with environment variables"""
    module = MagicMock()
    module.params = {
        'api_key': None,
        'api_url': None
    }
    
    with patch.dict(os.environ, {
        'SCM_API_KEY': 'env_test_key',
        'SCM_API_URL': 'https://env.test.api.url'
    }):
        client = get_scm_client(module)
    
    mock_scm_client.assert_called_once_with(
        api_key='env_test_key', 
        base_url='https://env.test.api.url'
    )
    assert client is not None


@patch('ansible_collections.cdot65.scm.plugins.module_utils.scm.SCMClient')
def test_get_scm_client_missing_api_key(mock_scm_client):
    """Test get_scm_client fails when API key is missing"""
    module = MagicMock()
    module.params = {
        'api_key': None,
        'api_url': 'https://test.api.url'
    }
    
    with patch.dict(os.environ, {'SCM_API_KEY': '', 'SCM_API_URL': ''}):
        with pytest.raises(SystemExit):
            get_scm_client(module)
            
    module.fail_json.assert_called_once()
    assert 'API key is required' in module.fail_json.call_args[1]['msg']


def test_handle_scm_error():
    """Test that handle_scm_error translates errors correctly"""
    module = MagicMock()
    
    # Test with generic exception
    handle_scm_error(module, Exception("Test error"))
    module.fail_json.assert_called_with(msg="Unknown error occurred: Test error")
    
    # Reset mock
    module.reset_mock()
    
    # Create a mock for SCMAuthenticationError with a custom exception class
    mock_auth_error = type('SCMAuthenticationError', (Exception,), {})()
    mock_auth_error.__str__ = lambda _: "Auth failed"
    
    with patch('ansible_collections.cdot65.scm.plugins.module_utils.scm.SCMAuthenticationError', mock_auth_error.__class__):
        handle_scm_error(module, mock_auth_error)
        module.fail_json.assert_called_with(msg="Authentication error: Auth failed")


@patch('ansible_collections.cdot65.scm.plugins.module_utils.scm.SCMResourceNotFoundError')
def test_is_resource_exists(mock_not_found):
    """Test is_resource_exists for folder resources"""
    # Mock client with folder methods
    client = MagicMock()
    client.folder.get_by_id.return_value = {'id': '123', 'name': 'test_folder'}
    client.folder.list.return_value = [
        {'id': '123', 'name': 'test_folder'},
        {'id': '456', 'name': 'other_folder'}
    ]
    
    # Test exists by ID
    exists, data = is_resource_exists(client, 'folder', resource_id='123')
    assert exists is True
    assert data['id'] == '123'
    
    # Test exists by name
    exists, data = is_resource_exists(client, 'folder', resource_name='test_folder')
    assert exists is True
    assert data['name'] == 'test_folder'
    
    # Test not exists by name
    exists, data = is_resource_exists(client, 'folder', resource_name='nonexistent')
    assert exists is False
    assert data is None
