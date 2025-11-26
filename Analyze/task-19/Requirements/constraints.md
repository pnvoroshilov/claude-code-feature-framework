# Constraints: MongoDB Atlas Integration

**Task ID:** 19  
**Last Updated:** 2025-11-26

---

## 1. Technical Constraints

### TC-1: Technology Stack (MANDATORY)
**Constraint:** Must use specific MongoDB and embedding technologies

**Technologies:**
- **MongoDB Driver:** Motor (async) >= 3.3.0
- **Embedding Model:** voyage-3-large (1024 dimensions)
- **Embedding API:** Voyage AI SDK >= 0.2.0
- **Backend Framework:** FastAPI (async/await pattern)
- **Database Pattern:** Repository pattern or Adapter pattern

**Rationale:** Motor is official async driver for FastAPI; voyage-3-large provides superior embeddings vs all-MiniLM-L6-v2

**Impact:** Cannot use synchronous `pymongo` for FastAPI endpoints; must handle async contexts throughout

---

### TC-2: Existing Codebase Integration (MANDATORY)
**Constraint:** Cannot break existing SQLite + ChromaDB implementation

**Protected Components:**
- SQLite database schema (all tables)
- ChromaDB collection structure
- all-MiniLM-L6-v2 embedding model
- Existing MCP tools interface
- FastAPI endpoints (no signature changes)

**Rationale:** Backward compatibility critical; existing local storage must remain functional

**Impact:** Dual implementation required; repository pattern mandatory to abstract storage

---

### TC-3: MongoDB Atlas Limitations (INFORMATIONAL)
**Constraint:** MongoDB Atlas Free Tier (M0) has resource limits

**M0 Cluster Limits:**
- **Storage:** 512MB maximum
- **Connections:** 100 concurrent connections max
- **RAM:** 512MB shared
- **CPU:** Shared (no guaranteed capacity)
- **Throughput:** Throttled at high load
- **Vector Search:** Requires M10+ cluster ($0.08/hour minimum)

**Rationale:** Free tier suitable for development, not production

**Impact:**
- Must document production cluster requirements (M10+)
- Free tier cannot use Vector Search (requires paid cluster)
- Large projects (>512MB) cannot use free tier

---

### TC-4: voyage-3-large API Constraints (MANDATORY)
**Constraint:** Voyage AI API has rate limits and costs

**Rate Limits:**
- **Requests:** 1,000 requests/minute
- **Tokens:** 1M tokens/month (free tier)
- **Batch Size:** 100 texts per request maximum
- **Dimensions:** Fixed at 1024 (cannot customize)

**Costs (as of Nov 2025):**
- **Free Tier:** 1M tokens/month
- **Pay-as-you-go:** $0.10 per 1M tokens
- **Estimated:** 10k messages = ~5M tokens = $0.50

**Rationale:** API is external service with limits

**Impact:**
- Must batch embedding requests (100 texts/call)
- Must implement retry logic for rate limits
- Must document expected costs for users
- Large migrations may incur API costs

---

### TC-5: Database Schema Mapping (MANDATORY)
**Constraint:** SQLite relational schema must map to MongoDB documents

**Mapping Challenges:**
- **Foreign Keys:** No native support in MongoDB → use application-level joins or embedded documents
- **AUTOINCREMENT:** MongoDB uses ObjectId → need custom sequence or accept ObjectId
- **CASCADE DELETE:** No native support → must implement in application layer
- **Transactions:** Limited to replica sets (not available on M0 free tier)
- **Indexes:** Different syntax and capabilities

**Rationale:** Document-based vs relational models have fundamental differences

**Impact:**
- Repository layer must handle foreign key logic
- CASCADE DELETE logic in Python code
- ObjectId conversion for existing integer IDs
- Careful index design for performance

---

## 2. Design Constraints

### DC-1: Repository Pattern (MANDATORY)
**Constraint:** Must implement Repository pattern for database abstraction

