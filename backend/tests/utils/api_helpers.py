"""
API Test Helpers for BARQ Fleet Management System

This module provides helper functions for API testing including:
- Authentication helpers
- Request builders
- Response validators
- Common test utilities

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

from typing import Dict, Any, Optional, List
from fastapi.testclient import TestClient
from app.core.security import TokenManager


# ==================== Authentication Helpers ====================

def get_auth_headers(token: str) -> Dict[str, str]:
    """
    Create authorization headers for authenticated requests

    Args:
        token: JWT access token

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}


def create_test_token(user_id: int, email: str, role: str = "user") -> str:
    """
    Create a test JWT token

    Args:
        user_id: User ID
        email: User email
        role: User role

    Returns:
        JWT access token string
    """
    return TokenManager.create_access_token(
        data={"sub": str(user_id), "email": email, "role": role}
    )


def login_user(client: TestClient, email: str, password: str) -> Dict[str, Any]:
    """
    Login a user and return the authentication response

    Args:
        client: FastAPI test client
        email: User email
        password: User password

    Returns:
        Login response data including token
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()


# ==================== Request Builders ====================

def make_get_request(
    client: TestClient,
    url: str,
    token: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Make an authenticated GET request

    Args:
        client: FastAPI test client
        url: Request URL
        token: Optional JWT token
        params: Optional query parameters

    Returns:
        Response object
    """
    headers = get_auth_headers(token) if token else {}
    return client.get(url, headers=headers, params=params or {})


def make_post_request(
    client: TestClient,
    url: str,
    data: Dict[str, Any],
    token: Optional[str] = None
) -> Any:
    """
    Make an authenticated POST request

    Args:
        client: FastAPI test client
        url: Request URL
        data: Request body data
        token: Optional JWT token

    Returns:
        Response object
    """
    headers = get_auth_headers(token) if token else {}
    return client.post(url, json=data, headers=headers)


def make_put_request(
    client: TestClient,
    url: str,
    data: Dict[str, Any],
    token: Optional[str] = None
) -> Any:
    """
    Make an authenticated PUT request

    Args:
        client: FastAPI test client
        url: Request URL
        data: Request body data
        token: Optional JWT token

    Returns:
        Response object
    """
    headers = get_auth_headers(token) if token else {}
    return client.put(url, json=data, headers=headers)


def make_patch_request(
    client: TestClient,
    url: str,
    data: Dict[str, Any],
    token: Optional[str] = None
) -> Any:
    """
    Make an authenticated PATCH request

    Args:
        client: FastAPI test client
        url: Request URL
        data: Request body data
        token: Optional JWT token

    Returns:
        Response object
    """
    headers = get_auth_headers(token) if token else {}
    return client.patch(url, json=data, headers=headers)


def make_delete_request(
    client: TestClient,
    url: str,
    token: Optional[str] = None
) -> Any:
    """
    Make an authenticated DELETE request

    Args:
        client: FastAPI test client
        url: Request URL
        token: Optional JWT token

    Returns:
        Response object
    """
    headers = get_auth_headers(token) if token else {}
    return client.delete(url, headers=headers)


# ==================== Response Validators ====================

def assert_success_response(response: Any, status_code: int = 200):
    """
    Assert that a response is successful

    Args:
        response: Response object
        status_code: Expected status code
    """
    assert response.status_code == status_code
    data = response.json()
    assert data.get("success") is True or "data" in data


def assert_error_response(
    response: Any,
    status_code: int,
    error_message: Optional[str] = None
):
    """
    Assert that a response is an error

    Args:
        response: Response object
        status_code: Expected status code
        error_message: Optional expected error message
    """
    assert response.status_code == status_code
    data = response.json()

    if error_message:
        assert error_message in str(data.get("detail", ""))


def assert_validation_error(response: Any, field: Optional[str] = None):
    """
    Assert that a response is a validation error

    Args:
        response: Response object
        field: Optional field name that should have error
    """
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

    if field:
        errors = data["detail"]
        assert any(
            error.get("loc", [])[-1] == field
            for error in errors
        )


def assert_unauthorized(response: Any):
    """
    Assert that a response is unauthorized

    Args:
        response: Response object
    """
    assert response.status_code == 401


def assert_forbidden(response: Any):
    """
    Assert that a response is forbidden

    Args:
        response: Response object
    """
    assert response.status_code == 403


def assert_not_found(response: Any):
    """
    Assert that a response is not found

    Args:
        response: Response object
    """
    assert response.status_code == 404


# ==================== Data Validators ====================

def assert_courier_data(data: Dict[str, Any], expected: Dict[str, Any]):
    """
    Assert courier data matches expected values

    Args:
        data: Actual courier data
        expected: Expected courier data
    """
    assert data["barq_id"] == expected["barq_id"]
    assert data["full_name"] == expected["full_name"]
    assert data["email"] == expected["email"]
    assert data["status"] == expected["status"]


def assert_vehicle_data(data: Dict[str, Any], expected: Dict[str, Any]):
    """
    Assert vehicle data matches expected values

    Args:
        data: Actual vehicle data
        expected: Expected vehicle data
    """
    assert data["plate_number"] == expected["plate_number"]
    assert data["vehicle_type"] == expected["vehicle_type"]
    assert data["make"] == expected["make"]
    assert data["model"] == expected["model"]
    assert data["status"] == expected["status"]


