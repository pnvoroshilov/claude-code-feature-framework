# Technical Requirements: MongoDB Atlas Integration

**Task ID:** 19
**Complexity:** COMPLEX
**Last Updated:** 2025-11-26

---

## Executive Summary

Implement dual storage backend for ClaudeTask Framework using Repository pattern:
- **Current**: SQLite + ChromaDB + all-MiniLM-L6-v2 (384d embeddings)
- **New**: MongoDB Atlas + Vector Search + voyage-3-large (1024d embeddings)
- **Approach**: Optional cloud storage selected per-project, backward compatible

**Total Estimated Effort:** 80-116 hours (2-3 weeks single developer)

---

## What to Change

### 1. Backend Database Layer

#### 1.1 Repository Pattern Implementation

**NEW: `claudetask/backend/app/repositories/base.py`**
```python
from abc import ABC, abstractmethod
from typing import Optional, List, Any

class BaseRepository(ABC):
    """Abstract base repository for database operations"""

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Any]: ...

    @abstractmethod
    async def create(self, entity: Any) -> str: ...

    @abstractmethod
    async def update(self, entity: Any) -> None: ...

    @abstractmethod
    async def delete(self, id: str) -> None: ...

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Any]: ...
```

**WHY**: Abstracts storage implementation (SQLite vs MongoDB). Allows swapping backends without changing business logic. SOLID principle: Dependency Inversion.

---

#### 1.2 Project Repository

**NEW: `claudetask/backend/app/repositories/project_repository.py`**

**SQLite Implementation** (existing):
```python
class SQLiteProjectRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self._db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def create(self, project: Project) -> str:
        self._db.add(project)
        await self._db.commit()
        return project.id

    # ... other CRUD methods
```

**MongoDB Implementation** (NEW):
```python
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBProjectRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        self._db = client[db_name]
        self._collection = self._db["projects"]

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        doc = await self._collection.find_one({"_id": project_id})
        if doc:
            return self._doc_to_project(doc)
        return None

    async def create(self, project: Project) -> str:
        doc = self._project_to_doc(project)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    def _project_to_doc(self, project: Project) -> dict:
        """Convert Project model to MongoDB document"""
        return {
            "_id": project.id,
            "name": project.name,
            "path": project.path,
            "github_repo": project.github_repo,
            "custom_instructions": project.custom_instructions,
            "tech_stack": project.tech_stack,
            "project_mode": project.project_mode,
            "is_active": project.is_active,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }

    def _doc_to_project(self, doc: dict) -> Project:
        """Convert MongoDB document to Project model"""
        return Project(
            id=doc["_id"],
            name=doc["name"],
            path=doc["path"],
            # ... map all fields
        )
```

**WHY**: Repository pattern allows identical business logic for both storage modes. MongoDB documents match SQLAlchemy ORM structure for seamless conversion.

---

#### 1.3 Task Repository

**NEW: `claudetask/backend/app/repositories/task_repository.py`**

**Key Differences from Project**:
- Foreign key `project_id` → MongoDB uses embedded reference
- JSON columns (`stage_results`, `testing_urls`) → Native MongoDB arrays/objects
- CASCADE DELETE → Implemented in application layer

**MongoDB CASCADE DELETE**:
```python
async def delete_project(self, project_id: str) -> None:
    """Delete project and all related tasks (CASCADE)"""
    # Delete tasks first
    await self._db["tasks"].delete_many({"project_id": project_id})

    # Delete task history
    await self._db["task_history"].delete_many({"project_id": project_id})

    # Delete project
    await self._db["projects"].delete_one({"_id": project_id})
```

**WHY**: MongoDB doesn't have native CASCADE DELETE. Must implement in application layer to maintain data integrity.

---

#### 1.4 Conversation Memory Repository

**NEW: `claudetask/backend/app/repositories/memory_repository.py`**

