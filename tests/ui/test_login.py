from __future__ import annotations

import re

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
        login = LoginPage(
            page,
            base_url,
        ).open()
        login.login("standard_user", "secret_sauce")

        dashboard = DashboardPage(page, base_url)
        dashboard.expect.to_have_url(re.compile(r"/inventory\.html$"))
        dashboard.expect_logon()

    @allure.title("Wrong password shows error message")
    def test_login_wrong_password(self, page: Page, base_url: str) -> None:
        login = LoginPage(page, base_url).open()
        login.login("admin", "wrongpassword")
        login.expect_error_visible()
