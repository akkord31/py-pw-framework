from __future__ import annotations

import secrets
from collections.abc import Iterator

import httpx
import pytest

from tms.mock_api import MockTmsApi


@pytest.fixture(scope="session")
def tms_api() -> Iterator[MockTmsApi]:
    api = MockTmsApi(token=secrets.token_urlsafe(32)).start()
    try:
        yield api
    finally:
        api.stop()


@pytest.fixture
def api_client(tms_api: MockTmsApi) -> Iterator[httpx.Client]:
    with httpx.Client(
        base_url=tms_api.base_url,
        headers={"Authorization": f"Bearer {tms_api.token}"},
        timeout=3.0,
    ) as client:
        yield client
