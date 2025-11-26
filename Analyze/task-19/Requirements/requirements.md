# Requirements: MongoDB Atlas Integration for RAG and Database Storage

**Task ID:** 19  
**Task Title:** Mongo RAG - MongoDB Atlas with Vector Search  
**Date Created:** 2025-11-26  
**Complexity:** COMPLEX  

## Executive Summary

Add MongoDB Atlas as an optional cloud-based storage backend for the ClaudeTask Framework, allowing users to choose between:
- **Local Storage**: SQLite + ChromaDB with all-MiniLM-L6-v2 embeddings (384 dimensions)
- **Cloud Storage**: MongoDB Atlas + Vector Search with voyage-3-large embeddings (1024 dimensions)

**Business Value:**
- Cloud-based data persistence with automatic backups
- Centralized data access across multiple development machines
- Enhanced vector search capabilities (1024d vs 384d embeddings)
- Production-ready scalability for growing projects with 100k+ conversations
- Reduced local disk usage (ChromaDB can grow to GB-scale)
- Collaboration-friendly: shared database across teams

**Scope:**
- Backend database abstraction layer using Repository pattern
- RAG service refactoring for dual storage backends
- MongoDB Atlas integration with Motor (async driver)
- voyage-3-large embedding integration via Voyage AI API
- UI configuration toggle in Project Setup
- Data migration utilities (local → cloud)
- Backward compatibility with existing local storage

---

## User Stories

### US-1: Storage Mode Selection
**As a** Framework Administrator  
**I want** to select storage mode (Local or Cloud) during project creation  
**So that** I can choose between local development and cloud-based persistence

**Acceptance Criteria:**
- Storage mode selection in Project Setup UI (new field after "Project Mode")
- Two radio options: "Local Storage (SQLite + ChromaDB)" and "Cloud Storage (MongoDB Atlas)"
- Default: Local Storage
- Mode saved in `project_settings.storage_mode` column
- Mode immutable after creation (migration tool required to change)
- Tooltip explains costs, requirements, benefits of each mode
- Disabled if MongoDB connection not configured globally

### US-2: MongoDB Atlas Global Configuration
**As a** Framework Administrator  
**I want** to configure MongoDB Atlas credentials in global settings  
**So that** all cloud storage projects can connect to my database

**Acceptance Criteria:**
- New settings page: "Cloud Storage Configuration"
- Fields: Connection String, Database Name, Voyage AI API Key
- Connection string validation: `mongodb+srv://` or `mongodb://` format
- "Test Connection" button verifies credentials before saving
- Secure storage: environment variables (`.env` file) or encrypted config
- TLS/SSL enforced by default
- Voyage AI API key required for voyage-3-large embeddings
- Configuration persists across restarts
- Clear error messages for connection failures

### US-3: Vector Search with voyage-3-large
**As a** Developer using RAG  
**I want** semantic search with voyage-3-large embeddings (1024d)  
**So that** I get higher quality results than all-MiniLM-L6-v2 (384d)

**Acceptance Criteria:**
- voyage-3-large embeddings generated for all conversations
- MongoDB Atlas Vector Search index auto-created on `conversations.embedding`
- Cosine similarity metric for vector comparisons
- Search supports metadata filters: `project_id`, `session_id`, `task_id`, date range
- Returns top-k results with similarity scores
- Pagination via limit/offset parameters
- Performance: search completes in <500ms for 10k+ documents
- Fallback to non-vector search if index not ready

### US-4: Data Migration (Local → Cloud)
**As a** Framework Administrator  
**I want** to migrate existing project from local to cloud storage  
**So that** I can transition without data loss

**Acceptance Criteria:**
- CLI migration tool: `python -m claudetask.migrations.migrate_to_mongodb --project-id=<id>`
- Migrates all tables: projects, tasks, task_history, conversations, summaries
- Conversation embeddings regenerated with voyage-3-large
- Progress bar showing % complete
- Batch processing (100 records/batch) for large datasets
- Dry-run mode: `--dry-run` flag previews without committing
- Rollback on failure (atomic operations per batch)
- Data validation: record counts, embedding dimensions
- Original local data preserved until validation succeeds
- Estimated time displayed before migration starts

### US-5: Backward Compatibility
**As a** Developer using local storage  
**I want** existing local storage to work unchanged  
**So that** I'm not forced to use cloud storage

**Acceptance Criteria:**
- Local storage remains default and fully functional
- No MongoDB dependencies when using local mode (optional imports)
- Existing projects work without configuration changes
- ChromaDB collection management unchanged
- all-MiniLM-L6-v2 model continues working
- Local and cloud projects coexist in same installation
- No performance degradation for local storage

