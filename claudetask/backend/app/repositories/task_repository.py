"""Task repository implementations for SQLite and MongoDB"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from .base import BaseRepository
from ..models import Task, TaskStatus, TaskPriority, TaskType


class SQLiteTaskRepository(BaseRepository):
    """
    SQLite implementation of Task repository using SQLAlchemy ORM.

    Maintains backward compatibility with existing local storage.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize SQLite task repository.

        Args:
            db: SQLAlchemy async session
        """
        self._db = db

    async def get_by_id(self, id: str) -> Optional[Task]:
        """Retrieve task by ID from SQLite."""
        result = await self._db.execute(
            select(Task).where(Task.id == int(id))
        )
        return result.scalar_one_or_none()

    async def create(self, entity: Task) -> str:
        """Create new task in SQLite."""
        self._db.add(entity)
        await self._db.commit()
        await self._db.refresh(entity)
        return str(entity.id)

    async def update(self, entity: Task) -> None:
        """Update existing task in SQLite."""
        entity.updated_at = datetime.utcnow()
        await self._db.commit()
        await self._db.refresh(entity)

    async def delete(self, id: str) -> None:
        """Delete task from SQLite (CASCADE handles history)."""
        task = await self.get_by_id(id)
        if task:
            await self._db.delete(task)
            await self._db.commit()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Task]:
        """List tasks from SQLite with pagination and filters."""
        query = select(Task)

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query = query.where(Task.project_id == filters["project_id"])
            if "status" in filters:
                query = query.where(Task.status == filters["status"])
            if "priority" in filters:
                query = query.where(Task.priority == filters["priority"])
            if "type" in filters:
                query = query.where(Task.type == filters["type"])

        query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
        result = await self._db.execute(query)
        return result.scalars().all()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count tasks in SQLite."""
        from sqlalchemy import func

        query = select(func.count(Task.id))

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query = query.where(Task.project_id == filters["project_id"])
            if "status" in filters:
                query = query.where(Task.status == filters["status"])

        result = await self._db.execute(query)
        return result.scalar()

    async def get_by_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a project."""
        return await self.list(filters={"project_id": project_id}, limit=1000)

    async def get_by_status(self, status: TaskStatus, project_id: Optional[str] = None) -> List[Task]:
        """Get tasks by status, optionally filtered by project."""
        filters = {"status": status}
        if project_id:
            filters["project_id"] = project_id
        return await self.list(filters=filters, limit=1000)


class MongoDBTaskRepository(BaseRepository):
    """
    MongoDB implementation of Task repository using Motor async driver.

    Provides cloud-based storage with MongoDB Atlas for task data.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB task repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._collection = db["tasks"]

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve task by ID from MongoDB."""
        from bson import ObjectId

        try:
            doc = await self._collection.find_one({"_id": ObjectId(id)})
            if doc:
                return self._doc_to_task(doc)
        except Exception:
            # If ID is not a valid ObjectId, try as integer for backward compatibility
            doc = await self._collection.find_one({"task_id": int(id)})
            if doc:
                return self._doc_to_task(doc)

        return None

    async def create(self, entity: Any) -> str:
        """Create new task in MongoDB."""
        doc = self._task_to_doc(entity)
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing task in MongoDB."""
        from bson import ObjectId

        doc = self._task_to_doc(entity)
        doc["updated_at"] = datetime.utcnow()

        # Use ObjectId for _id if available
        task_id = entity.id if isinstance(entity, dict) else entity.id
        if isinstance(task_id, str) and len(task_id) == 24:
            await self._collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": doc}
            )
        else:
            # Fallback to task_id field
            await self._collection.update_one(
                {"task_id": int(task_id)},
                {"$set": doc}
            )

    async def delete(self, id: str) -> None:
        """
        Delete task from MongoDB.

        CASCADE DELETE: Also deletes related task history.
        """
        from bson import ObjectId

        # Delete related task history
        await self._db["task_history"].delete_many({"task_id": int(id)})

        # Delete task
        try:
            await self._collection.delete_one({"_id": ObjectId(id)})
        except Exception:
            # Fallback to task_id field
            await self._collection.delete_one({"task_id": int(id)})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List tasks from MongoDB with pagination and filters."""
        query = {}

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "status" in filters:
                query["status"] = filters["status"]
            if "priority" in filters:
                query["priority"] = filters["priority"]
            if "type" in filters:
                query["type"] = filters["type"]

        cursor = (
            self._collection
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._doc_to_task(doc) for doc in docs]

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count tasks in MongoDB."""
        query = {}

        # Apply filters if provided
        if filters:
            if "project_id" in filters:
                query["project_id"] = filters["project_id"]
            if "status" in filters:
                query["status"] = filters["status"]

        return await self._collection.count_documents(query)

    async def get_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a project."""
        return await self.list(filters={"project_id": project_id}, limit=1000)

    async def get_by_status(self, status: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks by status, optionally filtered by project."""
        filters = {"status": status}
        if project_id:
            filters["project_id"] = project_id
        return await self.list(filters=filters, limit=1000)

    def _task_to_doc(self, task: Any) -> Dict[str, Any]:
        """
        Convert Task model to MongoDB document.

        Args:
            task: Task model instance or dict

        Returns:
            MongoDB document dictionary
        """
        if isinstance(task, dict):
            return task

        return {
            "task_id": task.id,  # Keep original ID for reference
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "type": task.type.value if hasattr(task.type, 'value') else task.type,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "analysis": task.analysis,
            "stage_results": task.stage_results or [],
            "testing_urls": task.testing_urls,
            "git_branch": task.git_branch,
            "worktree_path": task.worktree_path,
            "assigned_agent": task.assigned_agent,
            "estimated_hours": task.estimated_hours,
            "created_at": task.created_at,
            "updated_at": task.updated_at or datetime.utcnow(),
            "completed_at": task.completed_at
        }

    def _doc_to_task(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to Task dict.

        Args:
            doc: MongoDB document

        Returns:
            Task dictionary compatible with Pydantic models
        """
        return {
            "id": doc.get("task_id") or str(doc["_id"]),
            "project_id": doc["project_id"],
            "title": doc["title"],
            "description": doc.get("description"),
            "type": doc.get("type", "Feature"),
            "priority": doc.get("priority", "Medium"),
            "status": doc.get("status", "Backlog"),
            "analysis": doc.get("analysis"),
            "stage_results": doc.get("stage_results", []),
            "testing_urls": doc.get("testing_urls"),
            "git_branch": doc.get("git_branch"),
            "worktree_path": doc.get("worktree_path"),
            "assigned_agent": doc.get("assigned_agent"),
            "estimated_hours": doc.get("estimated_hours"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "completed_at": doc.get("completed_at")
        }
