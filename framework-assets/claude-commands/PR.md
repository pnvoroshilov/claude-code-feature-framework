---
description: Execute code review workflow - manual or automated based on project settings (UC-05)
argument-hint: [task-id]
---

# Code Review Workflow - UC-05

When you run this command, the system will execute the UC-05 code review workflow based on the project's `manual_mode` setting.

## Step 1: Check Project Settings

First, determine which code review mode is enabled:

```bash
mcp__claudetask__get_project_settings
```

Look for: `"Manual Mode": True` or `False`

## Step 2a: Manual Mode (manual_mode = true)

If Manual Mode is enabled, the user performs code review manually:

### Notify User
```
✅ Task is ready for Code Review.

Manual Mode is enabled - please review the code manually:
- Review the Pull Request on GitHub/GitLab
- Check code quality and adherence to standards
- Verify test coverage
- Ensure DoD is met
- Approve or request changes

Update task status when review is complete.
```

### Save Stage Result
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Code Review" \
  --summary="Awaiting manual code review" \
  --details="Manual mode enabled - user will review PR manually
PR is ready for review
Waiting for user approval or feedback"
```

### Wait for User
- User will review the PR manually
- User will approve or request changes
- User will update status when review is complete
- **DO NOT auto-transition** - wait for user action

## Step 2b: Automated Mode (manual_mode = false)

If Automated Mode is enabled, delegate to code review agent:

### Get Task and PR Details
```bash
# Get task details
mcp__claudetask__get_task --task_id={id}

# Get PR information from task
# The PR URL should be in task metadata
```

### Delegate to Code Review Agent

```bash
mcp__claudetask__delegate_to_agent \
  --task_id={id} \
  --agent_type="fullstack-code-reviewer" \
  --instructions="Review the PR for task #{id}. Check:
- Code quality and best practices
- Test coverage and passing tests
- DoD compliance
- Security vulnerabilities
- Performance considerations
- Architecture consistency

If approved: auto-merge PR and save review results.
If issues found: document them and DO NOT merge.

Save review report in /Tests/Report/code-review.md"
```

### Wait for Code Review Results

Monitor agent completion and check review report:
- `/Tests/Report/code-review.md`

### Analyze Review Results

Review the code review report and determine:
- ✅ Approved → Auto-merge PR and proceed
- ❌ Changes required → Return to "In Progress"
- ⚠️ Minor issues → Document and decide based on severity

### Auto-Merge (if approved)

```bash
# If review passed, merge PR
cd worktrees/task-{id}
git checkout main
git pull origin main
git merge --no-ff task-{id}-branch
git push origin main
```

### Save Stage Result

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Code Review" \
  --summary="Automated code review completed" \
  --details="Code Review: [APPROVED/CHANGES REQUIRED]
Issues found: [count]
Review report: /Tests/Report/code-review.md
PR status: [MERGED/PENDING]"
```

### Auto-Transition Status

**Based on review results:**

```bash
# If review approved and PR merged
mcp__claudetask__update_status --task_id={id} --status="Done" \
  --comment="Code review passed, PR merged successfully"

# If changes required
mcp__claudetask__update_status --task_id={id} --status="In Progress" \
  --comment="Code review failed: [list issues]"
```

## Usage

```bash
/PR [task-id]
```

## Example

```bash
/PR 42
```

This will:
1. ✅ Check project settings for review mode
2. ✅ If manual mode: Notify user, wait for manual review
3. ✅ If automated mode: Delegate to code review agent, auto-merge if approved

## Required Preconditions

- Task must be in "Code Review" status
- Testing must be complete
- PR must exist
- All tests must be passing

## Notes

- This implements UC-05 from `Workflow/new_workflow_usecases.md`
- Supports both manual and automated code review modes
- Mode is determined by `manual_mode` project setting
- In manual mode: User reviews and merges PR manually
- In automated mode: Code review agent analyzes and auto-merges if approved
- **CRITICAL**: Only transitions to "Done" in automated mode with successful review
