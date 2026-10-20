---
name: writing-api-tests
description: >-
  Create and maintain Python pytest API tests using the project's BaseApi
  client, service layer, Endpoints registry, Pydantic models and Allure.
  Use for API test implementation, service methods, contract assertions,
  authentication, negative scenarios and API regression coverage.
---

# Writing API Tests

## Purpose

Implement reliable API tests that verify documented requirements
and application contracts.

Follow `AGENTS.md` for global project rules.

Related skills:
- `fetching-test-cases-and-wiki` — retrieve requirements.
- `capturing-test-cases` — normalize Jira/Zephyr cases.
- `api-contract-audit` — verify contracts.
- `allure-annotations-and-naming` — test metadata.
- `triaging-test-failures` — investigate failures.

## 1. Scope and Priorities

Prefer API coverage before UI coverage when functionality
can be verified at both layers.

Native Android/iOS behavior is outside the project scope.

For mobile-oriented requirements:

- Test exposed backend and Web API behavior.
- Verify relevant settings, fields and round-trips.
- Report mobile-only scenarios as out of scope.
- Do not assert fields absent from the deployed API.

Never invent API behavior.

## 2. Test Sources

### Spec-driven — default

Source: Confluence specification.

1. Read the authoritative specification.
2. Identify endpoints, payloads and expected results.
3. Verify missing technical details against the live API.
4. Report gaps and contradictions.
5. Implement only sufficiently verified behavior.

If the specification lacks an endpoint, status or allowed value,
probe the service and tell the requester what was missing.

Observed behavior alone is not proof of intended behavior.

Use:

```python
@allure.link(
    "https://example.atlassian.net/wiki/...",
    name="Spec",
)
```

Do not create fictitious Zephyr test cases.

### Development-task-driven

Source: Jira Story, Task or Improvement.

Read the issue and its linked requirements.

Use:

```python
@allure.link(
    "https://example.atlassian.net/browse/3747",
    name="Dev task",
)
```

Do not require a Zephyr case unless one is actually part
of the task.

### Case-driven

Source: Jira/Zephyr Test.

Tests must follow the approved document:

```text
docs/tasks/{num}/{num}_cases.md
```

**Do not start implementation before explicit human approval.**

Use `capturing-test-cases` for the approval procedure.

## 3. Architecture

The established API architecture is:

```text
tests/api_tests/
    ↓
api_client/services/
    ↓
api_client/base_requests.py   (BaseApi)
    ↓
api_client/endpoints.py       (Endpoints)
```

Data models:

```text
data/models/api_responses.py
data/models/enums.py
```

Fixtures:

```text
fixtures/api_fixtures.py
```

Responsibilities:

| Layer | Responsibility |
|---|---|
| Test | Scenario and assertions |
| Service | Business operations |
| BaseApi | HTTP transport and Allure attachments |
| Endpoints | Centralized endpoint paths |
| Pydantic | Request/response validation |
| Fixtures | Authorization and dependencies |

Do not perform raw HTTP calls directly in tests
when the existing service layer supports the operation.

Inspect actual implementations before calling their methods.

## 4. Test Organization

### Spec-driven API tests

Group by service or functionality:

```text
tests/api_tests/<service>/test_<aspect>.py
```

Example:

```text
tests/api_tests/auth/test_login.py
tests/api_tests/letters/test_search.py
```

### Case-driven API tests

Group cases from one Jira task together:

```text
tests/api_tests/{num}/test_{num}.py
```

Use module-level test functions.

Do not use test classes.

Before creating a test:

1. Check for an existing target file.
2. Check for an existing function with the same name.
3. Reuse an existing module when appropriate.
4. Never overwrite unrelated tests.

## 5. Test Naming

Use:

```text
test_{micro_service}_{endpoint}_{info?}_{pos|neg}
```

Examples:

```python
def test_auth_login_pos():
    ...

def test_auth_login_neg():
    ...

def test_letters_search_in_progress_pos():
    ...

def test_pms_spells_general_pos():
    ...
```

Rules:

- Name tests by functionality, not Jira ID.
- `info` is optional.
- `pos` and `neg` are mandatory suffixes.
- No return type annotations on test functions.
- No test-function docstrings.
- No duplicate function names.

## 6. Endpoints

The application does not expose a complete authoritative
Swagger/OpenAPI specification.

REST paths are maintained in:

```text
docs/reference/api_catalog.md
api_client/endpoints.py
```

Use existing `Endpoints` constants.

Do not inline endpoint strings in service methods.

For new endpoints:

1. Verify the path through documented or observed evidence.
2. Check whether an `Endpoints` constant already exists.
3. Add the constant if required.
4. Update the API catalog.
5. Use `{id}`-style path parameter templates.

