# Architecture Decision Records (ADR): MongoDB Atlas Integration

**Task ID:** 19
**Last Updated:** 2025-11-26

---

## ADR-001: Use Repository Pattern for Database Abstraction

**Status:** Accepted

**Context:**
ClaudeTask Framework currently uses SQLite with SQLAlchemy ORM directly in business logic. Adding MongoDB Atlas as an optional backend requires abstracting database access to support both storage modes without duplicating business logic.

**Decision Drivers:**
- Need to support two different database technologies (SQLite and MongoDB)
- Business logic should not depend on specific database implementation
- Must maintain backward compatibility with existing local storage
- Code maintainability and testability
- SOLID principles (Dependency Inversion)

**Options Considered:**

### Option 1: Repository Pattern
**Approach**: Abstract database operations behind repository interfaces. Implement SQLite and MongoDB versions separately.

**Pros:**
- Clean separation between business logic and data access
- Easily testable (can mock repositories)
- Supports multiple storage backends
- SOLID compliant (Dependency Inversion Principle)
- Industry standard pattern for data access abstraction

**Cons:**
- Requires refactoring existing database access code
- Additional abstraction layer adds some complexity
- More files and classes to maintain

**Cost**: High upfront (16-24 hours), low ongoing maintenance

### Option 2: Adapter Pattern with Single Service Layer
**Approach**: Create database adapters that convert between MongoDB documents and SQLAlchemy models.

**Pros:**
- Less refactoring of existing code
- Single service layer handles business logic

**Cons:**
- Tight coupling between adapters and ORM models
- Complex conversion logic between document and relational models
- Harder to test in isolation
- Violates Single Responsibility Principle

**Cost**: Medium upfront (10-15 hours), high ongoing maintenance

### Option 3: Conditional Logic in Business Layer
**Approach**: Use `if storage_mode == "mongodb"` throughout business logic.

**Pros:**
- Quick to implement
- No abstraction layer needed

**Cons:**
- Violates Open/Closed Principle
- Business logic polluted with infrastructure concerns
- Hard to test
- Maintenance nightmare as storage modes grow
- Code duplication inevitable

**Cost**: Low upfront (5-8 hours), very high ongoing maintenance

**Decision:** **Option 1 - Repository Pattern**

**Rationale:**
- Clean Architecture principle: Infrastructure depends on domain, not vice versa
- SOLID principles: Dependency Inversion (depend on abstractions)
- Future-proof: Easy to add PostgreSQL, Firestore, etc.
- Testability: Can mock repositories in unit tests
- Industry standard: Well-known pattern with established best practices

**Consequences:**

**Positive:**
- Business logic independent of storage implementation
- Easy to add new storage backends
- Highly testable with dependency injection
- Clear separation of concerns

**Negative:**
- Requires refactoring existing database access code
- More files and classes to manage
- Learning curve for developers unfamiliar with Repository pattern

**Implementation Notes:**
- Use ABC (Abstract Base Class) for repository interfaces
- Implement SQLite repositories first (refactor existing code)
- Implement MongoDB repositories second
- Use Factory pattern to instantiate correct repository based on storage mode

---

## ADR-002: Use voyage-3-large for MongoDB Vector Search

**Status:** Accepted

**Context:**
Current RAG system uses `all-MiniLM-L6-v2` model (384-dimensional embeddings) with ChromaDB. MongoDB Atlas Vector Search requires choosing an embedding model. Need to decide whether to keep same model or upgrade.

**Decision Drivers:**
- Embedding quality impacts search relevance
- MongoDB Atlas Vector Search optimized for higher-dimensional vectors
- API costs for embedding generation
- Migration effort (must regenerate all embeddings if changing models)

**Options Considered:**

### Option 1: Keep all-MiniLM-L6-v2 (384d)
**Pros:**
- No model switching complexity
- Free (runs locally via SentenceTransformers)
- Fast embedding generation
- Existing embeddings can be reused

**Cons:**
- Lower quality compared to modern models
- 384 dimensions less effective for MongoDB Vector Search (optimized for 512+)
- Misses opportunity to improve search quality
- Not leveraging cloud infrastructure advantage

**Cost**: Free, but lower search quality

### Option 2: Use voyage-3-large (1024d)
**Pros:**
- State-of-the-art embedding quality (better than OpenAI ada-002)
- 1024 dimensions optimal for MongoDB Vector Search
- Designed specifically for RAG use cases
- Justifies using cloud storage (better search as value-add)