**Required Structure:**
```python
# Abstract interface
class ProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: str) -> Project: ...
    @abstractmethod
    async def create(self, project: Project) -> str: ...
    @abstractmethod
    async def update(self, project: Project) -> None: ...
    @abstractmethod
    async def delete(self, project_id: str) -> None: ...

# SQLite implementation
class SQLiteProjectRepository(ProjectRepository):
    async def get_by_id(self, project_id: str) -> Project:
        # SQLAlchemy logic
        ...

# MongoDB implementation
class MongoDBProjectRepository(ProjectRepository):
    async def get_by_id(self, project_id: str) -> Project:
        # Motor logic
        ...

# Factory
def get_project_repository(storage_mode: str) -> ProjectRepository:
    if storage_mode == "local":
        return SQLiteProjectRepository()
    elif storage_mode == "mongodb":
        return MongoDBProjectRepository()
```

**Rationale:** Single responsibility; testability; swappable implementations

**Impact:** Significant refactoring of existing database access code

---

### DC-2: Dependency Injection (MANDATORY)
**Constraint:** FastAPI endpoints must use dependency injection for repositories

**Pattern:**
```python
from fastapi import Depends

async def get_project_repo(
    project_id: str = Path(...)
) -> ProjectRepository:
    project = await get_project_by_id(project_id)
    return get_project_repository(project.storage_mode)

@app.get("/api/projects/{project_id}")
async def get_project_endpoint(
    project_id: str,
    repo: ProjectRepository = Depends(get_project_repo)
):
    return await repo.get_by_id(project_id)
```

**Rationale:** Testability (mock repositories); clean architecture

**Impact:** All endpoints accessing database must be refactored to use dependencies

---

### DC-3: UI Configuration Separation (RECOMMENDED)
**Constraint:** Storage mode configuration should be minimal in UI

**Approach:**
- **Global Config:** MongoDB connection string, database name, Voyage AI key (Settings page)
- **Per-Project:** Storage mode selection only (radio button)
- **No per-project credentials:** Use global configuration

**Rationale:** Simpler UX; centralized credential management

**Impact:** One MongoDB cluster serves all cloud storage projects

---

## 3. Performance Constraints

### PC-1: Vector Search Latency (TARGET)
**Constraint:** Vector Search should complete in <500ms for 10k+ documents

**Factors Affecting Performance:**
- **Index Type:** IVF (Inverted File) vs HNSW (Hierarchical Navigable Small World)
- **Number of Candidates:** Higher = more accurate but slower
- **Filter Complexity:** Metadata filters add overhead
- **Network Latency:** MongoDB Atlas hosted remotely

**Target Metrics:**
- **P50:** <200ms
- **P95:** <500ms
- **P99:** <1000ms

**Rationale:** User experience; comparable to ChromaDB local performance

**Impact:**
- Must choose appropriate Vector Search index type
- May need to tune `numCandidates` parameter
- Document performance expectations for users

---

### PC-2: Embedding Generation Throughput (MANDATORY)
**Constraint:** voyage-3-large API calls must be batched to avoid rate limits

**Batching Strategy:**
- **Batch Size:** 100 texts per API call (max allowed)
- **Parallelism:** 10 concurrent API requests max
- **Retry Logic:** Exponential backoff on rate limit (429 status)
- **Progress:** Report progress every 1000 embeddings

**Throughput:**
- **Sequential:** ~1000 embeddings/minute (10 batches/min × 100/batch)
- **Parallel (10x):** ~10,000 embeddings/minute
- **Large Migration:** 100k messages = ~10 minutes

**Rationale:** API rate limits; migration time acceptable; no user wait

**Impact:** Migration of large projects requires time; must implement queue and batch processing

---

### PC-3: MongoDB Connection Pool (MANDATORY)
**Constraint:** Connection pool must be configured to prevent exhaustion

**Pool Configuration:**
```python
client = AsyncIOMotorClient(
    connection_string,
    maxPoolSize=10,          # Max connections
    minPoolSize=1,           # Min connections
    maxIdleTimeMS=30000,     # Close idle after 30s
    serverSelectionTimeoutMS=5000  # Timeout if can't connect
)
```

**Rationale:** MongoDB Atlas M0 has 100 connection limit shared across all clients

**Impact:** Must not exceed 10 connections per framework instance; may need connection queuing

---

## 4. Security Constraints

### SC-1: Credential Storage (MANDATORY)
**Constraint:** MongoDB and Voyage AI credentials must NOT be in database or code

