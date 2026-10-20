---
name: triaging-test-failures
description: >-
  Analyze failed and broken pytest tests using Allure results.
  Determine the root cause of each failure by comparing test
  expectations, requirements and actual application behavior.
  Classify failures, collect evidence and identify the responsible
  team. Use after test runs with failures.
---

# Triaging Test Failures

## Purpose

Analyze failed or broken automated tests and determine
the root cause and responsible owner.

This skill is **read-only analysis**.

Never modify tests, documentation, application code or
expected results during triage.

Follow `AGENTS.md` for global project rules.

Used by:
- `report-analyst` — reporting and failure classification.
- `sdet-reviewer` — investigation of automation defects.
- `sdet-orchestrator` — coordination and delegation.

## 1. Allure Data Sources

Do not parse `allure-report/index.html`.

The generated HTML report contains embedded JavaScript
and is not a reliable source for structured analysis.

Use the raw files in `allure-results/`.

| Artifact | Location | Contents |
|---|---|---|
| Test results | `*-result.json` | Status, errors, steps, labels, links |
| Containers | `*-container.json` | Setup and teardown fixtures |
| Attachments | `*-attachment.*` | API requests, responses and other evidence |

Important fields:

- `name`
- `fullName`
- `historyId`
- `status`
- `statusDetails.message`
- `statusDetails.trace`
- `labels`
- `links`
- `steps`
- `attachments`

Analyze tests with:

```python
status in {"failed", "broken"}
```

Distinguish test-body failures from setup and teardown failures.

## 2. Failure Analyzer

The project provides:

`tools/analyse_allure_failures.py`

Run:

```bash
python tools/analyse_allure_failures.py
```

Include complete tracebacks:

```bash
python tools/analyse_allure_failures.py --full
```

Analyze skipped tests:

```bash
python tools/analyse_allure_failures.py --status skipped
```

Export machine-readable results:

```bash
python tools/analyse_allure_failures.py \
  --results allure-results \
  --json docs/runs/last_run/failures.json
```

The analyzer:

1. Reads Allure result JSON.
2. Deduplicates reruns using the latest `historyId`.
3. Calculates passed/failed/broken/skipped totals.
4. Groups failures by error signature.
5. Extracts messages and relevant traceback lines.

Possible error signatures:

- Timeout
- Locator failure
- HTTP status mismatch
- Database error
- Assertion failure
- Connection error

**Error signatures are not root causes.**

A timeout may indicate either an automation defect
or an application problem.

The analyst must investigate the underlying cause.

## 3. Root Cause Classification

Assign one primary root cause to every confirmed failure.

| Cause | Description | Owner |
|---|---|---|
| `OUTDATED_TEST_CASE` | Zephyr test case is obsolete; application behavior is correct | BA / QA |
| `OUTDATED_DOCUMENTATION` | Confluence specification is obsolete; application behavior is correct | BA / QA |
| `AUTOMATION_DEFECT` | Test implementation, data, assertions or synchronization are incorrect | SDET |
| `APPLICATION_BUG` | Application contradicts verified requirements | Development |

Optional secondary tag:

`ENVIRONMENT/FLAKY`

Use this for infrastructure, intermittent timing,
shared-state or environment-related problems.

A secondary tag does not replace the primary cause.

### Outdated test case

The automated test correctly reproduces an outdated
Jira/Zephyr test case.

Actions:

1. Identify the outdated source requirement.
2. Document the conflicting application behavior.
3. Route the case to BA/QA.
4. Wait for a human to correct the test case.
5. Update automation only after the source is approved.

**Never automatically modify Zephyr test cases.**

### Outdated documentation

The automated test follows an outdated Confluence specification.

Actions:

1. Identify the obsolete requirement.
2. Collect evidence of actual behavior.
3. Route the discrepancy to BA/QA.
4. Wait for human approval and documentation correction.
5. Update automation afterward.

**Never automatically modify authoritative requirements.**

### Automation defect

The test implementation is incorrect.

Examples:

- Wrong expected value
- Incorrect test data
- Invalid locator
- Wrong endpoint
- Missing precondition
- Race condition
- Broken test isolation
- Incorrect synchronization

Owner: SDET.

The triage skill identifies the defect but does not fix it.

### Application bug

Application behavior contradicts verified requirements.

Examples:

- Unexpected HTTP 500
- Incorrect response data
- Broken API contract
- Missing functionality
- Incorrect business logic

Owner: Development.

Recommend a Jira bug with reproducible evidence.

Do not create tickets without authorization.

## 4. Three-Way Comparison

Root cause is determined by comparing:

1. **Source** — Jira/Zephyr case or Confluence specification.
2. **Test** — implemented assertions and actions.
3. **Application** — observed runtime behavior.

| Test vs source | Application vs source | Verdict |
|---|---|---|
| Different | Matches | Automation defect |
| Matches | Different, but new behavior is approved | Outdated case/documentation |
| Matches | Different, source remains correct | Application bug |
| Matches | Intermittent behavior | Investigate automation, environment and application |

Do not declare the application correct merely
because it consistently behaves a certain way.

Approval or authoritative evidence is required.

### Investigation procedure

For each failure:

1. Read the analyzer output.
2. Inspect the full traceback.
3. Identify the failing test and its dependencies.
4. Determine whether the test is case-driven or spec-driven.
5. Retrieve the original requirement.
6. Inspect actual application behavior.
7. Compare the three sources.
8. Assign the root cause and owner.
9. Record supporting evidence.
10. Hand the verdict to `report-analyst`.

Use `fetching-test-cases-and-wiki` when requirements
must be retrieved.

Use `api-contract-audit` for API contract contradictions.

## 5. Insufficient Evidence

When the root cause cannot be established,
mark the failure:

`NEEDS-INFO`

Specify:

- What is known.
- Which evidence is missing.
- Why a verdict cannot be reached.
- What investigation is needed next.

Never:

- Invent expected results.
- Fabricate a root cause.
- Reinterpret requirements without evidence.
- Force a failure into one of the four categories.
- Repeatedly rerun tests until they become green.

Uncertain findings must remain explicitly uncertain.

## 6. Evidence Collection

### Error messages

`statusDetails.message` contains the failure headline.

Example:

```text
Expected status 200 but got 500
```

### Tracebacks

`statusDetails.trace` identifies the failing call
and relevant source location.

Capture:

- File and line number
- Failing assertion
- Actual value
- Expected value
- Relevant exception

### API failures

Use the existing `BaseApi` / `BaseAssertions` evidence:

- HTTP method
- Endpoint URL
- Request payload
- Response status
- Response body

Avoid exposing tokens, passwords or sensitive data.

An HTTP 500 is not automatically an application bug.
Verify the request, preconditions and contract first.

### UI failures

Inspect:

- Locator uniqueness
- Element visibility
- Loading indicators
- Browser context state
- Page navigation
- Playwright trace, when available

Playwright traces are UI-specific.

Run scripts may reproduce failed UI tests with `--pw-trace`.

Do not expect Playwright traces for API-only failures.

### Database and timing

For intermittent failures, inspect:

- Test data isolation
- Concurrent updates
- Transaction boundaries
- Polling and retry behavior
- Database state
- Shared test fixtures

Use existing `db/` repositories when available.

Treat a failed precondition separately from
a failed application assertion.

Do not assume every setup failure is an automation defect.

## 7. Worked Examples

### Example A — HTTP 500

Test:

`test_recipients_latest_pos`

Failure:

```text
Expected status 200 but got 500
/api/author/recipients/latest-recipients
```

If the request follows the verified contract
and the environment is healthy:

- Cause: `APPLICATION_BUG`
- Owner: Development
- Action: Recommend a Jira bug

### Example B — Inconsistent counts

Test:

`test_letters_search_held_user_filter_pos`

Failure:

```text
held(0) + free(9) != total(10)
```

Three sequential OData calls may observe different states.

Investigate:

- Shared-state changes between requests
- Non-atomic reads
- Incorrect filter implementation

Possible outcomes:

- Incorrect filtering → `APPLICATION_BUG`
- Unstable test snapshot → `AUTOMATION_DEFECT`
- Insufficient evidence → `NEEDS-INFO`

Do not classify before reproducing the behavior.

## 8. Reporting

Hand findings to `report-analyst`.

After each completed run, the reporting workflow
maintains two documents:

```text
docs/runs/last_run/task_report.md
docs/runs/last_run/test_failure_triage.md
```

### Run report

`task_report.md` contains:

- Run description
- Last updated date
- Overall status
- Passed/failed/broken/skipped totals
- Root cause summary
- Required handoffs
- Run history

### Failure triage report

`test_failure_triage.md` contains:

- Failure classification table
- Evidence per failure
- Responsible owner
- Bugs to raise
- Missing information
- Recommended next actions

Suggested table:

| Test | Root cause | Evidence | Owner | Action |
|---|---|---|---|---|
| `test_example` | `AUTOMATION_DEFECT` | Invalid locator | SDET | Fix locator |
| `test_api` | `APPLICATION_BUG` | Verified contract mismatch | Dev | Raise bug |

Keep the two reports synchronized.

Prefer concise Markdown tables.

Link Jira and Confluence sources instead of
duplicating entire specifications.

Collapse previous runs into one run-history table.

**This skill performs analysis only.**
Report updates are the responsibility of `report-analyst`.

## 9. Preconditions

Required:

- Completed pytest execution
- Available `allure-results/`
- Relevant test implementation
- Access to requirements when needed

Generate the HTML report if necessary:

```bash
allure generate allure-results \
  --clean \
  --single-file \
  -o allure-report
```

HTML generation is optional for triage.

Live API or database verification may require
credentials already configured in `.env`.

Never expose credentials.

## 10. Completion Criteria

Triage is complete when:

- [ ] Every failed/broken test is identified.
- [ ] Reruns are deduplicated.
- [ ] Relevant tracebacks are inspected.
- [ ] Test expectations are compared with requirements.
- [ ] Actual application behavior is considered.
- [ ] Confirmed failures have a root cause.
- [ ] Uncertain failures are marked `NEEDS-INFO`.
- [ ] Every finding contains evidence.
- [ ] Every confirmed cause has an owner.
- [ ] Results are handed to `report-analyst`.
- [ ] No tests, requirements or application files were modified.