**Cons:**
- API costs: $0.10 per 1M tokens (but free tier: 1M tokens/month)
- Requires Voyage AI API key
- Migration requires regenerating all embeddings
- Network latency for API calls

**Cost**: $0-$0.50 for typical projects (most fit in free tier)

### Option 3: Use OpenAI text-embedding-ada-002 (1536d)
**Pros:**
- Excellent quality
- OpenAI ecosystem integration

**Cons:**
- More expensive than Voyage AI ($0.13 per 1M tokens)
- Larger dimension (1536d) means more storage
- Not specialized for RAG like voyage-3-large

**Cost**: ~$0.65 for typical projects

**Decision:** **Option 2 - voyage-3-large**

**Rationale:**
- Superior embedding quality justifies cloud storage
- 1024 dimensions optimal for MongoDB Vector Search
- Free tier (1M tokens/month) covers most projects
- Voyage AI designed specifically for RAG/semantic search use cases
- Cost-effective compared to OpenAI
- Provides tangible improvement over local storage (better search quality)

**Consequences:**

**Positive:**
- Significantly better search relevance vs all-MiniLM-L6-v2
- Users see clear benefit of cloud storage mode
- 1024d vectors well-suited for MongoDB Atlas Vector Search
- Free tier adequate for most projects

**Negative:**
- Migration requires regenerating all embeddings (time-intensive)
- Requires Voyage AI API key (additional setup)
- API rate limits (1000 req/min) require batching
- Network dependency for embedding generation

**Implementation Notes:**
- Batch embedding requests (100 texts per API call)
- Implement retry logic for rate limit errors (429 status)
- Use async wrapper for Voyage AI SDK (sync by default)
- Document API costs transparently for users
- Provide cost calculator in migration tool

---

## ADR-003: Global vs Per-Project MongoDB Configuration

**Status:** Accepted

**Context:**
MongoDB Atlas connection credentials (connection string, database name) and Voyage AI API key must be configured. Need to decide whether configuration is global (shared across all projects) or per-project (each project can use different MongoDB cluster).

**Decision Drivers:**
- User experience (how many times must user configure?)
- Security (storing multiple credentials vs single set)
- Cost (one MongoDB cluster vs many)
- Typical usage pattern (how many projects use cloud storage?)

**Options Considered:**

### Option 1: Global Configuration
**Approach**: Single MongoDB connection string and Voyage AI API key configured once in Settings. All cloud storage projects use same cluster.

**Pros:**
- Configure once, use for all projects
- Simpler UX
- Single MongoDB cluster (cost-effective)
- Easier credential management
- Less configuration surface area

**Cons:**
- All projects share same database (but in separate collections)
- Cannot use different MongoDB clusters per project
- Cannot use organization-specific clusters

**Cost**: One-time configuration

### Option 2: Per-Project Configuration
**Approach**: Each project can specify its own MongoDB credentials.

**Pros:**
- Flexibility to use different clusters
- Isolation between projects (different databases/clusters)
- Can use organization-specific clusters

**Cons:**
- Configure credentials for every project
- Multiple MongoDB clusters (higher cost)
- More credentials to manage securely
- Complex UX

**Cost**: Configuration per project

### Option 3: Hybrid (Global Default + Per-Project Override)
**Approach**: Global configuration as default, but allow per-project overrides.

**Pros:**
- Best of both worlds
- Most projects use global, special cases use override

**Cons:**
- Most complex implementation
- UX complexity (users confused by two config locations)
- Maintenance burden

**Cost**: High implementation complexity

**Decision:** **Option 1 - Global Configuration**

**Rationale:**
- Typical user manages 1-5 projects using cloud storage
- All projects can share one MongoDB Atlas M0 cluster (512MB free tier)
- Simpler UX: configure once in Settings, enable per-project in Project Setup
- Easier credential management (`.env` file)
- MongoDB collections naturally isolate project data (`project_id` field)
- Cost-effective: M0 free tier sufficient for multiple small projects

**Consequences:**

**Positive:**
- One-time configuration (great UX)
- Single MongoDB cluster (cost-effective)
- Simple credential management
- Easy to set up and get started

**Negative:**
- All cloud projects share same cluster (but isolated by collections)
- Cannot use different clusters per project (edge case)
- Free tier 512MB shared across all cloud projects