### US-6: Transparent Database Abstraction
**As a** Backend Developer  
**I want** unified database interface abstracting storage  
**So that** business logic doesn't care about MongoDB vs SQLite

**Acceptance Criteria:**
- Repository pattern: `ProjectRepository`, `TaskRepository`, `ConversationRepository`
- Single CRUD interface for all entities
- Storage mode determined from `project_settings.storage_mode`
- No `if storage_mode == "mongodb"` in business logic
- MCP tools work identically for both modes
- FastAPI endpoints unchanged
- Dependency injection for repository implementations
- Unit tests mock repository interfaces

---

## Functional Requirements

### FR-1: Storage Mode Management
- **FR-1.1:** Project creation includes storage mode selection (UI field)
- **FR-1.2:** Storage mode stored in `project_settings.storage_mode` (values: "local", "mongodb")
- **FR-1.3:** Storage mode immutable after creation (data integrity)
- **FR-1.4:** Migration tool for manual storage mode conversion

### FR-2: MongoDB Atlas Integration
- **FR-2.1:** Connection string validated and stored in `.env` file
- **FR-2.2:** Connection pool with configurable size (default: 10 connections)
- **FR-2.3:** Automatic reconnection on transient failures (3 retries, exponential backoff)
- **FR-2.4:** Health check endpoint: `GET /api/health/mongodb`
- **FR-2.5:** Support for serverless and dedicated MongoDB Atlas clusters

### FR-3: Database Schema Mapping
- **FR-3.1:** SQLite tables mapped to MongoDB collections
- **FR-3.2:** Foreign key relationships via references (`project_id` field)
- **FR-3.3:** AUTOINCREMENT replaced with MongoDB ObjectId or sequence
- **FR-3.4:** CASCADE DELETE implemented in application layer
- **FR-3.5:** Indexes created on frequently queried fields

### FR-4: Vector Search Implementation
- **FR-4.1:** Vector Search index created on `conversations.embedding`
- **FR-4.2:** voyage-3-large API integration (Voyage AI SDK)
- **FR-4.3:** Embedding generation batched (max 100 texts/batch)
- **FR-4.4:** Metadata filters: project_id, session_id, task_id, timestamp range
- **FR-4.5:** Similarity threshold configurable (default: 0.7)
- **FR-4.6:** Pagination support (limit/offset)

### FR-5: MCP Tools Compatibility
- **FR-5.1:** `mcp__claudetask__get_project_memory_context` works for both modes
- **FR-5.2:** `mcp__claudetask__search_project_memories` uses appropriate backend
- **FR-5.3:** `mcp__claudetask__save_conversation_message` generates embeddings with correct model
- **FR-5.4:** `mcp__claudetask__update_project_summary` updates MongoDB or SQLite
- **FR-5.5:** All MCP tools return identical data structures

### FR-6: Data Migration
- **FR-6.1:** CLI command: `python -m claudetask.migrations.migrate_to_mongodb`
- **FR-6.2:** Batch processing (100 records/batch) with progress bar
- **FR-6.3:** Dry-run mode: `--dry-run` flag
- **FR-6.4:** Rollback on failure (per-batch atomic operations)
- **FR-6.5:** Data validation after migration

---

## Definition of Done (DoD)

### Functionality DoD
- [ ] Storage mode toggle working in Project Setup UI
- [ ] MongoDB Atlas connection configuration functional
- [ ] Test connection validates MongoDB credentials
- [ ] All SQLite tables have MongoDB collection equivalents
- [ ] Vector Search returns relevant results
- [ ] voyage-3-large embeddings generated correctly
- [ ] Migration utility completes successfully for test project
- [ ] Local storage unchanged and fully functional
- [ ] All MCP tools work with both storage modes

### Code Quality DoD
- [ ] Repository pattern implemented for database abstraction
- [ ] No hardcoded storage mode checks in business logic
- [ ] Environment variables for MongoDB credentials (no secrets in code)
- [ ] Connection pooling configured
- [ ] Error handling for connection failures
- [ ] Logging for database operations (debug level)
- [ ] Type hints for all new classes and methods
- [ ] Docstrings for public interfaces
- [ ] Code follows existing patterns (FastAPI async, Pydantic models)

### Testing DoD
- [ ] Unit tests for MongoDB repository implementations
- [ ] Integration tests for MongoDB Atlas connectivity
- [ ] Integration tests for Vector Search queries
- [ ] Migration tests with sample dataset (1000 conversations)
- [ ] Tests for both storage modes (local and cloud)
- [ ] Error scenario tests (connection failure, invalid credentials)
- [ ] Performance tests for large datasets (10k+ conversations)
- [ ] End-to-end tests for MCP tools with both backends

