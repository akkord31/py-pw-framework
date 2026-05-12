from __future__ import annotations


class APIError(Exception):
    def __init__(self, status_code: int, body: str, url: str = "") -> None:
        self.status_code = status_code
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status_code} @ {url!r}: {body[:300]}")


class UnauthorizedError(APIError):
    pass


class ForbiddenError(APIError):
    pass


class NotFoundError(APIError):
    pass


class UnprocessableError(APIError):
    pass


class ServerError(APIError):
    pass


_STATUS_MAP: dict[int, type[APIError]] = {
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    422: UnprocessableError,
}


def raise_for_status(status_code: int, body: str, url: str = "") -> None:
    if status_code < 400:
        return

    if status_code >= 500:
        raise ServerError(status_code, body, url)

    raise _STATUS_MAP.get(status_code, APIError)(status_code, body, url)
