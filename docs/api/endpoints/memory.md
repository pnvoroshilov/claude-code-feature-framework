# Memory API Endpoints

Complete API reference for project memory management with automatic storage backend selection (SQLite/ChromaDB or MongoDB/Vector Search).

**Last Updated**: 2025-11-27
**Version**: 1.1

## Overview

The Memory API provides endpoints for storing, retrieving, and searching conversation history with automatic semantic indexing. The system automatically uses the appropriate storage backend based on the project's `storage_mode` setting:

- **Local Storage**: SQLite + ChromaDB with all-MiniLM-L6-v2 (384d embeddings)
- **Cloud Storage**: MongoDB Atlas + Vector Search with voyage-3-large (1024d embeddings)

All endpoints follow the same interface regardless of storage backend, ensuring seamless operation.

## Base URL

```
/api/projects/{project_id}/memory
```

All endpoints require a valid `project_id` path parameter.

## Storage Backend Selection

The API automatically selects the storage backend:

```python
# Backend logic
storage_mode = project_settings.storage_mode  # "local" or "mongodb"

if storage_mode == "mongodb":
    # Use MongoDB + Voyage AI embeddings (1024d)
    repo = MongoDBMemoryRepository(mongodb_db)
else:
    # Use SQLite + ChromaDB (384d)
    repo = SQLiteMemoryRepository(sqlite_db)
```

No client-side configuration required - storage mode is determined at project creation time.

## Endpoints

### 1. Save Conversation Message

Save a new message to conversation history with automatic embedding generation.

**Endpoint**: `POST /api/projects/{project_id}/memory/messages`

**Authentication**: Not required (internal API)

**Request Body**:
```json
{
  "message_type": "user",
  "content": "How do I implement authentication?",
  "task_id": 42,
  "metadata": {
    "session_id": "abc-123",
    "timestamp": "2025-11-27T10:30:00Z",
    "context": "authentication-feature"
  }
}
```

**Parameters**:
- `message_type` (string, required): Type of message - "user", "assistant", or "system"
- `content` (string, required): Message content (text)
- `task_id` (integer, optional): Associated task ID
- `metadata` (object, optional): Additional metadata (stored as JSON)

**Response** (201 Created):
```json
{
  "message_id": "msg_abc123",
  "status": "saved",
  "indexed": true,
  "embedding_model": "voyage-3-large",
  "storage_backend": "mongodb"
}
```

**Response Fields**:
- `message_id`: Unique identifier for the saved message
- `status`: "saved" if successful
- `indexed`: Whether embedding was generated and stored
- `embedding_model`: Model used for embeddings ("all-MiniLM-L6-v2" or "voyage-3-large")
- `storage_backend`: "local" or "mongodb"

**Error Responses**:
- `400 Bad Request`: Invalid message type or empty content
- `404 Not Found`: Project not found
- `500 Internal Server Error`: Database or embedding service error

**Example**:
```bash
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "assistant",
    "content": "To implement authentication, use FastAPI with JWT tokens...",
    "task_id": 42
  }'
```

---

### 2. Get Recent Messages

Retrieve recent conversation messages for context loading.

**Endpoint**: `GET /api/projects/{project_id}/memory/messages/recent`

**Query Parameters**:
- `limit` (integer, optional): Number of messages to retrieve (default: 50, max: 200)
- `session_id` (string, optional): Filter by specific session
- `task_id` (integer, optional): Filter by specific task

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "msg_001",
      "message_type": "user",
      "content": "How do I add authentication?",
      "timestamp": "2025-11-27T10:30:00Z",
      "task_id": 42,
      "session_id": "abc-123"
    },
    {
      "id": "msg_002",
      "message_type": "assistant",
      "content": "To add authentication...",
      "timestamp": "2025-11-27T10:31:00Z",
      "task_id": 42,
      "session_id": "abc-123"
    }
  ],
  "count": 2,
  "storage_backend": "mongodb"
}
```

**Example**:
```bash
# Get last 50 messages
curl "http://localhost:3333/api/projects/proj_123/memory/messages/recent?limit=50"

# Get messages for specific task
curl "http://localhost:3333/api/projects/proj_123/memory/messages/recent?task_id=42"
```

---

### 3. Search Memory (Semantic Search)

Perform semantic search across conversation history using natural language queries.

**Endpoint**: `POST /api/projects/{project_id}/memory/search`

**Request Body**:
```json
{
  "query": "authentication implementation patterns",
  "limit": 20,
  "session_id": null
}
```

**Parameters**:
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Number of results to return (default: 20, max: 100)
- `session_id` (string, optional): Filter results to specific session

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "msg_042",
      "content": "We implemented JWT authentication with refresh tokens...",
      "message_type": "assistant",
      "timestamp": "2025-11-25T14:20:00Z",
      "task_id": 38,
      "similarity": 0.89,
      "metadata": {
        "session_id": "xyz-789",
        "context": "security-feature"
      }
    },
    {
      "id": "msg_103",
      "content": "For authentication, we chose OAuth2 with PKCE flow...",
      "message_type": "assistant",
      "timestamp": "2025-11-20T09:15:00Z",
      "task_id": 22,
      "similarity": 0.82,
      "metadata": {}
    }
  ],
  "query_embedding_model": "voyage-3-large",
  "search_method": "vector_search",
  "count": 2,
  "storage_backend": "mongodb"
}
```