**MongoDB with Vector Search**:
```python
class MongoDBMemoryRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        self._db = client[db_name]
        self._collection = self._db["conversation_memory"]

    async def create_vector_index(self):
        """Create MongoDB Atlas Vector Search index"""
        # Index created via MongoDB Atlas UI or API
        # Index name: vector_search_idx
        # Field: embedding (array of 1024 floats)
        # Similarity: cosine
        pass

    async def save_message(
        self,
        project_id: str,
        content: str,
        embedding: List[float],
        metadata: dict
    ) -> int:
        """Save conversation message with voyage-3-large embedding"""
        doc = {
            "project_id": project_id,
            "content": content,
            "embedding": embedding,  # 1024-dimensional vector
            "message_type": metadata.get("message_type"),
            "session_id": metadata.get("session_id"),
            "task_id": metadata.get("task_id"),
            "timestamp": datetime.utcnow(),
            "metadata": metadata
        }
        result = await self._collection.insert_one(doc)
        return result.inserted_id

    async def vector_search(
        self,
        project_id: str,
        query_embedding: List[float],
        limit: int = 20,
        filters: Optional[dict] = None
    ) -> List[dict]:
        """Search using MongoDB Atlas Vector Search"""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_search_idx",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit
                }
            },
            {
                "$match": {"project_id": project_id}
            }
        ]

        # Add metadata filters if provided
        if filters:
            pipeline.append({"$match": filters})

        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)
```

**WHY**: MongoDB Atlas Vector Search provides cosine similarity search. voyage-3-large (1024d) offers superior semantic understanding vs all-MiniLM-L6-v2 (384d).

---

### 2. Embedding Service Layer

#### 2.1 Voyage AI Integration

**NEW: `claudetask/backend/app/services/embedding_service.py`**

```python
import voyageai
from typing import List
import asyncio

class VoyageEmbeddingService:
    def __init__(self, api_key: str):
        self.client = voyageai.Client(api_key=api_key)
        self.model = "voyage-3-large"
        self.dimensions = 1024

    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate voyage-3-large embeddings in batches"""
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Voyage AI SDK is sync, run in executor
            embeddings = await asyncio.to_thread(
                self.client.embed,
                batch,
                model=self.model,
                input_type="document"
            )

            all_embeddings.extend(embeddings.embeddings)

        return all_embeddings

    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        result = await self.generate_embeddings([text])
        return result[0]
```

**WHY**: Voyage AI API requires batching (max 100 texts) and rate limit handling. Async wrapper needed for FastAPI integration.

---

#### 2.2 Embedding Service Factory

**NEW: `claudetask/backend/app/services/embedding_factory.py`**

```python
class EmbeddingServiceFactory:
    @staticmethod
    def create(storage_mode: str) -> Any:
        """Create embedding service based on storage mode"""
        if storage_mode == "local":
            # Use all-MiniLM-L6-v2 (384d)
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer("all-MiniLM-L6-v2")

        elif storage_mode == "mongodb":
            # Use voyage-3-large (1024d)
            from app.services.embedding_service import VoyageEmbeddingService
            api_key = os.getenv("VOYAGE_AI_API_KEY")
            return VoyageEmbeddingService(api_key=api_key)

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")
```

**WHY**: Decouples embedding logic from storage implementation. Single source of truth for embedding model selection.

---

### 3. MongoDB Client Configuration

#### 3.1 MongoDB Connection Manager

**NEW: `claudetask/backend/app/database_mongodb.py`**

```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db_name: str = os.getenv("MONGODB_DATABASE_NAME", "claudetask")

    async def connect(self):
        """Connect to MongoDB Atlas"""
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")

        if not connection_string:
            raise ValueError("MONGODB_CONNECTION_STRING not set in environment")

        self.client = AsyncIOMotorClient(
            connection_string,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            tls=True,  # Enforce TLS
            tlsAllowInvalidCertificates=False
        )

        # Test connection
        await self.client.admin.command('ping')
        print(f"Connected to MongoDB Atlas: {self.db_name}")

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    def get_database(self):
        """Get database instance"""
        if not self.client:
            raise RuntimeError("MongoDB not connected")
        return self.client[self.db_name]


# Global instance
mongodb_manager = MongoDBManager()


async def get_mongodb():
    """Dependency for FastAPI endpoints"""
    return mongodb_manager.get_database()
```

**WHY**: Connection pooling prevents exhaustion (max 10 connections). TLS enforced for security. Motor provides async MongoDB support for FastAPI.

---

#### 3.2 Environment Configuration

**MODIFY: `.env` file (template)**

```bash
# MongoDB Atlas Configuration (optional)
MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE_NAME=claudetask

# Voyage AI API Key (required for MongoDB storage)
VOYAGE_AI_API_KEY=vo-your-api-key-here
```

**WHY**: Credentials never in code or database. `.env` file excluded from git. Environment variables standard for cloud config.

