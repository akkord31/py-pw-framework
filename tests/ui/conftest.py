from __future__ import annotations

import allure
import pytest
from playwright.sync_api import BrowserContext, Page

from framework.ui.browser.browser_factory import BrowserFactory


@pytest.fixture(scope="session")
def browser_factory(headless: bool, slow_mo: int) -> BrowserFactory:
    with BrowserFactory(headless=headless, slow_mo=slow_mo) as factory:
        yield factory


@pytest.fixture(scope="function")
def context(browser_factory: BrowserFactory) -> BrowserContext:
    ctx = browser_factory.new_context()
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    p = context.new_page()

    # attach Playwright traces for Allure on failure
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield p

    # save trace as Allure attachment on failure
    trace_path = "/tmp/trace.zip"
    context.tracing.stop(path=trace_path)
    allure.attach.file(
        trace_path,
        name="playwright-trace",
        attachment_type=allure.attachment_type.ZIP,
    )

    p.close()
