---
name: writing-ui-tests
description: >-
  Implement and maintain pytest + Playwright Sync UI tests in tests/ui/ using
  the existing LoginPage/DashboardPage Page Objects, BrowserFactory fixtures,
  reusable components, and Allure reporting. Use for new UI scenarios,
  regressions, assertions, parametrization, and UI test fixes.
---

# Writing UI Tests

## When to use

Use this Skill when adding or changing a UI test under `tests/ui/`, or when a
UI scenario needs a new Page Object/component. Use `page-object-creation` for
the Page Object/component work, and `allure-annotations-and-naming` for test
metadata.

Follow `AGENTS.md` for global rules. Inspect the current test module, Page
Object, and fixture before editing.

## 1. Test architecture

```text
tests/ui/            pytest tests (class-based)
    |
pages/               LoginPage, DashboardPage
    |
framework/ui/        BasePage, PageAdapter, UiComponent,
                     components/, BrowserFactory
    |
Playwright Sync API
```

Rules:

- UI tests are class-based (`TestLogin`, `TestComponentScoping`). Preserve
  that style; do not convert existing UI tests to module-level functions.
- Tests interact through Page Objects/components. Do not put application
  selectors or raw browser flows in scenario test methods.
- `page` is a native Playwright `Page`. Page Objects may wrap it in
  `PageAdapter`. These types are not interchangeable.
- Keep the existing directory and test organization. Do not create a parallel
  test tree or a new abstraction layer.

## 2. Fixtures

`tests/ui/conftest.py` provides:

| Fixture | Scope | Purpose |
|---|---|---|
| `base_url` | session | `BASE_URL` from environment; raises if missing |
| `headless` | session | Browser headless setting (currently `False`) |
| `slow_mo` | session | Playwright slow-motion setting |
| `browser_factory` | session | `BrowserFactory` lifecycle |
| `context` | function | Isolated primary `BrowserContext` |
| `page` | function | Native Playwright `Page`; starts/stops tracing |

Reuse these fixtures. Do not call `sync_playwright().start()`, create an
independent browser, or duplicate trace setup in a test. Contexts are closed
by the fixture; do not close the shared browser yourself.

The `page` fixture writes a trace to `/tmp/trace.zip` and attaches it to
Allure. The fixed path can collide under parallel execution; do not change
the fixture unless the task explicitly requires it.

## 3. Page Object usage

Use existing public methods and inspect their contracts first.

```python
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

login = LoginPage(page, base_url).open()
login.login("standard_user", "secret_sauce")
login.expect_error_visible()

dashboard = DashboardPage(page, base_url)
dashboard.expect.to_have_url(re.compile(r"/inventory\.html$"))
dashboard.expect_logon()
```

- `LoginPage` composes `LoginForm`; it exposes `username_input`,
  `password_input`, `login_button`, `error_message`, `login()`, and
  expectation methods.
- `DashboardPage` exposes `app_logo`, `user_menu`, `logout_button`, `logout()`,
  and `expect_logon()`.
- `BasePage.open()` navigates using `PATH` and `base_url`, calls
  `_wait_for_ready()`, and returns the page object.
- `BasePage.expect` delegates to Playwright page assertions. `PageAdapter`
  also exposes `expect`, `url`, `locator`, `frame_locator`, `goto`,
  `wait_for_load_state`, `wait_for_url`, `screenshot`, and an explicit
  `raw_page` escape hatch.

If an interaction is missing, add a focused public Page Object method using
`page-object-creation`; do not bypass the Page Object layer.

## 4. Test implementation

A UI test should state a precondition, perform the user action through Page
Objects, and assert the observable outcome. Example structure:

```python
@allure.feature("Authentication")
@allure.story("UI Login")
@pytest.mark.ui
class TestLogin:
    @allure.title("Successful login redirects to dashboard")
    @pytest.mark.smoke
    def test_login_success(self, page: Page, base_url: str) -> None:
        login = LoginPage(page, base_url).open()
        login.login("standard_user", "secret_sauce")

        dashboard = DashboardPage(page, base_url)
        dashboard.expect.to_have_url(re.compile(r"/inventory\.html$"))
        dashboard.expect_logon()
```

Keep each test focused on one meaningful scenario. Check existing modules
first and do not duplicate a scenario, file, or test function name. Preserve
existing return annotations and neighboring style.

## 5. Assertions

Prefer retrying Playwright assertions over boolean checks:

```python
login.expect_error_visible()
login.expect_error("Epic sadface: Username and password do not match")
dashboard.expect_logon()
```

Use native `expect` for page-level state when the Page Object does not wrap it:

```python
from playwright.sync_api import expect

expect(page).to_have_url(re.compile(r"/inventory\.html$"))
```

Every documented expected result must have an assertion. Do not treat a
completed click, a non-raising call, or `locator.count() > 0` as proof of
behavior. Do not assert only that an element exists when visibility, text,
state, or navigation is the requirement.

## 6. Synchronization and locators

Rely on Playwright auto-waiting and retrying assertions. Use observable
state: visibility, text, attributes, URL, enabled/disabled state, or
navigation.

Avoid:

- `time.sleep()`
- arbitrary retry loops
- increasing global timeouts to hide a race
- `networkidle` as a universal readiness strategy

Verified selectors belong in Page Objects/components. Use existing selectors
or inspect the actual DOM/application source. Do not invent selectors or
claim DOM inspection without performing it. If Playwright MCP is connected,
verify its actual tools and use it only for inspection; otherwise use
repository evidence or supplied DOM fragments.

## 7. Test data and isolation

- Use `BASE_URL` and existing environment configuration; never hardcode
  credentials, tokens, or production personal data.
- Use deterministic test data and clean up persistent state created by a test.
- Do not depend on execution order or share mutable state between tests.
- Do not create an extra context unless the scenario needs isolated browser
  state.
- Keep tests independent; parallel tooling is not declared, so do not claim
  parallel behavior or add parallel-specific markers.

## 8. Parametrization

Use `@pytest.mark.parametrize` only for variants with the same workflow and
assertion structure:

```python
@pytest.mark.parametrize(
    "username",
    ["invalid_user", "locked_out_user"],
    ids=["invalid-user", "locked-out-user"],
)
def test_login_rejected(self, page: Page, base_url: str, username: str) -> None:
    ...
```

Do not merge scenarios with different actions, preconditions, expected
results, or business meaning. Separate cases remain separate tests.

## 9. Markers and Allure

Use markers registered in `pytest.ini`: `ui`, `api`, `smoke`, `regression`.
Apply `ui` to UI test classes/modules consistently; use `smoke` only for
smoke scenarios. Do not invent Jira, auth, or functionality markers.

For new or updated tests, apply `allure-annotations-and-naming`. This project
does not use `@allure.severity` or project-specific step fixtures.

## 10. Failures and blocked scenarios

Investigate a failure before changing expectations. Distinguish automation
defects, application defects, invalid data, environment problems, and
outdated requirements; load `triaging-test-failures` for deeper analysis.

- Do not weaken assertions or delete coverage to get green.
- Use `pytest.skip` only for a verified runtime blocker; use
  `pytest.mark.skip(reason=...)` for a documented blocker.
- Use `pytest.mark.xfail` only for a understood, documented expected failure.
- Do not leave placeholder tests or silently omit an approved scenario.

## 11. Verification

Run focused checks from the repository root:

```bash
.venv/bin/python -m pytest tests/ui/test_login.py -q
.venv/bin/python -m pytest tests/ui -q
.venv/bin/ruff check tests/ui pages framework/ui
git diff --check
```

Adapt paths to the changed test. Report the exact command, exit code, and
result. If the browser, `BASE_URL`, network, or display is unavailable,
report the check as unavailable rather than passed.