def assert_delivery_data(data: Dict[str, Any], expected: Dict[str, Any]):
    """
    Assert delivery data matches expected values

    Args:
        data: Actual delivery data
        expected: Expected delivery data
    """
    assert data["tracking_number"] == expected["tracking_number"]
    assert data["status"] == expected["status"]
    assert data["customer_name"] == expected["customer_name"]


def assert_pagination(data: Dict[str, Any], expected_items: int):
    """
    Assert pagination data is correct

    Args:
        data: Response data with pagination
        expected_items: Expected number of items
    """
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "pages" in data
    assert len(data["items"]) == expected_items


# ==================== List & Filtering Helpers ====================

def test_list_endpoint(
    client: TestClient,
    url: str,
    token: str,
    expected_count: Optional[int] = None
):
    """
    Test a list endpoint with standard checks

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        expected_count: Optional expected item count
    """
    response = make_get_request(client, url, token)
    assert_success_response(response)

    data = response.json()
    assert "items" in data or isinstance(data, list)

    if expected_count is not None:
        items = data.get("items", data)
        assert len(items) == expected_count

    return data


def test_filter_endpoint(
    client: TestClient,
    url: str,
    token: str,
    filters: Dict[str, Any],
    expected_count: Optional[int] = None
):
    """
    Test a list endpoint with filters

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        filters: Filter parameters
        expected_count: Optional expected item count
    """
    response = make_get_request(client, url, token, params=filters)
    assert_success_response(response)

    data = response.json()
    items = data.get("items", data)

    if expected_count is not None:
        assert len(items) == expected_count

    return data


def test_search_endpoint(
    client: TestClient,
    url: str,
    token: str,
    search_term: str,
    expected_count: Optional[int] = None
):
    """
    Test a search endpoint

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        search_term: Search query
        expected_count: Optional expected result count
    """
    response = make_get_request(
        client, url, token,
        params={"search": search_term}
    )
    assert_success_response(response)

    data = response.json()
    items = data.get("items", data)

    if expected_count is not None:
        assert len(items) == expected_count

    return data


# ==================== CRUD Test Helpers ====================

def test_create_endpoint(
    client: TestClient,
    url: str,
    token: str,
    data: Dict[str, Any],
    expected_status: int = 201
):
    """
    Test a create endpoint

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        data: Data to create
        expected_status: Expected status code

    Returns:
        Created resource data
    """
    response = make_post_request(client, url, data, token)
    assert response.status_code == expected_status

    result = response.json()
    assert "id" in result or "data" in result

    return result


def test_get_endpoint(
    client: TestClient,
    url: str,
    token: str,
    expected_status: int = 200
):
    """
    Test a get endpoint

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        expected_status: Expected status code

    Returns:
        Retrieved resource data
    """
    response = make_get_request(client, url, token)
    assert response.status_code == expected_status

    return response.json()


def test_update_endpoint(
    client: TestClient,
    url: str,
    token: str,
    data: Dict[str, Any],
    expected_status: int = 200
):
    """
    Test an update endpoint

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        data: Data to update
        expected_status: Expected status code

    Returns:
        Updated resource data
    """
    response = make_put_request(client, url, data, token)
    assert response.status_code == expected_status

    return response.json()


def test_delete_endpoint(
    client: TestClient,
    url: str,
    token: str,
    expected_status: int = 204
):
    """
    Test a delete endpoint

    Args:
        client: FastAPI test client
        url: Endpoint URL
        token: Auth token
        expected_status: Expected status code
    """
    response = make_delete_request(client, url, token)
    assert response.status_code == expected_status


# ==================== Workflow Test Helpers ====================

def create_workflow_instance(
    client: TestClient,
    token: str,
    template_id: int,
    entity_type: str,
    entity_id: int
) -> Dict[str, Any]:
    """
    Create a workflow instance

    Args:
        client: FastAPI test client
        token: Auth token
        template_id: Workflow template ID
        entity_type: Entity type (e.g., 'leave', 'delivery')
        entity_id: Entity ID

    Returns:
        Workflow instance data
    """
    data = {
        "template_id": template_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "title": f"Test {entity_type} workflow"
    }

    response = make_post_request(
        client,
        "/api/v1/workflow/instances",
        data,
        token
    )

    assert_success_response(response, 201)
    return response.json()


def approve_workflow_step(
    client: TestClient,
    token: str,
    instance_id: int,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Approve a workflow step

    Args:
        client: FastAPI test client
        token: Auth token
        instance_id: Workflow instance ID
        notes: Optional approval notes

    Returns:
        Updated workflow instance data
    """
    data = {"action": "approve"}
    if notes:
        data["notes"] = notes

    response = make_post_request(
        client,
        f"/api/v1/workflow/instances/{instance_id}/action",
        data,
        token
    )

    assert_success_response(response)
    return response.json()


def reject_workflow_step(
    client: TestClient,
    token: str,
    instance_id: int,
    reason: str
) -> Dict[str, Any]:
    """
    Reject a workflow step

    Args:
        client: FastAPI test client
        token: Auth token
        instance_id: Workflow instance ID
        reason: Rejection reason

    Returns:
        Updated workflow instance data
    """
    data = {"action": "reject", "notes": reason}

    response = make_post_request(
        client,
        f"/api/v1/workflow/instances/{instance_id}/action",
        data,
        token
    )

    assert_success_response(response)
    return response.json()
