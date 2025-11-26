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

### 2. Get Project Sessions (with Pagination)

**GET** `/api/claude-sessions/projects/{project_name}/sessions`

Get all Claude Code sessions for a specific project with pagination support.

**Query Parameters:**
- `project_dir` (optional, recommended): Project directory path
- `limit` (optional, default: 50, max: 100): Number of sessions per page
- `offset` (optional, default: 0): Number of sessions to skip

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
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

**Pagination Example:**
```bash
# Get first 50 sessions
curl "http://localhost:3333/api/claude-sessions/projects/MyProject/sessions?limit=50&offset=0"

# Get next 50 sessions
curl "http://localhost:3333/api/claude-sessions/projects/MyProject/sessions?limit=50&offset=50"
```

**Security Improvements (2025-11-26)**:
- `limit` parameter capped at 100 to prevent excessive data transfer
- `offset` must be non-negative (≥ 0)
- Sessions sorted by `last_timestamp` DESC before pagination
- Invalid parameters return 422 validation error

### 3. Get Session Details (with Validation)

**GET** `/api/claude-sessions/sessions/{session_id}`

Get detailed information about a specific session.

**Path Parameters:**
- `session_id`: UUID format session identifier (validated)

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

**Session ID Validation (2025-11-26)**:
- `session_id` must be valid UUID format: `^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$`
- Invalid format returns 400 Bad Request: "Invalid session_id format"
- Example valid: `a1b2c3d4-1234-5678-90ab-cdef12345678`
- Example invalid: `invalid-id`, `abc123`

**Security Benefits**:
- Prevents path traversal attacks via crafted session IDs
- Ensures session files follow expected naming convention
- Validates input before filesystem operations

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
- `working_dir`: Current working directory of the Claude process (via `lsof`)
- `project_name`: Extracted from working directory path (e.g., "project" from "/path/to/project")
- `session_id`: Active session identifier (if available)
- `project_dir`: Path to session storage directory for the project
- Enhanced filtering ensures only meaningful project sessions are shown

**Active Session Detection (v2.1)**:

The endpoint now uses `lsof` to detect the current working directory of each Claude process:

```python
def get_process_cwd(pid: str) -> str:
    """Get the current working directory of a process using lsof"""
    result = subprocess.run(["lsof", "-p", pid], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if '\tcwd\t' in line or ' cwd ' in line:
            # Parse lsof output: NAME is the last column
            parts = line.split()
            if len(parts) >= 9:
                return ' '.join(parts[8:])
    return None
```

**System Path Filtering**:

The endpoint excludes processes running in system directories:
- `/var/folders/` - Temporary system files
- `/Applications/` - Application bundles
- `/System/` - macOS system files
- `/Library/` - System libraries
- `/tmp/`, `/private/` - Temporary directories
- `/usr/`, `/opt/` - Unix system directories

**Subprocess Exclusion**:

Filters out Electron/Chrome helper processes:
- `--type=` flags (renderer, gpu-process, utility)
- `Helper` processes
- `crashpad` crash reporter
- `mcp-server` processes
- Python multiprocessing helpers

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

### 9. Get Session Messages (JSONL Parsing)

**GET** `/api/projects/{project_id}/sessions/{session_id}/messages`

Retrieve messages from a session's JSONL file with security validation and empty message filtering.

**Path Parameters:**
- `project_id`: Project identifier (may be a file path, will be encoded)
- `session_id`: Session identifier

**Query Parameters:**
- `limit` (optional, default: 100): Maximum number of messages to return

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Message content here",
      "timestamp": "2025-11-26T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Response content here",
      "timestamp": "2025-11-26T10:31:00Z"
    }
  ]
}
```

**Security Features (2025-11-26)**:
- **Path Validation**: All JSONL file paths validated to be within `~/.claude` directory
- **Path Traversal Prevention**: Rejects attempts to access files outside `.claude` base
- **Project Path Encoding**: Slashes in project paths replaced with dashes for safe filesystem operations
- **Empty Message Filtering**: Automatically skips empty messages, "...", and "…" placeholders

**Message Filtering Logic**:
```python
# Filters applied during parsing:
1. Skip messages with empty content
2. Skip messages with only whitespace
3. Skip placeholder messages ("..." or "…")
4. For array content, verify at least one text block has content
```

**Use Cases**:
- Fetch conversation history for session continuation
- Load message context for Claude Code "Continue Session" feature
- Display session messages in UI without empty placeholders
- Maintain clean message history for analysis
- Power "View Details" dialog in Sessions page for active sessions

**Continue Session Integration**:

This endpoint enables the "Continue Session" feature, allowing users to resume Claude Code sessions with full context:

```typescript
// Frontend: Fetch messages when continuing a session
const response = await axios.get(
  `/api/projects/${projectId}/sessions/${sessionId}/messages?limit=100`
);

// Claude loads the last 100 messages as context
// User can continue exactly where they left off
// No context loss between sessions
```

**Example Request**:
```bash
# Get last 50 messages from session
curl "http://localhost:3333/api/projects/my-project/sessions/abc-123-def/messages?limit=50"
```

**Implementation Details**:
- Uses `collections.deque` with `maxlen` for efficient last-N message retrieval
- JSONL file parsed line-by-line to handle large files efficiently
- Handles both string content and Claude API structured content
- Aligns with `claude_sessions.py` empty message filtering (lines 167-175)
- Database fallback if JSONL file not found

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
- `422`: Validation error (invalid query parameters)
- `500`: Internal server error

## Logging

All API operations are logged with structured logging:

```python
logger.info(f"Executing Claude command: {command} in {project_dir}")
logger.error(f"Failed to parse session {session_file.name}: {e}")
logger.info(f"Loaded {len(messages)} messages from JSONL for session {session_id}")
logger.warning(f"Security: JSONL path {resolved} is outside .claude directory")
```

Log files can be found in `.claude/logs/` directory.
