# MCP Call Logging Documentation

## Overview

The ClaudeTask MCP Bridge now includes comprehensive logging for all MCP (Model Context Protocol) calls. This provides full visibility into the communication between Claude and the backend system.

## Features

### 🔵 Request Logging
- **Tool Name**: The MCP function being called
- **Arguments**: Complete JSON of all parameters passed
- **Timestamp**: Precise time of each request

### ✅ Response Logging
- **Success Status**: Confirmation when calls complete successfully
- **Result Preview**: First 500 characters of the response
- **Error Tracking**: Detailed error messages if calls fail

## Log Locations

### 1. Console Output
When the MCP server is running, logs are displayed in real-time in the console with colored indicators:
- 🔵 Blue for incoming calls
- ✅ Green for successful responses
- ❌ Red for errors

### 2. File Output
Persistent logs are saved to:
```
claudetask/backend/logs/mcp/mcp_calls.log
```

## Log Format

```
2025-11-24 20:30:15,123 - __main__ - INFO - ============================================================
2025-11-24 20:30:15,124 - __main__ - INFO - 🔵 MCP CALL RECEIVED: get_project_settings
2025-11-24 20:30:15,125 - __main__ - INFO - 📥 Arguments: {}
2025-11-24 20:30:15,126 - __main__ - INFO - ============================================================
2025-11-24 20:30:15,200 - __main__ - INFO - ============================================================
2025-11-24 20:30:15,201 - __main__ - INFO - ✅ MCP CALL SUCCESS: get_project_settings
2025-11-24 20:30:15,202 - __main__ - INFO - 📤 Result preview: {"project_mode": "development", "worktree_enabled": true}
2025-11-24 20:30:15,203 - __main__ - INFO - ============================================================
```

## Logged MCP Functions

All MCP functions are logged, including:

### Task Management
- `get_next_task` - Get highest priority task
- `get_task` - Get specific task details
- `analyze_task` - Analyze task requirements
- `update_status` - Update task status
- `complete_task` - Mark task as complete
- `append_stage_result` - Save stage results

### Project Management
- `get_project_settings` - Get project configuration
- `create_worktree` - Create git worktree
- `verify_connection` - Check backend connection
- `get_task_queue` - Get current task queue

### Memory & RAG
- `save_conversation_message` - Save conversation to memory
- `get_project_memory_context` - Load project context
- `update_project_summary` - Update project summary
- `search_project_memories` - Search through memories
- `search_codebase` - Semantic search in code
- `find_similar_tasks` - Find similar past tasks

### Agent Management
- `delegate_to_agent` - Delegate work to specialist agents
- `recommend_agent` - Get agent recommendations
- `list_agents` - List available agents

### Session Management
- `start_claude_session` - Start Claude session
- `get_session_status` - Check session status
- `stop_session` - Stop active session
- `set_testing_urls` - Save testing URLs

### Indexing
- `index_codebase` - Index entire codebase
- `index_files` - Index specific files
- `reindex_codebase` - Re-index codebase

## Benefits

1. **Debugging**: Quickly identify issues in MCP communication
2. **Auditing**: Complete audit trail of all MCP operations
3. **Performance**: Monitor response times and identify bottlenecks
4. **Development**: Understand MCP flow for new feature development
5. **Troubleshooting**: Detailed error messages for failed calls

## Usage Examples

### View Real-Time Logs
When MCP server is running, logs appear in console automatically.

### View Historical Logs
```bash
# View last 50 lines
tail -n 50 claudetask/backend/logs/mcp/mcp_calls.log

# Follow logs in real-time
tail -f claudetask/backend/logs/mcp/mcp_calls.log

# Search for specific function
grep "save_conversation_message" claudetask/backend/logs/mcp/mcp_calls.log

# View errors only
grep "ERROR" claudetask/backend/logs/mcp/mcp_calls.log
```

### Analyze Call Patterns
```bash
# Count calls by function
grep "MCP CALL RECEIVED" mcp_calls.log | cut -d: -f4 | sort | uniq -c

# Find slow calls (you'd need to analyze timestamps)
grep -A1 "MCP CALL RECEIVED" mcp_calls.log
```

## Implementation Details

The logging is implemented in `claudetask/mcp_server/claudetask_mcp_bridge.py`:

1. **Initialization**: Logging is configured when MCP server starts
2. **Request Interception**: All incoming calls are logged before processing
3. **Response Tracking**: All responses are logged after processing
4. **Error Handling**: Exceptions are caught and logged with full details

## Privacy & Security

⚠️ **Warning**: Logs may contain sensitive information including:
- Task descriptions and analyses
- Code snippets from semantic search
- Conversation content
- Project configuration

Ensure logs are:
- Not committed to version control (already in .gitignore)
- Properly secured in production environments
- Regularly rotated to prevent disk space issues

## Troubleshooting

### Logs Not Appearing
1. Check if MCP server is running
2. Verify log directory exists: `claudetask/backend/logs/mcp/`
3. Check file permissions

### Log File Too Large
Consider implementing log rotation:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'mcp_calls.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Future Enhancements

Potential improvements for MCP logging:
- [ ] Log rotation to manage file size
- [ ] Structured JSON logging for better parsing
- [ ] Performance metrics (call duration)
- [ ] Request/Response correlation IDs
- [ ] Dashboard for log visualization
- [ ] Alert system for errors
- [ ] Privacy filters for sensitive data