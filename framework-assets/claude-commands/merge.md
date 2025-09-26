---
allowed-tools: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep, WebSearch, WebFetch, Task]
argument-hint: [task-id]
description: Complete a task by merging PR, cleaning worktree, and stopping session
---

# /merge Command - Complete Task and Merge PR

You've been asked to complete Task {{TASK_ID}} by merging its pull request and cleaning up the development environment.

## EXECUTE THESE STEPS IN ORDER:

### 1. Verify Task Status
First, check that the task is in PR status and has an open pull request:
```bash
mcp:get_task {{TASK_ID}}
```

### 2. Merge Pull Request
Use MCP to complete the task, which will:
- Merge the pull request to main branch
- Delete the feature branch
- Remove the worktree
```bash
mcp:complete_task {{TASK_ID}}
```

### 3. Update Task Status to Done
After successful merge, update the task status:
```bash
mcp:update_status {{TASK_ID}} Done "PR merged, worktree cleaned"
```

### 4. Stop Claude Session and Clean Resources
Stop the Claude session and terminate all test servers:
```bash
mcp:stop_session {{TASK_ID}}
```
This will:
- Complete the Claude session
- Stop any embedded terminal sessions
- Kill all test server processes (frontend/backend)
- Free up ports for other tasks

## Important Notes:

⚠️ **CRITICAL**: This command should only be run when:
- Task is in PR status
- User has reviewed and approved the PR
- All tests are passing
- User clicked "Done" button to trigger this command

🌳 **Worktree Cleanup**: The worktree at `./worktrees/task-{{TASK_ID}}` will be removed

🔄 **Git Operations**:
- Feature branch `feature/task-{{TASK_ID}}` will be merged
- Branch will be deleted after merge
- Changes will be in main branch

📊 **Final State**:
- Task status: Done
- PR: Merged
- Worktree: Removed
- Branch: Deleted
- Claude session: Completed
- Terminal sessions: Stopped
- Test servers: Terminated
- Ports: Released

## Error Handling:

If merge fails:
1. Check for merge conflicts
2. Ensure PR is approved
3. Verify tests are passing
4. Report specific error to user

## Completion Message:

After successful completion, report:
```
✅ Task #{{TASK_ID}} Completed Successfully!

- Pull Request: Merged ✓
- Feature Branch: Deleted ✓
- Worktree: Cleaned ✓
- Task Status: Done ✓
- Claude Session: Completed ✓
- Terminal Sessions: Stopped ✓
- Test Servers: Terminated ✓
- Ports: Released ✓

The implementation is now in the main branch.
All resources have been cleaned up.
```