The project can generate a local OpenAPI representation:

```bash
python -m tools.generate_openapi
```

See `api-contract-audit` for source and Confluence merging.

## 7. Pydantic Models

Define or reuse models in:

```text
data/models/api_responses.py
```

Use Pydantic v2.

Example:

```python
from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    user_id: int = Field(..., alias="userId")
    display_name: str = Field(..., alias="displayName")
```

Rules:

- Reuse existing models.
- Use API aliases for camelCase fields.
- Use `extra="ignore"` when appropriate.
- Required fields use `Field(...)`.
- Optional fields use `X | None`.
- Do not invent fields.
- Preserve meaningful descriptions.
- Validate actual field values.

### Response validation

Do not assert only the response type.

Weak:

```python
assert isinstance(items, list)
```

Better:

```python
assert items, "Expected a non-empty response"

for item in items:
    UserProfile.model_validate(item)
```

If an empty list is valid, do not assert non-emptiness.
Instead verify the documented list behavior and validate
each item when present.

## 8. Enums

Use source-derived enums from:

```text
data/models/enums.py
```

Source extraction:

```bash
python -m tools.extract_schemas
```

For enum-backed fields:

1. Inspect the actual source enum.
2. Verify the live API value range.
3. Type the corresponding Pydantic field.
4. Assert valid enum values.

Do not restrict a field to an enum if the deployed API
returns values outside that enum.

Do not replace meaningful value assertions with
type-only checks.

## 9. Services and HTTP

Business operations belong in:

```text
api_client/services/
```

Services use `BaseApi` for HTTP methods:

- GET
- POST
- PUT
- PATCH
- DELETE

Status verification is handled by `BaseApi`.

Pass `expected_code` for non-default expected statuses.

BaseApi also attaches request and response evidence
to Allure when the call uses the service layer.

Do not duplicate this logging in every test.

Never attach secrets or authorization tokens.

## 10. Authentication

Use service factories from:

```text
fixtures/api_fixtures.py
```

Examples include:

- `organisation_items_api`
- `letters_api`
- `settings_api`
- `templates_api`
- `accounts_api`
- `recipients_api`
- `notifications_api`
- `user_profiles_api`

Inspect available fixtures before use.

The default role is:

```text
nonai_doc
```

An additional role may be:

```text
nonai_doc2
```

Services are created by calling the fixture factory:

```python
api = letters_api()
```

Role selection, when supported:

```python
api = letters_api("nonai_doc2")
```

Tokens are cached using `user_token_by_role`.

Credentials come from `.env` through `UsersCredentials`.

For login contract tests, use the unauthenticated
`auth_api` fixture.

### Login details

Current authentication endpoint:

```text
POST /api/web/login
```

The request requires the client header configured
through `WEB_CLIENT_AUTH`.

The application uses bearer tokens.

Do not hardcode credentials.

## 11. Negative Tests

Test invalid input, authorization failures and
contract-defined error responses.

Prefer a service method returning `LoggedResponse`
when the test needs to inspect an error response.

Example pattern:

```python
response = service.get_resource_response(
    resource_id,
    expected_code=404,
)
```

Verify:

- HTTP status
- Error structure
- Documented error message
- Relevant response fields

Do not fabricate expected error codes.

### Login safety

Never intentionally lock a real account.

Wrong passwords against existing users may decrement
their lockout counter.

For negative authentication testing, prefer a
non-existent username when the contract permits it.

## 12. Test Data and State Changes

Store reusable test data outside `tests/`:

```text
data/<feature>_data/<feature>_data.py
```

Use existing fixtures and models.

### Write tests

For state-changing tests:

1. Capture original state.
2. Perform the mutation.
3. Verify the response.
4. Read back the updated state.
5. Restore the original state in `finally`.

Example:

```python
original = service.get_settings()

try:
    service.update_settings(new_settings)

    actual = service.get_settings()
    assert actual == new_settings, (
        "Expected updated settings to be persisted"
    )
finally:
    service.update_settings(original)
```

Treat this as a conceptual pattern; use real project APIs.

### Disposable data

Prefer existing fixtures such as:

```text
seed_letter
audio_clip
```

`seed_letter` creates removable test records.

`audio_clip(seconds)` generates deterministic audio
for upload and validation tests.

Do not mutate shared production-like data unnecessarily.

## 13. Parametrization

Use parametrization only when scenarios share:

- Identical actions
- Identical expected-result structure
- Identical preconditions

Example:

```python
@pytest.mark.parametrize(
    "value",
    ["asc", "desc"],
    ids=["ascending", "descending"],
)
def test_letters_search_sort_pos(value):
    ...
```

