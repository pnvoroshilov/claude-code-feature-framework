# 🛠️ MCP Command Reference

## Essential Commands (Use Continuously)

### Task Queue Management

```bash
# Primary monitoring command - use constantly
mcp:get_task_queue

# Get highest priority task
mcp:get_next_task

# Get specific task details
mcp:get_task <task_id>
```

### Task Status Management

```bash
# Update task status
mcp:update_status <task_id> <status>

# Example
mcp:update_status 42 "Testing"
```

### Stage Results (MANDATORY for Every Status Change)

```bash
# Save results after each phase
mcp__claudetask__append_stage_result \
  --task_id=<id> \
  --status="<current_status>" \
  --summary="<brief summary>" \
  --details="<detailed information>"

# Example
mcp__claudetask__append_stage_result \
  --task_id=42 \
  --status="Analysis" \
  --summary="Analysis complete" \
  --details="Requirements and architecture documented"
```

### Testing URLs (CRITICAL for Testing Status)

```bash
# 🔴 MANDATORY when moving to Testing status
mcp__claudetask__set_testing_urls \
  --task_id=<id> \
  --urls='{"frontend": "http://localhost:PORT", "backend": "http://localhost:PORT"}'

# Example
mcp__claudetask__set_testing_urls \
  --task_id=42 \
  --urls='{"frontend": "http://localhost:3001", "backend": "http://localhost:3333"}'
```

### Resource Cleanup (Task Completion)

```bash
# Clean up all resources when task is done
mcp:stop_session <task_id>

# Example
mcp:stop_session 42
```

### Analysis Commands

```bash
# Analyze task (for agent context, not your analysis)
mcp:analyze_task <task_id>

# Update task analysis (save agent's results)
mcp:update_task_analysis <task_id> "<analysis_text>"
```

### Worktree Management

```bash
# Create isolated git worktree for task
mcp:create_worktree <task_id>

# Complete task and merge (includes cleanup)
mcp:complete_task <task_id>
```

### Agent Delegation

```bash
# Delegate to specialized agent
mcp:delegate_to_agent <task_id> <agent_type> "<instructions>"

# Example
mcp:delegate_to_agent 42 "frontend-developer" "Create login button component"
```

### RAG Tools (Semantic Search)

```bash
# Search codebase semantically
mcp__claudetask__search_codebase \
  --query="<description>" \
  --top_k=20 \
  --language="<language>"

# Example
mcp__claudetask__search_codebase \
  --query="user authentication login form" \
  --top_k=20 \
  --language="typescript"

# Find similar past tasks
mcp__claudetask__find_similar_tasks \
  --task_description="<description>" \
  --top_k=10

# Example
mcp__claudetask__find_similar_tasks \
  --task_description="Add user profile settings page" \
  --top_k=10
```

### Project Management

```bash
# Get active project
mcp:get_active_project

# Get project settings
mcp:get_project_settings <project_id>

# Update project settings
mcp:update_project_settings <project_id> <settings_json>
```

### Session Management

```bash
# Start Claude session for task
mcp:start_claude_session <task_id> "<context>"

# Get session status
mcp:get_session_status <task_id>

# Stop session (includes cleanup)
mcp:stop_session <task_id>
```

## Command Usage Patterns

### Continuous Monitoring Loop

```bash
# Run in continuous loop
while true:
  1. mcp:get_task_queue
  2. Check each task status
  3. Delegate or update as needed
  4. Save stage results
  5. Continue monitoring
```

### Task Status Update Pattern

```bash
# Always combine status update with stage result
1. mcp__claudetask__append_stage_result --task_id={id} --status="..." --summary="..." --details="..."
2. mcp:update_status {id} "New Status"
```

### Testing Setup Pattern

```bash
# When moving to Testing status
1. Find free ports (lsof -i :PORT)
2. Start test servers
3. 🔴 MANDATORY: mcp__claudetask__set_testing_urls --task_id={id} --urls='{...}'
4. mcp__claudetask__append_stage_result --task_id={id} --status="Testing" ...
5. Notify user
```

### Task Completion Pattern

```bash
# When user requests completion
1. mcp:stop_session {task_id}
2. mcp__claudetask__append_stage_result --task_id={id} --status="Done" ...
3. mcp:update_status {id} "Done"
4. Notify user
```

## Quick Reference by Status

### Backlog → Analysis
```bash
mcp:update_status {id} "Analysis"
# Then delegate to business-analyst and systems-analyst
```

### Analysis → In Progress
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Analysis" --summary="Analysis complete" --details="..."
mcp:update_status {id} "In Progress"
```

### In Progress → Testing
```bash
# Auto-detect implementation completion
mcp__claudetask__append_stage_result --task_id={id} --status="In Progress" --summary="Implementation complete" --details="..."
mcp:update_status {id} "Testing"
# Then setup test environment
```

### Testing → Code Review
```bash
# User updates manually after testing
# You don't auto-transition from Testing
```

### Code Review → Pull Request
```bash
mcp__claudetask__append_stage_result --task_id={id} --status="Code Review" --summary="Review complete" --details="..."
mcp:update_status {id} "Pull Request"
# Then create PR
```

### Pull Request → Done
```bash
# Only when user explicitly requests
mcp:stop_session {id}
mcp__claudetask__append_stage_result --task_id={id} --status="Done" --summary="Task completed" --details="..."
mcp:update_status {id} "Done"
```

## Commands to NEVER Use Directly

**FORBIDDEN - Always delegate instead:**

```bash
# ❌ DO NOT use directly for development:
Read/Write/Edit tools     # → Delegate to developer agents
Bash for development      # → Delegate to devops agents
Analysis activities       # → Delegate to analyst agents
Documentation creation    # → Delegate to technical-writer
```

## Command Frequency Guidelines

**Use constantly (in monitoring loop):**
- `mcp:get_task_queue` - Every monitoring cycle
- `mcp:get_task <id>` - When checking task details

**Use for every status change:**
- `mcp__claudetask__append_stage_result` - Every transition
- `mcp:update_status` - After agent work completes

**Use when required by status:**
- `mcp__claudetask__set_testing_urls` - Every Testing status (mandatory!)
- `mcp:stop_session` - Every Done transition (mandatory!)

**Use for delegation:**
- Task tool with agent - For all technical work
- `mcp:delegate_to_agent` - If available for task delegation

**Use rarely (only when needed):**
- `mcp__claudetask__search_codebase` - When you need context
- `mcp__claudetask__find_similar_tasks` - When looking for patterns
- `mcp:create_worktree` - Usually automatic via backend
