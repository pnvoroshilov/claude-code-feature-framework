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

        # Create a map of custom config names to their enabled status
        custom_config_names_enabled = {}
        for config in custom_configs:
            is_enabled = (config.id, "custom") in enabled_config_ids
            custom_config_names_enabled[config.name] = is_enabled

        for config in all_default_configs:
            # Check if default config is enabled OR if imported config with same name is enabled
            is_default_enabled = (config.id, "default") in enabled_config_ids
            is_imported_enabled = custom_config_names_enabled.get(config.name, False)
            is_enabled = is_default_enabled or is_imported_enabled

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

    async def enable_mcp_config(self, project_id: str, mcp_config_id: int, mcp_config_type: str = "default") -> MCPConfigInDB:
        """
        Enable an MCP config by writing it from DB to project's .mcp.json

        Process:
        1. Check if imported config exists in DB for this MCP (use imported config if available)
        2. Otherwise use default/custom MCP config from DB
        3. Write MCP config from DB to .mcp.json
        4. Insert into project_mcp_configs junction table
        5. Return enabled MCP config

        DB is the source of truth - .mcp.json is just the output file
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # First, check if there's an imported config for this MCP name in custom_mcp_configs
        # Imported configs have the actual project-specific settings
        if mcp_config_type == "default":
            # Get default MCP config name
            default_config_result = await self.db.execute(
                select(DefaultMCPConfig).where(DefaultMCPConfig.id == mcp_config_id)
            )
            default_mcp_config = default_config_result.scalar_one_or_none()

            if not default_mcp_config:
                raise ValueError(f"Default MCP config {mcp_config_id} not found")

            # Check if imported config exists for this MCP name
            imported_config_result = await self.db.execute(
                select(CustomMCPConfig).where(
                    and_(
                        CustomMCPConfig.project_id == project_id,
                        CustomMCPConfig.name == default_mcp_config.name,
                        CustomMCPConfig.category == "imported"
                    )
                )
            )
            imported_config = imported_config_result.scalar_one_or_none()

            if imported_config:
                # Use imported config instead (has correct project-specific settings)
                mcp_config = imported_config
                actual_config_id = imported_config.id
                actual_config_type = "custom"
                logger.info(f"Found imported config for {default_mcp_config.name}, using imported version")
            else:
                # Use default config
                mcp_config = default_mcp_config
                actual_config_id = mcp_config_id
                actual_config_type = "default"
        else:
            # Get custom MCP config
            config_result = await self.db.execute(
                select(CustomMCPConfig).where(CustomMCPConfig.id == mcp_config_id)
            )
            mcp_config = config_result.scalar_one_or_none()

            if not mcp_config:
                raise ValueError(f"Custom MCP config {mcp_config_id} not found")

            actual_config_id = mcp_config_id
            actual_config_type = "custom"

        # Check if already enabled
        existing = await self.db.execute(
            select(ProjectMCPConfig).where(
                and_(
                    ProjectMCPConfig.project_id == project_id,
                    ProjectMCPConfig.mcp_config_id == actual_config_id,
                    ProjectMCPConfig.mcp_config_type == actual_config_type
                )
            )
        )
        if existing.scalars().first():
            raise ValueError(f"MCP config already enabled for project")

        # Write config from DB to .mcp.json (DB is source of truth)
        config_data = mcp_config.config

        success = await self.file_service.merge_mcp_config_to_project(
            project_path=project.path,
            mcp_config_name=mcp_config.name,
            config_data=config_data
        )

        if not success:
            raise RuntimeError(f"Failed to merge MCP config to project")

        # Insert into project_mcp_configs
        project_mcp_config = ProjectMCPConfig(
            project_id=project_id,
            mcp_config_id=actual_config_id,
            mcp_config_type=actual_config_type,
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_mcp_config)
        await self.db.commit()

        logger.info(f"Enabled MCP config {mcp_config.name} for project {project_id} (config from DB)")

        return self._to_config_dto(mcp_config, actual_config_type, True)

    async def disable_mcp_config(self, project_id: str, mcp_config_id: int):
        """
        Disable an MCP config by removing it from project

        Process:
        1. Get MCP config name (check both default and imported)
        2. Delete ALL junction table records for this MCP name (default + imported)
        3. Remove MCP config from .mcp.json
        4. Keep records in DB (custom_mcp_configs) - don't delete from DB

        DB is the source of truth - when re-enabling, config will be written from DB
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # First, try to get the MCP config to determine its name
        # Try default first
        default_config_result = await self.db.execute(
            select(DefaultMCPConfig).where(DefaultMCPConfig.id == mcp_config_id)
        )
        default_mcp_config = default_config_result.scalar_one_or_none()

        if default_mcp_config:
            # This is a default MCP config
            mcp_name = default_mcp_config.name

            # Look for junction records for this default config
            result = await self.db.execute(
                select(ProjectMCPConfig).where(
                    and_(
                        ProjectMCPConfig.project_id == project_id,
                        ProjectMCPConfig.mcp_config_id == mcp_config_id,
                        ProjectMCPConfig.mcp_config_type == "default"
                    )
                )
            )
            default_junction_records = result.scalars().all()

            # Also look for imported config with same name
            imported_result = await self.db.execute(
                select(CustomMCPConfig).where(
                    and_(
                        CustomMCPConfig.project_id == project_id,
                        CustomMCPConfig.name == mcp_name,
                        CustomMCPConfig.category == "imported"
                    )
                )
            )
            imported_config = imported_result.scalar_one_or_none()

            imported_junction_records = []
            if imported_config:
                # Look for junction records for imported config
                imported_junction_result = await self.db.execute(
                    select(ProjectMCPConfig).where(
                        and_(
                            ProjectMCPConfig.project_id == project_id,
                            ProjectMCPConfig.mcp_config_id == imported_config.id,
                            ProjectMCPConfig.mcp_config_type == "custom"
                        )
                    )
                )
                imported_junction_records = imported_junction_result.scalars().all()

            # Collect all junction records to delete
            all_junction_records = default_junction_records + imported_junction_records

            if not all_junction_records:
                raise ValueError(f"MCP config not enabled for project")

        else:
            # Try custom config
            custom_config_result = await self.db.execute(
                select(CustomMCPConfig).where(CustomMCPConfig.id == mcp_config_id)
            )
            custom_mcp_config = custom_config_result.scalar_one_or_none()

            if not custom_mcp_config:
                raise ValueError(f"MCP config {mcp_config_id} not found")

            mcp_name = custom_mcp_config.name

            # Get junction records for this custom config
            result = await self.db.execute(
                select(ProjectMCPConfig).where(
                    and_(
                        ProjectMCPConfig.project_id == project_id,
                        ProjectMCPConfig.mcp_config_id == mcp_config_id
                    )
                )
            )
            all_junction_records = result.scalars().all()

            if not all_junction_records:
                raise ValueError(f"MCP config not enabled for project")

        # Remove MCP config from .mcp.json
        # Config stays in DB, so when re-enabled it will be written from DB with correct settings
        await self.file_service.remove_mcp_config_from_project(
            project_path=project.path,
            mcp_config_name=mcp_name
        )

        # Delete all junction records (both default and imported)
        for config_record in all_junction_records:
            await self.db.delete(config_record)
        await self.db.commit()

        logger.info(f"Disabled MCP config {mcp_name} for project {project_id} (removed {len(all_junction_records)} junction record(s) from DB and removed from .mcp.json)")

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
