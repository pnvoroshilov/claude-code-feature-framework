# 🧪 /test Command Behavior in AUTO MODE

**CRITICAL: This file defines MANDATORY behavior for the /test command when `manual_mode = false`**

## 🔴🔴🔴 MANDATORY AUTO MODE BEHAVIOR

When executing `/test {task_id}` in AUTO mode (`manual_mode = false`):

### After Tests Complete Successfully

**YOU MUST AUTOMATICALLY EXECUTE THE NEXT COMMAND:**

```bash
# ✅ Tests PASSED
if all_tests_passed:
    # 🔴 MANDATORY: Execute /PR command IMMEDIATELY
    SlashCommand("/PR {task_id}")

    # DO NOT just say "ready for PR"
    # DO NOT wait for user confirmation
    # DO NOT stop after testing
    # EXECUTE THE COMMAND NOW!
```

### After Tests Fail

```bash
# ❌ Tests FAILED
if tests_failed:
    # Return to development
    SlashCommand("/start-develop")

    # Provide failure details
    # List what needs to be fixed
```

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ WRONG: Just reporting test results
```
"All tests passed successfully. The task is ready for code review and PR creation."
```

### ✅ CORRECT: Executing the next command
```
"All tests passed successfully. Now executing /PR command to create pull request..."
[Actually executes: SlashCommand("/PR 42")]
```

### ❌ WRONG: Asking user what to do next
```
"Tests completed. Would you like me to create a PR?"
```

### ✅ CORRECT: Automatic continuation
```
"Tests completed successfully. Automatically proceeding with PR creation..."
[Executes: SlashCommand("/PR 42")]
```

## 📋 Complete /test Command Flow in AUTO MODE

```
/test {task_id} executed
    ↓
Run automated tests
    ↓
Analyze results
    ↓
Tests PASSED? ──────┬─── YES ───→ 🔴 EXECUTE: /PR {task_id}
                    │                   ↓
                    │              Create PR
                    │                   ↓
                    │              Update status
                    │
                    └─── NO ────→ EXECUTE: /start-develop
                                        ↓
                                   Return to coding

```

## 🎯 Implementation Checklist for /test Command

When `/test` command completes in AUTO mode:

1. ✅ Analyze test results
2. ✅ Save stage result with test summary
3. ✅ **EXECUTE NEXT COMMAND BASED ON RESULTS**
   - If PASSED → `/PR {task_id}`
   - If FAILED → `/start-develop`
4. ✅ Update task status accordingly
5. ✅ Continue autonomous workflow

## 📝 Stage Results Required

```bash
# After tests pass and before executing /PR
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="Testing" \
  --summary="All automated tests passed" \
  --details="Unit tests: 50/50 passed
Integration tests: 20/20 passed
E2E tests: 10/10 passed
Proceeding to PR creation"

# Then IMMEDIATELY execute
SlashCommand("/PR {task_id}")
```

## 🚨 CRITICAL REMINDERS

1. **AUTO MODE = AUTONOMOUS WORKFLOW**
   - Don't stop after testing
   - Don't ask for confirmation
   - Execute next command automatically

2. **CHAIN COMMANDS TOGETHER**
   - `/test` → `/PR` (if passed)
   - `/test` → `/start-develop` (if failed)

3. **NO HUMAN INTERVENTION IN AUTO MODE**
   - The whole point of AUTO mode is automation
   - Commands should chain without waiting

## 🔍 How to Check if in AUTO Mode

```bash
# Check project settings
mcp__claudetask__get_project_settings

# Look for:
"Workflow Mode: Automated (manual_mode=false)"

# If TRUE → Follow this document
# If FALSE → Follow manual testing workflow
```

## ❓ Decision Tree

```
Is manual_mode = false?
    ↓
   YES (AUTO MODE)
    ↓
Tests completed?
    ↓
Tests passed? ──┬── YES → EXECUTE /PR {task_id} NOW!
                │
                └── NO → EXECUTE /start-develop NOW!
```

## 📚 Related Documentation

- [orchestration-role.md](orchestration-role.md) - Main orchestration instructions
- [testing-workflow.md](testing-workflow.md) - Testing phase details
- [auto-mode-monitoring.md](auto-mode-monitoring.md) - AUTO mode monitoring

## ✅ Success Criteria

The `/test` command in AUTO mode is successful when:

1. Tests are executed automatically
2. Results are analyzed programmatically
3. **Next command is executed without human intervention**
4. Workflow continues seamlessly
5. No "ready for PR" messages without actual PR command execution