**Response Fields**:
- `results`: Array of matching messages sorted by relevance
- `similarity`: Cosine similarity score (0-1, higher is more relevant)
- `query_embedding_model`: Model used to embed the search query
- `search_method`: "vector_search" (MongoDB) or "chromadb" (local)
- `count`: Number of results returned
- `storage_backend`: "local" or "mongodb"

**Example**:
```bash
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to handle database migrations",
    "limit": 10
  }'
```

---

### 4. Update Project Summary

Update the project's condensed knowledge summary with new insights.

**Endpoint**: `POST /api/projects/{project_id}/memory/summary`

**Request Body**:
```json
{
  "trigger": "important_decision",
  "new_insights": "Decided to use MongoDB Atlas for vector search due to better performance with 1024d embeddings and sub-200ms query times.",
  "last_summarized_message_id": "msg_150"
}
```

**Parameters**:
- `trigger` (string, required): What triggered the update - "session_end", "important_decision", "task_complete", "manual"
- `new_insights` (string, required): New information to incorporate into summary
- `last_summarized_message_id` (string, optional): ID of last message included in summary (for incremental updates)

**Response** (200 OK):
```json
{
  "status": "updated",
  "summary_version": 15,
  "summary_length": 12500,
  "last_updated": "2025-11-27T11:00:00Z",
  "storage_backend": "mongodb"
}
```

**Example**:
```bash
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "task_complete",
    "new_insights": "Completed authentication feature using FastAPI JWT with refresh tokens. Key learnings: Store refresh tokens in HTTP-only cookies for security."
  }'
```

---

### 5. Get Project Summary

Retrieve the current project knowledge summary.

**Endpoint**: `GET /api/projects/{project_id}/memory/summary`

**Response** (200 OK):
```json
{
  "project_id": "proj_123",
  "summary": "## Project Overview\n\nThis is a task management system...\n\n## Key Decisions\n- Chose MongoDB Atlas for scalability...\n- Implemented JWT authentication...",
  "version": 15,
  "last_updated": "2025-11-27T11:00:00Z",
  "summary_length": 12500,
  "storage_backend": "mongodb"
}
```

**Example**:
```bash
curl "http://localhost:3333/api/projects/proj_123/memory/summary"
```

---

### 6. Get Memory Statistics

Retrieve statistics about stored memories and indexing status.

**Endpoint**: `GET /api/projects/{project_id}/memory/stats`

**Response** (200 OK):
```json
{
  "total_messages": 1523,
  "indexed_messages": 1523,
  "unindexed_messages": 0,
  "storage_backend": "mongodb",
  "embedding_model": "voyage-3-large",
  "embedding_dimensions": 1024,
  "collection_name": "conversation_memory",
  "vector_index_name": "memory_vector_idx",
  "oldest_message": "2025-09-01T08:00:00Z",
  "newest_message": "2025-11-27T11:00:00Z",
  "index_health": "healthy"
}
```

**Local Storage Response** (SQLite + ChromaDB):
```json
{
  "total_messages": 842,
  "indexed_messages": 842,
  "unindexed_messages": 0,
  "storage_backend": "local",
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimensions": 384,
  "chromadb_collection": "memory_proj_123",
  "chromadb_location": "/path/to/.claude/data/chromadb",
  "oldest_message": "2025-10-15T09:00:00Z",
  "newest_message": "2025-11-27T11:00:00Z",
  "index_health": "healthy"
}
```

**Example**:
```bash
curl "http://localhost:3333/api/projects/proj_123/memory/stats"
```

---

### 7. Reindex Messages

Trigger reindexing of unindexed messages (useful after migration or embedding model changes).

**Endpoint**: `POST /api/projects/{project_id}/memory/reindex`

**Query Parameters**:
- `force` (boolean, optional): Reindex all messages even if already indexed (default: false)

**Response** (200 OK):
```json
{
  "status": "reindexing_started",
  "total_messages": 1523,
  "messages_to_index": 15,
  "estimated_time_seconds": 8,
  "job_id": "reindex_abc123"
}
```

**Example**:
```bash
# Reindex only unindexed messages
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/reindex"

# Force reindex all messages
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/reindex?force=true"
```

---

### 8. Intelligent Summary Update

Update project summary with structured insights including key decisions, tech stack, patterns, and gotchas.

