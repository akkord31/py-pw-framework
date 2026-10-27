from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import ValidationError

from tms.errors import (
    TmsApiError,
    TmsAuthenticationError,
    TmsAuthorizationError,
    TmsConfigurationError,
    TmsError,
    TmsNotFoundError,
    TmsRateLimitError,
    TmsResponseError,
    TmsServerError,
    TmsTimeoutError,
    TmsTransportError,
    TmsValidationError,
)
from tms.models import TestCase, TestCasePage

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class TmsClient:
    """HTTP implementation of the read-only ``TmsProvider`` contract.

    The client owns bearer authentication, timeouts, bounded exponential
    retries and translation of API error envelopes into typed exceptions.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 5.0,
        max_retries: int = 2,
        backoff: float = 0.1,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise TmsConfigurationError("base_url must start with http:// or https://")
        if not token:
            raise TmsConfigurationError("A bearer token is required")
        if timeout <= 0:
            raise TmsConfigurationError("timeout must be greater than zero")
        if max_retries < 0:
            raise TmsConfigurationError("max_retries must not be negative")
        if backoff < 0:
            raise TmsConfigurationError("backoff must not be negative")

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff = backoff
        client_kwargs: dict[str, Any] = {
            "base_url": self._base_url,
            "timeout": httpx.Timeout(timeout),
            "headers": {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "User-Agent": "py-pw-framework-tms/0.1",
            },
            "follow_redirects": False,
        }
        if transport is not None:
            client_kwargs["transport"] = transport
        self._client = httpx.Client(**client_kwargs)

    def search_test_cases(
        self,
        *,
        query: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TestCasePage:
        params: dict[str, str | int] = {"page": page, "page_size": page_size}
        optional = {
            "q": query,
            "priority": priority,
            "status": status,
            "tag": tag,
        }
        for key, value in optional.items():
            if value is not None and value != "":
                params[key] = value

        response = self._request("GET", "/api/v1/test-cases", params=params)
        return self._parse_page(response)

    def get_test_case(self, case_id: str) -> TestCase:
        safe_id = quote(case_id, safe="")
        response = self._request("GET", f"/api/v1/test-cases/{safe_id}")
        return self._parse_case(response)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TmsClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        last_error: TmsError | None = None
        for attempt in range(1, self._max_retries + 2):
            try:
                response = self._client.request(method, path, **kwargs)
            except httpx.TimeoutException as exc:
                last_error = TmsTimeoutError(
                    f"TMS request timed out after {self._timeout}s",
                    code="timeout",
                    attempts=attempt,
                )
                last_error.__cause__ = exc
            except httpx.TransportError as exc:
                last_error = TmsTransportError(
                    f"TMS transport error: {exc.__class__.__name__}",
                    code="transport_error",
                    attempts=attempt,
                )
                last_error.__cause__ = exc
            else:
                if (
                    response.status_code in RETRYABLE_STATUS_CODES
                    and attempt <= self._max_retries
                ):
                    logger.warning(
                        "Retryable TMS response %s on attempt %s/%s",
                        response.status_code,
                        attempt,
                        self._max_retries + 1,
                    )
                    self._sleep(attempt)
                    continue
                return self._handle_response(response, attempts=attempt)

            if attempt <= self._max_retries:
                self._sleep(attempt)

        if last_error is None:  # pragma: no cover - defensive
            raise TmsTransportError("TMS request failed", code="transport_error")
        raise last_error

    def _sleep(self, attempt: int) -> None:
        if self._backoff:
            time.sleep(self._backoff * (2 ** (attempt - 1)))

    def _handle_response(
        self,
        response: httpx.Response,
        *,
        attempts: int,
    ) -> httpx.Response:
        if response.status_code < 400:
            return response

        code, message, details = self._error_payload(response)
        common = {
            "code": code,
            "status_code": response.status_code,
            "details": details,
            "attempts": attempts,
        }
        if response.status_code == 401:
            raise TmsAuthenticationError(message, **common)
        if response.status_code == 403:
            raise TmsAuthorizationError(message, **common)
        if response.status_code == 404:
            raise TmsNotFoundError(message, **common)
        if response.status_code in {400, 422}:
            raise TmsValidationError(message, **common)
        if response.status_code == 429:
            raise TmsRateLimitError(message, **common)
        if response.status_code >= 500:
            raise TmsServerError(message, **common)
        raise TmsApiError(message, **common)

    @staticmethod
    def _error_payload(response: httpx.Response) -> tuple[str, str, Any]:
        fallback = response.text[:300] or response.reason_phrase
        try:
            payload = response.json()
        except ValueError:
            return "http_error", fallback, None
        if not isinstance(payload, dict):
            return "http_error", fallback, payload
        error = payload.get("error")
        if not isinstance(error, dict):
            return "http_error", fallback, payload
        code = error.get("code") or "http_error"
        message = error.get("message") or fallback
        return str(code), str(message), error.get("details")

    @staticmethod
    def _parse_page(response: httpx.Response) -> TestCasePage:
        try:
            payload = response.json()
            return TestCasePage.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            raise TmsResponseError(
                "TMS search response did not match TestCasePage",
                code="invalid_response",
                status_code=response.status_code,
                attempts=1,
            ) from exc

    @staticmethod
    def _parse_case(response: httpx.Response) -> TestCase:
        try:
            payload = response.json()
            return TestCase.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            raise TmsResponseError(
                "TMS test-case response did not match TestCase",
                code="invalid_response",
                status_code=response.status_code,
                attempts=1,
            ) from exc


__all__ = ["TmsClient"]