Do not merge separate Jira/Zephyr cases into one test.

Different workflows or expected outcomes require
separate test functions.

## 14. Assertions

Every assertion must have a meaningful failure message.

Example:

```python
assert model.enabled is True, (
    "Expected the feature to be enabled"
)
```

Prefer meaningful business invariants:

- Uniqueness
- Correct ordering
- Referential consistency
- Round-trip persistence
- Valid enum membership
- Required schema fields

Do not assert arbitrary values captured from one run
unless they form a verified regression contract.

### None and falsy values

Truthiness checks are appropriate only when all falsy
values are invalid.

If `0`, `False`, `""` or `[]` is valid, use precise comparisons:

```python
assert model.retry_count is not None, (
    "Expected retry_count to be provided"
)
```

Do not substitute a truthiness check that rejects valid data.

## 15. Allure Annotations

Use `allure-annotations-and-naming`.

Every API test requires:

- `@allure.title`
- `@allure.description`
- A source link
- Appropriate `pytestmark`
- An oracle label

Example:

```python
import allure
import pytest

from data.models.api_responses import GeneralSpell

pytestmark = [
    allure.feature("Templates"),
    pytest.mark.api,
    pytest.mark.regress,
]


@allure.title("PMS spells catalogue matches the schema")
@allure.description(
    "Verify the general spell catalogue response schema."
)
@allure.link(
    "https://example.atlassian.net/wiki/...",
    name="Spec",
)
@allure.label("oracle", "task")
def test_pms_spells_general_pos(
    templates_api,
    step_num,
    check_step,
):
    step_num(1, "Fetch the general spells catalogue")
    items = templates_api().get_general_spells()

    check_step(1, "Every spell matches the expected schema")
    for item in items:
        GeneralSpell.model_validate(item)
```

The URL and wording must come from real requirements.

## 16. Test Oracle

Every API test must explicitly identify its oracle.

Supported labels:

```python
@allure.label("oracle", "task")
```

```python
@allure.label("oracle", "source_code")
```

### `task`

Expected results come from Jira or Confluence.

This verifies intended behavior.

### `source_code`

Expected results come from:

- Application implementation
- Captured traffic
- Source-derived schemas
- Observed API behavior without an approved specification

This is characterization or regression coverage,
not proof of business correctness.

Oracle label rules are documented in:

```text
docs/reference/source_labels.md
```

Run the existing labelling utility after adding tests:

```bash
python -m tools.label_test_oracle
```

## 17. Stability

### Feature flags and capabilities

Prefer capability-aware assertions when the requirement
defines different behavior for enabled and disabled states.

Read actual feature availability instead of hardcoding
an environment assumption.

Do not silently accept missing required behavior.

### Environment differences

If builds differ, identify the exact supported contracts.

Do not weaken assertions merely to pass on every build.

Report undocumented differences.

### Confirmed application bugs

A completely implemented test blocked by a confirmed
application defect may use:

```python
@pytest.mark.xfail(
    reason="Confirmed backend defect: <Jira issue>",
    strict=False,
)
```

Record supporting evidence.

Do not use xfail to conceal an uninvestigated failure.

### Timing

For performance checks:

- Exclude warm-up requests.
- Account for environment variability.
- Use documented performance expectations.
- Avoid arbitrary tight timeouts.

## 18. Blocked Scenarios

Never ship partially implemented green tests.

If a test is substantially implemented but blocked:

```python
@pytest.mark.skip(
    reason="Blocked: required API field is not deployed"
)
```

When no meaningful implementation is possible:

- Do not create a placeholder.
- Record the scenario in `task_report.md`.
- Explain the blocker.
- Notify the requester.

Runtime data-dependent skips are acceptable when
the test cannot proceed without required data.

Do not leave permanent skips without reviewing whether
the scenario can be replaced by a meaningful invariant.

## 19. Contract Verification

Before asserting:

1. Read the documented requirement.
2. Inspect the endpoint definition.
3. Probe the deployed service where necessary.
4. Confirm the payload shape.
5. Verify enum values.
6. Resolve contradictions or report blockers.

A not-yet-deployed field may be represented as optional
for forward compatibility.

Do not assert that field until it exists and the expected
behavior is verified.

### OData

The OData metadata endpoint is:

```text
GET /api/author/odata/$metadata
```

Reference:

```text
docs/reference/odata_metadata_summary.md
```

Use metadata for entity types and enum information.

## 20. Generated API Documentation

Relevant tools:

```bash
python -m tools.generate_openapi
python -m tools.extract_schemas
python -m tools.check_tests_vs_swagger
```

The test-to-Swagger check reports:

- `OK`
- `METHOD-MISMATCH`
- `MISSING`