**Endpoint**: `POST /api/projects/{project_id}/memory/summary/intelligent-update`

**Request Body**:
```json
{
  "summary": "ClaudeTask Framework is an autonomous task orchestration system built with Python FastAPI backend and React frontend. Recent work focused on migrating memory storage to MongoDB Atlas with Voyage AI embeddings for semantic search.",
  "key_decisions": [
    "Migrated to MongoDB Atlas for better scalability",
    "Adopted hook-based logging system with storage_mode support",
    "Using Voyage AI for embeddings instead of OpenAI"
  ],
  "tech_stack": [
    "Python",
    "FastAPI",
    "MongoDB",
    "React",
    "TypeScript",
    "Voyage AI"
  ],
  "patterns": [
    "Repository pattern for data access",
    "Hook-logger centralization",
    "MCP-based tool integration"
  ],
  "gotchas": [
    "Always source hook-logger.sh in hooks",
    "Use [skip-hook] tag to prevent infinite loops",
    "Check storage_mode before logging"
  ]
}
```

**Parameters**:
- `summary` (string, required): Comprehensive project narrative (2-5 paragraphs)
- `key_decisions` (array, optional): List of architectural/implementation decisions
- `tech_stack` (array, optional): List of technologies used
- `patterns` (array, optional): List of coding/architectural patterns
- `gotchas` (array, optional): List of warnings and pitfalls

**Response** (200 OK):
```json
{
  "success": true,
  "summary": "ClaudeTask Framework is...",
  "key_decisions": [...],
  "tech_stack": [...],
  "patterns": [...],
  "gotchas": [...],
  "last_updated": "2025-11-27T14:30:00Z",
  "version": 16,
  "storage_mode": "mongodb"
}
```

**Features**:
- Completely replaces existing summary (no merge)
- Generates embedding for semantic search (MongoDB only)
- Increments version number
- Structures project knowledge for easy retrieval

**Use Cases**:
- Automatic summarization via `/summarize-project` command
- Claude's intelligent analysis of conversation history
- Post-session knowledge consolidation
- Structured project documentation

**Example**:
```bash
curl -X POST "http://localhost:3333/api/projects/proj_123/memory/summary/intelligent-update" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Project overview...",
    "key_decisions": ["Decision 1: Reason"],
    "tech_stack": ["Python", "FastAPI"],
    "patterns": ["Repository Pattern"],
    "gotchas": ["Always check storage_mode"]
  }'
```

---

### 9. Delete Messages

Delete specific messages or all messages in a session/task.

**Endpoint**: `DELETE /api/projects/{project_id}/memory/messages`

**Query Parameters**:
- `message_id` (string, optional): Delete specific message
- `session_id` (string, optional): Delete all messages in session
- `task_id` (integer, optional): Delete all messages in task
- `before_date` (string, optional): Delete messages before date (ISO 8601 format)

**Response** (200 OK):
```json
{
  "deleted_count": 42,
  "storage_backend": "mongodb"
}
```

**Error Responses**:
- `400 Bad Request`: No deletion criteria provided
- `404 Not Found`: Message/session/task not found

**Example**:
```bash
# Delete specific message
curl -X DELETE "http://localhost:3333/api/projects/proj_123/memory/messages?message_id=msg_042"

# Delete all messages from a task
curl -X DELETE "http://localhost:3333/api/projects/proj_123/memory/messages?task_id=42"

# Delete messages before a date
curl -X DELETE "http://localhost:3333/api/projects/proj_123/memory/messages?before_date=2025-09-01T00:00:00Z"
```

---

## Storage Backend Comparison

| Feature | Local (SQLite + ChromaDB) | Cloud (MongoDB + Vector Search) |
|---------|---------------------------|----------------------------------|
| **Embedding Model** | all-MiniLM-L6-v2 (384d) | voyage-3-large (1024d) |
| **Search Quality** | Good for general text | Superior for code and technical content |
| **Query Speed** | ~50-100ms | ~20-50ms (sub-200ms guaranteed) |
| **Setup Complexity** | Zero config | Requires MongoDB Atlas + Voyage AI API |
| **Cost** | Free | MongoDB Atlas (free tier available) + Voyage AI ($0.00013/1K tokens) |
| **Scalability** | Limited to local disk | Highly scalable cloud storage |
| **Backup** | Manual file backup | Automatic MongoDB backups |
| **Multi-device** | Single machine only | Accessible from any machine |

## MCP Tools Integration

The Memory API is integrated with MCP tools for Claude Code:

### `get_project_memory_context`
Loads complete memory context at session start:
- Project summary
- Last 50 messages
- Top 20 relevant RAG results

Automatically called by `OnSessionStart` hook.

### `save_conversation_message`
Saves messages automatically during sessions via `Memory Conversation Capture` hook.

