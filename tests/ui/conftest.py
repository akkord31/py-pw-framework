from __future__ import annotations

import os

import allure
import pytest
from playwright.sync_api import BrowserContext, Page
from collections.abc import Iterator

from framework.ui.browser.browser_factory import BrowserFactory

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    url = os.getenv("BASE_URL")
    if not url:
        raise RuntimeError("BASE_URL is not configured")
    return url


@pytest.fixture(scope="session")
def headless() -> bool:
    return False


@pytest.fixture(scope="session")
def slow_mo() -> int:
    return 0


@pytest.fixture(scope="session")
def browser_factory(headless: bool, slow_mo: int) -> Iterator[BrowserFactory]:
    with BrowserFactory(headless=headless, slow_mo=slow_mo) as factory:
        yield factory


@pytest.fixture(scope="function")
def context(browser_factory: BrowserFactory) -> Iterator[BrowserContext]:
    ctx = browser_factory.new_context("primary")
    try:
        yield ctx
    finally:
        browser_factory.close_context("primary")


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Iterator[Page]:
    p = context.new_page()
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )

    try:
        yield p
    finally:
        trace_path = "/tmp/trace.zip"
        try:
            context.tracing.stop(path=trace_path)
            allure.attach.file(
                trace_path,
                name="playwright-trace",
                attachment_type=allure.attachment_type.ZIP,
            )
        finally:
            p.close()
