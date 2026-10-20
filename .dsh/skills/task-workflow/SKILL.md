---
name: task-workflow
description: >-
  Manage the complete SDET task lifecycle: intake, source classification,
  requirements analysis, implementation verification, test-case approval,
  automated test development, execution, failure triage and reporting.
  Use at the beginning of any automation task.
---

# Task Workflow

## Purpose

Coordinate automation tasks from the initial request to the final report.

Follow `AGENTS.md` for global project rules and
`docs/reference/spec_driven_test_requirements.md` for the Definition of Ready.

This skill coordinates other skills rather than duplicating their instructions.

## Related Skills

| Skill | Responsibility |
|---|---|
| `fetching-test-cases-and-wiki` | Retrieve requirements and test cases |
| `capturing-test-cases` | Normalize cases and obtain approval |
| `api-contract-audit` | Verify API contracts |
| `page-object-creation` | Create Page Objects and components |
| `writing-ui-tests` | Implement UI tests |
| `writing-api-tests` | Implement API tests |
| `allure-annotations-and-naming` | Enforce test conventions |
| `triaging-test-failures` | Investigate execution failures |

## 1. Task Intake

Accept a Jira ID, Confluence specification or direct user request.

Example requests:

- `Handle task 3747`
- `Implement test case 2936`
- `Generate API tests from this specification`
- `Continue task 3747`

These are natural-language requests, not registered CLI commands.

Before starting:

1. Read `AGENTS.md`.
2. Inspect existing task documentation.
3. Identify the source and expected deliverables.
4. Determine the task's current workflow stage.
5. Avoid repeating previously completed work.

For continuation, read the existing `task_report.md` checkpoint.

## 2. Classify the Source

Classify the task before selecting implementation skills.

| Source | Workflow |
|---|---|
| Jira/Zephyr Test | Case-driven |
| Jira Story/Task/Improvement | Development-task-driven |
| Confluence specification | Spec-driven |
| Direct user request | Determine source and scope |

Do not treat every Jira issue as a test case.

### Case-driven

Retrieve the case and use `capturing-test-cases`.

Requires explicit approval of the normalized case document.

### Development-task-driven

Read the Jira issue, acceptance criteria and directly linked documents.

No Zephyr case document is required unless the task explicitly uses one.

### Spec-driven

Use the authoritative Confluence specification.

For API specifications, prioritize backend contract coverage.

Do not manufacture Zephyr test cases.

## 3. Analyze Requirements

Check the source against:

`docs/reference/spec_driven_test_requirements.md`

Verify:

- Functional requirements
- Preconditions
- Expected results
- Test data
- User roles
- Environment dependencies
- Scope and testability
- Contradictions between sources

### Linked documents

Inspect direct links from the initial source.

Maximum traversal depth: **one level**.

Do not recursively follow links found inside linked documents.

Validate each link before relying on its content.

| Linked source | Action |
|---|---|
| Confluence | Read intended behavior |
| Zephyr/Jira Test | Extract relevant steps and expectations |
| Related Jira task | Check dependencies and overlapping scope |
| Jira bug | Check status and affected functionality |

### Linked bugs

For a bug with status `Done`:

- Include the confirmed fix in regression coverage when relevant.
- Avoid duplicating an existing test.

For a bug not marked `Done`:

- Do not assert its unresolved behavior as already implemented.
- Record affected scenarios in the deferred backlog.
- Include the bug ID and current status.

## 4. Verify Implementation

Compare requirements against actual application behavior.

Application source code is read-only.

Default source branch: `develop`.

Use available tools:

- `integrations/bitbucket_client.py`
- Existing API services
- Database repositories under `db/`
- Playwright MCP, when connected

Do not assume any integration is connected without checking.

### Verification outcomes

| Verdict | Meaning |
|---|---|
| `Match` | Implementation agrees with requirements |
| `Drift` | Implementation contradicts requirements |
| `Not implemented` | Required behavior is absent |
| `Unknown` | Evidence is insufficient |

Record a side-by-side comparison:

| Data | Required | Implemented | Verdict | Evidence |
|---|---|---|---|---|
| User field | Username | Doctor name | Drift | Spec and source |
| Response status | 200 | 200 | Match | API response |

Use actual evidence instead of placeholder values in real reports.

On contradictions:

1. Record the discrepancy.
2. Identify affected scenarios.
3. Prepare a BA or Development question.
4. Do not invent the correct behavior.
5. Suspend implementation of the affected scenarios.

## 5. Create Task Documentation

Create a task directory:

```text
docs/tasks/{num}/
```

When no numeric identifier exists, use a short snake_case slug:

```text
docs/tasks/upload_template/
```

Required document:

```text
docs/tasks/{num}/task_report.md
```

Use the existing template:

`docs/reference/task_docs_templates.md`

Do not invent a competing report format.

### Task report

Maintain:

- Task source and scope
- Current status
- Last updated date
- Requirements analysis
- Implementation comparison
- Test coverage
- Blocked scenarios
- Execution results
- Follow-up actions

Keep detailed findings in Chapter 3.

### Status

Use the project's existing status values:

- `Done` — completed and verified scope
- `Suspended` — unresolved blockers prevent completion

Never mark an incomplete task as `Done`.

Update status and date whenever the task progresses.

## 6. Record Questions

Create question files only when necessary.

