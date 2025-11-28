# Testing Workflow - Integrated Test Suite Management

**This applies to DEVELOPMENT MODE only. SIMPLE mode has no Testing status.**

## Testing Mode Configuration

**This project supports TWO testing modes controlled by `manual_mode` setting:**

- **MANUAL MODE** (`manual_mode = true`) - UC-04 Variant B
  - User performs manual testing
  - Test servers started for user access
  - Testing URLs saved for persistence
  - User manually transitions status after testing

- **AUTOMATED MODE** (`manual_mode = false`) - UC-04 Variant A
  - **NEW**: Run existing project tests first (regression check)
  - Testing agents write and execute new tests
  - New tests staged in `{test_staging_dir}/task-{id}/`
  - Auto-merge tests into main suite after PR approval
  - Auto-transition based on test results

## Check Testing Mode BEFORE Starting

**FIRST, check project settings to determine which mode to use:**

```bash
mcp__claudetask__get_project_settings
```

Look for:
- `"Manual Mode": True` or `False`
- `"test_command"`: Command to run existing tests
- `"test_directory"`: Main test directory
- `"test_framework"`: pytest/jest/vitest/etc.
- `"test_staging_dir"`: Staging directory for new tests
- `"auto_merge_tests"`: Whether to auto-merge after PR

---

# 🔴🔴🔴 CRITICAL: PORT ISOLATION RULES

**⚠️ MANDATORY PORT ISOLATION POLICY - NEVER VIOLATE THESE RULES!**

## Golden Rules for Test Environment Ports

### 1. **ALWAYS USE NEW PORTS**
Every test environment MUST start on NEW, UNUSED ports.
```
✅ CORRECT: Find free ports → Start servers on those ports
❌ WRONG: Kill existing process → Reuse port
❌ WRONG: Stop other task's servers to free ports
```

### 2. **NEVER KILL OTHER PROCESSES**
Do NOT terminate processes on occupied ports unless they belong to the SAME task.
```
✅ CORRECT: Port 3333 occupied → Find port 3334 or higher
❌ WRONG: Port 3333 occupied → Kill process → Use 3333
❌ WRONG: Stop backend on 3333 to start new backend
```

### 3. **NEVER REUSE PORTS FROM OTHER TASKS**
Each task has its own isolated test environment.
```
✅ CORRECT: Task-42 on 3333/3000, Task-43 on 3334/3001
❌ WRONG: Stop Task-42's servers to run Task-43's tests
```

### 4. **ONLY STOP YOUR OWN SERVERS**
Only when cleaning up the SAME task's environment.
```
✅ CORRECT: /merge task-42 → Stop task-42's servers
❌ WRONG: Starting task-43 → Stop task-42's servers
```

## Port Allocation Strategy

**Recommended port ranges:**
- Backend: 3333, 3334, 3335, ... (3333-5000)
- Frontend: 3000, 3001, 3002, ... (3000-4000)

**Finding free ports:**
```bash
# Check multiple ports at once
for port in 3333 3334 3335 3336; do
  lsof -i :$port > /dev/null 2>&1 || echo "Port $port is FREE"
done

# Find first free port in range
for port in $(seq 3333 3400); do
  lsof -i :$port > /dev/null 2>&1 || { echo $port; break; }
done
```

## Why Port Isolation Matters

1. **Parallel Development** - Multiple tasks can be tested simultaneously
2. **No Conflicts** - Task-42's tests don't affect Task-43's environment
3. **Safe Cleanup** - Stopping one task doesn't break another
4. **Predictability** - Each task has stable, dedicated URLs

---

# MANUAL TESTING MODE (`manual_mode = true`)

## CRITICAL TESTING URL REQUIREMENT

**You MUST save testing URLs IMMEDIATELY after starting test servers**
**This is NOT optional - it is MANDATORY for task tracking**

## MANUAL TESTING CHECKLIST (ALL STEPS REQUIRED)

When task moves to "Testing" status in MANUAL mode:

### Step 1: Find Available Ports (WITHOUT KILLING ANYTHING)

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

### Step 2: Start Backend Server (ON FREE PORT)
```bash
cd worktrees/task-{id}
python -m uvicorn app.main:app --port $BACKEND_PORT --reload &
```

### Step 3: Start Frontend Server (ON FREE PORT)
```bash
cd worktrees/task-{id}
PORT=$FRONTEND_PORT npm start &
```

