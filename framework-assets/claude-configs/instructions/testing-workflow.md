# 🧪 Testing Workflow - Manual Testing Setup

⚠️ **This applies to DEVELOPMENT MODE only. SIMPLE mode has no Testing status.**

## 🚨🚨🚨 CRITICAL TESTING URL REQUIREMENT 🚨🚨🚨

**⛔ FAILURE TO SAVE TESTING URLs = CRITICAL ERROR**
**You MUST save testing URLs IMMEDIATELY after starting test servers**
**This is NOT optional - it is MANDATORY for task tracking**

## When Testing Phase Starts

**Testing status is triggered when**:
- Task transitions from "In Progress" to "Testing"
- Implementation is detected as complete
- User manually updates status to "Testing"

## 📋 TESTING ENVIRONMENT CHECKLIST (ALL STEPS REQUIRED)

When task moves to "Testing" status:

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

## What NOT to Do in Testing Status

❌ **DO NOT delegate to testing agents** - This is for MANUAL testing only
❌ **DO NOT create automated tests** - Unless explicitly requested
❌ **DO NOT auto-transition** - Wait for user to update status
❌ **DO NOT run test commands** - User will test manually

## Testing Status Exit

**User will update status when testing is complete:**

- If tests pass → User updates to "Code Review"
- If bugs found → User updates to "In Progress" to fix
- If major issues → User may update to "Analysis" to re-evaluate

**You should NEVER auto-transition from Testing status.**

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

## Key Reminder

**EVERY TIME you setup test environment:**
1. ✅ Find free ports
2. ✅ Start servers
3. ✅ **SAVE URLs** (mandatory!)
4. ✅ Save stage result
5. ✅ Notify user
6. ✅ Wait for user testing

**The `set_testing_urls` command is NOT optional - it MUST be called for proper task tracking.**