---

### 4. Storage Provider Factory

#### 4.1 Repository Factory

**NEW: `claudetask/backend/app/repositories/factory.py`**

```python
from app.repositories.project_repository import (
    SQLiteProjectRepository,
    MongoDBProjectRepository
)
from app.repositories.task_repository import (
    SQLiteTaskRepository,
    MongoDBTaskRepository
)
from app.repositories.memory_repository import (
    SQLiteMemoryRepository,
    MongoDBMemoryRepository
)


class RepositoryFactory:
    """Factory for creating storage-specific repositories"""

    @staticmethod
    async def get_project_repository(
        project_id: str,
        db: AsyncSession = None
    ) -> BaseRepository:
        """Get project repository based on project's storage mode"""
        # Get project settings to determine storage mode
        if db:
            result = await db.execute(
                select(ProjectSettings).where(
                    ProjectSettings.project_id == project_id
                )
            )
            settings = result.scalar_one_or_none()
            storage_mode = settings.storage_mode if settings else "local"
        else:
            storage_mode = "local"  # Default

        if storage_mode == "local":
            return SQLiteProjectRepository(db)
        elif storage_mode == "mongodb":
            from app.database_mongodb import get_mongodb
            mongodb = await get_mongodb()
            return MongoDBProjectRepository(mongodb)
        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")

    @staticmethod
    async def get_task_repository(project_id: str, db: AsyncSession = None):
        # Similar logic for task repository
        pass

    @staticmethod
    async def get_memory_repository(project_id: str, db: AsyncSession = None):
        # Similar logic for memory repository
        pass
```

**WHY**: Centralized factory pattern. Business logic calls factory, gets correct repository. No `if storage_mode == "mongodb"` in controllers.

---

### 5. Database Schema Changes

#### 5.1 Add Storage Mode Column

**NEW: `claudetask/backend/migrations/010_add_storage_mode.sql`**

```sql
-- Add storage_mode column to project_settings
ALTER TABLE project_settings
ADD COLUMN storage_mode TEXT NOT NULL DEFAULT 'local';

-- Valid values: 'local' or 'mongodb'
-- Immutable after creation (enforced in application layer)

-- Create index for faster lookups
CREATE INDEX idx_project_settings_storage_mode
ON project_settings(storage_mode);
```

**WHY**: Per-project storage mode selection. Default "local" ensures backward compatibility. Index improves query performance.

---

#### 5.2 MongoDB Collections Design

**MongoDB Collections** (no migration needed, created on first use):

```javascript
// Collection: projects
{
  "_id": "uuid",
  "name": "string",
  "path": "string",
  "github_repo": "string",
  "custom_instructions": "string",
  "tech_stack": ["array"],
  "project_mode": "string",
  "is_active": "boolean",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}

// Collection: tasks
{
  "_id": "ObjectId",
  "project_id": "uuid",  // Reference to projects._id
  "title": "string",
  "description": "string",
  "type": "string",
  "priority": "string",
  "status": "string",
  "analysis": "string",
  "stage_results": ["array"],  // Native JSON
  "testing_urls": {"object"},
  "git_branch": "string",
  "worktree_path": "string",
  "assigned_agent": "string",
  "estimated_hours": "number",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "completed_at": "ISODate"
}

// Collection: conversation_memory
{
  "_id": "ObjectId",
  "project_id": "uuid",
  "session_id": "uuid",
  "task_id": "number",
  "message_type": "string",  // "user" | "assistant" | "system"
  "content": "string",
  "embedding": [1024 floats],  // voyage-3-large vector
  "timestamp": "ISODate",
  "metadata": {"object"}
}

// Vector Search Index on conversation_memory.embedding
// Created via MongoDB Atlas UI:
{
  "name": "vector_search_idx",
  "type": "vectorSearch",
  "definition": {
    "fields": [{
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine"
    }]
  }
}
```

**Indexes**:
```javascript
// conversation_memory
db.conversation_memory.createIndex({ "project_id": 1 })
db.conversation_memory.createIndex({ "session_id": 1 })
db.conversation_memory.createIndex({ "task_id": 1 })
db.conversation_memory.createIndex({ "timestamp": -1 })

// tasks
db.tasks.createIndex({ "project_id": 1 })
db.tasks.createIndex({ "status": 1 })
db.tasks.createIndex({ "created_at": -1 })
```

