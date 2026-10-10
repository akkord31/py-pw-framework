from __future__ import annotations

import allure
from playwright.sync_api import Page

from framework.ui import UiComponent
from framework.ui.base_page import BasePage
from framework.ui.components.button import Button
from framework.ui.page_adapter import PageAdapter


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(PageAdapter(page), base_url)
        self.app_logo = UiComponent(page, page.locator("//div[@class='app_logo']"))
        self.user_menu = Button(page, "[data-testid='user-menu']")
        self.logout_button = Button(page, "[data-testid='logout']")

    def _wait_for_ready(self) -> None:
        self._page.wait_for_load_state("networkidle")
        self.app_logo.expect.to_be_visible()

    @allure.step("Logout from dashboard")
    def logout(self) -> None:
        self.user_menu.click()
        self.logout_button.click()

    def expect_logon(self) -> None:
        self.app_logo.expect.to_be_visible()
