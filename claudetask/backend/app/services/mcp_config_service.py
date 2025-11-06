"""Service for managing MCP configurations"""

import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from ..models import (
    Project, DefaultMCPConfig, CustomMCPConfig, ProjectMCPConfig
)
from ..schemas import MCPConfigInDB, MCPConfigCreate, MCPConfigsResponse
from .mcp_config_file_service import MCPConfigFileService

logger = logging.getLogger(__name__)


class MCPConfigService:
    """Service for managing MCP configurations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = MCPConfigFileService()

    async def get_project_mcp_configs(self, project_id: str) -> MCPConfigsResponse:
        """
        Get all MCP configs for a project organized by type

        Returns:
        MCPConfigsResponse with:
        - enabled: Currently enabled MCP configs
        - available_default: Default MCP configs that can be enabled
        - custom: User-created custom MCP configs
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all default MCP configs
        default_configs_result = await self.db.execute(
            select(DefaultMCPConfig).where(DefaultMCPConfig.is_active == True)
        )
        all_default_configs = default_configs_result.scalars().all()

        # Get enabled MCP configs for this project
        enabled_configs_result = await self.db.execute(
            select(ProjectMCPConfig).where(ProjectMCPConfig.project_id == project_id)
        )
        enabled_project_configs = enabled_configs_result.scalars().all()
        enabled_config_ids = {
            (pc.mcp_config_id, pc.mcp_config_type) for pc in enabled_project_configs
        }

        # Get custom MCP configs for this project
        custom_configs_result = await self.db.execute(
            select(CustomMCPConfig).where(CustomMCPConfig.project_id == project_id)
        )
        custom_configs = custom_configs_result.scalars().all()

        # Organize MCP configs
        enabled = []
        available_default = []

        for config in all_default_configs:
            is_enabled = (config.id, "default") in enabled_config_ids
            config_dto = self._to_config_dto(config, "default", is_enabled)

            # Always add to available_default (show all default configs)
            available_default.append(config_dto)

            # Also add to enabled list if enabled
            if is_enabled:
                enabled.append(config_dto)

        custom_dtos = []
        for config in custom_configs:
            is_enabled = (config.id, "custom") in enabled_config_ids
            config_dto = self._to_config_dto(config, "custom", is_enabled)
            custom_dtos.append(config_dto)

            if is_enabled:
                enabled.append(config_dto)

        return MCPConfigsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos
        )

    async def enable_mcp_config(self, project_id: str, mcp_config_id: int) -> MCPConfigInDB:
        """
        Enable a default MCP config by merging it to project's .mcp.json

        Process:
        1. Validate MCP config exists
        2. Merge MCP config to .mcp.json
        3. Insert into project_mcp_configs junction table
        4. Return enabled MCP config
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get MCP config (assume default for now, can extend to custom)
        config_result = await self.db.execute(
            select(DefaultMCPConfig).where(DefaultMCPConfig.id == mcp_config_id)
        )
        mcp_config = config_result.scalar_one_or_none()

        if not mcp_config:
            raise ValueError(f"MCP config {mcp_config_id} not found")

        # Check if already enabled (use .first() to handle duplicates gracefully)
        existing = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == mcp_config_id,
                    ProjectMCPConfig.mcp_config_type == "default"
                )
            )
        )
        if existing.scalars().first():
            raise ValueError(f"MCP config already enabled for project")

        # Check if MCP config already exists in project's .mcp.json
        # If it exists, don't overwrite (user may have customized it)
        config_exists = await self.file_service.mcp_config_exists_in_project(
            project_path=project.path,
            mcp_config_name=mcp_config.name
        )

        if not config_exists:
            # Prepare config data - customize for specific MCP servers
            config_data = self._prepare_mcp_config_for_project(
                mcp_config_name=mcp_config.name,
                base_config=mcp_config.config,
                project=project
            )

            # Only merge if config doesn't exist in project
            success = await self.file_service.merge_mcp_config_to_project(
                project_path=project.path,
                mcp_config_name=mcp_config.name,
                config_data=config_data
            )

            if not success:
                raise RuntimeError(f"Failed to merge MCP config to project")
        else:
            logger.info(f"MCP config '{mcp_config.name}' already exists in project, skipping merge to preserve custom settings")

        # Insert into project_mcp_configs
        project_mcp_config = ProjectMCPConfig(
            project_id=project_id,
            mcp_config_id=mcp_config_id,
            mcp_config_type="default",
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_mcp_config)
        await self.db.commit()

        logger.info(f"Enabled MCP config {mcp_config.name} for project {project_id}")

        return self._to_config_dto(mcp_config, "default", True)

    async def disable_mcp_config(self, project_id: str, mcp_config_id: int):
        """
        Disable an MCP config by removing it from project

        Process:
        1. Delete from project_mcp_configs junction table
        2. Remove MCP config from .mcp.json
        3. Keep record in custom_mcp_configs if custom (don't delete)
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all project_mcp_config records (may have duplicates)
        result = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == mcp_config_id
                )
            )
        )
        project_mcp_configs = result.scalars().all()

        if not project_mcp_configs:
            raise ValueError(f"MCP config not enabled for project")

        # Use first record to get mcp_config_type
        project_mcp_config = project_mcp_configs[0]

        # Get MCP config details for name
        if project_mcp_config.mcp_config_type == "default":
            config_result = await self.db.execute(
                select(DefaultMCPConfig).where(DefaultMCPConfig.id == mcp_config_id)
            )
            mcp_config = config_result.scalar_one_or_none()
        else:
            config_result = await self.db.execute(
                select(CustomMCPConfig).where(CustomMCPConfig.id == mcp_config_id)
            )
            mcp_config = config_result.scalar_one_or_none()

        if not mcp_config:
            raise ValueError(f"MCP config {mcp_config_id} not found")

        # Remove MCP config from project's .mcp.json
        success = await self.file_service.remove_mcp_config_from_project(
            project_path=project.path,
            mcp_config_name=mcp_config.name
        )

        if not success:
            logger.warning(f"Failed to remove MCP config from .mcp.json (may not exist)")

        # Delete all records from project_mcp_configs (handle duplicates)
        for config_record in project_mcp_configs:
            await self.db.delete(config_record)
        await self.db.commit()

        logger.info(f"Disabled MCP config {mcp_config.name} for project {project_id} (removed {len(project_mcp_configs)} record(s))")

    async def create_custom_mcp_config(
        self,
        project_id: str,
        config_create: MCPConfigCreate
    ) -> MCPConfigInDB:
        """
        Create a custom MCP config

        Process:
        1. Validate config JSON
        2. Create database record
        3. Optionally enable it immediately
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Validate config JSON
        if not self.file_service.validate_mcp_config_json(config_create.config):
            raise ValueError(f"Invalid MCP config JSON")

        # Check for duplicate name
        existing = await self.db.execute(
            select(CustomMCPConfig).where(
                and_(
                    CustomMCPConfig.project_id == project_id,
                    CustomMCPConfig.name == config_create.name
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"MCP config with name '{config_create.name}' already exists")

        # Create custom MCP config record
        custom_mcp_config = CustomMCPConfig(
            project_id=project_id,
            name=config_create.name,
            description=config_create.description,
            category=config_create.category,
            config=config_create.config,
            status="active",
            created_by="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(custom_mcp_config)
        await self.db.commit()
        await self.db.refresh(custom_mcp_config)

        logger.info(f"Created custom MCP config {custom_mcp_config.id} for project {project_id}")

        return self._to_config_dto(custom_mcp_config, "custom", False)

    async def delete_custom_mcp_config(self, project_id: str, mcp_config_id: int):
        """
        Delete a custom MCP config permanently

        Process:
        1. Verify MCP config is custom (not default)
        2. Remove from project_mcp_configs junction table
        3. Remove MCP config from .mcp.json
        4. Delete record from custom_mcp_configs table
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get custom MCP config
        result = await self.db.execute(
            select(CustomMCPConfig).where(
                and_(
                    CustomMCPConfig.id == mcp_config_id,
                    CustomMCPConfig.project_id == project_id
                )
            )
        )
        custom_mcp_config = result.scalar_one_or_none()

        if not custom_mcp_config:
            raise ValueError(f"Custom MCP config {mcp_config_id} not found")

        # Delete from project_mcp_configs if enabled
        project_config_result = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == mcp_config_id,
                    ProjectMCPConfig.mcp_config_type == "custom"
                )
            )
        )
        project_mcp_config = project_config_result.scalar_one_or_none()

        if project_mcp_config:
            await self.db.delete(project_mcp_config)

        # Remove MCP config from .mcp.json
        await self.file_service.remove_mcp_config_from_project(
            project_path=project.path,
            mcp_config_name=custom_mcp_config.name
        )

        # Delete custom_mcp_configs record
        await self.db.delete(custom_mcp_config)
        await self.db.commit()

        logger.info(f"Deleted custom MCP config {custom_mcp_config.name} from project {project_id}")

    async def get_default_mcp_configs(self) -> List[MCPConfigInDB]:
        """Get all default MCP configs catalog"""
        result = await self.db.execute(
            select(DefaultMCPConfig).where(DefaultMCPConfig.is_active == True)
        )
        configs = result.scalars().all()

        return [
            self._to_config_dto(config, "default", False)
            for config in configs
        ]

    # Helper methods

    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    def _to_config_dto(
        self,
        mcp_config: Any,
        config_type: str,
        is_enabled: bool
    ) -> MCPConfigInDB:
        """Convert database model to DTO"""
        return MCPConfigInDB(
            id=mcp_config.id,
            name=mcp_config.name,
            description=mcp_config.description,
            mcp_config_type=config_type,
            category=mcp_config.category,
            config=mcp_config.config,
            is_enabled=is_enabled,
            status=getattr(mcp_config, "status", None),
            created_by=getattr(mcp_config, "created_by", "system"),
            created_at=mcp_config.created_at,
            updated_at=mcp_config.updated_at
        )

    def _prepare_mcp_config_for_project(
        self,
        mcp_config_name: str,
        base_config: Dict[str, Any],
        project: Project
    ) -> Dict[str, Any]:
        """
        Prepare MCP config with project-specific values

        For claudetask MCP: Replace template values with actual project data
        For other MCPs: Use base config as-is
        """
        import copy
        from pathlib import Path

        config = copy.deepcopy(base_config)

        # Special handling for claudetask MCP
        if mcp_config_name == "claudetask":
            # Get absolute path to claudetask venv python
            project_root = Path(project.path)
            if project_root.name == "Claude Code Feature Framework":
                # This is the framework project itself
                venv_python = project_root / "claudetask" / "mcp_server" / "venv" / "bin" / "python"
                server_script = project_root / "claudetask" / "mcp_server" / "native_stdio_server.py"
            else:
                # External project - look for framework in parent or use relative paths
                venv_python = Path("python3")  # Fallback to system python
                server_script = Path("claudetask/mcp_server/native_stdio_server.py")

            # Update command with absolute path
            config["command"] = str(venv_python) if venv_python.exists() else "python3"

            # Update args with absolute path
            if "args" in config and len(config["args"]) > 0:
                config["args"][0] = str(server_script) if server_script.exists() else config["args"][0]

            # Update env variables with project-specific values
            if "env" not in config:
                config["env"] = {}

            config["env"]["CLAUDETASK_PROJECT_ID"] = project.id
            config["env"]["CLAUDETASK_PROJECT_PATH"] = project.path
            config["env"]["CLAUDETASK_BACKEND_URL"] = os.getenv("CLAUDETASK_BACKEND_URL", "http://localhost:3333")

            logger.info(f"Prepared claudetask MCP config for project {project.id}: command={config['command']}, project_path={project.path}")

        return config
