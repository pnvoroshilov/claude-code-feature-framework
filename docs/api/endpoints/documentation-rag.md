# Documentation RAG API Endpoints

Complete API reference for semantic documentation search with MongoDB Atlas Vector Search and Voyage AI embeddings.

**Last Updated**: 2025-11-27
**Version**: 1.0
**Status**: Production Ready

## Overview

The Documentation RAG API provides semantic search across project documentation using MongoDB Atlas Vector Search with voyage-3-large embeddings (1024 dimensions). This enables intelligent documentation discovery through natural language queries.

**Key Features:**
- Full documentation indexing (markdown, text files)
- Incremental updates based on file changes
- Smart markdown chunking by sections
- Semantic search with natural language queries
- voyage-3-large embeddings (1024d) for superior understanding
- Automatic indexing via post-push git hook

## Requirements

**Storage Mode**: MongoDB (Cloud Storage)
**Dependencies:**
- MongoDB Atlas with Vector Search enabled
- Voyage AI API key configured
- `documentation_chunks` collection with vector index

**Configuration:**
```bash
# .env
MONGODB_URI=mongodb+srv://...
VOYAGE_AI_API_KEY=your-api-key-here
```

## Base URL

```
/api/documentation-rag/{project_id}
```

All endpoints require a valid `project_id` path parameter.

## Architecture

```
Documentation Files (docs/, README.md, etc.)
           ↓
    DocumentationIndexer
           ↓
    Smart Chunking (by sections, headings)
           ↓
    Voyage AI Embeddings (1024d)
           ↓
    MongoDB documentation_chunks collection
           ↓
    Vector Search via $vectorSearch aggregation
           ↓
    Relevant Documentation Results
```

## Endpoints

### 1. Index Documentation

Index all documentation files for a project with full or incremental indexing.

**Endpoint**: `POST /api/documentation-rag/{project_id}/index`

**Authentication**: Not required (internal API)

**Request Body**:
```json
{
  "repo_path": "/Users/user/projects/myapp",
  "full_reindex": false
}
```

**Parameters**:
- `repo_path` (string, required): Absolute path to repository root
- `full_reindex` (boolean, optional): Delete all existing chunks and reindex from scratch (default: false)

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Documentation indexing completed",
  "total_files": 42,
  "indexed_files": 38,
  "skipped_files": 4,
  "total_chunks": 312,
  "errors": [],
  "duration_seconds": 12.5
}
```

**Response Fields**:
- `total_files`: Total documentation files found
- `indexed_files`: Number of files successfully indexed
- `skipped_files`: Files skipped (unchanged or errors)
- `total_chunks`: Total documentation chunks created
- `errors`: List of errors encountered (if any)
- `duration_seconds`: Time taken for indexing

**Error Responses**:
- `503 Service Unavailable`: MongoDB not connected or Voyage AI API key missing
- `500 Internal Server Error`: Indexing failure

**Example**:
```bash
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/index" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/Users/user/projects/myapp",
    "full_reindex": false
  }'
```

**Indexing Behavior**:
- **Supported Extensions**: `.md`, `.markdown`, `.txt`, `.rst`, `.adoc`
- **Prioritized Directories**: `docs/`, `doc/`, `documentation/`, `wiki/`
- **Root Files**: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, etc.
- **Skip Directories**: `node_modules`, `venv`, `__pycache__`, `.git`, `dist`, `build`
- **Chunking**: Smart markdown chunking by sections and headings
- **Change Detection**: Files are re-indexed only if content changed (hash-based)

---

### 2. Index Specific Files

Index or re-index specific documentation files.

**Endpoint**: `POST /api/documentation-rag/{project_id}/index-files`

**Request Body**:
```json
{
  "file_paths": [
    "docs/api/endpoints/authentication.md",
    "docs/architecture/overview.md",
    "README.md"
  ],
  "repo_path": "/Users/user/projects/myapp"
}
```

**Parameters**:
- `file_paths` (array, required): List of file paths relative to repo_path
- `repo_path` (string, required): Absolute path to repository root

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "File indexing completed",
  "indexed_files": 3,
  "skipped_files": 0,
  "total_chunks": 45,
  "errors": []
}
```

**Use Cases**:
- Re-index after editing documentation
- Add newly created documentation files
- Fix indexing errors for specific files
- Selective indexing during development

**Example**:
```bash
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/index-files" \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["docs/api/new-endpoint.md", "README.md"],
    "repo_path": "/Users/user/projects/myapp"
  }'
```