**Storage Mechanism:**
- **Primary:** `.env` file in project root (excluded from git)
- **Alternative:** Encrypted configuration file with master password
- **Environment Variables:** `MONGODB_CONNECTION_STRING`, `VOYAGE_AI_API_KEY`

**Rationale:** Security best practice; prevent credential leaks

**Impact:**
- Must create `.env` file management logic
- Must ensure `.env` in `.gitignore`
- Must validate `.env` exists before using cloud storage

---

### SC-2: Connection String Validation (MANDATORY)
**Constraint:** MongoDB connection string must be validated for security

**Validation Rules:**
- **Format:** Starts with `mongodb://` or `mongodb+srv://`
- **Authentication:** Contains username and password (URL-encoded)
- **TLS/SSL:** Contains `ssl=true` or uses `mongodb+srv://` (implicit TLS)
- **No Plain Passwords:** Password must be URL-encoded (no special chars unencoded)
- **No Localhost:** For cloud storage, localhost not allowed

**Rationale:** Prevent insecure connections; ensure proper authentication

**Impact:** Must implement validation before saving connection string; reject invalid strings

---

### SC-3: TLS/SSL Enforcement (MANDATORY)
**Constraint:** All MongoDB connections must use TLS/SSL

**Enforcement:**
- **mongodb+srv://:** Implicit TLS (preferred)
- **mongodb://:** Must include `?tls=true` or `?ssl=true`
- **Motor Client:** Verify TLS enabled via connection parameters

**Rationale:** Protect data in transit; MongoDB Atlas requires TLS

**Impact:** Reject connections without TLS; document TLS requirement

---

### SC-4: API Key Security (MANDATORY)
**Constraint:** Voyage AI API key must be protected

**Protection Measures:**
- **Storage:** Only in `.env` file (never in database or logs)
- **Logging:** Mask API key in logs (show only first/last 4 chars)
- **Error Messages:** Never include API key in user-facing errors
- **UI:** Display as password field (hidden characters)

**Rationale:** API keys are sensitive credentials

**Impact:** Must sanitize logs; never expose API key to frontend

---

## 5. Data Constraints

### DC-1: Embedding Dimension Mismatch (CRITICAL)
**Constraint:** Cannot mix 384d (all-MiniLM-L6-v2) and 1024d (voyage-3-large) embeddings

**Problem:**
- Local storage: 384-dimensional embeddings
- Cloud storage: 1024-dimensional embeddings
- Vector Search requires consistent dimensions

**Solutions:**
1. **Migration Regenerates Embeddings:** All embeddings regenerated with voyage-3-large during migration
2. **Separate Indexes:** Local and cloud use different models (no mixing)
3. **No Hybrid:** Cannot search across local and cloud simultaneously

**Rationale:** Cosine similarity requires same dimensions

**Impact:** Migration must regenerate ALL embeddings; cannot share embeddings between modes

---

### DC-2: Data Size Limits (INFORMATIONAL)
**Constraint:** MongoDB Atlas M0 Free Tier limited to 512MB

**Typical Data Sizes:**
- **Project:** ~10KB
- **Task:** ~5KB
- **Conversation Message:** ~2KB + embedding (4KB for 1024d floats) = ~6KB total
- **Project Summary:** ~50KB

**Capacity Estimates:**
- **Small Project:** 1,000 messages = ~6MB
- **Medium Project:** 10,000 messages = ~60MB
- **Large Project:** 100,000 messages = ~600MB (exceeds free tier)

**Rationale:** Free tier for testing/small projects only

**Impact:**
- Must document size limits
- Must recommend M10+ for production (>10k messages)
- Migration may fail if project > 512MB

---

### DC-3: Schema Evolution (MANDATORY)
**Constraint:** MongoDB schema must support future changes

**Considerations:**
- **Versioning:** Include `schema_version` field in documents
- **Optional Fields:** Use optional fields for new features
- **Migration Path:** Plan for schema migrations
- **Backward Compatibility:** Old documents readable by new code

**Rationale:** Schema will evolve over time

**Impact:** Design schema with extensibility in mind; include version field

---

## 6. Business Constraints

### BC-1: No Breaking Changes (MANDATORY)
**Constraint:** Existing local storage users must not be affected

**Requirements:**
- Local storage remains default
- No forced migration
- No new dependencies for local mode
- No performance regression for local mode
- Existing projects work without configuration

