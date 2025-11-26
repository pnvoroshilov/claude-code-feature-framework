# Acceptance Criteria: MongoDB Atlas Integration

**Task ID:** 19  
**Last Updated:** 2025-11-26

## Overview

Detailed acceptance criteria for MongoDB Atlas integration with Vector Search, covering all user stories and scenarios for successful implementation.

---

## US-1: Storage Mode Selection

### AC-1.1: Storage Mode UI in Project Setup
**GIVEN** user is creating new project  
**WHEN** user reaches Project Setup screen  
**THEN**
- "Storage Mode" field visible after "Project Mode" selection
- Two radio options: "Local Storage (SQLite + ChromaDB)" and "Cloud Storage (MongoDB Atlas)"
- "Local Storage" selected by default
- Tooltip icon with explanation of each mode
- If MongoDB not configured globally, "Cloud Storage" option disabled with message

**AND WHEN** user selects "Cloud Storage"  
**THEN**
- No additional fields required (uses global MongoDB configuration)
- Proceed button enabled if MongoDB connection exists
- Warning shown: "Requires MongoDB Atlas connection and Voyage AI API key"

### AC-1.2: Storage Mode Persistence
**GIVEN** user creates project with storage mode  
**WHEN** project created successfully  
**THEN**
- `project_settings.storage_mode` column contains "local" or "mongodb"
- Storage mode visible in project details (read-only)
- Cannot change mode via UI after creation
- Migration tool link shown in project settings

### AC-1.3: Storage Mode Immutability
**GIVEN** existing project with storage mode  
**WHEN** user tries to edit project settings  
**THEN**
- Storage mode field displayed as read-only label
- Message: "Storage mode cannot be changed after creation. Use migration tool if needed."
- Link to migration documentation

---

## US-2: MongoDB Atlas Global Configuration

### AC-2.1: Configuration UI
**GIVEN** user navigates to Settings → Cloud Storage  
**WHEN** configuration page loads  
**THEN**
- Form with three fields:
  - MongoDB Connection String (password input, placeholder: `mongodb+srv://...`)
  - Database Name (text input, default: `claudetask`)
  - Voyage AI API Key (password input, placeholder: `vo-...`)
- "Test Connection" button (primary action)
- "Save Configuration" button (disabled until test succeeds)
- Current status indicator (Connected/Disconnected)

### AC-2.2: Connection String Validation
**GIVEN** user enters connection string  
**WHEN** user clicks "Test Connection"  
**THEN** (validation occurs)
- Format validated: starts with `mongodb://` or `mongodb+srv://`
- Contains authentication credentials
- Contains cluster URL
- Does not contain plain passwords (should be URL-encoded)

**IF validation fails**:
- Error message: "Invalid connection string format. Expected mongodb+srv://..."
- Save button remains disabled

**IF validation succeeds**:
- API call: `POST /api/settings/cloud-storage/test`
- Loading indicator shown
- On success: "Connection successful!" (green alert)
- On failure: Specific error (auth failure, network error, etc.)

### AC-2.3: Secure Credential Storage
**GIVEN** user saves configuration  
**WHEN** "Save Configuration" clicked  
**THEN**
- Credentials written to `.env` file (not database)
- `.env` file entries:
  ```
  MONGODB_CONNECTION_STRING=mongodb+srv://...
  MONGODB_DATABASE_NAME=claudetask
  VOYAGE_AI_API_KEY=vo-...
  ```
- `.env` added to `.gitignore` if not already
- Success message: "Configuration saved. Restart required."
- Configuration persists across restarts

### AC-2.4: Test Connection Behavior
**GIVEN** user clicks "Test Connection"  
**WHEN** backend tests connection  
**THEN**
- Validates TLS/SSL enabled
- Attempts to connect with credentials
- Tests write permissions (creates test collection)
- Tests Voyage AI API with dummy request
- Returns detailed status:
  ```json
  {
    "mongodb_connected": true,
    "voyage_ai_valid": true,
    "database_writable": true,
    "error": null
  }
  ```

**Error scenarios**:
- "Invalid credentials" → Authentication error
- "Network unreachable" → Network/firewall issue
- "IP not whitelisted" → MongoDB Atlas Network Access issue
- "Voyage AI API key invalid" → API key problem

---

## US-3: Vector Search with voyage-3-large

### AC-3.1: Embedding Generation
**GIVEN** new conversation message saved  
**WHEN** project uses MongoDB storage  
**THEN**
- Message content sent to Voyage AI API
- Batch processing: queue messages, send 100 at a time
- Embedding returned: array of 1024 floats
- Embedding saved in `conversations.embedding` field
- If API fails: log error, retry 3 times, then save without embedding

### AC-3.2: Vector Search Index Creation
**GIVEN** project uses MongoDB storage  
**WHEN** first conversation saved  
**THEN**
- Vector Search index created automatically:
  ```json
  {
    "type": "vectorSearch",
    "fields": [{
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    }]
  }
  ```
- Index name: `vector_search_idx`
- Index status: "In Progress" (can take minutes for large collections)
- Search falls back to metadata-only until index ready

