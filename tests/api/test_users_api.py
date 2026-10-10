from __future__ import annotations

import httpx
import pytest
import respx

from clients.users_client import UsersClient
from framework.api.exceptions import NotFoundError

BASE_URL = "http://testserver"


@pytest.fixture
def users_client():
    client = UsersClient(base_url=BASE_URL)
    yield client
    client.close()


@respx.mock
def test_get_user(users_client: UsersClient) -> None:
    respx.get(f"{BASE_URL}/users/1").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 1,
                "username": "admin",
                "email": "admin@test.local",
                "role": "admin",
                "is_active": True,
            },
        )
    )

    user = users_client.get_user(1)

    assert user.id == 1
    assert user.username == "admin"
    assert user.role == "admin"


@respx.mock
def test_get_user_not_found(users_client: UsersClient) -> None:
    respx.get(f"{BASE_URL}/users/999").mock(
        return_value=httpx.Response(404, json={"detail": "User not found"})
    )

    with pytest.raises(NotFoundError) as exc_info:
        users_client.get_user(999)

    assert exc_info.value.status_code == 404
