"""Hook repository implementations for MongoDB storage"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

from .base import BaseRepository


class MongoDBHookRepository(BaseRepository):
    """
    MongoDB implementation of hook repository.

    Manages three collections:
    - default_hooks: Framework-provided hooks (global)
    - custom_hooks: User-created hooks (per project)
    - project_hooks: Junction table for enabled hooks per project
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB hook repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._default_hooks = db["default_hooks"]
        self._custom_hooks = db["custom_hooks"]
        self._project_hooks = db["project_hooks"]

    # ==================
    # BaseRepository Implementation
    # ==================

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get hook by ID (checks both default and custom)."""
        # Try default first
        doc = await self._default_hooks.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_hook(doc, "default")

        # Try custom
        doc = await self._custom_hooks.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_hook(doc, "custom")

        return None

    async def create(self, entity: Any) -> str:
        """Create new hook."""
        doc = self._hook_to_doc(entity)
        result = await self._custom_hooks.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing hook."""
        hook_id = entity.get("id") if isinstance(entity, dict) else entity.id
        hook_type = entity.get("hook_type", "custom") if isinstance(entity, dict) else getattr(entity, "hook_type", "custom")

        doc = self._hook_to_doc(entity)
        doc.pop("_id", None)

        collection = self._default_hooks if hook_type == "default" else self._custom_hooks
        await collection.update_one(
            {"_id": ObjectId(hook_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete hook by ID."""
        await self._default_hooks.delete_one({"_id": ObjectId(id)})
        await self._custom_hooks.delete_one({"_id": ObjectId(id)})
        await self._project_hooks.delete_many({"hook_id": id})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List hooks with pagination and filters."""
        results = []

        # Get default hooks
        query = {"is_active": True}
        cursor = self._default_hooks.find(query).skip(skip).limit(limit)
        async for doc in cursor:
            results.append(self._doc_to_hook(doc, "default"))

        # Get custom hooks if project_id filter provided
        if filters and "project_id" in filters:
            query = {"project_id": filters["project_id"]}
            cursor = self._custom_hooks.find(query).skip(skip).limit(limit)
            async for doc in cursor:
                results.append(self._doc_to_hook(doc, "custom"))

        return results

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count hooks."""
        default_count = await self._default_hooks.count_documents({"is_active": True})

        custom_count = 0
        if filters and "project_id" in filters:
            custom_count = await self._custom_hooks.count_documents({"project_id": filters["project_id"]})

        return default_count + custom_count

    # ==================
    # Default Hooks Methods
    # ==================

    async def get_all_default_hooks(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get all default hooks."""
        query = {"is_active": is_active}
        cursor = self._default_hooks.find(query).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_hook(doc, "default") for doc in docs]

    async def get_default_hook(self, hook_id: str) -> Optional[Dict[str, Any]]:
        """Get default hook by ID."""
        try:
            doc = await self._default_hooks.find_one({"_id": ObjectId(hook_id)})
            if doc:
                return self._doc_to_hook(doc, "default")
        except Exception:
            pass
        return None

    async def get_default_hook_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get default hook by name."""
        doc = await self._default_hooks.find_one({"name": name})
        if doc:
            return self._doc_to_hook(doc, "default")
        return None

    async def create_default_hook(self, hook: Dict[str, Any]) -> str:
        """Create new default hook."""
        doc = {
            "name": hook["name"],
            "description": hook["description"],
            "category": hook.get("category", "General"),
            "hook_config": hook["hook_config"],
            "setup_instructions": hook.get("setup_instructions"),
            "dependencies": hook.get("dependencies"),
            "script_file": hook.get("script_file"),
            "is_active": hook.get("is_active", True),
            "is_favorite": hook.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._default_hooks.insert_one(doc)
        return str(result.inserted_id)

    async def update_default_hook(self, hook_id: str, updates: Dict[str, Any]) -> None:
        """Update default hook."""
        updates["updated_at"] = datetime.utcnow()
        await self._default_hooks.update_one(
            {"_id": ObjectId(hook_id)},
            {"$set": updates}
        )

    async def get_favorite_default_hooks(self) -> List[Dict[str, Any]]:
        """Get all favorite default hooks."""
        cursor = self._default_hooks.find({"is_favorite": True, "is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_hook(doc, "default") for doc in docs]

    # ==================
    # Custom Hooks Methods
    # ==================

    async def get_custom_hooks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all custom hooks for a project."""
        cursor = self._custom_hooks.find({"project_id": project_id}).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_hook(doc, "custom") for doc in docs]

    async def get_custom_hook(self, hook_id: str) -> Optional[Dict[str, Any]]:
        """Get custom hook by ID."""
        try:
            doc = await self._custom_hooks.find_one({"_id": ObjectId(hook_id)})
            if doc:
                return self._doc_to_hook(doc, "custom")
        except Exception:
            pass
        return None

    async def get_custom_hook_by_name(self, project_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get custom hook by name within a project."""
        doc = await self._custom_hooks.find_one({
            "project_id": project_id,
            "name": name
        })
        if doc:
            return self._doc_to_hook(doc, "custom")
        return None

    async def create_custom_hook(self, hook: Dict[str, Any]) -> str:
        """Create new custom hook."""
        doc = {
            "project_id": hook["project_id"],
            "name": hook["name"],
            "description": hook["description"],
            "category": hook.get("category", "Custom"),
            "file_name": hook.get("file_name"),
            "hook_config": hook.get("hook_config", {}),
            "setup_instructions": hook.get("setup_instructions"),
            "dependencies": hook.get("dependencies"),
            "status": hook.get("status", "creating"),
            "error_message": hook.get("error_message"),
            "created_by": hook.get("created_by", "user"),
            "is_favorite": hook.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._custom_hooks.insert_one(doc)
        return str(result.inserted_id)

    async def update_custom_hook(self, hook_id: str, updates: Dict[str, Any]) -> None:
        """Update custom hook."""
        updates["updated_at"] = datetime.utcnow()
        await self._custom_hooks.update_one(
            {"_id": ObjectId(hook_id)},
            {"$set": updates}
        )

    async def delete_custom_hook(self, hook_id: str) -> None:
        """Delete custom hook permanently."""
        await self._custom_hooks.delete_one({"_id": ObjectId(hook_id)})
        await self._project_hooks.delete_many({
            "hook_id": hook_id,
            "hook_type": "custom"
        })

    async def get_favorite_custom_hooks(self) -> List[Dict[str, Any]]:
        """Get all favorite custom hooks across all projects."""
        cursor = self._custom_hooks.find({"is_favorite": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_hook(doc, "custom") for doc in docs]

    # ==================
    # Project Hooks (Junction) Methods
    # ==================

    async def get_enabled_hooks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all enabled hooks for a project."""
        cursor = self._project_hooks.find({"project_id": project_id})
        enabled_records = await cursor.to_list(length=1000)

        hooks = []
        for record in enabled_records:
            hook_id = record["hook_id"]
            hook_type = record["hook_type"]

            if hook_type == "default":
                hook = await self.get_default_hook(hook_id)
            else:
                hook = await self.get_custom_hook(hook_id)

            if hook:
                hook["is_enabled"] = True
                hook["enabled_at"] = record.get("enabled_at")
                hook["enabled_by"] = record.get("enabled_by")
                hooks.append(hook)

        return hooks

    async def is_hook_enabled(
        self,
        project_id: str,
        hook_id: str,
        hook_type: str
    ) -> bool:
        """Check if hook is enabled for project."""
        doc = await self._project_hooks.find_one({
            "project_id": project_id,
            "hook_id": hook_id,
            "hook_type": hook_type
        })
        return doc is not None

    async def enable_hook(
        self,
        project_id: str,
        hook_id: str,
        hook_type: str,
        enabled_by: str = "user"
    ) -> str:
        """Enable hook for a project."""
        existing = await self._project_hooks.find_one({
            "project_id": project_id,
            "hook_id": hook_id,
            "hook_type": hook_type
        })
        if existing:
            return str(existing["_id"])

        doc = {
            "project_id": project_id,
            "hook_id": hook_id,
            "hook_type": hook_type,
            "enabled_at": datetime.utcnow(),
            "enabled_by": enabled_by
        }
        result = await self._project_hooks.insert_one(doc)
        return str(result.inserted_id)

    async def disable_hook(
        self,
        project_id: str,
        hook_id: str,
        hook_type: str
    ) -> bool:
        """Disable hook for a project."""
        result = await self._project_hooks.delete_one({
            "project_id": project_id,
            "hook_id": hook_id,
            "hook_type": hook_type
        })
        return result.deleted_count > 0

    async def disable_all_hooks(self, project_id: str) -> int:
        """Disable all hooks for a project."""
        result = await self._project_hooks.delete_many({"project_id": project_id})
        return result.deleted_count

    async def get_enabled_hook_ids(self, project_id: str) -> set:
        """Get set of (hook_id, hook_type) tuples for enabled hooks."""
        cursor = self._project_hooks.find(
            {"project_id": project_id},
            {"hook_id": 1, "hook_type": 1}
        )
        docs = await cursor.to_list(length=1000)
        return {(doc["hook_id"], doc["hook_type"]) for doc in docs}

    async def get_all_enabled_project_hooks(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all ProjectHook records for a project."""
        cursor = self._project_hooks.find({"project_id": project_id})
        docs = await cursor.to_list(length=1000)
        return docs

    # ==================
    # Utility Methods
    # ==================

    def _hook_to_doc(self, hook: Any) -> Dict[str, Any]:
        """Convert hook to MongoDB document."""
        if isinstance(hook, dict):
            doc = hook.copy()
            if "id" in doc:
                doc["_id"] = ObjectId(doc.pop("id"))
            return doc

        return {
            "name": hook.name,
            "description": hook.description,
            "category": hook.category,
            "hook_config": hook.hook_config,
            "setup_instructions": getattr(hook, "setup_instructions", None),
            "dependencies": getattr(hook, "dependencies", None),
            "is_active": getattr(hook, "is_active", True),
            "is_favorite": getattr(hook, "is_favorite", False),
            "status": getattr(hook, "status", None),
            "error_message": getattr(hook, "error_message", None),
            "created_by": getattr(hook, "created_by", "system"),
            "created_at": hook.created_at,
            "updated_at": hook.updated_at
        }

    def _doc_to_hook(self, doc: Dict[str, Any], hook_type: str) -> Dict[str, Any]:
        """Convert MongoDB document to hook dict."""
        return {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc["description"],
            "hook_type": hook_type,
            "category": doc.get("category", "General"),
            "hook_config": doc.get("hook_config", {}),
            "setup_instructions": doc.get("setup_instructions"),
            "dependencies": doc.get("dependencies"),
            "script_file": doc.get("script_file"),
            "is_active": doc.get("is_active", True),
            "is_favorite": doc.get("is_favorite", False),
            "is_enabled": doc.get("is_enabled", False),
            "status": doc.get("status"),
            "error_message": doc.get("error_message"),
            "created_by": doc.get("created_by", "system"),
            "project_id": doc.get("project_id"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
            "enabled_at": doc.get("enabled_at"),
            "enabled_by": doc.get("enabled_by")
        }

    # ==================
    # Index Creation
    # ==================

    async def create_indexes(self):
        """Create MongoDB indexes for optimal performance."""
        # Default hooks indexes
        await self._default_hooks.create_index("name", unique=True)
        await self._default_hooks.create_index("is_active")
        await self._default_hooks.create_index("is_favorite")
        await self._default_hooks.create_index("category")

        # Custom hooks indexes
        await self._custom_hooks.create_index("project_id")
        await self._custom_hooks.create_index([("project_id", 1), ("name", 1)], unique=True)
        await self._custom_hooks.create_index("is_favorite")
        await self._custom_hooks.create_index("status")

        # Project hooks (junction) indexes
        await self._project_hooks.create_index("project_id")
        await self._project_hooks.create_index([
            ("project_id", 1),
            ("hook_id", 1),
            ("hook_type", 1)
        ], unique=True)
