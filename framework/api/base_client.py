from __future__ import annotations

import logging
import typing

import httpx

from framework.api.exceptions import raise_for_status

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            follow_redirects=True,
        )

    def set_token(self, token: str) -> None:
        self._client.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self) -> None:
        self._client.headers.pop("Authorization", None)

    def get(self, path: str, **kwargs: typing.Any) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: typing.Any) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: typing.Any) -> httpx.Response:
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: typing.Any) -> httpx.Response:
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: typing.Any) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs: typing.Any) -> httpx.Response:
        url = (
            path if path.startswith("http") else f"{self._base_url}/{path.lstrip('/')}"
        )
        logger.debug("%s %s", method, url)

        response = self._client.request(method, url, **kwargs)
        logger.debug(
            "%s %s -> %d (%.0f ms)",
            method,
            url,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )

        raise_for_status(response.status_code, response.text, url)
        return response

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BaseClient":
        return self

    def __exit__(self, *_: typing.Any) -> None:
        self.close()
