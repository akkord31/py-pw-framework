# py-pw-framework — AI Agent Instructions

## Purpose

This repository is a Python test automation framework built with
pytest, Playwright Sync API, Allure and pytest-xdist.

DeepSeek Harness is used to assist with test automation,
framework development, requirements analysis and code review.

These instructions apply to the main agent and delegated subagents.

Before making changes:
1. Understand the task.
2. Inspect the existing implementation.
3. Load relevant Skills.
4. Follow existing architecture.
5. Make the smallest necessary changes.
6. Verify and report the result.

Never invent framework methods, locators, fixtures, endpoints
or application behavior.

## 1. Project Architecture

### UI automation

The existing UI framework includes:

- `framework/ui/base_page.py` — BasePage.
- `framework/ui/page_adapter.py` — PageAdapter.
- `framework/ui/components/` — reusable UI components.
- `BrowserFactory` — browser and context lifecycle.
- `pages/` — application Page Objects.
- `tests/` — pytest tests.

Important abstractions:

- BasePage
- PageAdapter
- UiComponent
- Input
- Button
- BrowserFactory

Inspect the actual classes before using their interfaces.

Native Playwright Page and PageAdapter are not interchangeable.

UI tests interact with application functionality through
Page Objects and reusable components.

Keep selectors inside Page Objects or UI components.

### API automation

When the corresponding modules exist, use:

- `api_client/base_requests.py` — BaseApi.
- `api_client/services/` — business-level API operations.
- `api_client/endpoints.py` — centralized endpoint paths.
- `data/models/` — Pydantic models and enums.
- `fixtures/api_fixtures.py` — API fixtures.

Prefer the existing service layer over direct HTTP requests
inside tests.

### Source of truth

The actual repository implementation determines which
framework interfaces, fixtures, paths and conventions exist.

Project documentation and Skills define intended conventions,
but must not be used to invent missing functionality.

## 2. Application Source vs Automation Code

"Application source code" means the product repository,
not this automation framework.

Application source:

- Read-only.
- Prefer branch `develop` when available.
- Never modify application files.
- Never create commits or pull requests.

Automation repository:

- May be modified within the approved task scope.
- Must preserve existing architecture.
- Must not change unrelated files.

Distinguish actual application behavior from intended behavior.

If implementation contradicts requirements, document the
discrepancy instead of changing assertions to match a defect.

## 3. Agents

Agent instructions are stored in:

`.dsh/agents/`

Available roles:

| Agent | Responsibility |
|---|---|
| `sdet-orchestrator` | Coordinates task execution and delegation |
| `sdet-architect` | Designs and implements test automation |
| `sdet-reviewer` | Independent read-only code review |
| `sdet-refactor-cleaner` | Improves existing code without changing behavior |
| `spec-analyst` | Analyzes requirements and testability |
| `report-analyst` | Investigates failures and Allure reports |
| `doc-updater` | Maintains project documentation |

### Orchestrator

The main agent acts as the orchestrator.

Read `.dsh/agents/sdet-orchestrator.md` when coordinating
a multi-stage task.

Responsibilities:

1. Analyze the request.
2. Identify relevant Skills.
3. Select specialist roles when delegation adds value.
4. Define task scope and acceptance criteria.
5. Coordinate implementation and review.
6. Verify the final result.
7. Report completed work and blockers.

Do not create subagents for trivial tasks unnecessarily.

### Delegation

The current DeepSeek Harness configuration does not
register `.dsh/agents/*.md` as callable named agents.

Agent files are instruction templates.

To delegate:

1. Read the complete specialist role file.
2. Create a fresh anonymous subagent using the available
   `subagent` tool.
3. Include the role instructions in its prompt.
4. Provide task context, working directory, relevant files,
   allowed changes and expected deliverable.
5. Wait for the result.
6. Inspect the result before continuing.

Do not invent named-agent selectors.

### Independent review

For implementation review:

1. Complete implementation.
2. Capture changed files and relevant diff.
3. Read `sdet-reviewer.md`.
4. Spawn a fresh reviewer subagent.
5. Provide the complete review instructions and diff.
6. Request findings without modifications.
7. Evaluate and address confirmed findings.

Prefer a fresh `subagent` over `subagent_fork`
for independent review.

Reviewer instructions alone do not guarantee
filesystem read-only permissions.

Use actual read-only permissions when supported.
Otherwise treat the review as instruction-level read-only
and verify that no files were changed.

### Agent permissions

- `sdet-architect`: implementation within approved scope.
- `sdet-reviewer`: read-only review.
- `spec-analyst`: requirements analysis.
- `report-analyst`: failure analysis and reporting.
- `sdet-refactor-cleaner`: approved refactoring only.
- `doc-updater`: approved documentation changes.
- `sdet-orchestrator`: coordination and verification.

Never claim a permission restriction is technically enforced
unless the active tool configuration enforces it.

## 4. Skills

Skills are stored in:

`.dsh/skills/<skill-name>/SKILL.md`

Use the Harness skill tool to load Skills by exact name.

