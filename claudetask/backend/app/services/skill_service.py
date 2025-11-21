"""Service for managing skills"""

import os
import re
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
        - favorites: User favorite skills (cross-project)
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

        # Get custom skills for this project only
        custom_skills_result = await self.db.execute(
            select(CustomSkill).where(CustomSkill.project_id == project_id)
        )
        custom_skills = custom_skills_result.scalars().all()

        # Get ALL favorite custom skills from ALL projects (for Favorites tab)
        favorite_custom_skills_result = await self.db.execute(
            select(CustomSkill).where(CustomSkill.is_favorite == True)
        )
        all_favorite_custom_skills = favorite_custom_skills_result.scalars().all()

        # Organize skills
        enabled = []
        enabled_names = set()  # Track names to avoid duplicates in enabled list
        available_default = []
        favorites = []

        # Process default skills
        for skill in all_default_skills:
            is_enabled = (skill.id, "default") in enabled_skill_ids
            skill_dto = self._to_skill_dto(skill, "default", is_enabled, project.path)

            # Add to available_default (show all default skills)
            available_default.append(skill_dto)

            # Also add to favorites if marked as favorite
            if skill.is_favorite:
                favorites.append(skill_dto)

            # Add to enabled only if enabled and not already added
            if is_enabled and skill.name not in enabled_names:
                enabled.append(skill_dto)
                enabled_names.add(skill.name)

        # Process custom skills (for this project only)
        custom_dtos = []
        for skill in custom_skills:
            is_enabled = (skill.id, "custom") in enabled_skill_ids
            skill_dto = self._to_skill_dto(skill, "custom", is_enabled, project.path)

            # Add to custom list (always show in Custom Skills)
            custom_dtos.append(skill_dto)

            # Add to enabled only if not already added (avoid duplicates)
            if is_enabled and skill.name not in enabled_names:
                enabled.append(skill_dto)
                enabled_names.add(skill.name)

        # Process ALL favorite custom skills (from all projects) for Favorites tab
        favorite_names = set()  # Track names to avoid duplicates in favorites list
        for skill in all_favorite_custom_skills:
            # Check if enabled in current project
            is_enabled = (skill.id, "custom") in enabled_skill_ids
            skill_dto = self._to_skill_dto(skill, "custom", is_enabled, project.path)

            # Add to favorites if not already added (avoid duplicates by name)
            if skill.name not in favorite_names:
                favorites.append(skill_dto)
                favorite_names.add(skill.name)

        return SkillsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_skill(self, project_id: str, skill_id: int, skill_type: str = "default") -> SkillInDB:
        """
        Enable a skill by copying it to project

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

        # Get skill based on skill_type
        if skill_type == "default":
            skill_result = await self.db.execute(
                select(DefaultSkill).where(DefaultSkill.id == skill_id)
            )
            skill = skill_result.scalar_one_or_none()
            source_type = "default"
        else:
            # For custom skills, search across all projects (to support favorites from other projects)
            skill_result = await self.db.execute(
                select(CustomSkill).where(CustomSkill.id == skill_id)
            )
            skill = skill_result.scalar_one_or_none()
            source_type = "custom"

        if not skill:
            raise ValueError(f"Skill {skill_id} not found")

        # Check if already enabled
        existing = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id,
                    ProjectSkill.skill_type == skill_type
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Skill already enabled for project")

        # For custom skills from other projects, get the source project path
        source_project_path = None
        if skill_type == "custom" and skill.project_id != project_id:
            # Skill is from another project - get that project's path
            source_project = await self._get_project(skill.project_id)
            if source_project:
                source_project_path = source_project.path
                logger.info(f"Enabling favorite skill from project {skill.project_id} to project {project_id}")

        # Copy skill file to project
        success = await self.file_service.copy_skill_to_project(
            project_path=project.path,
            skill_file_name=skill.file_name,
            source_type=source_type,
            source_project_path=source_project_path
        )

        if not success:
            raise RuntimeError(f"Failed to copy skill file to project")

        # Insert into project_skills
        project_skill = ProjectSkill(
            project_id=project_id,
            skill_id=skill_id,
            skill_type=skill_type,
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_skill)
        await self.db.commit()

        logger.info(f"Enabled skill {skill.name} for project {project_id}")

        return self._to_skill_dto(skill, skill_type, True, project.path)

    async def disable_skill(self, project_id: str, skill_id: int, skill_type: str = "default"):
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

        # Get project_skill record (with skill_type to avoid multiple rows)
        result = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id,
                    ProjectSkill.skill_type == skill_type
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
            logger.info(f"{'='*80}")
            logger.info(f"Background task started: execute_skill_creation_cli")
            logger.info(f"Project ID: {project_id}")
            logger.info(f"Skill ID: {skill_id}")
            logger.info(f"Skill Name: {skill_name}")
            logger.info(f"{'='*80}")

            # Get project
            logger.debug(f"Getting project {project_id} from database")
            project = await self._get_project(project_id)
            if not project:
                error_msg = f"Project {project_id} not found"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"✓ Project found: {project.name} at {project.path}")

            # Sanitize inputs
            logger.debug("Sanitizing user inputs")
            safe_name = self.creation_service.sanitize_skill_input(skill_name)
            safe_description = self.creation_service.sanitize_skill_input(skill_description)
            logger.info(f"✓ Inputs sanitized: name='{safe_name}', description length={len(safe_description)}")

            # Execute CLI command
            logger.info("Calling create_skill_via_claude_cli...")
            result = await self.creation_service.create_skill_via_claude_cli(
                project_path=project.path,
                skill_name=safe_name,
                skill_description=safe_description
            )
            logger.info(f"✓ create_skill_via_claude_cli returned: success={result.get('success')}")

            if result["success"]:
                logger.info("Skill creation succeeded - updating database")

                # Update skill status to active
                logger.debug(f"Fetching skill {skill_id} from database")
                skill_result = await self.db.execute(
                    select(CustomSkill).where(CustomSkill.id == skill_id)
                )
                custom_skill = skill_result.scalar_one_or_none()

                if custom_skill:
                    logger.info(f"✓ Found skill record in database")

                    # Detect actual file structure created by Skills Creator
                    logger.debug("Detecting skill file structure")
                    actual_file_name = await self._detect_skill_file_structure(
                        project_path=project.path,
                        skill_name=custom_skill.name
                    )

                    # Update file_name if different from initial guess
                    if actual_file_name and actual_file_name != custom_skill.file_name:
                        logger.info(f"✓ Updating skill file_name from {custom_skill.file_name} to {actual_file_name}")
                        custom_skill.file_name = actual_file_name
                    else:
                        logger.debug(f"File name unchanged: {custom_skill.file_name}")

                    logger.info("Updating skill status to 'active'")
                    custom_skill.status = "active"
                    custom_skill.content = result.get("content", "")
                    custom_skill.updated_at = datetime.utcnow()

                    # Archive custom skill to .claudetask/custom-skills/ for persistence
                    logger.info("Archiving custom skill for persistence")
                    archive_success = await self.file_service.archive_custom_skill(
                        project_path=project.path,
                        skill_file_name=custom_skill.file_name
                    )
                    if archive_success:
                        logger.info("✓ Skill archived successfully")
                    else:
                        logger.warning("⚠️ Skill archiving failed (non-critical - skill still works)")

                    # Enable skill immediately
                    logger.info("Enabling skill for project")
                    project_skill = ProjectSkill(
                        project_id=project_id,
                        skill_id=skill_id,
                        skill_type="custom",
                        enabled_at=datetime.utcnow(),
                        enabled_by="user"
                    )
                    self.db.add(project_skill)

                    logger.debug("Committing database changes")
                    await self.db.commit()

                    logger.info(f"{'='*80}")
                    logger.info(f"✓ SUCCESS: Custom skill '{skill_name}' created for project {project_id}")
                    logger.info(f"Skill ID: {skill_id}")
                    logger.info(f"File: {custom_skill.file_name}")
                    logger.info(f"Status: active")
                    logger.info(f"{'='*80}")
                else:
                    logger.error(f"Skill {skill_id} not found in database after creation")
            else:
                logger.warning("Skill creation failed - updating status to 'failed'")

                # Update skill status to failed
                skill_result = await self.db.execute(
                    select(CustomSkill).where(CustomSkill.id == skill_id)
                )
                custom_skill = skill_result.scalar_one_or_none()

                if custom_skill:
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Updating skill {skill_id} to failed status")
                    logger.error(f"Error message: {error_msg}")

                    custom_skill.status = "failed"
                    custom_skill.error_message = error_msg
                    custom_skill.updated_at = datetime.utcnow()
                    await self.db.commit()

                    logger.error(f"{'='*80}")
                    logger.error(f"✗ FAILED: Custom skill '{skill_name}' creation failed")
                    logger.error(f"Skill ID: {skill_id}")
                    logger.error(f"Error: {error_msg}")
                    logger.error(f"{'='*80}")
                else:
                    logger.error(f"Skill {skill_id} not found in database to update failure status")

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

        # Permanently delete skill files (from both .claude/skills/ and .claudetask/skills/)
        await self.file_service.permanently_delete_custom_skill(
            project_path=project.path,
            skill_file_name=custom_skill.file_name
        )

        # Delete custom_skills record
        await self.db.delete(custom_skill)
        await self.db.commit()

        logger.info(f"Permanently deleted custom skill {custom_skill.name} from project {project_id}")

    async def update_custom_skill_status(
        self,
        project_id: str,
        skill_id: int,
        status: str,
        error_message: str | None = None
    ):
        """
        Update custom skill status and archive it

        This is called by MCP tools after skill creation is complete.
        Process:
        1. Update skill status in database
        2. Archive skill to .claudetask/custom-skills/
        3. Enable skill if status is "active"
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
            raise ValueError(f"Custom skill {skill_id} not found for project {project_id}")

        # Update status
        custom_skill.status = status
        if error_message:
            custom_skill.error_message = error_message
        custom_skill.updated_at = datetime.utcnow()

        # If status is active, archive and enable
        if status == "active":
            # Archive to .claudetask/skills/
            await self.file_service.archive_custom_skill(
                project_path=project.path,
                skill_file_name=custom_skill.file_name
            )

            # Enable skill (add to project_skills if not already enabled)
            existing = await self.db.execute(
                select(ProjectSkill).where(
                    and_(
                        ProjectSkill.project_id == project_id,
                        ProjectSkill.skill_id == skill_id,
                        ProjectSkill.skill_type == "custom"
                    )
                )
            )

            if not existing.scalar_one_or_none():
                project_skill = ProjectSkill(
                    project_id=project_id,
                    skill_id=skill_id,
                    skill_type="custom",
                    enabled_at=datetime.utcnow(),
                    enabled_by="user"
                )
                self.db.add(project_skill)

        await self.db.commit()

        logger.info(f"Updated custom skill {custom_skill.name} status to '{status}' for project {project_id}")

    async def update_custom_skill_content(
        self,
        project_id: str,
        skill_id: int,
        new_content: str
    ):
        """
        Update custom skill content through UI

        This is called when user edits skill content through the UI.
        Process:
        1. Update skill content in database
        2. Update archive in .claudetask/custom-skills/
        3. If skill is enabled, update .claude/skills/ as well

        Args:
            project_id: Project ID
            skill_id: Custom skill ID
            new_content: New skill content
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
            raise ValueError(f"Custom skill {skill_id} not found for project {project_id}")

        # Update content in database
        custom_skill.content = new_content
        custom_skill.updated_at = datetime.utcnow()
        await self.db.commit()

        # Update archive in .claudetask/custom-skills/
        await self.file_service.update_skill_content_in_archive(
            project_path=project.path,
            skill_file_name=custom_skill.file_name,
            new_content=new_content
        )

        # Check if skill is enabled
        enabled_result = await self.db.execute(
            select(ProjectSkill).where(
                and_(
                    ProjectSkill.project_id == project_id,
                    ProjectSkill.skill_id == skill_id,
                    ProjectSkill.skill_type == "custom"
                )
            )
        )
        is_enabled = enabled_result.scalar_one_or_none() is not None

        # If enabled, also update .claude/skills/
        if is_enabled:
            await self.file_service.copy_skill_to_project(
                project_path=project.path,
                skill_file_name=custom_skill.file_name,
                source_type="custom"
            )

        logger.info(f"Updated custom skill {custom_skill.name} content for project {project_id}")

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

    async def save_to_favorites(self, project_id: str, skill_id: int, skill_type: str = "custom") -> SkillInDB:
        """
        Mark a skill as favorite

        Process:
        1. Get skill (default or custom)
        2. Verify not already a favorite
        3. Set is_favorite = True

        Args:
            project_id: Project ID (for validation)
            skill_id: ID of the skill to favorite
            skill_type: Type of skill ("default" or "custom")

        This makes the skill appear in Favorites tab
        """
        # Get project (for validation)
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if skill_type == "default":
            # Get default skill
            default_skill_result = await self.db.execute(
                select(DefaultSkill).where(DefaultSkill.id == skill_id)
            )
            skill = default_skill_result.scalar_one_or_none()

            if not skill:
                raise ValueError(f"Default skill {skill_id} not found")

            # Check if already a favorite
            if skill.is_favorite:
                raise ValueError(f"Skill '{skill.name}' is already in favorites")

            # Mark as favorite
            skill.is_favorite = True
            skill.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(skill)

            logger.info(f"Marked default skill '{skill.name}' as favorite (ID: {skill.id})")

            return self._to_skill_dto(skill, "default", False, project.path)
        else:
            # Get custom skill for this project only
            custom_skill_result = await self.db.execute(
                select(CustomSkill).where(
                    and_(
                        CustomSkill.id == skill_id,
                        CustomSkill.project_id == project_id
                    )
                )
            )
            skill = custom_skill_result.scalar_one_or_none()

            if not skill:
                raise ValueError(f"Custom skill {skill_id} not found in this project")

            # Check if already a favorite
            if skill.is_favorite:
                raise ValueError(f"Skill '{skill.name}' is already in favorites")

            # Mark as favorite
            skill.is_favorite = True
            skill.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(skill)

            logger.info(f"Marked custom skill '{skill.name}' as favorite (ID: {skill.id})")

            return self._to_skill_dto(skill, "custom", False, project.path)

    async def remove_from_favorites(self, project_id: str, skill_id: int, skill_type: str = "custom") -> None:
        """
        Unmark a skill as favorite

        Process:
        1. Get skill (default or custom)
        2. Verify it's marked as favorite
        3. Set is_favorite = False

        Args:
            project_id: Project ID (for validation)
            skill_id: ID of the skill to unfavorite
            skill_type: Type of skill ("default" or "custom")
        """
        # Get project (for validation)
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if skill_type == "default":
            # Get default skill
            default_skill_result = await self.db.execute(
                select(DefaultSkill).where(DefaultSkill.id == skill_id)
            )
            skill = default_skill_result.scalar_one_or_none()

            if not skill:
                raise ValueError(f"Default skill {skill_id} not found")

            # Check if it's marked as favorite
            if not skill.is_favorite:
                raise ValueError(f"Skill '{skill.name}' is not in favorites")

            # Unmark as favorite
            skill.is_favorite = False
            skill.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed default skill '{skill.name}' from favorites (ID: {skill_id})")
        else:
            # Get custom skill for this project only
            custom_skill_result = await self.db.execute(
                select(CustomSkill).where(
                    and_(
                        CustomSkill.id == skill_id,
                        CustomSkill.project_id == project_id
                    )
                )
            )
            skill = custom_skill_result.scalar_one_or_none()

            if not skill:
                raise ValueError(f"Custom skill {skill_id} not found in this project")

            # Check if it's marked as favorite
            if not skill.is_favorite:
                raise ValueError(f"Skill '{skill.name}' is not in favorites")

            # Unmark as favorite
            skill.is_favorite = False
            skill.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed custom skill '{skill.name}' from favorites (ID: {skill_id})")

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
            is_favorite=getattr(skill, "is_favorite", False),
            status=getattr(skill, "status", None),
            created_by=getattr(skill, "created_by", "system"),
            created_at=skill.created_at,
            updated_at=skill.updated_at
        )

    def _generate_skill_file_name(self, skill_name: str) -> str:
        """Generate file name from skill name"""
        # Convert to lowercase, replace spaces with hyphens
        file_name = skill_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.md"

    async def _detect_skill_file_structure(self, project_path: str, skill_name: str) -> str:
        """
        Detect actual file structure created by Skills Creator

        Skills Creator can create either:
        - Simple file: skill-name.md
        - Directory structure: skill-name/SKILL.md (with examples/, resources/, templates/)

        Args:
            project_path: Project root path
            skill_name: Name of the skill

        Returns:
            Actual file_name that matches the created structure
        """
        # Generate expected base name
        base_name = skill_name.lower().replace(" ", "-")
        base_name = re.sub(r'[^a-z0-9-_]', '', base_name)

        skills_dir = os.path.join(project_path, ".claude", "skills")

        # Check for directory-based skill (comprehensive package)
        dir_path = os.path.join(skills_dir, base_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            # Check if SKILL.md exists in directory
            skill_md_path = os.path.join(dir_path, "SKILL.md")
            if os.path.exists(skill_md_path):
                logger.info(f"Detected directory-based skill: {base_name}/SKILL.md")
                return f"{base_name}/SKILL.md"

        # Check for simple file-based skill
        file_path = os.path.join(skills_dir, f"{base_name}.md")
        if os.path.exists(file_path):
            logger.info(f"Detected file-based skill: {base_name}.md")
            return f"{base_name}.md"

        # Fallback to generated name if nothing found
        logger.warning(f"Could not detect skill structure for {skill_name}, using default: {base_name}.md")
        return f"{base_name}.md"
