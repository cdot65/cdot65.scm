"""Type stubs for client.py module."""

from typing import Any

def get_scm_client_argument_spec() -> dict[str, dict[str, Any]]: ...
def get_scm_client(module: Any) -> Any: ...
def handle_scm_error(module: Any, error: Exception) -> None: ...
def get_oauth2_token(
    client_id: str,
    client_secret: str,
    tsg_id: str,
    scopes: list[str] | None = None,
    log_level: str = "ERROR",
) -> dict[str, Any]: ...
def is_resource_exists(
    client: Any, resource_type: str, resource_id: str | None = None, resource_name: str | None = None
) -> tuple[bool, dict[str, Any] | None]: ...
