#!/usr/bin/python

# Copyright: (c) 2025, Calvin Remsburg (@cdot65) <dev@cdot.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from unittest.mock import MagicMock, patch

# Import the module being tested
from ansible_collections.cdot65.scm.plugins.module_utils.client import (
    get_oauth2_token,
    get_scm_client,
    get_scm_client_argument_spec,
    handle_scm_error,
    is_resource_exists,
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


def test_scm_client_argument_spec():
    """Test that the argument spec contains expected keys."""
    specs = get_scm_client_argument_spec()
    assert "client_id" in specs
    assert "client_secret" in specs
    assert "tsg_id" in specs
    assert "scopes" in specs
    assert "log_level" in specs
    assert specs["client_secret"]["no_log"] is True
    assert specs["client_id"]["no_log"] is True


@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.ScmClient")
def test_get_scm_client_with_params(mock_scm_client):
    """Test get_scm_client with parameters from the module."""
    module = MagicMock()
    module.params = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tsg_id": "test_tsg_id",
        "log_level": "DEBUG",
    }

    client = get_scm_client(module)

    mock_scm_client.assert_called_once_with(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
        log_level="DEBUG",
    )
    assert client is not None


@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.ScmClient")
@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.APIError", MockAPIError)
def test_get_scm_client_handles_exceptions(mock_scm_client):
    """Test get_scm_client handles SDK exceptions."""
    module = MagicMock()
    module.params = {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tsg_id": "test_tsg_id",
        "log_level": "ERROR",
    }

    # Mock the ScmClient to raise an APIError
    mock_scm_client.side_effect = MockAPIError("SDK Error")

    get_scm_client(module)

    # Should call fail_json when exception occurs
    module.fail_json.assert_called_once()
    assert "Failed to initialize SCM client" in module.fail_json.call_args[1]["msg"]


def test_handle_scm_error():
    """Test that handle_scm_error translates errors correctly."""
    module = MagicMock()

    # Test with generic exception
    handle_scm_error(module, Exception("Test error"))
    module.fail_json.assert_called_with(msg="Test error")


@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.NotFoundError", MockNotFoundError)
def test_is_resource_exists_by_id():
    """Test is_resource_exists for resources found by ID."""
    # Setup mock client
    client = MagicMock()
    folder_service = MagicMock()
    client.folder = folder_service

    # Test with resource found by ID
    folder_data = {"id": "folder123", "name": "Test Folder"}
    folder_service.get.return_value = folder_data

    exists, data = is_resource_exists(client, "folder", resource_id="folder123")
    assert exists is True
    assert data == folder_data
    folder_service.get.assert_called_once_with("folder123")


@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.NotFoundError", MockNotFoundError)
def test_is_resource_exists_by_name():
    """Test is_resource_exists for resources found by name."""
    # Setup mock client
    client = MagicMock()
    folder_service = MagicMock()
    client.folder = folder_service

    # Test with resource found by name
    folder_list_response = MagicMock()
    folder_list_response.data = [
        {"id": "folder456", "name": "Another Folder"},
        {"id": "folder789", "name": "Test Folder"},
    ]
    folder_service.list.return_value = folder_list_response

    # Test resource not found by ID, but found by name
    folder_service.get.side_effect = MockNotFoundError("Not found")

    exists, data = is_resource_exists(client, "folder", resource_id=None, resource_name="Test Folder")
    assert exists is True
    assert data == {"id": "folder789", "name": "Test Folder"}


@patch("ansible_collections.cdot65.scm.plugins.module_utils.client.NotFoundError", MockNotFoundError)
def test_is_resource_exists_not_found():
    """Test is_resource_exists when resource is not found."""
    # Setup mock client
    client = MagicMock()
    folder_service = MagicMock()
    client.folder = folder_service

    folder_list_response = MagicMock()
    folder_list_response.data = [
        {"id": "folder456", "name": "Another Folder"},
    ]
    folder_service.list.return_value = folder_list_response

    # Test resource not found by either ID or name
    folder_service.get.side_effect = MockNotFoundError("Not found")

    exists, data = is_resource_exists(client, "folder", resource_id=None, resource_name="Non-existent Folder")
    assert exists is False
    assert data is None


@patch("scm.auth.OAuth2Client")
@patch("scm.models.auth.AuthRequestModel")
def test_get_oauth2_token(mock_auth_request, mock_oauth_client):
    """Test get_oauth2_token function."""
    # Setup mocks
    mock_token_data = {
        "access_token": "test_token_123",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "tsg_id:12345",
    }
    mock_oauth_instance = MagicMock()
    mock_oauth_instance.session.token = mock_token_data
    mock_oauth_client.return_value = mock_oauth_instance

    # Call the function
    result = get_oauth2_token(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
        scopes=["tsg_id:12345"],
        log_level="ERROR",
    )

    # Verify the result
    assert result["access_token"] == "test_token_123"
    assert result["expires_in"] == 3600
    assert result["token_type"] == "Bearer"
    assert result["scope"] == "tsg_id:12345"
    assert "raw" in result

    # Verify AuthRequestModel was called with correct params
    mock_auth_request.assert_called_once_with(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tsg_id="test_tsg_id",
        scope="tsg_id:12345",
    )
