# Session Continuation Feature

## Overview

The Session Continuation feature allows users to resume Claude Code sessions with full conversation context, enabling seamless workflows across multiple work sessions.

**Version**: 1.0
**Added**: 2025-11-26
**Related Tasks**: task-14, task-15

## Purpose

When working on complex development tasks, you may need to:
- Take breaks without losing context
- Continue work across different days
- Resume after interruptions or crashes
- Review and continue previous conversations

The Session Continuation feature ensures no context is lost between sessions.

## How It Works

### 1. Session Storage

All Claude Code sessions are automatically saved to JSONL files:

**File Location**: `~/.claude/projects/{project-name}/{session-id}.jsonl`

**Content Stored**:
- User messages
- Assistant responses
- Tool calls and results
- Session metadata (git branch, working directory, timestamps)
- Errors and warnings

### 2. Active Session Detection

The system detects active Claude Code sessions using process monitoring:

**Detection Method**:
```python
# Use `lsof` to get process working directory
def get_process_cwd(pid: str) -> str:
    result = subprocess.run(["lsof", "-p", pid], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if '\tcwd\t' in line:
            return extract_path_from_lsof_line(line)
```

**Filtering**:
- Excludes system paths (`/var/folders/`, `/Applications/`, etc.)
- Excludes subprocess helpers (Electron renderers, MCP servers)
- Only shows project-related Claude processes

### 3. Message Retrieval

When continuing a session, the last N messages are loaded:

**API Endpoint**: `GET /api/projects/{project_id}/sessions/{session_id}/messages?limit=100`

**Security Features**:
- Path validation (must be within `~/.claude` directory)
- Session ID format validation (UUID or agent-ID format)
- Path traversal prevention
- Empty message filtering

**Message Filtering**:
```python
# Skip empty messages before sending to frontend
if not content or content.strip() in ["", "...", "…"]:
    continue
```

### 4. Context Loading

Claude loads the conversation context:

1. Fetches last 100 messages from session file
2. Parses JSONL format with error handling
3. Filters out empty/placeholder messages
4. Presents context to Claude for continuation

## User Experience

### Viewing Active Sessions

1. Navigate to `/sessions` page
2. Expand "System Processes" accordion
3. See all active Claude Code sessions with:
   - Process ID (PID)
   - CPU and memory usage
   - Project name and directory
   - Session ID (if available)

### Viewing Session Details

1. Find an active session in the process monitor
2. Click "View Details" button
3. See comprehensive session information:
   - Session metadata (ID, timestamps, file size)
   - Git branch and working directory
   - Claude version used
   - Message count breakdown
   - **Full conversation history** (chronological)
   - Tool usage statistics
   - Files modified
   - Errors encountered

### Message Display

**Message List Features**:
- Chronological order (oldest to newest)
- User messages (👤 icon)
- Assistant messages (🤖 icon)
- Formatted timestamps
- Full message content (no truncation)
- Smart content parsing (handles Claude API format)
- Empty message filtering

**Example Message**:
```
👤 User  |  2025-11-26 10:30:15
Create a new React component for the dashboard

🤖 Assistant  |  2025-11-26 10:30:18
I'll create a new React component for the dashboard. Let me start by creating the component file...
```

### Continuing a Session (Future)

**Planned Workflow**:
1. View session details
2. Click "Continue Session" button
3. Claude Code opens with full conversation context
4. Continue working exactly where you left off

**Current Status**: Message viewing implemented, UI continuation button planned for future release.

## API Integration

### Session Messages Endpoint

**Endpoint**: `GET /api/projects/{project_id}/sessions/{session_id}/messages`

**Query Parameters**:
- `limit` (default: 100): Maximum messages to retrieve

