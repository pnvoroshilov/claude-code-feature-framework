# MCP Tools Reference

Complete reference for ClaudeTask MCP (Model Context Protocol) tools available to Claude Code agents.

## Overview

ClaudeTask provides MCP tools through the `claudetask` MCP server, which bridges Claude Code with the ClaudeTask backend API. These tools enable task management, code search, and project configuration.

## MCP Server Configuration

**Location:** `.mcp.json` in project root

**Server Name:** `claudetask`

**Configuration:**
```json
{
  "mcpServers": {
    "claudetask": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/claudetask/mcp_server/native_stdio_server.py"],
      "env": {
        "CLAUDETASK_PROJECT_ID": "project-uuid",
        "CLAUDETASK_PROJECT_PATH": "/path/to/project",
        "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
      }
    }
  }
}
```

## Available Tools

### Task Management

#### `get_task_queue`
Get all tasks in the queue for the current project.

**Usage:**
```
mcp:get_task_queue
```

**Returns:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Add continue button to task cards",
      "status": "Backlog",
      "priority": "High",
      "type": "Feature",
      "description": "...",
      "created_at": "2025-11-20T10:00:00"
    }
  ],
  "total": 1
}
```

#### `get_next_task`
Get the highest priority task from the queue.

**Usage:**
```
mcp:get_next_task
```

**Returns:** Single task object (highest priority)

#### `get_task`
Get detailed information about a specific task.

**Parameters:**
- `task_id` (required): Task ID

**Usage:**
```
mcp:get_task --task_id=42
```

**Returns:** Complete task details including history and stage results

#### `update_status`
Update the status of a task.

**Parameters:**
- `task_id` (required): Task ID
- `status` (required): New status (Backlog, Analysis, In Progress, Testing, Code Review, PR, Done, Blocked)

**Usage:**
```
mcp:update_status --task_id=42 --status="In Progress"
```

#### `append_stage_result`
Save stage-specific results for a task (analysis, implementation, testing, etc.).

**Parameters:**
- `task_id` (required): Task ID
- `status` (required): Current status/stage
- `summary` (required): Brief summary of results
- `details` (optional): Detailed results

**Usage:**
```
mcp:append_stage_result --task_id=42 --status="Analysis" \
  --summary="Requirements analyzed" \
  --details="Detailed requirements and implementation plan"
```

#### `set_testing_urls`
Save testing environment URLs for a task.

**Parameters:**
- `task_id` (required): Task ID
- `urls` (required): JSON object with frontend/backend URLs

**Usage:**
```
mcp:set_testing_urls --task_id=42 \
  --urls='{"frontend": "http://localhost:3001", "backend": "http://localhost:4000"}'
```

**Important:** This is MANDATORY when setting up test environments. URLs are saved to task database for persistent access.

### Project Configuration

#### `get_project_settings` ⭐ NEW
Get current project settings including mode and worktree configuration.

**Usage:**
```
mcp:get_project_settings
```

**Returns:**
```json
{
  "project_id": "abc-123",
  "project_name": "My Project",
  "project_path": "/path/to/project",
  "project_mode": "development",
  "worktree_enabled": true,
  "custom_instructions": "Project-specific instructions...",
  "tech_stack": ["React", "FastAPI", "TypeScript"]
}
```

**Use Cases:**
- Determine current project mode (simple vs development)
- Check if worktrees are enabled
- Read custom instructions dynamically
- Adapt behavior based on project configuration

**Example Usage in CLAUDE.md:**
```markdown
Before starting work, check project settings:

1. Call `mcp:get_project_settings`
2. If `project_mode = "simple"`:
   - Use simplified 3-column workflow
   - Skip worktree creation
   - Work directly in main branch
3. If `project_mode = "development"`:
   - Use full 7-column workflow
   - Create worktrees if `worktree_enabled = true`
   - Follow complete git workflow
