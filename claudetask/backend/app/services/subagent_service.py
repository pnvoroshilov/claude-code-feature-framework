"""Service for managing subagents"""

import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime

from ..models import (
    Project, DefaultSubagent, CustomSubagent, ProjectSubagent
)
from ..schemas import SubagentInDB, SubagentCreate, SubagentsResponse
from .subagent_file_service import SubagentFileService
from .subagent_creation_service import SubagentCreationService

logger = logging.getLogger(__name__)


class SubagentService:
    """Service for managing subagents"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = SubagentFileService()
        self.creation_service = SubagentCreationService()

    async def get_project_subagents(self, project_id: str) -> SubagentsResponse:
        """
        Get all subagents for a project organized by type

        Returns:
        SubagentsResponse with:
        - enabled: Currently enabled subagents
        - available_default: Default subagents that can be enabled
        - custom: User-created custom subagents
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all default subagents
        default_subagents_result = await self.db.execute(
            select(DefaultSubagent).where(DefaultSubagent.is_active == True)
        )
        all_default_subagents = default_subagents_result.scalars().all()

        # Get enabled subagents for this project
        enabled_subagents_result = await self.db.execute(
            select(ProjectSubagent).where(ProjectSubagent.project_id == project_id)
        )
        enabled_project_subagents = enabled_subagents_result.scalars().all()
        enabled_subagent_ids = {
            (ps.subagent_id, ps.subagent_type) for ps in enabled_project_subagents
        }

        # Get custom subagents for this project
        custom_subagents_result = await self.db.execute(
            select(CustomSubagent).where(CustomSubagent.project_id == project_id)
        )
        custom_subagents = custom_subagents_result.scalars().all()

        # Organize subagents
        enabled = []
        available_default = []
        favorites = []

        for subagent in all_default_subagents:
            is_enabled = (subagent.id, "default") in enabled_subagent_ids
            subagent_dto = self._to_subagent_dto(subagent, "default", is_enabled)

            # Always add to available_default (show all default subagents)
            available_default.append(subagent_dto)

            # Add to favorites if marked as favorite
            if subagent.is_favorite:
                favorites.append(subagent_dto)

            # Also add to enabled list if enabled
            if is_enabled:
                enabled.append(subagent_dto)

        custom_dtos = []
        for subagent in custom_subagents:
            is_enabled = (subagent.id, "custom") in enabled_subagent_ids
            subagent_dto = self._to_subagent_dto(subagent, "custom", is_enabled)
            custom_dtos.append(subagent_dto)

            # Add to favorites if marked as favorite
            if subagent.is_favorite:
                favorites.append(subagent_dto)

            if is_enabled:
                enabled.append(subagent_dto)

        return SubagentsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_subagent(self, project_id: str, subagent_id: int, subagent_kind: str = "default") -> SubagentInDB:
        """
        Enable a subagent for a project

        Process:
        1. Validate subagent exists
        2. Insert into project_subagents junction table
        3. Return enabled subagent
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get subagent based on kind
        if subagent_kind == "default":
            subagent_result = await self.db.execute(
                select(DefaultSubagent).where(DefaultSubagent.id == subagent_id)
            )
            subagent = subagent_result.scalar_one_or_none()
        else:
            subagent_result = await self.db.execute(
                select(CustomSubagent).where(
                    and_(
                        CustomSubagent.id == subagent_id,
                        CustomSubagent.project_id == project_id
                    )
                )
            )
            subagent = subagent_result.scalar_one_or_none()

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Check if already enabled
        existing = await self.db.execute(
            select(ProjectSubagent).where(
                and_(
                    ProjectSubagent.project_id == project_id,
                    ProjectSubagent.subagent_id == subagent_id,
                    ProjectSubagent.subagent_type == subagent_kind
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Subagent already enabled for project")

        # Copy subagent file to project
        subagent_config = None
        if subagent_kind == "custom":
            subagent_config = subagent.config

        success = await self.file_service.copy_subagent_to_project(
            project_path=project.path,
            subagent_type=subagent.subagent_type,
            subagent_config=subagent_config
        )

        if not success:
            raise RuntimeError(f"Failed to copy subagent file to project")

        # Insert into project_subagents
        project_subagent = ProjectSubagent(
            project_id=project_id,
            subagent_id=subagent_id,
            subagent_type=subagent_kind,
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_subagent)
        await self.db.commit()

        # Return enabled subagent
        return self._to_subagent_dto(subagent, subagent_kind, is_enabled=True)

    async def disable_subagent(self, project_id: str, subagent_id: int):
        """
        Disable a subagent for a project

        Process:
        1. Get subagent details to find file name
        2. Delete subagent file from .claude/agents/
        3. Remove record from project_subagents junction table
        4. Keep record in custom_subagents if it's a custom subagent
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Find enabled subagent
        result = await self.db.execute(
            select(ProjectSubagent).where(
                and_(
                    ProjectSubagent.project_id == project_id,
                    ProjectSubagent.subagent_id == subagent_id
                )
            )
        )
        project_subagent = result.scalar_one_or_none()

        if not project_subagent:
            raise ValueError(f"Subagent not enabled for project")

        # Get subagent details for file deletion
        if project_subagent.subagent_type == "default":
            subagent_result = await self.db.execute(
                select(DefaultSubagent).where(DefaultSubagent.id == subagent_id)
            )
            subagent = subagent_result.scalar_one_or_none()
        else:
            subagent_result = await self.db.execute(
                select(CustomSubagent).where(CustomSubagent.id == subagent_id)
            )
            subagent = subagent_result.scalar_one_or_none()

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Delete subagent file from project
        success = await self.file_service.delete_subagent_from_project(
            project_path=project.path,
            subagent_type=subagent.subagent_type
        )

        if not success:
            logger.warning(f"Failed to delete subagent file from project (may not exist)")

        # Delete from project_subagents
        await self.db.delete(project_subagent)
        await self.db.commit()

    async def create_custom_subagent(self, project_id: str, subagent_create: SubagentCreate) -> SubagentInDB:
        """
        Create a custom subagent record (step 1 of 2)

        This creates the database record with status "creating".
        The actual CLI interaction happens in background task.
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Validate subagent name
        if not self.creation_service.validate_agent_name(subagent_create.name):
            raise ValueError(f"Invalid subagent name: {subagent_create.name}")

        # Check if subagent name already exists for this project
        existing = await self.db.execute(
            select(CustomSubagent).where(
                and_(
                    CustomSubagent.project_id == project_id,
                    CustomSubagent.name == subagent_create.name
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Custom subagent with name '{subagent_create.name}' already exists")

        # Convert name to kebab-case for subagent_type
        subagent_type = subagent_create.name.lower().replace(' ', '-')

        # Create custom subagent record with "creating" status
        custom_subagent = CustomSubagent(
            project_id=project_id,
            name=subagent_create.name,
            description=subagent_create.description,
            category=subagent_create.category or "Custom",
            subagent_type=subagent_type,
            config=subagent_create.config,
            tools_available=subagent_create.tools_available or ["Read", "Write", "Edit", "Bash", "Grep"],
            status="creating",  # Will be updated by background task
            created_by="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(custom_subagent)
        await self.db.commit()
        await self.db.refresh(custom_subagent)

        logger.info(f"Created custom subagent record {custom_subagent.id} for project {project_id}")

        return self._to_subagent_dto(custom_subagent, "custom", False, project.path)

    async def execute_subagent_creation_cli(
        self,
        project_id: str,
        subagent_id: int,
        agent_name: str,
        agent_description: str
    ):
        """
        Execute Claude Code CLI to create subagent (background task)

        This is step 2 of 2 for custom subagent creation.
        """
        try:
            # Get project
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Sanitize inputs
            safe_name = self.creation_service.sanitize_agent_input(agent_name)
            safe_description = self.creation_service.sanitize_agent_input(agent_description)

            # Execute CLI command
            result = await self.creation_service.create_subagent_via_claude_cli(
                project_path=project.path,
                agent_name=safe_name,
                agent_description=safe_description
            )

            if result["success"]:
                # Update subagent status to active
                subagent_result = await self.db.execute(
                    select(CustomSubagent).where(CustomSubagent.id == subagent_id)
                )
                custom_subagent = subagent_result.scalar_one_or_none()

                if custom_subagent:
                    custom_subagent.status = "active"
                    custom_subagent.config = result.get("content", "")
                    custom_subagent.updated_at = datetime.utcnow()

                    # Enable subagent immediately
                    project_subagent = ProjectSubagent(
                        project_id=project_id,
                        subagent_id=subagent_id,
                        subagent_type="custom",
                        enabled_at=datetime.utcnow(),
                        enabled_by="user"
                    )
                    self.db.add(project_subagent)

                    await self.db.commit()

                    logger.info(f"Successfully created custom subagent {agent_name} for project {project_id}")
            else:
                # Update subagent status to failed
                subagent_result = await self.db.execute(
                    select(CustomSubagent).where(CustomSubagent.id == subagent_id)
                )
                custom_subagent = subagent_result.scalar_one_or_none()

                if custom_subagent:
                    custom_subagent.status = "failed"
                    custom_subagent.error_message = result.get("error", "Unknown error")
                    custom_subagent.updated_at = datetime.utcnow()
                    await self.db.commit()

                    logger.error(f"Failed to create custom subagent {agent_name}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Exception in subagent creation CLI execution: {e}", exc_info=True)

            # Update subagent status to failed
            try:
                subagent_result = await self.db.execute(
                    select(CustomSubagent).where(CustomSubagent.id == subagent_id)
                )
                custom_subagent = subagent_result.scalar_one_or_none()

                if custom_subagent:
                    custom_subagent.status = "failed"
                    custom_subagent.error_message = str(e)
                    custom_subagent.updated_at = datetime.utcnow()
                    await self.db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update subagent status: {update_error}")

    async def delete_custom_subagent(self, project_id: str, subagent_id: int):
        """
        Delete a custom subagent permanently

        Process:
        1. Verify it's a custom subagent for this project
        2. Get project details for file deletion
        3. Delete agent file from .claude/agents/
        4. Remove from project_subagents if enabled
        5. Delete from custom_subagents table
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get custom subagent
        result = await self.db.execute(
            select(CustomSubagent).where(
                and_(
                    CustomSubagent.id == subagent_id,
                    CustomSubagent.project_id == project_id
                )
            )
        )
        custom_subagent = result.scalar_one_or_none()

        if not custom_subagent:
            raise ValueError(f"Custom subagent {subagent_id} not found for project {project_id}")

        # Delete agent file from project's .claude/agents/ directory
        success = await self.file_service.delete_subagent_from_project(
            project_path=project.path,
            subagent_type=custom_subagent.subagent_type
        )

        if not success:
            logger.warning(f"Failed to delete subagent file from project (may not exist)")

        # Remove from project_subagents if enabled
        enabled_result = await self.db.execute(
            select(ProjectSubagent).where(
                and_(
                    ProjectSubagent.project_id == project_id,
                    ProjectSubagent.subagent_id == subagent_id,
                    ProjectSubagent.subagent_type == "custom"
                )
            )
        )
        project_subagent = enabled_result.scalar_one_or_none()
        if project_subagent:
            await self.db.delete(project_subagent)

        # Delete custom subagent record
        await self.db.delete(custom_subagent)
        await self.db.commit()

        logger.info(f"Deleted custom subagent {custom_subagent.name} from project {project_id}")

    async def sync_enabled_subagents_after_framework_update(
        self,
        project_id: str,
        project_path: str
    ):
        """
        Sync enabled subagents after framework update

        Process:
        1. Check which agent files actually exist in .claude/agents/
        2. Get all default subagents from DB
        3. For each default subagent:
           - If file exists in project → ensure ProjectSubagent record exists
           - If file doesn't exist → remove ProjectSubagent record if exists
        4. Custom subagents are not affected (they manage their own files)
        """
        import os

        # Get agents directory
        agents_dir = os.path.join(project_path, ".claude", "agents")
        if not os.path.exists(agents_dir):
            logger.warning(f"Agents directory not found: {agents_dir}")
            return

        # Get all agent files in project
        existing_agent_files = set()
        for file_name in os.listdir(agents_dir):
            if file_name.endswith(".md"):
                # Convert file name to subagent_type (remove .md)
                subagent_type = file_name[:-3]
                existing_agent_files.add(subagent_type)

        logger.info(f"Found {len(existing_agent_files)} agent files in project: {existing_agent_files}")

        # Get all default subagents from DB
        default_subagents_result = await self.db.execute(
            select(DefaultSubagent).where(DefaultSubagent.is_active == True)
        )
        all_default_subagents = default_subagents_result.scalars().all()

        # Get currently enabled subagents for this project
        enabled_result = await self.db.execute(
            select(ProjectSubagent).where(
                and_(
                    ProjectSubagent.project_id == project_id,
                    ProjectSubagent.subagent_type == "default"
                )
            )
        )
        enabled_project_subagents = {
            ps.subagent_id: ps for ps in enabled_result.scalars().all()
        }

        # Sync: enable agents whose files exist, disable agents whose files don't exist
        for subagent in all_default_subagents:
            file_exists = subagent.subagent_type in existing_agent_files
            is_enabled = subagent.id in enabled_project_subagents

            if file_exists and not is_enabled:
                # File exists but not enabled → create ProjectSubagent record
                project_subagent = ProjectSubagent(
                    project_id=project_id,
                    subagent_id=subagent.id,
                    subagent_type="default",
                    enabled_at=datetime.utcnow(),
                    enabled_by="framework_update"
                )
                self.db.add(project_subagent)
                logger.info(f"Enabled subagent {subagent.subagent_type} (file exists)")

            elif not file_exists and is_enabled:
                # File doesn't exist but enabled → remove ProjectSubagent record
                project_subagent = enabled_project_subagents[subagent.id]
                await self.db.delete(project_subagent)
                logger.info(f"Disabled subagent {subagent.subagent_type} (file not found)")

        await self.db.commit()
        logger.info(f"Synced enabled subagents for project {project_id}")

    async def save_to_favorites(self, subagent_id: int, subagent_kind: str = "custom") -> SubagentInDB:
        """
        Mark a subagent as favorite

        Process:
        1. Get subagent (default or custom)
        2. Verify it's not already a favorite
        3. Set is_favorite = True

        Args:
            subagent_id: ID of the subagent to favorite
            subagent_kind: Type of subagent ("default" or "custom")

        Returns:
            SubagentInDB: The favorited subagent
        """
        if subagent_kind == "default":
            # Get default subagent
            result = await self.db.execute(
                select(DefaultSubagent).where(DefaultSubagent.id == subagent_id)
            )
            subagent = result.scalar_one_or_none()

            if not subagent:
                raise ValueError(f"Default subagent {subagent_id} not found")

            # Check if already a favorite
            if subagent.is_favorite:
                raise ValueError(f"Subagent '{subagent.name}' is already in favorites")

            # Mark as favorite
            subagent.is_favorite = True
            subagent.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(subagent)

            logger.info(f"Marked default subagent '{subagent.name}' as favorite (ID: {subagent.id})")

            return self._to_subagent_dto(subagent, "default", False)
        else:
            # Get custom subagent
            result = await self.db.execute(
                select(CustomSubagent).where(CustomSubagent.id == subagent_id)
            )
            subagent = result.scalar_one_or_none()

            if not subagent:
                raise ValueError(f"Custom subagent {subagent_id} not found")

            # Check if already a favorite
            if subagent.is_favorite:
                raise ValueError(f"Subagent '{subagent.name}' is already in favorites")

            # Mark as favorite
            subagent.is_favorite = True
            subagent.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(subagent)

            logger.info(f"Marked custom subagent '{subagent.name}' as favorite (ID: {subagent.id})")

            return self._to_subagent_dto(subagent, "custom", False)

    async def remove_from_favorites(self, subagent_id: int, subagent_kind: str = "custom") -> None:
        """
        Unmark a subagent as favorite

        Process:
        1. Get subagent (default or custom)
        2. Verify it's marked as favorite
        3. Set is_favorite = False

        Args:
            subagent_id: ID of the subagent to unfavorite
            subagent_kind: Type of subagent ("default" or "custom")
        """
        if subagent_kind == "default":
            # Get default subagent
            result = await self.db.execute(
                select(DefaultSubagent).where(DefaultSubagent.id == subagent_id)
            )
            subagent = result.scalar_one_or_none()

            if not subagent:
                raise ValueError(f"Default subagent {subagent_id} not found")

            # Check if it's marked as favorite
            if not subagent.is_favorite:
                raise ValueError(f"Subagent '{subagent.name}' is not in favorites")

            # Unmark as favorite
            subagent.is_favorite = False
            subagent.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed default subagent '{subagent.name}' from favorites (ID: {subagent_id})")
        else:
            # Get custom subagent
            result = await self.db.execute(
                select(CustomSubagent).where(CustomSubagent.id == subagent_id)
            )
            subagent = result.scalar_one_or_none()

            if not subagent:
                raise ValueError(f"Custom subagent {subagent_id} not found")

            # Check if it's marked as favorite
            if not subagent.is_favorite:
                raise ValueError(f"Subagent '{subagent.name}' is not in favorites")

            # Unmark as favorite
            subagent.is_favorite = False
            subagent.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed custom subagent '{subagent.name}' from favorites (ID: {subagent_id})")

    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    def _to_subagent_dto(
        self,
        subagent: Any,
        subagent_kind: str,
        is_enabled: bool,
        project_path: str = ""
    ) -> SubagentInDB:
        """Convert DB model to DTO"""
        return SubagentInDB(
            id=subagent.id,
            name=subagent.name,
            description=subagent.description,
            category=subagent.category,
            subagent_type=subagent.subagent_type,
            subagent_kind=subagent_kind,
            tools_available=subagent.tools_available if hasattr(subagent, 'tools_available') else [],
            recommended_for=subagent.recommended_for if hasattr(subagent, 'recommended_for') else [],
            is_enabled=is_enabled,
            status=subagent.status if hasattr(subagent, 'status') else None,
            created_by=subagent.created_by if hasattr(subagent, 'created_by') else None,
            created_at=subagent.created_at,
            updated_at=subagent.updated_at
        )
