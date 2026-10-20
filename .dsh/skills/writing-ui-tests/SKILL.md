---
name: writing-ui-tests
description: >-
  Create, extend and maintain UI automation tests in py-pw-framework
  using Python, pytest, Playwright sync API, Allure and the existing
  Page Object Model. Use for UI scenarios, assertions, fixtures,
  parametrization, regression testing and browser automation.
---

# Writing UI Tests

## Purpose

Implement reliable UI automation tests using the existing
pytest and Playwright framework.

Follow `AGENTS.md` for global project rules.

Related skills:
- `page-object-creation` — Page Objects and UI components.
- `allure-annotations-and-naming` — applicable reporting conventions.
- `triaging-test-failures` — failure investigation.

Always inspect the actual project code before implementation.

Never invent framework methods, fixtures, locators or component APIs.

## 1. Framework Architecture

The project uses a custom Page Object Model.

```text
tests/ui/
    |
    v
pages/
    |
    v
framework/ui/base_page.py
    |
    v
framework/ui/page_adapter.py
    |
    v
Playwright sync API
```

Reusable UI components are implemented using:

```text
framework/ui/
framework/ui/components/
```

Important abstractions:

| Component | Responsibility |
|---|---|
| `BasePage` | Base implementation for Page Objects |
| `PageAdapter` | Abstraction around Playwright Page |
| `UiComponent` | Reusable locator-based UI component |
| `Input` | Text input interactions |
| `Button` | Button interactions |
| `BrowserFactory` | Browser and context management |

Page Objects belong in:

```text
pages/
```

Tests must interact with the application through Page Objects.

Do not duplicate Playwright operations already encapsulated
by the framework.

## 2. Native Page vs PageAdapter

The pytest `page` fixture returns a native Playwright `Page`.

Page Objects may use `PageAdapter` internally.

These types are not interchangeable.

Before implementing a test:

1. Inspect the Page Object constructor.
2. Inspect `BasePage`.
3. Inspect `PageAdapter`.
4. Verify how native Playwright objects are wrapped.
5. Use the existing public interface.

Existing project usage:

```python
login_page = LoginPage(page, base_url)
```

Do not assume `PageAdapter` exposes every native Playwright method.

Do not invent adapter attributes such as `raw_page`.

Use the project's existing access mechanism.

## 3. Test Organization

Follow existing neighboring tests.

The current project uses feature-oriented test classes.

Example:

```python
class TestLogin:
    def test_valid_login(self, page, base_url):
        ...
```

Rules:

- Group related tests into `Test<Feature>` classes.
- Name methods `test_<expected_behavior>`.
- Use clear, descriptive test names.
- Keep each test focused on one meaningful scenario.
- Use pytest fixtures for setup and teardown.
- Do not introduce new directory structures unnecessarily.
- Do not restructure existing tests without authorization.

Example structure:

```text
tests/
    ui/
        test_login.py
```

Before creating a new file or test method,
check that it does not already exist.

Do not duplicate scenarios.

## 4. Browser Fixtures

The project provides browser-management fixtures.

| Fixture | Scope | Purpose |
|---|---|---|
| `base_url` | session | Application URL from `BASE_URL` |
| `headless` | session | Browser headless configuration |
| `slow_mo` | session | Playwright interaction delay |
| `browser_factory` | session | BrowserFactory lifecycle |
| `context` | function | Isolated BrowserContext |
| `page` | function | Native Playwright Page |

Verify the current implementation in `conftest.py`.

Use existing fixtures rather than creating browsers manually.

Do not call `sync_playwright().start()` inside ordinary tests
when the framework already manages Playwright.

### Browser contexts

A BrowserContext provides isolated browser state.

Different contexts have separate:

- Cookies
- Local storage
- Session-related browser state

Multiple pages inside one context may share cookies
and local storage for the same origin.

Session storage is generally scoped to an individual
top-level browsing context.

Do not create additional contexts without a test requirement.

### Tracing

The existing `page` fixture starts Playwright tracing with:

- Screenshots
- DOM snapshots
- Sources

During teardown, traces are saved and attached to Allure.

Do not duplicate tracing logic inside tests.

Known framework limitation:

```text
/tmp/trace.zip
```

The fixed trace path may cause collisions in parallel execution.

When modifying tracing, prefer unique paths per test,
but do not change the fixture without authorization.

## 5. Test Implementation

Each test must contain:

1. Preconditions.
2. User actions.
3. Expected behavior.
4. Assertions.
5. Cleanup when required.

Tests should describe business scenarios,
not low-level browser implementation details.

Good:

```python
login = LoginPage(page, base_url).open()

login.login(username, password)
login.expect_error_visible()
```

