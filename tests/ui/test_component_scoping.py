from __future__ import annotations

import allure
import pytest
from playwright.sync_api import Page, expect

from framework.ui.components.button import Button
from framework.ui.components.input import Input

ISOLATED_DOM = """
<div data-test="container-a">
  <input data-test="username" value="container-a-value">
  <button
    data-test="action"
    data-state="idle"
    onclick="this.dataset.state = 'clicked'; this.textContent = 'container-a-clicked'"
  >container-a-idle</button>
</div>
<div data-test="container-b">
  <input data-test="username" value="container-b-value">
  <button
    data-test="action"
    data-state="idle"
    onclick="this.dataset.state = 'clicked'; this.textContent = 'container-b-clicked'"
  >container-b-idle</button>
</div>
"""


def _load_isolated_dom(page: Page) -> None:
    page.set_content(ISOLATED_DOM)


@allure.feature("UI components")
@allure.story("Root-scoped components")
@pytest.mark.ui
class TestComponentScoping:
    @allure.title("Input resolves its selector inside the given root")
    @allure.description(
        "Verifies that Input built with an explicit root reads the value "
        "from container B, the second of two matching containers, while the "
        "same selector matches both containers when resolved page-wide."
    )
    def test_input_root_scopes_locator(self, page: Page) -> None:
        _load_isolated_dom(page)

        username = Input(
            page,
            "[data-test='username']",
            root=page.locator("[data-test='container-b']"),
        )

        assert username.locator.count() == 1, (
            "Root-scoped Input must resolve exactly one username field"
        )
        assert username.input_value() == "container-b-value", (
            "Root-scoped Input must read container B's value, not container A's"
        )
        assert page.locator("[data-test='username']").count() == 2, (
            "The username selector must match both containers page-wide"
        )

    @allure.title("Button acts only on the element inside its root")
    @allure.description(
        "Verifies that Button built with an explicit root clicks only "
        "container B's button, the second of two matching containers, and "
        "leaves container A's button unchanged, while the same selector "
        "matches both containers page-wide."
    )
    def test_button_root_scopes_locator(self, page: Page) -> None:
        _load_isolated_dom(page)

        action = Button(
            page,
            "[data-test='action']",
            root=page.locator("[data-test='container-b']"),
        )
        container_a_action = page.locator(
            "[data-test='container-a'] [data-test='action']"
        )

        assert page.locator("[data-test='action']").count() == 2, (
            "The action selector must match both containers page-wide"
        )

        action.click()

        action.expect.to_have_text("container-b-clicked")
        action.expect.to_have_attribute("data-state", "clicked")
        expect(container_a_action).to_have_text("container-a-idle")
        expect(container_a_action).to_have_attribute("data-state", "idle")
