DeepSeek Harness — installation and validation
This directory contains 7 role instruction files, 9 complete Skills and a project AGENTS.md.
Apply
1. Back up the existing .dsh/ and any existing project governance documentation.
2. Copy AGENTS.md to the repository root and .dsh/agents/ and .dsh/skills/ to the corresponding workspace paths.
3. Review the actual git diff before staging or committing. Merge any additional project-specific rules into AGENTS.md rather than silently dropping them.
4. In Harness using the standard preset, ask it to list discoverable Skills. Confirm all nine names load successfully and that skill text is actually read.
5. Ask the main agent to read .dsh/agents/sdet-reviewer.md and delegate a read-only diff review using an anonymous subagent. Confirm that it did not modify the workspace.
6. Try a small UI Page Object task through the page-object-creation Skill and sdet-architect role; review the generated diff and targeted validation results.
Harness behavior that matters
Role Markdown files are not automatically registered named subagents in the inspected configuration. The parent must supply the complete role instructions to an anonymous child, and use actual permission settings to protect read-only work. The nine Skills are discoverable under the existing .dsh/skills/ directory in the observed session.

Task handling uses regular natural-language requests, for example: "Apply task-workflow to task 2936" or "Resume task 2936 using docs/tasks/2936/task_report.md". These instructions do not register CLI aliases.

The exact availability of Jira/Zephyr/Confluence, application source and Playwright MCP must be checked in the running session. The source project's full original governance document was not provided, so AGENTS.md must be reconciled with any additional real repository rules before becoming authoritative.