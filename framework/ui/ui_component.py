from __future__ import annotations

from playwright.sync_api import Locator, LocatorAssertions, Page
from playwright.sync_api import expect as pw_expect


class UiComponent:
    def __init__(self, page: Page, locator: Locator) -> None:
        self._page = page
        self._locator = locator

    @property
    def locator(self) -> Locator:
        return self._locator

    @property
    def expect(self) -> LocatorAssertions:
        return pw_expect(self._locator)
