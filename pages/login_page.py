import allure
from playwright.sync_api import Page

from framework.ui.base_page import BasePage
from framework.ui.page_adapter import PageAdapter
from framework.ui.ui_component import UiComponent
from framework.ui.components.button import Button
from framework.ui.components.input import Input


class LoginPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(PageAdapter(page), base_url)

        self.username_input = Input(page, "[data-test='username']")
        self.password_input = Input(page, "[data-test='password']")
        self.login_button = Button(page, "[data-test='login-button']")
        self.error_message = UiComponent(
            page,
            page.locator("[data-test='error']"),
        )

    def _wait_for_ready(self) -> None:
        self.login_button.expect.to_be_visible()

    @allure.step("Login as {username}")
    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    @allure.step("Verify login error message")
    def expect_error(self, text: str) -> None:
        self.error_message.expect.to_have_text(text)

    @allure.step("Verify login error is visible")
    def expect_error_visible(self) -> None:
        self.error_message.expect.to_be_visible()

    @allure.step("Verify login error is not visible")
    def expect_error_not_visible(self) -> None:
        self.error_message.expect.not_to_be_visible()