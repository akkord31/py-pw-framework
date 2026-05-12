from __future__ import annotations

from typing import Optional

from playwright.sync_api import Page

from framework.ui.ui_component import UiComponent


class Button(UiComponent):
	def __init__(self, page: Page, selector: str) -> None:
		super().__init__(page, page.locator(selector))

	def click(
			self,
			*,
			modifiers=None,
			position=None,
			delay: Optional[float] = None,
			button=None,
			click_count: Optional[int] = None,
			timeout: Optional[float] = None,
			force: Optional[bool] = None,
			trial: Optional[bool] = None,
	) -> None:
		self.locator.click(
			modifiers=modifiers,
			position=position,
			delay=delay,
			button=button,
			click_count=click_count,
			timeout=timeout,
			force=force,
			trial=trial,
		)
