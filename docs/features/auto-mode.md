# AUTO Mode - Autonomous Task Execution

AUTO mode enables fully autonomous task execution where Claude Code automatically progresses tasks through the workflow without waiting for manual commands.

## Overview

When AUTO mode is enabled (`manual_mode = false`), Claude Code operates as a fully autonomous agent that:
- Continuously monitors the task queue
- Automatically progresses tasks through all stages
- Executes tests and creates pull requests without user intervention
- Only pauses for true human input (manual testing, approvals)

## Mode Comparison

### Manual Mode (`manual_mode = true`)

**Behavior**:
- User explicitly triggers each command (`/next`, `/start`, `/test`, `/PR`)
- Claude waits for user input at each stage
- Full control over workflow progression
- Ideal for learning the framework or careful oversight

**Example Session**:
```
User: /next
Claude: Analyzes task, provides plan
User: /start
Claude: Begins implementation
User: /test
Claude: Sets up testing environment
User: [manually tests]
User: /PR
Claude: Creates pull request
```

### AUTO Mode (`manual_mode = false`)

**Behavior**:
- Claude automatically progresses through stages
- Continuously checks task queue
- Executes commands without user prompts
- Only stops for manual testing or approvals

**Example Session**:
```
Claude: [Automatically picks next task]
Claude: [Analyzes task]
Claude: [Implements changes]
Claude: [Runs automated tests]
Claude: [Sets up manual testing environment]
User: [Tests manually, provides feedback]
Claude: [Automatically creates PR after successful test]
```

## AUTO Mode Workflow

### Stage 1: Task Selection

Claude automatically:
1. Calls `mcp__claudetask__get_task_queue`
2. Identifies highest priority task in "Backlog"
3. Transitions to "Analysis" status
4. No user command needed

### Stage 2: Analysis

Claude automatically:
1. Analyzes task requirements
2. Creates implementation plan
3. Saves analysis results
4. Transitions to "In Progress"
5. No user command needed

### Stage 3: Implementation

Claude automatically:
1. Creates git worktree
2. Implements features
3. Commits changes
4. Detects completion
5. Transitions to "Testing"
6. No user command needed

### Stage 4: Automated Testing

Claude automatically:
1. Sets up test environment
2. Finds available ports
3. Starts development servers
4. Saves testing URLs
5. Runs automated tests if configured

**Critical**: Must use `mcp__claudetask__set_testing_urls` to save URLs.

### Stage 5: Manual Testing (USER ACTION REQUIRED)

**This is where AUTO mode pauses!**

Claude:
1. Notifies user: "Testing URLs saved. Please verify manually."
2. Waits for user to test the implementation
3. Monitors for `/PR` command or user feedback

User must:
1. Open testing URLs
2. Manually verify functionality
3. Provide feedback or issue `/PR` command

### Stage 6: Pull Request Creation (AUTO RESUMES)

After successful manual testing, Claude automatically:
1. Detects `/PR` command
2. Transitions to "Pull Request" status
3. Creates pull request (if remote repo exists)
4. Or merges locally (if no remote)
5. Saves stage results
6. No additional user command needed

**NEW**: As of recent update, `/PR` is executed automatically after successful tests when `manual_mode = false`.

### Stage 7: Continuous Monitoring

Claude continues:
1. Returns to monitoring task queue
2. Picks next task
3. Repeats cycle
4. Never stops unless explicitly commanded

## Configuration

### Enable AUTO Mode

**Via MCP Tool**:
```bash
mcp__claudetask__update_project_settings \
  --project_id="your-project-id" \
  --manual_mode=false
```

**Via API**:
```http
PUT /api/projects/{project_id}/settings
Content-Type: application/json

{
  "manual_mode": false
}
```

**Via UI**:
1. Navigate to Project Settings
2. Toggle "Manual Mode" switch OFF
3. Save changes

### Check Current Mode

```bash
# Via MCP
mcp__claudetask__get_project_settings --project_id="your-project-id"

# Via API
curl http://localhost:3333/api/projects/{project_id}/settings
```

Response includes:
```json
{
  "manual_mode": false,
  "auto_transition_enabled": true
}
```

## AUTO Mode Instructions

Claude follows specific instructions in AUTO mode (from `.claudetask/instructions/auto-mode-monitoring.md`):

### Continuous Monitoring Loop