**Response**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Create a new component",
      "timestamp": "2025-11-26T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I'll create the component...",
      "timestamp": "2025-11-26T10:30:05Z"
    }
  ]
}
```

### Session Details Endpoint

**Endpoint**: `GET /api/claude-sessions/sessions/{session_id}`

**Query Parameters**:
- `project_dir` (required): Project directory path
- `include_messages` (default: false): Include full message history

**Response**:
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def",
    "file_path": "/Users/.../.claude/projects/MyProject/abc-123-def.jsonl",
    "file_size": 45678,
    "created_at": "2025-11-26T10:00:00Z",
    "last_timestamp": "2025-11-26T11:00:00Z",
    "cwd": "/Users/username/Projects/MyProject",
    "git_branch": "feature/new-feature",
    "claude_version": "1.5.0",
    "message_count": 42,
    "user_messages": 21,
    "assistant_messages": 21,
    "tool_calls": {
      "Read": 15,
      "Write": 8,
      "Bash": 5
    },
    "commands_used": ["npm install", "git status"],
    "files_modified": ["src/App.tsx", "package.json"],
    "errors": [],
    "messages": [/* full message history */]
  }
}
```

### Active Sessions Endpoint

**Endpoint**: `GET /api/claude-sessions/active-sessions`

**Enhanced Response (v2.1)**:
```json
{
  "success": true,
  "active_sessions": [
    {
      "pid": "12345",
      "cpu": "2.5",
      "mem": "1.8",
      "command": "claude code --cwd /path/to/project",
      "working_dir": "/Users/username/Projects/MyProject",
      "project_name": "MyProject",
      "session_id": "abc-123-def",
      "project_dir": "/Users/username/.claude/projects/MyProject"
    }
  ],
  "count": 1
}
```

## Security

### Path Validation

All file paths validated to prevent path traversal:

```python
def parse_jsonl_messages(jsonl_path: Path, _skip_validation: bool = False):
    if not _skip_validation:
        resolved = jsonl_path.resolve()
        claude_base = (Path.home() / ".claude").resolve()
        if not str(resolved).startswith(str(claude_base)):
            raise ValueError("Invalid file path - security check failed")
```

### Session ID Validation

Session IDs must match expected format:

```python
# UUID format or agent format
SESSION_ID_PATTERN = re.compile(
    r'^([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}|agent-[a-f0-9]{8})$'
)

if not SESSION_ID_PATTERN.match(session_id):
    raise HTTPException(status_code=400, detail="Invalid session ID format")
```

### Empty Message Filtering

Prevents displaying placeholder or empty messages:

**Server-side filtering** (main.py):
```python
if not content or (isinstance(content, str) and not content.strip()):
    continue
```

**Client-side filtering** (Sessions.tsx):
```typescript
.filter(msg => {
  const content: any = msg.content;
  if (typeof content === 'string') {
    const trimmed = content.trim();
    return trimmed && trimmed !== '...' && trimmed !== '…';
  }
  return !!content;
})
```

## Performance

### Efficient Message Retrieval

Uses `collections.deque` with `maxlen` for last-N messages:

```python
from collections import deque

messages = deque(maxlen=limit)  # Auto-discards oldest messages
for line in jsonl_file:
    entry = json.loads(line)
    messages.append(parse_message(entry))

return list(messages)  # Returns last N messages efficiently
```

### Lazy Loading

- Session details loaded only when "View Details" clicked
- Messages included only when `include_messages=true`
- Large session files read incrementally (line-by-line)

### Pagination Support

- ClaudeCodeSessionsView: 20 sessions per page
- Active sessions: All shown (typically small number)
- Messages: Configurable limit (default: 100)

## Use Cases

### 1. Daily Development Workflow

**Scenario**: Working on a feature across multiple days

**Steps**:
1. Day 1: Work on feature, create components
2. End of day: Close Claude Code
3. Day 2: View sessions, see yesterday's work
4. Click "View Details" to review what was done
5. Continue where you left off (future: with one click)

### 2. Debugging Session Issues

**Scenario**: Session crashed or encountered errors

**Steps**:
1. Navigate to Sessions page
2. Find the problematic session
3. View session details
4. Review message history to identify error
5. Check error log for stack traces
6. Analyze tool calls leading to crash

### 3. Team Collaboration

**Scenario**: Understanding what was done in a session

**Steps**:
1. Teammate shares session ID
2. Locate session in ClaudeCodeSessionsView
3. View session details
4. Review full conversation
5. Understand context and decisions made

