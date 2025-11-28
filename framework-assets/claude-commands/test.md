---
description: Execute testing workflow - manual or automated based on project settings (UC-04)
argument-hint: [task-id]
---

# Testing Workflow - UC-04 with Integrated Test Suite

When you run this command, the system will execute the UC-04 testing workflow based on the project's `manual_mode` setting.

## MANDATORY: RAG-First Search Policy

**Before creating ANY tests, ALWAYS use RAG search to understand testing patterns:**

```bash
# 1. Search for existing test patterns in the project
mcp__claudetask__search_codebase --query="test pytest unittest mock fixture" --top_k=20

# 2. Search for feature-specific test examples
mcp__claudetask__search_codebase --query="test <feature area being tested>" --top_k=20

# 3. Search documentation for testing guidelines
mcp__claudetask__search_documentation --query="testing guidelines test patterns" --top_k=10
```

**Why RAG First for Testing?**
- Discover existing test patterns to follow
- Find mocking strategies used in the project
- Understand test fixture conventions
- Match assertion styles and test structure

---

## Step 1: Check Project Settings

First, determine which testing mode is enabled and get test configuration:

```bash
mcp__claudetask__get_project_settings
```

**Look for:**
- `"manual_mode": true` or `false`
- `"test_command"`: Command to run existing tests (e.g., "pytest", "npm test")
- `"test_directory"`: Main test directory (e.g., "tests", "src/__tests__")
- `"test_framework"`: Test framework (pytest/jest/vitest/mocha/unittest)
- `"test_staging_dir"`: Staging directory for new task tests (e.g., "tests/staging")
- `"auto_merge_tests"`: Whether to auto-merge tests after PR approval

---

## Step 2a: Manual Mode (`manual_mode = true`)

If Manual Mode is enabled, follow the manual testing workflow:

---

### 🔴🔴🔴 CRITICAL: PORT ISOLATION RULES

**⚠️ MANDATORY - NEVER VIOLATE THESE RULES!**

1. **ALWAYS USE NEW PORTS** - Find free ports, don't kill processes
2. **NEVER KILL OTHER PROCESSES** - Don't terminate processes on occupied ports
3. **NEVER REUSE PORTS FROM OTHER TASKS** - Each task has isolated environment
4. **ONLY STOP YOUR OWN SERVERS** - Only during cleanup of the SAME task

```
✅ CORRECT: Port 3333 occupied → Find port 3334 → Use 3334
❌ WRONG: Port 3333 occupied → Kill process → Use 3333
❌ WRONG: Stop other task's servers to free ports
```

---

### Find Available Ports (WITHOUT KILLING ANYTHING!)

```bash
# Check which ports are occupied - DO NOT KILL THESE!
echo "=== Currently occupied ports (DO NOT TOUCH) ==="
lsof -i :3333 2>/dev/null && echo "3333: OCCUPIED - skip"
lsof -i :3334 2>/dev/null && echo "3334: OCCUPIED - skip"
lsof -i :3335 2>/dev/null && echo "3335: OCCUPIED - skip"

# Find first FREE backend port
for port in 3333 3334 3335 3336 3337 3338 3339 3340; do
  lsof -i :$port > /dev/null 2>&1 || { BACKEND_PORT=$port; break; }
done
echo "FREE backend port: $BACKEND_PORT"

# Find first FREE frontend port
for port in 3000 3001 3002 3003 3004 3005; do
  lsof -i :$port > /dev/null 2>&1 || { FRONTEND_PORT=$port; break; }
done
echo "FREE frontend port: $FRONTEND_PORT"
```

**⚠️ NEVER run `kill`, `pkill`, or `lsof -t ... | xargs kill` on ports!**

### Start Backend Server (ON FREE PORT)
```bash
cd worktrees/task-{id}
python -m uvicorn app.main:app --port $BACKEND_PORT --reload &
```

### Start Frontend Server (ON FREE PORT)
```bash
cd worktrees/task-{id}
PORT=$FRONTEND_PORT npm start &
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

### STEP 1: RAG Search for Test Patterns (MANDATORY)

**Before creating any tests, search for existing patterns:**

```bash
# Find existing test patterns
mcp__claudetask__search_codebase --query="pytest test fixture mock" --top_k=20

# Find tests for similar features
mcp__claudetask__search_codebase --query="test <feature being implemented>" --top_k=20

# Find integration test patterns
mcp__claudetask__search_codebase --query="integration test API endpoint" --top_k=20

# Find E2E test patterns
mcp__claudetask__search_codebase --query="playwright E2E test browser" --top_k=20

