"""Type stubs for client.py module."""

from typing import Any, Dict, List, Optional, Union

def get_scm_client_argument_spec() -> Dict[str, Dict[str, Any]]: ...
def get_scm_client(module: Any) -> Any: ...
def handle_scm_error(module: Any, error: Exception) -> None: ...
def get_oauth2_token(
    client_id: str,
    client_secret: str,
    tsg_id: str,
    scopes: Optional[List[str]] = None,
    log_level: str = "ERROR",
) -> Dict[str, Any]: ...
def is_resource_exists(
    client: Any, resource_type: str, resource_id: Optional[str] = None, resource_name: Optional[str] = None
) -> tuple[bool, Optional[Dict[str, Any]]]: ...
