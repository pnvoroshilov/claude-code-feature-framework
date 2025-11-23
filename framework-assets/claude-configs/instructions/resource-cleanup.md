# 🧹 Resource Cleanup - Task Completion

## When to Clean Up Resources

**⚠️ ONLY when user EXPLICITLY requests task completion**

User must type exact phrases like:
- "mark task X as done"
- "complete task X"
- Use `/merge` command

**❌ NEVER clean up resources automatically**
**❌ NEVER clean up without explicit user request**

## What Resources to Clean Up

When task is marked as Done:
1. ✅ Claude session (if active)
2. ✅ Embedded terminal sessions
3. ✅ Test server processes (frontend, backend)
4. ✅ Occupied ports
5. ✅ Testing URLs from task
6. ✅ Git worktree (if no remote repository)

## Automated Cleanup Command (PREFERRED)

**Use this single command for complete cleanup:**

```bash
mcp:stop_session {task_id}
```

**This command automatically:**
- Completes the Claude session
- Stops all embedded terminal sessions
- Kills all test server processes
- Releases all occupied ports
- Clears testing URLs from task

## Manual Cleanup (If Needed)

**If automated cleanup fails, use manual cleanup:**

### Step 1: Find All Test Processes

```bash
# Get testing URLs from task to find ports
mcp:get_task {task_id}
# Look for testing_urls field

# Check processes on those ports
lsof -i :{frontend_port}
lsof -i :{backend_port}

# Also search for task-specific processes
ps aux | grep "task-{id}"
```

### Step 2: Terminate All Processes

```bash
# Kill frontend process
kill {frontend_pid}

# Kill backend process
kill {backend_pid}

# Kill any other task-specific processes
kill {other_pid}

# If processes won't die, use force kill
kill -9 {pid}
```

### Step 3: Complete Claude Session

```bash
# Call API to complete session
curl -X POST {backend_url}/api/sessions/{task_id}/complete

# Stop embedded sessions if they exist
# (This is usually handled by stop_session)
```

### Step 4: Clear Testing URLs

```bash
# Clear URLs from task
mcp__claudetask__set_testing_urls --task_id={task_id} --urls='{}'
```

## Save Cleanup Results

After cleanup (automated or manual):

```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Done" \
  --summary="Task completed with full resource cleanup" \
  --details="Claude session: Completed
Terminal sessions: Stopped
Test servers: Terminated
Ports released: [list of ports]
All resources freed successfully"
```

## Report Cleanup Completion

```
Task #{id} completed:
- Claude session: Completed ✓
- Terminal sessions: Stopped ✓
- Test servers: Terminated ✓
- Ports released: [list] ✓
- All resources cleaned up ✓
```

## Complete Example

```bash
# User says: "mark task 42 as done"

# 1. Use automated cleanup
mcp:stop_session 42

# 2. Save cleanup results
mcp__claudetask__append_stage_result --task_id=42 --status="Done" \
  --summary="Task completed with full resource cleanup" \
  --details="Claude session: Completed
Terminal sessions: Stopped
Test servers: Terminated (ports 3333, 3001)
All resources freed successfully"

# 3. Update task status
mcp:update_status 42 "Done"

# 4. Report to user
echo "Task #42 completed:
- Claude session: Completed ✓
- Terminal sessions: Stopped ✓
- Test servers: Terminated ✓
- Ports released: 3333, 3001 ✓
- All resources cleaned up ✓"
```

## Why Resource Cleanup is Important

**Clean up resources to:**
- ✅ Free system resources (CPU, memory)
- ✅ Release ports for other tasks
- ✅ Prevent zombie processes
- ✅ Maintain clean development environment
- ✅ Avoid port conflicts with future tasks
- ✅ Ensure proper task state tracking

## Troubleshooting Cleanup

### Process Won't Terminate:
```bash
# Use force kill
kill -9 {pid}

# If still running, check if it's a different process
ps aux | grep {pid}
```

### Port Still Occupied After Killing Process:
```bash
# Check again what's using the port
lsof -i :{port}

# Kill the actual process
kill -9 {actual_pid}

# Wait a moment and check again
sleep 2
lsof -i :{port}
```

### Can't Find Test Processes:
```bash
# List all node processes (frontend)
ps aux | grep node

# List all python processes (backend)
ps aux | grep python

# List all processes with "task-{id}" in command
ps aux | grep "task-{id}"
```

### Session Won't Complete:
```bash
# Check if session exists
curl {backend_url}/api/sessions/embedded/active

# Force stop if needed
# (Contact backend API directly)
```

## Cleanup Checklist

Before marking task as Done:

- [ ] User explicitly requested completion
- [ ] `mcp:stop_session {task_id}` executed
- [ ] All test processes terminated
- [ ] All ports released
- [ ] Testing URLs cleared
- [ ] Claude session completed
- [ ] Worktree merged if no remote (see [local-worktree-merge.md](local-worktree-merge.md))

## 🔀 Git Worktree Cleanup

**For projects WITHOUT remote repository:**

When task is in "Pull Request" status and no remote exists:
1. First merge changes locally - see **[Local Worktree Merge](local-worktree-merge.md)**
2. Then remove worktree as part of cleanup

```bash
# Check if remote exists
git remote -v

# If NO remote, merge first
git checkout main
git merge feature/task-{id} --no-ff

# Then cleanup worktree
git worktree remove worktrees/task-{id}
git branch -d feature/task-{id}
git worktree prune
```

**⚠️ CRITICAL**: Never remove worktree before merging changes!
- [ ] Cleanup results saved with `append_stage_result`
- [ ] Task status updated to "Done"
- [ ] User notified of completion

## What NOT to Clean Up

**NEVER clean up without user request:**
- ❌ Don't clean up just because task looks complete
- ❌ Don't clean up when moving to Code Review or PR
- ❌ Don't clean up based on assumptions
- ❌ Don't delete worktrees (separate explicit request required)
- ❌ Don't delete git branches automatically

**See [critical-restrictions.md](critical-restrictions.md) for deletion rules**
