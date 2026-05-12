from __future__ import annotations

import allure

from framework.ui.base_page import BasePage
from framework.ui.components.button import Button
from framework.ui.page_adapter import PageAdapter


class DashboardPage(BasePage):
    PATH = "/dashboard"

    def __init__(self, page: PageAdapter, base_url: str) -> None:
        super().__init__(page, base_url)
        self.welcome_banner = page.locator("[data-testid='welcome-banner']")
        self.user_menu = Button(page, "[data-testid='user-menu']")
        self.logout_button = Button(page, "[data-testid='logout']")

    def _wait_for_ready(self) -> None:
        self._page.wait_for_load_state("networkidle")
        self.welcome_banner.expect.to_be_visible()

    @allure.step("Logout from dashboard")
    def logout(self) -> None:
        self.user_menu.click()
        self.logout_button.click()

    def expect_welcome(self, username: str) -> None:
        self.welcome_banner.expect.to_contain_text(username)
