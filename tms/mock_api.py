from __future__ import annotations

import json
import logging
import secrets
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from tms.mock_data import get_mock_cases
from tms.models import Priority, TestCase, TestCaseStatus

logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class _QueryError(ValueError):
    pass


def _first(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    return values[0] if values else None


def _positive_int(
    params: dict[str, list[str]],
    key: str,
    *,
    default: int,
    maximum: int | None = None,
) -> int:
    raw = _first(params, key)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise _QueryError(f"{key} must be an integer") from exc
    if value < 1:
        raise _QueryError(f"{key} must be at least 1")
    if maximum is not None and value > maximum:
        raise _QueryError(f"{key} must be at most {maximum}")
    return value


def _enum_param(params: dict[str, list[str]], key: str) -> str | None:
    raw = _first(params, key)
    if raw is None:
        return None
    return raw.casefold()


def _haystack(case: TestCase) -> str:
    parts = [
        case.id,
        case.title,
        case.description,
        case.component,
        case.owner,
        *case.tags,
        *(step.action for step in case.steps),
        *(step.expected_result for step in case.steps),
    ]
    return " ".join(parts).casefold()


def _make_handler(cases: list[TestCase], token: str) -> type[BaseHTTPRequestHandler]:
    class MockTmsHandler(BaseHTTPRequestHandler):
        server_version = "MockTms/0.1"
        sys_version = ""

        def log_message(self, fmt: str, *args: Any) -> None:
            logger.debug("%s - %s", self.address_string(), fmt % args)

        def _send_json(self, status_code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _error(
            self,
            status_code: int,
            code: str,
            message: str,
            *,
            details: Any = None,
        ) -> None:
            error: dict[str, Any] = {"code": code, "message": message}
            if details is not None:
                error["details"] = details
            self._send_json(status_code, {"error": error})

        def _authorized(self) -> bool:
            header = self.headers.get("Authorization", "")
            scheme, _, value = header.partition(" ")
            if scheme.casefold() != "bearer" or not value:
                return False
            return secrets.compare_digest(value, token)

        def _list_cases(self, query: str) -> None:
            params = parse_qs(query, keep_blank_values=True)
            try:
                page = _positive_int(params, "page", default=1)
                page_size = _positive_int(
                    params,
                    "page_size",
                    default=DEFAULT_PAGE_SIZE,
                    maximum=MAX_PAGE_SIZE,
                )
                priority_raw = _enum_param(params, "priority")
                status_raw = _enum_param(params, "status")
                tag_raw = _enum_param(params, "tag")
                priority = Priority(priority_raw) if priority_raw else None
                status = TestCaseStatus(status_raw) if status_raw else None
            except (ValueError, _QueryError) as exc:
                self._error(400, "invalid_query", str(exc))
                return

            query_text = (_first(params, "q") or "").strip().casefold()
            filtered = [
                case
                for case in cases
                if (not query_text or query_text in _haystack(case))
                and (priority is None or case.priority == priority)
                and (status is None or case.status == status)
                and (
                    tag_raw is None
                    or any(tag.casefold() == tag_raw for tag in case.tags)
                )
            ]

            total = len(filtered)
            total_pages = (total + page_size - 1) // page_size if total else 0
            start = (page - 1) * page_size
            items = filtered[start : start + page_size]

            self._send_json(
                200,
                {
                    "items": [item.model_dump(mode="json") for item in items],
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                },
            )

        def _get_case(self, case_id: str) -> None:
            case = next((item for item in cases if item.id == case_id), None)
            if case is None:
                self._error(
                    404,
                    "not_found",
                    f"Test case {case_id!r} was not found",
                )
                return
            self._send_json(200, case.model_dump(mode="json"))

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"

            if path == f"{API_PREFIX}/health":
                self._send_json(
                    200,
                    {
                        "status": "ok",
                        "service": "mock-tms",
                        "api_version": "v1",
                    },
                )
                return

            if not self._authorized():
                self._error(
                    401,
                    "unauthorized",
                    "A valid bearer token is required",
                )
                return

            if path == f"{API_PREFIX}/test-cases":
                self._list_cases(parsed.query)
                return

            prefix = f"{API_PREFIX}/test-cases/"
            if path.startswith(prefix):
                case_id = unquote(path[len(prefix) :])
                if not case_id or "/" in case_id:
                    self._error(404, "not_found", "Unknown TMS resource")
                    return
                self._get_case(case_id)
                return

            self._error(404, "not_found", "Unknown TMS resource")

        def _method_not_allowed(self) -> None:
            self._error(
                405,
                "method_not_allowed",
                "This mock TMS API is read-only",
            )

        do_POST = _method_not_allowed
        do_PUT = _method_not_allowed
        do_PATCH = _method_not_allowed
        do_DELETE = _method_not_allowed

    return MockTmsHandler


class MockTmsApi:
    """Threaded local REST API with deterministic data and bearer auth."""

    def __init__(
        self,
        token: str,
        *,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        if not token:
            raise ValueError("token must not be empty")
        self._token = token
        self._host = host
        self._port = port
        self._cases = get_mock_cases()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def token(self) -> str:
        return self._token

    @property
    def base_url(self) -> str:
        if self._server is None:
            raise RuntimeError("MockTmsApi is not started")
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> "MockTmsApi":
        if self._server is not None:
            raise RuntimeError("MockTmsApi is already started")
        handler = _make_handler(self._cases, self._token)
        server = ThreadingHTTPServer((self._host, self._port), handler)
        server.daemon_threads = True
        thread = threading.Thread(
            target=server.serve_forever,
            name="mock-tms-api",
            daemon=True,
        )
        thread.start()
        self._server = server
        self._thread = thread
        return self

    def stop(self) -> None:
        server, thread = self._server, self._thread
        self._server = None
        self._thread = None
        if server is None:
            return
        server.shutdown()
        server.server_close()
        if thread is not None:
            thread.join(timeout=2)

    def __enter__(self) -> "MockTmsApi":
        return self.start()

    def __exit__(self, *_: object) -> None:
        self.stop()


def main(argv: list[str] | None = None) -> int:
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Run the local read-only mock TMS REST API."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)

    token = os.getenv("TMS_API_TOKEN")
    if not token:
        print(
            "TMS_API_TOKEN is required to start the standalone mock API.",
            file=sys.stderr,
        )
        return 2

    api = MockTmsApi(token, host=args.host, port=args.port).start()
    print(
        f"Mock TMS API listening on {api.base_url} (API: /api/v1)",
        file=sys.stderr,
    )
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        api.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