### 4. Recovering from Interruptions

**Scenario**: Claude session interrupted (power loss, OS crash)

**Steps**:
1. Restart system
2. View Sessions page
3. Find last active session
4. Review message history
5. Continue work with full context

## Integration Points

### Frontend Components

**Sessions.tsx**:
- Manages session details dialog
- Fetches session messages on demand
- Displays message history with filtering

**ClaudeCodeSessionsView.tsx**:
- Lists all sessions for a project
- Provides session search and filtering
- Shows session statistics

### Backend Endpoints

**claude_sessions.py**:
- `/sessions/{session_id}` - Session details
- `/active-sessions` - Process monitoring
- Session ID validation
- Empty message filtering

**main.py**:
- `/projects/{project_id}/sessions/{session_id}/messages` - Message retrieval
- JSONL parsing with security validation
- Path traversal prevention

### Data Sources

**JSONL Files**:
- Primary source: `~/.claude/projects/{project-name}/{session-id}.jsonl`
- Fallback: Database messages (if JSONL not found)

**Database**:
- `claude_sessions` table for metadata
- Fallback storage for messages

## Future Enhancements

### Planned Features

1. **One-Click Resume**:
   - Button in session details dialog
   - Opens Claude Code with full context
   - Auto-loads conversation history

2. **Session Branching**:
   - Continue from specific message
   - Create alternate conversation paths
   - Explore different solutions

3. **Session Sharing**:
   - Export session to shareable format
   - Import sessions from teammates
   - Collaborative debugging

4. **Smart Recommendations**:
   - Suggest related sessions
   - Identify similar work patterns
   - Auto-detect continuation opportunities

5. **Advanced Filtering**:
   - Filter messages by type (user/assistant/tool)
   - Search within conversation
   - Highlight important messages

## Troubleshooting

### Session Not Found

**Problem**: "Session not found" error when viewing details

**Solutions**:
1. Verify session ID format (must be UUID)
2. Check project directory path is correct
3. Ensure JSONL file exists: `~/.claude/projects/{project}/{session-id}.jsonl`
4. Verify file permissions

### Empty Message History

**Problem**: Session details show 0 messages

**Causes**:
1. All messages are empty placeholders (filtered out)
2. JSONL file corrupted
3. Session just started (no messages yet)

**Solutions**:
1. Check JSONL file manually: `cat ~/.claude/projects/{project}/{session-id}.jsonl`
2. Verify messages have content (not just "...")
3. Check for JSON parsing errors in logs

### Active Session Not Detected

**Problem**: Running Claude session not shown in process monitor

**Causes**:
1. Process running in system directory (filtered out)
2. Subprocess/helper process (not main Claude CLI)
3. `lsof` unable to determine working directory

**Solutions**:
1. Ensure Claude launched with `--cwd` or in project directory
2. Check process with: `ps aux | grep claude`
3. Verify working directory: `lsof -p {pid} | grep cwd`

### Path Validation Error

**Problem**: "Invalid file path - security check failed"

**Cause**: Attempting to access file outside `~/.claude` directory

**Solution**: Session files must be in `.claude` directory. Check project structure.

## Related Documentation

- [Claude Sessions API](../api/endpoints/claude-sessions.md) - API reference
- [Sessions Component](../components/Sessions.md) - UI documentation
- [ClaudeCodeSessions Component](../components/ClaudeCodeSessions.md) - Session analytics
- [Memory System](./memory-system.md) - Long-term context persistence

## Summary

The Session Continuation feature provides:

- **Zero Context Loss**: All conversations automatically saved
- **Full History Access**: View complete message history for any session
- **Active Monitoring**: Real-time tracking of running Claude sessions
- **Security**: Path validation and session ID verification
- **Performance**: Efficient message retrieval with filtering
- **User-Friendly**: Intuitive UI for session exploration

This feature ensures developers can work seamlessly across multiple sessions, review past work, and maintain full context throughout complex development workflows.

---

**Version**: 1.0
**Last Updated**: 2025-11-26
**Status**: Active (Message viewing implemented, UI continuation planned)
