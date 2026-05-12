from __future__ import annotations

from typing import Any, Literal

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright

BrowserName = Literal["chromium", "firefox", "webkit"]


class BrowserFactory:
    def __init__(
        self,
        browser_name: BrowserName = "chromium",
        headless: bool = True,
        slow_mo: int = 0,
    ) -> None:
        self._browser_name = browser_name
        self._headless = headless
        self._slow_mo = slow_mo
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: dict[str, BrowserContext] = {}

    def start(self) -> "BrowserFactory":
        self._playwright = sync_playwright().start()
        engine = getattr(self._playwright, self._browser_name)
        self._browser = engine.launch(
            headless=self._headless,
            slow_mo=self._slow_mo,
        )
        return self

    def stop(self) -> None:
        for ctx in self._contexts.values():
            ctx.close()
        self._contexts.clear()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def new_context(
        self,
        name: Literal["primary", "secondary"] = "primary",
        **kwargs: Any,
    ) -> BrowserContext:
        assert self._browser, "Call start() first"

        if name in self._contexts:
            raise RuntimeError(f"Context {name!r} already exists, close it first")

        defaults: dict[str, Any] = {
            "viewport": {"width": 1920, "height": 1080},
            "locale": "en-US",
            "ignore_https_errors": True,
        }
        defaults.update(kwargs)

        ctx = self._browser.new_context(**defaults)
        self._contexts[name] = ctx
        return ctx

    def get_context(self, name: Literal["primary", "secondary"] = "primary") -> BrowserContext:
        if name not in self._contexts:
            raise RuntimeError(f"Context {name!r} not found, call new_context() first")
        return self._contexts[name]

    def close_context(self, name: Literal["primary", "secondary"]) -> None:
        ctx = self._contexts.pop(name, None)
        if ctx:
            ctx.close()

    def __enter__(self) -> "BrowserFactory":
        return self.start()

    def __exit__(self, *_: Any) -> None:
        self.stop()
