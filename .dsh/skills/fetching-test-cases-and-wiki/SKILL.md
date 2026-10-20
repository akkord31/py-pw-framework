---
name: fetching-test-cases-and-wiki
description: >-
  Retrieve requirements and test cases from Confluence, Jira and Zephyr
  Squad Cloud. Read application source code through Bitbucket when
  needed. Use before implementing tests to verify source requirements,
  expected results, preconditions and API contracts.
---

# Fetching Test Cases and Wiki

## Purpose

Retrieve authoritative requirements and test-case data before
generating automated tests.

Follow `AGENTS.md` for global project rules.

Related skills:
- `capturing-test-cases` — normalize and approve Zephyr test cases.
- `api-contract-audit` — compare API specifications.
- `writing-api-tests` — implement API tests.
- `writing-ui-tests` — implement UI tests.

Never invent requirements or expected results.

## Source selection

Choose the retrieval workflow based on the task type.

| Task type | Primary source |
|---|---|
| Spec-driven API tests | Confluence |
| Jira/Zephyr case-driven tests | Zephyr Squad |
| Jira development task | Jira and linked specifications |
| API implementation investigation | Bitbucket application source |
| Existing automation investigation | Local automation repository |

### Spec-driven mode

Spec-driven mode is the default for new API tests.

When generating tests directly from Confluence:

1. Retrieve the specification.
2. Extract backend/API requirements.
3. Identify endpoints, parameters and expected results.
4. Inspect application source if needed to understand implementation.
5. Probe the live API when needed to verify actual behavior.
6. Report missing or contradictory information.

Do not create or retrieve Zephyr test cases merely to fill gaps
in a Confluence-based task.

A runtime observation is evidence of implementation behavior,
not automatic proof of the intended requirement.

### Case-driven mode

Use Zephyr Squad when the task explicitly references a
Jira/Zephyr test case.

Retrieve:

- Test-case ID and title
- Priority
- Preconditions
- Ordered test steps
- Test data
- Expected results
- Related Jira/Confluence documentation

After retrieval, load `capturing-test-cases`.

Do not generate test code until the normalized case document
has received explicit human approval.

## Scope restrictions

The automation framework covers:

- Backend APIs
- Web application functionality
- Supported service integrations

Mobile-only functionality is out of scope.

Examples:

- Android/iOS native controls
- Device camera behavior
- Native mobile alerts
- Mobile-specific pickers

When a specification contains mobile requirements:

1. Extract testable backend behavior.
2. Extract testable web behavior.
3. Identify mobile-only requirements separately.
4. Report excluded coverage.

Prefer API coverage before UI coverage where appropriate.

## Source terminology

"Application source code" means the separate application repository.

It does not mean this automation repository.

Rules:

- Application source is read-only.
- Use branch `develop`.
- Never modify application source files.
- Never create commits in the application repository.
- Do not infer expected behavior solely from implementation.

## Data sources

| Source | Integration | Authentication |
|---|---|---|
| Confluence Cloud | Atlassian MCP or REST client | OAuth or Atlassian API token |
| Jira Cloud | Atlassian MCP or REST client | OAuth or Atlassian API token |
| Zephyr Squad Cloud | ZAPI client | JWT |
| Bitbucket Cloud | REST client | Bitbucket API token |

The integrations are not interchangeable.

**Important:** Atlassian MCP does not provide direct access
to Zephyr Squad test steps.

Use the project's ZAPI client for Zephyr data.

## Validate source links

Before relying on a linked Jira or Confluence page,
verify that the resource is accessible.

Available project commands:

```bash
python -m tools.validate_links \
  --url "<source-url>" \
  --check-availability
```

Audit repository links:

```bash
python -m tools.validate_links --check-availability
```

Programmatic validation:

```python
from helpers.link_validator import Clients, validate_link

check = validate_link(
    url,
    clients=Clients.build(),
    check_reachability=True,
)

print(check.approved)
print(check.likely_outdated)
```

Rules:

- An unapproved host is not a trusted source.
- An inaccessible resource may be outdated or temporarily unavailable.
- Do not silently substitute another page.
- Record unresolved source problems in the task documentation.

## Channel A — Confluence and Jira

### Atlassian MCP

Use the official Atlassian MCP integration when configured
and available in the current DeepSeek Harness session.

Server endpoint:

```text
https://mcp.atlassian.com/v1/sse
```

Authentication uses browser-based OAuth.

Before making MCP calls:

1. Confirm the server is connected.
2. Inspect the available MCP tools.
3. Confirm access to the required Confluence space or Jira project.
4. Use only tools actually exposed by the session.

Do not assume MCP is connected because a skill mentions it.

### Confluence retrieval

For a specification:

1. Locate the authoritative page.
2. Read the complete relevant content.
3. Follow related specification links.
4. Extract functional requirements.
5. Extract API endpoints and expected responses.
6. Identify ambiguities and missing information.
7. Preserve original page URLs.

Do not invent page IDs or specifications.

### REST fallback

When MCP is unavailable, use the existing
Confluence REST client if configured.

File:

`integrations/confluence_client.py`

Example:

```python
from integrations.confluence_client import ConfluenceClient

client = ConfluenceClient()

page = client.get_page("123456")

page = client.get_page_by_title(
    "App",
    "Edit the job's data",
)

results = client.search(
    'space = APP AND title ~ "Edit job"',
    limit=10,
)

text = ConfluenceClient.storage_to_text(page)
```

The client uses:

- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Do not print or expose credentials.

If neither MCP nor REST is available, report the blocker.

### Confluence API extraction

For API contract analysis, run:

```bash
python -m tools.extract_confluence_api
```

Expected output:

```text
docs/reference/swagger/openapi_confluence.json
```

Then load `api-contract-audit`.

Extracted nearby status codes or field names are evidence,
not automatically verified contract definitions.

### Confluence attachments

Architecture diagrams may be stored as page attachments.

Use the authenticated Confluence REST endpoint:

```text
GET /wiki/rest/api/content/{page_id}/child/attachment
```

Download only required attachments and preserve their source.

Relevant local destinations:

```text
docs/reference/diagrams/
docs/reference/architecture_frontend_services.md
```

Do not invent diagrams or architecture relationships.

## Channel B — Zephyr Squad Cloud

Use the existing Zephyr Squad client.

File:

`integrations/zephyr_squad_client.py`

Class:

`ZephyrSquadClient`

The client signs ZAPI requests using JWT.

### Required environment variables

```dotenv
ZEPHYR_ACCOUNT_ID=<account-id>
ZEPHYR_ACCESS_KEY=<access-key>
ZEPHYR_SECRET_KEY=<secret-key>
ZEPHYR_VERSION_ID=<jira-version-id>

JIRA_EMAIL=<email>
JIRA_API_TOKEN=<api-token>
```

Read credentials from the environment.

Never hardcode them in source files.

Never include their values in logs, reports or responses.

### Verified API characteristics

Base URL:

```text
https://prod-api.zephyr4jiracloud.com/connect
```

JWT uses:

- `sub` — Atlassian account ID
- `iss` — Zephyr access key
- `iat` — issued-at timestamp
- `exp` — expiration timestamp
- `qsh` — canonical request hash

The `qsh` path is relative to the add-on base.

Do not include `/connect` in the canonical request path.

Including it may cause `401 qsh mismatch`.

Relevant endpoints:

```text
GET /public/rest/api/1.0/serverinfo
GET /public/rest/api/2.0/teststep/{issueId}?projectId=
```

The test-step endpoint requires a numeric Jira issue ID.

Resolve issue keys through Jira when necessary.

### Retrieve a test case

By Jira key:

```bash
python -m integrations.fetch_test_case 2936
```

By numeric issue ID:

```bash
python -m integrations.fetch_test_case 606320 --key 2936
```

Programmatic retrieval:

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

The result is a normalized `TmsTestCase`.

Priority is informational.

Do not map Jira priority or Zephyr step priority
to `@allure.severity`.

The project does not use `@allure.severity`.

### Case-driven handoff

After retrieval:

1. Load `capturing-test-cases`.
2. Write `docs/tasks/{num}/{num}_cases.md`.
3. Preserve all source steps and expected results.
4. Identify unresolved requirements.
5. Request human approval.
6. Wait for approval before implementing tests.

## Channel C — Bitbucket application source

Use this channel to inspect actual application implementation.

File:

`integrations/bitbucket_client.py`

Class:

`BitbucketClient`

Required credentials:

- `BITBUCKET_EMAIL`
- `BITBUCKET_API_TOKEN`

The client must be used for read-only inspection.

Example:

```python
from integrations.bitbucket_client import BitbucketClient

client = BitbucketClient()

client.get_current_user()

repository = client.get_source_repository()

branch = repository["mainbranch"]["name"]

source = client.get_file(
    "src/App/Startup.cs",
    ref="develop",
)
```

Rules:

- Read application source from `develop`.
- Do not modify application source.
- Do not create branches, commits or pull requests.
- Verify discovered endpoints against the live service.
- Do not treat implementation behavior as approved requirements.

### Extract backend endpoints

When the project tool is available:

```bash
python -m tools.extract_endpoints
```

Expected outputs:

```text
docs/reference/endpoints.md
docs/reference/endpoints.json
```

Source-derived endpoints may include:

- Administrative endpoints
- Mobile-only endpoints
- Write operations with special preconditions
- Endpoints unavailable in the current environment

Do not automatically generate tests for every discovered endpoint.

## Coverage traceability

To analyze requirement coverage, use:

```bash
python -m tools.coverage_report
```

For a specific feature:

```bash
python -m tools.coverage_report \
  --feature "Sample ID" \
  --with-steps
```

Expected report:

```text
docs/runs/stats/requirements_automation_coverage.md
```

Coverage categories include:

- `AUTOMATED`
- `MANUAL ONLY`
- `NO TEST CASE`

Traceability chain:

Confluence requirement → Jira/Zephyr case → automated test.

Do not classify a requirement as automated without
verifying the corresponding test implementation.

## Output

Return the retrieved information in a structured summary:

1. Source URLs and identifiers
2. Requirement or test-case title
3. Preconditions
4. Relevant functionality
5. Ordered actions and expected results
6. Required test data
7. API endpoints, if applicable
8. Missing or contradictory information
9. Recommended next skill

For case-driven work, hand off to `capturing-test-cases`.

For spec-driven API work, hand off to `api-contract-audit`
or `writing-api-tests` as appropriate.

## Restrictions

- Never invent Jira, Confluence or Zephyr content.
- Never assume an integration is available without checking.
- Never reveal credentials.
- Never modify application source.
- Never silently change source requirements.
- Never use Zephyr to fill gaps in Confluence-only tasks.
- Never treat a live API response as an approved requirement.
- Never implement case-driven tests before human approval.