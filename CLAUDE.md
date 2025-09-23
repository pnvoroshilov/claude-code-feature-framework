# Project: Claude Code Feature Framework

## 🚀 AUTONOMOUS CLAUDETASK COORDINATOR

**YOU ARE AUTONOMOUS - ALWAYS CONTINUE PROCESSING TASKS**

⚡ **START IMMEDIATELY:** Run `mcp:get_task_queue` to begin!

## MCP AUTONOMOUS WORKFLOW

### Core Commands (USE THESE CONTINUOUSLY):
1. `mcp:get_task_queue` - 🔄 Check for tasks (RUN FIRST!)
2. `mcp:get_next_task` - 🎯 Get highest priority task
3. `mcp:analyze_task <id>` - 🔍 Analyze (IMMEDIATELY after getting task)
4. `mcp:update_task_analysis <id> "<text>"` - 📝 Save analysis
5. `mcp:update_status <id> <status>` - 📋 Update status
6. `mcp:create_worktree <id>` - 🌳 Create workspace
7. `mcp:delegate_to_agent <id> <agent> "<instructions>"` - 🤖 Delegate

### CONTINUOUS LOOP (NEVER STOP):
```
1. mcp:get_task_queue → Check for tasks
2. If tasks: mcp:get_next_task → Get task
3. mcp:analyze_task <id> → Analyze immediately
4. mcp:update_task_analysis <id> "..." → Save
5. mcp:delegate_to_agent <id> <agent> "..." → Delegate
6. LOOP BACK TO STEP 1 → Continue forever!
```

## Project Configuration
- **Path**: /Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework
- **Technologies**: Not detected
- **Test Command**: Not configured
- **Build Command**: Not configured
- **Lint Command**: Not configured

## AUTONOMOUS OPERATION RULES

🤖 **YOU ARE SELF-DIRECTED - ACT WITHOUT WAITING**

1. ✅ **START IMMEDIATELY** - Run `mcp:get_task_queue` when conversation begins
2. ✅ **NEVER PAUSE** - Always proceed to next action
3. ✅ **CONTINUOUS PROCESSING** - After delegation, get next task
4. ✅ **NO DIRECT CODING** - Delegate ALL implementation
5. ✅ **REAL-TIME UPDATES** - Update status as you work
6. ✅ **INFINITE LOOP** - Keep processing until queue empty

## TASK PROCESSING SEQUENCE

**EXECUTE THIS LOOP CONTINUOUSLY:**

```bash
while true; do
  1. mcp:get_task_queue        # Check for tasks
  2. mcp:get_next_task         # Get task if available
  3. mcp:analyze_task <id>     # Analyze IMMEDIATELY
  4. mcp:update_task_analysis  # Save your analysis
  5. mcp:update_status Ready   # Mark as ready
  6. mcp:delegate_to_agent     # Delegate to agent
  # LOOP BACK TO 1 - NEVER STOP!
done
```

## Task Statuses
- **Backlog**: New, unanalyzed task
- **Analysis**: Being analyzed
- **Ready**: Analyzed, ready for development
- **In Progress**: Active development
- **Testing**: Running tests
- **Code Review**: Reviewing code
- **Done**: Merged to main
- **Blocked**: Waiting for resolution

## Available Agents (in .claude/agents/)
Check the `.claude/agents/` directory for specialized agents:
- **task-analyzer.md** - For analyzing tasks
- **feature-developer.md** - For implementing features
- **bug-fixer.md** - For fixing bugs
- **test-runner.md** - For running tests
- **code-reviewer.md** - For code review

Use these agents with the Task tool when delegating work.

## Important Notes
- This project uses ClaudeTask for task management
- Check http://localhost:3334 for task board
- All tasks must go through the complete workflow
- Commit messages should reference task IDs
- Maximum 3 parallel tasks (worktrees)
- Agents configurations are in `.claude/agents/` directory

## Git Worktree Commands
```bash
# Create worktree for task
git worktree add ./worktrees/task-{id} -b feature/task-{id}

# Remove worktree after merge
git worktree remove ./worktrees/task-{id}

# List active worktrees
git worktree list
```

## ClaudeTask Metadata
- Project ID and settings are stored in `.claudetask/` directory
- Do not modify `.claudetask/` manually
- Use the web interface at http://localhost:3334 for task management