**Rationale:** User trust; adoption resistance if breaking changes

**Impact:** Dual implementation complexity; extensive testing required

---

### BC-2: Optional Feature (MANDATORY)
**Constraint:** MongoDB Atlas integration is optional, not required

**Implementation:**
- MongoDB/Motor imports lazy-loaded (only if cloud mode used)
- Voyage AI SDK optional dependency
- Framework works without MongoDB Atlas configured
- Error messages guide user to setup if cloud mode selected without config

**Rationale:** Not all users want/need cloud storage

**Impact:** Conditional imports; graceful degradation; clear user messaging

---

### BC-3: Cost Transparency (RECOMMENDED)
**Constraint:** Users must understand costs before using cloud storage

**Documentation Required:**
- MongoDB Atlas cluster costs (M0 free, M10 paid)
- Voyage AI API costs (per 1M tokens)
- Estimated costs for typical project sizes
- Comparison: local (free) vs cloud (paid)

**Rationale:** Avoid surprise bills; informed decision-making

**Impact:** Must create cost calculator/estimator; warn users about potential costs

---

## 7. Time and Resource Constraints

### RC-1: Migration Duration (INFORMATIONAL)
**Constraint:** Large project migrations can take hours

**Duration Estimates:**
- **1,000 messages:** ~1 minute
- **10,000 messages:** ~10 minutes
- **100,000 messages:** ~100 minutes (~1.7 hours)
- **1,000,000 messages:** ~1000 minutes (~16.7 hours)

**Factors:**
- Voyage AI API rate limits
- Network latency to MongoDB Atlas
- Local SQLite read speed
- MongoDB write throughput

**Rationale:** Embedding regeneration is bottleneck

**Impact:**
- Must support pausable/resumable migrations
- Must display realistic time estimates
- Must run migrations in background (async task)

---

### RC-2: Development Effort (INFORMATIONAL)
**Constraint:** Implementation is complex and time-consuming

**Estimated Effort:**
- **Repository Pattern Implementation:** 16-24 hours
- **MongoDB Integration:** 12-16 hours
- **Voyage AI Integration:** 8-12 hours
- **Migration Utility:** 12-16 hours
- **UI Configuration:** 8-12 hours
- **Testing:** 16-24 hours
- **Documentation:** 8-12 hours
- **Total:** 80-116 hours (2-3 weeks for single developer)

**Rationale:** Large feature with many components

**Impact:** Significant time investment; prioritize core functionality

---

## 8. Dependencies and Integration Constraints

### IC-1: External Service Dependencies (MANDATORY)
**Constraint:** Requires active MongoDB Atlas and Voyage AI accounts

**Setup Requirements:**
1. **MongoDB Atlas:**
   - Create account (free tier available)
   - Create cluster (M0 free or M10+ paid)
   - Configure Network Access (IP whitelist)
   - Create database user (username/password)
   - Get connection string

2. **Voyage AI:**
   - Create account (voyageai.com)
   - Get API key
   - Understand rate limits and costs

**Rationale:** External services beyond our control

**Impact:**
- Users must complete setup before using cloud storage
- Setup guide must be comprehensive
- Test connection functionality critical

---

### IC-2: Network Requirements (MANDATORY)
**Constraint:** Requires stable internet connection for cloud storage

**Network Considerations:**
- **Latency:** Higher latency to MongoDB Atlas vs local SQLite
- **Bandwidth:** Large migrations use significant bandwidth
- **Reliability:** Connection failures require retry logic
- **Firewall:** MongoDB Atlas requires outbound connections on port 27017

**Rationale:** Cloud service accessed over internet

**Impact:**
- Offline mode not supported for cloud storage
- Network issues cause degraded performance
- Must handle connection failures gracefully

---

### IC-3: Version Compatibility (MANDATORY)
**Constraint:** Must maintain compatibility with specific library versions

**Dependencies:**
```python
motor>=3.3.0,<4.0         # Async MongoDB driver
pymongo>=4.6.0,<5.0       # Sync MongoDB driver (for migration)
voyageai>=0.2.0,<1.0      # Voyage AI SDK
python-dotenv>=1.0.0      # Environment variables
```

**Rationale:** Breaking changes in major versions

