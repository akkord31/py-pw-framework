# py-pw-framework — Agent Instructions

## 1. Purpose and Authority

This repository is a Python test-automation framework for UI and API testing:
pytest, Playwright Sync API, Allure, httpx with Pydantic, and a local
read-only TMS mock.

This file is authoritative for the single main DeepSeek Harness agent. It owns
inspection, planning, implementation, test execution, debugging, verification,
and reporting. There is no separate coordinator layer and no mandatory subagent chain.

System, developer, and explicit user instructions take precedence. Verified
repository evidence outranks this file, which outranks Skill procedures and
neighboring conventions. If sources conflict, stop and report the
contradiction. Never invent modules, classes, methods, fixtures, locators,
endpoints, markers, tools, integrations, or behavior.

## 2. Single-Agent Loop

1. Inspect the request, scope, acceptance criteria, and relevant code.
2. Identify missing information, source limits, and approval needs.
3. Plan the smallest change that reuses existing abstractions.
4. Implement directly in the approved scope.
5. Run focused checks and inspect actual failures.
6. Fix automation issues and repeat verification.
7. Review the final diff for scope creep and lost requirements.
8. Report files, commands, evidence, blockers, and residual risks.

Do not delegate routine planning, implementation, testing, debugging, or
reporting. No separate workflow Skill is used.

## 3. Verified Repository Map

| Area | Actual implementation |
|---|---|
| UI | `framework/ui/` — `BasePage`, `PageAdapter`, `UiComponent`, `Input`, `Button`, `CheckBox`, `LoginForm`, `BrowserFactory`; Page Objects in `pages/`; class-based tests and fixtures in `tests/ui/` |
| API | `framework/api/base_client.py` (`BaseClient`), `framework/api/exceptions.py`, clients in `clients/`, Pydantic models in `models/`; module-level `respx` tests in `tests/api/` |
| TMS | `tms/` — local read-only provider, client, mock API, MCP server; tests in `tests/tms/` |
| Config | `pytest.ini` registers `ui`, `api`, `smoke`, `regression` and writes Allure results; dependencies are in `pyproject.toml` |

Preserve the architecture:

- UI tests use Page Objects/components; do not put application selectors or
  browser mechanics in scenario tests.
- API tests use `BaseClient` + `clients/` + `models/`; do not add a parallel
  client, service, endpoint-registry, or shared-fixture layer.
- Do not add layers/dependencies the repository lacks. Native `Page` and
  `PageAdapter` are not interchangeable.

## 4. Skills: Progressive Disclosure

Skills live in `.dsh/skills/<name>/SKILL.md`. Load one by exact name only when
its procedure is relevant; if the Skill tool is unavailable, read that file
directly. Start with this file and do not preload every Skill.

| Need | Skill |
|---|---|
| UI work | `writing-ui-tests`; use `page-object-creation` when pages/components change |
| API tests | `writing-api-tests` |
| Reporting, failures, external cases | `allure-annotations-and-naming`, `triaging-test-failures`, `capturing-test-cases` |

Read a Skill in full before applying it. A Skill may add procedure but cannot
weaken this file’s approval, security, delegation, or test-quality rules.

## 5. External TMS Approval Gate

Any test case imported from an external TMS (Jira, Zephyr, the TMS MCP
integration, or equivalent) requires explicit human approval before
implementation.

1. Obtain the source case without inventing missing content.
2. Normalize it with `capturing-test-cases`, preserving steps, data, and
   expected results.
3. Present the normalized case and unresolved questions.
4. Wait for explicit human approval before changing anything.

Before approval, do not create or modify tests, Page Objects, clients,
fixtures, or test data. Approval cannot be inferred from silence or an
unrelated request to continue. Spec- and development-task work follows its
source only when no external TMS case is involved.

## 6. Optional Anonymous Delegation

Routine work stays with the main agent. Use an anonymous `subagent` only when
independent verification or isolated research clearly benefits from a fresh
context, such as reviewing a nontrivial diff or investigating a large,
self-contained failure.

- Do not assume named agents, model selectors, or per-agent permissions; none
  are guaranteed. Never pass a role name; do not use role-template files.
- For independent review, use a fresh `subagent`, not `subagent_fork`; provide
  the diff, requirements, and checks. Verify findings and workspace changes.
- Markdown instructions are not a security boundary.

Do not create a subagent for routine implementation, test authoring,
documentation, or coordination.

## 7. Engineering Invariants

- Use pytest and Playwright Sync API. Reuse `tests/ui/conftest.py` fixtures and
  existing Page Objects/components.
- API tests use `BaseClient`, `clients/`, `models/`, and `respx`. Keep transport
  in clients and assertions in tests.
- Tests must be meaningful, deterministic, and isolated. Verify behavior and
  expected values, never only a Python type.
- Do not create `pass`, `...`, or placeholder tests. Do not weaken or delete
  assertions to make a test green. Skip only for a documented blocker; use
  `xfail` only for a verified expected failure.
- Use only markers registered in `pytest.ini`; do not invent Jira or
  functionality markers. Apply `allure-annotations-and-naming` for metadata;
  do not use `@allure.severity`.
- Preserve class-based UI tests and module-level API tests; do not rename or
  restructure them to satisfy a template.

## 8. Security, Secrets, and Git

- Application source is read-only (prefer `develop`); never modify or commit
  there, or open pull requests. Do not modify production/live data or run
  destructive commands without authorization.
- Treat `.env`, tokens, credentials, cookies, and auth headers as sensitive.
  Never print, log, commit, attach to Allure, or report their values. Use
  `.env-example` placeholders and environment variables.
- Do not commit or push unless explicitly requested. Do not stage generated
  output, caches, IDE files, or secrets. Keep changes in scope and never revert
  unrelated work.

## 9. Optional Integrations

Jira, Zephyr, Confluence, Bitbucket, Playwright MCP, the TMS MCP server, and
databases may or may not be connected; treat them as optional capabilities.

- Confirm the integration and exact tool names first. `tms/` is a local
  read-only mock; `tests/tms/` is not a real Jira/Zephyr connection.
- If unavailable, report the limitation and use repository/user evidence;
  never fabricate records or links.

## 10. Verification and Reporting

Run focused tests and relevant static checks when the environment permits.
Record the exact command, exit code, and outcome. Investigate failures and
distinguish automation defects, application defects, requirement gaps, and
environment blockers.

For nontrivial changes, review the diff, assertions, Page Object boundaries,
fixtures/isolation, API contracts, Allure, and scope; optionally obtain
independent anonymous review. Report the summary, changed files, commands,
results, blockers, missing coverage, and residual risks. Never claim success
without evidence; state explicitly when verification was impossible.

## 11. Completion Checklist

- [ ] Scope, source, approval status, code, tests, fixtures, and configs known.
- [ ] Only necessary Skills loaded; no nonexistent path/fixture/marker/tool assumed.
- [ ] External TMS cases received explicit human approval.
- [ ] Changes stay within the requested scope.
- [ ] Focused tests and static checks ran where possible, with evidence.
- [ ] Assertions are meaningful and no placeholders remain.
- [ ] Security, secrets, Git, final diff, and report are complete.
