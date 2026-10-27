from __future__ import annotations

import secrets

import httpx
import pytest

from tms.client import TmsClient
from tms.errors import (
    TmsAuthenticationError,
    TmsConfigurationError,
    TmsNotFoundError,
    TmsResponseError,
    TmsServerError,
    TmsTimeoutError,
    TmsValidationError,
)
from tms.mock_api import MockTmsApi
from tms.mock_data import get_mock_cases
from tms.models import TestCasePage
from tms.provider import TmsProvider

TEST_TOKEN = secrets.token_urlsafe(24)


def _page_payload() -> dict:
    case = get_mock_cases()[0]
    return TestCasePage(
        items=[case],
        page=1,
        page_size=20,
        total=1,
        total_pages=1,
    ).model_dump(mode="json")


def test_client_satisfies_provider_and_works_against_mock_api(
    tms_api: MockTmsApi,
) -> None:
    with TmsClient(
        tms_api.base_url,
        tms_api.token,
        timeout=3.0,
        max_retries=0,
    ) as client:
        assert isinstance(client, TmsProvider)

        page = client.search_test_cases(
            query="login",
            priority="high",
            page_size=2,
        )
        assert page.total >= 1
        assert all(case.priority.value == "high" for case in page.items)

        case = client.get_test_case("TMS-1001")
        assert case.id == "TMS-1001"
        assert case.steps
        assert case.version.number == 3


def test_get_missing_case_raises_not_found(tms_api: MockTmsApi) -> None:
    with TmsClient(
        tms_api.base_url,
        tms_api.token,
        max_retries=0,
    ) as client:
        with pytest.raises(TmsNotFoundError) as exc_info:
            client.get_test_case("TMS-9999")

    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "not_found"


def test_transient_server_errors_are_retried_then_succeed() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls < 3:
            return httpx.Response(
                503,
                json={
                    "error": {
                        "code": "unavailable",
                        "message": "temporarily unavailable",
                    }
                },
            )
        return httpx.Response(200, json=_page_payload())

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        max_retries=2,
        backoff=0.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        page = client.search_test_cases()

    assert calls == 3
    assert page.total == 1


def test_retry_budget_is_bounded() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            503,
            json={
                "error": {
                    "code": "unavailable",
                    "message": "still unavailable",
                }
            },
        )

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        max_retries=2,
        backoff=0.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(TmsServerError) as exc_info:
            client.search_test_cases()

    assert calls == 3
    assert exc_info.value.attempts == 3
    assert exc_info.value.status_code == 503


def test_authentication_errors_are_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "unauthorized",
                    "message": "bad token",
                }
            },
        )

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        max_retries=4,
        backoff=0.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(TmsAuthenticationError) as exc_info:
            client.search_test_cases()

    assert calls == 1
    assert exc_info.value.status_code == 401


def test_timeouts_are_retried_then_raise_timeout_error() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("timed out", request=request)

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        timeout=0.01,
        max_retries=1,
        backoff=0.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(TmsTimeoutError) as exc_info:
            client.search_test_cases()

    assert calls == 2
    assert exc_info.value.attempts == 2


def test_validation_errors_are_not_retried() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": "invalid_query",
                    "message": "page must be at least 1",
                }
            },
        )

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        max_retries=2,
        backoff=0.0,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(TmsValidationError) as exc_info:
            client.search_test_cases(page=0)

    assert calls == 1
    assert exc_info.value.code == "invalid_query"


def test_malformed_success_payload_is_structured() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    with TmsClient(
        "http://testserver",
        TEST_TOKEN,
        max_retries=0,
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(TmsResponseError) as exc_info:
            client.search_test_cases()

    assert exc_info.value.code == "invalid_response"


def test_configuration_rejects_missing_token() -> None:
    with pytest.raises(TmsConfigurationError):
        TmsClient("http://testserver", "")
