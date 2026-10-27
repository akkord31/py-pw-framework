from __future__ import annotations

from typing import Any


class TmsError(Exception):
    """Base class for every TMS failure.

    ``code`` is the stable machine-readable code from the API (or a local
    fallback such as ``transport_error``). ``attempts`` records how many HTTP
    attempts were made, which is useful when diagnosing retry exhaustion.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: Any = None,
        attempts: int | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.attempts = attempts
        super().__init__(message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        if self.code:
            parts.append(f"code={self.code}")
        if self.attempts is not None:
            parts.append(f"attempts={self.attempts}")
        return " | ".join(parts)


class TmsConfigurationError(TmsError):
    """Invalid client or server configuration."""


class TmsAuthenticationError(TmsError):
    """The bearer token was missing, invalid or rejected (401)."""


class TmsAuthorizationError(TmsError):
    """The bearer token is valid but not allowed to perform the request (403)."""


class TmsNotFoundError(TmsError):
    """The requested test case does not exist (404)."""


class TmsApiError(TmsError):
    """The API rejected the request with an unmapped 4xx status."""


class TmsValidationError(TmsError):
    """The API rejected request parameters (400/422)."""


class TmsRateLimitError(TmsError):
    """The server kept returning 429 after the bounded retries."""


class TmsServerError(TmsError):
    """The server kept failing (5xx) after the bounded retries."""


class TmsTransportError(TmsError):
    """A connection/transport failure survived the bounded retries."""


class TmsTimeoutError(TmsTransportError):
    """A request timeout survived the bounded retries."""


class TmsResponseError(TmsError):
    """The server returned a successful status with an invalid payload."""


__all__ = [
    "TmsApiError",
    "TmsAuthenticationError",
    "TmsAuthorizationError",
    "TmsConfigurationError",
    "TmsError",
    "TmsNotFoundError",
    "TmsRateLimitError",
    "TmsResponseError",
    "TmsServerError",
    "TmsTimeoutError",
    "TmsTransportError",
    "TmsValidationError",
]
