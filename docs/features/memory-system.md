# Project Memory System

The ClaudeTask Framework includes an intelligent memory system that preserves context and knowledge across sessions, ensuring Claude Code never loses track of your project's history.

## Overview

The memory system automatically captures conversations, decisions, and context from every session, making it available in future sessions. This eliminates the need to re-explain project architecture, past decisions, or implementation patterns.

## Key Features

### 1. Automatic Context Loading

When Claude Code starts a new session, the framework automatically:
- Loads the project summary (3-5 pages of condensed knowledge)
- Retrieves the last 50 messages for immediate context
- Performs RAG semantic search for relevant historical information

No manual intervention required - context is ready from the first message.

### 2. Conversation Persistence

Every message exchanged between you and Claude is automatically saved:
- User questions and requests
- Claude's responses and analysis
- System messages and events
- All task-related discussions

Messages are indexed in real-time using ChromaDB for semantic search.

### 3. Project Summary

The system maintains a living document of your project:
- Architecture overview and key decisions
- Technology stack and patterns
- Common gotchas and solutions
- Best practices discovered

The summary is automatically updated after each session, growing smarter over time.

### 4. Semantic Search

All historical conversations are indexed using embeddings:
- Vector database (ChromaDB) for fast similarity search
- Hybrid search combining embeddings and metadata
- Context-aware retrieval based on current task
- Separate collections per project

## Memory Components

### Database Tables

#### `conversation_memory`
Stores all conversation messages with full context:
```sql
CREATE TABLE conversation_memory (
    id INTEGER PRIMARY KEY,
    project_id TEXT NOT NULL,
    session_id TEXT,
    task_id INTEGER,
    message_type TEXT,        -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    timestamp DATETIME,
    metadata TEXT             -- JSON metadata
);
```

#### `project_summaries`
Maintains condensed project knowledge:
```sql
CREATE TABLE project_summaries (
    project_id TEXT PRIMARY KEY,
    summary TEXT,             -- 3-5 pages (~15,000 chars)
    key_decisions TEXT,       -- JSON array
    tech_stack TEXT,          -- JSON array
    patterns TEXT,            -- JSON array
    gotchas TEXT,             -- JSON array
    last_updated DATETIME,
    version INTEGER
);
```

#### `memory_rag_status`
Tracks RAG indexing status:
```sql
CREATE TABLE memory_rag_status (
    id INTEGER PRIMARY KEY,
    project_id TEXT,
    message_id INTEGER,
    indexed_at DATETIME,
    collection_name TEXT,
    embedding_model TEXT
);
```

### RAG Collections

**Centralized ChromaDB Storage** (as of 2025-11-25):
- **Location**: Framework root `.claude/data/chromadb` (shared across all projects)
- **Benefit**: Single vector database instance reduces memory overhead
- **Collection per project**: Each project has its own collection `memory_{project_id}`
- **Embedding model**: `all-MiniLM-L6-v2`
- **Metadata filtering**: By date, task, message type
- **Automatic reindexing**: On updates

Previously, each project had its own ChromaDB directory. Now all projects share a centralized ChromaDB instance for better resource management.

## Automatic Workflow

### Session Start
1. `OnSessionStart` hook triggers
2. `get_project_memory_context` MCP tool called
3. System loads:
   - Project summary
   - Last 50 messages
   - Top 20 relevant RAG results
4. Context injected into Claude's working memory

### During Session
1. Every message automatically saved to database
2. Messages indexed in RAG collection
3. Important events trigger summary updates
4. No manual intervention needed

### Session End
1. Session insights extracted
2. Project summary updated with new knowledge
3. Cleanup of temporary data
4. Memory ready for next session

## MCP Tools

### Automatic (via Hooks)

These work without manual intervention:

#### Memory Conversation Capture
- **Enabled by default**: Yes
- **Purpose**: Saves all messages automatically
- **Hook type**: Message interceptor
- **Status**: Active on all projects

#### Memory Session Summarizer
- **Enabled by default**: Yes
- **Purpose**: Updates project summary
- **Hook type**: Session end
- **Status**: Active on all projects

### Manual Commands

For specific memory operations:

#### Load Full Context
```bash
mcp__claudetask__get_project_memory_context
```
Returns complete memory context including summary, recent messages, and RAG search results.

#### Save Important Insight
```bash
mcp__claudetask__save_conversation_message \
  --message_type="assistant" \
  --content="Critical architectural decision: Using event-driven architecture for real-time updates"
```

#### Update Project Summary
```bash
mcp__claudetask__update_project_summary \
  --trigger="important_decision" \
  --new_insights="Migrated from REST polling to WebSocket for live updates. Reduced latency by 90%."
```

#### Search Historical Context
```bash
mcp__claudetask__search_project_memories \
  --query="authentication implementation" \
  --max_results=10
```

## Configuration

### Memory Limits

- **Project Summary**: 15,000 characters (~5 pages)
- **Recent Messages**: 50 messages (sliding window)
- **RAG Search Results**: 20 documents by default
- **Message Retention**: Unlimited (archived after 30 days)

### Hook Status

Check memory hooks status:
```bash
curl http://localhost:3333/api/projects/{project_id}/hooks
```

Enable/disable hooks via ClaudeTask UI:
- Navigate to Project Settings
- Go to Hooks tab
- Toggle memory hooks as needed

