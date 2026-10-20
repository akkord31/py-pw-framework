---
name: allure-annotations-and-naming
description: >-
  Use when creating or updating pytest tests to apply the project requirements for
  Allure titles, descriptions, links, step numbering, test names and markers.
---

# Allure Annotations and Naming

> Follow `AGENTS.md` for all global rules. This skill is the checklist for annotations.

> **Terminology — "source code" = the application source code.**
> In any prompt or request, "source code" means the application source
> (read-only, branch `develop`), not this automation repository.
> See `AGENTS.md` → Application source vs. automation code.

## Test naming

### UI tests

- **From a Jira test case:** `test_{case}`
  - `{case}` = Jira case number (`2936` → `2936`).
  - No description in the function name — readable text belongs in `@allure.title`.
  - One test covering several sub-cases joins the numbers with `_`.
  - Example: `test_2936_1`.

- **From a spec / wiki (no Jira case):** `test_{testing_functionality}`
  - Use a short functionality slug without a case number.
  - Example: `test_navbar_items_present`.

### API tests

- `test_{micro_service}_{endpoint}_{info?}_{pos|neg}`
  - Name the test after the functionality being exercised, not its Jira ID.
  - `{info}` is optional.
  - `{pos|neg}` is required.
  - `pos` means a positive scenario.
  - `neg` means a negative scenario.

Examples:

```python
def test_auth_login_pos():
    ...

def test_auth_login_neg():
    ...

def test_pms_spells_general_pos():
    ...
```

Before creating a new test, perform two duplication checks:

1. Verify that the target directory does not already contain a test file with the same name.
   Never overwrite an existing `test_*.py` file. Extend it when appropriate.

2. Verify that the target module does not already contain a test function with the same name.
   Choose another scenario number, slug or optional `{info}` segment if necessary.

Test functions must not have return type annotations.

## Module-level metadata (`pytestmark`)

Declare annotations and markers shared by every test in a module once, at module level.

```python
import allure
import pytest

pytestmark = [
    allure.feature("Letter View page"),
    pytest.mark.ui,
    pytest.mark.regress,
]
```

Move the following shared annotations to `pytestmark`:

- `allure.feature`
- `pytest.mark.ui` or `pytest.mark.api`
- `pytest.mark.smoke` or `pytest.mark.regress`
- Shared functionality markers
- Shared Jira task markers

Keep annotations that vary between tests on individual functions:

- `@allure.testcase`
- `@allure.title`
- `@allure.description`
- `@pytest.mark.parametrize`
- `@pytest.mark.skip`
- `@pytest.mark.auth`

If `allure.feature` differs between tests in the same module, apply it individually.

## Required annotations

Every test must include its own title and description.

For case-driven tests, include the Jira/Zephyr test-case reference.

```python
import allure
import pytest

pytestmark = [
    allure.feature("Organisation items"),
    pytest.mark.api,
]


@allure.title("123-1: Full test case title from Jira")
@allure.description(
    "Brief description of the functionality being tested."
)
@allure.testcase(
    "https://example.atlassian.net/browse/123",
    "123-1",
)
@pytest.mark.smoke
@pytest.mark.auth("nonai_doc")
def test_123_1(page, step_num):
    ...
```

### `@allure.title`

For Jira/Zephyr case-driven tests:

- Start with the TMS identifier: `###-<sub>:`.
- Follow it with the full test-case title.
- Preserve the source's meaning and expected behavior.
- If a test covers several sub-cases, join their identifiers with `-`.

Examples:

```python
@allure.title("2936-1: One metadata setting ON - Edit button is present")
```

```python
@allure.title("2936-8-9-10: Verify supported metadata configurations")
```

Tests must not contain function docstrings.

The readable title belongs in `@allure.title`, and the functionality description belongs in `@allure.description`.

### `@allure.description`

Required for every test:

- Case-driven tests
- Spec-driven tests
- Development-task-driven tests

The description must explain the functionality being verified.

Store additional test information in `@allure.description` rather than a function docstring.

### `@allure.testcase`

Use only when a real Jira/Zephyr test case exists.

```python
@allure.testcase(
    "https://example.atlassian.net/browse/2936",
    "2936-12",
)
```

Rules:

- Inline the complete URL.
- Do not hide it behind a module-level constant.
- Include the scenario sub-number.
- For combined sub-cases, join identifiers with `-`.
- Respect the `.flake8` line-length limit of 120 characters.

### No Jira/Zephyr test case

When the task has no test-case reference:

- Do not use `@allure.testcase`.
- Use `@allure.link` instead.

Use:

- `name="Spec"` for a Confluence specification.
- `name="Dev task"` for a Jira development task.

## Spec-driven tests

When tests are based on a Confluence specification rather than Jira/Zephyr test cases, use:

- `@allure.title` without a TMS identifier.
- `@allure.description` with a functionality summary.
- `@allure.link` pointing to the original specification.

Example:

```python
import allure


@allure.title("PMS spells catalogue conforms to the spell schema")
@allure.description(
    "PMS exposes the Cast Spell catalogue through "
    "GET /api/author/pms/spells/general and verifies "
    "that every entry matches the expected schema."
)
@allure.link(
    "https://example.atlassian.net/wiki/spaces/pages/151519234",
    name="Spec",
)
def test_pms_spells_general_pos(templates_api, step_num, check_step):
    ...
```

Rules:

- Inline the full Confluence URL.
- Do not use a module-level `SPEC_URL` constant.
- Do not invent a Jira test-case identifier.
- Use the application's actual specification and endpoint information.
- When requests go through the project service layer, reuse the existing `BaseApi` request/response attachments.

See `AGENTS.md` → Requirements and validation.

## Development-task-driven tests

A development task can be a Jira:

- Story
- Task
- Improvement
- Bug

When a development task has no Zephyr case, annotate it similarly to a spec-driven test.

```python
import allure


@allure.link(
    "https://example.atlassian.net/browse/3747",
    name="Dev task",
)
@allure.title(
    "Template field is shown when Dictation Type is Conversation"
)
@allure.description(
    "Verifies that the Template field appears for each audio file "
    "when Dictation Type is Conversation."
)
def test_upload_template_visible_for_conversation_pos():
    ...
```

Rules:

- Do not add a fabricated TMS identifier.
- Use `name="Dev task"` for Jira development tasks.
- Prefer `name="Spec"` when an authoritative Confluence specification is available.
- Inline full URLs rather than hiding them behind constants.

## Severity

`@allure.severity` is not used in this project.

Do not add it to:

- Individual tests
- `pytestmark`
- New test templates
- Existing test examples

Jira step priority is not equivalent to Allure severity.

## Step numbering and titles

Every step title must match its source.

Sources can be:

- Zephyr test cases
- Confluence specifications
- Approved acceptance criteria

### Action steps

Use the exact wording of the test-case action.

### Check steps

Use the exact wording of the expected result.

Do not paraphrase the original source without a reason.

### `step_num`

Use the project's existing `step_num` fixture.

```python
step_num(1, "Log in")
```

Rules:

- Pass one integer as the first argument.
- Pass the source's action wording as the second argument.
- Call the fixture directly.
- Do not wrap it in a `with` statement.
- Place it immediately before the corresponding action.

The fixture renders steps in the project's established format:

```text
- - - << Step 1. Log in >> - - -
```

### `check_step`

Use the project's existing `check_step` fixture.

```python
check_step(1, "Header contains Edit button")
```

Rules:

- Pass one integer as the first argument.
- Pass the expected-result wording as the second argument.
- Call it directly.
- Place it immediately before the corresponding assertion or verification.
- Number expected-result checks sequentially.

Rendered format:

```text
- - - << ER 1 >> - - - Header contains Edit button
```

### Steps executed inside fixtures

When a fixture performs actions corresponding to documented test-case steps:

- Declare the `step_num` calls in the test.
- Do not add `step_num` calls inside the fixture.
- Use one `step_num` call per documented action.
- Then invoke the fixture.

Example:

```python
def test_2936_1(new_letter, step_num, check_step):
    step_num(1, "Log in")
    step_num(2, "Open the letter")

    letter_view, edit_modal = new_letter(
        flags={"show_mrn": True}
    )

    step_num(3, "Click on Edit button")
    letter_view.click_edit()

    check_step(1, "Header contains Edit button")
    letter_view.check_edit_button_present()

    check_step(2, "Button is unlocked")
    letter_view.check_edit_button_enabled()
```

## Parametrized tests

When a parametrized test executes the same scenario with different inputs, its report must identify the concrete input being verified.

A generic step title produces indistinguishable report entries for all parameter variants.

### Incorrect

```python
check_step(
    1,
    "Modal contains header, enabled field, Update and Cancel"
)

edit_modal.check_modal_open()
edit_modal.check_fields(expected_keys={field})
edit_modal.check_action_buttons()
```

### Correct