If the skill tool is unavailable, read the corresponding
SKILL.md directly.

Do not invent Skill names or invocation commands.

### Available Skills

| Skill | When to use |
|---|---|
| `task-workflow` | End-to-end task execution |
| `fetching-test-cases-and-wiki` | Jira, Zephyr, Confluence and source retrieval |
| `capturing-test-cases` | Normalize test cases and obtain approval |
| `api-contract-audit` | Compare API requirements and implementation |
| `page-object-creation` | Create or modify Page Objects and UI components |
| `writing-ui-tests` | Implement UI tests |
| `writing-api-tests` | Implement API tests |
| `allure-annotations-and-naming` | Apply test names, annotations and markers |
| `triaging-test-failures` | Analyze failed and broken tests |

### Skill selection

Load only Skills relevant to the current task.

For UI implementation:

1. `writing-ui-tests`
2. `page-object-creation`, when required
3. `allure-annotations-and-naming`

For API implementation:

1. `writing-api-tests`
2. `api-contract-audit`, when required
3. `allure-annotations-and-naming`

For requirements analysis:

1. `task-workflow`
2. `fetching-test-cases-and-wiki`
3. `capturing-test-cases`, for Zephyr/Jira cases

For test failures:

1. `triaging-test-failures`
2. Delegate to `report-analyst` when appropriate.

### Instruction priority

Follow:

1. Explicit user requirements and task-specific constraints.
2. Actual repository interfaces and verified facts.
3. Relevant specialized Skill instructions.
4. These general project instructions.
5. Existing neighboring code conventions.

When instructions conflict, investigate the contradiction.

Do not silently combine incompatible conventions.
Ask for clarification when the correct choice cannot
be determined from the repository.

## 5. Task Workflow

For substantial automation tasks, load `task-workflow`.

### Stage 1 — Intake

Determine:

- Source task or requirement.
- Target functionality.
- UI or API scope.
- Expected outcome.
- Existing implementation.
- Necessary Skills.

### Stage 2 — Requirements analysis

Use authoritative requirements from:

- Jira
- Zephyr Squad
- Confluence
- Approved task documentation

Verify source availability before relying on it.

Inspect directly linked documents when relevant.
Do not recursively traverse unrelated documentation.

### Stage 3 — Implementation verification

Compare:

- Expected behavior.
- Actual application behavior.
- Existing automated coverage.

Do not invent expected results.

Record contradictions and missing requirements.

### Stage 4 — Approval

For Jira/Zephyr case-driven tasks:

1. Retrieve the source case.
2. Create `docs/tasks/{num}/{num}_cases.md`.
3. Preserve steps and expected results.
4. Identify unresolved questions.
5. Present the document for approval.
6. Wait for explicit human approval.

Do not implement case-driven tests before approval.

Spec-driven and development-task-driven tasks follow their
respective workflows.

### Stage 5 — Implementation

Use the appropriate specialized Skill.

Implement only approved or sufficiently verified behavior.

Prefer focused changes and existing abstractions.

### Stage 6 — Verification

Run relevant static checks and targeted tests
when the environment and task permissions allow them.

Investigate failures before changing expectations.

### Stage 7 — Reporting

Report:

- Changed files.
- Implemented functionality.
- Commands executed.
- Test results.
- Unresolved blockers.
- Remaining risks.

Never claim success without evidence.

## 6. UI Test Conventions

Use Python, pytest and Playwright Sync API.

Follow `writing-ui-tests`.

### Test organization

Preserve the existing UI test structure.

Where the project uses feature-oriented classes:

```python
class TestLogin:
    def test_valid_login(self, page, base_url):
        ...
```

Do not convert existing class-based UI tests into
module-level functions solely because API tests use them.

### Page Objects

Tests use existing Page Object methods.

Example:

```python
login = LoginPage(page, base_url).open()
login.login(username, password)
login.expect_error_visible()
```

Verify actual method contracts before using them.

Keep browser interaction details out of test bodies.

### Synchronization

Prefer:

- Playwright auto-waiting.
- Retrying assertions.
- Observable application state.

Avoid:

- `time.sleep()`.
- Arbitrary retries.
- Excessive global timeouts.

### Isolation

Reuse browser fixtures and BrowserFactory.

Do not initialize independent browsers unnecessarily.

Avoid shared mutable state and test-order dependencies.

Account for pytest-xdist compatibility.

## 7. API Test Conventions

Follow `writing-api-tests`.

Use module-level API test functions unless the current
repository defines a different convention.

Naming:

`test_{service}_{endpoint}_{info?}_{pos|neg}`

Prefer:

- BaseApi.
- Existing service methods.
- Centralized Endpoints.
- Pydantic models.
- Existing authentication fixtures.

Do not inline endpoint paths in service methods.

Do not assert only the Python type of a response.

Validate actual response values and business invariants.

Restore changed application state after write tests.

### API source labels

Use the established test-oracle labels:

- `task` — expected behavior from approved requirements.
- `source_code` — implementation-derived regression behavior.

Do not treat source-derived expectations as business approval.

## 8. Allure and Pytest

