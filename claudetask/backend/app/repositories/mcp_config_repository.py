"""MCP Config repository implementations for MongoDB storage"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

from .base import BaseRepository


class MongoDBMCPConfigRepository(BaseRepository):
    """
    MongoDB implementation of MCP config repository.

    Manages three collections:
    - default_mcp_configs: Framework-provided MCP configs (global)
    - custom_mcp_configs: User-created MCP configs (per project)
    - project_mcp_configs: Junction table for enabled configs per project
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize MongoDB MCP config repository.

        Args:
            db: Motor async database instance
        """
        self._db = db
        self._default_mcp_configs = db["default_mcp_configs"]
        self._custom_mcp_configs = db["custom_mcp_configs"]
        self._project_mcp_configs = db["project_mcp_configs"]

    # ==================
    # BaseRepository Implementation
    # ==================

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get MCP config by ID (checks both default and custom)."""
        # Try default first
        doc = await self._default_mcp_configs.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_config(doc, "default")

        # Try custom
        doc = await self._custom_mcp_configs.find_one({"_id": ObjectId(id)})
        if doc:
            return self._doc_to_config(doc, "custom")

        return None

    async def create(self, entity: Any) -> str:
        """Create new MCP config."""
        doc = self._config_to_doc(entity)
        result = await self._custom_mcp_configs.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity: Any) -> None:
        """Update existing MCP config."""
        config_id = entity.get("id") if isinstance(entity, dict) else entity.id
        config_type = entity.get("mcp_config_type", "custom") if isinstance(entity, dict) else getattr(entity, "mcp_config_type", "custom")

        doc = self._config_to_doc(entity)
        doc.pop("_id", None)

        collection = self._default_mcp_configs if config_type == "default" else self._custom_mcp_configs
        await collection.update_one(
            {"_id": ObjectId(config_id)},
            {"$set": doc}
        )

    async def delete(self, id: str) -> None:
        """Delete MCP config by ID."""
        await self._default_mcp_configs.delete_one({"_id": ObjectId(id)})
        await self._custom_mcp_configs.delete_one({"_id": ObjectId(id)})
        await self._project_mcp_configs.delete_many({"mcp_config_id": id})

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List MCP configs with pagination and filters."""
        results = []

        # Get default configs
        query = {"is_active": True}
        cursor = self._default_mcp_configs.find(query).skip(skip).limit(limit)
        async for doc in cursor:
            results.append(self._doc_to_config(doc, "default"))

        # Get custom configs if project_id filter provided
        if filters and "project_id" in filters:
            query = {"project_id": filters["project_id"]}
            cursor = self._custom_mcp_configs.find(query).skip(skip).limit(limit)
            async for doc in cursor:
                results.append(self._doc_to_config(doc, "custom"))

        return results

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count MCP configs."""
        default_count = await self._default_mcp_configs.count_documents({"is_active": True})

        custom_count = 0
        if filters and "project_id" in filters:
            custom_count = await self._custom_mcp_configs.count_documents({"project_id": filters["project_id"]})

        return default_count + custom_count

    # ==================
    # Default MCP Configs Methods
    # ==================

    async def get_all_default_configs(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get all default MCP configs."""
        query = {"is_active": is_active}
        cursor = self._default_mcp_configs.find(query).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_config(doc, "default") for doc in docs]

    async def get_default_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get default MCP config by ID."""
        try:
            doc = await self._default_mcp_configs.find_one({"_id": ObjectId(config_id)})
            if doc:
                return self._doc_to_config(doc, "default")
        except Exception:
            pass
        return None

    async def get_default_config_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get default MCP config by name."""
        doc = await self._default_mcp_configs.find_one({"name": name})
        if doc:
            return self._doc_to_config(doc, "default")
        return None

    async def create_default_config(self, config: Dict[str, Any]) -> str:
        """Create new default MCP config."""
        doc = {
            "name": config["name"],
            "description": config["description"],
            "category": config.get("category", "General"),
            "config": config["config"],
            "setup_instructions": config.get("setup_instructions"),
            "dependencies": config.get("dependencies"),
            "is_active": config.get("is_active", True),
            "is_favorite": config.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._default_mcp_configs.insert_one(doc)
        return str(result.inserted_id)

    async def update_default_config(self, config_id: str, updates: Dict[str, Any]) -> None:
        """Update default MCP config."""
        updates["updated_at"] = datetime.utcnow()
        await self._default_mcp_configs.update_one(
            {"_id": ObjectId(config_id)},
            {"$set": updates}
        )

    async def get_favorite_default_configs(self) -> List[Dict[str, Any]]:
        """Get all favorite default MCP configs."""
        cursor = self._default_mcp_configs.find({"is_favorite": True, "is_active": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_config(doc, "default") for doc in docs]

    # ==================
    # Custom MCP Configs Methods
    # ==================

    async def get_custom_configs(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all custom MCP configs for a project."""
        cursor = self._custom_mcp_configs.find({"project_id": project_id}).sort("name", 1)
        docs = await cursor.to_list(length=1000)
        return [self._doc_to_config(doc, "custom") for doc in docs]

    async def get_custom_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get custom MCP config by ID."""
        try:
            doc = await self._custom_mcp_configs.find_one({"_id": ObjectId(config_id)})
            if doc:
                return self._doc_to_config(doc, "custom")
        except Exception:
            pass
        return None

    async def get_custom_config_by_name(self, project_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get custom MCP config by name within a project."""
        doc = await self._custom_mcp_configs.find_one({
            "project_id": project_id,
            "name": name
        })
        if doc:
            return self._doc_to_config(doc, "custom")
        return None

    async def get_imported_config(self, project_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Get imported MCP config by name within a project."""
        doc = await self._custom_mcp_configs.find_one({
            "project_id": project_id,
            "name": name,
            "category": "imported"
        })
        if doc:
            return self._doc_to_config(doc, "custom")
        return None

    async def create_custom_config(self, config: Dict[str, Any]) -> str:
        """Create new custom MCP config."""
        doc = {
            "project_id": config["project_id"],
            "name": config["name"],
            "description": config["description"],
            "category": config.get("category", "Custom"),
            "config": config.get("config", {}),
            "setup_instructions": config.get("setup_instructions"),
            "dependencies": config.get("dependencies"),
            "status": config.get("status", "active"),
            "error_message": config.get("error_message"),
            "created_by": config.get("created_by", "user"),
            "is_favorite": config.get("is_favorite", False),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self._custom_mcp_configs.insert_one(doc)
        return str(result.inserted_id)

    async def update_custom_config(self, config_id: str, updates: Dict[str, Any]) -> None:
        """Update custom MCP config."""
        updates["updated_at"] = datetime.utcnow()
        await self._custom_mcp_configs.update_one(
            {"_id": ObjectId(config_id)},
            {"$set": updates}
        )

    async def delete_custom_config(self, config_id: str) -> None:
        """Delete custom MCP config permanently."""
        await self._custom_mcp_configs.delete_one({"_id": ObjectId(config_id)})
        await self._project_mcp_configs.delete_many({
            "mcp_config_id": config_id,
            "mcp_config_type": "custom"
        })

    async def get_favorite_custom_configs(self) -> List[Dict[str, Any]]:
        """Get all favorite custom MCP configs across all projects."""
        cursor = self._custom_mcp_configs.find({"is_favorite": True})
        docs = await cursor.to_list(length=100)
        return [self._doc_to_config(doc, "custom") for doc in docs]

    # ==================
    # Project MCP Configs (Junction) Methods
    # ==================

    async def get_enabled_configs(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all enabled MCP configs for a project."""
        cursor = self._project_mcp_configs.find({"project_id": project_id})
        enabled_records = await cursor.to_list(length=1000)

        configs = []
        for record in enabled_records:
            config_id = record["mcp_config_id"]
            config_type = record["mcp_config_type"]

            if config_type == "default":
                config = await self.get_default_config(config_id)
            else:
                config = await self.get_custom_config(config_id)

            if config:
                config["is_enabled"] = True
                config["enabled_at"] = record.get("enabled_at")
                config["enabled_by"] = record.get("enabled_by")
                configs.append(config)

        return configs

    async def is_config_enabled(
        self,
        project_id: str,
        config_id: str,
        config_type: str
    ) -> bool:
        """Check if MCP config is enabled for project."""
        doc = await self._project_mcp_configs.find_one({
            "project_id": project_id,
            "mcp_config_id": config_id,
            "mcp_config_type": config_type
        })
        return doc is not None

    async def enable_config(
        self,
        project_id: str,
        config_id: str,
        config_type: str,
        enabled_by: str = "user"
    ) -> str:
        """Enable MCP config for a project."""
        existing = await self._project_mcp_configs.find_one({
            "project_id": project_id,
            "mcp_config_id": config_id,
            "mcp_config_type": config_type
        })
        if existing:
            return str(existing["_id"])

        doc = {
            "project_id": project_id,
            "mcp_config_id": config_id,
            "mcp_config_type": config_type,
            "enabled_at": datetime.utcnow(),
            "enabled_by": enabled_by
        }
        result = await self._project_mcp_configs.insert_one(doc)
        return str(result.inserted_id)

    async def disable_config(
        self,
        project_id: str,
        config_id: str,
        config_type: str
    ) -> bool:
        """Disable MCP config for a project."""
        result = await self._project_mcp_configs.delete_one({
            "project_id": project_id,
            "mcp_config_id": config_id,
            "mcp_config_type": config_type
        })
        return result.deleted_count > 0

    async def disable_all_configs(self, project_id: str) -> int:
        """Disable all MCP configs for a project."""
        result = await self._project_mcp_configs.delete_many({"project_id": project_id})
        return result.deleted_count

    async def get_enabled_config_ids(self, project_id: str) -> set:
        """Get set of (config_id, config_type) tuples for enabled configs."""
        cursor = self._project_mcp_configs.find(
            {"project_id": project_id},
            {"mcp_config_id": 1, "mcp_config_type": 1}
        )
        docs = await cursor.to_list(length=1000)
        return {(doc["mcp_config_id"], doc["mcp_config_type"]) for doc in docs}

    async def get_all_enabled_project_configs(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all ProjectMCPConfig records for a project."""
        cursor = self._project_mcp_configs.find({"project_id": project_id})
        docs = await cursor.to_list(length=1000)
        return docs

    # ==================
    # Utility Methods
    # ==================

    def _config_to_doc(self, config: Any) -> Dict[str, Any]:
        """Convert MCP config to MongoDB document."""
        if isinstance(config, dict):
            doc = config.copy()
            if "id" in doc:
                doc["_id"] = ObjectId(doc.pop("id"))
            return doc

        return {
            "name": config.name,
            "description": config.description,
            "category": config.category,
            "config": config.config,
            "setup_instructions": getattr(config, "setup_instructions", None),
            "dependencies": getattr(config, "dependencies", None),
            "is_active": getattr(config, "is_active", True),
            "is_favorite": getattr(config, "is_favorite", False),
            "status": getattr(config, "status", None),
            "error_message": getattr(config, "error_message", None),
            "created_by": getattr(config, "created_by", "system"),
            "created_at": config.created_at,
            "updated_at": config.updated_at
        }

    def _doc_to_config(self, doc: Dict[str, Any], config_type: str) -> Dict[str, Any]:
        """Convert MongoDB document to MCP config dict."""
        return {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "description": doc["description"],
            "mcp_config_type": config_type,
            "category": doc.get("category", "General"),
            "config": doc.get("config", {}),
            "setup_instructions": doc.get("setup_instructions"),
            "dependencies": doc.get("dependencies"),
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
        # Default MCP configs indexes
        await self._default_mcp_configs.create_index("name", unique=True)
        await self._default_mcp_configs.create_index("is_active")
        await self._default_mcp_configs.create_index("is_favorite")
        await self._default_mcp_configs.create_index("category")

        # Custom MCP configs indexes
        await self._custom_mcp_configs.create_index("project_id")
        await self._custom_mcp_configs.create_index([("project_id", 1), ("name", 1)], unique=True)
        await self._custom_mcp_configs.create_index("is_favorite")
        await self._custom_mcp_configs.create_index("status")
        await self._custom_mcp_configs.create_index("category")

        # Project MCP configs (junction) indexes
        await self._project_mcp_configs.create_index("project_id")
        await self._project_mcp_configs.create_index([
            ("project_id", 1),
            ("mcp_config_id", 1),
            ("mcp_config_type", 1)
        ], unique=True)
