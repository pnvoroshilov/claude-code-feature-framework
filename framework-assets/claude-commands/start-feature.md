---
allowed-tools: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep, WebSearch, WebFetch, Task]
argument-hint: [task-id]
description: Start working on a task from the ClaudeTask board. Gets task status and follows MCP instructions.
---

# Start Feature Development

I'll start by getting the current task status and following the instructions provided by MCP.

## MANDATORY: RAG-First Search Policy

**Before ANY code exploration or implementation, ALWAYS use RAG search:**

```bash
# Search codebase for relevant patterns
mcp__claudetask__search_codebase --query="<feature description>" --top_k=20

# Search documentation for architectural guidance
mcp__claudetask__search_documentation --query="<feature area>" --top_k=10
```

**Why RAG First?**
- Semantic understanding - finds conceptually related code
- Cross-file discovery - identifies patterns across entire codebase
- Historical learning - leverages indexed past implementations
- Faster context gathering - single query vs multiple grep/glob operations

## Getting Task Information

First, let me determine which task to work on:
- If a task ID was provided: I'll get that specific task
- If no task ID: I'll get the next available task from the queue

### Available MCP Commands:
- `mcp__claudetask__get_task_queue` - View all tasks in the queue
- `mcp__claudetask__get_next_task` - Get the highest priority task ready for work
- `mcp__claudetask__get_task` - Get details of a specific task
- `mcp__claudetask__update_status` - Update task status and receive next steps

## Workflow

### Step 1: Get Task
```bash
# If task ID provided:
mcp__claudetask__get_task --task_id=<task_id>

# If no task ID:
mcp__claudetask__get_next_task
```

### Step 2: Check Current Status
The MCP response will include:
- Task details (title, description, type, priority)
- Current status
- Analysis (if available)
- **Next steps** - Instructions on what to do based on current status

### Step 3: RAG Context Gathering (MANDATORY)

**Before proceeding, gather context using RAG:**

```bash
# 1. Search for similar implementations
mcp__claudetask__search_codebase --query="<task title and key features>" --top_k=20

# 2. Search for related documentation
mcp__claudetask__search_documentation --query="<task area: API/UI/database/etc>" --top_k=10

# 3. Find similar historical tasks
mcp__claudetask__find_similar_tasks --task_description="<task description>" --top_k=5
```

### Step 4: Follow MCP Instructions and Workflow
Based on the task's current status, MCP will provide specific next steps:

- **Backlog** → Move to "Analysis" status and create `Analyze/` folder in worktree
- **Analysis** → Delegate to Requirements Writer and System Architect agents
- **In Progress** → Begin development in task worktree
- **Testing** → Perform manual testing and document in `Tests/` folder
- **Code Review** → Review code changes (if manual_mode enabled)
- **Done** → Task completed
- **Blocked** → Instructions to resolve blockers

### New Workflow for Analysis Phase:

When task enters "Analysis" status:

1. **Create Analyze Folder in Worktree:**
```bash
# MCP will automatically create Analyze/ folder in task worktree
# Path: worktrees/task-{id}/Analyze/
# Contains: README.md with instructions
```

**IMPORTANT:** The folder is named `Analyze` (NOT "Analyse")!

2. **RAG Search Before Delegating:**
```bash
# Search existing documentation first
mcp__claudetask__search_documentation --query="architecture patterns {feature area}" --top_k=10

# Search codebase for similar implementations
mcp__claudetask__search_codebase --query="similar feature implementation" --top_k=20
```

3. **Delegate to Requirements Analyst Agent:**
```bash
# Use Task tool to delegate
Task tool with requirements-analyst agent:
"Create comprehensive requirements documentation for this task.

**MANDATORY: Use RAG Search First!**
Before analyzing, run these MCP commands:
- mcp__claudetask__search_codebase --query='<task keywords>' --top_k=20
- mcp__claudetask__search_documentation --query='<feature area>' --top_k=10
- mcp__claudetask__find_similar_tasks --task_description='<description>'

**STEP 1: Check Other Active Tasks**
Run: mcp__claudetask__get_task_queue

**STEP 2: Analyze Project Documentation (from RAG results)**
Review: docs/architecture/, docs/api/, docs/components/

**STEP 3: Create Requirements**
Task details: [task info]
Output to: worktrees/task-<id>/Analyze/requirements.md"
```

4. **Wait for requirements documentation completion**

5. **Delegate to System Architect Agent:**
```bash
# Use Task tool to delegate
Task tool with system-architect agent:
"Create technical architecture document for this task.

**MANDATORY: Use RAG Search First!**
- mcp__claudetask__search_codebase --query='architecture patterns <feature>' --top_k=20
- mcp__claudetask__search_documentation --query='system design <area>' --top_k=10

Requirements: [from requirements.md]
Task details: [task info]
Output to: worktrees/task-<id>/Analyze/architecture.md"
```

6. **After both documents created → Move to "In Progress"**

### Step 5: Update Status
When moving to a new phase:
```bash
mcp__claudetask__update_status --task_id=<task_id> --status="<new_status>"
```

The response will include:
- Confirmation of status change
- **Next steps** for the new status
- Any automated actions taken (like worktree creation)

## Key Principles

1. **RAG First** - Always search codebase and documentation before exploring manually
2. **Always follow MCP instructions** - Each status update returns specific next steps
3. **Status drives workflow** - The current status determines what actions to take
4. **Automated assistance** - MCP handles worktree creation, branch management, etc.
5. **Clear progression** - Move through statuses systematically
6. **Analyze folder path** - Always `worktrees/task-{id}/Analyze/` (NOT "Analyse")

## RAG Search Examples

```bash
# Find authentication implementations
mcp__claudetask__search_codebase --query="user authentication login JWT session" --top_k=20

# Find API patterns
mcp__claudetask__search_codebase --query="REST API endpoint FastAPI router" --top_k=20

# Find UI component patterns
mcp__claudetask__search_codebase --query="React component MUI Material-UI" --top_k=20

# Find database patterns
mcp__claudetask__search_codebase --query="MongoDB repository CRUD operations" --top_k=20

# Find documentation on feature area
mcp__claudetask__search_documentation --query="API design guidelines" --top_k=10
```

Let me start by getting the task information...
