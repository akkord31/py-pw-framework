from __future__ import annotations

import argparse
import json
import logging
import os
import secrets
import sys
from typing import Any, TextIO

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tms.client import TmsClient
from tms.errors import TmsConfigurationError, TmsError
from tms.mock_api import MockTmsApi
from tms.provider import TmsProvider

logger = logging.getLogger(__name__)

SERVER_NAME = "mock-tms"
SERVER_VERSION = "0.1.0"
SUPPORTED_PROTOCOL_VERSIONS = frozenset(
    {
        "2024-11-05",
        "2025-03-26",
        "2025-06-18",
        "2026-07-28",
    }
)

SEARCH_TOOL = "search_test_cases"
GET_TOOL = "get_test_case"

TOOLS: list[dict[str, Any]] = [
    {
        "name": SEARCH_TOOL,
        "description": (
            "Search read-only TMS test cases. Returns a page of typed test "
            "cases with steps, expected results, priority, status and version "
            "metadata."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Case-insensitive text search.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "approved", "deprecated"],
                },
                "tag": {"type": "string"},
                "page": {"type": "integer", "minimum": 1, "default": 1},
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": GET_TOOL,
        "description": (
            "Retrieve one read-only TMS test case by its stable TMS id, "
            "including every step and expected result."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string",
                    "pattern": r"^TMS-\d{4}$",
                    "description": "Stable test-case id, for example TMS-1001.",
                }
            },
            "required": ["case_id"],
            "additionalProperties": False,
        },
    },
]


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str | None = None
    priority: str | None = None
    status: str | None = None
    tag: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class GetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(pattern=r"^TMS-\d{4}$")


class McpServer:
    """Small JSON-RPC 2.0 / MCP stdio server with two read-only tools."""

    def __init__(
        self,
        provider: TmsProvider,
        stdin: Any,
        stdout: TextIO,
    ) -> None:
        self._provider = provider
        self._stdin = stdin
        self._stdout = stdout

    def serve(self) -> None:
        for line in self._stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._write(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                        },
                    }
                )
                continue

            if not isinstance(message, dict):
                self._write(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32600,
                            "message": "Invalid request",
                        },
                    }
                )
                continue

            method = message.get("method")
            if method == "exit":
                break
            if "id" not in message:
                # Notifications (including notifications/initialized).
                continue

            response = self._handle(message)
            if response is not None:
                self._write(response)

    def _handle(self, message: dict[str, Any]) -> dict[str, Any]:
        request_id = message.get("id")
        method = message.get("method")
        params = message.get("params") or {}
        if not isinstance(params, dict):
            return self._rpc_error(request_id, -32602, "params must be an object")

        if method == "initialize":
            requested = params.get("protocolVersion")
            version = (
                requested if requested in SUPPORTED_PROTOCOL_VERSIONS else "2025-06-18"
            )
            return self._result(
                request_id,
                {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                    "instructions": (
                        "Read-only mock TMS. Use search_test_cases to find "
                        "cases and get_test_case to read one case."
                    ),
                },
            )

        if method == "ping":
            return self._result(request_id, {})

        if method == "shutdown":
            return self._result(request_id, {})

        if method == "tools/list":
            return self._result(request_id, {"tools": TOOLS})

        if method == "tools/call":
            return self._call_tool(request_id, params)

        return self._rpc_error(request_id, -32601, f"Unknown method: {method}")

    def _call_tool(
        self,
        request_id: Any,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            return self._rpc_error(request_id, -32602, "arguments must be an object")

        try:
            if name == SEARCH_TOOL:
                request = SearchRequest.model_validate(arguments)
                result = self._provider.search_test_cases(
                    query=request.query,
                    priority=request.priority,
                    status=request.status,
                    tag=request.tag,
                    page=request.page,
                    page_size=request.page_size,
                )
                return self._result(
                    request_id,
                    self._tool_result(result.model_dump(mode="json")),
                )

            if name == GET_TOOL:
                request = GetRequest.model_validate(arguments)
                result = self._provider.get_test_case(request.case_id)
                return self._result(
                    request_id,
                    self._tool_result(result.model_dump(mode="json")),
                )

            return self._rpc_error(request_id, -32602, f"Unknown tool: {name}")
        except ValidationError as exc:
            return self._result(
                request_id,
                self._tool_error("invalid_arguments", str(exc)),
            )
        except TmsError as exc:
            return self._result(
                request_id,
                self._tool_error(exc.code or "tms_error", exc.message),
            )
        except Exception:
            logger.exception("Unexpected TMS tool failure")
            return self._result(
                request_id,
                self._tool_error(
                    "internal_error",
                    "Unexpected TMS tool failure",
                ),
            )

    def _result(self, request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    def _rpc_error(
        self,
        request_id: Any,
        code: int,
        message: str,
    ) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }

    def _tool_result(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(data, indent=2, ensure_ascii=False),
                }
            ],
            "structuredContent": data,
            "isError": False,
        }

    def _tool_error(self, code: str, message: str) -> dict[str, Any]:
        return {
            "content": [{"type": "text", "text": f"{code}: {message}"}],
            "isError": True,
        }

    def _write(self, response: dict[str, Any]) -> None:
        self._stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        self._stdout.flush()


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise TmsConfigurationError(f"{name} must be a number") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise TmsConfigurationError(f"{name} must be an integer") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only mock TMS MCP server (stdio transport)."
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Start the in-process mock REST API and serve it via MCP.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("TMS_LOG_LEVEL", "WARNING"),
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.WARNING),
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    api: MockTmsApi | None = None
    try:
        token = os.getenv("TMS_API_TOKEN")
        if args.mock:
            token = token or secrets.token_urlsafe(32)
            api = MockTmsApi(token).start()
            base_url = api.base_url
        else:
            base_url = os.getenv("TMS_API_BASE_URL", "http://127.0.0.1:8765")
            if not token:
                raise TmsConfigurationError(
                    "TMS_API_TOKEN is required when --mock is not used"
                )

        provider = TmsClient(
            base_url,
            token,
            timeout=_env_float("TMS_TIMEOUT_SECONDS", 5.0),
            max_retries=_env_int("TMS_MAX_RETRIES", 2),
            backoff=_env_float("TMS_BACKOFF_SECONDS", 0.1),
        )
        try:
            McpServer(provider, sys.stdin, sys.stdout).serve()
        finally:
            provider.close()
    except TmsConfigurationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    finally:
        if api is not None:
            api.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
