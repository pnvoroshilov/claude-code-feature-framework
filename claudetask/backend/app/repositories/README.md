# Repository Pattern Implementation

This package implements the Repository pattern for database abstraction in ClaudeTask Framework.

## Overview

The Repository pattern provides a clean abstraction layer between the business logic and data storage, enabling the application to use either SQLite (local) or MongoDB Atlas (cloud) storage without changing business logic code.

## Architecture

```
repositories/
├── __init__.py              # Package exports
├── base.py                  # Abstract base repository (ABC)
├── project_repository.py    # Project CRUD (SQLite + MongoDB)
├── task_repository.py       # Task CRUD (SQLite + MongoDB)
├── memory_repository.py     # Conversation memory + Vector Search
└── factory.py               # Repository factory for storage selection
```

## Usage

### Get Repository via Factory

```python
from app.repositories.factory import RepositoryFactory
from app.database import get_db

# Get project repository
async with AsyncSession() as db:
    repo = await RepositoryFactory.get_project_repository(
        project_id="abc123",
        db=db
    )

    # Use repository (works with both SQLite and MongoDB)
    project = await repo.get_by_id("abc123")
    await repo.update(project)
```

### Direct Usage (if you know storage mode)

```python
# SQLite
from app.repositories.project_repository import SQLiteProjectRepository

repo = SQLiteProjectRepository(db)
project = await repo.get_by_id("abc123")

# MongoDB
from app.repositories.project_repository import MongoDBProjectRepository
from app.database_mongodb import get_mongodb

db = await get_mongodb()
repo = MongoDBProjectRepository(db)
project = await repo.get_by_id("abc123")
```

## Repository Implementations

### SQLiteProjectRepository
- Uses SQLAlchemy ORM
- Maintains backward compatibility
- Default for local storage

### MongoDBProjectRepository
- Uses Motor async driver
- Implements CASCADE DELETE in application layer
- Provides cloud storage capabilities

### SQLiteTaskRepository
- Foreign key relationships via SQLAlchemy
- Automatic CASCADE DELETE via database

### MongoDBTaskRepository
- ObjectId for primary keys
- Manual CASCADE DELETE implementation
- JSON fields stored natively

### SQLiteMemoryRepository
- Integrates with ChromaDB for vector search
- Uses all-MiniLM-L6-v2 embeddings (384d)

### MongoDBMemoryRepository
- MongoDB Atlas Vector Search
- Uses voyage-3-large embeddings (1024d)
- Cosine similarity for semantic search

## Storage Mode Selection

The factory determines storage mode from project settings:

```python
# Query project_settings.storage_mode
# Values: "local" or "mongodb"
storage_mode = await RepositoryFactory._get_storage_mode(project_id, db)
```

## Benefits

1. **Abstraction**: Business logic doesn't care about storage implementation
2. **Testability**: Easy to mock repository interfaces
3. **Extensibility**: Can add PostgreSQL, DynamoDB, etc.
4. **SOLID**: Dependency Inversion - depend on abstractions (ABC)
5. **Flexibility**: Switch storage backends per project

## Example: Adding New Storage Backend

```python
# 1. Create new implementation
class PostgreSQLProjectRepository(BaseRepository):
    async def get_by_id(self, id: str):
        # PostgreSQL implementation
        pass

# 2. Update factory
class RepositoryFactory:
    @staticmethod
    async def get_project_repository(project_id, db):
        storage_mode = await get_storage_mode(project_id)

        if storage_mode == "postgresql":
            return PostgreSQLProjectRepository(db)
        # ... existing modes
```

## Testing

```python
# Mock repository for unit tests
class MockProjectRepository(BaseRepository):
    def __init__(self):
        self.projects = {}

    async def get_by_id(self, id: str):
        return self.projects.get(id)

    async def create(self, entity):
        self.projects[entity.id] = entity
        return entity.id
```

## See Also

- `app/database_mongodb.py` - MongoDB connection manager
- `app/services/embedding_factory.py` - Embedding service selection
- `migrations/migrate_to_mongodb.py` - Data migration utility
