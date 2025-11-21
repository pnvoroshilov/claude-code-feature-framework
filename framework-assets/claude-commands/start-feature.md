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

### Step 3: Follow MCP Instructions and New Workflow
Based on the task's current status, MCP will provide specific next steps:

- **Backlog** → Move to "Analyse" status and create Analyse/ folder
- **Analyse** → Delegate to Requirements Writer and System Architect agents
- **In Progress** → Begin development in task worktree
- **Tests** → Perform manual testing and document in Tests/ folder
- **Code Review** → Review code changes (if manual_mode enabled)
- **PR** → Create pull request and merge
- **Blocked** → Instructions to resolve blockers

### New Workflow for Analysis Phase:

When task enters "Analyse" status:

1. **Create Analyse Folder in Worktree:**
```bash
# MCP will automatically create Analyse/ folder in task worktree
# Contains: README.md with instructions
```

2. **Delegate to Requirements Analyst Agent:**
```bash
# Use Task tool to delegate
Task tool with requirements-analyst agent:
"Create comprehensive requirements documentation for this task.

**STEP 1: Check Other Active Tasks**
Run: mcp:get_task_queue

**STEP 2: Analyze Project Documentation**
Review docs/architecture/, docs/api/, docs/components/

**STEP 3: Create Requirements**
Task details: [task info]
Output to: worktrees/task-<id>/Analyze/Requirements/"
```

3. **Wait for requirements documentation completion**

4. **Delegate to System Architect Agent:**
```bash
# Use Task tool to delegate
Task tool with system-architect agent:
"Create technical architecture document for this task.
Requirements: [from requirements.md]
Task details: [task info]
Output to: worktrees/task-<id>/Analyse/architecture.md"
```

5. **After both documents created → Move to "In Progress"**

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