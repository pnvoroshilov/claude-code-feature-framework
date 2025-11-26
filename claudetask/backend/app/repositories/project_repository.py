"""Project repository implementations for SQLite and MongoDB"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime

from .base import BaseRepository
from ..models import Project


class SQLiteProjectRepository(BaseRepository):
    """
    SQLite implementation of Project repository using SQLAlchemy ORM.

    This implementation maintains backward compatibility with existing
    local storage infrastructure.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize SQLite repository.

        Args:
            db: SQLAlchemy async session
        """
        self._db = db

    async def get_by_id(self, id: str) -> Optional[Project]:
        """Retrieve project by ID from SQLite."""
        result = await self._db.execute(
            select(Project).where(Project.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, entity: Project) -> str:
        """Create new project in SQLite."""
        self._db.add(entity)
        await self._db.commit()
        await self._db.refresh(entity)
        return entity.id

    async def update(self, entity: Project) -> None:
        """Update existing project in SQLite."""
        entity.updated_at = datetime.utcnow()
        await self._db.commit()
        await self._db.refresh(entity)

    async def delete(self, id: str) -> None:
        """Delete project from SQLite."""
        project = await self.get_by_id(id)
        if project:
            await self._db.delete(project)
            await self._db.commit()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Project]:
        """List projects from SQLite with pagination."""
        query = select(Project)

        # Apply filters if provided
        if filters:
            if "is_active" in filters:
                query = query.where(Project.is_active == filters["is_active"])
            if "project_mode" in filters:
                query = query.where(Project.project_mode == filters["project_mode"])

        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count projects in SQLite."""
        from sqlalchemy import func

        query = select(func.count(Project.id))

        # Apply filters if provided
        if filters:
            if "is_active" in filters:
                query = query.where(Project.is_active == filters["is_active"])
            if "project_mode" in filters:
                query = query.where(Project.project_mode == filters["project_mode"])

        result = await self._db.execute(query)
        return result.scalar()

    async def get_by_path(self, path: str) -> Optional[Project]:
        """Get project by path (unique constraint)."""
        result = await self._db.execute(
            select(Project).where(Project.path == path)
        )
        return result.scalar_one_or_none()

    async def get_active_project(self) -> Optional[Project]:
        """Get currently active project."""
        result = await self._db.execute(
            select(Project).where(Project.is_active == True)
        )
        return result.scalar_one_or_none()


class MongoDBProjectRepository(BaseRepository):
    """
    MongoDB implementation of Project repository using Motor async driver.

    This implementation provides cloud-based storage with MongoDB Atlas,
    enabling multi-device access and automatic backups.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._collection = db["projects"]

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve project by ID from MongoDB."""
        doc = await self._collection.find_one({"_id": id})
        if doc:
            return self._doc_to_project(doc)
        return None

    async def create(self, entity: Any) -> str:
        """Create new project in MongoDB."""
        doc = self._project_to_doc(entity)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing project in MongoDB."""
        doc = self._project_to_doc(entity)
        doc["updated_at"] = datetime.utcnow()

        await self._collection.update_one(
            {"_id": entity.id},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """
        Delete project from MongoDB.

        Note: CASCADE DELETE is implemented in application layer.
        This will also delete related tasks, history, and conversations.
        """
        # Delete related tasks
        await self._db["tasks"].delete_many({"project_id": id})

        # Delete related task history
        await self._db["task_history"].delete_many({"project_id": id})

        # Delete related conversations
        await self._db["conversation_memory"].delete_many({"project_id": id})

        # Delete project settings
        await self._db["project_settings"].delete_one({"project_id": id})

        # Delete project
        await self._collection.delete_one({"_id": id})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List projects from MongoDB with pagination."""
        query = {}

        # Apply filters if provided
        if filters:
            if "is_active" in filters:
                query["is_active"] = filters["is_active"]
            if "project_mode" in filters:
                query["project_mode"] = filters["project_mode"]

        cursor = self._collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_project(doc) for doc in docs]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count projects in MongoDB."""
        query = {}

        # Apply filters if provided
        if filters:
            if "is_active" in filters:
                query["is_active"] = filters["is_active"]
            if "project_mode" in filters:
                query["project_mode"] = filters["project_mode"]

        return await self._collection.count_documents(query)

    async def get_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get project by path (unique constraint)."""
        doc = await self._collection.find_one({"path": path})
        if doc:
            return self._doc_to_project(doc)
        return None

    async def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Get currently active project."""
        doc = await self._collection.find_one({"is_active": True})
        if doc:
            return self._doc_to_project(doc)
        return None

    def _project_to_doc(self, project: Any) -> Dict[str, Any]:
        """
        Convert Project model to MongoDB document.

        Args:
            project: Project model instance or dict

        Returns:
            MongoDB document dictionary
        """
        if isinstance(project, dict):
            return project

        return {
            "_id": project.id,
            "name": project.name,
            "path": project.path,
            "github_repo": project.github_repo,
            "custom_instructions": project.custom_instructions,
            "tech_stack": project.tech_stack or [],
            "project_mode": project.project_mode,
            "is_active": project.is_active,
            "created_at": project.created_at,
            "updated_at": project.updated_at or datetime.utcnow()
        }

    def _doc_to_project(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to Project dict.

        Args:
            doc: MongoDB document

        Returns:
            Project dictionary compatible with Pydantic models
        """
        return {
            "id": doc["_id"],
            "name": doc["name"],
            "path": doc["path"],
            "github_repo": doc.get("github_repo"),
            "custom_instructions": doc.get("custom_instructions", ""),
            "tech_stack": doc.get("tech_stack", []),
            "project_mode": doc.get("project_mode", "simple"),
            "is_active": doc.get("is_active", False),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        }
