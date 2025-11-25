# Claude Sessions API

API endpoints for managing Claude Code sessions, including launching embedded sessions, monitoring active sessions, and executing slash commands programmatically.

## Base Path

`/api/claude-sessions`

## Endpoints

### 1. Get All Projects

**GET** `/api/claude-sessions/projects`

Returns all Claude Code projects discovered in the system.

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "name": "Project Name",
      "path": "/path/to/project",
      "session_count": 5
    }
  ],
  "total": 1
}
```

### 2. Get Project Sessions

**GET** `/api/claude-sessions/projects/{project_name}/sessions`

Get all Claude Code sessions for a specific project.

**Query Parameters:**
- `project_dir` (optional, recommended): Project directory path

**Response:**
```json
{
  "success": true,
  "project": "Project Name",
  "sessions": [
    {
      "session_id": "abc123",
      "first_timestamp": "2025-11-16T10:30:00",
      "last_timestamp": "2025-11-16T11:45:00",
      "message_count": 42,
      "tool_uses": ["Read", "Write", "Bash"]
    }
  ],
  "total": 1
}
```

### 3. Get Session Details

**GET** `/api/claude-sessions/sessions/{session_id}`

Get detailed information about a specific session.

**Query Parameters:**
- `project_dir` (required): Project directory path
- `include_messages` (optional, default: false): Include full message history

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "abc123",
    "first_timestamp": "2025-11-16T10:30:00",
    "last_timestamp": "2025-11-16T11:45:00",
    "message_count": 42,
    "tool_uses": ["Read", "Write", "Bash"],
    "messages": [
      {
        "type": "user",
        "timestamp": "2025-11-16T10:30:00",
        "content": "User message here",
        "role": "user"
      }
    ]
  }
}
```

### 4. Search Sessions

**GET** `/api/claude-sessions/sessions/search`

Search sessions by content, file paths, or commands.

**Query Parameters:**
- `query` (required): Search query string
- `project_name` (optional): Filter by project name

**Response:**
```json
{
  "success": true,
  "query": "search term",
  "results": [
    {
      "session_id": "abc123",
      "project": "Project Name",
      "matches": 3,
      "snippets": ["... matched text ..."]
    }
  ],
  "total": 1
}
```

### 5. Get Statistics

**GET** `/api/claude-sessions/statistics`

Get aggregate statistics across Claude Code sessions.

**Query Parameters:**
- `project_name` (optional): Filter by project name

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_sessions": 42,
    "total_messages": 1234,
    "most_used_tools": {
      "Read": 450,
      "Write": 320,
      "Bash": 280
    },
    "average_session_length": 28.5
  }
}
```

### 6. Get Active Sessions

**GET** `/api/claude-sessions/active-sessions`

Get currently running Claude Code sessions - **only project-related processes**.

**Filtering Logic** (Enhanced 2025-11-26):
- Includes: Claude processes with `--cwd` or `--working-dir` pointing to user project directories
- Excludes: System subprocesses, node internals, helper processes, Electron/Chrome renderer processes
- Excludes: System paths (`/var/folders/`, `/Applications/`, `/System/`, `/Library/`, `/tmp/`, `/private/`)
- Removes duplicates by PID

**Response:**
```json
{
  "success": true,
  "active_sessions": [
    {
      "pid": "12345",
      "cpu": "5.2",
      "mem": "2.1",
      "started": "10:30",
      "working_dir": "/path/to/project",
      "project_name": "project",
      "command": "claude code --cwd /path/to/project"
    }
  ],
  "count": 1
}
```

**New Fields (2025-11-26)**:
- `project_name`: Extracted from working directory path (e.g., "project" from "/path/to/project")
- Enhanced filtering ensures only meaningful project sessions are shown

### 7. Kill Session

**POST** `/api/claude-sessions/sessions/{pid}/kill`

Terminate an active Claude Code session gracefully.

**Path Parameters:**
- `pid`: Process ID of the session to kill

**Response:**
```json
{
  "success": true,
  "message": "Session 12345 terminated gracefully"
}
```

**Error Responses:**
- `404`: Process not found
- `403`: Permission denied

### 8. Execute Command (Hook Integration)

**POST** `/api/claude-sessions/execute-command`

Execute a Claude Code slash command programmatically by launching an embedded Claude session. This endpoint is designed for integration with git hooks and automation scripts.

**Query Parameters:**
- `command` (required): Slash command to execute (must start with `/`)
- `project_dir` (optional): Project directory path (defaults to current directory)

**Example:**
```bash
curl -X POST "http://localhost:3333/api/claude-sessions/execute-command?command=/update-documentation&project_dir=/path/to/project"
```

**URL Encoding for Paths with Spaces:**

When using this endpoint from shell scripts (like git hooks), you must URL-encode the `project_dir` parameter if it contains spaces:

```bash
# Using jq for URL encoding
PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_DIR" | jq -sRr @uri)
curl -X POST "http://localhost:3333/api/claude-sessions/execute-command?command=/update-documentation&project_dir=${PROJECT_DIR_ENCODED}"
```

**Example with spaces:**
```bash
# Original path: /Users/name/Start Up/Project
# URL-encoded: /Users/name/Start%20Up/Project

