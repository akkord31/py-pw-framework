from typing import Optional

from playwright.sync_api import Page

from framework.ui.ui_component import UiComponent


class CheckBox(UiComponent):
    def __init__(self, page: Page, selector: str) -> None:
        super().__init__(page, page.locator(selector))

    def check(
        self, *, timeout: Optional[float] = None, force: Optional[bool] = None
    ) -> None:
        self.locator.check(timeout=timeout, force=force)

    def uncheck(
        self, *, timeout: Optional[float] = None, force: Optional[bool] = None
    ) -> None:
        self.locator.uncheck(timeout=timeout, force=force)

    def is_checked(self, *, timeout: Optional[float] = None) -> bool:
        return self.locator.is_checked(timeout=timeout)

    def set_value(self, checked: bool, *, timeout: Optional[float] = None) -> None:
        if self.is_checked() != checked:
            self.check(timeout=timeout) if checked else self.uncheck(timeout=timeout)