### Step 4: SAVE TESTING URLs (MANDATORY - DO NOT SKIP)

```bash
mcp__claudetask__set_testing_urls --task_id={id} \
  --urls='{"frontend": "http://localhost:FREE_FRONTEND_PORT", "backend": "http://localhost:FREE_BACKEND_PORT"}'
```

### Step 5: Save Stage Result

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Testing environment prepared with URLs saved" \
  --details="Backend: http://localhost:FREE_BACKEND_PORT
Frontend: http://localhost:FREE_FRONTEND_PORT
URLs SAVED to task database for persistent access
Ready for manual testing"
```

### Step 6: Notify User and Wait

```
Testing environment ready and URLs SAVED to task:
- Backend: http://localhost:FREE_BACKEND_PORT
- Frontend: http://localhost:FREE_FRONTEND_PORT
- URLs permanently saved to task #{id} for easy access

Please perform manual testing and update status when complete.
```

**NEVER auto-transition from Testing status in MANUAL mode.**

---

# AUTOMATED TESTING MODE (`manual_mode = false`)

## NEW 5-STEP TESTING WORKFLOW

### Step 1: Run EXISTING Project Tests (Regression Check)

**CRITICAL: Before creating new tests, verify existing tests still pass!**

```bash
# Get project settings for test command
mcp__claudetask__get_project_settings

# Run existing test suite
# Use test_command from settings, default examples:
# Python: pytest {test_directory} -v
# Node: npm test
# Custom: {test_command}
```

**Run the test command:**
```bash
# Example for pytest
pytest tests/ -v --tb=short

# Example for jest
npm test

# Example for custom command from settings
{test_command}
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

SlashCommand("/start-develop")
```

**If existing tests PASS → Continue to Step 2**

### Step 2: Create NEW Tests for This Task

**Delegate to testing agents to create task-specific tests:**

```bash
# Get task details and analysis docs
mcp__claudetask__get_task --task_id={id}
```

**Read project test settings:**
- `test_directory`: Where existing tests live (e.g., "tests")
- `test_framework`: Which framework to use (pytest/jest/vitest)
- `test_staging_dir`: Where to put new tests (e.g., "tests/staging")

**Create staging directory for this task:**
```bash
mkdir -p {test_staging_dir}/task-{id}
```

**Delegate test creation:**

**For Backend/Unit Tests (quality-engineer agent):**
```
Task agent: quality-engineer

Instructions:
Read the task analysis documents in /Analyze folder.
Create unit tests for the new functionality implemented in this task.
Follow the project's test patterns from {test_directory}.
Use {test_framework} framework.

Save tests to: {test_staging_dir}/task-{id}/
File naming: test_{feature_name}.py (or .test.ts for JS)

Tests should cover:
- All new functions/methods
- Edge cases
- Error handling
- Integration with existing code
```

**For Frontend/E2E Tests (web-tester agent):**
```
Task agent: web-tester

Instructions:
Read the task analysis documents in /Analyze folder.
Create E2E tests for any UI changes in this task.
Use Playwright for browser testing.

Save tests to: {test_staging_dir}/task-{id}/
File naming: e2e_{feature_name}.spec.ts

Tests should cover:
- User flows
- UI interactions
- Visual elements
```

### Step 3: Run NEW Tests in Isolation

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
- Review and fix the tests (may be test bugs, not code bugs)
- Or return to development if code needs fixes
- Retry Step 3

**If new tests PASS → Continue to Step 4**

### Step 4: Run ALL Tests Together

**Verify new tests don't conflict with existing tests:**

```bash
# Run full suite including staging
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

### Step 5: Save Results and Transition

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

# AUTO MODE: Execute next command immediately!
SlashCommand("/PR {task_id}")
```

---

## TEST MERGE WORKFLOW (After PR Approval)

**When `auto_merge_tests = true` and PR is merged:**

The `/merge` command will automatically:

1. **Move tests from staging to main directory:**
```bash
# Move unit tests
mv {test_staging_dir}/task-{id}/test_*.py {test_directory}/unit/

# Move e2e tests
mv {test_staging_dir}/task-{id}/e2e_*.spec.ts {test_directory}/e2e/

