# Claude Code Sessions API

## Overview

API для чтения и анализа локальных сессий Claude Code из `~/.claude/projects/`. Реализовано по подходу **Claudia GUI** - чтение JSONL файлов напрямую без использования официального API.

## Features

✅ **Чтение всех проектов** - Список всех Claude Code проектов
✅ **Парсинг сессий** - Детальная информация о каждой сессии
✅ **Поиск по содержимому** - Поиск по сессиям по ключевым словам
✅ **Статистика использования** - Агрегированная статистика по инструментам и активности
✅ **История сообщений** - Полная история взаимодействий

## Architecture

```
~/.claude/projects/
  └─ PROJECT_NAME/
     ├─ session-uuid-1.jsonl    # JSONL формат
     ├─ session-uuid-2.jsonl
     └─ session-uuid-3.jsonl
```

Каждая строка JSONL файла содержит:
- `type`: Тип записи (user, assistant, tool_use, tool_result, system)
- `timestamp`: Временная метка
- `content`: Содержимое сообщения/результата
- `cwd`: Рабочая директория
- `gitBranch`: Git ветка
- `version`: Версия Claude Code

## API Endpoints

### 1. Get All Projects

```http
GET /api/claude-sessions/projects
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "name": "Framework",
      "path": "/Users/.../Claude/Code/Feature/Framework",
      "directory": "/Users/.../.claude/projects/-Users-...",
      "sessions_count": 59,
      "last_modified": "2025-11-12T23:51:25"
    }
  ],
  "total": 8
}
```

### 2. Get Project Sessions

```http
GET /api/claude-sessions/projects/{project_name}/sessions
```

**Response:**
```json
{
  "success": true,
  "project": "Framework",
  "sessions": [
    {
      "session_id": "cb6e8208-7d2f-4b64-b8f3-9c2e8f0a1b3c",
      "file_path": "/Users/.../.claude/projects/.../session.jsonl",
      "file_size": 430403,
      "created_at": "2025-11-12T14:22:49.925Z",
      "last_timestamp": "2025-11-12T15:30:12.123Z",
      "cwd": "/Users/.../project",
      "git_branch": "main",
      "claude_version": "2.0.36",
      "message_count": 55,
      "user_messages": 23,
      "assistant_messages": 32,
      "tool_calls": {
        "Read": 15,
        "Write": 8,
        "Edit": 12,
        "Bash": 5
      },
      "commands_used": ["/help", "/agents"],
      "files_modified": ["src/main.py", "README.md"],
      "errors": []
    }
  ],
  "total": 59
}
```

### 3. Get Session Details

```http
GET /api/claude-sessions/sessions/{session_id}
  ?project_name=Framework
  &include_messages=true
```

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "cb6e8208-...",
    "cwd": "/Users/.../project",
    "git_branch": "main",
    "claude_version": "2.0.36",
    "message_count": 55,
    "tool_calls": {...},
    "messages": [
      {
        "type": "user",
        "timestamp": "2025-11-12T14:22:49.925Z",
        "content": "Add a new feature...",
        "uuid": "msg-uuid-1",
        "parent_uuid": null
      },
      {
        "type": "assistant",
        "timestamp": "2025-11-12T14:23:10.123Z",
        "content": "I'll help you add that feature...",
        "uuid": "msg-uuid-2",
        "parent_uuid": "msg-uuid-1"
      }
    ]
  }
}
```

### 4. Search Sessions

```http
GET /api/claude-sessions/sessions/search
  ?query=error
  &project_name=Framework
```

**Response:**
```json
{
  "success": true,
  "query": "error",
  "results": [
    {
      "session_id": "...",
      "project": "Framework",
      "message_count": 55,
      "created_at": "...",
      "tool_calls": {...}
    }
  ],
  "total": 41
}
```

### 5. Get Statistics

```http
GET /api/claude-sessions/statistics
  ?project_name=Framework
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_sessions": 59,
    "total_messages": 10605,
    "total_tool_calls": {
      "Read": 1250,
      "Write": 450,
      "Edit": 890,
      "Bash": 320,
      "Grep": 670
    },
    "total_files_modified": 523,
    "total_errors": 24,
    "recent_sessions": [...]
  }
}
```

## Python Service Usage

```python
from app.services.claude_sessions_reader import ClaudeSessionsReader

reader = ClaudeSessionsReader()

# Get all projects
projects = reader.get_all_projects()

