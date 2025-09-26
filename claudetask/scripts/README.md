# ClaudeTask Scripts

## Session & Resource Management Tools

### 🛑 test_stop_session.py
Test the `stop_session` MCP command for proper cleanup of Claude sessions and test servers.

**Usage:**
```bash
python test_stop_session.py TASK_ID
```

**What it does:**
- Shows current task status and running processes
- Calls the MCP `stop_session` command
- Verifies that Claude session is completed
- Checks that test server processes are killed
- Confirms ports are released
- Validates testing URLs are cleared

**Example:**
```bash
# Test cleanup for task 23
python test_stop_session.py 23
```

## Testing URL Validation Tools

### 🔍 validate_testing_urls.py
Validates that all tasks in Testing status have their URLs properly saved.

**Usage:**
```bash
python validate_testing_urls.py
```

**What it checks:**
- All tasks currently in Testing status
- Whether testing URLs are saved for each task
- Recent testing status transitions
- Provides fix commands if URLs are missing

### 🔧 fix_missing_urls.py
Helper script to manually save testing URLs when the framework forgets.

**Usage:**
```bash
# Basic usage with default ports
python fix_missing_urls.py TASK_ID

# Specify custom ports
python fix_missing_urls.py TASK_ID --frontend-port 3002 --backend-port 4001

# Check before overwriting
python fix_missing_urls.py TASK_ID --check-first
```

**Examples:**
```bash
# Fix task 23 with default ports (frontend: 3001, backend: 4000)
python fix_missing_urls.py 23

# Fix task 24 with custom ports
python fix_missing_urls.py 24 --frontend-port 3005 --backend-port 4500
```

## Why Testing URLs Must Be Saved

When the framework moves a task to Testing status and sets up test environments, it **MUST** save the URLs using `mcp__claudetask__set_testing_urls`. This is critical for:

1. **Task Tracking** - URLs are permanently stored in the task database
2. **User Access** - Users can retrieve test URLs anytime from task details
3. **Framework Validation** - Ensures test environments are properly tracked
4. **Debugging** - Helps identify which ports are used by which tasks

## Common Issues

### Issue: Framework forgets to save URLs
**Solution:** The CLAUDE.md file has been updated with prominent warnings and a mandatory checklist to ensure URLs are always saved.

### Issue: URLs not saved after test environment setup
**Quick Fix:** 
```bash
python fix_missing_urls.py TASK_ID --frontend-port ACTUAL_PORT --backend-port ACTUAL_PORT
```

### Issue: Need to validate all testing tasks
**Run validation:**
```bash
python validate_testing_urls.py
```

## Prevention

The framework should automatically save URLs when transitioning to Testing status by:
1. Starting test servers on available ports
2. **IMMEDIATELY** calling `mcp__claudetask__set_testing_urls` 
3. Only then saving the stage result
4. Notifying the user with confirmation that URLs were saved

This is enforced through the CLAUDE.md instructions marked as **CRITICAL MANDATORY STEP**.