**WHY**: MongoDB document structure mirrors SQLAlchemy ORM for consistency. Indexes optimize frequent queries. Vector index enables semantic search.

---

### 6. Frontend Changes

#### 6.1 Project Setup Storage Mode Selection

**MODIFY: `claudetask/frontend/src/pages/ProjectSetup.tsx`**

```typescript
// Add storage mode state
const [storageMode, setStorageMode] = useState<'local' | 'mongodb'>('local');
const [mongodbConfigured, setMongodbConfigured] = useState(false);

// Check if MongoDB is configured
useEffect(() => {
  axios.get(`${API_BASE_URL}/api/settings/cloud-storage/status`)
    .then(response => {
      setMongodbConfigured(response.data.configured);
    })
    .catch(() => setMongodbConfigured(false));
}, []);

// Add UI after project mode selection
<FormControl component="fieldset" sx={{ mt: 3 }}>
  <FormLabel component="legend">Storage Mode</FormLabel>
  <RadioGroup
    value={storageMode}
    onChange={(e) => setStorageMode(e.target.value as 'local' | 'mongodb')}
  >
    <FormControlLabel
      value="local"
      control={<Radio />}
      label={
        <Box>
          <Typography variant="subtitle2">Local Storage (SQLite + ChromaDB)</Typography>
          <Typography variant="caption" color="text.secondary">
            Default. All data stored locally. Works offline. Free.
          </Typography>
        </Box>
      }
    />
    <FormControlLabel
      value="mongodb"
      control={<Radio />}
      label={
        <Box>
          <Typography variant="subtitle2">
            Cloud Storage (MongoDB Atlas)
            {!mongodbConfigured && <Chip label="Requires Setup" size="small" color="warning" sx={{ ml: 1 }} />}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Cloud-based persistence. Requires MongoDB Atlas and Voyage AI API key.
            Enables better vector search (1024d vs 384d embeddings).
          </Typography>
        </Box>
      }
      disabled={!mongodbConfigured}
    />
  </RadioGroup>
  {!mongodbConfigured && storageMode === 'mongodb' && (
    <Alert severity="warning" sx={{ mt: 1 }}>
      MongoDB Atlas not configured. Go to Settings → Cloud Storage to configure.
    </Alert>
  )}
</FormControl>

// Add tooltip with cost information
<Tooltip title={
  <Box>
    <Typography variant="caption" display="block">Local: Free, unlimited</Typography>
    <Typography variant="caption" display="block">
      Cloud: MongoDB M0 (free, 512MB) or M10+ ($0.08/hr, production)
    </Typography>
    <Typography variant="caption" display="block">
      Voyage AI: Free tier (1M tokens/month), then $0.10 per 1M tokens
    </Typography>
  </Box>
}>
  <IconButton size="small"><InfoIcon /></IconButton>
</Tooltip>
```

**WHY**: User selects storage mode during project creation. Clear explanation of costs and requirements. Disabled if MongoDB not configured.

---

#### 6.2 Cloud Storage Configuration Page

**NEW: `claudetask/frontend/src/pages/CloudStorageSettings.tsx`**

