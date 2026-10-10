from __future__ import annotations

import typing

from playwright.sync_api import FrameLocator, Locator, Page, PageAssertions
from playwright.sync_api import expect as pw_expect


class PageAdapter:
    def __init__(self, page: Page) -> None:
        self._page = page

    def locator(self, selector: str) -> Locator:
        return self._page.locator(selector)

    def frame_locator(self, selector: str) -> FrameLocator:
        return self._page.frame_locator(selector)

    def goto(self, url: str) -> None:
        self._page.goto(url)

    def wait_for_load_state(
        self,
        state: typing.Literal[
            "domcontentloaded", "load", "networkidle"
        ] = "domcontentloaded",
        *,
        timeout: typing.Optional[float] = None,
    ) -> None:
        self._page.wait_for_load_state(state, timeout=timeout)

    def wait_for_url(self, url: str, *, timeout: typing.Optional[float] = None) -> None:
        self._page.wait_for_url(url, timeout=timeout)

    def screenshot(self, *, path: str | None = None, full_page: bool = False) -> bytes:
        return self._page.screenshot(path=path, full_page=full_page)

    @property
    def expect(self) -> PageAssertions:
        return pw_expect(self._page)

    @property
    def url(self) -> str:
        return self._page.url

    @property
    def raw_page(self) -> Page:
        """Escape hatch — прямой доступ к pw.Page"""
        return self._page
