# 🤖 AUTO MODE MONITORING AND COMMAND EXECUTION

**This file provides specific instructions for monitoring tasks and executing commands in AUTO mode.**

## 📋 When `manual_mode = false` (AUTO MODE)

### Continuous Monitoring Loop

```
WHILE TRUE:
  1. Check task queue every 30 seconds
  2. For each task, check for status changes
  3. Execute appropriate commands based on transitions
  4. Track command execution to avoid duplicates
```

## 🎯 Status Transition Detection and Actions

### Monitor for Status Changes

The orchestrator MUST detect when task status changes and execute commands accordingly:

```python
# Pseudo-code for monitoring logic
previous_status = get_task_status(task_id)
current_status = get_task_status(task_id)

if status_changed(previous_status, current_status):
    handle_status_transition(task_id, previous_status, current_status)
```

### Status Transition → Command Mapping

| Previous Status | New Status | Action Required | Command to Execute |
|----------------|------------|-----------------|-------------------|
| Backlog | Analysis | Start analysis | None (agents handle) |
| Analysis | In Progress | Start development | `/start-develop` |
| In Progress | Testing | Start testing | `/test {task_id}` |
| Testing | Code Review | Tests passed | `/PR {task_id}` |
| Testing | In Progress | Tests failed | `/start-develop` |
| Code Review | Done | PR merged | None (cleanup) |
| Code Review | In Progress | Review failed | `/start-develop` |

## 🔍 Detecting Status Transitions

### Method 1: Direct Status Monitoring

```bash
# Check task status periodically
mcp__claudetask__get_task --task_id={id}

# Compare with previous known status
if [previous_status != current_status]:
    # Status changed, take action
```

### Method 2: Stage Results Analysis

```bash
# Check stage_results for completion indicators
mcp__claudetask__get_task --task_id={id}

# Look for stage results indicating completion:
- "Testing completed successfully"
- "All tests passed"
- "Ready for code review"
```

### Method 3: Command Completion Tracking

```bash
# After executing a command, wait for it to complete
SlashCommand("/test 42")

# Monitor for command completion signals:
- Task status change
- Stage result added
- Success/failure message
```

## 🚨 CRITICAL: Prevent Duplicate Commands

**NEVER execute the same command twice for the same transition:**

```bash
# Track executed commands per task
executed_commands[task_id] = []

# Before executing a command
if command not in executed_commands[task_id]:
    SlashCommand(command)
    executed_commands[task_id].append(command)
```

## 📊 Complete AUTO Mode Flow

```
Task Status: Backlog
    ↓
[Analysis agents work]
    ↓
Task Status: Analysis → In Progress (detected)
    ↓
🤖 EXECUTE: /start-develop
    ↓
[Development happens]
    ↓
Task Status: In Progress → Testing (detected)
    ↓
🤖 EXECUTE: /test {task_id}
    ↓
[Tests run]
    ↓
Task Status: Testing → Code Review (detected)
    ↓
🤖 EXECUTE: /PR {task_id}
    ↓
[Code review happens]
    ↓
Task Status: Code Review → Done (detected)
    ↓
🤖 Cleanup resources
```

## 🔄 Handling Manual UI Updates

**IMPORTANT**: Users might update status manually through UI. The orchestrator MUST:

1. **Detect manual status changes**: Compare task status periodically
2. **Catch up with appropriate commands**: If status changed without command execution
3. **Save stage results**: Even for manual transitions

### Example: User manually moves Testing → Code Review

```bash
# Orchestrator detects:
previous_status = "Testing"
current_status = "Code Review"
no_pr_command_executed = True

# Orchestrator should:
if current_status == "Code Review" and no_pr_command_executed:
    # User manually transitioned, execute PR command now
    SlashCommand("/PR {task_id}")
    save_stage_result("Testing completed, PR command executed")
```

## 📝 Stage Results for AUTO Mode

**Every transition MUST save a stage result:**

```bash
# When executing /test command
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="Testing" \
  --summary="Automated testing initiated" \
  --details="/test command executed in AUTO mode"

# When tests complete (detected by status change)
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="Testing" \
  --summary="Tests completed successfully" \
  --details="All tests passed, ready for code review"

# When executing /PR command
mcp__claudetask__append_stage_result \
  --task_id={id} \
  --status="Code Review" \
  --summary="Pull request creation initiated" \
  --details="/PR command executed in AUTO mode"
```

## 🎯 Implementation Checklist

For proper AUTO mode operation, the orchestrator MUST:

1. ✅ **Monitor task queue continuously** (every 30 seconds)
2. ✅ **Track previous status** for each task
3. ✅ **Detect status changes** reliably
4. ✅ **Execute commands** based on transitions
5. ✅ **Prevent duplicate** command execution
6. ✅ **Save stage results** for every transition
7. ✅ **Handle manual updates** gracefully
8. ✅ **Log all actions** for debugging

## 🐛 Troubleshooting

### Commands Not Executing

1. **Check `manual_mode` setting**:
   ```bash
   mcp__claudetask__get_project_settings
   # Ensure manual_mode = false
   ```

2. **Verify status transition detected**:
   - Check if stage_results exist for the transition
   - Ensure orchestrator is monitoring actively

3. **Check for command execution history**:
   - Look for duplicate prevention blocking execution
   - Verify slash command is available

### Status Changes Without Commands

If status changes but commands aren't executed:

1. **Orchestrator might be offline** - Check if monitoring loop is running
2. **Manual UI update** - User changed status directly
3. **Command failed silently** - Check logs for errors

### Recovery Actions

When detecting missed transitions:

```bash
# Example: Task is in Code Review but no /PR executed
if status == "Code Review" and not has_pr_stage_result():
    # Catch up by executing missed command
    SlashCommand("/PR {task_id}")
    append_stage_result("Executed missed /PR command")
```

## 📚 Related Documentation

- [orchestration-role.md](orchestration-role.md) - Main orchestration instructions
- [status-transitions.md](status-transitions.md) - Status flow rules
- [testing-workflow.md](testing-workflow.md) - Testing phase details

## ✅ Success Criteria

AUTO mode is working correctly when:

1. All status transitions trigger appropriate commands
2. No duplicate commands are executed
3. Stage results document every transition
4. Manual UI updates are detected and handled
5. Commands execute within 1 minute of status change