```python
field_label = edit_modal.field_label(field)

check_step(
    1,
    "The Edit modal is displayed with its header"
)
edit_modal.check_modal_open()

check_step(
    2,
    f"Only the {field_label} is displayed"
)
edit_modal.check_fields(expected_keys={field})

check_step(
    3,
    "The Update and Cancel buttons are displayed"
)
edit_modal.check_action_buttons()
```

Rules:

- Derive labels from the Page Object when the project provides them.
- Do not duplicate UI labels throughout tests.
- Preserve the original expected-result meaning.
- Add concrete parameter values when necessary.
- Split compound expected results into separately numbered checks when appropriate.

This is a deliberate exception to strictly verbatim step wording: additional parameter information is allowed to make the report understandable.

## Pytest markers

The project uses markers for:

- Test type
- Test suite
- Functionality
- Jira task traceability
- Parallel execution
- Authentication

The marker registration strategy must match the current `pytest.ini` and `conftest.py`.

Do not invent markers without verifying the existing project configuration.

### Common markers

| Marker | Purpose |
|---|---|
| `ui` | UI tests |
| `api` | API tests |
| `smoke` | Smoke suite |
| `regress` | Regression suite |
| `xdist_group` | Group tests on an xdist worker |
| `not_parallel` | Tests requiring serialized execution |
| `<feature>` | Functionality grouping |
| `<task_id>` | Jira task traceability |
| `auth("<role>")` | Authenticated test context |

### Marker registration

For markers not dynamically registered by the project:

1. Add the marker to `pytest.ini`.
2. Give it a clear description.
3. Run `pytest --markers`.
4. Verify that no `PytestUnknownMarkWarning` appears.

`pytest.ini` is the project's source of truth for manually registered markers.

Before changing marker registration, inspect the hooks in `conftest.py`.

## Functionality markers

Functionality markers allow related UI and API tests to be selected together.

Example:

```bash
pytest -m edit_modal
```

This should select tests associated with the `edit_modal` functionality.

A functionality marker is derived from the feature name using `snake_case`.

Examples:

- `Edit modal` → `edit_modal`
- `Letters service` → `letters`
- `Auth (API)` → `auth`

The project may generate these markers automatically.

Inspect the current implementation before adding explicit markers.

Relevant hooks may include:

- `pytest_collection_modifyitems`
- `pytest_configure`
- `_feature_slugs_for_item`
- `_discover_feature_markers`

### Explicit functionality markers

When automatic feature-marker generation is not implemented, declare the marker explicitly.

```python
pytestmark = [
    allure.feature("Edit modal"),
    pytest.mark.edit_modal,
    allure.story("Edit metadata modal"),
    pytest.mark.ui,
    pytest.mark.regress,
]
```

Register the marker in `pytest.ini`.

### Automatically generated functionality markers

When `conftest.py` generates them:

- Set `allure.feature` correctly.
- Set `allure.story` correctly.
- Do not duplicate automatically generated markers.
- Verify the results with `pytest --markers`.

Use consistent feature names across UI and API modules to support unified selection.

## Jira task markers

Every test originating from a Jira task must carry that task's identifier.

This applies to:

- UI tests
- API tests
- Tests in task-specific modules
- Tests in service-grouped directories
- Tests in feature-grouped directories
- Tests derived from development tasks
- Tests derived from specifications linked to a Jira task

For example, Jira task `3746` requires marker `3746`.

Because Python does not allow a numeric attribute name in dotted syntax, use `getattr`.

```python
import allure
import pytest

pytestmark = [
    allure.feature("Letter priority"),
    pytest.mark.api,
    pytest.mark.regress,
    getattr(pytest.mark, "3746"),
]
```

Do not write:

```python
pytest.mark.3746
```

That is invalid Python syntax.

### Rules

- Put a shared task marker in module-level `pytestmark`.
- Use a function-level marker when different tests belong to different tasks.
- Register the marker in `pytest.ini` if it is not already dynamically registered.
- Keep the marker consistent across UI and API tests originating from the same Jira task.

Example registration:

```ini
[pytest]
markers =
    3746: tests based on Jira task 3746
```

Example selection:

```bash
pytest -m 3746
```

## Authentication markers

The `auth` marker may have two distinct usages in the current project.

### Authentication fixture marker

```python
@pytest.mark.auth("nonai_doc")
```

This supplies role-specific authentication context through the project's existing authentication mechanism.

### Functionality marker

```python
pytest.mark.auth
```

A bare functionality marker does not necessarily establish an authenticated session.

Before adding either form:

- Inspect the project's `conftest.py`.
- Verify the authentication hook or fixture.
- Preserve the distinction between bare and parametrized markers.
- Do not invent role names.

## Parallelization markers

### `xdist_group`

Used to keep related tests on the same pytest-xdist worker.

The project may apply this automatically from `conftest.py`.

Do not manually duplicate it without checking the current implementation.

### `not_parallel`

Used when a test cannot safely execute alongside other tests.

Consult:

```text
docs/reference/parallelization.md
```

Verify how `conftest.py` implements serialization before applying this marker.

## Checklist before finishing a test

### Naming

- [ ] UI Jira-based test follows `test_{case}_{sub}` or the established project convention.
- [ ] UI spec-driven test follows `test_{testing_functionality}`.
- [ ] API test follows `test_{micro_service}_{endpoint}_{info?}_{pos|neg}`.
- [ ] No duplicate test file has been created.
- [ ] No duplicate test function exists.
- [ ] Test function has no return type annotation.
- [ ] Test is a module-level function, not a `class Test...` method.
- [ ] Test has no function docstring.

### Allure

- [ ] `@allure.title` is present.
- [ ] `@allure.description` is present.
- [ ] Jira/Zephyr tests use `@allure.testcase`.
- [ ] Spec-driven tests use `@allure.link(..., name="Spec")`.
- [ ] Development-task tests use `@allure.link(..., name="Dev task")`.
- [ ] Full source URLs are inlined.
- [ ] `@allure.severity` is absent.
- [ ] Shared `allure.feature` is declared at module level.

### Pytest markers

- [ ] Correct `ui` or `api` marker is applied.
- [ ] Correct suite marker is applied.
- [ ] Functionality marker follows the project's registration strategy.
- [ ] Jira task marker is present when required.
- [ ] New manually registered markers are documented in `pytest.ini`.
- [ ] Authentication marker is present when required.
- [ ] Parallelization constraints are respected.

### Steps and expected results

- [ ] Action steps use `step_num`.
- [ ] Expected-result checks use `check_step`.
- [ ] Step numbers are integers.
- [ ] Action wording matches the source.
- [ ] Expected-result wording matches the source.
- [ ] Parametrized reports include concrete parameter values when necessary.
- [ ] Fixture-executed steps are labelled in the test, not inside fixtures.
- [ ] Every source step and expected result is implemented.

### Code quality

- [ ] Every `assert` has a descriptive failure message.
- [ ] English-only code and test descriptions.
- [ ] No `print` statements.
- [ ] No commented-out implementation code.
- [ ] Existing framework abstractions are reused.
- [ ] Flake8 checks pass.
- [ ] Test follows the project's pytest, Playwright and service-layer architecture.

To inspect new commented-out code, use:

```bash
git diff -U0 -- '*.py' |
    grep -nE '^\+\s*#\s*(@|def |return |assert |import |pytest\.|allure\.|self\.)'
```

Explanatory comments are allowed. Commented-out executable statements are not.

### Execution and incomplete tests

- [ ] The generated test was executed when the environment allowed it.
- [ ] Any execution blocker is documented.
- [ ] A largely implemented but blocked test remains skipped with an explicit reason.
- [ ] No partially implemented test is reported as green.
- [ ] No empty test placeholder is left in the suite.
- [ ] Deferred scenarios are recorded in the task report.

See `AGENTS.md` → Blocked and incomplete scenarios.

## Handling blocked scenarios

### Largely implemented test

If a test is mostly implemented but temporarily blocked:

- Keep the implementation.
- Mark the entire test as skipped.
- State the exact blocker.
- Notify the requester.

Example:

```python
@pytest.mark.skip(
    reason="Blocked: expected API response field is absent in develop"
)
def test_pms_spells_general_pos(templates_api):
    ...
```

### Scenario that cannot be implemented

If implementation cannot meaningfully begin:

- Do not create a placeholder test.
- Document the scenario in:

```text
docs/tasks/<id>/task_report.md
```

- Explain the missing requirements, dependencies or environment capabilities.

### Empty tests

Remove tests containing only:

- `pass`
- `...`
- A docstring
- A placeholder comment

### Runtime data-dependent skips

Runtime skips are acceptable when required test data is unavailable.

```python
if not test_data:
    pytest.skip("No suitable test data available")
```

### No partial green tests

Never silently omit unimplemented expected results while allowing a test to pass.

Every documented step and expected result must be covered.

If an expected result cannot be implemented but the remainder of the test is complete, skip the whole test with a clear explanation.