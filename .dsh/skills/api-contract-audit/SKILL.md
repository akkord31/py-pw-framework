---
name: api-contract-audit
description: >-
  Audit API contracts against Confluence specifications, application
  source code and Swagger. Identify contradictions, document questions
  for BA/Dev and maintain the merged OpenAPI specification.
---

# API Contract Audit

## Purpose

Audit API contracts before implementing or updating API tests.

This skill ensures that tests are based on verified requirements
rather than assumptions about application behavior.

Follow `AGENTS.md` for project-wide rules.

Related skills:
- `fetching-test-cases-and-wiki` — retrieve Confluence requirements.
- `writing-api-tests` — implement tests based on verified contracts.

## Sources of truth

The following sources have distinct responsibilities:

1. **Confluence** — intended application behavior.
2. **Application source code** — actual implementation.
3. **Swagger/OpenAPI** — consolidated API contract.
4. **Live API responses** — runtime evidence.

Application source code refers to the separate application repository,
not the automation framework.

The application repository is read-only. Use branch `develop`.

Never modify application source code.

## Contract labels

Source labels are described in:

`docs/reference/source_labels.md`

The consolidated specification is stored in:

`docs/reference/swagger/openapi.json`

Supported `x-labels` values:

- `source_code` — endpoint confirmed by application source.
- `task` — endpoint documented in Confluence.

Confluence information is represented by the `task` label.

### Label interpretation

| Labels | Meaning |
|---|---|
| `source_code` | Confirmed implementation |
| `task` | Documented requirement, not confirmed |
| `source_code`, `task` | Present in both sources |

Endpoints documented only in Confluence must have:

```json
{
  "x-labels": ["task"],
  "x-unverified": true
}
```

Preserve their provenance using:

- `x-confluence-pages`
- `x-raw-paths`

Never invent endpoints, HTTP methods, response statuses or schemas.

## Conflict resolution

When Confluence contradicts the implementation:

1. Preserve source-derived information in the merged Swagger.
2. Record the discrepancy.
3. Ask the BA which behavior is intended.
4. Ask Development which behavior is implemented.
5. Do not create requirement-based assertions until the conflict
   has been resolved.

**Important:** Actual application behavior does not automatically
become the expected requirement.

The source-wins rule applies only to merging conflicting data into
the consolidated Swagger. It does not resolve business requirements.

## Workflow

### Step 1 — Verify prerequisites

Confirm that the repository contains:

- `docs/reference/swagger/openapi.json`
- `tools/generate_openapi.py`
- `tools/extract_confluence_api.py`
- `tools/compare_swaggers.py`
- `tools/compare_api_contracts.py`
- `tools/merge_confluence_into_swagger.py`
- `tools/check_tests_vs_swagger.py`

Do not invent missing scripts or paths.

If a required script is absent, report the blocker and adapt only
after inspecting the repository.

Confluence access may require:

- `JIRA_EMAIL`
- `JIRA_API_TOKEN`

Never expose credentials in logs or reports.

### Step 2 — Generate source Swagger

```bash
python -m tools.generate_openapi
```

This generates the source-derived API specification.

**Warning:** Regeneration may replace previously merged Confluence
metadata. Always perform the merge again afterward.

### Step 3 — Extract Confluence contracts

```bash
python -m tools.extract_confluence_api
```

Expected output:

`docs/reference/swagger/openapi_confluence.json`

The extraction collects available evidence, including:

- HTTP methods
- Endpoint paths
- Nearby status codes
- Nearby request/response fields
- Confluence page references

Proximity-derived data is low-confidence evidence.

Do not treat nearby text as a verified contract.

Preserve original endpoint strings in `x-raw-paths`.

### Step 4 — Compare endpoint topology

```bash
python -m tools.compare_swaggers
```

Expected report:

`docs/reference/swagger/confluence_vs_source_diff.md`

Classify endpoints as:

- Present in both sources
- Confluence-only
- Source-only

