---
name: writing-api-tests
description: >-
  Implement and maintain pytest API tests in tests/api/ using BaseClient,
  clients/, Pydantic models in models/, error mapping, and respx isolation.
  Use for HTTP contract tests, authentication, negative cases, response
  validation, and API regression coverage.
---

# Writing API Tests

## When to use

Use this Skill for API test implementation or changes under `tests/api/`.
For a UI scenario, use `writing-ui-tests`; for external TMS case approval,
use `capturing-test-cases`; for test metadata, use
`allure-annotations-and-naming`.

Follow `AGENTS.md` for global rules. Inspect the actual client, model, and
test module before editing.

## 1. Actual API architecture

```text
tests/api/                  module-level pytest tests + local fixtures
    |
clients/                    AuthClient, UsersClient
    |
framework/api/base_client.py    BaseClient (httpx transport)
    |
framework/api/exceptions.py     APIError mapping
    |
models/                     Pydantic request/response models
```

Important facts:

- Do not add a parallel client, service, endpoint-registry, or shared-fixture
  layer; reuse the classes above.
- `BaseClient` owns an `httpx.Client`, base URL, timeout, bearer header
  helpers, request helpers, and typed error raising.
- `clients/auth_client.py` and `clients/users_client.py` are the business
  clients.
- `models/auth.py` and `models/user.py` define the Pydantic contracts.
- `tests/api/conftest.py` is effectively empty; fixtures are local to test
  modules.

Do not introduce a new transport/client layer when `BaseClient` or an
existing client already covers the operation.

## 2. Test organization and naming

- Use module-level test functions, not test classes. Preserve the existing
  style in `tests/api/test_auth_api.py` and `tests/api/test_users_api.py`.
- Use descriptive names such as `test_login_returns_token`,
  `test_login_invalid_password`, or `test_get_user_not_found`.
- For a case-driven test, use a stable case-based name such as
  `test_<case_id>[_<n>]` only when a real approved TMS case exists.
- Do not rename existing tests or force a `pos`/`neg` suffix that the
  repository does not use.
- Check for an existing file/function before adding a duplicate scenario.

## 3. Clients and models

Use clients, not ad-hoc HTTP calls, when a client method exists:

```python
from clients.auth_client import AuthClient
from models.auth import LoginRequest

client = AuthClient(base_url="http://testserver")
try:
    response = client.login(
        LoginRequest(username="standard_user", password="secret_sauce")
    )
finally:
    client.close()
```

Rules:

- Construct clients with `base_url`; call `close()` in a fixture or `finally`.
- Use `model_validate(response.json())` through existing client methods; do
  not bypass typed responses when the client already validates them.
- `LoginResponse.token` is the alias-backed access token field; inspect the
  model rather than inventing a new shape.
- `AuthClient` exposes `login`, `logout`, `refresh_token`, and Bearer token
  helpers inherited from `BaseClient`.
- `UsersClient` exposes `get_user`, `get_users`, `create_user`,
  `update_user`, and `delete_user`; preserve its existing not-found behavior.
- Do not inline endpoint paths in tests when a client method exists.

## 4. Isolated HTTP tests with respx

The current API tests use `respx` against a fixed base URL:

```python
import httpx
import pytest
import respx

from clients.auth_client import AuthClient
from framework.api.exceptions import UnauthorizedError
from models.auth import LoginRequest

BASE_URL = "http://testserver"


@pytest.fixture
def auth_client():
    client = AuthClient(base_url=BASE_URL)
    yield client
    client.close()


@respx.mock
def test_login_returns_token(auth_client: AuthClient) -> None:
    respx.post(f"{BASE_URL}/auth/login").mock(
        return_value=httpx.Response(
            200,
            json={"access_token": "abc123", "token_type": "bearer"},
        )
    )

    response = auth_client.login(
        LoginRequest(username="standard_user", password="secret_sauce")
    )

    assert response.token == "abc123"
    assert response.token_type == "bearer"
```

- Mock the exact method/path used by the client.
- Use a local fixture for client lifecycle; close the client in teardown.
- Do not require a live service for isolated contract tests.
- If a live service is verified and needed, make that explicit in the test
  name/report and restore any changed state. Do not silently switch a mocked
  test to a live one.

## 5. Assertions and error contracts

Assert status behavior, parsed values, schema, and business invariants:

- `response.status_code` when using a raw response.
- Typed fields from the Pydantic model.
- Expected error class and status for `401`, `403`, `404`, `422`, and `5xx`.
- Required fields, enum values, ordering, uniqueness, and round-trips.
- Exact expected messages only when the contract defines them.

`BaseClient` maps errors as follows:

| Status | Exception |
|---|---|
| `401` | `UnauthorizedError` |
| `403` | `ForbiddenError` |
| `404` | `NotFoundError` |
| `422` | `UnprocessableError` |
| `>=500` | `ServerError` |
| other `>=400` | `APIError` |

Use `pytest.raises` and inspect the exception:

```python
with pytest.raises(UnauthorizedError) as exc_info:
    auth_client.login(LoginRequest(username="standard_user", password="wrong"))

assert exc_info.value.status_code == 401
```

Do not assert only that a result is a `dict`, `list`, or model instance when
the actual status, field value, or business invariant is available. Do not
invent status codes, error messages, or response fields.

## 6. Test data and state

- Use deterministic data and a test-specific base URL.
- Never hardcode real credentials, tokens, or production personal data.
- Prefer nonexistent/mock identifiers for negative lookups.
- For live write tests, capture the original state, perform the mutation,
  verify the response and read-back, and restore in `finally`.
- Do not mutate shared production-like data without explicit authorization.
- Keep tests independent; do not depend on execution order.

## 7. Parametrization

Use `@pytest.mark.parametrize` only when variants share the same request flow,
preconditions, and assertion structure. Use descriptive IDs. Do not merge
separate TMS cases or different expected outcomes into one test.

## 8. Failures, markers, and reporting

Investigate failures before editing expectations. Distinguish a client/model
defect from a contract disagreement, environment issue, or application defect;
load `triaging-test-failures` when deeper analysis is needed.

- Do not weaken assertions or add placeholders to get green.
- Do not use `skip`/`xfail` without a documented reason.
- Use only markers registered in `pytest.ini`; apply `api` to new API tests
  when consistent with the surrounding module.
- Apply `allure-annotations-and-naming` when adding metadata. Do not invent
  Jira IDs or `@allure.testcase` links.

## 9. Verification

Run focused checks from the repository root:

```bash
.venv/bin/python -m pytest tests/api/test_auth_api.py -q
.venv/bin/python -m pytest tests/api -q
.venv/bin/ruff check tests/api clients models framework/api
git diff --check
```

Report the exact command, exit code, and outcome. If a live service or
credential is unavailable, report that coverage gap rather than claiming a
pass.
