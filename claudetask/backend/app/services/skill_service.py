"""Service for managing skills"""

import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime

from ..models import (
    Project, DefaultSkill, CustomSkill, ProjectSkill, AgentSkillRecommendation
)
from ..schemas import SkillInDB, SkillCreate, SkillsResponse
from .skill_file_service import SkillFileService
from .skill_creation_service import SkillCreationService

logger = logging.getLogger(__name__)


class SkillService:
    """Service for managing skills"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = SkillFileService()
        self.creation_service = SkillCreationService()

    async def get_project_skills(self, project_id: str) -> SkillsResponse:
        """
        Get all skills for a project organized by type

        Returns:
        SkillsResponse with:
        - enabled: Currently enabled skills
        - available_default: Default skills that can be enabled
        - custom: User-created custom skills
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all default skills
        default_skills_result = await self.db.execute(
            select(DefaultSkill).where(DefaultSkill.is_active == True)
        )
        all_default_skills = default_skills_result.scalars().all()

        # Get enabled skills for this project
        enabled_skills_result = await self.db.execute(
            select(ProjectSkill).where(ProjectSkill.project_id == project_id)
        )
        enabled_project_skills = enabled_skills_result.scalars().all()
        enabled_skill_ids = {
            (ps.skill_id, ps.skill_type) for ps in enabled_project_skills
        }

        # Get custom skills for this project
        custom_skills_result = await self.db.execute(
            select(CustomSkill).where(CustomSkill.project_id == project_id)
        )
        custom_skills = custom_skills_result.scalars().all()

        # Organize skills
        enabled = []
        available_default = []

        for skill in all_default_skills:
            is_enabled = (skill.id, "default") in enabled_skill_ids
            skill_dto = self._to_skill_dto(skill, "default", is_enabled, project.path)

            # Always add to available_default (show all default skills)
            available_default.append(skill_dto)

            # Also add to enabled list if enabled
            if is_enabled:
                enabled.append(skill_dto)

        custom_dtos = []
        for skill in custom_skills:
            is_enabled = (skill.id, "custom") in enabled_skill_ids
            skill_dto = self._to_skill_dto(skill, "custom", is_enabled, project.path)
            custom_dtos.append(skill_dto)

            if is_enabled:
                enabled.append(skill_dto)

        return SkillsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos
        )

    async def enable_skill(self, project_id: str, skill_id: int) -> SkillInDB:
        """
        Enable a default skill by copying it to project

        Process:
        1. Validate skill exists
        2. Copy skill file to .claude/skills/
        3. Insert into project_skills junction table
        4. Return enabled skill
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get skill (assume default for now, can extend to custom)
        skill_result = await self.db.execute(
            select(DefaultSkill).where(DefaultSkill.id == skill_id)
        )
        skill = skill_result.scalar_one_or_none()

        if not skill:
            raise ValueError(f"Skill {skill_id} not found")

        # Check if already enabled
        existing = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id,
                    ProjectSkill.skill_type == "default"
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Skill already enabled for project")

        # Copy skill file to project
        success = await self.file_service.copy_skill_to_project(
            project_path=project.path,
            skill_file_name=skill.file_name,
            source_type="default"
        )

        if not success:
            raise RuntimeError(f"Failed to copy skill file to project")

        # Insert into project_skills
        project_skill = ProjectSkill(
            project_id=project_id,
            skill_id=skill_id,
            skill_type="default",
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_skill)
        await self.db.commit()

        logger.info(f"Enabled skill {skill.name} for project {project_id}")

        return self._to_skill_dto(skill, "default", True, project.path)

    async def disable_skill(self, project_id: str, skill_id: int):
        """
        Disable a skill by removing it from project

        Process:
        1. Delete from project_skills junction table
        2. Delete skill file from .claude/skills/
        3. Keep record in custom_skills if custom (don't delete)
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get project_skill record
        result = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id
                )
            )
        )
        project_skill = result.scalar_one_or_none()

        if not project_skill:
            raise ValueError(f"Skill not enabled for project")

        # Get skill details for file name
        if project_skill.skill_type == "default":
            skill_result = await self.db.execute(
                select(DefaultSkill).where(DefaultSkill.id == skill_id)
            )
            skill = skill_result.scalar_one_or_none()
        else:
            skill_result = await self.db.execute(
                select(CustomSkill).where(CustomSkill.id == skill_id)
            )
            skill = skill_result.scalar_one_or_none()

        if not skill:
            raise ValueError(f"Skill {skill_id} not found")

        # Delete skill file from project
        success = await self.file_service.delete_skill_from_project(
            project_path=project.path,
            skill_file_name=skill.file_name
        )

        if not success:
            logger.warning(f"Failed to delete skill file from project (may not exist)")

        # Delete from project_skills
        await self.db.delete(project_skill)
        await self.db.commit()

        logger.info(f"Disabled skill {skill.name} for project {project_id}")

    async def create_custom_skill(
        self,
        project_id: str,
        skill_create: SkillCreate
    ) -> SkillInDB:
        """
        Create a custom skill record (step 1 of 2)

        This creates the database record with status "creating".
        The actual CLI interaction happens in background task.
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Validate skill name
        if not self.creation_service.validate_skill_name(skill_create.name):
            raise ValueError(f"Invalid skill name: {skill_create.name}")

        # Check for duplicate name
        existing = await self.db.execute(
            select(CustomSkill).where(
                and_(
                    CustomSkill.project_id == project_id,
                    CustomSkill.name == skill_create.name
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Skill with name '{skill_create.name}' already exists")

        # Generate file name
        file_name = self._generate_skill_file_name(skill_create.name)

        # Create custom skill record
        custom_skill = CustomSkill(
            project_id=project_id,
            name=skill_create.name,
            description=skill_create.description,
            category="Custom",  # Default category for custom skills
            file_name=file_name,
            status="creating",  # Will be updated by background task
            created_by="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(custom_skill)
        await self.db.commit()
        await self.db.refresh(custom_skill)

        logger.info(f"Created custom skill record {custom_skill.id} for project {project_id}")

        return self._to_skill_dto(custom_skill, "custom", False, project.path)

    async def execute_skill_creation_cli(
        self,
        project_id: str,
        skill_id: int,
        skill_name: str,
        skill_description: str
    ):
        """
        Execute Claude Code CLI to create skill (background task)

        This is step 2 of 2 for custom skill creation.
        """
        try:
            # Get project
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Sanitize inputs
            safe_name = self.creation_service.sanitize_skill_input(skill_name)
            safe_description = self.creation_service.sanitize_skill_input(skill_description)

            # Execute CLI command
            result = await self.creation_service.create_skill_via_claude_cli(
                project_path=project.path,
                skill_name=safe_name,
                skill_description=safe_description
            )

            if result["success"]:
                # Update skill status to active
                skill_result = await self.db.execute(
                    select(CustomSkill).where(CustomSkill.id == skill_id)
                )
                custom_skill = skill_result.scalar_one_or_none()

                if custom_skill:
                    custom_skill.status = "active"
                    custom_skill.content = result.get("content", "")
                    custom_skill.updated_at = datetime.utcnow()

                    # Enable skill immediately
                    project_skill = ProjectSkill(
                        project_id=project_id,
                        skill_id=skill_id,
                        skill_type="custom",
                        enabled_at=datetime.utcnow(),
                        enabled_by="user"
                    )
                    self.db.add(project_skill)

                    await self.db.commit()

                    logger.info(f"Successfully created custom skill {skill_name} for project {project_id}")
            else:
                # Update skill status to failed
                skill_result = await self.db.execute(
                    select(CustomSkill).where(CustomSkill.id == skill_id)
                )
                custom_skill = skill_result.scalar_one_or_none()

                if custom_skill:
                    custom_skill.status = "failed"
                    custom_skill.error_message = result.get("error", "Unknown error")
                    custom_skill.updated_at = datetime.utcnow()
                    await self.db.commit()

                    logger.error(f"Failed to create custom skill {skill_name}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Exception in skill creation CLI execution: {e}", exc_info=True)

            # Update skill status to failed
            try:
                skill_result = await self.db.execute(
                    select(CustomSkill).where(CustomSkill.id == skill_id)
                )
                custom_skill = skill_result.scalar_one_or_none()

                if custom_skill:
                    custom_skill.status = "failed"
                    custom_skill.error_message = str(e)
                    custom_skill.updated_at = datetime.utcnow()
                    await self.db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update skill status: {update_error}")

    async def delete_custom_skill(self, project_id: str, skill_id: int):
        """
        Delete a custom skill permanently

        Process:
        1. Verify skill is custom (not default)
        2. Remove from project_skills junction table
        3. Delete skill file from .claude/skills/
        4. Delete record from custom_skills table
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get custom skill
        result = await self.db.execute(
            select(CustomSkill).where(
                and_(
                    CustomSkill.id == skill_id,
                    CustomSkill.project_id == project_id
                )
            )
        )
        custom_skill = result.scalar_one_or_none()

        if not custom_skill:
            raise ValueError(f"Custom skill {skill_id} not found")

        # Delete from project_skills if enabled
        project_skill_result = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id,
                    ProjectSkill.skill_type == "custom"
                )
            )
        )
        project_skill = project_skill_result.scalar_one_or_none()

        if project_skill:
            await self.db.delete(project_skill)

        # Delete skill file
        await self.file_service.delete_skill_from_project(
            project_path=project.path,
            skill_file_name=custom_skill.file_name
        )

        # Delete custom_skills record
        await self.db.delete(custom_skill)
        await self.db.commit()

        logger.info(f"Deleted custom skill {custom_skill.name} from project {project_id}")

    async def get_default_skills(self) -> List[SkillInDB]:
        """Get all default skills catalog"""
        result = await self.db.execute(
            select(DefaultSkill).where(DefaultSkill.is_active == True)
        )
        skills = result.scalars().all()

        return [
            self._to_skill_dto(skill, "default", False, "")
            for skill in skills
        ]

    async def get_agent_recommended_skills(
        self,
        project_id: str,
        agent_name: str
    ) -> List[SkillInDB]:
        """Get recommended skills for a specific agent"""
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get recommendations
        result = await self.db.execute(
            select(AgentSkillRecommendation, DefaultSkill)
            .join(DefaultSkill, AgentSkillRecommendation.skill_id == DefaultSkill.id)
            .where(AgentSkillRecommendation.agent_name == agent_name)
            .order_by(AgentSkillRecommendation.priority)
        )
        recommendations = result.all()

        # Check which skills are enabled
        enabled_result = await self.db.execute(
            select(ProjectSkill).where(ProjectSkill.project_id == project_id)
        )
        enabled_skills = {
            (ps.skill_id, ps.skill_type) for ps in enabled_result.scalars().all()
        }

        skills = []
        for rec, skill in recommendations:
            is_enabled = (skill.id, "default") in enabled_skills
            skills.append(self._to_skill_dto(skill, "default", is_enabled, project.path))

        return skills

    # Helper methods

    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    def _to_skill_dto(
        self,
        skill: Any,
        skill_type: str,
        is_enabled: bool,
        project_path: str
    ) -> SkillInDB:
        """Convert database model to DTO"""
        file_path = None
        if is_enabled and project_path:
            file_path = os.path.join(project_path, ".claude", "skills", skill.file_name)

        return SkillInDB(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            skill_type=skill_type,
            category=skill.category,
            file_path=file_path,
            is_enabled=is_enabled,
            status=getattr(skill, "status", None),
            created_by=getattr(skill, "created_by", "system"),
            created_at=skill.created_at,
            updated_at=skill.updated_at
        )

    def _generate_skill_file_name(self, skill_name: str) -> str:
        """Generate file name from skill name"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        file_name = skill_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.md"