---

### 3. Search Documentation

Perform semantic search across documentation using natural language queries.

**Endpoint**: `POST /api/documentation-rag/{project_id}/search`

**Request Body**:
```json
{
  "query": "how to configure authentication with JWT tokens",
  "limit": 20,
  "min_similarity": 0.5,
  "doc_type": null
}
```

**Parameters**:
- `query` (string, required): Natural language search query
- `limit` (integer, optional): Maximum results to return (default: 20, max: 100)
- `min_similarity` (float, optional): Minimum similarity score 0-1 (default: 0.0)
- `doc_type` (string, optional): Filter by document type - "markdown", "readme", "api-doc", "guide", etc.

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "674a3f1e8b9c2d001f3e4a5b",
      "content": "## JWT Authentication\n\nTo configure JWT authentication, set the following environment variables...",
      "file_path": "docs/api/authentication.md",
      "title": "JWT Authentication",
      "headings": ["API Documentation", "Authentication", "JWT Authentication"],
      "doc_type": "markdown",
      "similarity": 0.89,
      "start_line": 42,
      "end_line": 68,
      "summary": "Configuration guide for JWT token-based authentication including environment variables and token generation."
    },
    {
      "id": "674a3f1e8b9c2d001f3e4a5c",
      "content": "Authentication uses JWT tokens with RS256 signing. Tokens expire after 24 hours...",
      "file_path": "docs/architecture/security.md",
      "title": "Security Architecture",
      "headings": ["Architecture", "Security", "Authentication"],
      "doc_type": "markdown",
      "similarity": 0.82,
      "start_line": 15,
      "end_line": 30,
      "summary": "Architectural overview of authentication system using JWT tokens with RS256 algorithm."
    }
  ],
  "query": "how to configure authentication with JWT tokens",
  "count": 2,
  "embedding_model": "voyage-3-large",
  "search_method": "vector_search"
}
```

**Response Fields**:
- `results`: Array of matching documentation chunks sorted by relevance
- `id`: Unique chunk identifier
- `content`: Documentation chunk content
- `file_path`: Relative path from project root
- `title`: Section title
- `headings`: Heading hierarchy
- `doc_type`: Type of document
- `similarity`: Cosine similarity score (0-1, higher is more relevant)
- `start_line`, `end_line`: Line numbers in original file
- `summary`: AI-generated summary of the chunk
- `embedding_model`: Model used for embeddings
- `search_method`: "vector_search" (MongoDB Atlas)

**Example**:
```bash
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database migration best practices",
    "limit": 10,
    "min_similarity": 0.6
  }'
```

---

### 4. Get Documentation Statistics

Retrieve statistics about indexed documentation.

**Endpoint**: `GET /api/documentation-rag/{project_id}/stats`

**Response** (200 OK):
```json
{
  "total_chunks": 1842,
  "total_files": 127,
  "doc_types": {
    "markdown": 1620,
    "readme": 85,
    "api-doc": 92,
    "guide": 45
  },
  "file_distribution": {
    "docs/api/": 542,
    "docs/architecture/": 318,
    "docs/guides/": 245,
    "docs/components/": 427,
    "root": 85
  },
  "embedding_model": "voyage-3-large",
  "embedding_dimensions": 1024,
  "collection_name": "documentation_chunks",
  "vector_index_name": "documentation_vector_idx",
  "oldest_indexed": "2025-11-15T10:00:00Z",
  "newest_indexed": "2025-11-27T14:30:00Z",
  "index_health": "healthy"
}
```

**Example**:
```bash
curl "http://localhost:3333/api/documentation-rag/proj_123/stats"
```

---

### 5. Reindex Documentation

Trigger full reindexing of all documentation (useful after major documentation reorganization).

**Endpoint**: `POST /api/documentation-rag/{project_id}/reindex`

**Request Body**:
```json
{
  "repo_path": "/Users/user/projects/myapp"
}
```

**Response** (200 OK):
```json
{
  "status": "reindexing_started",
  "deleted_chunks": 1842,
  "message": "Full reindexing in progress"
}
```

**Example**:
```bash
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/reindex" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/Users/user/projects/myapp"}'
```

---

### 6. Delete Documentation Chunks

Delete documentation chunks by file path or document type.

**Endpoint**: `DELETE /api/documentation-rag/{project_id}/chunks`

**Query Parameters**:
- `file_path` (string, optional): Delete chunks from specific file
- `doc_type` (string, optional): Delete chunks of specific document type

**Response** (200 OK):
```json
{
  "deleted_count": 42,
  "message": "Documentation chunks deleted successfully"
}
```

**Error Responses**:
- `400 Bad Request`: No deletion criteria provided

**Example**:
```bash
# Delete chunks from specific file
curl -X DELETE "http://localhost:3333/api/documentation-rag/proj_123/chunks?file_path=docs/old-guide.md"