### Performance Settings

Memory system is optimized for:
- Fast context loading (<1 second)
- Real-time message indexing
- Efficient vector search
- Minimal impact on conversation latency
- **Centralized ChromaDB**: Single database instance shared across projects reduces memory footprint

## Use Cases

### 1. Onboarding New Sessions

**Scenario**: Starting work after a week away

**Without Memory**:
- Re-explain project architecture
- Remind Claude of past decisions
- Re-discover solutions to known issues

**With Memory**:
- Claude immediately recalls project context
- Knows what's been implemented
- Remembers patterns and gotchas

### 2. Complex Decision Tracking

**Scenario**: Made architectural decision 3 weeks ago

**Search Past Decision**:
```bash
mcp__claudetask__search_project_memories \
  --query="why did we choose GraphQL over REST"
```

Returns the full context of that decision including reasoning and alternatives considered.

### 3. Pattern Recognition

**Scenario**: Implementing similar feature to previous work

Claude automatically:
- Recalls similar implementations
- Suggests proven patterns
- Warns about known pitfalls
- Maintains consistency across features

## Best Practices

### DO:
- Trust the automatic system - it captures everything important
- Use `update_project_summary` for critical architectural decisions
- Rely on loaded context at session start
- Search historical context for specific information

### DON'T:
- Manually save every message (hooks handle this)
- Reload context repeatedly (it's cached per session)
- Ignore the loaded context when starting work
- Disable memory hooks without good reason

## Troubleshooting

### Context Not Loading

**Check hooks are enabled**:
```bash
curl http://localhost:3333/api/projects/{project_id}/hooks | grep memory
```

**Verify messages being saved**:
```sql
SELECT COUNT(*) FROM conversation_memory
WHERE project_id = 'your-project-id';
```

**Check MCP server**:
```bash
ps aux | grep claudetask_mcp
```

### Memory Too Large

- Summary auto-truncates at 15,000 characters
- Old messages archived after 30 days
- RAG index rebuilds periodically for optimization

### Search Not Working

**Check RAG service**:
```bash
curl http://localhost:3333/api/projects/{project_id}/rag/status
```

**Rebuild index if needed**:
```bash
mcp__claudetask__reindex_codebase --full_reindex=true
```

### Performance Issues

**Check memory statistics**:
```bash
curl http://localhost:3333/api/projects/{project_id}/memory/stats
```

Returns:
- Total messages stored
- Summary version
- Index size
- Last update timestamp

## API Endpoints

### Save Message
```http
POST /api/projects/{project_id}/memory/messages
Content-Type: application/json

{
  "session_id": "session-uuid",
  "task_id": 42,
  "message_type": "assistant",
  "content": "Full message content",
  "metadata": {}
}
```

### Get Context
```http
GET /api/projects/{project_id}/memory/context?session_id=session-uuid
```

Returns:
```json
{
  "summary": "Project summary...",
  "recent_messages": [...],
  "rag_results": [...],
  "version": 5
}
```

### Update Summary
```http
PUT /api/projects/{project_id}/memory/summary
Content-Type: application/json

{
  "trigger": "session_end",
  "new_insights": "Key findings from this session..."
}
```

### Search Memories
```http
POST /api/projects/{project_id}/memory/search
Content-Type: application/json

{
  "query": "search text",
  "max_results": 20,
  "filter_metadata": {
    "task_id": 42
  }
}
```

## Database Schema

Complete schema for memory system:

```sql
-- Conversation messages
CREATE TABLE conversation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    session_id TEXT,
    task_id INTEGER,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Indexes
CREATE INDEX idx_conv_project ON conversation_memory(project_id);
CREATE INDEX idx_conv_timestamp ON conversation_memory(project_id, timestamp DESC);
CREATE INDEX idx_conv_session ON conversation_memory(session_id);
CREATE INDEX idx_conv_task ON conversation_memory(task_id);

-- Project summaries
CREATE TABLE project_summaries (
    project_id TEXT PRIMARY KEY,
    summary TEXT,
    key_decisions TEXT,
    tech_stack TEXT,
    patterns TEXT,
    gotchas TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- RAG indexing status
CREATE TABLE memory_rag_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    message_id INTEGER NOT NULL,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    collection_name TEXT,
    embedding_model TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (message_id) REFERENCES conversation_memory(id)
);

-- Memory session tracking
CREATE TABLE memory_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    context_loaded_at DATETIME,
    summary_version INTEGER,
    messages_loaded INTEGER DEFAULT 0,
    rag_results_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

## Future Enhancements

### Planned Features
- Claude API integration for intelligent summarization
- Cross-project memory sharing
- Memory export/import for backup
- Advanced analytics and insights
- Custom embedding models
- Multi-modal memory (images, diagrams)

### Research Areas
- Optimal summary length vs. comprehensiveness
- Memory pruning strategies for very large projects
- Privacy-preserving memory sharing
- Integration with external knowledge bases

## Summary

The memory system is your project's persistent brain:
- **Automatic**: Works via hooks, no manual intervention
- **Comprehensive**: Captures all important context
- **Intelligent**: RAG search finds relevant information
- **Persistent**: Survives across sessions
- **Growing**: Gets smarter with each interaction

Trust the system - it remembers so you don't have to!
