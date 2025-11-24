# Project Memory System Instructions

## 🧠 Overview

The ClaudeTask Framework includes an intelligent memory system that preserves context and knowledge across sessions. This system is **enabled by default** and works automatically.

## 🎯 Purpose

The memory system solves these critical problems:
- **Context Loss**: No more explaining the project from scratch each session
- **Knowledge Fragmentation**: Insights from different tasks are connected
- **Repeated Work**: Solutions are remembered and reused
- **Learning Curve**: New sessions start with full project understanding

## 📚 Memory Components

### 1. **Project Summary** (3-5 pages)
- Comprehensive overview of architecture, decisions, patterns
- Automatically updated after each session
- Limited to ~15,000 characters for optimal performance
- Includes key technologies, gotchas, and solutions

### 2. **Conversation History** (Last 50 messages)
- Raw, unfiltered recent messages
- Provides immediate context of recent work
- Sliding window - always the most recent 50

### 3. **RAG-Indexed Memories** (Semantic search)
- All historical messages indexed for search
- ChromaDB vector database with embeddings
- Intelligent retrieval based on current task
- Separate collections per project

### 4. **Session Summaries**
- End-of-session insights captured
- Important decisions highlighted
- Patterns and solutions extracted
- Merged into project summary

## 🔄 Automatic Workflow

### Session Start
1. **Hook Triggered**: `OnSessionStart` event fires
2. **Context Loaded**: `get_project_memory_context` called automatically
3. **Memory Retrieved**:
   - Project summary loaded
   - Last 50 messages fetched
   - RAG search for relevant context
4. **Context Applied**: Full history available to Claude

### During Session
1. **Message Capture**: Every user/assistant message saved
2. **Real-time Indexing**: Messages added to RAG index
3. **Important Events**: Critical decisions trigger summary updates

### Session End
1. **Summary Generation**: Session insights extracted
2. **Project Update**: Summary merged with existing knowledge
3. **Cleanup**: Temporary data cleared

## 🛠️ Memory Tools

### Automatic (via Hooks)
These work without any manual intervention:
- `Memory Conversation Capture` - Saves all messages
- `Memory Session Summarizer` - Updates project summary

### Manual (MCP Commands)
Use these for specific memory operations:

```bash
# Load full context manually
mcp__claudetask__get_project_memory_context

# Save specific insight
mcp__claudetask__save_conversation_message \
  --message_type="assistant" \
  --content="Important finding..."

# Update summary with key decision
mcp__claudetask__update_project_summary \
  --trigger="important_decision" \
  --new_insights="Architectural change..."

# Search historical knowledge
mcp__claudetask__search_project_memories \
  --query="authentication implementation"
```

## 💾 Storage Architecture

### Database Tables
- `conversation_memory` - All messages with metadata
- `project_summaries` - Condensed project knowledge
- `memory_rag_status` - Indexing tracking
- `memory_sessions` - Session management

### RAG Collections
- `memory_{project_id}` - Project-specific ChromaDB collection
- Embeddings via `all-MiniLM-L6-v2` model
- Hybrid search with metadata filtering

## ⚙️ Configuration

### Default Hooks Status
```json
{
  "memory-conversation-capture": {
    "enabled": true,
    "favorite": true
  },
  "memory-session-summarizer": {
    "enabled": true,
    "favorite": false
  }
}
```

### Memory Limits
- Project Summary: 15,000 characters (~5 pages)
- Recent Messages: 50 messages
- RAG Search Results: 20 by default
- Session Summary: Unlimited (merged into project)

## 🎯 Best Practices

### DO:
- ✅ Let the automatic system work - don't override unless necessary
- ✅ Mark important decisions with `update_project_summary`
- ✅ Trust the loaded context - it's comprehensive
- ✅ Use search for specific historical queries

### DON'T:
- ❌ Manually save every message (hooks do this)
- ❌ Reload context repeatedly (it's cached)
- ❌ Ignore the loaded context - it contains valuable history
- ❌ Disable memory hooks without good reason

## 🔍 Troubleshooting

### Context Not Loading
1. Check if hooks are enabled:
   ```sql
   SELECT * FROM project_hooks WHERE project_id = 'your-project-id';
   ```

2. Verify MCP server is running:
   ```bash
   ps aux | grep claudetask_mcp
   ```

3. Check database for messages:
   ```sql
   SELECT COUNT(*) FROM conversation_memory WHERE project_id = 'your-project-id';
   ```

### Memory Too Large
- Summary automatically truncates at 15,000 chars
- Old messages archived after 30 days
- RAG index rebuilds periodically

### Search Not Working
1. Check RAG service status
2. Verify ChromaDB collections exist
3. Rebuild index if necessary:
   ```bash
   mcp__claudetask__reindex_codebase --full_reindex=true
   ```

## 📈 Memory Statistics

Monitor memory health with:
```bash
curl http://localhost:3333/api/projects/{project_id}/memory/stats
```

Returns:
- Total messages stored
- Summary version number
- Last update timestamp
- Index status

## 🚀 Advanced Features

### Custom Summarization
Future enhancement: Integrate Claude API for intelligent summarization instead of simple concatenation.

### Cross-Project Memory
Future enhancement: Share patterns and solutions across related projects.

### Memory Export/Import
Future enhancement: Backup and restore project memory.

## 📝 Summary

The memory system is your project's brain:
- **Automatic**: Works without intervention via hooks
- **Comprehensive**: Captures everything important
- **Intelligent**: RAG search finds relevant context
- **Persistent**: Survives across sessions
- **Growing**: Gets smarter with each session

Trust the system - it remembers so you don't have to explain twice!