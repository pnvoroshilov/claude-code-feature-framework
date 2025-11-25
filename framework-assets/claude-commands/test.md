---
description: Execute testing workflow - manual or automated based on project settings (UC-04)
argument-hint: [task-id]
---

# Testing Workflow - UC-04 with Integrated Test Suite

When you run this command, the system will execute the UC-04 testing workflow based on the project's `manual_mode` setting.

## Step 1: Check Project Settings

First, determine which testing mode is enabled and get test configuration:

```bash
mcp__claudetask__get_project_settings
```

**Look for:**
- `"Manual Mode": True` or `False`
- `"test_command"`: Command to run existing tests (e.g., "pytest", "npm test")
- `"test_directory"`: Main test directory (e.g., "tests", "src/__tests__")
- `"test_framework"`: Test framework (pytest/jest/vitest/mocha/unittest)
- `"test_staging_dir"`: Staging directory for new task tests (e.g., "tests/staging")
- `"auto_merge_tests"`: Whether to auto-merge tests after PR approval

---

## Step 2a: Manual Mode (`manual_mode = true`)

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

### MANDATORY: Save Testing URLs
```bash
mcp__claudetask__set_testing_urls --task_id={id} \
  --urls='{"frontend": "http://localhost:FREE_FRONTEND_PORT", "backend": "http://localhost:FREE_BACKEND_PORT"}'
```

**DO NOT SKIP THIS STEP** - Testing URLs MUST be saved for task tracking!

### Save Stage Result
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Testing environment ready with URLs saved" \
  --details="Backend: http://localhost:FREE_BACKEND_PORT
Frontend: http://localhost:FREE_FRONTEND_PORT
URLs saved to database for persistent access
Ready for manual testing"
```

### Notify User and Wait
```
Testing environment ready and URLs SAVED to task:
- Backend: http://localhost:FREE_BACKEND_PORT
- Frontend: http://localhost:FREE_FRONTEND_PORT
- URLs permanently saved to task #{id} for easy access

Please perform manual testing and update status when complete.
```

**DO NOT auto-transition** - wait for user action in manual mode.

---

## Step 2b: Automated Mode (`manual_mode = false`)

If Automated Mode is enabled, follow the 5-step integrated test workflow:

### STEP 1: Run EXISTING Project Tests (Regression Check)

**CRITICAL: Before creating new tests, verify existing tests still pass!**

```bash
# Get task context
mcp__claudetask__get_task --task_id={id}

# Run existing test suite using test_command from settings
# Default commands by framework:
# - pytest: pytest {test_directory}/ -v --tb=short
# - jest: npm test
# - vitest: npx vitest run
# - custom: {test_command}
```

**If existing tests FAIL:**
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="REGRESSION DETECTED: Existing tests failed" \
  --details="The implementation broke existing tests.
Failed tests: [list failed tests]
Action: Returning to development to fix regression"

mcp__claudetask__update_status --task_id={id} --status="In Progress" \
  --comment="Regression detected: existing tests failed"

# Return to development
SlashCommand("/start-develop")
```

**If existing tests PASS → Continue to Step 2**

### STEP 2: Create NEW Tests for This Task

**Create staging directory:**
```bash
mkdir -p {test_staging_dir}/task-{id}
```

**Delegate test creation to specialized agents:**

**For Backend/Unit Tests (quality-engineer agent):**

Use Task tool with `subagent_type="quality-engineer"`:
```
Instructions:
1. Read task analysis documents in /Analyze folder
2. Create unit tests for new functionality
3. Follow project's test patterns from {test_directory}
4. Use {test_framework} framework
5. Save tests to: {test_staging_dir}/task-{id}/
6. File naming: test_{feature_name}.py (or .test.ts for JS)

Tests should cover:
- All new functions/methods
- Edge cases
- Error handling
- Integration with existing code
```

**For Frontend/E2E Tests (web-tester agent):**

Use Task tool with `subagent_type="web-tester"`:
```
Instructions:
1. Read task analysis documents in /Analyze folder
2. Create E2E tests for UI changes
3. Use Playwright for browser testing
4. Save tests to: {test_staging_dir}/task-{id}/
5. File naming: e2e_{feature_name}.spec.ts

Tests should cover:
- User flows
- UI interactions
- Visual elements
```

### STEP 3: Run NEW Tests in Isolation

**Run only the new tests to verify they work:**

```bash
# For pytest
pytest {test_staging_dir}/task-{id}/ -v

# For jest
npm test -- --testPathPattern="staging/task-{id}"

# For vitest
npx vitest run {test_staging_dir}/task-{id}/
```

**If new tests FAIL:**
- Review and fix tests (may be test bugs, not code bugs)
- Or return to development if code needs fixes
- Retry Step 3

**If new tests PASS → Continue to Step 4**

### STEP 4: Run ALL Tests Together

**Verify new tests don't conflict with existing tests:**

```bash
# For pytest
pytest {test_directory}/ {test_staging_dir}/task-{id}/ -v

# For jest
npm test

# For vitest
npx vitest run
```

**If combined tests FAIL:**
- Investigate conflicts
- Fix test isolation issues
- Retry

**If ALL tests PASS → Continue to Step 5**

### STEP 5: Save Results and Auto-Transition

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="All tests passed - ready for code review" \
  --details="REGRESSION CHECK: All existing tests PASS
NEW TESTS CREATED:
- {test_staging_dir}/task-{id}/test_*.py
COMBINED TEST RUN: ALL PASS

Tests will be merged to main suite after PR approval."

mcp__claudetask__update_status --task_id={id} --status="Code Review" \
  --comment="All automated tests passed"
```

**IN AUTO MODE: Execute /PR command IMMEDIATELY!**
```bash
SlashCommand("/PR {task_id}")
```

---

## Usage

```bash
/test [task-id]
```

## Example

```bash
/test 42
```

This will:
1. Check project settings for testing mode and test configuration
2. If manual mode: Start test servers, save URLs, wait for user
3. If automated mode:
   - Run existing tests (regression check)
   - Create new tests via agents
   - Stage new tests in `{test_staging_dir}/task-{id}/`
   - Run all tests
   - Auto-transition and execute `/PR`

## Required Preconditions

- Task must be in "Testing" status
- Implementation must be complete
- For automated mode: Analysis documents must exist
- Test configuration should be set in project settings

## Test Configuration (Project Settings)

| Setting | Description | Default |
|---------|-------------|---------|
| `test_command` | Command to run tests | Framework default |
| `test_directory` | Main test directory | `tests` |
| `test_framework` | Test framework | `pytest` |
| `test_staging_dir` | Staging for new tests | `tests/staging` |
| `auto_merge_tests` | Auto-merge after PR | `true` |

## Test Merge Process

**When `auto_merge_tests = true` and PR is merged:**

The `/merge` command will automatically:
1. Move tests from `{test_staging_dir}/task-{id}/` to main `{test_directory}/`
2. Clean up staging directory
3. Commit test additions

**This ensures new tests become part of the permanent test suite.**

## Notes

- This implements UC-04 from `Workflow/new_workflow_usecases.md`
- Supports both manual and automated testing modes
- **NEW**: Runs existing tests first to catch regressions
- **NEW**: Creates new tests in staging directory
- **NEW**: Merges tests to main suite after PR approval
- Mode is determined by `manual_mode` project setting
- In manual mode: Testing URLs are **mandatory**
- In automated mode: Tests run automatically and status auto-transitions
