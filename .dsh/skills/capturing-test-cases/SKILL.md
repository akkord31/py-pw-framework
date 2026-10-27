---
name: capturing-test-cases
description: >-
  Normalize an externally sourced Jira, Zephyr, or TMS MCP test case into a
  reviewable specification and obtain explicit human approval before creating
  UI or API tests. Preserve original steps, data, preconditions, and expected
  results; report gaps instead of inventing them.
---

# Capturing Test Cases

## When to use

Use this Skill when the task implements a test case imported from an external
TMS, including Jira/Zephyr Test issues and cases returned by a connected TMS
MCP tool.

Do not use it for:
- A Confluence specification with no TMS case.
- A Jira Story, Task, or Improvement without a test case.
- A direct user request that defines its own expected behavior.

Those sources follow their own requirements. Do not treat every Jira issue as a
test case.

Follow `AGENTS.md` for global rules. This Skill is the mandatory approval
procedure for externally sourced cases.

## 1. Obtain the source

Use the source supplied by the user or an integration that is actually
connected in this session.

- If a TMS MCP tool is available, inspect its exact name/schema and use it.
- If no integration is available, ask for the case export or a complete
  description. Report the blocker; do not invent case content.
- Inspect directly linked evidence only when supplied: related Jira issue,
  specification, acceptance criteria, or attachments.
- Do not recursively crawl unrelated documentation.
- Do not modify application source or external TMS records.

Never fabricate a case ID, title, step, expected result, URL, or status.

## 2. Capture the original content

Preserve the source's meaning before imposing structure:

- Case ID, title, source URL/reference.
- Status/priority and owner, when present.
- Preconditions and required role/permissions.
- Environment, configuration, and feature flags.
- Ordered actions with exact test data.
- Expected result after each action or at the defined checkpoint.
- Parametrization or variants explicitly present in the source.
- Linked requirements or bugs that constrain behavior.

If a step or expected result is missing, record the gap. Do not fill it with a
guess.

## 3. Normalize for review

Present a self-contained normalization in the response. Create a file only when
the user explicitly requests one and approves the path; do not assume a
task-document directory or template exists in this repository.

Use this structure:

```markdown
## Case <id> — <title>

Source: <real URL or reference>
Status/priority: <source values>
Preconditions:
1. ...
Test data:
- ...
Steps and expected results:
1. Action: ...
   Expected: ...
Automated coverage:
| Case | Proposed test | Status |
|---|---|---|
| <id> | test_<id>[_<n>] | Pending approval |
Open questions:
- ...
Source notes:
- ...
```

Rules:

- Preserve original wording when it defines expected behavior.
- Keep the case-to-test mapping explicit.
- Do not merge separate cases into one test.
- Do not claim coverage before implementation.
- Do not invent test data, credentials, or environment values.

## 4. Identify gaps and assumptions

List unresolved questions separately from approved content:

- Missing precondition or initial state.
- Ambiguous action or expected result.
- Missing role, permission, or feature flag.
- Unclear test data or cleanup.
- Contradiction between the case and linked requirement.
- Behavior that cannot be automated with the current framework.

If an assumption is necessary to explain the case, label it explicitly as an
assumption, cite the supporting evidence, and keep it pending until the source
owner confirms it. Do not silently turn an assumption into a requirement.

## 5. Parametrization and coverage

Parametrize only when variants:

- Use the same logical actions.
- Have the same expected-result structure.
- Differ only in input values or a clearly bounded configuration.

Do not combine scenarios with different actions, preconditions, expected
results, or business behavior. Each approved source case must have a coverage
decision: automated, deferred, or blocked, with a reason.

## 6. Mandatory human approval

Before creating or modifying any test, Page Object, client, fixture, or test
data:

1. Present the normalized case(s).
2. Highlight assumptions, open questions, and coverage decisions.
3. Request explicit approval.
4. Stop and wait for the response.
5. If changes are requested, revise and present again.

**Approval cannot be inferred** from silence, an unrelated request, or a
general instruction to continue. Record the approval and approved scope in the
final report; do not fabricate an approver or date.

If the user rejects or suspends a case, do not implement it. Keep the blocker
and affected scenarios visible.

## 7. After approval

Only after explicit approval:

1. Choose UI or API implementation based on the approved behavior.
2. Load `writing-ui-tests` or `writing-api-tests`, plus
   `page-object-creation` when a Page Object/component is needed.
3. Load `allure-annotations-and-naming` when adding metadata.
4. Implement only approved scenarios; preserve the approved meaning.
5. Run the focused tests and report execution evidence.
6. Report deferred, blocked, or partially covered cases honestly.

Do not silently omit an approved case. Do not create a placeholder test for a
scenario that cannot be implemented; report it as deferred or blocked.

## 8. Completion checklist

- [ ] Source is identified and available.
- [ ] Original steps, data, preconditions, and expected results are preserved.
- [ ] Gaps and assumptions are explicit.
- [ ] Each case has a coverage decision.
- [ ] No test, Page Object, client, fixture, or test data was created before
      approval.
- [ ] Human approval is explicit and recorded.
- [ ] Only approved scenarios were implemented.
- [ ] Deferred/blocked cases and missing evidence are reported.
