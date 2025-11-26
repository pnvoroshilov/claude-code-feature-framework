# Codebase RAG API Endpoints

## Overview

The Codebase RAG (Retrieval-Augmented Generation) API provides semantic code search capabilities using MongoDB Atlas Vector Search with Voyage AI embeddings. This enables Claude Code to search and understand your entire codebase semantically.

**Version**: 1.0.0
**Last Updated**: 2025-11-26
**Status**: Production Ready
**Storage Backend**: MongoDB Atlas Only

## Prerequisites

- MongoDB Atlas cluster configured (see [Cloud Storage Settings](../../features/mongodb-atlas-storage.md))
- Voyage AI API key configured
- Project storage mode set to `"mongodb"`

## Base URL

```
http://localhost:3333/api/codebase
```

## Endpoints

### 1. Index Codebase

Index entire codebase with semantic chunking and vector embeddings.

**Endpoint**: `POST /api/codebase/index`

**Request Body**:
```json
{
  "repo_path": "/path/to/repository",
  "full_reindex": false
}
```

**Parameters**:
- `repo_path` (string, required): Absolute path to repository root
- `full_reindex` (boolean, optional): Delete all existing chunks before indexing (default: false)

**Response** (200 OK):
```json
{
  "project_id": "abc-123",
  "files_processed": 245,
  "chunks_created": 1823,
  "total_tokens": 456789,
  "duration_seconds": 127.5,
  "status": "completed"
}
```

**Background Processing**: Indexing runs asynchronously. Large codebases may take several minutes.

**Supported Languages**:
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.tsx`, `.jsx`)
- Java (`.java`)
- C# (`.cs`)
- Go (`.go`)
- Rust (`.rs`)
- C/C++ (`.c`, `.cpp`)
- Ruby (`.rb`)
- PHP (`.php`)
- Swift (`.swift`)
- Kotlin (`.kt`)
- Scala (`.scala`)
- Vue (`.vue`)
- Svelte (`.svelte`)
- HTML/CSS (`.html`, `.css`, `.scss`)

**Chunking Strategy**:
- Chunk size: 500 tokens (configurable)
- Chunk overlap: 50 tokens (prevents context loss)
- Semantic boundaries: Functions, classes, modules
- Preserves code structure and symbols

**Example**:
```bash
curl -X POST http://localhost:3333/api/codebase/index \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/me/projects/my-app",
    "full_reindex": true
  }'
```

---

### 2. Index Specific Files

Index only specific files (incremental indexing).

**Endpoint**: `POST /api/codebase/index-files`

**Request Body**:
```json
{
  "repo_path": "/path/to/repository",
  "file_paths": [
    "src/components/Header.tsx",
    "backend/api/users.py",
    "utils/helpers.js"
  ]
}
```

**Parameters**:
- `repo_path` (string, required): Repository root path
- `file_paths` (array of strings, required): Relative paths to files within repository

**Response** (200 OK):
```json
{
  "indexed_files": 3,
  "chunks_created": 47,
  "skipped_files": 0,
  "errors": []
}
```

**Use Cases**:
- Update index after code changes
- Index newly created files
- Re-index modified files without full reindex

**Example**:
```bash
curl -X POST http://localhost:3333/api/codebase/index-files \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/me/projects/my-app",
    "file_paths": ["src/api/auth.ts", "src/models/User.ts"]
  }'
```

---

### 3. Search Codebase

Semantic search across indexed codebase using natural language.

**Endpoint**: `POST /api/codebase/search`

**Request Body**:
```json
{
  "query": "authentication middleware that verifies JWT tokens",
  "limit": 20,
  "min_similarity": 0.0,
  "language": "python"
}
```

**Parameters**:
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum results to return (default: 20)
- `min_similarity` (float, optional): Minimum similarity score 0.0-1.0 (default: 0.0)
- `language` (string, optional): Filter by programming language (e.g., "python", "typescript")

**Response** (200 OK):
```json
{
  "query": "authentication middleware that verifies JWT tokens",
  "results": [
    {
      "chunk_id": "abc123-chunk-001",
      "file_path": "backend/middleware/auth.py",
      "start_line": 45,
      "end_line": 78,
      "content": "def verify_jwt_token(token: str) -> Dict:\n    \"\"\"Verify JWT token and return payload...",
      "summary": "JWT token verification middleware with expiration checking",
      "language": "python",
      "chunk_type": "function",
      "symbols": ["verify_jwt_token", "decode_token", "check_expiration"],
      "score": 0.92
    },
    {
      "chunk_id": "abc123-chunk-015",
      "file_path": "backend/routers/auth.py",
      "start_line": 12,
      "end_line": 34,
      "content": "async def authenticate_user(credentials: LoginCredentials):...",
      "summary": "User authentication endpoint using JWT",
      "language": "python",
      "chunk_type": "function",
      "symbols": ["authenticate_user", "create_access_token"],
      "score": 0.87
    }
  ],
  "total_results": 2,
  "search_time_ms": 142
}
```

**Search Features**:
- **Semantic Understanding**: Understands intent, not just keywords
- **Multi-language**: Search across different programming languages
- **Context Aware**: Returns surrounding code context
- **Symbol Extraction**: Identifies functions, classes, variables
- **Relevance Ranking**: Results sorted by similarity score

**Example Queries**:
```bash
# Find authentication code
curl -X POST http://localhost:3333/api/codebase/search \
  -H "Content-Type: application/json" \
  -d '{"query": "user login and authentication flow"}'