### AC-3.3: Semantic Search Query
**GIVEN** user executes `mcp__claudetask__search_project_memories`  
**WHEN** search query processed  
**THEN**
- Query text converted to voyage-3-large embedding (1024d)
- MongoDB Vector Search query:
  ```python
  {
    "$vectorSearch": {
      "index": "vector_search_idx",
      "path": "embedding",
      "queryVector": [embedding array],
      "numCandidates": 100,
      "limit": 20
    }
  }
  ```
- Results include similarity scores (0.0 to 1.0)
- Results filtered by project_id automatically
- Additional metadata filters applied (session_id, task_id, date range)

### AC-3.4: Search Performance
**GIVEN** collection with 10,000 conversations  
**WHEN** vector search executes  
**THEN**
- Search completes in <500ms (95th percentile)
- Returns top-20 results by default
- Supports pagination: `limit` and `skip` parameters
- Falls back to non-vector search if index unavailable

---

## US-4: Data Migration (Local → Cloud)

### AC-4.1: Migration CLI Invocation
**GIVEN** project exists with local storage  
**WHEN** admin runs: `python -m claudetask.migrations.migrate_to_mongodb --project-id=abc123`  
**THEN**
- Migration script starts
- Displays project info: name, path, message count
- Estimates time: ~30 min for 10k messages
- Asks for confirmation: "Proceed with migration? (y/n)"

### AC-4.2: Dry-Run Mode
**GIVEN** admin runs with `--dry-run` flag  
**WHEN** migration executes  
**THEN**
- Analyzes project data without changing anything
- Reports what would be migrated:
  ```
  Projects: 1
  Tasks: 15
  Conversations: 8,543
  Embeddings to regenerate: 8,543
  Estimated time: 28 minutes
  ```
- No data written to MongoDB
- No local data modified

### AC-4.3: Batch Processing
**GIVEN** migration in progress  
**WHEN** processing conversations  
**THEN**
- Conversations migrated in batches of 100
- Progress bar shows: `[=====>    ] 45% (3,845 / 8,543)`
- Each batch:
  1. Fetch 100 conversations from SQLite
  2. Generate voyage-3-large embeddings (API call)
  3. Insert batch into MongoDB
  4. Update progress
- If batch fails: log error, rollback batch, continue with next

### AC-4.4: Rollback on Failure
**GIVEN** migration fails mid-process  
**WHEN** error occurs (e.g., MongoDB connection lost)  
**THEN**
- Migration stops immediately
- All changes to MongoDB rolled back (use transactions)
- Local SQLite data unchanged
- Error message: "Migration failed at batch 34/85. Error: {details}"
- User can retry migration

### AC-4.5: Data Validation
**GIVEN** migration completes  
**WHEN** validation phase runs  
**THEN**
- Compares record counts:
  - Projects: SQLite = MongoDB
  - Tasks: SQLite = MongoDB
  - Conversations: SQLite = MongoDB
- Verifies embedding dimensions:
  - All embeddings are 1024-dimensional
  - No null embeddings (except where API failed)
- Reports validation result:
  ```
  ✓ Projects: 1 / 1
  ✓ Tasks: 15 / 15
  ✓ Conversations: 8,543 / 8,543
  ✓ Embeddings: 8,539 / 8,543 (4 failed)
  Migration successful!
  ```

### AC-4.6: Post-Migration Cleanup
**GIVEN** migration validated successfully  
**WHEN** user confirms cleanup  
**THEN**
- `project_settings.storage_mode` updated to "mongodb"
- Local SQLite data archived (not deleted)
- ChromaDB collection preserved (for rollback if needed)
- Message: "Migration complete. Local data preserved in backup."

---

## US-5: Backward Compatibility

### AC-5.1: Existing Local Projects Unchanged
**GIVEN** existing project with local storage  
**WHEN** framework starts after MongoDB integration  
**THEN**
- Project loads normally
- No MongoDB connection attempted
- ChromaDB used for vector search
- all-MiniLM-L6-v2 embeddings continue working
- No performance degradation
- No configuration changes required

### AC-5.2: New Local Projects
**GIVEN** user creates new project  
**WHEN** "Local Storage" selected (default)  
**THEN**
- Project initialized with SQLite
- ChromaDB collection created
- all-MiniLM-L6-v2 embeddings used
- No MongoDB dependencies loaded
- Works offline (no API calls)

### AC-5.3: Mixed Project Coexistence
**GIVEN** multiple projects: some local, some cloud  
**WHEN** framework running  
**THEN**
- Each project uses its configured storage mode
- Local projects use SQLite + ChromaDB
- Cloud projects use MongoDB Atlas + Vector Search
- No interference between projects
- API endpoints work for both types

---

## US-6: Transparent Database Abstraction

### AC-6.1: Repository Interface
**GIVEN** backend code accessing database  
**WHEN** executing CRUD operations  
**THEN**
- Business logic uses repository interfaces:
  ```python
  project_repo = get_project_repository()  # Factory based on storage_mode
  project = await project_repo.get_by_id(project_id)
  ```
