from typing import Optional

from playwright.sync_api import Locator, Page

from framework.ui.ui_component import UiComponent


class Input(UiComponent):
    def __init__(
        self,
        page: Page,
        selector: str,
        *,
        root: Optional[Locator] = None,
    ) -> None:
        locator = page.locator(selector) if root is None else root.locator(selector)
        super().__init__(page, locator)

    def fill(
        self,
        value: str,
        *,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
    ) -> None:
        self.locator.fill(value, timeout=timeout, force=force)

    def clear(
        self,
        *,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
    ) -> None:
        self.locator.clear(timeout=timeout, force=force)

    def input_value(self, *, timeout: Optional[float] = None) -> str:
        return self.locator.input_value(timeout=timeout)