**Impact:** Pin major versions; test upgrades carefully

---

## 9. Known Limitations

### KL-1: No Real-Time Sync (KNOWN)
**Limitation:** Changes from one instance not reflected in others without refresh

**Details:**
- No WebSocket or change streams
- Multi-user editing not supported
- Must refresh to see changes from other users

**Rationale:** Out of scope for initial implementation

**Impact:** Document limitation; consider future enhancement

---

### KL-2: No Hybrid Storage (KNOWN)
**Limitation:** Cannot use SQLite for relational + MongoDB for RAG only

**Details:**
- All-or-nothing: either full local or full cloud
- Cannot mix storage backends within one project
- Cannot share embeddings between local and cloud projects

**Rationale:** Complexity of hybrid approach

**Impact:** Users must choose one mode; migration required to switch

---

### KL-3: No Offline Cloud Mode (KNOWN)
**Limitation:** Cloud storage requires internet connection

**Details:**
- Cannot access cloud-stored projects offline
- No local cache of cloud data
- Fails gracefully with error message

**Rationale:** Cloud service requires network

**Impact:** Local storage recommended for offline work

---

### KL-4: Free Tier Limitations (KNOWN)
**Limitation:** MongoDB Atlas M0 not suitable for production

**Limitations:**
- 512MB storage limit
- Shared CPU/RAM (unpredictable performance)
- No Vector Search support (requires M10+)
- 100 connection limit (shared)

**Rationale:** Free tier designed for development/testing

**Impact:** Must document M10+ requirement for production; free tier only for demos

---

## 10. Assumptions

### A-1: MongoDB Atlas Availability
**Assumption:** MongoDB Atlas service is reliable and available

**Risk:** Medium (cloud service outages possible)

**Mitigation:** Document fallback to local storage if cloud unavailable

---

### A-2: Voyage AI API Stability
**Assumption:** Voyage AI API remains available with consistent pricing

**Risk:** Medium (startup service, pricing may change)

**Mitigation:** Abstract embedding generation; support multiple embedding providers

---

### A-3: User Technical Expertise
**Assumption:** Users can setup MongoDB Atlas and obtain API keys

**Risk:** Low (documentation and guides provided)

**Mitigation:** Detailed setup guide with screenshots; test connection functionality

---

### A-4: Project Sizes Under 1GB
**Assumption:** Most projects stay under 1GB (100k-500k messages)

**Risk:** Low (typical projects have <50k conversations)

**Mitigation:** Document size limits; provide cost calculator

---

## Summary Matrix

| Category | Constraint | Priority | Impact |
|----------|-----------|----------|--------|
| Technical | Motor Async Driver | MANDATORY | High - Async patterns required |
| Technical | MongoDB Atlas Limits | INFORMATIONAL | Medium - Free tier limitations |
| Technical | voyage-3-large API | MANDATORY | High - Batching and rate limits |
| Design | Repository Pattern | MANDATORY | High - Major refactoring |
| Design | Dependency Injection | MANDATORY | High - Endpoint changes |
| Performance | Vector Search Latency | TARGET | Medium - User experience |
| Performance | Embedding Throughput | MANDATORY | High - Migration speed |
| Security | Credential Storage | MANDATORY | High - Security risk |
| Security | TLS/SSL Enforcement | MANDATORY | High - Data protection |
| Data | Embedding Dimensions | CRITICAL | High - Cannot mix 384d and 1024d |
| Business | No Breaking Changes | MANDATORY | High - Backward compatibility |
| Business | Optional Feature | MANDATORY | Medium - Conditional logic |
| Resource | Migration Duration | INFORMATIONAL | Medium - User expectations |
| Integration | External Services | MANDATORY | High - Setup requirements |
| Limitation | No Real-Time Sync | KNOWN | Low - Document only |
| Limitation | Free Tier Limits | KNOWN | Medium - Production considerations |

---

**Total Constraints:** 31 (17 MANDATORY, 3 TARGET, 5 INFORMATIONAL, 6 KNOWN LIMITATIONS, 4 ASSUMPTIONS)

**Critical Path Blockers:** None identified (all external dependencies optional)

**Document Status:** Final  
**Last Updated:** 2025-11-26  
**Total Pages:** ~3 pages
