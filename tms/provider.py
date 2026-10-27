from __future__ import annotations

from typing import Protocol, runtime_checkable

from tms.models import TestCase, TestCasePage


@runtime_checkable
class TmsProvider(Protocol):
    """Read-only TMS provider contract.

    ``TmsClient`` is the HTTP implementation used by the local mock. A real
    Zephyr/Jira adapter can implement the same protocol without changing the
    MCP server or its tools.
    """

    def search_test_cases(
        self,
        *,
        query: str | None = None,
        priority: str | None = None,
        status: str | None = None,
        tag: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TestCasePage: ...

    def get_test_case(self, case_id: str) -> TestCase: ...

    def close(self) -> None: ...


__all__ = ["TmsProvider"]