```text
docs/tasks/{num}/
├── task_report.md
├── ba_questions.md
├── dev_questions.md
└── qa_questions.md
```

| File | Owner | Purpose |
|---|---|---|
| `ba_questions.md` | Business Analyst | Requirements and contradictions |
| `dev_questions.md` | Development/DevOps | Implementation and environment |
| `qa_questions.md` | QA | Test-case details and expected results |

Every question should include:

1. Source reference
2. Missing or contradictory information
3. Available evidence
4. Specific decision required
5. Affected test scenarios

Do not silently resolve unanswered questions.

## 7. Present Analysis

Before implementation, report:

- Source classification
- Readiness verdict
- Implementation verification
- Missing requirements
- Contradictions
- Proposed coverage
- Current task status

If the task is suspended, explain the blocker and stop
implementation of affected scenarios.

## 8. Case-Driven Approval Gate

This stage is mandatory for Jira/Zephyr Test cases.

Load `capturing-test-cases`.

Create:

```text
docs/tasks/{num}/{num}_cases.md
```

The document must contain:

- Original case title and source URL
- Preconditions
- Test data
- Ordered actions
- Expected results
- Parametrization, when appropriate
- Automated coverage table
- Source data-quality notes

### Approval procedure

1. Present the completed document.
2. Highlight unresolved assumptions.
3. Request explicit human approval.
4. Stop until approval is received.
5. Revise and present again when requested.
6. Record the approval in `task_report.md`.

**Do not create or modify tests, Page Objects, API services,
fixtures or test data before approval.**

Spec-driven and development-task-driven tasks skip this gate
unless the user explicitly requires case approval.

## 9. Implement Tests

Implementation starts only after:

- Requirements are sufficiently clear.
- Relevant implementation is verified.
- Blocking contradictions are resolved.
- Required case approval is received.

### Select test type

UI is the default for case-driven and development-task-driven
web functionality.

Use:

```text
tests/ui_tests/
```

Use API tests when the scenario explicitly targets an API,
service contract or backend behavior.

Use:

```text
tests/api_tests/
```

Do not implement mobile-native behavior.

### Select Skills

For UI tests:

1. `writing-ui-tests`
2. `page-object-creation`, when needed
3. `allure-annotations-and-naming`

For API tests:

1. `api-contract-audit`, when needed
2. `writing-api-tests`
3. `allure-annotations-and-naming`

### Case mapping

Each approved Jira/Zephyr case maps to one test function.

Example:

```text
Case 1 → test_2936_1
Case 2 → test_2936_2
Case 3 → test_2936_3
```

Do not merge separate cases into one test.

Parametrization is allowed only for variations within
the same scenario with identical steps and expected-result structure.

### Jira markers

Every test originating from a Jira task carries its task marker.

For numeric marker names, use valid Python syntax:

```python
pytestmark = [
    pytest.mark.ui,
    getattr(pytest.mark, "2936"),
]
```

Register manually managed markers in `pytest.ini`.

Follow `allure-annotations-and-naming`.

## 10. Execute Tests

Run targeted tests before broader suites.

Examples:

```bash
pytest -m "2936" -v
```

```bash
pytest tests/ui_tests/ -q
```

Run the actual relevant test path when possible.

Never claim tests passed without execution evidence.

### Failure handling

Load `triaging-test-failures` when execution fails.

Investigate:

- Incorrect test expectations
- Test implementation defects
- Missing preconditions or data
- Environment problems
- Application defects

Fix automation defects and rerun affected tests.

Do not modify assertions merely to make tests pass.

### Blocked tests

If a substantially implemented test cannot execute
because of a verified blocker:

```python
@pytest.mark.skip(
    reason="Blocked: required feature is not available"
)
def test_example():
    ...
```

Do not leave empty placeholder tests.

Scenarios that cannot meaningfully be implemented belong
in the deferred backlog, not as empty test functions.

Never report partial coverage as a passing test.

## 11. Record Results

Update:

```text
docs/tasks/{num}/task_report.md
```

Include:

- Implemented test names
- Modified files
- Executed commands
- Passed/failed/skipped counts
- Identified defects
- Deferred scenarios
- Remaining questions
- Final status
- Last updated date

For execution-level reporting, coordinate with `report-analyst`.

Relevant outputs:

```text
docs/runs/last_run/task_report.md
docs/runs/last_run/test_failure_triage.md
```

Use concise tables rather than long narratives.

## 12. Completion Criteria

A task is complete when:

- [ ] Source classification is recorded.
- [ ] Requirements have been analyzed.
- [ ] Implementation has been checked.
- [ ] Contradictions have been resolved or documented.
- [ ] Case-driven approval was obtained when required.
- [ ] Every approved scenario has a coverage decision.
- [ ] Automated tests follow project architecture.
- [ ] Allure annotations and Jira markers are correct.
- [ ] Relevant tests have been executed.
- [ ] Failures have been triaged.
- [ ] Blockers and deferred work are documented.
- [ ] `task_report.md` is current.
- [ ] Final results have been presented to the user.

## Restrictions

- Never invent requirements or expected behavior.
- Never modify application source code.
- Never bypass mandatory human approval.
- Never silently omit approved test cases.
- Never turn incomplete tests into false green results.
- Never claim execution without evidence.
- Never invent integrations or CLI commands.
- Never commit or push without explicit authorization.