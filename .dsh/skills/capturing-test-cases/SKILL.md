---
name: capturing-test-cases
description: >-
  Capture and normalize Jira/Zephyr test cases into structured Markdown
  documentation. Preserve original test steps and expected results,
  identify missing requirements, and obtain explicit human approval
  before generating automated tests.
---

# Capturing Test Cases

## Purpose

Convert Jira/Zephyr test cases into reviewed and approved
Markdown specifications used to generate automated tests.

Follow `AGENTS.md` for global project rules.

Related skills:
- `fetching-test-cases-and-wiki` — retrieve source cases.
- `task-workflow` — coordinate the complete task lifecycle.
- `writing-ui-tests` — generate UI tests.
- `writing-api-tests` — generate API tests.
- `allure-annotations-and-naming` — apply test metadata.

This skill produces:

`docs/tasks/{num}/{num}_cases.md`

**Never generate test code before explicit human approval.**

## When to use

Use this skill when the source is a Jira `Test` issue
or Zephyr Squad test case with structured:

- Test steps
- Test data
- Expected results
- Preconditions

Do not use it for Confluence-only specifications or
Jira development tasks without actual Zephyr cases.

| Source | Workflow |
|---|---|
| Jira/Zephyr Test | Capture cases and obtain approval |
| Confluence specification | Spec-driven workflow |
| Jira Story/Task/Improvement | Development-task workflow |
| Development task linked to Zephyr case | Determine the authoritative source first |

Do not treat every Jira issue as a test case.

## Workflow

### Step 1 — Retrieve the source case

Use the `fetching-test-cases-and-wiki` skill.

When the existing integration is available:

```bash
python -m integrations.fetch_test_case 2936
```

Or:

```bash
python -m integrations.fetch_test_case 606320 --key 2936
```

The integration returns a normalized `TmsTestCase`.

Example:

```python
from integrations.fetch_test_case import fetch_test_case

case = fetch_test_case("2936")

print(case.key)
print(case.issue_id)
print(case.title)
print(case.test_type)
print(case.priority)

for step in case.steps:
    print(
        step.order,
        step.action,
        step.data,
        step.expected,
        step.status,
    )
```

Do not invent test-case content if integration access is unavailable.

If credentials or access are missing, request the source
document or report the blocker.

Also retrieve relevant linked information:

- Confluence specifications
- Jira development tasks
- Acceptance criteria
- Feature configuration
- Required user roles
- Preconditions
- Environment requirements

Use original sources whenever possible.

### Step 2 — Create the normalized document

Create:

```text
docs/tasks/{num}/{num}_cases.md
```

Follow the project template:

`docs/reference/task_docs_templates.md`

Inspect existing examples when available:

```text
docs/tasks/2936/2936_cases.md
docs/tasks/2820/2820_cases.md
```

Do not replace an existing approved document without reviewing
its current content and confirming the intended changes.

### Document structure

The document must contain:

1. Original test-case title.
2. Jira/Zephyr reference.
3. Short functionality summary.
4. Automated coverage table.
5. Individual case blocks.
6. Source data-quality notes.

Example:

```markdown
## Example test case title

Source: [2936](https://example.atlassian.net/browse/2936)

Verifies editing metadata when the required feature flags
and user permissions are configured.

## Automated coverage

| Case | Automated test | Status |
|---|---|---|
| 1 | test_2936_1 | Pending approval |
| 2 | test_2936_2 | Pending approval |

## Case 1

**Preconditions**

1. User has the required role.
2. Feature flag is enabled.

**Steps**

1. Log in.
2. Open the letter.
3. Click Edit.

**Expected results**

1. Edit button is displayed.
2. Edit modal opens.

---

## Source data-quality notes

- Original case reviewed.
- No unresolved source corrections.
```

Use actual Jira/Zephyr wording in production documents.

The example above illustrates the structure only.

### Automated coverage statuses

The `Automated coverage` table is the central
case-to-test mapping.

Supported statuses:

- `Pending approval`
- `Ready`
- `Automated`
- `Deferred — <blocker>`
- `Skipped — <reason>`

Keep this table synchronized with implementation progress.

Do not mark a case `Automated` merely because a test file exists.
Its implementation must cover the required behavior.

### Step 3 — Preserve source fidelity

Source wording determines the final test steps and assertions.

Rules:

- Preserve original action wording.
- Preserve original expected-result wording.
- Preserve the meaning of test data.
- Keep the order of source steps.
- Normalize list numbering where appropriate.
- Do not omit expected results.
- Do not add unsupported requirements.

These texts will later be used by:

```python
step_num(1, "Original action text")
check_step(1, "Original expected-result text")
```

Refer to `allure-annotations-and-naming` for detailed rules.

### Step 4 — Normalize source formatting

Jira/Zephyr exports may contain formatting artifacts.

Remove unnecessary markup such as:

```text
{color:green}
{noformat}
*[Pass]*
```

Also normalize:

