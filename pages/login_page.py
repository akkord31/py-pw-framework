from __future__ import annotations

import allure
from playwright.sync_api import Page

from framework.ui.components.button import Button
from framework.ui.components.input import InputField
from framework.ui.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.username_input = InputField(page, "[data-testid='username']")
        self.password_input = InputField(page, "[data-testid='password']")
        self.submit_button = Button(page, "[data-testid='login-submit']")
        self.error_message = page.locator("[data-testid='login-error']")

    def _wait_for_ready(self) -> None:
        self._page.wait_for_load_state("domcontentloaded")
        self.submit_button.expect.to_be_visible()

    @allure.step("Login as {username}")
    def login(self, username: str, password: str) -> None:
        self.username_input.fill_value(username)
        self.password_input.fill_value(password)
        self.submit_button.click()

    def expect_error(self, text: str) -> None:
        from playwright.sync_api import expect
        expect(self.error_message).to_have_text(text)

    def expect_error_visible(self) -> None:
        from playwright.sync_api import expect
        expect(self.error_message).to_be_visible()
