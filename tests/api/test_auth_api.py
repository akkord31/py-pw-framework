from __future__ import annotations

import httpx
import pytest
import respx

from clients.auth_client import AuthClient
from framework.api.exceptions import ForbiddenError, UnauthorizedError
from models.auth import LoginRequest

BASE_URL = "http://testserver"


@pytest.fixture
def auth_client():
    client = AuthClient(base_url=BASE_URL)
    yield client
    client.close()


@respx.mock
def test_login_returns_token(auth_client: AuthClient) -> None:
    respx.post(f"{BASE_URL}/auth/login").mock(
        return_value=httpx.Response(
            200, json={"access_token": "abc123", "token_type": "bearer"}
        )
    )

    response = auth_client.login(LoginRequest(username="admin", password="admin"))

    assert response.token == "abc123"
    assert response.token_type == "bearer"


@respx.mock
def test_login_invalid_password(auth_client: AuthClient) -> None:
    respx.post(f"{BASE_URL}/auth/login").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid credentials"})
    )

    with pytest.raises(UnauthorizedError) as exc_info:
        auth_client.login(LoginRequest(username="admin", password="wrong"))

    assert exc_info.value.status_code == 401


@respx.mock
def test_login_forbidden(auth_client: AuthClient) -> None:
    respx.post(f"{BASE_URL}/auth/login").mock(
        return_value=httpx.Response(403, json={"detail": "Forbidden"})
    )

    with pytest.raises(ForbiddenError) as exc_info:
        auth_client.login(LoginRequest(username="blocked_user", password="admin"))

    assert exc_info.value.status_code == 403
