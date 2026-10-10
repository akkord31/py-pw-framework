from __future__ import annotations

import logging

import allure
from playwright.sync_api import FrameLocator, PageAssertions

from framework.ui.page_adapter import PageAdapter

logger = logging.getLogger(__name__)


class BasePage:
    PATH: str = "/"

    def __init__(self, page: PageAdapter, base_url: str) -> None:
        self._page = page
        self._base_url = base_url.rstrip("/")

    @property
    def expect(self) -> PageAssertions:
        return self._page.expect

    @allure.step("Navigate to page")
    def open(self) -> "BasePage":
        url = f"{self._base_url}{self.PATH}"
        logger.info("Navigating to %s", url)
        self._page.goto(url)
        self._wait_for_ready()
        return self

    def _wait_for_ready(self) -> None:
        self._page.wait_for_load_state("domcontentloaded")

    def get_iframe_locator(self, selector: str) -> FrameLocator:
        return self._page.frame_locator(selector)