### Documentation DoD
- [ ] Architecture documentation updated with Repository pattern
- [ ] MongoDB schema design documented (collections, indexes)
- [ ] Configuration guide for MongoDB Atlas setup
- [ ] Migration guide (local → cloud)
- [ ] voyage-3-large API usage documented
- [ ] Troubleshooting guide for connection issues
- [ ] Performance comparison: ChromaDB vs MongoDB Vector Search
- [ ] API documentation for repository interfaces

### Security DoD
- [ ] MongoDB credentials not in database or code
- [ ] `.env` file for environment variables
- [ ] TLS/SSL enforced for MongoDB connections
- [ ] Connection string validation (format, required fields)
- [ ] No credentials in logs or error messages
- [ ] Voyage AI API key securely stored

### Deployment DoD
- [ ] MongoDB Atlas setup guide (M0 Free Tier instructions)
- [ ] Environment variable configuration documented
- [ ] Database indexes created automatically on first run
- [ ] Vector Search index creation automated
- [ ] Backward compatibility verified with existing projects
- [ ] Migration path documented for production

---

## Non-Functional Requirements

### Performance
- MongoDB queries complete in <200ms for typical operations
- Vector Search returns results in <500ms for 10k+ documents
- Embedding generation batched (100 texts/batch) to minimize API calls
- Connection pool prevents exhaustion (max 10 connections)
- Index creation for frequently queried fields

### Scalability
- Support for projects with 100k+ conversation messages
- Vector Search handles up to 1M embeddings per project
- Concurrent access from multiple Claude sessions
- MongoDB Atlas auto-scaling for growing datasets

### Reliability
- Automatic retry on transient failures (3 retries, exponential backoff)
- Graceful degradation if voyage-3-large API unavailable
- Data consistency with transactions where necessary
- No data loss during migration

### Security
- All MongoDB connections use TLS 1.2+
- Credentials never logged or displayed
- IP whitelist for MongoDB Atlas clusters
- Role-based access control (RBAC) for MongoDB users

### Maintainability
- Clear separation between storage implementations
- Single interface for database operations
- Easy to add new backends (e.g., PostgreSQL + pgvector)
- Configuration-driven storage selection

---

## Dependencies

### External Services
- **MongoDB Atlas:** Cloud database (M0 Free Tier or higher)
- **Voyage AI API:** voyage-3-large embeddings (API key required)

### Python Libraries
- `pymongo>=4.6.0`: MongoDB sync driver
- `motor>=3.3.0`: Async MongoDB driver for FastAPI
- `voyageai>=0.2.0`: Voyage AI SDK
- `python-dotenv>=1.0.0`: Environment variable management

### Infrastructure
- MongoDB Atlas cluster (M0 Free Tier: 512MB, 100 connections)
- Voyage AI API key (voyageai.com)
- Network access: IP whitelist in MongoDB Atlas

---

## Technical Constraints

### Database Constraints
- MongoDB Atlas M0 Free Tier: 512MB storage, 100 max connections
- Vector Search requires M10+ cluster for production
- voyage-3-large API rate limits: 1000 req/min (verify current limits)

### Migration Constraints
- Large datasets require hours for migration (10k messages = ~30 min)
- Embedding regeneration CPU-intensive (voyage-3-large API)
- Cannot migrate project while in active use (requires downtime)

### Backward Compatibility
- Must not break existing local storage projects
- Local storage remains default
- No forced migration

---

## Success Metrics

### Adoption
- 20% of new projects use MongoDB Atlas (3 months post-launch)
- At least 3 successful production migrations (6 months)

### Performance
- Vector Search latency <500ms (95th percentile)
- MongoDB queries equal to or faster than SQLite
- voyage-3-large relevance improvement: >15% (measured via user feedback)

### Reliability
- Zero data loss during migrations
- 99.9% MongoDB Atlas uptime
- <1% migration failure rate

---

## Open Questions

1. **voyage-3-large Costs:** Expected costs for 100k+ messages? Document cost estimates and caching strategies
2. **Hybrid Mode:** Support SQLite for relational + MongoDB only for RAG? Reduces storage costs
3. **Migration Downtime:** Can we support live migration with zero downtime? Dual-write during transition?
4. **Vector Index:** Automatic or manual index creation? Large indexes take hours to build
5. **Embedding Model Switching:** Allow users to switch models without full reindexing?

---

## Active Task Conflicts

**No conflicts detected:** Only task-19 worktree exists currently.

---

## References

- MongoDB Atlas: https://www.mongodb.com/docs/atlas/
- MongoDB Vector Search: https://www.mongodb.com/docs/atlas/atlas-vector-search/
- Voyage AI API: https://docs.voyageai.com/
- ChromaDB: https://docs.trychroma.com/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

**Document Status:** Final  
**Last Updated:** 2025-11-26  
**Total Pages:** ~3 pages