# Delete all README chunks
curl -X DELETE "http://localhost:3333/api/documentation-rag/proj_123/chunks?doc_type=readme"
```

---

## Document Chunk Structure

Each documentation chunk stored in MongoDB has the following structure:

```json
{
  "_id": "ObjectId(...)",
  "project_id": "proj_123",
  "file_path": "docs/api/authentication.md",
  "content": "## JWT Authentication\n\nTo configure JWT...",
  "embedding": [0.012, -0.045, 0.089, ...],  // 1024 dimensions
  "start_line": 42,
  "end_line": 68,
  "doc_type": "markdown",
  "title": "JWT Authentication",
  "headings": ["API Documentation", "Authentication", "JWT Authentication"],
  "summary": "Configuration guide for JWT tokens...",
  "file_hash": "sha256:abc123...",
  "indexed_at": "2025-11-27T14:30:00Z",
  "metadata": {
    "file_size": 12456,
    "language": "markdown"
  }
}
```

## Smart Markdown Chunking

The Documentation Indexer uses intelligent chunking strategies:

### 1. Section-Based Chunking
- Chunks created at markdown heading boundaries (`##`, `###`, etc.)
- Preserves heading hierarchy in metadata
- Maintains context within sections

### 2. Size-Based Chunking
- Target chunk size: ~1000 characters
- Chunk overlap: 100 characters (for context preservation)
- Respects section boundaries when possible

### 3. Metadata Extraction
- **Title**: Extracted from nearest heading
- **Headings**: Full hierarchy (e.g., `["API", "Authentication", "JWT"]`)
- **Doc Type**: Detected from file location and content
- **Summary**: AI-generated chunk summary (optional)

## Automatic Indexing with Git Hook

Documentation is automatically re-indexed after every push to `main` branch via the `post-push-docs-rag` git hook.

**Hook Configuration** (`.claude/project-hooks/post-push-docs-rag.json`):
```json
{
  "name": "Documentation Indexer",
  "description": "Automatically re-index documentation after pushing to main",
  "event": "post-push",
  "script_path": "framework-assets/claude-hooks/post-push-docs-rag.sh",
  "enabled": true,
  "required_storage_mode": "mongodb",
  "conditions": {
    "branches": ["main", "master"]
  }
}
```

**What it does:**
1. Detects changed `.md` files in `docs/` directory
2. Calls `/api/documentation-rag/{project_id}/index-files` with changed files
3. Performs incremental indexing (only changed files)
4. Logs results to `.claude/logs/hooks/post-push-docs-rag.log`

**Disable automatic indexing:**
```bash
# Edit hook configuration
# Set "enabled": false
```

## Usage Patterns

### Pattern 1: Initial Documentation Setup

```bash
# First-time indexing of all documentation
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/index" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/project",
    "full_reindex": true
  }'
```

### Pattern 2: Incremental Updates (Automatic)

```bash
# Handled automatically by post-push hook
# Just push to main and hook will re-index changed docs
git add docs/new-guide.md
git commit -m "docs: Add new user guide"
git push origin main
# Hook automatically re-indexes docs/new-guide.md
```

### Pattern 3: Manual Incremental Update

```python
import requests

# After editing documentation files
response = requests.post(
    "http://localhost:3333/api/documentation-rag/proj_123/index-files",
    json={
        "file_paths": ["docs/api/new-endpoint.md", "README.md"],
        "repo_path": "/path/to/project"
    }
)
```

### Pattern 4: Semantic Documentation Search

```python
# Search for relevant documentation
response = requests.post(
    "http://localhost:3333/api/documentation-rag/proj_123/search",
    json={
        "query": "how to implement authentication with OAuth2",
        "limit": 5,
        "min_similarity": 0.7
    }
)

results = response.json()["results"]
for doc in results:
    print(f"File: {doc['file_path']} (relevance: {doc['similarity']:.2f})")
    print(f"Title: {doc['title']}")
    print(f"Content: {doc['content'][:200]}...\n")
```