# Check testing documentation
mcp__claudetask__search_documentation --query="testing strategy test coverage" --top_k=10
```

### STEP 2: Run EXISTING Project Tests (Regression Check)

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

**If existing tests PASS → Continue to Step 3**

### STEP 3: Create NEW Tests for This Task

**Create staging directory:**
```bash
mkdir -p {test_staging_dir}/task-{id}
```

**Delegate test creation to specialized agents WITH RAG instructions:**

**For Backend/Unit Tests (quality-engineer agent):**

```
Task(
  subagent_type="quality-engineer",
  prompt="""
  Create unit tests for Task #{task_id}:

  **MANDATORY: RAG Search First!**
  Before writing ANY tests, run:
  - mcp__claudetask__search_codebase --query="pytest test fixture mock <feature>" --top_k=20
  - mcp__claudetask__search_codebase --query="test {test_directory} patterns" --top_k=20
  - mcp__claudetask__search_documentation --query="testing guidelines coverage" --top_k=10

  Instructions:
  1. Read task analysis documents in worktrees/task-{id}/Analyze/ folder
  2. Review RAG results for existing test patterns
  3. Create unit tests following project conventions
  4. Use {test_framework} framework
  5. Save tests to: {test_staging_dir}/task-{id}/
  6. File naming: test_{feature_name}.py (or .test.ts for JS)

  Tests should cover:
  - All new functions/methods
  - Edge cases
  - Error handling
  - Integration with existing code

  MATCH existing test patterns found via RAG!
  """
)
```

**For Frontend/E2E Tests (web-tester agent):**

```
Task(
  subagent_type="web-tester",
  prompt="""
  Create E2E tests for Task #{task_id}:

  **MANDATORY: RAG Search First!**
  Before writing ANY tests, run:
  - mcp__claudetask__search_codebase --query="playwright E2E test spec browser" --top_k=20
  - mcp__claudetask__search_codebase --query="test UI component interaction" --top_k=20
  - mcp__claudetask__search_documentation --query="E2E testing guidelines" --top_k=10

  Instructions:
  1. Read task analysis documents in worktrees/task-{id}/Analyze/ folder
  2. Review RAG results for existing E2E patterns
  3. Create E2E tests for UI changes
  4. Use Playwright for browser testing
  5. Save tests to: {test_staging_dir}/task-{id}/
  6. File naming: e2e_{feature_name}.spec.ts

  Tests should cover:
  - User flows
  - UI interactions
  - Visual elements

  MATCH existing E2E patterns found via RAG!
  """
)
```

### STEP 4: Run NEW Tests in Isolation

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
- Retry Step 4

**If new tests PASS → Continue to Step 5**

### STEP 5: Run ALL Tests Together

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

**If ALL tests PASS → Continue to Step 6**

### STEP 6: Save Results and Auto-Transition

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

## RAG Search Patterns for Testing

```bash
# Unit test patterns
mcp__claudetask__search_codebase --query="pytest fixture mock patch" --top_k=20
mcp__claudetask__search_codebase --query="unittest TestCase setUp tearDown" --top_k=20

# API test patterns
mcp__claudetask__search_codebase --query="test API client endpoint request" --top_k=20
mcp__claudetask__search_codebase --query="test FastAPI TestClient httpx" --top_k=20

# Database test patterns
mcp__claudetask__search_codebase --query="test database MongoDB mock" --top_k=20
mcp__claudetask__search_codebase --query="test repository fixture seed" --top_k=20

# Frontend test patterns
mcp__claudetask__search_codebase --query="test React render fireEvent" --top_k=20
mcp__claudetask__search_codebase --query="jest mock component snapshot" --top_k=20

# E2E test patterns
mcp__claudetask__search_codebase --query="playwright page locator click" --top_k=20
mcp__claudetask__search_codebase --query="E2E test user flow form" --top_k=20
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
2. **RAG Search** - Find existing test patterns
3. If manual mode: Start test servers, save URLs, wait for user
4. If automated mode:
   - Run existing tests (regression check)
   - Create new tests via agents **with RAG context**
   - Stage new tests in `{test_staging_dir}/task-{id}/`
   - Run all tests
   - Auto-transition and execute `/PR`

---

## Required Preconditions

- Task must be in "Testing" status
- Implementation must be complete
- For automated mode: Analysis documents must exist in `worktrees/task-{id}/Analyze/`
- Test configuration should be set in project settings

---

## Test Configuration (Project Settings)

| Setting | Description | Default |
|---------|-------------|---------|
| `test_command` | Command to run tests | Framework default |
| `test_directory` | Main test directory | `tests` |
| `test_framework` | Test framework | `pytest` |
| `test_staging_dir` | Staging for new tests | `tests/staging` |
| `auto_merge_tests` | Auto-merge after PR | `true` |

---

## Test Merge Process

**When `auto_merge_tests = true` and PR is merged:**

The `/merge` command will automatically:
1. Move tests from `{test_staging_dir}/task-{id}/` to main `{test_directory}/`
2. Clean up staging directory
3. Commit test additions

**This ensures new tests become part of the permanent test suite.**

---

## Notes

- This implements UC-04 from `Workflow/new_workflow_usecases.md`
- **RAG search is MANDATORY** before creating tests
- Supports both manual and automated testing modes
- Runs existing tests first to catch regressions
- Creates new tests in staging directory
- Merges tests to main suite after PR approval
- Mode is determined by `manual_mode` project setting
- In manual mode: Testing URLs are **mandatory**
- In automated mode: Tests run automatically and status auto-transitions
