"""Subagent repository implementations for MongoDB storage"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

from .base import BaseRepository


class MongoDBSubagentRepository(BaseRepository):
    """
    MongoDB implementation of subagent repository.

    Manages four collections:
    - default_subagents: Framework-provided subagents (global)
    - custom_subagents: User-created subagents (per project)
    - project_subagents: Junction table for enabled subagents per project
    - subagent_skills: Junction table for skills assigned to subagents
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB subagent repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._default_subagents = db["default_subagents"]
        self._custom_subagents = db["custom_subagents"]
        self._project_subagents = db["project_subagents"]
        self._subagent_skills = db["subagent_skills"]

    # ==================
    # BaseRepository Implementation
    # ==================

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get subagent by ID (checks both default and custom)."""
        # Try default first
        doc = await self._default_subagents.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_subagent(doc, "default")

        # Try custom
        doc = await self._custom_subagents.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_subagent(doc, "custom")

        return None

    async def create(self, entity: Any) -> str:
        """Create new subagent."""
        doc = self._subagent_to_doc(entity)
        result = await self._custom_subagents.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing subagent."""
        subagent_id = entity.get("id") if isinstance(entity, dict) else entity.id
        subagent_kind = entity.get("subagent_kind", "custom") if isinstance(entity, dict) else getattr(entity, "subagent_kind", "custom")

        doc = self._subagent_to_doc(entity)
        doc.pop("_id", None)

        collection = self._default_subagents if subagent_kind == "default" else self._custom_subagents
        await collection.update_one(
            {"_id": ObjectId(subagent_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete subagent by ID."""
        await self._default_subagents.delete_one({"_id": ObjectId(id)})
        await self._custom_subagents.delete_one({"_id": ObjectId(id)})
        await self._project_subagents.delete_many({"subagent_id": id})
        await self._subagent_skills.delete_many({"subagent_id": id})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List subagents with pagination and filters."""
        results = []

        # Get default subagents
        query = {"is_active": True}
        cursor = self._default_subagents.find(query).skip(skip).limit(limit)
        async for doc in cursor:
            results.append(self._doc_to_subagent(doc, "default"))

        # Get custom subagents if project_id filter provided
        if filters and "project_id" in filters:
            query = {"project_id": filters["project_id"]}
            cursor = self._custom_subagents.find(query).skip(skip).limit(limit)
            async for doc in cursor:
                results.append(self._doc_to_subagent(doc, "custom"))

        return results

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count subagents."""
        default_count = await self._default_subagents.count_documents({"is_active": True})

        custom_count = 0
        if filters and "project_id" in filters:
            custom_count = await self._custom_subagents.count_documents({"project_id": filters["project_id"]})

        return default_count + custom_count

    # ==================
    # Default Subagents Methods
    # ==================

    async def get_all_default_subagents(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get all default subagents."""
        query = {"is_active": is_active}
        cursor = self._default_subagents.find(query).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_subagent(doc, "default") for doc in docs]

    async def get_default_subagent(self, subagent_id: str) -> Optional[Dict[str, Any]]:
        """Get default subagent by ID."""
        try:
            doc = await self._default_subagents.find_one({"_id": ObjectId(subagent_id)})
            if doc:
                return self._doc_to_subagent(doc, "default")
        except Exception:
            pass
        return None

    async def get_default_subagent_by_type(self, subagent_type: str) -> Optional[Dict[str, Any]]:
        """Get default subagent by type."""
        doc = await self._default_subagents.find_one({"subagent_type": subagent_type})
        if doc:
            return self._doc_to_subagent(doc, "default")
        return None

    async def create_default_subagent(self, subagent: Dict[str, Any]) -> str:
        """Create new default subagent."""
        doc = {
            "name": subagent["name"],
            "description": subagent["description"],
            "category": subagent.get("category", "General"),
            "subagent_type": subagent["subagent_type"],
            "config": subagent.get("config"),
            "tools_available": subagent.get("tools_available", []),
            "recommended_for": subagent.get("recommended_for", []),
            "is_active": subagent.get("is_active", True),
            "is_favorite": subagent.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._default_subagents.insert_one(doc)
        return str(result.inserted_id)

    async def update_default_subagent(self, subagent_id: str, updates: Dict[str, Any]) -> None:
        """Update default subagent."""
        updates["updated_at"] = datetime.utcnow()
        await self._default_subagents.update_one(
            {"_id": ObjectId(subagent_id)},
            {"$set": updates}
        )

    async def get_favorite_default_subagents(self) -> List[Dict[str, Any]]:
        """Get all favorite default subagents."""
        cursor = self._default_subagents.find({"is_favorite": True, "is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_subagent(doc, "default") for doc in docs]

    # ==================
    # Custom Subagents Methods
    # ==================

    async def get_custom_subagents(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all custom subagents for a project."""
        cursor = self._custom_subagents.find({"project_id": project_id}).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_subagent(doc, "custom") for doc in docs]

    async def get_custom_subagent(self, subagent_id: str) -> Optional[Dict[str, Any]]:
        """Get custom subagent by ID."""
        try:
            doc = await self._custom_subagents.find_one({"_id": ObjectId(subagent_id)})
            if doc:
                return self._doc_to_subagent(doc, "custom")
        except Exception:
            pass
        return None

    async def get_custom_subagent_by_name(self, project_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get custom subagent by name within a project."""
        doc = await self._custom_subagents.find_one({
            "project_id": project_id,
            "name": name
        })
        if doc:
            return self._doc_to_subagent(doc, "custom")
        return None

    async def get_custom_subagent_by_type(self, project_id: str, subagent_type: str) -> Optional[Dict[str, Any]]:
        """Get custom subagent by type within a project."""
        doc = await self._custom_subagents.find_one({
            "project_id": project_id,
            "subagent_type": subagent_type
        })
        if doc:
            return self._doc_to_subagent(doc, "custom")
        return None

    async def create_custom_subagent(self, subagent: Dict[str, Any]) -> str:
        """Create new custom subagent."""
        doc = {
            "project_id": subagent["project_id"],
            "name": subagent["name"],
            "description": subagent["description"],
            "category": subagent.get("category", "Custom"),
            "subagent_type": subagent["subagent_type"],
            "config": subagent.get("config"),
            "tools_available": subagent.get("tools_available", []),
            "status": subagent.get("status", "creating"),
            "error_message": subagent.get("error_message"),
            "created_by": subagent.get("created_by", "user"),
            "is_favorite": subagent.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._custom_subagents.insert_one(doc)
        return str(result.inserted_id)

    async def update_custom_subagent(self, subagent_id: str, updates: Dict[str, Any]) -> None:
        """Update custom subagent."""
        updates["updated_at"] = datetime.utcnow()
        await self._custom_subagents.update_one(
            {"_id": ObjectId(subagent_id)},
            {"$set": updates}
        )

    async def delete_custom_subagent(self, subagent_id: str) -> None:
        """Delete custom subagent permanently."""
        await self._custom_subagents.delete_one({"_id": ObjectId(subagent_id)})
        await self._project_subagents.delete_many({
            "subagent_id": subagent_id,
            "subagent_type": "custom"
        })
        await self._subagent_skills.delete_many({
            "subagent_id": subagent_id,
            "subagent_type": "custom"
        })

    async def get_favorite_custom_subagents(self) -> List[Dict[str, Any]]:
        """Get all favorite custom subagents across all projects."""
        cursor = self._custom_subagents.find({"is_favorite": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_subagent(doc, "custom") for doc in docs]

    # ==================
    # Project Subagents (Junction) Methods
    # ==================

    async def get_enabled_subagents(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all enabled subagents for a project."""
        cursor = self._project_subagents.find({"project_id": project_id})
        enabled_records = await cursor.to_list(length=1000)

        subagents = []
        for record in enabled_records:
            subagent_id = record["subagent_id"]
            subagent_type = record["subagent_type"]

            if subagent_type == "default":
                subagent = await self.get_default_subagent(subagent_id)
            else:
                subagent = await self.get_custom_subagent(subagent_id)

            if subagent:
                subagent["is_enabled"] = True
                subagent["enabled_at"] = record.get("enabled_at")
                subagent["enabled_by"] = record.get("enabled_by")
                subagents.append(subagent)

        return subagents

    async def is_subagent_enabled(
        self,
        project_id: str,
        subagent_id: str,
        subagent_type: str
    ) -> bool:
        """Check if subagent is enabled for project."""
        doc = await self._project_subagents.find_one({
            "project_id": project_id,
            "subagent_id": subagent_id,
            "subagent_type": subagent_type
        })
        return doc is not None

    async def enable_subagent(
        self,
        project_id: str,
        subagent_id: str,
        subagent_type: str,
        enabled_by: str = "user"
    ) -> str:
        """Enable subagent for a project."""
        existing = await self._project_subagents.find_one({
            "project_id": project_id,
            "subagent_id": subagent_id,
            "subagent_type": subagent_type
        })
        if existing:
            return str(existing["_id"])

        doc = {
            "project_id": project_id,
            "subagent_id": subagent_id,
            "subagent_type": subagent_type,
            "enabled_at": datetime.utcnow(),
            "enabled_by": enabled_by
        }
        result = await self._project_subagents.insert_one(doc)
        return str(result.inserted_id)

    async def disable_subagent(
        self,
        project_id: str,
        subagent_id: str,
        subagent_type: str
    ) -> bool:
        """Disable subagent for a project."""
        result = await self._project_subagents.delete_one({
            "project_id": project_id,
            "subagent_id": subagent_id,
            "subagent_type": subagent_type
        })
        return result.deleted_count > 0

    async def disable_all_subagents(self, project_id: str) -> int:
        """Disable all subagents for a project."""
        result = await self._project_subagents.delete_many({"project_id": project_id})
        return result.deleted_count

    async def get_enabled_subagent_ids(self, project_id: str) -> set:
        """Get set of (subagent_id, subagent_type) tuples for enabled subagents."""
        cursor = self._project_subagents.find(
            {"project_id": project_id},
            {"subagent_id": 1, "subagent_type": 1}
        )
        docs = await cursor.to_list(length=1000)
        return {(doc["subagent_id"], doc["subagent_type"]) for doc in docs}

    # ==================
    # Subagent Skills Methods
    # ==================

    async def get_subagent_skills(
        self,
        subagent_id: str,
        subagent_type: str
    ) -> List[Dict[str, Any]]:
        """Get all skills assigned to a subagent."""
        cursor = self._subagent_skills.find({
            "subagent_id": subagent_id,
            "subagent_type": subagent_type
        })
        docs = await cursor.to_list(length=100)
        return docs

    async def assign_skill(
        self,
        subagent_id: str,
        subagent_type: str,
        skill_id: str,
        skill_type: str,
        assigned_by: str = "user"
    ) -> str:
        """Assign a skill to a subagent."""
        existing = await self._subagent_skills.find_one({
            "subagent_id": subagent_id,
            "subagent_type": subagent_type,
            "skill_id": skill_id,
            "skill_type": skill_type
        })
        if existing:
            return str(existing["_id"])

        doc = {
            "subagent_id": subagent_id,
            "subagent_type": subagent_type,
            "skill_id": skill_id,
            "skill_type": skill_type,
            "assigned_at": datetime.utcnow(),
            "assigned_by": assigned_by
        }
        result = await self._subagent_skills.insert_one(doc)
        return str(result.inserted_id)

    async def unassign_skill(
        self,
        subagent_id: str,
        subagent_type: str,
        skill_id: str,
        skill_type: str
    ) -> bool:
        """Remove skill assignment from subagent."""
        result = await self._subagent_skills.delete_one({
            "subagent_id": subagent_id,
            "subagent_type": subagent_type,
            "skill_id": skill_id,
            "skill_type": skill_type
        })
        return result.deleted_count > 0

    async def clear_subagent_skills(
        self,
        subagent_id: str,
        subagent_type: str
    ) -> int:
        """Remove all skills from a subagent."""
        result = await self._subagent_skills.delete_many({
            "subagent_id": subagent_id,
            "subagent_type": subagent_type
        })
        return result.deleted_count

    # ==================
    # Utility Methods
    # ==================

    def _subagent_to_doc(self, subagent: Any) -> Dict[str, Any]:
        """Convert subagent to MongoDB document."""
        if isinstance(subagent, dict):
            doc = subagent.copy()
            if "id" in doc:
                doc["_id"] = ObjectId(doc.pop("id"))
            return doc

        return {
            "name": subagent.name,
            "description": subagent.description,
            "category": subagent.category,
            "subagent_type": subagent.subagent_type,
            "config": getattr(subagent, "config", None),
            "tools_available": getattr(subagent, "tools_available", []),
            "recommended_for": getattr(subagent, "recommended_for", []),
            "is_active": getattr(subagent, "is_active", True),
            "is_favorite": getattr(subagent, "is_favorite", False),
            "status": getattr(subagent, "status", None),
            "error_message": getattr(subagent, "error_message", None),
            "created_by": getattr(subagent, "created_by", "system"),
            "created_at": subagent.created_at,
            "updated_at": subagent.updated_at
        }

    def _doc_to_subagent(self, doc: Dict[str, Any], subagent_kind: str) -> Dict[str, Any]:
        """Convert MongoDB document to subagent dict."""
        return {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc["description"],
            "subagent_kind": subagent_kind,
            "category": doc.get("category", "General"),
            "subagent_type": doc.get("subagent_type"),
            "config": doc.get("config"),
            "tools_available": doc.get("tools_available", []),
            "recommended_for": doc.get("recommended_for", []),
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
        # Default subagents indexes
        await self._default_subagents.create_index("subagent_type", unique=True)
        await self._default_subagents.create_index("name")
        await self._default_subagents.create_index("is_active")
        await self._default_subagents.create_index("is_favorite")
        await self._default_subagents.create_index("category")

        # Custom subagents indexes
        await self._custom_subagents.create_index("project_id")
        await self._custom_subagents.create_index([("project_id", 1), ("name", 1)], unique=True)
        await self._custom_subagents.create_index([("project_id", 1), ("subagent_type", 1)], unique=True)
        await self._custom_subagents.create_index("is_favorite")
        await self._custom_subagents.create_index("status")

        # Project subagents (junction) indexes
        await self._project_subagents.create_index("project_id")
        await self._project_subagents.create_index([
            ("project_id", 1),
            ("subagent_id", 1),
            ("subagent_type", 1)
        ], unique=True)

        # Subagent skills indexes
        await self._subagent_skills.create_index([
            ("subagent_id", 1),
            ("subagent_type", 1)
        ])
        await self._subagent_skills.create_index([
            ("subagent_id", 1),
            ("subagent_type", 1),
            ("skill_id", 1),
            ("skill_type", 1)
        ], unique=True)
