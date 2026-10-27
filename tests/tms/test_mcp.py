from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _send(proc: subprocess.Popen[str], message: dict[str, Any]) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()


def _read(proc: subprocess.Popen[str]) -> dict[str, Any]:
    assert proc.stdout is not None
    line = proc.stdout.readline()
    assert line, "MCP server closed stdout unexpectedly"
    return json.loads(line)


def _call(
    proc: subprocess.Popen[str],
    request_id: int,
    method: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        },
    )
    while True:
        response = _read(proc)
        if response.get("id") == request_id:
            return response


@pytest.fixture
def mcp_server() -> Iterator[subprocess.Popen[str]]:
    env = os.environ.copy()
    env.pop("TMS_API_TOKEN", None)
    proc = subprocess.Popen(
        [sys.executable, "-m", "tms.mcp_server", "--mock"],
        cwd=PROJECT_ROOT,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    try:
        yield proc
    finally:
        if proc.poll() is None:
            try:
                if proc.stdin is not None:
                    proc.stdin.close()
            except OSError:
                pass
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def _initialize(proc: subprocess.Popen[str]) -> dict[str, Any]:
    response = _call(
        proc,
        1,
        "initialize",
        {
            "protocolVersion": "2026-07-28",
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1.0"},
        },
    )
    _send(
        proc,
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        },
    )
    return response


def test_initialize_and_tool_list(mcp_server: subprocess.Popen[str]) -> None:
    response = _initialize(mcp_server)

    assert response["result"]["serverInfo"]["name"] == "mock-tms"
    assert response["result"]["protocolVersion"] == "2026-07-28"

    tools = _call(mcp_server, 2, "tools/list")["result"]["tools"]
    names = {tool["name"] for tool in tools}
    assert names == {"search_test_cases", "get_test_case"}
    assert all(tool["inputSchema"]["type"] == "object" for tool in tools)


def test_mcp_search_and_get(mcp_server: subprocess.Popen[str]) -> None:
    _initialize(mcp_server)

    search = _call(
        mcp_server,
        2,
        "tools/call",
        {
            "name": "search_test_cases",
            "arguments": {
                "query": "login",
                "priority": "high",
                "page_size": 2,
            },
        },
    )["result"]
    assert search["isError"] is False
    page = search["structuredContent"]
    assert page["page_size"] == 2
    assert page["total"] >= 1
    assert all(item["priority"] == "high" for item in page["items"])
    assert json.loads(search["content"][0]["text"]) == page

    get = _call(
        mcp_server,
        3,
        "tools/call",
        {
            "name": "get_test_case",
            "arguments": {"case_id": "TMS-1001"},
        },
    )["result"]
    assert get["isError"] is False
    case = get["structuredContent"]
    assert case["id"] == "TMS-1001"
    assert case["steps"][0]["expected_result"]
    assert case["version"]["number"] == 3


def test_mcp_not_found_is_a_tool_error(
    mcp_server: subprocess.Popen[str],
) -> None:
    _initialize(mcp_server)

    result = _call(
        mcp_server,
        2,
        "tools/call",
        {
            "name": "get_test_case",
            "arguments": {"case_id": "TMS-9999"},
        },
    )["result"]

    assert result["isError"] is True
    assert "not_found" in result["content"][0]["text"]


def test_mcp_invalid_arguments_are_a_tool_error(
    mcp_server: subprocess.Popen[str],
) -> None:
    _initialize(mcp_server)

    result = _call(
        mcp_server,
        2,
        "tools/call",
        {
            "name": "search_test_cases",
            "arguments": {"page": 0},
        },
    )["result"]

    assert result["isError"] is True
    assert "invalid_arguments" in result["content"][0]["text"]


def test_mcp_unknown_tool_is_a_protocol_error(
    mcp_server: subprocess.Popen[str],
) -> None:
    _initialize(mcp_server)

    response = _call(
        mcp_server,
        2,
        "tools/call",
        {"name": "delete_everything", "arguments": {}},
    )

    assert response["error"]["code"] == -32602