```

**Benefits:**
- Dynamic CLAUDE.md behavior based on actual settings
- No need to regenerate CLAUDE.md on settings change
- Single source of truth in database
- Real-time configuration awareness

### RAG (Retrieval-Augmented Generation)

#### `search_codebase`
Semantic search across project codebase.

**Parameters:**
- `query` (required): Search query
- `top_k` (optional, default: 15): Number of results
- `language` (optional): Filter by programming language
- `file_type` (optional): Filter by file extension

**Usage:**
```
mcp:search_codebase --query="button component implementation" --top_k=20 --language="typescript"
```

**Returns:**
```json
{
  "results": [
    {
      "file_path": "src/components/Button.tsx",
      "similarity_score": 0.92,
      "content": "...",
      "line_number": 15
    }
  ]
}
```

#### `find_similar_tasks`
Find similar past tasks for learning implementation patterns.

**Parameters:**
- `task_description` (required): Task description
- `top_k` (optional, default: 10): Number of results

**Usage:**
```
mcp:find_similar_tasks --task_description="Add continue button to UI" --top_k=5
```

**Returns:** Similar tasks with implementation details and outcomes

### Git Worktree Management

#### `create_worktree`
Create a git worktree for a task (DEVELOPMENT mode only).

**Parameters:**
- `task_id` (required): Task ID

**Usage:**
```
mcp:create_worktree --task_id=42
```

Creates worktree at `worktrees/task-42` with branch `feature/task-42`

#### `delete_worktree`
Delete a task's worktree (ONLY on explicit user request).

**Parameters:**
- `task_id` (required): Task ID

**Usage:**
```
mcp:delete_worktree --task_id=42
```

**Warning:** NEVER call this automatically. Only when user explicitly requests deletion.

### Agent Delegation

#### `delegate_to_agent`
Delegate work to a specialized agent.

**Parameters:**
- `task_id` (required): Task ID
- `agent` (required): Agent name
- `instructions` (required): Work instructions

**Usage:**
```
mcp:delegate_to_agent --task_id=42 --agent="frontend-developer" \
  --instructions="Implement the button component following Material-UI patterns"
```

**Available Agents:**
- `business-analyst` - Business requirements analysis
- `systems-analyst` - Technical architecture analysis
- `frontend-developer` - React/TypeScript development
- `backend-architect` - FastAPI/Python backend
- `mobile-react-expert` - Mobile-first React development
- `fullstack-code-reviewer` - Code review
- `quality-engineer` - Test creation
- `web-tester` - E2E testing
- `devops-engineer` - Deployment and infrastructure
- `technical-writer` - Documentation

### Session Management

#### `stop_session`
Stop a Claude Code session and clean up all resources.

**Parameters:**
- `task_id` (required): Task ID

**Usage:**
```
mcp:stop_session --task_id=42
```

**Cleanup Actions:**
- Terminates embedded terminal sessions
- Kills test server processes
- Releases occupied ports
- Clears testing URLs
- Marks session as complete

**Important:** Always call this when task is done to free system resources.

## Tool Usage Patterns

### Pattern 1: Continuous Task Monitoring
```bash
# Infinite loop for task processing
while true; do
  mcp:get_task_queue
  # If tasks found:
  mcp:get_next_task
  mcp:update_status --task_id=$ID --status="Analysis"
  # Analyze...
  mcp:append_stage_result --task_id=$ID --status="Analysis" --summary="..."
  mcp:update_status --task_id=$ID --status="In Progress"
done
```

### Pattern 2: RAG-Enhanced Analysis
```bash
# Before analyzing, search for context
mcp:search_codebase --query="similar button implementations"
mcp:find_similar_tasks --task_description="button feature"

# Analyze with context
# Provide enriched analysis to implementation agents
```

### Pattern 3: Testing Environment Setup
```bash
# When moving to Testing status:
# 1. Find free ports
lsof -i :3001
lsof -i :4000

# 2. Start servers
# 3. MANDATORY: Save testing URLs
mcp:set_testing_urls --task_id=$ID \
  --urls='{"frontend": "http://localhost:3001", "backend": "http://localhost:4000"}'

# 4. Save stage result
mcp:append_stage_result --task_id=$ID --status="Testing" \
  --summary="Test environment ready with URLs saved"

# 5. Notify user with URLs
```

### Pattern 4: Dynamic Mode Adaptation
```bash
# At session start:
settings=$(mcp:get_project_settings)

if [ "$settings.project_mode" = "simple" ]; then
  # Use 3-column workflow
  # Skip worktree creation
  # Work in main branch
