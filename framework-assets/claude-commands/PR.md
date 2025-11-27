---
description: Execute code review workflow - manual or automated based on project settings (UC-05)
argument-hint: [task-id]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Code Review Workflow - UC-05

Execute code review for Task {{TASK_ID}} based on project's `manual_mode` setting.

## MANDATORY: RAG-First Search Policy

**Before ANY code review, ALWAYS use RAG search to understand context:**

```bash
# 1. Search for code standards and review guidelines
mcp__claudetask__search_documentation --query="code review standards guidelines" --top_k=10

# 2. Search for patterns in the changed code areas
mcp__claudetask__search_codebase --query="<main changed component/module>" --top_k=20

# 3. Search for security patterns
mcp__claudetask__search_codebase --query="security validation authentication" --top_k=20
```

**Why RAG First for Code Review?**
- Understand project coding standards
- Find similar implementations for comparison
- Identify security patterns used in the project
- Discover related code that should be consistent

---

## Step 1: Check Project Settings

```bash
mcp__claudetask__get_project_settings
```

Look for: `"manual_mode": true` or `false`

---

## Step 2a: Manual Mode (manual_mode = true)

### Notify User
```
Task #{{TASK_ID}} is ready for Code Review.

Manual Mode is enabled - please review the code manually:
- Review the changes in the feature branch
- Check code quality and adherence to standards
- Verify test coverage
- Ensure DoD is met

When review is complete, run: /merge {{TASK_ID}}
```

### Save Stage Result
```bash
mcp__claudetask__append_stage_result --task_id={{TASK_ID}} --status="Code Review" \
  --summary="Awaiting manual code review" \
  --details="Manual mode - user will review and run /merge when ready"
```

**STOP HERE** - Wait for user to complete review and run `/merge`

---

## Step 2b: Automated Mode (manual_mode = false)

### Get Task Details
```bash
mcp__claudetask__get_task --task_id={{TASK_ID}}
```

Extract: `git_branch`, `project_path`

### RAG Context Gathering (MANDATORY)

**Before delegating code review, gather context:**

```bash
# Search for code review guidelines
mcp__claudetask__search_documentation --query="code review checklist standards" --top_k=10

# Search for patterns in changed areas
mcp__claudetask__search_codebase --query="<changed file/module patterns>" --top_k=20

# Search for security best practices
mcp__claudetask__search_codebase --query="security OWASP validation sanitization" --top_k=20

# Search for similar features for comparison
mcp__claudetask__search_codebase --query="<similar feature implementation>" --top_k=20
```

### Delegate Code Review to Agent

Use the Task tool to spawn `fullstack-code-reviewer`:

```
Task(
  subagent_type="fullstack-code-reviewer",
  prompt="""
  Perform code review for Task #{{TASK_ID}}:

  **Branch:** <branch_name>
  **Project path:** <project_path>

  ## MANDATORY: RAG Search First!

  Before reviewing, run these MCP commands to understand context:
  - mcp__claudetask__search_codebase --query="<main changed module> patterns" --top_k=20
  - mcp__claudetask__search_documentation --query="code review standards" --top_k=10
  - mcp__claudetask__search_codebase --query="security validation error handling" --top_k=20

  Use RAG results to:
  1. Understand existing patterns in changed areas
  2. Verify code follows project conventions
  3. Check security patterns are followed

  ## Your Tasks:

  1. **Get the diff:**
     ```bash
     cd <project_path>
     git fetch origin
     git diff main...<branch_name>
     ```

  2. **Review for:**
     - Code quality and best practices (compare with RAG patterns)
     - No security vulnerabilities (OWASP top 10)
     - Proper error handling (match existing patterns)
     - Code follows project conventions (from RAG)
     - No hardcoded secrets or credentials
     - Reasonable performance
     - Tests cover new functionality

  3. **Create review report:**
     Write to: worktrees/task-{{TASK_ID}}/Tests/Report/code-review-{{TASK_ID}}.md

  4. **Return verdict:**
     - APPROVED - all checks pass
     - CHANGES_REQUIRED - issues found (list them)
  """
)
```

### Process Review Results

**If APPROVED:**

```bash
# 1. Save stage result
mcp__claudetask__append_stage_result --task_id={{TASK_ID}} --status="Code Review" \
  --summary="Code review APPROVED - PR ready for merge" \
  --details="All checks passed. Proceeding to merge."
```

Then **IMMEDIATELY** execute: `SlashCommand("/merge {{TASK_ID}}")`

**Note:** Code Review status now includes PR management (PR status was removed).

**If CHANGES_REQUIRED:**

```bash
# 1. Save stage result with issues
mcp__claudetask__append_stage_result --task_id={{TASK_ID}} --status="Code Review" \
  --summary="Code review: Changes required" \
  --details="Issues found: <list from agent>"

# 2. Return to In Progress
mcp__claudetask__update_status --task_id={{TASK_ID}} --status="In Progress" \
  --comment="Code review failed: <issues>"
```

Then in AUTO mode, execute: `SlashCommand("/start-develop")`

---

## CRITICAL FOR AUTO MODE

**When `manual_mode = false` and code review APPROVED:**

1. Save stage result
2. **IMMEDIATELY** execute `/merge {{TASK_ID}}`
3. **DO NOT** say "awaiting user verification"
4. **DO NOT** wait for user action
5. **DO NOT** stop and ask for confirmation

**Note:** PR status was removed. Code Review now handles both review and PR management.

The workflow must be FULLY AUTOMATIC:
```
/PR → fullstack-code-reviewer → APPROVED → /merge → pr-merge-agent → Done
```

---

## RAG Search Patterns for Code Review

```bash
# Code quality patterns
mcp__claudetask__search_codebase --query="clean code SOLID principles" --top_k=20
mcp__claudetask__search_codebase --query="error handling try catch exception" --top_k=20

# Security patterns
mcp__claudetask__search_codebase --query="input validation sanitization" --top_k=20
mcp__claudetask__search_codebase --query="authentication authorization JWT" --top_k=20
mcp__claudetask__search_codebase --query="SQL injection XSS prevention" --top_k=20

# Performance patterns
mcp__claudetask__search_codebase --query="async await performance optimization" --top_k=20
mcp__claudetask__search_codebase --query="database query index optimization" --top_k=20

# Testing patterns
mcp__claudetask__search_codebase --query="test coverage mock assertion" --top_k=20

# Documentation
mcp__claudetask__search_documentation --query="code review checklist" --top_k=10
mcp__claudetask__search_documentation --query="security guidelines OWASP" --top_k=10
```

---

## Flow Summary

```
Manual Mode:
  /PR → Notify user → WAIT → user runs /merge → pr-merge-agent → Done

Auto Mode:
  /PR → RAG search → fullstack-code-reviewer (review) → APPROVED → /merge → pr-merge-agent → Done
  /PR → RAG search → fullstack-code-reviewer (review) → REJECTED → /start-develop (fix issues)
```

---

## Usage

```bash
/PR [task-id]
```

## Preconditions

- Task must be in "Testing" or "Code Review" status
- Testing must be complete
- Feature branch must exist with commits
- Analysis documents in `worktrees/task-{id}/Analyze/`