### Pattern 5: Full Reindex After Major Reorganization

```bash
# After moving or restructuring documentation
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/reindex" \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/project"}'
```

## Performance Characteristics

### Indexing Performance
- **Full indexing**: ~5-30 seconds for medium projects (50-200 docs)
- **Incremental**: ~100-500ms per file
- **Batch size**: 100 chunks per embedding batch (Voyage AI rate limit: 2000 RPS)

### Search Performance
- **Query time**: ~20-50ms (sub-200ms guaranteed)
- **Embedding generation**: ~50-100ms (Voyage AI API)
- **Vector search**: ~10-30ms (MongoDB Atlas)

### Storage Efficiency
- **Chunk size**: ~1KB average
- **Embedding size**: 4KB (1024 floats × 4 bytes)
- **Total per chunk**: ~5KB
- **100 docs**: ~500KB storage

## MCP Tools Integration

The Documentation RAG API is integrated with MCP tools for Claude Code.

### Available MCP Tools

**`search_project_documentation`**
Search documentation using natural language:
```python
await mcp.call_tool("search_project_documentation", {
    "query": "database migration best practices",
    "limit": 10
})
```

**`index_documentation`**
Manually trigger documentation indexing:
```python
await mcp.call_tool("index_documentation", {
    "full_reindex": false
})
```

## Error Handling

All endpoints return standard HTTP error responses:

**503 Service Unavailable** - Missing dependencies:
```json
{
  "error": "MongoDB not connected. Configure MongoDB Atlas first.",
  "code": "MONGODB_NOT_CONNECTED"
}
```

**503 Service Unavailable** - Missing API key:
```json
{
  "error": "VOYAGE_AI_API_KEY not configured. Required for documentation embedding.",
  "code": "MISSING_API_KEY"
}
```

**500 Internal Server Error** - Indexing failure:
```json
{
  "error": "Failed to index documentation",
  "code": "INDEXING_ERROR",
  "details": "Voyage AI API timeout after 30 seconds"
}
```

## Best Practices

1. **Incremental Indexing**: Let the post-push hook handle automatic updates - don't manually reindex unless needed

2. **Specific Queries**: Use detailed search queries for better results ("JWT token configuration" vs "authentication")

3. **Similarity Threshold**: Set `min_similarity` to 0.6-0.7 to filter out low-quality matches

4. **Monitor Stats**: Check `/stats` endpoint periodically to ensure indexing is working

5. **Organize Documentation**: Well-structured documentation with clear headings improves chunking quality

6. **Full Reindex Sparingly**: Only use full reindex after major documentation reorganization

7. **Clean Up Deleted Files**: Use DELETE endpoint to remove chunks from deleted documentation

## Comparison: Code RAG vs Documentation RAG

| Feature | Codebase RAG | Documentation RAG |
|---------|--------------|-------------------|
| **Purpose** | Search source code | Search documentation |
| **File Types** | `.py`, `.ts`, `.js`, etc. | `.md`, `.txt`, `.rst`, etc. |
| **Chunking** | Function/class-based | Section/heading-based |
| **Use Case** | Find code implementations | Find usage guides |
| **Indexing** | Manual (`index_codebase`) | Automatic (post-push hook) |
| **Collection** | `codebase_chunks` | `documentation_chunks` |
| **Vector Index** | `codebase_vector_idx` | `documentation_vector_idx` |

## Migration from Local Storage

Documentation RAG is only available with MongoDB storage mode. To migrate:

```bash
# Use the migration CLI tool
python -m claudetask.migrations.migrate_to_mongodb \
  --project-id=proj_123 \
  --target-mode=mongodb

# Then index documentation
curl -X POST "http://localhost:3333/api/documentation-rag/proj_123/index" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/project",
    "full_reindex": true
  }'
```

## See Also

- [Codebase RAG API](./codebase-rag.md) - Semantic code search
- [Memory API](./memory.md) - Conversation memory with RAG
- [MongoDB Atlas Storage](../../features/mongodb-atlas-storage.md) - Cloud storage setup
- [Cloud Storage API](./cloud-storage.md) - MongoDB and Voyage AI configuration

---

**API Version**: 1.0
**Storage Backend**: MongoDB Atlas + Vector Search
**Embedding Model**: voyage-3-large (1024d)
**Requires**: MongoDB storage mode
