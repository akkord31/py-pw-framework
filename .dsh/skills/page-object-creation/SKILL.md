---
name: page-object-creation
description: >-
  Create, extend and refactor Playwright Page Objects and UI components.
  Use when implementing new pages, locators, reusable UI elements or
  page-level interactions in the existing Python pytest framework.
---

# Page Object Creation

## Purpose

Create maintainable Page Objects and reusable UI components
using the existing Python, pytest and Playwright sync API architecture.

Follow `AGENTS.md` for global project rules.

Related skills:
- `writing-ui-tests` — UI test implementation.
- `allure-annotations-and-naming` — reporting conventions.
- `triaging-test-failures` — investigation of UI failures.

Never invent framework interfaces, component methods or selectors.

## 1. Framework Architecture

The project uses:

| Component | Location | Responsibility |
|---|---|---|
| `BasePage` | `framework/ui/base_page.py` | Base class for Page Objects |
| `PageAdapter` | `framework/ui/page_adapter.py` | Playwright page abstraction |
| `UiComponent` | `framework/ui/ui_component.py` | Base UI component wrapper |
| `Input` | `framework/ui/components/input.py` | Input interactions |
| `Button` | `framework/ui/components/button.py` | Button interactions |
| `BrowserFactory` | `framework/ui/browser/browser_factory.py` | Browser and context management |

Before implementation, read the actual definitions.

Do not assume that methods available in native Playwright
are automatically exposed through `PageAdapter`.

### PageAdapter

Use `PageAdapter` for page-level browser operations
supported by its current interface.

Examples of responsibilities:

- Navigation
- Page load handling
- Locator access
- Frame or iframe interactions
- Browser page operations

Inspect the adapter before calling a method.

If a native Playwright `Page` or `Locator` is required,
use the existing access mechanism exposed by the adapter.

Do not assume `raw_page` exists without verifying it.

Do not modify `PageAdapter` merely to support one Page Object
unless explicitly authorized.

### BasePage

Application Page Objects inherit from `BasePage`.

Follow its actual constructor contract.

The project convention uses `PageAdapter` and `base_url`,
but inspect `BasePage.__init__` before instantiation.

Reuse inherited methods rather than duplicating navigation,
waiting or locator functionality.

### UiComponent

Use `UiComponent` and existing specialized components
to encapsulate element interactions.

Before creating a component, inspect:

- Its constructor arguments.
- Its expected `Page` or `Locator` type.
- Its public methods.
- Its waiting behavior.
- Its assertion methods.

Do not pass `PageAdapter` to an API expecting native `Page`
unless the existing framework explicitly supports it.

## 2. File Structure

Application Page Objects belong in:

```text
pages/
```

Naming conventions:

```text
login_page.py
settings_page.py
users_page.py
```

Class names:

```python
LoginPage
SettingsPage
UsersPage
```

Reusable UI components belong in the appropriate existing
component directory.

Inspect the project structure before choosing the location.

Do not create a new directory or abstraction layer
when an existing one is suitable.

## 3. Page Objects vs UI Components

### Page Object

Represents a page or meaningful application boundary.

Responsibilities:

- Page-specific locators.
- Page navigation.
- User-facing actions.
- Page-level state checks.
- Composition of UI components.

### UI Component

Represents a reusable or logically independent part of the UI.

Examples:

- Login form.
- Navigation menu.
- Modal dialog.
- Search panel.
- Table.
- Date picker.

Use an existing component when possible.

Create a new component when it meaningfully encapsulates
related elements or reusable behavior.

Do not extract every button or input into a separate class
unless the project architecture requires it.

## 4. Locator Rules

**All selectors must come from verified evidence.**

Acceptable sources:

1. Existing Page Objects.
2. Existing UI components.
3. Actual application DOM inspected through Playwright MCP.
4. Application source code.
5. Verified test documentation.

Never invent selectors.

### Preferred locator strategies

Choose stable selectors appropriate for the application:

1. Test-specific attributes such as `data-testid`.
2. Accessible roles and names.
3. Stable IDs and semantic attributes.
4. CSS selectors.
5. XPath when necessary.

This is a preference, not a mandatory hierarchy.

Prefer the most reliable selector available.

### Avoid

- Randomly generated classes or IDs.
- Fragile DOM hierarchies.
- Unnecessary positional selectors.
- Arbitrary `nth()` calls.
- Duplicated locators.
- CSS/XPath scattered throughout test functions.
- Hardcoded dynamic values.

When a locator matches multiple elements, scope it
to a stable parent or container.

Use `.first()` or `.nth()` only when the position
is meaningful and justified.

### Dynamic locators

Use parameterized Page Object methods.

Example:

```python
def get_user_row(self, username: str):
    ...
```

Build locators from stable identifiers.

Do not duplicate methods for every possible username,
host, database or table row.

## 5. UI Components

Prefer specialized wrappers:

- `Input` for text fields.
- `Button` for buttons.
- `UiComponent` for general elements.
- Existing specialized components when available.

Do not bypass a component's public API without a reason.

For composite components:

- Keep related locators together.
- Encapsulate meaningful interactions.
- Avoid duplicating parent Page Object logic.
- Use composition rather than unnecessary inheritance.

Example design:

```text
LoginPage
    └── LoginForm
          ├── username: Input
          ├── password: Input
          └── submit: Button
```

This diagram describes responsibilities, not constructor syntax.

Use actual project constructors and verified locators.

## 6. Page Object Methods

Methods should describe application behavior.

Prefer:

```python
login(username, password)
open_user_details(username)
select_role(role_name)
```

Over low-level methods that require tests to coordinate
multiple internal components unnecessarily.

Rules:

- Use descriptive `snake_case` names.
- Apply type annotations.
- Return meaningful values where appropriate.
- Keep methods focused on one action or responsibility.
- Reuse existing component methods.
- Avoid unnecessary side effects.
- Do not duplicate inherited functionality.

Separate actions from verification where practical.

Use Playwright assertions or existing component assertion methods
for state verification.

Never implement a method using a framework API
that has not been inspected.

## 7. Synchronization

Playwright provides automatic waiting for many interactions.

Prefer:

- Locator-based interaction.
- Playwright assertions.
- Existing framework waiting methods.
- Explicit condition-based waits when necessary.

Avoid:

```python
time.sleep(5)
```

Do not use arbitrary delays to fix flaky tests.

Do not use `networkidle` as a universal readiness strategy.

### Loading indicators

If the application displays a loading indicator:

1. Confirm its actual selector.
2. Identify when loading begins and ends.
3. Wait for the relevant observable state.
4. Avoid adding redundant waits.

### Dynamic content

Use conditions that reflect the application state:

- Element becomes visible.
- Element disappears.
- Attribute changes.
- Expected text appears.
- URL changes.
- Loading completes.

Respect the project's existing timeout configuration.

Do not increase global timeouts to hide a specific defect.

## 8. Iframes

Use the existing `PageAdapter` iframe mechanism
when available.

Before implementing iframe interactions:

1. Inspect `PageAdapter`.
2. Identify the actual iframe.
3. Confirm whether locators operate on `Page` or `FrameLocator`.
4. Reuse the existing abstraction.
5. Avoid creating separate iframe-handling mechanisms.

Do not assume that a locator from the main document
can locate elements inside an iframe.

## 9. Playwright MCP

Use Playwright MCP when available and relevant.

### Inspection workflow

1. Navigate to the target application.
2. Inspect the accessible page structure.
3. Identify target elements.
4. Verify locator uniqueness.
5. Check visibility and interaction states.
6. Implement using the existing framework.

Do not invent MCP tool names.

Inspect the tools actually available in the Harness session.

### If MCP is unavailable

Use:

- Existing Page Objects.
- Application source.
- Verified documentation.
- Supplied DOM fragments.

Clearly report which selectors remain unverified.

Do not claim that DOM inspection was performed.

Never perform destructive operations or expose credentials
during inspection without authorization.

## 10. Allure

Follow `allure-annotations-and-naming`.

Page-level Allure steps should describe meaningful behavior.

Avoid logging every internal locator operation.

Never attach:

- Passwords.
- Tokens.
- Session secrets.
- Sensitive personal data.

Do not add unnecessary decorators to every component method.

## 11. Implementation Workflow

### Before implementation

1. Read `AGENTS.md`.
2. Inspect `BasePage` and `PageAdapter`.
3. Inspect `UiComponent`, `Input` and `Button`.
4. Review similar Page Objects.
5. Identify reusable abstractions.
6. Verify actual selectors.
7. Determine the minimum required file changes.

### During implementation

1. Follow existing constructors.
2. Reuse existing components.
3. Encapsulate stable locators.
4. Implement meaningful methods.
5. Use Playwright synchronization.
6. Avoid unrelated refactoring.
7. Do not modify framework internals without authorization.

### After implementation

1. Check imports.
2. Check constructor compatibility.
3. Confirm component methods exist.
4. Check locator uniqueness when possible.
5. Run relevant static checks.
6. Run targeted UI tests when possible.
7. Review the diff.

Example:

```bash
git diff --check
ruff check pages/ framework/ui/
pytest tests/ui_tests/ -q
```

Use only commands supported by the actual repository.

Do not assume every example path or tool is configured.

## 12. Completion Criteria

The implementation is complete when:

- [ ] It follows `BasePage` and `PageAdapter` contracts.
- [ ] Existing components are reused.
- [ ] Locators are verified or explicitly identified as unverified.
- [ ] No framework APIs were invented.
- [ ] No arbitrary sleeps were introduced.
- [ ] No unrelated files were modified.
- [ ] Imports and static checks pass.
- [ ] Targeted tests were executed when possible.
- [ ] Remaining blockers are documented.

## Restrictions

- Never invent selectors.
- Never invent component methods.
- Never bypass existing abstractions without justification.
- Never hardcode credentials.
- Never modify application source code.
- Never introduce unnecessary dependencies.
- Never claim successful execution without evidence.
- Never commit or push without explicit authorization.