- No `if storage_mode == "mongodb"` in business logic
- Repository implementation determined at runtime
- SQLite repository for local mode
- MongoDB repository for cloud mode

### AC-6.2: MCP Tools Compatibility
**GIVEN** MCP tool called  
**WHEN** tool executes  
**THEN**
- Tool retrieves project's storage mode
- Uses appropriate repository implementation
- Returns identical data structure regardless of backend
- Example: `get_project_memory_context` returns same JSON for both modes

**Example data structure**:
```json
{
  "summary": "...",
  "recent_messages": [...],
  "rag_results": [...]
}
```
(Same format for SQLite and MongoDB backends)

### AC-6.3: Dependency Injection
**GIVEN** FastAPI endpoint  
**WHEN** endpoint function called  
**THEN**
- Repository injected via dependency:
  ```python
  @app.get("/api/projects/{id}")
  async def get_project(
      id: str,
      repo: ProjectRepository = Depends(get_project_repository)
  ):
      return await repo.get_by_id(id)
  ```
- Factory function determines implementation
- Endpoint code unchanged

---

## Cross-Cutting Acceptance Criteria

### Performance
- **AC-P1:** MongoDB queries complete in <200ms for standard operations
- **AC-P2:** Vector Search returns results in <500ms for 10k+ documents
- **AC-P3:** Embedding generation batched (100 texts/call)
- **AC-P4:** Connection pool prevents exhaustion (max 10 connections)

### Security
- **AC-S1:** MongoDB credentials never in database or logs
- **AC-S2:** TLS/SSL enforced for all MongoDB connections
- **AC-S3:** Connection string validated for security (no plain passwords)
- **AC-S4:** Voyage AI API key stored securely in `.env`

### Reliability
- **AC-R1:** Auto-retry on transient MongoDB failures (3 retries, exponential backoff)
- **AC-R2:** Graceful degradation if Voyage AI API unavailable
- **AC-R3:** Data validation after every migration
- **AC-R4:** Zero data loss during migrations

### Usability
- **AC-U1:** Clear error messages for connection issues
- **AC-U2:** Progress indicators for long-running operations (migration)
- **AC-U3:** Help tooltips explaining storage modes
- **AC-U4:** Test connection before allowing project creation

---

## Edge Cases

### EC-1: MongoDB Connection Lost During Operation
**GIVEN** project using MongoDB storage  
**WHEN** MongoDB connection lost mid-operation  
**THEN**
- Error caught and logged
- User sees: "Cloud storage temporarily unavailable. Retrying..."
- Auto-retry 3 times with exponential backoff
- If retry fails: show error, suggest checking connection
- No data loss or corruption

### EC-2: Voyage AI API Rate Limit Exceeded
**GIVEN** migration generating embeddings  
**WHEN** Voyage AI rate limit hit  
**THEN**
- API returns 429 Too Many Requests
- Migration pauses for 60 seconds
- Retries request
- Progress bar shows: "Rate limit reached. Waiting..."
- Migration continues after pause

### EC-3: Very Large Project Migration (100k+ messages)
**GIVEN** project with 150,000 conversations  
**WHEN** migration starts  
**THEN**
- Estimated time shown: ~8 hours
- Migration runs in background (resumable)
- Progress saved every 1000 records
- Can pause and resume migration
- Memory usage stays under 1GB

### EC-4: Concurrent Access During Migration
**GIVEN** migration in progress  
**WHEN** user tries to use project  
**THEN**
- Read-only mode during migration
- User sees: "Project migrating to cloud storage. Read-only mode."
- Can view data from SQLite (source)
- Cannot create new conversations
- Migration continues uninterrupted

### EC-5: Invalid voyage-3-large API Response
**GIVEN** embedding generation  
**WHEN** Voyage AI returns malformed response  
**THEN**
- Error logged with request/response details
- Conversation saved without embedding
- User notified: "Embedding generation failed for 1 message"
- Can retry embedding generation later

---

## Testing Checklist

### Manual Testing
- [ ] Create project with Local Storage mode
- [ ] Create project with Cloud Storage mode
- [ ] Configure MongoDB Atlas connection
- [ ] Test MongoDB connection (success and failure cases)
- [ ] Generate voyage-3-large embeddings
- [ ] Execute vector search query
- [ ] Migrate project from local to cloud (dry-run)
- [ ] Migrate project from local to cloud (actual)
- [ ] Verify data integrity after migration
- [ ] Test MCP tools with both storage modes
- [ ] Test error scenarios (connection loss, API failure)
- [ ] Test edge cases (large datasets, rate limits)

### Automated Testing
- [ ] Unit tests for repository implementations
- [ ] Integration tests for MongoDB connectivity
- [ ] Integration tests for Vector Search
- [ ] Migration tests with sample data
- [ ] Performance tests (query latency, search speed)
- [ ] Error handling tests
- [ ] Data validation tests

---

**Document Status:** Final  
**Total Scenarios:** 40+  
**Critical Paths:** 6 (Storage selection, Configuration, Vector Search, Migration, Compatibility, Abstraction)  
**Edge Cases:** 5  
**Last Updated:** 2025-11-26  
**Total Pages:** ~3 pages
