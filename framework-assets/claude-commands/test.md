---
description: Execute testing workflow - manual or automated based on project settings (UC-04)
argument-hint: [task-id]
---

# Testing Workflow - UC-04

When you run this command, the system will execute the UC-04 testing workflow based on the project's `manual_mode` setting.

## Step 1: Check Project Settings

First, determine which testing mode is enabled:

```bash
mcp__claudetask__get_project_settings
```

Look for: `"Manual Mode": True` or `False`

## Step 2a: Manual Mode (manual_mode = true)

If Manual Mode is enabled, follow the manual testing workflow:

### Find Available Ports
```bash
lsof -i :3333  # Backend default
lsof -i :3000  # Frontend default

# If occupied, find free ports in ranges:
# Backend: 3333-5000
# Frontend: 3000-4000
```

### Start Backend Server
```bash
cd worktrees/task-{id}
python -m uvicorn app.main:app --port FREE_BACKEND_PORT --reload &
```

### Start Frontend Server
```bash
cd worktrees/task-{id}
PORT=FREE_FRONTEND_PORT npm start &
```

### 🔴 MANDATORY: Save Testing URLs
```bash
mcp__claudetask__set_testing_urls --task_id={id} \
  --urls='{"frontend": "http://localhost:FREE_FRONTEND_PORT", "backend": "http://localhost:FREE_BACKEND_PORT"}'
```

⛔ **DO NOT SKIP THIS STEP** - Testing URLs MUST be saved for task tracking!

### Save Stage Result
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Testing environment ready with URLs saved" \
  --details="Backend: http://localhost:FREE_BACKEND_PORT
Frontend: http://localhost:FREE_FRONTEND_PORT
✅ URLs saved to database for persistent access
Ready for manual testing"
```

### Notify User
```
✅ Testing environment ready and URLs SAVED to task:
- Backend: http://localhost:FREE_BACKEND_PORT
- Frontend: http://localhost:FREE_FRONTEND_PORT
- URLs permanently saved to task #{id} for easy access

Please perform manual testing and update status when complete.
```

### Wait for User
- User will test manually via browser
- User will update status when testing is complete
- **DO NOT auto-transition** - wait for user action

## Step 2b: Automated Mode (manual_mode = false)

If Automated Mode is enabled, delegate to testing agents:

### Read Analysis Documents
```bash
# Get task details
mcp__claudetask__get_task --task_id={id}

# Read analysis docs in worktree
cat worktrees/task-{id}/Analyze/Requirements/*
cat worktrees/task-{id}/Analyze/Design/*
```

### Determine Test Types
Based on analysis docs and DoD, determine which tests are needed:
- ✅ UI/Frontend tests (web-tester agent)
- ✅ Backend/API tests (quality-engineer agent)
- ✅ Integration tests (if multiple components changed)

### Delegate to Testing Agents

**For Frontend/UI Testing:**
```bash
mcp__claudetask__delegate_to_agent \
  --task_id={id} \
  --agent_type="web-tester" \
  --instructions="Read /Analyze docs and DoD. Create and execute UI tests per test plan. Save results in /Tests/Report/ui-tests.md"
```

**For Backend Testing:**
```bash
mcp__claudetask__delegate_to_agent \
  --task_id={id} \
  --agent_type="quality-engineer" \
  --instructions="Read /Analyze docs and DoD. Create pytest tests for backend APIs. Test all endpoints from test plan. Run tests and save results in /Tests/Report/backend-tests.md"
```

### Wait for Test Results
Monitor agent completion and collect test reports from:
- `/Tests/Report/ui-tests.md`
- `/Tests/Report/backend-tests.md`

### Analyze Test Results
Review all test reports and determine:
- ✅ All tests passed → Proceed to next step
- ❌ Critical failures → Return to "In Progress"
- ⚠️ Minor issues → Document and proceed (or return based on severity)

### Save Stage Result
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Automated testing completed" \
  --details="UI Tests: [PASS/FAIL count]
Backend Tests: [PASS/FAIL count]
Total: [X passed, Y failed]
Reports: /Tests/Report/*.md"
```

### Auto-Transition Status
**Based on test results:**

```bash
# If all tests passed
mcp__claudetask__update_status --task_id={id} --status="Code Review" \
  --comment="All automated tests passed"

# NOTE: In AUTO mode (manual_mode = false), orchestrator will automatically
# execute /PR command next. In MANUAL mode, wait for user to transition.

# If critical issues found
mcp__claudetask__update_status --task_id={id} --status="In Progress" \
  --comment="Critical test failures: [list issues]"

# NOTE: In AUTO mode (manual_mode = false), orchestrator will automatically
# execute /start-develop to fix issues. In MANUAL mode, wait for user action.
```

## Usage

```bash
/test [task-id]
```

## Example

```bash
/test 42
```

This will:
1. ✅ Check project settings for testing mode
2. ✅ If manual mode: Start test servers, save URLs, wait for user
3. ✅ If automated mode: Delegate to testing agents, run tests, auto-transition

## Required Preconditions

- Task must be in "Testing" status
- Implementation must be complete
- Worktree must exist
- For automated mode: Analysis documents must exist

## Notes

- This implements UC-04 from `Workflow/new_workflow_usecases.md`
- Supports both manual and automated testing modes
- Mode is determined by `manual_mode` project setting
- In manual mode: Testing URLs are **mandatory**
- In automated mode: Tests run automatically and status auto-transitions
