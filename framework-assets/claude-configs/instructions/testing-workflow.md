# 🧪 Testing Workflow - Hybrid Testing Modes

⚠️ **This applies to DEVELOPMENT MODE only. SIMPLE mode has no Testing status.**

## 📋 Testing Mode Configuration

**This project supports TWO testing modes controlled by `manual_mode` setting:**

- **🔵 MANUAL MODE** (`manual_mode = true`) - UC-04 Variant B
  - User performs manual testing
  - Test servers started for user access
  - Testing URLs saved for persistence
  - User manually transitions status after testing

- **🟢 AUTOMATED MODE** (`manual_mode = false`) - UC-04 Variant A
  - Testing agents write and execute tests automatically
  - Tests run in isolated environment
  - Reports generated in `/Tests/Report`
  - Auto-transition based on test results

## 🔍 Check Testing Mode BEFORE Starting

**FIRST, check project settings to determine which mode to use:**

```bash
mcp__claudetask__get_project_settings
```

Look for: `"Manual Testing Mode": True` or `False`

## When Testing Phase Starts

**Testing status is triggered when**:
- Task transitions from "In Progress" to "Testing"
- Implementation is detected as complete
- User manually updates status to "Testing"

**After detecting Testing phase, follow the workflow for the configured mode below.**

---

# 🔵 MANUAL TESTING MODE (`manual_mode = true`)

## 🚨🚨🚨 CRITICAL TESTING URL REQUIREMENT 🚨🚨🚨

**⛔ FAILURE TO SAVE TESTING URLs = CRITICAL ERROR**
**You MUST save testing URLs IMMEDIATELY after starting test servers**
**This is NOT optional - it is MANDATORY for task tracking**

## 📋 MANUAL TESTING CHECKLIST (ALL STEPS REQUIRED)

When task moves to "Testing" status in MANUAL mode:

### Step 1: Find Available Ports
```bash
# Check if default ports are occupied
lsof -i :3333  # Backend default
lsof -i :3000  # Frontend default

# If occupied, find free ports in ranges:
# Backend: 3333-5000
# Frontend: 3000-4000
```

### Step 2: Start Backend Server
```bash
cd worktrees/task-{id}
python -m uvicorn app.main:app --port FREE_BACKEND_PORT --reload &
```

### Step 3: Start Frontend Server
```bash
cd worktrees/task-{id}
PORT=FREE_FRONTEND_PORT npm start &
```

### Step 4: 🔴 SAVE TESTING URLs (MANDATORY - DO NOT SKIP)

**⚠️ YOU MUST EXECUTE THIS COMMAND IMMEDIATELY:**

```bash
mcp__claudetask__set_testing_urls --task_id={id} \
  --urls='{"frontend": "http://localhost:FREE_FRONTEND_PORT", "backend": "http://localhost:FREE_BACKEND_PORT"}'
```

**⛔ DO NOT PROCEED WITHOUT SAVING URLs**
**⛔ THIS IS NOT OPTIONAL - IT IS REQUIRED**
**⛔ SKIPPING THIS STEP = TASK TRACKING FAILURE**

### Step 5: Save Stage Result (ONLY AFTER URLs ARE SAVED)

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Testing environment prepared with URLs saved" \
  --details="Backend: http://localhost:FREE_BACKEND_PORT
Frontend: http://localhost:FREE_FRONTEND_PORT
✅ URLs SAVED to task database for persistent access
Ready for manual testing"
```

### Step 6: Notify User WITH CONFIRMATION

```
✅ Testing environment ready and URLs SAVED to task:
- Backend: http://localhost:FREE_BACKEND_PORT
- Frontend: http://localhost:FREE_FRONTEND_PORT
- URLs permanently saved to task #{id} for easy access

Please perform manual testing and update status when complete.
```

### Step 7: Wait for User Testing

- ✅ User will manually test the implementation
- ✅ User will update status when testing is complete
- ❌ DO NOT delegate to testing agents
- ❌ DO NOT auto-transition to next status

## ⚠️ VALIDATION: If You Setup Test Environment WITHOUT Saving URLs

**This is a CRITICAL ERROR that must be fixed:**

The task tracking is INCOMPLETE if URLs are not saved because:
- User cannot access test URLs later
- URLs are not persisted in database
- Task status is incomplete

**If you forgot to save URLs, FIX IT IMMEDIATELY:**
```bash
# Get the actual ports from running processes
lsof -i :PORT_NUMBER

