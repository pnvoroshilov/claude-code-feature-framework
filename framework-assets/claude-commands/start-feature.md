---
allowed-tools: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep, WebSearch, WebFetch, Task]
argument-hint: [task-id]
description: Start working on a task from the ClaudeTask board. Gets task status and follows MCP instructions.
---

# Start Feature Development

I'll start by getting the current task status and following the instructions provided by MCP.

## Getting Task Information

First, let me determine which task to work on:
- If a task ID was provided: I'll get that specific task
- If no task ID: I'll get the next available task from the queue

### Available MCP Commands:
- `mcp:get_task_queue` - View all tasks in the queue
- `mcp:get_next_task` - Get the highest priority task ready for work
- `mcp:get_task <id>` - Get details of a specific task
- `mcp:update_status <id> <status>` - Update task status and receive next steps

## Workflow

### Step 1: Get Task
```bash
# If task ID provided:
mcp:get_task <task_id>

# If no task ID:
mcp:get_next_task
```

### Step 2: Check Current Status
The MCP response will include:
- Task details (title, description, type, priority)
- Current status
- Analysis (if available)
- **Next steps** - Instructions on what to do based on current status

### Step 3: Follow MCP Instructions
Based on the task's current status, MCP will provide specific next steps:

- **Backlog** → Instructions to analyze the task
- **Analysis** → Instructions to complete analysis and move to development
- **In Progress** → Instructions to implement, test, and review
- **Testing** → Instructions to run tests and verify
- **Code Review** → Instructions to review and prepare for merge
- **Blocked** → Instructions to resolve blockers

### Step 4: Update Status
When moving to a new phase:
```bash
mcp:update_status <task_id> "<new_status>"
```

The response will include:
- Confirmation of status change
- **Next steps** for the new status
- Any automated actions taken (like worktree creation)

## Key Principles

1. **Always follow MCP instructions** - Each status update returns specific next steps
2. **Status drives workflow** - The current status determines what actions to take
3. **Automated assistance** - MCP handles worktree creation, branch management, etc.
4. **Clear progression** - Move through statuses systematically

Let me start by getting the task information...