### `update_project_summary`
Updates project summary at session end via `Memory Session Summarizer` hook.

### `intelligent_update_project_summary`
Performs structured analysis and updates summary with key decisions, tech stack, patterns, and gotchas. Used by the `/summarize-project` slash command for intelligent project knowledge consolidation.

### `search_project_memories`
Allows Claude to search historical conversations for relevant context.

## Usage Patterns

### Pattern 1: Automatic Context Loading (Default)

```python
# Handled automatically by hooks
# OnSessionStart → get_project_memory_context
# Returns: {summary, recent_messages, rag_results}
```

### Pattern 2: Manual Message Save

```python
import requests

response = requests.post(
    "http://localhost:3333/api/projects/proj_123/memory/messages",
    json={
        "message_type": "system",
        "content": "Task #42 marked as complete",
        "task_id": 42,
        "metadata": {"event": "task_complete"}
    }
)
```

### Pattern 3: Semantic Search for Context

```python
# Search for relevant past discussions
response = requests.post(
    "http://localhost:3333/api/projects/proj_123/memory/search",
    json={
        "query": "how did we implement caching?",
        "limit": 5
    }
)

results = response.json()["results"]
for result in results:
    print(f"Relevance: {result['similarity']:.2f}")
    print(f"Content: {result['content'][:100]}...")
```

### Pattern 4: Summary Updates After Decisions

```python
# After important architectural decision
response = requests.post(
    "http://localhost:3333/api/projects/proj_123/memory/summary",
    json={
        "trigger": "important_decision",
        "new_insights": "Decided to use Redis for caching due to TTL support and pub/sub capabilities."
    }
)
```

### Pattern 5: Intelligent Structured Summarization

```python
# Automatic intelligent summary with structured data (via /summarize-project command)
response = requests.post(
    "http://localhost:3333/api/projects/proj_123/memory/summary/intelligent-update",
    json={
        "summary": "ClaudeTask Framework is an autonomous task orchestration system...",
        "key_decisions": [
            "Migrated to MongoDB Atlas for scalability",
            "Adopted Repository Pattern for storage abstraction"
        ],
        "tech_stack": ["Python", "FastAPI", "MongoDB", "React", "Voyage AI"],
        "patterns": ["Repository Pattern", "Hook-based logging", "MCP tools"],
        "gotchas": [
            "Use [skip-hook] tag to prevent recursion",
            "Always check storage_mode before logging"
        ]
    }
)

# This endpoint completely replaces the summary with structured data
# Ideal for periodic knowledge consolidation after major work sessions
```

## Error Handling

All endpoints return standard HTTP error responses:

**400 Bad Request**:
```json
{
  "error": "Invalid message type. Must be one of: user, assistant, system",
  "code": "INVALID_MESSAGE_TYPE"
}
```

**404 Not Found**:
```json
{
  "error": "Project not found",
  "code": "PROJECT_NOT_FOUND",
  "project_id": "proj_123"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Failed to generate embeddings",
  "code": "EMBEDDING_SERVICE_ERROR",
  "details": "Voyage AI API timeout after 30 seconds"
}
```

## Best Practices

1. **Let Hooks Handle It**: Memory capture and summarization work automatically - don't call these endpoints manually unless needed

2. **Use Semantic Search**: When looking for past context, use the search endpoint instead of retrieving all messages

3. **Monitor Stats**: Check `/stats` endpoint periodically to ensure indexing is keeping up

4. **Incremental Summaries**: Update summaries incrementally with `last_summarized_message_id` instead of regenerating from scratch

5. **Storage Mode Selection**: Choose storage mode at project creation based on:
   - **Local**: Small projects, single developer, cost-sensitive
   - **Cloud**: Large projects, team collaboration, better search quality needed

## Migration Between Storage Backends

To migrate a project from local to cloud storage (or vice versa):

```bash
# Use the migration CLI tool
python -m claudetask.migrations.migrate_to_mongodb \
  --project-id=proj_123 \
  --target-mode=mongodb
```

See: [MongoDB Atlas Storage Documentation](../../features/mongodb-atlas-storage.md)

## See Also

- [Memory System Overview](../../features/memory-system.md) - Complete memory system guide
- [MongoDB Atlas Storage](../../features/mongodb-atlas-storage.md) - Cloud storage setup
- [Codebase RAG API](./codebase-rag.md) - Semantic code search (MongoDB only)
- [Cloud Storage API](./cloud-storage.md) - MongoDB and Voyage AI configuration

---

**API Version**: 1.1
**Storage Backends**: SQLite + ChromaDB (local) / MongoDB + Vector Search (cloud)
**Embedding Models**: all-MiniLM-L6-v2 (384d) / voyage-3-large (1024d)
**Default Backend**: Local (SQLite + ChromaDB)
**Endpoints**: 9 (added intelligent summary update in v1.1)