Do not automatically assume that a missing endpoint is a defect.

### Step 5 — Compare complete contracts

```bash
python -m tools.compare_api_contracts
```

Expected output:

`docs/reference/swagger/api_contract_contradictions.json`

Review differences in:

- HTTP methods
- Endpoint paths
- Request body schemas
- Response body schemas
- Status codes
- Required fields
- Missing contract information

Classify findings:

| Finding | Handling |
|---|---|
| Method contradiction | High priority |
| Response status contradiction | Verify against authoritative sources |
| Request/response schema divergence | Verify |
| Missing specification | Record documentation gap |
| Missing implementation | Confirm with Development |

Do not convert uncertain extraction results into definitive defects.

### Step 6 — Prepare BA and Dev questions

Store unresolved issues in:

```text
docs/tasks/api_contract_audit/
├── ba_questions.md
└── dev_questions.md
```

**BA questions** clarify intended requirements.

**Dev questions** clarify actual implementation.

Each question should contain:

- HTTP method and endpoint
- Confluence reference
- Observed source behavior
- Description of the contradiction
- Specific question requiring an answer
- Current verification status

Do not silently resolve contradictions.

### Step 7 — Merge contracts

```bash
python -m tools.merge_confluence_into_swagger
```

The merge must:

- Preserve confirmed `source_code` definitions.
- Attach `task` labels where Confluence documents an endpoint.
- Add Confluence-only endpoints as unverified.
- Preserve page references and raw endpoint strings.
- Avoid duplicating previously merged endpoints.
- Avoid replacing verified methods or schemas with conflicting text.

Run the merge after source Swagger generation.

### Step 8 — Verify API tests against Swagger

```bash
python -m tools.check_tests_vs_swagger
```

Inspect the results:

| Status | Action |
|---|---|
| `OK` | Contract and service call match |
| `METHOD-MISMATCH` | Investigate source/Swagger discrepancy |
| `MISSING` | Check whether the endpoint is live or unused |
| `UNRESOLVED` | Investigate dynamic URL construction |

Never remove an endpoint or service method solely because the
comparison report marks it as missing.

Confirm actual usage before recommending deletion.

## Regeneration order

When refreshing the entire contract, use:

```bash
python -m tools.generate_openapi
python -m tools.extract_confluence_api
python -m tools.merge_confluence_into_swagger
```

Then run the comparison and validation tools.

Do not reverse the source-generation and merge steps.

## Test authoring rules

Before writing assertions, establish the test oracle.

### Confirmed in both sources

Labels:

`["source_code", "task"]`

Use the verified specification as the intended behavior.

Example:

```python
@allure.label("oracle", "task")
```

### Source-only endpoint

Labels:

`["source_code"]`

Use for implementation-based regression or characterization tests.

Example:

```python
@allure.label("oracle", "source_code")
```

Do not describe existing implementation behavior as an approved
business requirement.

### Confluence-only endpoint

Labels:

`["task"]`

And:

`"x-unverified": true`

Before writing a test:

1. Confirm that the endpoint exists.
2. Validate the HTTP method.
3. Verify the actual response.
4. Resolve any requirement contradictions.

Do not assert behavior for an endpoint that may not exist.

## Deliverables

A completed audit should produce, as applicable:

- Updated `openapi.json`
- Confluence-derived Swagger
- Endpoint topology comparison
- Contract contradiction report
- BA questions
- Development questions
- Test-to-Swagger validation results

Report:

1. Confirmed contracts
2. Discrepancies
3. Unverified endpoints
4. Blocked assertions
5. Required BA/Dev decisions

## Restrictions

- Never modify application source code.
- Never invent API behavior.
- Never fabricate documentation references.
- Never expose Atlassian credentials.
- Never treat extracted nearby text as certain.
- Never silently overwrite conflicting source definitions.
- Never commit or push changes without explicit authorization.
- Never report an unresolved contract as verified.