# Clean up staging directory
rm -rf {test_staging_dir}/task-{id}/
```

2. **Update test index if needed**

3. **Commit test additions:**
```bash
git add {test_directory}/
git commit -m "test: Add tests from task #{id}"
```

---

## PROJECT TEST STRUCTURE

**Recommended directory structure:**

```
project/
├── {test_directory}/           # Main test directory (e.g., "tests")
│   ├── unit/                   # Unit tests (permanent)
│   │   ├── test_users.py
│   │   ├── test_tasks.py
│   │   └── ...
│   ├── integration/            # Integration tests
│   │   └── ...
│   ├── e2e/                    # E2E tests
│   │   └── ...
│   └── conftest.py             # Shared fixtures (pytest)
├── {test_staging_dir}/         # Staging for new tests (e.g., "tests/staging")
│   ├── task-42/                # Tests for task 42 (before merge)
│   │   ├── test_new_feature.py
│   │   └── e2e_new_feature.spec.ts
│   └── task-43/
│       └── ...
└── Tests/                      # Test REPORTS (markdown)
    └── Report/
        └── task-{id}-report.md
```

---

## FRAMEWORK-SPECIFIC COMMANDS

### pytest (Python)
```bash
# Run all tests
pytest {test_directory}/ -v

# Run with coverage
pytest {test_directory}/ --cov=app --cov-report=term-missing

# Run specific directory
pytest {test_staging_dir}/task-{id}/ -v
```

### Jest (JavaScript/TypeScript)
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific pattern
npm test -- --testPathPattern="task-{id}"
```

### Vitest
```bash
# Run all tests
npx vitest run

# Run with coverage
npx vitest run --coverage

# Run specific directory
npx vitest run {test_staging_dir}/task-{id}/
```

---

## AUTOMATED MODE CHECKLIST

When task moves to "Testing" in AUTOMATED mode:

1. **Run existing tests** (regression check)
2. **Create new tests** via agents
3. **Save new tests** in staging directory
4. **Run new tests** in isolation
5. **Run all tests** combined
6. **Save stage result** with test summary
7. **Auto-transition** to Code Review
8. **Execute /PR command** immediately

**Tests are MERGED to main suite only after PR is approved and merged.**

---

## MODE COMPARISON

| Feature | Manual Mode | Automated Mode |
|---------|-------------|----------------|
| **Existing Tests** | Not run | Run first (regression check) |
| **New Tests** | Not created | Created by agents |
| **Test Location** | N/A | Staging dir → Main dir |
| **Who Tests** | User manually | Testing agents |
| **Test Servers** | Started for user | Not needed |
| **Testing URLs** | MUST save | Not required |
| **Status Transition** | User updates | Auto-transition |
| **Test Merge** | N/A | After PR approval |

---

## DECISION TREE

```
Task enters "Testing" status
    ↓
Check: mcp__claudetask__get_project_settings
    ↓
manual_mode = ?
    ↓
    ├─→ TRUE (Manual Mode)
    │   ├─→ Find free ports
    │   ├─→ Start test servers
    │   ├─→ SAVE testing URLs (mandatory!)
    │   ├─→ Save stage result
    │   ├─→ Notify user
    │   └─→ WAIT for user to update status
    │
    └─→ FALSE (Automated Mode)
        ├─→ STEP 1: Run existing tests
        │   ├─→ FAIL → Return to In Progress
        │   └─→ PASS → Continue
        ├─→ STEP 2: Create new tests (staging)
        ├─→ STEP 3: Run new tests in isolation
        │   ├─→ FAIL → Fix and retry
        │   └─→ PASS → Continue
        ├─→ STEP 4: Run all tests combined
        │   ├─→ FAIL → Investigate conflicts
        │   └─→ PASS → Continue
        ├─→ STEP 5: Save results
        ├─→ Update to Code Review
        └─→ Execute /PR {task_id}
```

---

## TROUBLESHOOTING

### No test_command configured
If `test_command` is not set, use framework defaults:
- pytest: `pytest tests/ -v`
- jest: `npm test`
- vitest: `npx vitest run`

### Staging directory doesn't exist
Create it: `mkdir -p {test_staging_dir}/task-{id}`

### Tests fail on merge
- Check for import conflicts
- Verify fixtures are available
- Check test isolation (no shared state)

### Agent doesn't create tests
- Ensure analysis docs exist
- Provide clear instructions
- Check DoD for test requirements