```typescript
export default function CloudStorageSettings() {
  const [connectionString, setConnectionString] = useState('');
  const [databaseName, setDatabaseName] = useState('claudetask');
  const [voyageApiKey, setVoyageApiKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [saving, setSaving] = useState(false);

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/settings/cloud-storage/test`,
        {
          connection_string: connectionString,
          database_name: databaseName,
          voyage_api_key: voyageApiKey
        }
      );

      setTestResult({
        success: true,
        data: response.data
      });
    } catch (error: any) {
      setTestResult({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConfiguration = async () => {
    setSaving(true);

    try {
      await axios.post(
        `${API_BASE_URL}/api/settings/cloud-storage/save`,
        {
          connection_string: connectionString,
          database_name: databaseName,
          voyage_api_key: voyageApiKey
        }
      );

      toast.success('Configuration saved. Restart required.');
    } catch (error: any) {
      toast.error('Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Cloud Storage Configuration
      </Typography>

      <TextField
        fullWidth
        type="password"
        label="MongoDB Connection String"
        placeholder="mongodb+srv://..."
        value={connectionString}
        onChange={(e) => setConnectionString(e.target.value)}
        sx={{ mt: 2 }}
        helperText="Format: mongodb+srv://user:password@cluster.mongodb.net/"
      />

      <TextField
        fullWidth
        label="Database Name"
        value={databaseName}
        onChange={(e) => setDatabaseName(e.target.value)}
        sx={{ mt: 2 }}
        helperText="Default: claudetask"
      />

      <TextField
        fullWidth
        type="password"
        label="Voyage AI API Key"
        placeholder="vo-..."
        value={voyageApiKey}
        onChange={(e) => setVoyageApiKey(e.target.value)}
        sx={{ mt: 2 }}
        helperText="Required for voyage-3-large embeddings"
      />

      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          onClick={handleTestConnection}
          disabled={!connectionString || !voyageApiKey || testing}
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </Button>

        <Button
          variant="contained"
          onClick={handleSaveConfiguration}
          disabled={!testResult?.success || saving}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </Button>
      </Box>

      {testResult && (
        <Alert severity={testResult.success ? 'success' : 'error'} sx={{ mt: 2 }}>
          {testResult.success ? (
            <>
              <AlertTitle>Connection Successful</AlertTitle>
              MongoDB: {testResult.data.mongodb_connected ? '✅' : '❌'}<br />
              Voyage AI: {testResult.data.voyage_ai_valid ? '✅' : '❌'}<br />
              Database Writable: {testResult.data.database_writable ? '✅' : '❌'}
            </>
          ) : (
            <>
              <AlertTitle>Connection Failed</AlertTitle>
              {testResult.error}
            </>
          )}
        </Alert>
      )}
    </Container>
  );
}
```

**WHY**: User-friendly configuration interface. Test connection before saving. Secure credential storage (password fields).

---

### 7. Backend API Endpoints

#### 7.1 Cloud Storage Configuration Endpoints

**NEW: `claudetask/backend/app/routers/cloud_storage.py`**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter()


class CloudStorageConfig(BaseModel):
    connection_string: str
    database_name: str
    voyage_api_key: str


@router.get("/api/settings/cloud-storage/status")
async def get_cloud_storage_status():
    """Check if MongoDB Atlas is configured"""
    configured = bool(
        os.getenv("MONGODB_CONNECTION_STRING") and
        os.getenv("VOYAGE_AI_API_KEY")
    )

    return {"configured": configured}


@router.post("/api/settings/cloud-storage/test")
async def test_cloud_storage_connection(config: CloudStorageConfig):
    """Test MongoDB and Voyage AI connections"""
    results = {
        "mongodb_connected": False,
        "voyage_ai_valid": False,
        "database_writable": False,
        "error": None
    }

    try:
        # Test MongoDB connection
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(
            config.connection_string,
            serverSelectionTimeoutMS=5000,
            tls=True
        )

        # Ping database
        await client.admin.command('ping')
        results["mongodb_connected"] = True

        # Test write permissions
        db = client[config.database_name]
        test_collection = db["_connection_test"]
        await test_collection.insert_one({"test": "connection"})
        await test_collection.delete_one({"test": "connection"})
        results["database_writable"] = True

        client.close()

    except Exception as e:
        results["error"] = f"MongoDB error: {str(e)}"
        return results

    try:
        # Test Voyage AI API
        import voyageai

        client = voyageai.Client(api_key=config.voyage_api_key)
        client.embed(["test"], model="voyage-3-large")
        results["voyage_ai_valid"] = True

    except Exception as e:
        results["error"] = f"Voyage AI error: {str(e)}"
        return results

    return results


@router.post("/api/settings/cloud-storage/save")
async def save_cloud_storage_config(config: CloudStorageConfig):
    """Save MongoDB and Voyage AI configuration to .env file"""
    # Get .env file path
    env_path = Path(__file__).parent.parent.parent.parent / ".env"

    # Read existing .env
    env_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

    # Update or add MongoDB config
    updated_lines = []
    keys_to_update = {
        "MONGODB_CONNECTION_STRING": config.connection_string,
        "MONGODB_DATABASE_NAME": config.database_name,
        "VOYAGE_AI_API_KEY": config.voyage_api_key
    }

    keys_updated = set()

    for line in env_lines:
        key = line.split('=')[0].strip()
        if key in keys_to_update:
            updated_lines.append(f"{key}={keys_to_update[key]}\n")
            keys_updated.add(key)
        else:
            updated_lines.append(line)

    # Add missing keys
    for key, value in keys_to_update.items():
        if key not in keys_updated:
            updated_lines.append(f"{key}={value}\n")

    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)

    # Update current environment (for immediate use without restart)
    os.environ.update(keys_to_update)

    return {"status": "saved", "restart_required": True}
```

**WHY**: Backend validates MongoDB and Voyage AI connections before saving. Credentials written to `.env` file for persistence. Environment updated immediately for testing.

---

### 8. Data Migration Utility

#### 8.1 Migration CLI Tool

**NEW: `claudetask/migrations/migrate_to_mongodb.py`**

```python
import asyncio
import sys
from rich.console import Console
from rich.progress import Progress
import click

console = Console()


@click.command()
@click.option('--project-id', required=True, help='Project ID to migrate')
@click.option('--dry-run', is_flag=True, help='Preview migration without committing')
async def migrate_project(project_id: str, dry_run: bool):
    """Migrate project from local to MongoDB Atlas storage"""

    console.print(f"[bold]MongoDB Migration Tool[/bold]")
    console.print(f"Project ID: {project_id}")
    console.print(f"Dry Run: {dry_run}\n")

    # Get project data from SQLite
    console.print("[cyan]Step 1: Loading project from SQLite...[/cyan]")
    from app.database import AsyncSessionLocal
    from app.models import Project, Task, TaskHistory, ConversationMemory

    async with AsyncSessionLocal() as db:
        project = await db.get(Project, project_id)
        if not project:
            console.print(f"[red]Project {project_id} not found[/red]")
            return

        # Get all related data
        tasks = await db.execute(
            select(Task).where(Task.project_id == project_id)
        )
        tasks = tasks.scalars().all()

        messages = await db.execute(
            select(ConversationMemory).where(
                ConversationMemory.project_id == project_id
            )
        )
        messages = messages.scalars().all()

        console.print(f"  Found: 1 project, {len(tasks)} tasks, {len(messages)} messages")

    # Estimate time
    estimated_minutes = len(messages) // 100  # 100 messages/minute
    console.print(f"[yellow]Estimated time: {estimated_minutes} minutes[/yellow]\n")

    if not dry_run:
        proceed = click.confirm("Proceed with migration?")
        if not proceed:
            console.print("[yellow]Migration cancelled[/yellow]")
            return

    # Migrate to MongoDB
    console.print("[cyan]Step 2: Migrating to MongoDB Atlas...[/cyan]")

    from app.database_mongodb import mongodb_manager
    from app.services.embedding_service import VoyageEmbeddingService

    await mongodb_manager.connect()
    db = mongodb_manager.get_database()

    embedding_service = VoyageEmbeddingService(
        api_key=os.getenv("VOYAGE_AI_API_KEY")
    )

    if not dry_run:
        # Migrate project
        await db.projects.insert_one({
            "_id": project.id,
            "name": project.name,
            # ... all fields
        })

        # Migrate tasks
        for task in tasks:
            await db.tasks.insert_one({
                # ... task fields
            })

        # Migrate and re-embed messages
        console.print("[cyan]Step 3: Regenerating embeddings with voyage-3-large...[/cyan]")

        with Progress() as progress:
            task_progress = progress.add_task(
                "[green]Embedding messages...",
                total=len(messages)
            )

            # Batch process (100 messages at a time)
            for i in range(0, len(messages), 100):
                batch = messages[i:i+100]

                # Generate embeddings
                texts = [msg.content for msg in batch]
                embeddings = await embedding_service.generate_embeddings(texts)

                # Insert to MongoDB
                docs = []
                for msg, embedding in zip(batch, embeddings):
                    docs.append({
                        "project_id": msg.project_id,
                        "content": msg.content,
                        "embedding": embedding,  # 1024-dimensional
                        # ... other fields
                    })

                await db.conversation_memory.insert_many(docs)

                progress.update(task_progress, advance=len(batch))

        # Validate migration
        console.print("[cyan]Step 4: Validating migration...[/cyan]")

        project_count = await db.projects.count_documents({"_id": project_id})
        task_count = await db.tasks.count_documents({"project_id": project_id})
        message_count = await db.conversation_memory.count_documents(
            {"project_id": project_id}
        )

        console.print(f"  Projects: {project_count} / 1")
        console.print(f"  Tasks: {task_count} / {len(tasks)}")
        console.print(f"  Messages: {message_count} / {len(messages)}")

        if project_count == 1 and task_count == len(tasks) and message_count == len(messages):
            console.print("[green]✓ Migration successful![/green]")

            # Update project settings to use MongoDB
            async with AsyncSessionLocal() as db:
                settings = await db.execute(
                    select(ProjectSettings).where(
                        ProjectSettings.project_id == project_id
                    )
                )
                settings = settings.scalar_one()
                settings.storage_mode = "mongodb"
                await db.commit()

            console.print("[green]✓ Project updated to use MongoDB storage[/green]")
        else:
            console.print("[red]✗ Migration failed - record counts don't match[/red]")

    else:
        # Dry run - just show what would be migrated
        console.print(f"[yellow]DRY RUN - Would migrate:[/yellow]")
        console.print(f"  - 1 project")
        console.print(f"  - {len(tasks)} tasks")
        console.print(f"  - {len(messages)} messages")
        console.print(f"  - Regenerate {len(messages)} embeddings with voyage-3-large")


if __name__ == "__main__":
    asyncio.run(migrate_project())
```

**WHY**: CLI migration tool for manual data migration. Dry-run mode for preview. Progress bar for long-running operations. Validation ensures data integrity.

---

## Where to Change

### New Files
- `claudetask/backend/app/repositories/base.py`
- `claudetask/backend/app/repositories/project_repository.py`
- `claudetask/backend/app/repositories/task_repository.py`
- `claudetask/backend/app/repositories/memory_repository.py`
- `claudetask/backend/app/repositories/factory.py`
- `claudetask/backend/app/services/embedding_service.py`
- `claudetask/backend/app/services/embedding_factory.py`
- `claudetask/backend/app/database_mongodb.py`
- `claudetask/backend/app/routers/cloud_storage.py`
- `claudetask/backend/migrations/010_add_storage_mode.sql`
- `claudetask/migrations/migrate_to_mongodb.py`
- `claudetask/frontend/src/pages/CloudStorageSettings.tsx`

### Modified Files
- `claudetask/frontend/src/pages/ProjectSetup.tsx` - Add storage mode selection UI
- `claudetask/backend/app/main.py` - Add cloud storage router, MongoDB startup
- `claudetask/backend/app/models.py` - Add ProjectSettings.storage_mode field
- `claudetask/config.py` - Add MongoDB config paths
- `.env.example` - Add MongoDB and Voyage AI config template
- `requirements.txt` - Add motor, voyageai dependencies

---

## Why These Changes

### Business Justification
1. **User Value**: Cloud persistence enables multi-device access, automatic backups
2. **Scalability**: MongoDB handles 100k+ messages better than SQLite
3. **Collaboration**: Shared database across team members
4. **Search Quality**: voyage-3-large (1024d) embeddings provide better semantic understanding

### Technical Justification
1. **Repository Pattern**: Abstracts storage, enables future backends (PostgreSQL, etc.)
2. **Backward Compatibility**: Local storage remains default, no breaking changes
3. **Testability**: Repository interfaces enable easy mocking in tests
4. **Maintainability**: Single codebase supports both storage modes
5. **Security**: Credentials in environment variables, never in code

### Architecture Alignment
- **Clean Architecture**: Repository pattern separates domain from infrastructure
- **SOLID Principles**: Dependency inversion (depend on abstractions)
- **Existing Patterns**: Mirrors SQLAlchemy ORM structure for consistency
- **FastAPI Async**: Motor (async MongoDB driver) fits async/await architecture

---

## Total Estimated Effort

| Component | Hours |
|-----------|-------|
| Repository Pattern | 16-24 |
| MongoDB Integration | 12-16 |
| Voyage AI Integration | 8-12 |
| Migration Utility | 12-16 |
| UI Configuration | 8-12 |
| Testing | 16-24 |
| Documentation | 8-12 |
| **Total** | **80-116 hours** |

**Timeline**: 2-3 weeks for single developer

---

## Next Steps

1. Implement Repository pattern base classes
2. Implement SQLite repositories (refactor existing code)
3. Implement MongoDB repositories
4. Add Voyage AI embedding service
5. Create storage provider factory
6. Add frontend storage mode selection
7. Build cloud storage configuration UI
8. Create migration utility
9. Write comprehensive tests
10. Update documentation

---

**Document Status:** Complete
**Ready for Implementation:** Yes
**Total Pages:** ~8 pages
