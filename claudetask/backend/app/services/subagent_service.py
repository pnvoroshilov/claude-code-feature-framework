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

logger = logging.getLogger(__name__)


class SubagentService:
    """Service for managing subagents"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = SubagentFileService()

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

        for subagent in all_default_subagents:
            is_enabled = (subagent.id, "default") in enabled_subagent_ids
            subagent_dto = self._to_subagent_dto(subagent, "default", is_enabled)

            # Always add to available_default (show all default subagents)
            available_default.append(subagent_dto)

            # Also add to enabled list if enabled
            if is_enabled:
                enabled.append(subagent_dto)

        custom_dtos = []
        for subagent in custom_subagents:
            is_enabled = (subagent.id, "custom") in enabled_subagent_ids
            subagent_dto = self._to_subagent_dto(subagent, "custom", is_enabled)
            custom_dtos.append(subagent_dto)

            if is_enabled:
                enabled.append(subagent_dto)

        return SubagentsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos
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
        Create a custom subagent

        Process:
        1. Validate project exists
        2. Validate subagent name uniqueness
        3. Create custom subagent record
        4. Return created subagent
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

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

        # Create custom subagent
        custom_subagent = CustomSubagent(
            project_id=project_id,
            name=subagent_create.name,
            description=subagent_create.description,
            category=subagent_create.category,
            subagent_type=subagent_create.subagent_type,
            config=subagent_create.config,
            tools_available=subagent_create.tools_available,
            status="active",
            created_by="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(custom_subagent)
        await self.db.commit()
        await self.db.refresh(custom_subagent)

        # Auto-enable the custom subagent
        project_subagent = ProjectSubagent(
            project_id=project_id,
            subagent_id=custom_subagent.id,
            subagent_type="custom",
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_subagent)
        await self.db.commit()

        return self._to_subagent_dto(custom_subagent, "custom", is_enabled=True)

    async def delete_custom_subagent(self, project_id: str, subagent_id: int):
        """
        Delete a custom subagent

        Process:
        1. Verify it's a custom subagent for this project
        2. Remove from project_subagents if enabled
        3. Delete from custom_subagents
        """
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

        # Delete custom subagent
        await self.db.delete(custom_subagent)
        await self.db.commit()

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
        is_enabled: bool
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