```
WHILE manual_mode = false:
  1. Check task queue
  2. Get next highest priority task
  3. Analyze and implement
  4. Run automated tests
  5. Setup manual testing environment
  6. PAUSE for user testing
  7. After /PR command: create PR automatically
  8. Return to step 1
```

### Critical AUTO Mode Rules

1. **Never Stop Monitoring**: Always check queue after completing task
2. **Auto-Execute /PR**: After successful tests, automatically create PR
3. **Pause for Human Input**: Only stop at manual testing stage
4. **Save Testing URLs**: Always use `set_testing_urls` tool
5. **Stage Results**: Save results at every transition

## Test Command AUTO Mode

Special behavior for `/test` command in AUTO mode (from `.claudetask/instructions/test-command-auto-mode.md`):

### AUTO Mode Test Flow

```bash
# When user or system executes /test

1. Setup test environment (ports, servers)
2. Save testing URLs (mandatory)
3. Run automated tests
4. If tests pass:
   - Display success message
   - AUTOMATICALLY execute /PR command
   - No user intervention needed
5. If tests fail:
   - Display error details
   - Pause for user investigation
   - Wait for manual /PR or fixes
```

### Key Change

**Before**: Even in AUTO mode, user had to manually execute `/PR` after tests passed.

**After**: In AUTO mode, `/PR` executes automatically after successful tests.

**Manual Mode**: User still must explicitly execute `/PR`.

## Examples

### Example 1: Complete AUTO Session

```
[Session Start]
Claude: Checking task queue...
Claude: Found task #45: "Implement user profile page"
Claude: Transitioning to Analysis...
Claude: Analysis complete. Creating implementation plan...
Claude: Transitioning to In Progress...
Claude: Creating worktree for task-45...
Claude: Implementing user profile component...
Claude: [3 commits made]
Claude: Implementation complete. Transitioning to Testing...
Claude: Finding available port... Found: 3001
Claude: Starting development server on http://localhost:3001
Claude: Testing URLs saved.
Claude: ⚠️ Manual testing required. Please verify:
        - Frontend: http://localhost:3001
        - Backend: http://localhost:3333
        Navigate to /profile page and test functionality.
Claude: Waiting for your feedback or /PR command...

[User manually tests the feature]

User: /PR
Claude: Tests successful! Creating pull request...
Claude: Transitioning to Pull Request status...
Claude: PR created: https://github.com/user/repo/pull/123
Claude: Task #45 completed. Returning to monitoring...
Claude: Checking task queue...
Claude: Found task #46: "Add email notifications"
[Cycle continues...]
```

### Example 2: AUTO Mode with Test Automation

```
[After implementation]
Claude: Transitioning to Testing...
Claude: Setting up test environment...
Claude: Running automated tests...
Claude: ✅ All tests passed (42 tests, 0 failures)
Claude: Automatically executing /PR command...
Claude: Creating pull request...
Claude: Task #47 completed. Moving to next task...
```

### Example 3: Manual Mode (for comparison)

```
[After implementation]
Claude: Implementation complete. Ready for testing.
Claude: [Waits for user]

User: /test
Claude: Setting up test environment...
Claude: Testing URLs saved. Please verify manually.
Claude: [Waits for user]

User: [manually tests]
User: /PR
Claude: Creating pull request...
```

## Monitoring AUTO Mode

### Check Active Status

```bash
# View current task
mcp__claudetask__get_current_task

# View task queue
mcp__claudetask__get_task_queue

# View project settings
mcp__claudetask__get_project_settings
```

### View Logs

AUTO mode operations are logged:

```bash
# Backend logs
tail -f claudetask/backend/server.log | grep AUTO

# MCP server logs
tail -f /tmp/claudetask_mcp.log | grep autonomous
```

## Pausing AUTO Mode

### Temporary Pause

```bash
# Interrupt current task (keeps AUTO mode enabled)
mcp__claudetask__update_status \
  --task_id={id} \
  --status="In Progress" \
  --comment="Pausing for manual investigation"
```

### Disable AUTO Mode

```bash
# Switch to manual mode
mcp__claudetask__update_project_settings \
  --manual_mode=true
```

## Best Practices

### When to Use AUTO Mode

**Good Use Cases**:
- ✅ Well-defined backlog of tasks
- ✅ Trusted codebase with tests
- ✅ Rapid iteration needed
- ✅ Working on multiple tasks sequentially
- ✅ Offline/async development