**Implementation Notes:**
- Store credentials in `.env` file (global configuration)
- UI: Settings → Cloud Storage Configuration page
- Per-project: only storage mode selection (radio button: Local / Cloud)
- Cloud mode uses global MongoDB credentials automatically
- Document free tier limits (512MB shared across projects)

---

## ADR-004: Synchronous Voyage AI SDK with Async Wrapper

**Status:** Accepted

**Context:**
Voyage AI Python SDK is synchronous (blocking). ClaudeTask backend uses FastAPI with async/await. Need to integrate sync SDK into async architecture.

**Decision Drivers:**
- FastAPI is async (blocking calls degrade performance)
- Voyage AI SDK does not provide async version
- Embedding generation can be slow (100+ messages)
- User experience (avoid request timeouts)

**Options Considered:**

### Option 1: Async Wrapper with asyncio.to_thread()
**Approach**: Wrap sync Voyage AI calls in `asyncio.to_thread()` to run in executor.

**Pros:**
- Proper async integration with FastAPI
- Non-blocking for FastAPI event loop
- Clean async/await syntax in business logic
- Allows concurrent requests

**Cons:**
- Slight overhead from thread pool
- Must ensure thread safety

**Implementation**:
```python
async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
    embeddings = await asyncio.to_thread(
        self.client.embed,
        texts,
        model="voyage-3-large"
    )
    return embeddings.embeddings
```

### Option 2: Run Sync Code Directly (Blocking)
**Approach**: Call Voyage AI SDK directly in async functions.

**Pros:**
- Simple implementation
- No executor overhead

**Cons:**
- Blocks FastAPI event loop (degrades performance)
- Long embedding generation blocks all requests
- Poor user experience (request timeouts)
- Anti-pattern in async frameworks

### Option 3: Background Tasks
**Approach**: Queue embedding generation as background task.

**Pros:**
- Non-blocking for API response
- User gets immediate response

**Cons:**
- Complex state management (when are embeddings ready?)
- Requires job queue infrastructure
- Over-engineering for this use case

**Decision:** **Option 1 - Async Wrapper with asyncio.to_thread()**

**Rationale:**
- Proper async integration with FastAPI
- Minimal overhead (thread pool reuse)
- Clean code with async/await syntax
- Handles long-running embedding generation gracefully
- Industry standard approach for sync-in-async integration

**Consequences:**

**Positive:**
- FastAPI remains responsive during embedding generation
- Proper async architecture
- Concurrent request handling not impacted
- Thread pool reuse minimizes overhead

**Negative:**
- Slight CPU overhead from thread management
- Must ensure Voyage AI SDK is thread-safe (verified: it is)

**Implementation Notes:**
- Use `asyncio.to_thread()` (Python 3.9+)
- Batch embeddings (100 texts per call) to minimize API requests
- Add timeout handling (5 minutes max for large batches)
- Log embedding generation time for monitoring

---

## ADR-005: Migration Strategy - Offline Tool vs Online Dual-Write

**Status:** Accepted

**Context:**
When user migrates project from local to MongoDB, all conversation embeddings must be regenerated with voyage-3-large (cannot reuse all-MiniLM-L6-v2 embeddings due to dimension mismatch). Migration can take hours for large projects (100k messages = ~100 minutes).

**Decision Drivers:**
- Migration duration (can be hours)
- Data consistency during migration
- User experience (downtime tolerance)
- Implementation complexity
- Risk of data loss

**Options Considered:**

### Option 1: Offline Migration Tool
**Approach**: CLI tool that migrates data while project is offline. User stops using project, runs migration, then resumes.

**Pros:**
- Simple implementation
- No dual-write complexity
- Atomic migration (clear before/after)
- Easy rollback (preserve local data)
- User has full control over timing

**Cons:**
- Project downtime during migration
- User cannot use project during migration
- Must schedule migration window

**Implementation**: `python -m claudetask.migrations.migrate_to_mongodb --project-id=<id>`

### Option 2: Online Migration with Dual-Write
**Approach**: Migrate in background while project remains usable. Write to both SQLite and MongoDB during migration.

**Pros:**
- Zero downtime
- User can continue working
- Gradual migration

**Cons:**
- Complex implementation (dual-write logic)
- Data consistency risks (sync issues between DBs)
- Rollback difficult
- Higher resource usage (write to both DBs)