else
  # Use 7-column workflow
  if [ "$settings.worktree_enabled" = true ]; then
    mcp:create_worktree --task_id=$ID
  fi
fi
```

### Pattern 5: Complete Task Lifecycle
```bash
# 1. Get task
mcp:get_next_task

# 2. Check project settings
mcp:get_project_settings

# 3. Analyze
mcp:search_codebase --query="relevant context"
mcp:find_similar_tasks --task_description="$TASK_DESC"
mcp:append_stage_result --task_id=$ID --status="Analysis" --summary="..."

# 4. Implement (via agent delegation)
mcp:delegate_to_agent --task_id=$ID --agent="frontend-developer" --instructions="..."

# 5. Setup testing
mcp:set_testing_urls --task_id=$ID --urls='...'

# 6. Cleanup when done
mcp:stop_session --task_id=$ID
```

## Error Handling

### Common Errors

**Task Not Found:**
```json
{
  "error": "Task with ID 999 not found",
  "code": "TASK_NOT_FOUND"
}
```

**Invalid Status Transition:**
```json
{
  "error": "Cannot transition from Done to In Progress",
  "code": "INVALID_TRANSITION"
}
```

**Worktree Already Exists:**
```json
{
  "error": "Worktree for task 42 already exists",
  "code": "WORKTREE_EXISTS"
}
```

**MCP Server Not Responding:**
```json
{
  "error": "Failed to connect to ClaudeTask backend",
  "code": "CONNECTION_ERROR"
}
```

### Error Recovery

1. **Connection Errors:** Verify backend is running on port 3333
2. **Task Errors:** Use `get_task` to verify current state
3. **Worktree Errors:** Check `git worktree list` for conflicts
4. **Permission Errors:** Verify MCP server has project access

## Best Practices

### 1. Always Check Project Settings First
```bash
# Start every session by checking configuration
mcp:get_project_settings
# Adapt workflow based on results
```

### 2. Save Testing URLs Immediately
```bash
# MANDATORY when starting test servers
mcp:set_testing_urls --task_id=$ID --urls='...'
# Do NOT skip this step
```

### 3. Use RAG Before Analysis
```bash
# Gather context before analyzing
mcp:search_codebase --query="relevant code"
mcp:find_similar_tasks --task_description="..."
# Then analyze with rich context
```

### 4. Append Stage Results Frequently
```bash
# After each major step
mcp:append_stage_result --task_id=$ID --status="..." --summary="..."
# Builds audit trail
```

### 5. Clean Up Resources
```bash
# When task complete
mcp:stop_session --task_id=$ID
# Frees ports, kills processes
```

### 6. Never Auto-Delete Worktrees
```bash
# WRONG:
mcp:delete_worktree --task_id=$ID  # Automatic deletion

# CORRECT:
# Only when user explicitly says: "delete worktree for task 42"
mcp:delete_worktree --task_id=$ID
```

## Troubleshooting

### Tool Not Available
**Symptom:** `mcp:get_project_settings` not recognized

**Solutions:**
1. Check `.mcp.json` exists in project root
2. Verify `claudetask` server is configured
3. Restart Claude Code to reload MCP servers
4. Check MCP server logs: `claudetask/mcp_server/logs/`

### Incorrect Project Settings
**Symptom:** `get_project_settings` returns wrong mode

**Solutions:**
1. Check database: `SELECT * FROM project_settings WHERE project_id = '...'`
2. Verify project ID in `.mcp.json` matches database
3. Regenerate CLAUDE.md: `POST /api/projects/{id}/regenerate-claude-md`

### Testing URLs Not Saved
**Symptom:** URLs disappear after session restart

**Solutions:**
1. Verify `set_testing_urls` was called
2. Check database: `SELECT testing_urls FROM tasks WHERE id = ...`
3. Ensure JSON format is correct: `{"frontend": "...", "backend": "..."}`

## See Also

- [Task Management API](./endpoints/tasks.md)
- [Project Settings API](./endpoints/projects.md)
- [RAG Indexing](./endpoints/rag-indexing.md)
- [CLAUDE.md Configuration](../../CLAUDE.md)
