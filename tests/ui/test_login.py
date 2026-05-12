from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


@allure.feature("Authentication")
@allure.story("UI Login")
@pytest.mark.ui
class TestLogin:

    @allure.title("Successful login redirects to dashboard")
    @pytest.mark.smoke
    def test_login_success(self, page: Page, base_url: str) -> None:
        login = LoginPage(page, base_url).open()
        login.login("admin", "admin")

        dashboard = DashboardPage(page, base_url)
        dashboard.expect_url_contains("/dashboard")
        dashboard.expect_welcome("admin")

    @allure.title("Wrong password shows error message")
    def test_login_wrong_password(self, page: Page, base_url: str) -> None:
        login = LoginPage(page, base_url).open()
        login.login("admin", "wrongpassword")
        login.expect_error_visible()

    @allure.title("Empty fields — submit button is disabled")
    def test_login_empty_fields(self, page: Page, base_url: str) -> None:
        login = LoginPage(page, base_url).open()
        login.submit_button.expect_disabled()