**Not Recommended**:
- ❌ Learning the framework
- ❌ Experimental/risky changes
- ❌ Need to review each step carefully
- ❌ Complex tasks requiring frequent human input

### Safety Measures

1. **Always Test Manually**: Never skip manual testing stage
2. **Monitor Progress**: Check logs periodically
3. **Version Control**: AUTO mode respects git workflow
4. **Easy Disable**: Can switch back to manual mode anytime
5. **Clear Feedback**: AUTO mode provides status updates

### Optimization Tips

1. **Prepare Backlog**: Prioritize tasks before enabling AUTO
2. **Clear Descriptions**: Well-defined tasks work best
3. **Automated Tests**: Add tests to speed up verification
4. **Fast Testing**: Set up quick manual testing procedures
5. **Monitor Queue**: Keep high-priority tasks at top

## Troubleshooting

### AUTO Mode Not Working

**Check mode setting**:
```bash
curl http://localhost:3333/api/projects/{project_id}/settings
# Should show: "manual_mode": false
```

**Check task queue**:
```bash
mcp__claudetask__get_task_queue
# Should show tasks in Backlog status
```

**Check MCP server**:
```bash
ps aux | grep claudetask_mcp
# Should show running process
```

### Tasks Not Auto-Progressing

**Common causes**:
1. No tasks in "Backlog" status
2. Manual mode still enabled
3. Task has errors/blocks
4. MCP server not responding

**Solutions**:
```bash
# Verify mode
mcp__claudetask__get_project_settings

# Check for errors
curl http://localhost:3333/api/projects/{project_id}/tasks/{task_id}

# Restart MCP server
# Close and reopen Claude Code
```

### Stuck at Manual Testing

**Expected behavior**: AUTO mode pauses here for human verification.

**To continue**:
1. Open testing URLs
2. Verify functionality
3. Issue `/PR` command
4. Or provide feedback if issues found

### Too Many Tasks Running

**Symptom**: Multiple worktrees, servers, or PRs active

**Solution**:
```bash
# Stop current task
mcp__claudetask__stop_session --task_id={id}

# Switch to manual mode
mcp__claudetask__update_project_settings --manual_mode=true

# Clean up resources
git worktree prune
pkill -f "port 3001"  # Kill test servers
```

## Performance Considerations

### Resource Usage

AUTO mode may create:
- Multiple git worktrees simultaneously
- Multiple test server instances
- High CPU usage during analysis
- Network traffic for API calls

**Mitigation**:
- Limit concurrent tasks (framework handles this)
- Clean up completed tasks promptly
- Monitor system resources

### Rate Limiting

AUTO mode respects:
- GitHub API rate limits
- MCP server request limits
- Database connection limits

If rate limited:
- Automatic backoff implemented
- Tasks queued for retry
- User notified of delays

## API Integration

### Webhooks for AUTO Mode

Configure webhooks to trigger AUTO mode:

```http
POST /api/projects/{project_id}/webhooks
Content-Type: application/json

{
  "event": "task_created",
  "action": "auto_start_if_enabled"
}
```

### Status Notifications

Subscribe to AUTO mode notifications:

```http
POST /api/projects/{project_id}/notifications/subscribe
Content-Type: application/json

{
  "channels": ["auto_mode_status"],
  "webhook_url": "https://your-service.com/webhook"
}
```

## Comparison Matrix

| Feature | Manual Mode | AUTO Mode |
|---------|-------------|-----------|
| Task Selection | User command | Automatic |
| Analysis | User command | Automatic |
| Implementation | User command | Automatic |
| Testing Setup | User command | Automatic |
| Manual Testing | User required | User required |
| PR Creation | User command | Automatic |
| Continuous Operation | No | Yes |
| User Oversight | High | Low |
| Speed | Slower | Faster |
| Control | Full | Delegated |

## Summary

AUTO mode transforms Claude Code into a fully autonomous development agent:

- **Automatic**: Progresses tasks without manual commands
- **Intelligent**: Pauses only for necessary human input
- **Fast**: Eliminates wait time between stages
- **Safe**: Maintains git workflow and testing requirements
- **Flexible**: Can switch back to manual mode anytime

Key innovation: After recent update, `/PR` command executes automatically after successful tests, eliminating the last manual step in AUTO mode workflow.

Perfect for rapid iteration, batch processing multiple tasks, or offline development sessions where you want Claude to autonomously work through your backlog while you focus on other work.
