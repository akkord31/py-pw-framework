from __future__ import annotations

import httpx

from tms.mock_api import MockTmsApi
from tms.mock_data import get_mock_cases
from tms.models import Priority


def test_health_is_public(tms_api: MockTmsApi) -> None:
    response = httpx.get(f"{tms_api.base_url}/api/v1/health", timeout=3.0)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "mock-tms",
        "api_version": "v1",
    }


def test_missing_bearer_token_is_rejected(tms_api: MockTmsApi) -> None:
    response = httpx.get(
        f"{tms_api.base_url}/api/v1/test-cases",
        timeout=3.0,
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_wrong_bearer_token_is_rejected(tms_api: MockTmsApi) -> None:
    response = httpx.get(
        f"{tms_api.base_url}/api/v1/test-cases",
        headers={"Authorization": "Bearer definitely-not-the-token"},
        timeout=3.0,
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_list_defaults(api_client: httpx.Client) -> None:
    response = api_client.get("/api/v1/test-cases")

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 20
    assert payload["total"] == 12
    assert payload["total_pages"] == 1
    assert len(payload["items"]) == 12


def test_search_filter_and_tag(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"q": "checkout", "priority": "high", "tag": "payment"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload["items"]] == ["TMS-1007"]
    assert payload["items"][0]["priority"] == Priority.HIGH.value


def test_search_matches_step_text(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"q": "token_type"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == ["TMS-1012"]


def test_filter_by_status(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"status": "draft"},
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == ["TMS-1009"]


def test_pagination_is_one_based(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"page": 3, "page_size": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 3
    assert payload["page_size"] == 5
    assert payload["total"] == 12
    assert payload["total_pages"] == 3
    assert len(payload["items"]) == 2


def test_invalid_pagination_is_structured(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"page": 0},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_query"


def test_invalid_priority_is_structured(api_client: httpx.Client) -> None:
    response = api_client.get(
        "/api/v1/test-cases",
        params={"priority": "urgent"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_query"


def test_get_case_contains_steps_and_version(api_client: httpx.Client) -> None:
    response = api_client.get("/api/v1/test-cases/TMS-1001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "TMS-1001"
    assert payload["priority"] == "high"
    assert payload["version"]["number"] == 3
    assert payload["version"]["changelog"]
    assert payload["steps"][0]["expected_result"]
    assert payload["steps"][0]["number"] == 1


def test_get_missing_case_is_structured(api_client: httpx.Client) -> None:
    response = api_client.get("/api/v1/test-cases/TMS-9999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_only_versioned_route_is_served(api_client: httpx.Client) -> None:
    response = api_client.get("/api/v2/test-cases")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_write_methods_are_rejected(api_client: httpx.Client) -> None:
    response = api_client.post("/api/v1/test-cases", json={"title": "nope"})

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


def test_mock_data_is_deterministic_and_complete() -> None:
    first = get_mock_cases()
    second = get_mock_cases()

    assert [case.model_dump() for case in first] == [
        case.model_dump() for case in second
    ]
    assert len(first) == 12
    assert len({case.id for case in first}) == 12
    assert {case.priority for case in first} == set(Priority)
    assert all(case.steps for case in first)
    assert all(step.expected_result.strip() for case in first for step in case.steps)
    assert all(case.version.number >= 1 for case in first)