curl -X POST "http://localhost:3333/api/claude-sessions/execute-command?command=/update-documentation&project_dir=/Users/name/Start%20Up/Project"
```

**How It Works:**

1. **Session Detection**: Checks if a Claude session already exists for the project
2. **Session Creation**: If no active session, creates a new embedded session using `pexpect`
   - Creates session with `task_id=0` to indicate hook-triggered session
   - Hook sessions skip `/start-feature` command (no task initialization)
3. **Command Execution**: Sends the slash command to Claude's stdin
4. **Response**: Returns session info immediately (command executes asynchronously)

**Response:**
```json
{
  "success": true,
  "message": "Command /update-documentation sent to Claude Code session",
  "command": "/update-documentation",
  "session_id": "hook-abc12345",
  "pid": 12345,
  "note": "Command is being executed in embedded Claude session"
}
```

**Use Cases:**

1. **Git Hooks**: Trigger documentation updates after merging to main
2. **CI/CD Integration**: Execute Claude commands from automation pipelines
3. **External Tools**: Allow external scripts to invoke Claude functionality

**Implementation Details:**

- Uses `pexpect` to spawn Claude process with `--mode embedded`
- Session remains active for command execution
- Supports both new session creation and reusing existing sessions
- Includes initialization delay (2 seconds) for new sessions
- Hook sessions (task_id=0) skip task initialization to prevent `/start-feature` from running
- Sends Enter key after command to execute it
- Session working directory set to `project_dir` parameter

**Security Considerations:**

- Only accepts slash commands (starting with `/`)
- Validates project directory existence
- Logs all command executions
- Requires backend API to be running on localhost

**Error Responses:**

```json
{
  "success": false,
  "detail": "Command must start with '/'"
}
```

```json
{
  "success": false,
  "detail": "Project directory not found"
}
```

```json
{
  "success": false,
  "detail": "Failed to create Claude session: <error message>"
}
```

## Common Use Cases

### Launching Documentation Updates from Git Hooks

The execute-command endpoint is primarily used by the post-merge documentation hook to automatically trigger documentation updates:

```bash
#!/bin/bash
# .claude/hooks/post-push-docs.sh

PROJECT_ROOT="$(pwd)"
API_URL="http://localhost:3333/api/claude-sessions/execute-command"
COMMAND="/update-documentation"

# URL encode project directory (handles spaces)
PROJECT_DIR_ENCODED=$(printf %s "$PROJECT_ROOT" | jq -sRr @uri)

# Execute command via API
curl -s -X POST "$API_URL?command=${COMMAND}&project_dir=${PROJECT_DIR_ENCODED}"
```

### Monitoring Active Development

Use active-sessions endpoint to see all running Claude instances:

```bash
curl http://localhost:3333/api/claude-sessions/active-sessions
```

### Session History Analysis

Get session details with message history for debugging:

```bash
curl "http://localhost:3333/api/claude-sessions/sessions/abc123?project_dir=/path/to/project&include_messages=true"
```

## Integration with ClaudeTask

These endpoints integrate with the ClaudeTask database to:
- Track session metadata in the `claude_sessions` table
- Link sessions to specific tasks via `task_id`
- Store session status and working directory
- Maintain session history for analytics

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "detail": "Error description"
}
```

HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `403`: Permission denied
- `404`: Resource not found
- `500`: Internal server error

## Logging

All API operations are logged with structured logging:

```python
logger.info(f"Executing Claude command: {command} in {project_dir}")
logger.error(f"Failed to parse session {session_file.name}: {e}")
```

Log files can be found in `.claude/logs/` directory.
