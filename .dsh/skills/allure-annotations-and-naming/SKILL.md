---
name: allure-annotations-and-naming
description: >-
  Apply this repository's pytest naming, Allure titles/stories/descriptions/
  links/steps, and registered markers to new or changed UI and API tests. Use
  when adding test metadata or reviewing whether a test is discoverable and
  readable in Allure.
---

# Allure Annotations and Naming

## When to use

Use this Skill when creating or updating a test's name, Allure metadata,
markers, or step reporting. It supplements `writing-ui-tests`,
`writing-api-tests`, and `page-object-creation`.

Follow `AGENTS.md` for global rules. Inspect neighboring tests before applying
a pattern; do not retrofit unrelated tests or rename existing ones.

## 1. Naming

### UI tests

- Preserve the existing `Test<Feature>` class and `test_<behavior>` method
  style, for example `TestLogin.test_login_success`.
- The readable expected behavior belongs in `@allure.title`, not in an
  artificially abbreviated method name.
- For a real case-driven test, a stable `test_<case_id>[_<n>]` name is
  acceptable; do not invent a case ID when none exists.

### API tests

- Keep module-level functions with descriptive names, for example
  `test_login_returns_token` and `test_get_user_not_found`.
- Do not force a `pos`/`neg` suffix or a service-prefixed naming scheme that
  the current repository does not use.
- For a real case-driven test, use `test_<case_id>[_<n>]`; otherwise preserve a
  short behavioral name.

Before adding a test, confirm the target file and function name do not already
exist. Do not rename unrelated tests to satisfy a template.

## 2. UI Allure structure

Follow the existing class-level pattern:

```python
@allure.feature("Authentication")
@allure.story("UI Login")
@pytest.mark.ui
class TestLogin:
    @allure.title("Successful login redirects to dashboard")
    @pytest.mark.smoke
    def test_login_success(self, page: Page, base_url: str) -> None:
        ...
```

Use:

- Class-level `@allure.feature` and `@allure.story`.
- Method-level `@allure.title` describing the expected behavior.
- `@allure.description` for a non-obvious scenario, setup, or root-scoping
  detail; see `TestComponentScoping`.
- `@allure.step` in Page Objects/clients for meaningful actions, as already
  used by `LoginPage.login`, `DashboardPage.logout`, and API clients.
- Existing return annotations (`-> None`) and neighboring formatting.

Do not add redundant reporting around every locator operation. Do not attach
passwords, tokens, cookies, or personal data to Allure.

## 3. API Allure structure

The current API modules are not annotated. When adding a new API test or
materially updating one, add only what improves discovery:

```python
@allure.feature("Authentication")
@allure.title("Login returns an access token")
def test_login_returns_token(auth_client: AuthClient) -> None:
    ...
```

Do not retrofit Allure metadata onto untouched API tests merely to make the
suite uniform. `BaseClient`/client methods may already carry `@allure.step`; do
not duplicate them in the test.

## 4. Links and case references

- Use `@allure.link(url, name="Spec")` for an actual specification URL.
- Use `@allure.link(url, name="Dev task")` for an actual development-task URL.
- Use `@allure.testcase(url, case_id)` only when a real Jira/Zephyr/TMS case
  exists and has been approved under `capturing-test-cases`.
- Never invent a Jira ID, case URL, or TMS identifier.
- Do not add a link merely to satisfy a checklist; omit it when no real source
  exists.

## 5. Markers

`pytest.ini` is the source of truth. It currently registers only:

- `ui`
- `api`
- `smoke`
- `regression`

Rules:

- Apply `ui` to UI tests and `api` to new API tests when consistent with the
  module.
- Use `smoke` only for smoke scenarios and `regression` only when the suite
  uses it.
- Do not invent Jira, auth, functionality, or parallel markers.
- If a new marker is genuinely required, register it in `pytest.ini` first and
  verify `pytest --markers`; do not assume a marker exists.

## 6. Steps and severity

- Do not add `@allure.severity`; this project does not use it.
- Do not add project-specific step fixtures; only use fixtures that actually
  exist in the repository.
- Do not add `@allure.step` to trivial helper methods or every locator call.
- Use `@allure.step` only for meaningful operations that already fit the
  project pattern.

## 7. Checklist

Before finishing:

- [ ] The test name follows the neighboring convention.
- [ ] UI tests keep class-level feature/story and a method title.
- [ ] API tests receive metadata only when new or materially changed.
- [ ] Descriptions explain non-obvious behavior rather than restating the name.
- [ ] Links and case references point to real sources.
- [ ] Only markers registered in `pytest.ini` are used.
- [ ] No `@allure.severity` or nonexistent step fixture was added.
- [ ] No sensitive values appear in titles, descriptions, steps, or attachments.
- [ ] Existing tests were not renamed or restructured unnecessarily.
