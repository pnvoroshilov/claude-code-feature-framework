"""Service for managing skills with MongoDB backend"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.skill_repository import MongoDBSkillRepository
from ..schemas import SkillInDB, SkillCreate, SkillsResponse
from .skill_file_service import SkillFileService
from .skill_creation_service import SkillCreationService

logger = logging.getLogger(__name__)


class SkillServiceMongoDB:
    """Service for managing skills with MongoDB storage"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = MongoDBSkillRepository(db)
        self.file_service = SkillFileService()
        self.creation_service = SkillCreationService()

    async def get_project_skills(self, project_id: str, project_path: str) -> SkillsResponse:
        """
        Get all skills for a project organized by type.

        Args:
            project_id: Project ID
            project_path: Project filesystem path

        Returns:
            SkillsResponse with enabled, available_default, custom, favorites
        """
        # Get enabled skill IDs
        enabled_ids = await self.repo.get_enabled_skill_ids(project_id)

        # Get all default skills
        all_default = await self.repo.get_all_default_skills()

        # Get custom skills for this project
        custom_skills = await self.repo.get_custom_skills(project_id)

        # Get enabled skills (full details)
        enabled_skills = await self.repo.get_enabled_skills(project_id)

        # Get favorites
        favorite_default = await self.repo.get_favorite_default_skills()
        favorite_custom = await self.repo.get_favorite_custom_skills()

        # Process results
        enabled = []
        available_default = []
        custom_dtos = []
        favorites = []

        enabled_names = set()

        # Process default skills
        for skill in all_default:
            is_enabled = (skill["id"], "default") in enabled_ids
            skill_dto = self._to_skill_dto(skill, is_enabled, project_path)
            available_default.append(skill_dto)

            if skill.get("is_favorite"):
                favorites.append(skill_dto)

            if is_enabled and skill["name"] not in enabled_names:
                enabled.append(skill_dto)
                enabled_names.add(skill["name"])

        # Process custom skills
        for skill in custom_skills:
            is_enabled = (skill["id"], "custom") in enabled_ids
            skill_dto = self._to_skill_dto(skill, is_enabled, project_path)
            custom_dtos.append(skill_dto)

            if is_enabled and skill["name"] not in enabled_names:
                enabled.append(skill_dto)
                enabled_names.add(skill["name"])

        # Process favorites
        favorite_names = {s.name for s in favorites}
        for skill in favorite_custom:
            if skill["name"] not in favorite_names:
                is_enabled = (skill["id"], "custom") in enabled_ids
                skill_dto = self._to_skill_dto(skill, is_enabled, project_path)
                favorites.append(skill_dto)

        return SkillsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_skill(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        skill_type: str = "default",
        source_project_path: Optional[str] = None
    ) -> SkillInDB:
        """
        Enable a skill by copying it to project.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID
            skill_type: "default" or "custom"
            source_project_path: For custom skills from other projects

        Returns:
            Enabled skill DTO
        """
        # Get skill
        if skill_type == "default":
            skill = await self.repo.get_default_skill(skill_id)
        else:
            skill = await self.repo.get_custom_skill(skill_id)

        if not skill:
            raise ValueError(f"Skill {skill_id} not found")

        # Check if already enabled
        if await self.repo.is_skill_enabled(project_id, skill_id, skill_type):
            raise ValueError("Skill already enabled for project")

        # Copy skill file to project
        success = await self.file_service.copy_skill_to_project(
            project_path=project_path,
            skill_file_name=skill["file_name"],
            source_type=skill_type,
            source_project_path=source_project_path
        )

        if not success:
            raise RuntimeError("Failed to copy skill file to project")

        # Enable in database
        await self.repo.enable_skill(project_id, skill_id, skill_type)

        logger.info(f"Enabled skill {skill['name']} for project {project_id}")

        return self._to_skill_dto(skill, True, project_path)

    async def disable_skill(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        skill_type: str = "default"
    ):
        """
        Disable a skill by removing it from project.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID
            skill_type: "default" or "custom"
        """
        # Get skill for file name
        if skill_type == "default":
            skill = await self.repo.get_default_skill(skill_id)
        else:
            skill = await self.repo.get_custom_skill(skill_id)

        if not skill:
            raise ValueError(f"Skill {skill_id} not found")

        # Delete skill file from project
        await self.file_service.delete_skill_from_project(
            project_path=project_path,
            skill_file_name=skill["file_name"]
        )

        # Disable in database
        await self.repo.disable_skill(project_id, skill_id, skill_type)

        logger.info(f"Disabled skill {skill['name']} for project {project_id}")

    async def create_custom_skill(
        self,
        project_id: str,
        project_path: str,
        skill_create: SkillCreate
    ) -> SkillInDB:
        """
        Create a custom skill record (step 1 of 2).

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_create: Skill creation data

        Returns:
            Created skill DTO (status: "creating")
        """
        # Validate skill name
        if not self.creation_service.validate_skill_name(skill_create.name):
            raise ValueError(f"Invalid skill name: {skill_create.name}")

        # Check for duplicate name
        existing = await self.repo.get_custom_skill_by_name(project_id, skill_create.name)
        if existing:
            raise ValueError(f"Skill with name '{skill_create.name}' already exists")

        # Generate file name
        file_name = self._generate_skill_file_name(skill_create.name)

        # Create custom skill record
        skill_id = await self.repo.create_custom_skill({
            "project_id": project_id,
            "name": skill_create.name,
            "description": skill_create.description,
            "category": "Custom",
            "file_name": file_name,
            "status": "creating",
            "created_by": "user"
        })

        skill = await self.repo.get_custom_skill(skill_id)
        logger.info(f"Created custom skill record {skill_id} for project {project_id}")

        return self._to_skill_dto(skill, False, project_path)

    async def execute_skill_creation_cli(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        skill_name: str,
        skill_description: str
    ):
        """
        Execute Claude Code CLI to create skill (background task).

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID in database
            skill_name: Skill name
            skill_description: Skill description
        """
        try:
            logger.info(f"Background task started: execute_skill_creation_cli")
            logger.info(f"Project ID: {project_id}, Skill ID: {skill_id}")

            # Sanitize inputs
            safe_name = self.creation_service.sanitize_skill_input(skill_name)
            safe_description = self.creation_service.sanitize_skill_input(skill_description)

            # Execute CLI command
            result = await self.creation_service.create_skill_via_claude_cli(
                project_path=project_path,
                skill_name=safe_name,
                skill_description=safe_description
            )

            if result["success"]:
                # Detect actual file structure
                actual_file_name = await self._detect_skill_file_structure(
                    project_path=project_path,
                    skill_name=skill_name
                )

                # Update skill status
                await self.repo.update_custom_skill(skill_id, {
                    "status": "active",
                    "file_name": actual_file_name,
                    "content": result.get("content", "")
                })

                # Archive skill
                await self.file_service.archive_custom_skill(
                    project_path=project_path,
                    skill_file_name=actual_file_name
                )

                # Enable skill
                await self.repo.enable_skill(project_id, skill_id, "custom")

                logger.info(f"Custom skill '{skill_name}' created successfully")
            else:
                await self.repo.update_custom_skill(skill_id, {
                    "status": "failed",
                    "error_message": result.get("error", "Unknown error")
                })
                logger.error(f"Custom skill '{skill_name}' creation failed")

        except Exception as e:
            logger.error(f"Exception in skill creation: {e}", exc_info=True)
            await self.repo.update_custom_skill(skill_id, {
                "status": "failed",
                "error_message": str(e)
            })

    async def delete_custom_skill(
        self,
        project_id: str,
        project_path: str,
        skill_id: str
    ):
        """
        Delete a custom skill permanently.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID
        """
        skill = await self.repo.get_custom_skill(skill_id)
        if not skill:
            raise ValueError(f"Custom skill {skill_id} not found")

        if skill.get("project_id") != project_id:
            raise ValueError("Skill belongs to different project")

        # Delete files
        await self.file_service.permanently_delete_custom_skill(
            project_path=project_path,
            skill_file_name=skill["file_name"]
        )

        # Delete from database
        await self.repo.delete_custom_skill(skill_id)

        logger.info(f"Permanently deleted custom skill {skill['name']}")

    async def update_custom_skill_status(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """
        Update custom skill status.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID
            status: New status
            error_message: Error message if failed
        """
        skill = await self.repo.get_custom_skill(skill_id)
        if not skill or skill.get("project_id") != project_id:
            raise ValueError(f"Custom skill {skill_id} not found for project")

        updates = {"status": status}
        if error_message:
            updates["error_message"] = error_message

        await self.repo.update_custom_skill(skill_id, updates)

        if status == "active":
            # Archive and enable
            await self.file_service.archive_custom_skill(
                project_path=project_path,
                skill_file_name=skill["file_name"]
            )
            await self.repo.enable_skill(project_id, skill_id, "custom")

        logger.info(f"Updated custom skill {skill['name']} status to '{status}'")

    async def update_custom_skill_content(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        new_content: str
    ):
        """
        Update custom skill content.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            skill_id: Skill ID
            new_content: New content
        """
        skill = await self.repo.get_custom_skill(skill_id)
        if not skill or skill.get("project_id") != project_id:
            raise ValueError(f"Custom skill {skill_id} not found for project")

        await self.repo.update_custom_skill(skill_id, {"content": new_content})

        # Update archive
        await self.file_service.update_skill_content_in_archive(
            project_path=project_path,
            skill_file_name=skill["file_name"],
            new_content=new_content
        )

        # If enabled, update active file
        if await self.repo.is_skill_enabled(project_id, skill_id, "custom"):
            await self.file_service.copy_skill_to_project(
                project_path=project_path,
                skill_file_name=skill["file_name"],
                source_type="custom"
            )

        logger.info(f"Updated custom skill {skill['name']} content")

    async def get_default_skills(self) -> List[SkillInDB]:
        """Get all default skills catalog."""
        skills = await self.repo.get_all_default_skills()
        return [self._to_skill_dto(s, False, "") for s in skills]

    async def save_to_favorites(
        self,
        project_id: str,
        project_path: str,
        skill_id: str,
        skill_type: str = "custom"
    ) -> SkillInDB:
        """Mark a skill as favorite."""
        if skill_type == "default":
            skill = await self.repo.get_default_skill(skill_id)
            if not skill:
                raise ValueError(f"Default skill {skill_id} not found")
            if skill.get("is_favorite"):
                raise ValueError(f"Skill '{skill['name']}' is already in favorites")
            await self.repo.update_default_skill(skill_id, {"is_favorite": True})
        else:
            skill = await self.repo.get_custom_skill(skill_id)
            if not skill or skill.get("project_id") != project_id:
                raise ValueError(f"Custom skill {skill_id} not found in this project")
            if skill.get("is_favorite"):
                raise ValueError(f"Skill '{skill['name']}' is already in favorites")
            await self.repo.update_custom_skill(skill_id, {"is_favorite": True})

        logger.info(f"Marked skill '{skill['name']}' as favorite")

        skill["is_favorite"] = True
        return self._to_skill_dto(skill, False, project_path)

    async def remove_from_favorites(
        self,
        project_id: str,
        skill_id: str,
        skill_type: str = "custom"
    ):
        """Remove a skill from favorites."""
        if skill_type == "default":
            skill = await self.repo.get_default_skill(skill_id)
            if not skill:
                raise ValueError(f"Default skill {skill_id} not found")
            if not skill.get("is_favorite"):
                raise ValueError(f"Skill '{skill['name']}' is not in favorites")
            await self.repo.update_default_skill(skill_id, {"is_favorite": False})
        else:
            skill = await self.repo.get_custom_skill(skill_id)
            if not skill or skill.get("project_id") != project_id:
                raise ValueError(f"Custom skill {skill_id} not found in this project")
            if not skill.get("is_favorite"):
                raise ValueError(f"Skill '{skill['name']}' is not in favorites")
            await self.repo.update_custom_skill(skill_id, {"is_favorite": False})

        logger.info(f"Removed skill '{skill['name']}' from favorites")

    # ==================
    # Helper Methods
    # ==================

    def _to_skill_dto(
        self,
        skill: Dict[str, Any],
        is_enabled: bool,
        project_path: str
    ) -> SkillInDB:
        """Convert skill dict to DTO."""
        file_path = None
        if is_enabled and project_path:
            file_path = os.path.join(project_path, ".claude", "skills", skill.get("file_name", ""))

        return SkillInDB(
            id=skill.get("id"),
            name=skill["name"],
            description=skill["description"],
            skill_type=skill.get("skill_type", "default"),
            category=skill.get("category", "General"),
            file_path=file_path,
            is_enabled=is_enabled,
            is_favorite=skill.get("is_favorite", False),
            status=skill.get("status"),
            created_by=skill.get("created_by", "system"),
            created_at=skill.get("created_at"),
            updated_at=skill.get("updated_at")
        )

    def _generate_skill_file_name(self, skill_name: str) -> str:
        """Generate file name from skill name."""
        file_name = skill_name.lower().replace(" ", "-")
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.md"

    async def _detect_skill_file_structure(
        self,
        project_path: str,
        skill_name: str
    ) -> str:
        """Detect actual file structure created by Skills Creator."""
        base_name = skill_name.lower().replace(" ", "-")
        base_name = re.sub(r'[^a-z0-9-_]', '', base_name)

        skills_dir = os.path.join(project_path, ".claude", "skills")

        # Check for directory-based skill
        dir_path = os.path.join(skills_dir, base_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            skill_md_path = os.path.join(dir_path, "SKILL.md")
            if os.path.exists(skill_md_path):
                return f"{base_name}/SKILL.md"

        # Check for simple file-based skill
        file_path = os.path.join(skills_dir, f"{base_name}.md")
        if os.path.exists(file_path):
            return f"{base_name}.md"

        return f"{base_name}.md"
