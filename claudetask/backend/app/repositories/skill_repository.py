"""Skill repository implementations for MongoDB storage"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

from .base import BaseRepository


class MongoDBSkillRepository(BaseRepository):
    """
    MongoDB implementation of skill repository.

    Manages three collections:
    - default_skills: Framework-provided skills (global)
    - custom_skills: User-created skills (per project)
    - project_skills: Junction table for enabled skills per project
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB skill repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._default_skills = db["default_skills"]
        self._custom_skills = db["custom_skills"]
        self._project_skills = db["project_skills"]

    # ==================
    # BaseRepository Implementation
    # ==================

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get skill by ID (checks both default and custom)."""
        # Try default first
        doc = await self._default_skills.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_skill(doc, "default")

        # Try custom
        doc = await self._custom_skills.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_skill(doc, "custom")

        return None

    async def create(self, entity: Any) -> str:
        """Create new skill."""
        doc = self._skill_to_doc(entity)
        result = await self._custom_skills.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing skill."""
        skill_id = entity.get("id") if isinstance(entity, dict) else entity.id
        skill_type = entity.get("skill_type", "custom") if isinstance(entity, dict) else getattr(entity, "skill_type", "custom")

        doc = self._skill_to_doc(entity)
        doc.pop("_id", None)  # Remove _id from update

        collection = self._default_skills if skill_type == "default" else self._custom_skills
        await collection.update_one(
            {"_id": ObjectId(skill_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete skill by ID."""
        # Try both collections
        await self._default_skills.delete_one({"_id": ObjectId(id)})
        await self._custom_skills.delete_one({"_id": ObjectId(id)})
        # Also remove from project_skills
        await self._project_skills.delete_many({"skill_id": id})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List skills with pagination and filters."""
        results = []

        # Get default skills
        query = {"is_active": True}
        cursor = self._default_skills.find(query).skip(skip).limit(limit)
        async for doc in cursor:
            results.append(self._doc_to_skill(doc, "default"))

        # Get custom skills if project_id filter provided
        if filters and "project_id" in filters:
            query = {"project_id": filters["project_id"]}
            cursor = self._custom_skills.find(query).skip(skip).limit(limit)
            async for doc in cursor:
                results.append(self._doc_to_skill(doc, "custom"))

        return results

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count skills."""
        default_count = await self._default_skills.count_documents({"is_active": True})

        custom_count = 0
        if filters and "project_id" in filters:
            custom_count = await self._custom_skills.count_documents({"project_id": filters["project_id"]})

        return default_count + custom_count

    # ==================
    # Default Skills Methods
    # ==================

    async def get_all_default_skills(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """
        Get all default skills.

        Args:
            is_active: Filter by active status

        Returns:
            List of default skill dicts
        """
        query = {"is_active": is_active}
        cursor = self._default_skills.find(query).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_skill(doc, "default") for doc in docs]

    async def get_default_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get default skill by ID."""
        try:
            doc = await self._default_skills.find_one({"_id": ObjectId(skill_id)})
            if doc:
                return self._doc_to_skill(doc, "default")
        except Exception:
            pass
        return None

    async def get_default_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get default skill by name."""
        doc = await self._default_skills.find_one({"name": name})
        if doc:
            return self._doc_to_skill(doc, "default")
        return None

    async def create_default_skill(self, skill: Dict[str, Any]) -> str:
        """Create new default skill."""
        doc = {
            "name": skill["name"],
            "description": skill["description"],
            "category": skill.get("category", "General"),
            "file_name": skill["file_name"],
            "content": skill.get("content"),
            "skill_metadata": skill.get("skill_metadata"),
            "is_active": skill.get("is_active", True),
            "is_favorite": skill.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._default_skills.insert_one(doc)
        return str(result.inserted_id)

    async def update_default_skill(self, skill_id: str, updates: Dict[str, Any]) -> None:
        """Update default skill."""
        updates["updated_at"] = datetime.utcnow()
        await self._default_skills.update_one(
            {"_id": ObjectId(skill_id)},
            {"$set": updates}
        )

    async def get_favorite_default_skills(self) -> List[Dict[str, Any]]:
        """Get all favorite default skills."""
        cursor = self._default_skills.find({"is_favorite": True, "is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_skill(doc, "default") for doc in docs]

    # ==================
    # Custom Skills Methods
    # ==================

    async def get_custom_skills(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all custom skills for a project.

        Args:
            project_id: Project ID

        Returns:
            List of custom skill dicts
        """
        cursor = self._custom_skills.find({"project_id": project_id}).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_skill(doc, "custom") for doc in docs]

    async def get_custom_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Get custom skill by ID."""
        try:
            doc = await self._custom_skills.find_one({"_id": ObjectId(skill_id)})
            if doc:
                return self._doc_to_skill(doc, "custom")
        except Exception:
            pass
        return None

    async def get_custom_skill_by_name(self, project_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get custom skill by name within a project."""
        doc = await self._custom_skills.find_one({
            "project_id": project_id,
            "name": name
        })
        if doc:
            return self._doc_to_skill(doc, "custom")
        return None

    async def create_custom_skill(self, skill: Dict[str, Any]) -> str:
        """
        Create new custom skill.

        Args:
            skill: Skill data dict

        Returns:
            ID of created skill
        """
        doc = {
            "project_id": skill["project_id"],
            "name": skill["name"],
            "description": skill["description"],
            "category": skill.get("category", "Custom"),
            "file_name": skill["file_name"],
            "content": skill.get("content"),
            "status": skill.get("status", "creating"),
            "error_message": skill.get("error_message"),
            "created_by": skill.get("created_by", "user"),
            "is_favorite": skill.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._custom_skills.insert_one(doc)
        return str(result.inserted_id)

    async def update_custom_skill(self, skill_id: str, updates: Dict[str, Any]) -> None:
        """
        Update custom skill.

        Args:
            skill_id: Skill ID
            updates: Fields to update
        """
        updates["updated_at"] = datetime.utcnow()
        await self._custom_skills.update_one(
            {"_id": ObjectId(skill_id)},
            {"$set": updates}
        )

    async def delete_custom_skill(self, skill_id: str) -> None:
        """
        Delete custom skill permanently.

        Args:
            skill_id: Skill ID to delete
        """
        await self._custom_skills.delete_one({"_id": ObjectId(skill_id)})
        # Also remove from project_skills
        await self._project_skills.delete_many({
            "skill_id": skill_id,
            "skill_type": "custom"
        })

    async def get_favorite_custom_skills(self) -> List[Dict[str, Any]]:
        """Get all favorite custom skills across all projects."""
        cursor = self._custom_skills.find({"is_favorite": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_skill(doc, "custom") for doc in docs]

    # ==================
    # Project Skills (Junction) Methods
    # ==================

    async def get_enabled_skills(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get all enabled skills for a project.

        Args:
            project_id: Project ID

        Returns:
            List of enabled skills with full details
        """
        cursor = self._project_skills.find({"project_id": project_id})
        enabled_records = await cursor.to_list(length=1000)

        skills = []
        for record in enabled_records:
            skill_id = record["skill_id"]
            skill_type = record["skill_type"]

            if skill_type == "default":
                skill = await self.get_default_skill(skill_id)
            else:
                skill = await self.get_custom_skill(skill_id)

            if skill:
                skill["is_enabled"] = True
                skill["enabled_at"] = record.get("enabled_at")
                skill["enabled_by"] = record.get("enabled_by")
                skills.append(skill)

        return skills

    async def is_skill_enabled(
        self,
        project_id: str,
        skill_id: str,
        skill_type: str
    ) -> bool:
        """
        Check if skill is enabled for project.

        Args:
            project_id: Project ID
            skill_id: Skill ID
            skill_type: "default" or "custom"

        Returns:
            True if enabled
        """
        doc = await self._project_skills.find_one({
            "project_id": project_id,
            "skill_id": skill_id,
            "skill_type": skill_type
        })
        return doc is not None

    async def enable_skill(
        self,
        project_id: str,
        skill_id: str,
        skill_type: str,
        enabled_by: str = "user"
    ) -> str:
        """
        Enable skill for a project.

        Args:
            project_id: Project ID
            skill_id: Skill ID
            skill_type: "default" or "custom"
            enabled_by: Who enabled it

        Returns:
            ID of project_skill record
        """
        # Check if already enabled
        existing = await self._project_skills.find_one({
            "project_id": project_id,
            "skill_id": skill_id,
            "skill_type": skill_type
        })
        if existing:
            return str(existing["_id"])

        doc = {
            "project_id": project_id,
            "skill_id": skill_id,
            "skill_type": skill_type,
            "enabled_at": datetime.utcnow(),
            "enabled_by": enabled_by
        }
        result = await self._project_skills.insert_one(doc)
        return str(result.inserted_id)

    async def disable_skill(
        self,
        project_id: str,
        skill_id: str,
        skill_type: str
    ) -> bool:
        """
        Disable skill for a project.

        Args:
            project_id: Project ID
            skill_id: Skill ID
            skill_type: "default" or "custom"

        Returns:
            True if successfully disabled
        """
        result = await self._project_skills.delete_one({
            "project_id": project_id,
            "skill_id": skill_id,
            "skill_type": skill_type
        })
        return result.deleted_count > 0

    async def disable_all_skills(self, project_id: str) -> int:
        """
        Disable all skills for a project.

        Args:
            project_id: Project ID

        Returns:
            Number of skills disabled
        """
        result = await self._project_skills.delete_many({"project_id": project_id})
        return result.deleted_count

    async def get_enabled_skill_ids(self, project_id: str) -> set:
        """
        Get set of (skill_id, skill_type) tuples for enabled skills.

        Args:
            project_id: Project ID

        Returns:
            Set of (skill_id, skill_type) tuples
        """
        cursor = self._project_skills.find(
            {"project_id": project_id},
            {"skill_id": 1, "skill_type": 1}
        )
        docs = await cursor.to_list(length=1000)
        return {(doc["skill_id"], doc["skill_type"]) for doc in docs}

    # ==================
    # Utility Methods
    # ==================

    def _skill_to_doc(self, skill: Any) -> Dict[str, Any]:
        """Convert skill to MongoDB document."""
        if isinstance(skill, dict):
            doc = skill.copy()
            if "id" in doc:
                doc["_id"] = ObjectId(doc.pop("id"))
            return doc

        return {
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
            "file_name": skill.file_name,
            "content": getattr(skill, "content", None),
            "is_active": getattr(skill, "is_active", True),
            "is_favorite": getattr(skill, "is_favorite", False),
            "status": getattr(skill, "status", None),
            "error_message": getattr(skill, "error_message", None),
            "created_by": getattr(skill, "created_by", "system"),
            "created_at": skill.created_at,
            "updated_at": skill.updated_at
        }

    def _doc_to_skill(self, doc: Dict[str, Any], skill_type: str) -> Dict[str, Any]:
        """Convert MongoDB document to skill dict."""
        return {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc["description"],
            "skill_type": skill_type,
            "category": doc.get("category", "General"),
            "file_name": doc.get("file_name"),
            "content": doc.get("content"),
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
        # Default skills indexes
        await self._default_skills.create_index("name", unique=True)
        await self._default_skills.create_index("is_active")
        await self._default_skills.create_index("is_favorite")
        await self._default_skills.create_index("category")

        # Custom skills indexes
        await self._custom_skills.create_index("project_id")
        await self._custom_skills.create_index([("project_id", 1), ("name", 1)], unique=True)
        await self._custom_skills.create_index("is_favorite")
        await self._custom_skills.create_index("status")

        # Project skills (junction) indexes
        await self._project_skills.create_index("project_id")
        await self._project_skills.create_index([
            ("project_id", 1),
            ("skill_id", 1),
            ("skill_type", 1)
        ], unique=True)