Avoid:

```python
page.locator("#user-name").fill(username)
page.locator("#password").fill(password)
page.locator("#login-button").click()
```

Raw Playwright operations belong in Page Objects
or UI components, not ordinary test methods.

The selectors above are illustrative only.
Use verified project locators.

## 6. Page Object Usage

Use existing public Page Object methods.

Before invoking a method:

1. Confirm that it exists.
2. Check its parameters.
3. Check its return value.
4. Check whether it performs assertions.
5. Check whether it changes the current page.

Example:

```python
login = LoginPage(page, base_url).open()
login.login(username, password)
login.expect_error_visible()
```

For successful login, use the actual application Page Object
and its verified navigation/assertion methods.

Do not assume that `open()` or `login()` returns a particular
type without inspecting the implementation.

### Missing Page Object methods

When a required interaction is missing:

1. Inspect existing Page Objects.
2. Inspect reusable UI components.
3. Verify the actual DOM or existing locators.
4. Add a focused public method when necessary.
5. Follow `page-object-creation`.

Do not bypass the Page Object layer as a shortcut.

## 7. UI Assertions

Prefer Playwright's retrying assertions
for asynchronous UI state.

Examples:

```python
from playwright.sync_api import expect

expect(locator).to_be_visible()
expect(locator).to_have_text("Expected text")
expect(locator).to_be_enabled()
```

Use these inside the appropriate Page Object
or component when the architecture supports it.

Test methods should express expected behavior
using the Page Object's public verification API.

### Meaningful assertions

Verify:

- Successful or failed navigation.
- Expected messages.
- Visibility and disappearance.
- Field values.
- Enabled/disabled state.
- Changes after user interaction.
- Application state relevant to the scenario.

Do not consider a test successful merely because
a click completed without raising an exception.

Every relevant expected result must be verified.

### URL assertions

Use native Playwright assertions or existing wrappers.

Example:

```python
expect(page).to_have_url(
    re.compile(r"/inventory\.html$")
)
```

Import `re` when needed.

Never invent methods such as `expect_url_contains`
without checking the framework.

## 8. Synchronization

Prefer Playwright's built-in auto-waiting.

Use:

- Locator actions.
- Retrying assertions.
- Observable UI state.
- Existing framework waiting methods.

Avoid:

```python
time.sleep(5)
```

Do not add arbitrary delays to hide flaky behavior.

### Loading indicators

When a loading indicator exists:

1. Verify its actual locator.
2. Understand the loading lifecycle.
3. Wait for the relevant condition.
4. Assert the resulting state.

Do not assume every delayed element indicates a loading issue.

### Element interaction failures

Investigate:

- Locator uniqueness.
- Element visibility.
- Element stability.
- Disabled state.
- Overlapping elements.
- Navigation in progress.
- Iframes.
- Detached DOM elements.

Do not immediately increase global timeouts.

## 9. Locators

Tests must not contain application selectors.

Locators belong in Page Objects or components.

Preferred approaches:

- Stable test IDs.
- Accessible roles and names.
- Stable semantic attributes.
- CSS selectors where appropriate.
- XPath when justified.

Avoid:

- Generated class names.
- Fragile absolute XPath.
- Unnecessary `.nth()`.
- Arbitrary `.first()`.
- Duplicated selectors.

Verify selectors from:

1. Existing project code.
2. Actual application DOM.
3. Playwright MCP when connected.
4. Application source code when available.

Never invent selectors.

## 10. Test Data

Use existing fixtures and configuration.

Do not hardcode:

- Passwords.
- API tokens.
- Production credentials.
- Sensitive user information.

Use `.env` through established project configuration.

Use test-specific data that is:

- Predictable.
- Reproducible.
- Independent.
- Safe to modify.

Clean up persistent data created by tests.

Do not depend on another test running first.

## 11. Parametrization

Use `pytest.mark.parametrize` for input variations
with the same workflow and assertion structure.

Example:

```python
@pytest.mark.parametrize(
    "username",
    ["invalid_user", "locked_out_user"],
    ids=["invalid-user", "locked-out-user"],
)
def test_login_rejected(self, page, base_url, username):
    ...
```

Use valid project test data and verify expected behavior.

Do not combine unrelated scenarios.

Prefer separate tests when:

- Actions differ.
- Preconditions differ significantly.
- Expected behavior differs.
- Scenarios represent distinct functionality.

Use descriptive parameter IDs when helpful.

## 12. Test Isolation

Tests should run independently whenever possible.

Rules:

- Do not rely on execution order.
- Do not share mutable state unnecessarily.
- Do not reuse browser contexts across unrelated tests.
- Restore modified persistent data.
- Avoid global mutable test variables.
- Consider pytest-xdist compatibility.

When parallel execution reveals flaky behavior,
investigate isolation before adding retries.

Do not suppress failures using arbitrary retries.

## 13. Allure Reporting

Follow the project's existing reporting conventions.

Relevant annotations include:

```python
@allure.feature("Login")
@allure.story("Authentication")
@allure.title("Invalid credentials are rejected")
```

Use meaningful titles that describe expected behavior.

Use `@allure.step` for meaningful operations
when appropriate to existing project patterns.

Do not add redundant reporting around every locator action.

Do not introduce reporting helpers from unrelated frameworks.

**Important:** This framework's UI tests do not automatically
require `step_num` or `check_step` fixtures.

Use such helpers only if they actually exist and are required
by the current project.

Never attach passwords or tokens to Allure.

## 14. Pytest Markers

Use markers registered in the project.

Typical markers include:

```python
@pytest.mark.ui
@pytest.mark.smoke
```

Rules:

- Apply `ui` according to existing conventions.
- Use `smoke` for smoke scenarios only.
- Verify marker registration in project configuration.
- Do not invent Jira task markers.
- Do not copy markers from unrelated test frameworks.

Use module-level or class-level markers
when appropriate to the existing test structure.

## 15. Playwright MCP

Use Playwright MCP for live browser inspection
when connected to DeepSeek Harness.

Useful tasks:

- Inspecting page structure.
- Verifying actual selectors.
- Reproducing UI defects.
- Investigating flaky tests.
- Checking user interactions.
- Confirming navigation.

Before invoking MCP:

1. Check which tools are available.
2. Confirm the browser can access the application.
3. Use actual supported tool names.
4. Inspect the live DOM when needed.
5. Record unverified assumptions.

Do not assume that MCP is connected
because the project previously used it.

Do not claim browser verification without executing it.

## 16. Failures and Blocked Tests

Investigate failures before changing expectations.

Use `triaging-test-failures` when appropriate.

Distinguish:

- Automation defects.
- Application bugs.
- Invalid test data.
- Environment issues.
- Outdated requirements.

Do not modify assertions merely to make tests green.

### Skipping tests

Use `pytest.skip` for legitimate missing runtime data.

Use `pytest.mark.skip` for documented blockers.

Use `pytest.mark.xfail` for understood, documented
expected failures.

Never hide an unexplained failure with `skip` or `xfail`.

Do not create placeholder tests containing only:

```python
pass
```

or:

```python
...
```

Never silently omit required assertions.

## 17. Implementation Workflow

### Before implementation

1. Read `AGENTS.md`.
2. Inspect the existing test module.
3. Inspect relevant fixtures in `conftest.py`.
4. Inspect Page Objects and UI components.
5. Verify the required test data.
6. Confirm expected application behavior.
7. Identify the smallest necessary change.

### During implementation

1. Reuse existing fixtures.
2. Use verified Page Object constructors.
3. Keep actions and assertions meaningful.
4. Reuse UI components.
5. Add focused Page Object methods when necessary.
6. Use Playwright auto-waiting.
7. Keep tests independent.
8. Avoid unrelated refactoring.

### After implementation

1. Verify imports and method signatures.
2. Confirm all referenced methods exist.
3. Run relevant static checks.
4. Run targeted pytest tests.
5. Inspect Allure evidence when needed.
6. Investigate failures.
7. Review the Git diff.
8. Report the actual result.

Example commands:

```bash
git diff --check
ruff check tests/ pages/ framework/
pytest tests/ui/ -q
```

Run these only when the corresponding tools
and paths exist in the current repository.

Do not claim successful validation if execution was blocked.

## 18. Completion Criteria

The implementation is complete when:

- [ ] Existing framework architecture is respected.
- [ ] Tests use Page Objects.
- [ ] All Page Object methods are verified.
- [ ] No selectors are invented.
- [ ] Fixtures are reused.
- [ ] All expected outcomes are asserted.
- [ ] Test data is isolated.
- [ ] No arbitrary sleeps are introduced.
- [ ] Allure annotations follow project conventions.
- [ ] Relevant pytest markers are applied.
- [ ] Tests run successfully when the environment permits.
- [ ] Failures and blockers are reported.
- [ ] No unrelated files were modified.

## Restrictions

- Never invent framework methods or fixtures.
- Never bypass Page Objects without justification.
- Never modify unrelated framework code.
- Never hardcode credentials.
- Never hide failures.
- Never claim tests passed without execution evidence.
- Never introduce unnecessary abstractions.
- Never commit or push without explicit authorization.