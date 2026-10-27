---
name: page-object-creation
description: >-
  Create, extend, or refactor Playwright Page Objects in pages/ and reusable UI
  components in framework/ui/components/. Use when adding page-level actions,
  verified locators, composite components, root-scoped inputs/buttons, or
  iframe handling in the existing pytest framework.
---

# Page Object Creation

## When to use

Use this Skill when a UI scenario needs a new Page Object, a new reusable UI
component, or a change to an existing locator/action. For test scenarios and
assertions, use `writing-ui-tests`. Follow `AGENTS.md` for global rules.

Inspect the actual class before using it. Never invent a constructor, method,
selector, or framework API.

## 1. Existing building blocks

| Class | Location | Contract |
|---|---|---|
| `BasePage` | `framework/ui/base_page.py` | `__init__(page: PageAdapter, base_url: str)`, `PATH`, `open()`, `expect`, `_wait_for_ready()`, `get_iframe_locator()` |
| `PageAdapter` | `framework/ui/page_adapter.py` | Wraps native `Page`: `locator`, `frame_locator`, `goto`, `wait_for_load_state`, `wait_for_url`, `screenshot`, `expect`, `url`, `raw_page` |
| `UiComponent` | `framework/ui/ui_component.py` | `__init__(page: Page, locator: Locator)`, `locator`, `expect` |
| `Input` | `framework/ui/components/input.py` | `Input(page, selector, *, root=None)`, `fill`, `clear`, `input_value` |
| `Button` | `framework/ui/components/button.py` | `Button(page, selector, *, root=None)`, `click(...)` |
| `CheckBox` | `framework/ui/components/checkbox.py` | `CheckBox(page, selector)`, `check`, `uncheck`, `is_checked`, `set_value` |
| `BrowserFactory` | `framework/ui/browser/browser_factory.py` | Session browser and context lifecycle; do not instantiate inside a test |

`PageAdapter.raw_page` exists, but prefer adapter methods. Native `Page` and
`PageAdapter` are not interchangeable: components such as `Input` and
`Button` expect native `Page` and `Locator`.

## 2. Page Objects

Application Page Objects belong in `pages/` and inherit `BasePage`.

```python
class LoginPage(BasePage):
    PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(PageAdapter(page), base_url)
        self.login_form = LoginForm(page)
        ...
```

Rules:

- Use `BasePage.open()` and `_wait_for_ready()` rather than duplicating
  navigation/readiness.
- Compose components; do not duplicate their locators or actions.
- Expose meaningful page-level actions and expectation methods.
- Keep selectors inside the Page Object/component, not in tests.
- Use `snake_case` methods and type annotations; inspect existing return types.

`LoginPage` composes `LoginForm`, exposes field aliases, and wraps the error
message. `DashboardPage` composes `UiComponent` and `Button` elements. Follow
these patterns before inventing new ones.

## 3. UI components

Use `UiComponent` for a general element and `Input`/`Button`/`CheckBox` for
specialized interactions. A composite component belongs in
`framework/ui/components/`.

```python
class LoginForm(UiComponent):
    def __init__(self, page: Page) -> None:
        super().__init__(page, page.locator("form"))
        self.username_input = Input(page, "[data-test='username']", root=self.locator)
        self.password_input = Input(page, "[data-test='password']", root=self.locator)
        self.login_button = Button(page, "[data-test='login-button']", root=self.locator)
```

Rules:

- Pass the native `Page` where the component expects it; scope child locators
  with `root=self.locator` when the selector is not page-unique.
- Keep related locators and interactions in the component.
- Use composition, not unnecessary inheritance.
- Do not extract every single element into a class.
- Do not add a new component directory; use `framework/ui/components/`.

## 4. Locators

Every selector must come from verified evidence:

1. Existing Page Objects/components.
2. Actual application DOM inspected through an available Playwright MCP tool.
3. Application source code.
4. Supplied/verified DOM fragments or test documentation.

Prefer stable `data-test`/`data-testid` attributes, accessible roles/names, or
stable semantic attributes. Use CSS/XPath only when appropriate. Avoid
generated classes, fragile absolute XPath, arbitrary `nth()`/`first()`, and
duplicated selectors.

When a selector matches multiple elements, scope it to a stable parent via
`root`. Do not guess. If DOM inspection is unavailable, report which selectors
remain unverified and do not claim inspection occurred.

Dynamic values belong in method parameters or stable locator construction, not
in duplicated methods for every value.

## 5. Synchronization and iframes

Rely on Playwright auto-waiting and retrying assertions. Use observable
state; do not add `time.sleep()` or global timeout increases to hide races.
`DashboardPage` uses `networkidle` for its existing readiness check; do not
copy that as a universal strategy.

For iframes, use `BasePage.get_iframe_locator()` or
`PageAdapter.frame_locator()`. Confirm whether subsequent locators operate on
`Page` or `FrameLocator`; ordinary page locators do not cross iframe
boundaries.

## 6. Allure

Page Object methods use meaningful `@allure.step` decorations where existing
patterns do (for example `BasePage.open`, `LoginPage.login`,
`DashboardPage.logout`). Do not decorate every locator operation. Never attach
passwords, tokens, session secrets, or sensitive personal data.

## 7. Implementation loop

1. Inspect `BasePage`, `PageAdapter`, `UiComponent`, and similar pages.
2. Reuse existing components and verify method signatures.
3. Choose the minimum file change and verified locators.
4. Implement the component/page method.
5. Check imports and constructor compatibility.
6. Run focused static checks and relevant UI tests.
7. Review the diff and report unverified selectors or blockers.

Example checks, adapted to the changed paths:

```bash
.venv/bin/ruff check pages framework/ui
.venv/bin/python -m pytest tests/ui -q
git diff --check
```

Do not modify `framework/ui` internals merely to support one Page Object
unless the task authorizes it. Do not create placeholder components. If a
browser, `BASE_URL`, or DOM inspection is unavailable,
report that limitation instead of claiming success.