# Find React components for forms
curl -X POST http://localhost:3333/api/codebase/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "form validation with error handling",
    "language": "typescript",
    "limit": 10
  }'

# Find database queries
curl -X POST http://localhost:3333/api/codebase/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SQL queries that join users and orders tables",
    "min_similarity": 0.5
  }'
```

---

### 4. Reindex Codebase

Re-index only changed files based on file hashes.

**Endpoint**: `POST /api/codebase/reindex`

**Request Body**:
```json
{
  "repo_path": "/path/to/repository"
}
```

**Response** (200 OK):
```json
{
  "files_scanned": 245,
  "files_changed": 12,
  "files_reindexed": 12,
  "chunks_updated": 89,
  "chunks_deleted": 34,
  "duration_seconds": 15.2
}
```

**How It Works**:
1. Scans all files in repository
2. Computes file hash (SHA-256) for each file
3. Compares with stored hashes in database
4. Re-indexes only files with changed hashes
5. Removes chunks for deleted files

**Use Cases**:
- Daily/hourly automated reindexing
- Post-merge hook integration
- CI/CD pipeline integration

**Example**:
```bash
curl -X POST http://localhost:3333/api/codebase/reindex \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/Users/me/projects/my-app"}'
```

---

### 5. Get Indexing Statistics

Retrieve statistics about indexed codebase.

**Endpoint**: `GET /api/codebase/{project_id}/stats`

**Parameters**:
- `project_id` (path parameter, required): Project UUID

**Response** (200 OK):
```json
{
  "project_id": "abc-123",
  "total_files": 245,
  "total_chunks": 1823,
  "total_size_bytes": 8934521,
  "languages": {
    "python": 567,
    "typescript": 892,
    "javascript": 234,
    "html": 89,
    "css": 41
  },
  "chunk_types": {
    "function": 1234,
    "class": 345,
    "module": 178,
    "import": 66
  },
  "last_indexed": "2025-11-26T14:32:18Z",
  "index_version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:3333/api/codebase/abc-123/stats
```

---

### 6. Delete Index

Delete all indexed chunks for a project.

**Endpoint**: `DELETE /api/codebase/{project_id}`

**Parameters**:
- `project_id` (path parameter, required): Project UUID

**Response** (200 OK):
```json
{
  "deleted_chunks": 1823,
  "deleted_files": 245,
  "status": "success"
}
```

**Example**:
```bash
curl -X DELETE http://localhost:3333/api/codebase/abc-123
```

---

## Error Responses

### MongoDB Not Configured

**Status**: 503 Service Unavailable

```json
{
  "detail": "MongoDB not connected. Configure MongoDB Atlas in Settings → Cloud Storage."
}
```

**Solution**: Configure MongoDB in Cloud Storage Settings page.

---

### Voyage AI API Key Missing

**Status**: 500 Internal Server Error

```json
{
  "detail": "Voyage AI API key not configured. Set VOYAGE_AI_API_KEY in Settings -> Cloud Storage."
}
```

**Solution**: Add Voyage AI API key in Cloud Storage Settings.

---

### Invalid Repository Path

**Status**: 400 Bad Request

```json
{
  "detail": "Repository path does not exist: /invalid/path"
}
```

**Solution**: Provide valid absolute path to repository.

---

### Storage Mode Not MongoDB

**Status**: 400 Bad Request

```json
{
  "detail": "Codebase RAG requires MongoDB storage mode. Current mode: local"
}
```

**Solution**: Migrate project to MongoDB storage mode.

---

## MCP Integration

The Codebase RAG service is integrated with the ClaudeTask MCP server, providing MCP tools for Claude Code:

### MCP Tools

**`mcp__claudetask__search_codebase`**: Search codebase semantically
```python
result = await mcp__claudetask__search_codebase(
    query="authentication middleware",
    limit=10
)
```

**`mcp__claudetask__index_codebase`**: Trigger full indexing
```python
result = await mcp__claudetask__index_codebase(
    full_reindex=True
)
```

**`mcp__claudetask__reindex_codebase`**: Incremental reindex
```python
result = await mcp__claudetask__reindex_codebase()
```

See [MCP Tools Documentation](../mcp-tools.md) for complete reference.

---

## Technical Architecture

### Indexing Pipeline

```
Source Files
    ↓
File Scanner (filter by extension)
    ↓
Code Chunker (semantic boundaries)
    ↓
Voyage AI Embeddings (1024d vectors)
    ↓
MongoDB Atlas Vector Search
```

### Search Pipeline

```
Natural Language Query
    ↓
Voyage AI Embedding (1024d vector)
    ↓
MongoDB $vectorSearch (cosine similarity)
    ↓
Ranked Results (with metadata)
```

### File Hash Tracking

- **Algorithm**: SHA-256
- **Purpose**: Detect file changes for incremental reindexing
- **Storage**: `file_hash` field in chunk documents
- **Update**: On file modification, old chunks deleted and new ones created

---

## Performance Considerations

### Indexing Performance

| Repository Size | Files | Indexing Time | Chunks Created |
|----------------|-------|---------------|----------------|
| Small (<100 files) | 50 | ~10 seconds | 200-500 |
| Medium (100-500 files) | 250 | ~60 seconds | 1000-3000 |
| Large (500-2000 files) | 1000 | ~5 minutes | 5000-15000 |
| Very Large (>2000 files) | 5000 | ~20 minutes | 20000-50000 |

**Optimization Tips**:
- Use `.gitignore` patterns to exclude unnecessary files
- Run initial index as background job
- Use incremental reindexing for frequent updates
- Schedule full reindex weekly, incremental daily

### Search Performance

- **Average Query Time**: 100-200ms
- **Vector Index**: Automatic via MongoDB Atlas
- **Similarity Algorithm**: Cosine similarity
- **Top-K Retrieval**: Optimized for 10-50 results

---

## Best Practices

### 1. Initial Setup

```bash
# 1. Configure MongoDB Atlas and Voyage AI
# (via Cloud Storage Settings UI)

# 2. Run full index
curl -X POST http://localhost:3333/api/codebase/index \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/project",
    "full_reindex": true
  }'