Apply `allure-annotations-and-naming` to new or updated tests
where its rules match the current project.

Use meaningful:

- Feature names.
- Scenario titles.
- Descriptions.
- Source links.
- Steps and assertions.

Do not add `@allure.severity` when prohibited by the project.

Do not invent Jira IDs or task markers.

### Project-specific reporting

Some existing test suites may use:

- `step_num`
- `check_step`
- `@allure.testcase`
- Jira task markers

Use these only when required by the applicable workflow
and supported by the current framework.

Do not automatically add these fixtures to UI tests
that do not implement them.

### Markers

Inspect:

- `pytest.ini`
- `conftest.py`

before changing marker registration.

Numeric Jira markers require valid Python syntax:

```python
getattr(pytest.mark, "2936")
```

Do not write invalid expressions such as:

```python
pytest.mark.2936
```

## 9. Test Quality

Tests must:

- Verify meaningful behavior.
- Have deterministic assertions.
- Use appropriate fixtures.
- Avoid duplicate scenarios.
- Preserve test isolation.
- Clean up modified state.
- Avoid unnecessary dependencies.
- Follow current repository formatting conventions.

Do not create tests containing only:

- `pass`
- `...`
- Placeholder comments

Do not remove assertions merely to make tests pass.

### Blocked scenarios

If a substantially implemented test is temporarily blocked:

- Keep the test skipped with the exact reason.
- Document the blocker.
- Notify the requester.

If no meaningful test implementation is possible:

- Do not create a placeholder test.
- Record the scenario as deferred.
- Explain the missing requirement or dependency.

Never ship a green test that silently omits
documented expected results.

Use `xfail` only for verified and documented expected failures.

## 10. Playwright MCP

Playwright MCP may be used for:

- DOM inspection.
- Locator verification.
- Page interaction.
- UI behavior investigation.
- Failure reproduction.

Before using MCP:

1. Confirm the server is connected.
2. Inspect available tools.
3. Use supported tool names.
4. Verify selectors against the actual DOM.

Do not assume MCP is available because it was configured
in another environment.

Never invent selectors or claim browser inspection
when no inspection occurred.

## 11. External Integrations

Available integrations may include:

- Jira Cloud.
- Zephyr Squad Cloud.
- Confluence Cloud.
- Bitbucket.
- Application API.
- Database connections.
- Playwright MCP.

Confirm availability in the current Harness session.

Do not fabricate tool access, retrieved records
or successful external operations.

Credentials and tokens are sensitive.

Never expose secrets in code, logs or reports.

Do not modify production systems or live application data
without explicit authorization.

## 12. Code Review

Use `sdet-reviewer` after significant changes.

Review:

- Architecture compatibility.
- API correctness.
- Locator reliability.
- Test isolation.
- Fixtures and teardown.
- Type safety.
- Assertions.
- Allure conventions.
- Unnecessary complexity.
- Scope violations.

Review findings must contain:

- File and location.
- Problem description.
- Evidence.
- Severity or priority.
- Recommended correction.

Do not report speculative problems as confirmed defects.

## 13. Documentation

Use `doc-updater` after structural changes
when documentation must be synchronized.

Keep documentation consistent with actual implementation.

Do not automatically rewrite authoritative Jira,
Zephyr or Confluence requirements.

Discrepancies in external requirements must be
reported for human review.

## 14. Completion Criteria

Before reporting a completed task:

- [ ] Requirements and scope are understood.
- [ ] Relevant Skills were loaded.
- [ ] Existing code was inspected.
- [ ] Appropriate architecture was reused.
- [ ] No unsupported interfaces were introduced.
- [ ] Changes are limited to the requested scope.
- [ ] Tests and checks were executed when possible.
- [ ] Failures and blockers were investigated.
- [ ] Final diff was reviewed.
- [ ] Significant changes received review when appropriate.
- [ ] Actual outcomes and remaining risks are documented.

Never commit or push changes unless explicitly requested.

## 15. Agent Instruction Design

Keep agent files concise.

- Maximum 150 lines per agent.
- Prefer 40–100 lines.
- Describe the role, responsibilities and restrictions.
- Refer to Skills for implementation details.
- Avoid duplicating detailed Skill instructions.

Keep Skills focused.

- Maximum 400 lines per Skill.
- Prefer 100–250 lines.
- Provide actionable implementation procedures.
- Preserve essential project-specific conventions.
- Avoid unnecessary repetition.

AGENTS.md defines shared behavior.
Agents define responsibilities.
Skills define procedures.

## 16. Known Harness Limitations

The verified DeepSeek Harness environment supports:

- Loading `AGENTS.md`.
- Discovering all nine project Skills.
- Loading Skills through the skill tool.
- Reading all seven agent instruction files.
- Creating anonymous subagents.

The current configuration does not provide
registered named agents from `.dsh/agents/`.

Do not claim that role files are automatically callable.

Anonymous delegation is supported, but role-specific
permissions are not guaranteed by the Markdown files.

Technical read-only enforcement must be verified
against the active sandbox and permission settings.