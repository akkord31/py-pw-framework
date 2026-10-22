import allure
from playwright.sync_api import Page

from framework.ui.base_page import BasePage
from framework.ui.components.login_form import LoginForm
from framework.ui.page_adapter import PageAdapter
from framework.ui.ui_component import UiComponent


class LoginPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(PageAdapter(page), base_url)

        self.login_form = LoginForm(page)
        self.username_input = self.login_form.username_input
        self.password_input = self.login_form.password_input
        self.login_button = self.login_form.login_button
        self.error_message = UiComponent(
            page,
            page.locator("[data-test='error']"),
        )

    def _wait_for_ready(self) -> None:
        self.login_button.expect.to_be_visible()

    @allure.step("Login as {username}")
    def login(self, username: str, password: str) -> None:
        self.login_form.login(username, password)

    @allure.step("Verify login error message")
    def expect_error(self, text: str) -> None:
        self.error_message.expect.to_have_text(text)

    @allure.step("Verify login error is visible")
    def expect_error_visible(self) -> None:
        self.error_message.expect.to_be_visible()

    @allure.step("Verify login error is not visible")
    def expect_error_not_visible(self) -> None:
        self.error_message.expect.not_to_be_visible()