# 3. Verify indexing
curl http://localhost:3333/api/codebase/{project_id}/stats
```

### 2. Incremental Updates

```bash
# After code changes, reindex incrementally
curl -X POST http://localhost:3333/api/codebase/reindex \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/project"}'
```

### 3. Hook Integration

Create post-push hook to auto-reindex:

```bash
#!/bin/bash
# .claude/hooks/post-push-reindex.sh

curl -X POST http://localhost:3333/api/codebase/reindex \
  -H "Content-Type: application/json" \
  -d "{\"repo_path\": \"$(pwd)\"}"
```

### 4. Search Optimization

```bash
# Narrow search with language filter
curl -X POST http://localhost:3333/api/codebase/search \
  -d '{
    "query": "user authentication",
    "language": "python",
    "min_similarity": 0.5,
    "limit": 10
  }'
```

---

## Limitations

1. **MongoDB Only**: Requires MongoDB Atlas storage mode
2. **File Size**: Maximum 10MB per file
3. **Supported Languages**: Limited to configured extensions
4. **Batch Size**: Embedding API rate limits apply
5. **Memory**: Large codebases may require significant memory during indexing

---

## Troubleshooting

### Indexing Fails

**Check**: MongoDB connection
```bash
curl http://localhost:3333/api/settings/cloud-storage/health
```

**Check**: Voyage AI API key
```bash
curl http://localhost:3333/api/settings/cloud-storage/status
```

### Search Returns No Results

1. Verify index exists: `GET /api/codebase/{project_id}/stats`
2. Check query is specific enough
3. Lower `min_similarity` threshold
4. Verify vector search index created in MongoDB Atlas

### Slow Indexing

1. Reduce `batch_size` (default: 50 chunks)
2. Exclude large directories (node_modules, build)
3. Run during off-peak hours
4. Use incremental reindexing instead of full reindex

---

## Related Documentation

- [MongoDB Atlas Storage Backend](../../features/mongodb-atlas-storage.md) - Cloud storage setup
- [Cloud Storage Settings](../../components/CloudStorageSettings.md) - Configuration UI
- [MCP Tools](../mcp-tools.md) - MCP integration for Claude Code
- [Memory System](../../features/memory-system.md) - Conversation memory with RAG

---

**Last Updated**: 2025-11-26
**API Version**: 1.0.0
**Storage Backend**: MongoDB Atlas + Voyage AI
