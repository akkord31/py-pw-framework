---
name: triaging-test-failures
description: >-
  Investigate failed or broken pytest runs using raw Allure result JSON,
  tracebacks, and attachments. Classify automation defects, application
  defects, requirement gaps, and environment blockers with evidence. Use when
  a UI or API test fails and the cause is not yet established.
---

# Triaging Test Failures

## When to use

Use this Skill after a pytest run reports failed, broken, or unexpectedly
skipped tests. It is read-only analysis: do not modify tests, Page Objects,
clients, fixtures, application code, or expected results during triage.

Follow `AGENTS.md` for global rules. Load `writing-ui-tests`,
`writing-api-tests`, or `page-object-creation` only when the task moves from
diagnosis to a fix.

## 1. Evidence sources

Do not parse the generated HTML Allure report; its embedded JavaScript is not
a reliable structured source. Use the raw files in the run's Allure results
directory. Use the actual `--alluredir` path from the pytest invocation.

| Artifact | Contents |
|---|---|
| `*-result.json` | name, fullName, historyId, status, statusDetails, labels, links, steps, attachments |
| `*-container.json` | fixture/setup/teardown containers |
| `*-attachment.*` | logs, screenshots, API payloads, Playwright traces |

Also inspect:

- The exact pytest command and exit code.
- The failing test function and its Page Object/client call chain.
- The relevant conftest/fixtures and test data.
- The requirement or approved TMS case when one exists.
- `pytest.ini` markers and `--tb` output.

Never fabricate a run, traceback, attachment, or requirement.

## 2. Triage procedure

1. List every `failed` and `broken` result; include unexpected skips.
2. Deduplicate reruns by `historyId`, keeping the latest result.
3. Read `statusDetails.message` and the relevant traceback.
4. Distinguish a test-body failure from setup/teardown failure.
5. Identify the first meaningful failure, not later cascade errors.
6. Inspect attachments, especially Playwright traces and HTTP payloads.
7. Compare source expectation, test implementation, and observed behavior.
8. Assign one primary cause and an evidence statement.
9. Recommend the smallest owner-specific next action.

For a suspected flaky failure, look for timing, locator, shared-state,
test-order, environment, and data-isolation signals before blaming the
application. A timeout or missing element is a symptom, not a root cause.

## 3. Classification

| Cause | Meaning | Typical owner |
|---|---|---|
| `AUTOMATION_DEFECT` | Wrong assertion/data/locator/flow, missing wait, isolation defect | SDET/automation |
| `APPLICATION_BUG` | Application contradicts verified requirements | Development |
| `REQUIREMENT_GAP` | Source is missing, ambiguous, or outdated | BA/QA/source owner |
| `ENVIRONMENT` | Browser, network, service, credentials, or data unavailable | Environment/DevOps |
| `UNCONFIRMED` | Evidence is insufficient for a primary cause | Requester |

Do not mark an application bug merely because observed behavior differs from
an unverified test. Do not mark an automation defect merely because the test
failed. Use one primary cause; add an optional `FLAKY` note only as a secondary
observation.

## 4. Three-way comparison

Compare:

1. **Source** — approved TMS case, spec, or development-task requirement.
2. **Test** — actions and assertions actually implemented.
3. **Application** — evidence from the run, not assumptions.

| Test vs source | Application vs source | Verdict |
|---|---|---|
| Differs | Matches | Automation defect |
| Matches | Differs; source outdated | Requirement gap |
| Matches | Differs; source valid | Application bug |
| Matches | Intermittent/unclear | Investigate isolation/environment; `UNCONFIRMED` if needed |

If no authoritative source exists, state that limitation. Observed behavior
alone does not prove intended behavior.

## 5. Evidence standard

Each finding must include:

- Test ID and file/line.
- Status (`failed` or `broken`) and the primary error.
- The relevant traceback lines or attachment.
- The expectation and observed result.
- The root-cause classification and confidence.
- The smallest recommended action and owner type.
- Any missing evidence or unresolved question.

Do not report speculative causes as confirmed. Mark uncertain findings
`UNCONFIRMED`; do not invent a root cause.

## 6. Reporting

Present a concise table in the response:

| Test | Cause | Evidence | Recommended action |
|---|---|---|---|
| `test_example` | `AUTOMATION_DEFECT` | Locator no longer matches DOM | Fix locator in Page Object |
| `test_api` | `APPLICATION_BUG` | Verified contract mismatch | Raise with Development |

Also report:

- Command and exit code.
- Passed/failed/broken/skipped counts.
- Scope of the triage (which tests/directories).
- Coverage or evidence gaps.
- Whether a fix was made or the task remains diagnostic.

Do not create report files or update requirements unless the user asks.
Never create a Jira bug or change a TMS case without authorization.

## 7. Completion criteria

- [ ] Every failed/broken test is accounted for.
- [ ] Reruns are deduplicated.
- [ ] Setup/teardown failures are distinguished from test-body failures.
- [ ] Actual evidence is cited.
- [ ] Confirmed failures have one primary cause and owner type.
- [ ] Uncertain failures are `UNCONFIRMED`.
- [ ] Recommended actions do not weaken assertions.
- [ ] Missing source/evidence is reported rather than guessed.
- [ ] No production, test, fixture, or requirement file was modified.