### Option 3: Read-Only Mode During Migration
**Approach**: Allow reads during migration, block writes.

**Pros:**
- Partial availability
- User can view data during migration

**Cons:**
- Complex state management
- User frustration (cannot add new data)
- Medium implementation complexity

**Decision:** **Option 1 - Offline Migration Tool**

**Rationale:**
- Simplicity: Clear migration process, easy to reason about
- Data Integrity: No dual-write complexity or sync issues
- Rollback Safety: Local data preserved until validation succeeds
- User Control: User schedules migration window
- Realistic: Large migrations happen infrequently (once per project)
- Transparent: Progress bar shows estimated time upfront

**Consequences:**

**Positive:**
- Simple, robust implementation
- Clear migration status (before, during, after)
- Easy rollback (just change storage_mode back to "local")
- No data consistency risks

**Negative:**
- Project downtime during migration (can be hours)
- User must plan migration timing
- Cannot use project during migration

**Implementation Notes:**
- CLI tool with rich progress bar
- Dry-run mode (`--dry-run`) for time estimation
- Batch processing (100 messages at a time)
- Pausable/resumable migration (save progress every 1000 records)
- Validation step (compare record counts)
- Preserve local data until validation succeeds
- Document expected downtime in migration guide

---

## ADR-006: MongoDB Free Tier (M0) vs Paid Tier (M10+)

**Status:** Accepted

**Context:**
MongoDB Atlas offers free tier (M0) with 512MB storage and paid tier (M10+) with Vector Search support. Need to decide which tier to target for initial implementation.

**Decision Drivers:**
- Development and testing requirements
- User adoption (free tier lowers barrier to entry)
- Vector Search availability (M0 does not support it)
- Production readiness
- Documentation clarity

**Options Considered:**

### Option 1: Require M10+ (Paid Tier)
**Approach**: Require paid MongoDB Atlas cluster ($0.08/hour minimum).

**Pros:**
- Vector Search available immediately
- Production-ready performance
- No storage limitations
- Predictable performance (dedicated resources)

**Cons:**
- Barrier to adoption (credit card required)
- Cannot test with free tier
- Users must pay to evaluate feature

**Cost**: $58/month minimum (M10 cluster)

### Option 2: Support M0 (Free Tier) for Development
**Approach**: Support M0 for development/testing, recommend M10+ for production.

**Pros:**
- Free tier lowers barrier to entry
- Users can test without credit card
- Good for small projects (<512MB)
- Development and testing covered

**Cons:**
- M0 does not support Vector Search (must document limitation)
- 512MB limit (small projects only)
- Shared resources (unpredictable performance)

**Cost**: Free (M0), upgrade to M10 when needed

**Decision:** **Option 2 - Support M0 for Development, Recommend M10+ for Production**

**Rationale:**
- Lower barrier to entry for evaluation
- Free tier adequate for development and small projects
- Clear upgrade path to production (M10+ for Vector Search)
- Transparent documentation about limitations
- Vector Search can gracefully degrade to metadata-only search on M0

**Consequences:**

**Positive:**
- Users can test MongoDB integration for free
- No credit card required for evaluation
- Good for personal projects and development
- Clear upgrade path when needed

**Negative:**
- Vector Search not available on M0 (must document clearly)
- Storage limit (512MB) restricts project size
- Performance unpredictable on shared tier

**Implementation Notes:**
- Document M0 limitations clearly in UI and setup guide
- Provide "Upgrade to M10+" link in settings when M0 detected
- Graceful degradation: fall back to metadata search if Vector Search unavailable
- Cost calculator shows M0 (free) vs M10 ($58/month) comparison
- Migration tool estimates project size and recommends tier

---

## Summary of Decisions

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Repository Pattern | Clean architecture, SOLID principles, future-proof |
| ADR-002 | voyage-3-large (1024d) | Superior quality, optimal for Vector Search, cost-effective |
| ADR-003 | Global MongoDB Config | Simple UX, cost-effective, configure once |
| ADR-004 | Async Wrapper for Voyage AI | Proper async integration with FastAPI |
| ADR-005 | Offline Migration Tool | Simple, robust, rollback safety |
| ADR-006 | Support M0 for Dev, M10 for Prod | Lower barrier to entry, clear upgrade path |

---

**Document Status:** Complete
**Last Updated:** 2025-11-26
**Total Pages:** ~6 pages
