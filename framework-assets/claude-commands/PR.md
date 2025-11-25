---
description: Execute code review workflow - manual or automated based on project settings (UC-05)
argument-hint: [task-id]
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Code Review Workflow - UC-05

Execute code review for Task {{TASK_ID}} based on project's `manual_mode` setting.

## Step 1: Check Project Settings

```bash
mcp__claudetask__get_project_settings
```

Look for: `"Manual Mode": True` or `False`

---

## Step 2a: Manual Mode (manual_mode = true)

### Notify User
```
✅ Task #{{TASK_ID}} is ready for Code Review.

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

### Delegate Code Review to Agent

Use the Task tool to spawn `fullstack-code-reviewer`:

```
Task(
  subagent_type="fullstack-code-reviewer",
  prompt="""
  Perform code review for Task #{{TASK_ID}}:

  **Branch:** <branch_name>
  **Project path:** <project_path>

  ## Your Tasks:

  1. **Get the diff:**
     ```bash
     cd <project_path>
     git fetch origin
     git diff main...<branch_name>
     ```

  2. **Review for:**
     - ✅ Code quality and best practices
     - ✅ No security vulnerabilities (OWASP top 10)
     - ✅ Proper error handling
     - ✅ Code follows project conventions
     - ✅ No hardcoded secrets or credentials
     - ✅ Reasonable performance
     - ✅ Tests cover new functionality

  3. **Create review report:**
     Write to: Tests/Report/code-review-{{TASK_ID}}.md

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
  --summary="Code review APPROVED" \
  --details="All checks passed. Proceeding to merge."

# 2. Update status to PR
mcp__claudetask__update_status --task_id={{TASK_ID}} --status="PR" \
  --comment="Code review passed"
```

Then **IMMEDIATELY** execute: `SlashCommand("/merge {{TASK_ID}}")`

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

## ⚠️ CRITICAL FOR AUTO MODE

**When `manual_mode = false` and code review APPROVED:**

1. ✅ Save stage result
2. ✅ Update status to "PR"
3. ✅ **IMMEDIATELY** execute `/merge {{TASK_ID}}`
4. ❌ **DO NOT** say "awaiting user verification"
5. ❌ **DO NOT** wait for user action
6. ❌ **DO NOT** stop and ask for confirmation

The workflow must be FULLY AUTOMATIC:
```
/PR → fullstack-code-reviewer → APPROVED → /merge → pr-merge-agent → Done
```

---

## Flow Summary

```
Manual Mode:
  /PR → Notify user → WAIT → user runs /merge → pr-merge-agent → Done

Auto Mode:
  /PR → fullstack-code-reviewer (review) → APPROVED → /merge → pr-merge-agent → Done
  /PR → fullstack-code-reviewer (review) → REJECTED → /start-develop (fix issues)
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
