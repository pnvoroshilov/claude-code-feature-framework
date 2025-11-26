"""Repository pattern for database abstraction"""

from .base import BaseRepository
from .project_repository import SQLiteProjectRepository, MongoDBProjectRepository
from .task_repository import SQLiteTaskRepository, MongoDBTaskRepository
from .memory_repository import SQLiteMemoryRepository, MongoDBMemoryRepository
from .factory import RepositoryFactory

__all__ = [
    "BaseRepository",
    "SQLiteProjectRepository",
    "MongoDBProjectRepository",
    "SQLiteTaskRepository",
    "MongoDBTaskRepository",
    "SQLiteMemoryRepository",
    "MongoDBMemoryRepository",
    "RepositoryFactory",
]