- Broken Markdown formatting
- Repeated text
- Obvious spelling mistakes
- Irrelevant manual execution markers
- Duplicated headings

Every meaningful correction must be documented in:

`## Source data-quality notes`

Never silently change application behavior or acceptance criteria.

If the original wording is ambiguous, preserve it and raise a question.

### Step 5 — Analyze preconditions

Each case must identify relevant prerequisites.

Examples:

- User role
- Authentication state
- Required feature flags
- Existing database records
- Required test data
- Tenant configuration
- Environment capabilities

Use exact configuration names from verified sources.

Example:

```markdown
**Preconditions**

1. User has the required permissions.
2. `ShowClinicDate = 1`.
3. A letter exists in the initial state.
```

Do not invent configuration values.

When source documentation does not provide a required value,
record the ambiguity.

### Step 6 — Handle missing information

Missing case details must be reported to the case owner.

Create or update:

```text
docs/tasks/{num}/qa_questions.md
```

Typical questions:

- What is the required initial state?
- Which role should execute this scenario?
- Which test data should be used?
- What is the expected result?
- Which parameter combinations are required?

Distinguish question owners:

| Question | Owner |
|---|---|
| Missing or ambiguous test-case steps | QA |
| Unclear business behavior | BA |
| Missing implementation or environment capability | Development |

Do not silently fill requirement gaps with guesses.

### Documented assumptions

Sometimes implementation planning can proceed using a
reasonable assumption supported by other project documentation.

Such assumptions must:

1. Be recorded in `qa_questions.md`.
2. Be explicitly identified in the case document.
3. Reference supporting evidence.
4. Remain pending until QA confirms them.

Use the marker:

```markdown
_(assumed — not in source; QA-pending, see `qa_questions.md`)_
```

Example:

```markdown
**Preconditions**

1. `ShowClinicDate = 1`.
   _(assumed — not in source; QA-pending, see `qa_questions.md`)_
```

Do not treat assumptions as approved requirements.

### Step 7 — Analyze parametrization

Parametrize a scenario only when variants:

- Execute the same logical actions.
- Have the same expected-result structure.
- Differ only by input values.
- Can be meaningfully expressed as one test.

Example:

```markdown
**Parametrization**

1. Status = In Progress.
2. Status = Completed.
```

Do not merge scenarios with different:

- Action sequences
- Expected results
- Preconditions
- Business behavior

Separate source cases must not be combined merely to reduce
the number of tests.

When variants require different assertions or workflows,
create separate case blocks and test functions.

### Step 8 — Review coverage completeness

Before requesting approval, verify:

- Every source case has a corresponding document entry.
- Every source step is represented.
- Every expected result is included.
- Required preconditions are identified.
- Test data is documented.
- Parametrization is justified.
- Missing requirements are recorded.
- Source corrections are documented.
- Case-to-test mapping is complete.

Never silently drop a source scenario.

If a case cannot be automated, document the blocker
rather than removing the case from the specification.

### Step 9 — Obtain human approval

**Mandatory approval gate.**

After preparing the document:

1. Present `docs/tasks/{num}/{num}_cases.md`.
2. Highlight the coverage table.
3. Highlight assumptions and unresolved questions.
4. Explicitly request approval.
5. Stop and wait.

Do not create or modify:

- Automated tests
- Page Objects
- API services
- Fixtures
- Test data generators

until the user approves the captured cases.

Approval must be explicit.

Silence or continuation of unrelated conversation
does not count as approval.

### Changes requested during review

When the user requests corrections:

1. Update the case document.
2. Recheck source fidelity.
3. Present the revised document.
4. Request approval again.

Repeat until the user approves.

### Step 10 — Record approval

After approval, update:

```text
docs/tasks/{num}/task_report.md
```

Record:

- Approver
- Approval date
- Approved document
- Outstanding assumptions, if any
- Approved implementation scope

Never fabricate approval information.

### Step 11 — Hand off implementation

Only after approval:

1. Determine whether each case requires UI or API tests.
2. Load `writing-ui-tests` or `writing-api-tests`.
3. Load `page-object-creation` when necessary.
4. Load `allure-annotations-and-naming`.
5. Generate tests from the approved document.
6. Run the tests when the environment permits.
7. Update the automated coverage table.
8. Record deferred or blocked cases.

The approved `{num}_cases.md` remains the contract
against which implementation is checked.

## Required deliverables

Before implementation:

- `docs/tasks/{num}/{num}_cases.md`
- `qa_questions.md`, if necessary
- Explicit human approval

After approval:

- Approval record in `task_report.md`
- Approved case-to-test mapping
- Clear hand-off to implementation skills

## Restrictions

- Never invent test steps or expected results.
- Never silently change source requirements.
- Never omit unresolved cases.
- Never combine scenarios with different expected behavior.
- Never mark incomplete coverage as automated.
- Never implement tests before approval.
- Never fabricate Jira/Zephyr references.
- Never expose credentials.
- Never modify application source code.