# Save URLs now
mcp__claudetask__set_testing_urls --task_id={id} \
  --urls='{"frontend": "http://localhost:ACTUAL_PORT", "backend": "http://localhost:ACTUAL_PORT"}'
```

## Manual Mode Restrictions

❌ **DO NOT delegate to testing agents** - This is for MANUAL testing only
❌ **DO NOT create automated tests** - Unless explicitly requested
❌ **DO NOT auto-transition** - Wait for user to update status
❌ **DO NOT run test commands** - User will test manually

## Manual Mode Status Exit

**User will update status when testing is complete:**

- If tests pass → User updates to "Code Review"
- If bugs found → User updates to "In Progress" to fix
- If major issues → User may update to "Analysis" to re-evaluate

**You should NEVER auto-transition from Testing status in MANUAL mode.**

---

# 🟢 AUTOMATED TESTING MODE (`manual_testing_mode = false`)

## 📋 AUTOMATED TESTING CHECKLIST

When task moves to "Testing" status in AUTOMATED mode:

### Step 1: Read Analysis Documents
```bash
# Get task context
mcp__claudetask__get_task --task_id={id}

# Read analysis docs in worktree
cat worktrees/task-{id}/Analyze/Requirements/*
cat worktrees/task-{id}/Analyze/Design/*
```

### Step 2: Determine Test Types
Based on analysis docs and DoD, determine which tests are needed:
- ✅ UI/Frontend tests (web-tester agent)
- ✅ Backend/API tests (quality-engineer agent)
- ✅ Integration tests (if multiple components changed)

### Step 3: Delegate to Testing Agents

**For Frontend/UI Testing:**
```bash
# Use web-tester agent for E2E browser testing
mcp__claudetask__delegate_to_agent \
  --task_id={id} \
  --agent_type="web-tester" \
  --instructions="Read /Analyze docs and DoD. Create and execute UI tests per test plan. Save results in /Tests/Report/ui-tests.md"
```

**For Backend Testing:**
```bash
# Use quality-engineer for backend/API testing
mcp__claudetask__delegate_to_agent \
  --task_id={id} \
  --agent_type="quality-engineer" \
  --instructions="Read /Analyze docs and DoD. Create pytest tests for backend APIs. Test all endpoints from test plan. Run tests and save results in /Tests/Report/backend-tests.md"
```

### Step 4: Wait for Test Results

Monitor agent completion and collect test reports from:
- `/Tests/Report/ui-tests.md`
- `/Tests/Report/backend-tests.md`

### Step 5: Analyze Test Results

Review all test reports and determine:
- ✅ All tests passed → Proceed to Step 6
- ❌ Critical failures → Return to "In Progress"
- ⚠️ Minor issues → Document and proceed (or return based on severity)

### Step 6: Save Stage Result

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Testing" \
  --summary="Automated testing completed" \
  --details="UI Tests: [PASS/FAIL count]
Backend Tests: [PASS/FAIL count]
Total: [X passed, Y failed]
Reports: /Tests/Report/*.md"
```

### Step 7: Auto-Transition Status

**Based on test results:**

```bash
# If all tests passed
mcp__claudetask__update_status --task_id={id} --status="Code Review" \
  --comment="All automated tests passed"

# If critical issues found
mcp__claudetask__update_status --task_id={id} --status="In Progress" \
  --comment="Critical test failures: [list issues]"
```

## Automated Mode Workflow

✅ **DO delegate to testing agents** - Use web-tester, python-expert
✅ **DO create automated tests** - Required for automated mode
✅ **DO auto-transition** - Based on test results
✅ **DO generate test reports** - Save in `/Tests/Report/`

## Automated Mode Status Exit

**Auto-transition based on test results:**

- All tests pass → Auto-update to "Code Review"
- Critical failures → Auto-update to "In Progress" with details
- Blocking issues → May return to "Analysis" if design flaws found

**You SHOULD auto-transition from Testing status in AUTOMATED mode.**

## Port Management Best Practices

### Default Ports:
- Backend: 3333
- Frontend: 3000

### If Ports Occupied:
1. Check with `lsof -i :PORT`
2. Find alternative ports in safe ranges
3. Use ports that won't conflict with other services

### Port Ranges to Use:
- Backend: 3333-5000 (avoid system ports < 3000)
- Frontend: 3000-4000 (avoid 8000+, often used by other tools)

## Troubleshooting

### Port Already in Use:
```bash
# Find process using port
lsof -i :PORT_NUMBER

# Kill old process if safe
kill PID_NUMBER

# Or use different port
```

### Server Won't Start:
- Check worktree directory exists
- Ensure dependencies installed
- Check for syntax errors in code
- Look at server logs for errors

### Frontend Not Accessible:
- Check PORT environment variable
- Ensure npm start completed successfully
- Check browser console for errors
- Verify REACT_APP_BACKEND_URL if needed

## Complete Example

```bash
# 1. Check ports
lsof -i :3333
lsof -i :3000

# 2. Start backend (port 3333 free)
cd worktrees/task-42
python -m uvicorn app.main:app --port 3333 --reload &

# 3. Start frontend (port 3000 occupied, use 3001)
PORT=3001 npm start &

# 4. 🔴 MANDATORY: Save URLs
mcp__claudetask__set_testing_urls --task_id=42 \
  --urls='{"frontend": "http://localhost:3001", "backend": "http://localhost:3333"}'

# 5. Save stage result
mcp__claudetask__append_stage_result --task_id=42 --status="Testing" \
  --summary="Testing environment ready with URLs saved" \
  --details="Backend: http://localhost:3333
Frontend: http://localhost:3001
✅ URLs saved to database"

# 6. Notify user
echo "✅ Testing environment ready:
- Backend: http://localhost:3333
- Frontend: http://localhost:3001
- URLs saved to task #42"
```

---

# 📊 Mode Comparison Summary

| Feature | Manual Mode (true) | Automated Mode (false) |
|---------|-------------------|------------------------|
| **Who Tests** | User manually | Testing agents |
| **Test Servers** | ✅ Started for user access | ❌ Not needed |
| **Testing URLs** | 🔴 MUST save URLs | ❌ Not required |
| **Test Reports** | User documents findings | Auto-generated in `/Tests/Report/` |
| **Status Transition** | User manually updates | Auto-transition based on results |
| **Delegation** | ❌ Forbidden | ✅ Required |
| **Test Creation** | ❌ Not created | ✅ Agents write tests |

## Decision Tree

```
Task enters "Testing" status
    ↓
Check: mcp__claudetask__get_project_settings
    ↓
manual_testing_mode = ?
    ↓
    ├─→ TRUE (Manual Mode)
    │   ├─→ Find free ports
    │   ├─→ Start test servers
    │   ├─→ 🔴 SAVE testing URLs (mandatory!)
    │   ├─→ Save stage result
    │   ├─→ Notify user
    │   └─→ WAIT for user to update status
    │
    └─→ FALSE (Automated Mode)
        ├─→ Read analysis docs
        ├─→ Determine test types
        ├─→ Delegate to testing agents
        ├─→ Wait for test reports
        ├─→ Analyze results
        ├─→ Save stage result
        └─→ AUTO-TRANSITION based on results
```

## Key Reminders by Mode

### Manual Mode Checklist:
1. ✅ Find free ports
2. ✅ Start servers
3. ✅ **SAVE URLs** (mandatory!)
4. ✅ Save stage result
5. ✅ Notify user
6. ✅ Wait for user testing
7. ❌ NEVER auto-transition

**The `set_testing_urls` command is NOT optional in Manual Mode - it MUST be called for proper task tracking.**

### Automated Mode Checklist:
1. ✅ Read analysis documents
2. ✅ Determine test types
3. ✅ Delegate to testing agents
4. ✅ Wait for test completion
5. ✅ Analyze test results
6. ✅ Save stage result with test summary
7. ✅ Auto-transition based on results
8. ✅ Create test reports in `/Tests/Report/`

**Testing agents MUST be used in Automated Mode - manual testing is not applicable.**