# Get sessions for a project
sessions = reader.get_project_sessions("Framework")

# Get detailed session info with messages
session = reader.get_session_details(
    project_name="Framework",
    session_id="cb6e8208-7d2f-4b64-b8f3-9c2e8f0a1b3c",
    include_messages=True
)

# Search sessions
results = reader.search_sessions(
    query="error",
    project_name="Framework"
)

# Get statistics
stats = reader.get_session_statistics(project_name="Framework")
```

## Session Metadata

Each session includes:

### Basic Metadata
- `session_id`: Unique identifier
- `file_path`: Path to JSONL file
- `file_size`: File size in bytes
- `created_at`: First message timestamp
- `last_timestamp`: Last message timestamp
- `cwd`: Working directory
- `git_branch`: Git branch
- `claude_version`: Claude Code version

### Activity Metrics
- `message_count`: Total messages
- `user_messages`: User message count
- `assistant_messages`: Assistant message count
- `tool_calls`: Dictionary of tool usage counts
- `commands_used`: List of slash commands used
- `files_modified`: List of modified files
- `errors`: List of error events

## Tool Call Tracking

Automatically tracks all Claude Code tool usage:

**Common Tools:**
- `Read` - File reading
- `Write` - File creation
- `Edit` - File editing
- `Bash` - Shell commands
- `Grep` - Code searching
- `Glob` - File pattern matching
- `Task` - Agent delegation
- `WebFetch` - Web content fetching
- `mcp__*` - MCP tool calls

## Use Cases

### 1. Session Analytics Dashboard
```python
stats = reader.get_session_statistics()
print(f"Total Sessions: {stats['total_sessions']}")
print(f"Most Used Tool: {max(stats['total_tool_calls'], key=stats['total_tool_calls'].get)}")
```

### 2. Error Investigation
```python
error_sessions = reader.search_sessions(query="error")
for session in error_sessions:
    if session['errors']:
        print(f"Session {session['session_id']}: {len(session['errors'])} errors")
```

### 3. Tool Usage Optimization
```python
for project in reader.get_all_projects():
    stats = reader.get_session_statistics(project['name'])
    print(f"{project['name']}: {stats['total_tool_calls']}")
```

### 4. Historical Analysis
```python
sessions = reader.get_project_sessions("Framework")
sorted_sessions = sorted(sessions, key=lambda x: x['message_count'], reverse=True)
print(f"Most active session: {sorted_sessions[0]['message_count']} messages")
```

## Testing

Run the test script:

```bash
python test_claude_sessions.py
```

Output includes:
- All projects with session counts
- Recent sessions with metadata
- Detailed session information
- Tool usage statistics
- Search results

## Integration with ClaudeTask

The Claude Sessions API integrates with ClaudeTask to:

1. **Track Development Activity** - Monitor which sessions worked on which tasks
2. **Analyze Productivity** - Measure time and tool usage per task
3. **Debug Issues** - Search historical sessions for similar problems
4. **Learn Patterns** - Identify common workflows and tool usage patterns

## Security & Privacy

- ✅ **Local Only** - All data read from `~/.claude/projects/` directory
- ✅ **Read-Only** - Never modifies session files
- ✅ **No External API** - No data sent to external services
- ✅ **User Control** - Respects local file permissions

## Comparison: Claudia vs Official API

| Feature | Claudia Approach (This) | Official API |
|---------|------------------------|--------------|
| **Data Source** | Local JSONL files | Anthropic Cloud |
| **Access** | Instant, offline | Requires network |
| **Privacy** | Complete local control | Data on Anthropic servers |
| **Cost** | Free | May have rate limits |
| **Real-time** | Delayed (file-based) | Real-time |
| **History** | Full local history | Limited by retention |

## Limitations

⚠️ **Current Limitations:**
- Only reads completed sessions (JSONL files)
- Cannot track active/running sessions
- No write capabilities (read-only)
- Depends on Claude Code JSONL format (may change)

## Future Enhancements

🚀 **Planned Features:**
- Real-time session monitoring
- Session replay visualization
- Export to other formats (JSON, CSV)
- Advanced analytics (time spent, productivity metrics)
- Integration with Claude Code via MCP

## Support

For issues or questions:
- Check Claude Code docs: https://docs.claude.com/claude-code
- Review Claudia project: https://github.com/getAsterisk/claudia
- ClaudeTask issues: [GitHub Issues]

---

**Created:** 2025-11-13
**Version:** 1.0.0
**License:** MIT
