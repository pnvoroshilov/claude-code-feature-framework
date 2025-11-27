"""Service for managing MCP configurations with MongoDB backend"""

import os
import logging
import copy
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from pathlib import Path

from ..repositories.mcp_config_repository import MongoDBMCPConfigRepository
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from .mcp_config_file_service import MCPConfigFileService

logger = logging.getLogger(__name__)


class MCPConfigServiceMongoDB:
    """Service for managing MCP configurations with MongoDB backend."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = MongoDBMCPConfigRepository(db)
        self.file_service = MCPConfigFileService()

    async def get_project_mcp_configs(
        self,
        project_id: str,
        project_path: str
    ) -> MCPConfigsResponse:
        """
        Get all MCP configs for a project organized by type.

        Returns:
        - enabled: Currently enabled MCP configs
        - available_default: Default MCP configs that can be enabled
        - custom: User-created custom MCP configs
        - favorites: Favorite MCP configs across all projects
        """
        # Get all default MCP configs
        all_default_configs = await self.repo.get_all_default_configs()

        # Get enabled config IDs for this project
        enabled_config_ids = await self.repo.get_enabled_config_ids(project_id)

        # Get custom configs for this project
        custom_configs = await self.repo.get_custom_configs(project_id)

        # Get ALL favorite custom configs (from all projects)
        all_favorite_custom_configs = await self.repo.get_favorite_custom_configs()

        # Organize configs
        enabled = []
        enabled_names = set()
        available_default = []
        favorites = []

        # Process default configs
        for config in all_default_configs:
            is_default_enabled = (config["id"], "default") in enabled_config_ids

            # Check if there's an imported config with same name that's enabled
            is_imported_enabled = False
            for custom_config in custom_configs:
                if custom_config.get("category") == "imported" and custom_config["name"] == config["name"]:
                    if (custom_config["id"], "custom") in enabled_config_ids:
                        is_imported_enabled = True
                        break

            is_enabled = is_default_enabled or is_imported_enabled
            config_dto = self._to_config_dto(config, is_enabled)

            # Add to default list
            available_default.append(config_dto)

            # Add to favorites if marked
            if config.get("is_favorite"):
                favorites.append(config_dto)

            # Add to enabled
            if is_enabled and config["name"] not in enabled_names:
                enabled.append(config_dto)
                enabled_names.add(config["name"])

        # Process custom configs
        custom_dtos = []
        for config in custom_configs:
            # Skip imported configs
            if config.get("category") == "imported":
                continue

            is_enabled = (config["id"], "custom") in enabled_config_ids
            config_dto = self._to_config_dto(config, is_enabled)

            custom_dtos.append(config_dto)

            if is_enabled and config["name"] not in enabled_names:
                enabled.append(config_dto)
                enabled_names.add(config["name"])

        # Process favorite custom configs
        favorite_names = {f.name for f in favorites}
        for config in all_favorite_custom_configs:
            if config.get("category") == "imported":
                continue

            is_enabled = (config["id"], "custom") in enabled_config_ids
            config_dto = self._to_config_dto(config, is_enabled)

            if config["name"] not in favorite_names:
                favorites.append(config_dto)
                favorite_names.add(config["name"])

        return MCPConfigsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_mcp_config(
        self,
        project_id: str,
        project_path: str,
        config_id: str,
        config_type: str = "default"
    ) -> MCPConfigInDB:
        """Enable an MCP config by writing it to project's .mcp.json."""

        # Get the config
        if config_type == "default":
            config = await self.repo.get_default_config(config_id)
            if not config:
                raise ValueError(f"Default MCP config {config_id} not found")

            # Check for imported config with same name
            imported_config = await self.repo.get_imported_config(project_id, config["name"])
            if imported_config:
                config = imported_config
                actual_config_id = imported_config["id"]
                actual_config_type = "custom"
                logger.info(f"Found imported config for {config['name']}, using imported version")
            else:
                actual_config_id = config_id
                actual_config_type = "default"
        else:
            config = await self.repo.get_custom_config(config_id)
            if not config:
                raise ValueError(f"Custom MCP config {config_id} not found")
            actual_config_id = config_id
            actual_config_type = "custom"

        # Check if already enabled
        if await self.repo.is_config_enabled(project_id, actual_config_id, actual_config_type):
            raise ValueError(f"MCP config already enabled for project")

        # Prepare config for project
        config_data = self._prepare_mcp_config_for_project(
            base_config=config.get("config", {}),
            mcp_config_name=config["name"],
            project_path=project_path,
            project_id=project_id
        )

        # Write to .mcp.json
        success = await self.file_service.merge_mcp_config_to_project(
            project_path=project_path,
            mcp_config_name=config["name"],
            config_data=config_data
        )

        if not success:
            raise RuntimeError(f"Failed to merge MCP config to project")

        # Enable in database
        await self.repo.enable_config(project_id, actual_config_id, actual_config_type)

        logger.info(f"Enabled MCP config {config['name']} for project {project_id}")

        return self._to_config_dto(config, True)

    async def disable_mcp_config(
        self,
        project_id: str,
        project_path: str,
        config_id: str,
        config_type: str = "default"
    ):
        """Disable an MCP config by removing it from project."""

        # Get config name
        if config_type == "default":
            config = await self.repo.get_default_config(config_id)
            if not config:
                raise ValueError(f"Default MCP config {config_id} not found")
            mcp_name = config["name"]

            # Check for imported config too
            imported_config = await self.repo.get_imported_config(project_id, mcp_name)
            if imported_config:
                await self.repo.disable_config(project_id, imported_config["id"], "custom")
        else:
            config = await self.repo.get_custom_config(config_id)
            if not config:
                raise ValueError(f"Custom MCP config {config_id} not found")
            mcp_name = config["name"]

        # Remove from .mcp.json
        await self.file_service.remove_mcp_config_from_project(
            project_path=project_path,
            mcp_config_name=mcp_name
        )

        # Disable in database
        await self.repo.disable_config(project_id, config_id, config_type)

        logger.info(f"Disabled MCP config {mcp_name} for project {project_id}")

    async def create_custom_mcp_config(
        self,
        project_id: str,
        project_path: str,
        config_create: MCPConfigCreate
    ) -> MCPConfigInDB:
        """Create a custom MCP config."""

        # Normalize config
        normalized_config = self._normalize_mcp_config(config_create.config)

        # Validate config
        if not self.file_service.validate_mcp_config_json(normalized_config):
            raise ValueError("Invalid MCP config JSON")

        # Check for duplicate name
        existing = await self.repo.get_custom_config_by_name(project_id, config_create.name)
        if existing:
            raise ValueError(f"MCP config with name '{config_create.name}' already exists")

        # Create config
        config_id = await self.repo.create_custom_config({
            "project_id": project_id,
            "name": config_create.name,
            "description": config_create.description,
            "category": config_create.category,
            "config": normalized_config,
            "status": "active",
            "created_by": "user"
        })

        config = await self.repo.get_custom_config(config_id)
        logger.info(f"Created custom MCP config {config_id} for project {project_id}")

        return self._to_config_dto(config, False)

    async def delete_custom_mcp_config(
        self,
        project_id: str,
        project_path: str,
        config_id: str
    ):
        """Delete a custom MCP config permanently."""

        # Get config
        config = await self.repo.get_custom_config(config_id)
        if not config:
            raise ValueError(f"Custom MCP config {config_id} not found")

        if config.get("project_id") != project_id:
            raise ValueError(f"Custom MCP config {config_id} not found in this project")

        # Remove from .mcp.json
        await self.file_service.remove_mcp_config_from_project(
            project_path=project_path,
            mcp_config_name=config["name"]
        )

        # Delete from database
        await self.repo.delete_custom_config(config_id)

        logger.info(f"Deleted custom MCP config {config['name']} from project {project_id}")

    async def get_default_mcp_configs(self) -> List[MCPConfigInDB]:
        """Get all default MCP configs catalog."""
        configs = await self.repo.get_all_default_configs()
        return [self._to_config_dto(config, False) for config in configs]

    async def save_to_favorites(
        self,
        project_id: str,
        project_path: str,
        config_id: str,
        config_type: str = "custom"
    ) -> MCPConfigInDB:
        """Mark an MCP config as favorite."""

        if config_type == "default":
            config = await self.repo.get_default_config(config_id)
            if not config:
                raise ValueError(f"Default MCP config {config_id} not found")

            if config.get("is_favorite"):
                raise ValueError(f"MCP config '{config['name']}' is already in favorites")

            await self.repo.update_default_config(config_id, {"is_favorite": True})
            config["is_favorite"] = True
        else:
            config = await self.repo.get_custom_config(config_id)
            if not config:
                raise ValueError(f"Custom MCP config {config_id} not found")

            if config.get("category") == "imported":
                raise ValueError("Cannot save imported configs to favorites")

            if config.get("is_favorite"):
                raise ValueError(f"MCP config '{config['name']}' is already in favorites")

            await self.repo.update_custom_config(config_id, {"is_favorite": True})
            config["is_favorite"] = True

        logger.info(f"Marked MCP config '{config['name']}' as favorite")
        return self._to_config_dto(config, False)

    async def remove_from_favorites(
        self,
        project_id: str,
        config_id: str,
        config_type: str = "custom"
    ):
        """Remove an MCP config from favorites."""

        if config_type == "default":
            config = await self.repo.get_default_config(config_id)
            if not config:
                raise ValueError(f"Default MCP config {config_id} not found")

            if not config.get("is_favorite"):
                raise ValueError(f"MCP config '{config['name']}' is not in favorites")

            await self.repo.update_default_config(config_id, {"is_favorite": False})
        else:
            config = await self.repo.get_custom_config(config_id)
            if not config:
                raise ValueError(f"Custom MCP config {config_id} not found")

            if not config.get("is_favorite"):
                raise ValueError(f"MCP config '{config['name']}' is not in favorites")

            await self.repo.update_custom_config(config_id, {"is_favorite": False})

        logger.info(f"Removed MCP config '{config['name']}' from favorites")

    # Helper methods

    def _to_config_dto(self, config: Dict[str, Any], is_enabled: bool) -> MCPConfigInDB:
        """Convert config dict to DTO."""
        return MCPConfigInDB(
            id=config["id"],
            name=config["name"],
            description=config["description"],
            mcp_config_type=config.get("mcp_config_type", "custom"),
            category=config.get("category", "General"),
            config=config.get("config", {}),
            is_enabled=is_enabled,
            is_favorite=config.get("is_favorite", False),
            status=config.get("status"),
            created_by=config.get("created_by", "system"),
            created_at=config.get("created_at"),
            updated_at=config.get("updated_at")
        )

    def _normalize_mcp_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MCP config by removing double-wrapped mcpServers structure."""
        if not config_data:
            return config_data

        if "mcpServers" in config_data:
            mcp_servers = config_data["mcpServers"]
            if isinstance(mcp_servers, dict) and len(mcp_servers) > 0:
                first_server_key = next(iter(mcp_servers))
                logger.info(f"Normalizing MCP config: Removing outer mcpServers wrapper, extracting '{first_server_key}'")
                return mcp_servers[first_server_key]

        return config_data

    def _prepare_mcp_config_for_project(
        self,
        mcp_config_name: str,
        base_config: Dict[str, Any],
        project_path: str,
        project_id: str
    ) -> Dict[str, Any]:
        """Prepare MCP config with project-specific values."""

        config = copy.deepcopy(base_config)

        # Special handling for claudetask MCP
        if mcp_config_name == "claudetask":
            project_root = Path(project_path)
            if project_root.name == "Claude Code Feature Framework":
                venv_python = project_root / "claudetask" / "mcp_server" / "venv" / "bin" / "python"
                server_script = project_root / "claudetask" / "mcp_server" / "native_stdio_server.py"
            else:
                venv_python = Path("python3")
                server_script = Path("claudetask/mcp_server/native_stdio_server.py")

            config["command"] = str(venv_python) if venv_python.exists() else "python3"

            if "args" in config and len(config["args"]) > 0:
                config["args"][0] = str(server_script) if server_script.exists() else config["args"][0]

            if "env" not in config:
                config["env"] = {}

            config["env"]["CLAUDETASK_PROJECT_ID"] = project_id
            config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
            config["env"]["CLAUDETASK_BACKEND_URL"] = os.getenv("CLAUDETASK_BACKEND_URL", "http://localhost:3333")

            logger.info(f"Prepared claudetask MCP config for project {project_id}")

        # Special handling for serena MCP
        elif mcp_config_name == "serena":
            if "args" in config:
                config["args"] = [
                    project_path if arg == "." else arg
                    for arg in config["args"]
                ]
            logger.info(f"Prepared serena MCP config for project {project_id}")

        return config
