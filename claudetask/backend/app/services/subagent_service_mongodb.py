"""Service for managing subagents with MongoDB backend"""

import os
import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from ..repositories.subagent_repository import MongoDBSubagentRepository
from ..repositories.skill_repository import MongoDBSkillRepository
from ..schemas import SubagentInDB, SubagentCreate, SubagentsResponse, SubagentSkillAssignment
from .subagent_file_service import SubagentFileService
from .subagent_creation_service import SubagentCreationService

logger = logging.getLogger(__name__)


class SubagentServiceMongoDB:
    """Service for managing subagents with MongoDB backend."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = MongoDBSubagentRepository(db)
        self.skill_repo = MongoDBSkillRepository(db)
        self.file_service = SubagentFileService()
        self.creation_service = SubagentCreationService()

    async def get_project_subagents(
        self,
        project_id: str,
        project_path: str
    ) -> SubagentsResponse:
        """Get all subagents for a project organized by type."""

        # Get all default subagents
        all_default_subagents = await self.repo.get_all_default_subagents()

        # Get enabled subagent IDs for this project
        enabled_subagent_ids = await self.repo.get_enabled_subagent_ids(project_id)

        # Get custom subagents for this project
        custom_subagents = await self.repo.get_custom_subagents(project_id)

        # Get favorite custom subagents
        all_favorite_custom = await self.repo.get_favorite_custom_subagents()

        # Load all skill assignments
        skill_assignments_by_subagent = {}
        for subagent in all_default_subagents:
            skills = await self.repo.get_subagent_skills(subagent["id"], "default")
            skill_assignments_by_subagent[(subagent["id"], "default")] = skills

        for subagent in custom_subagents:
            skills = await self.repo.get_subagent_skills(subagent["id"], "custom")
            skill_assignments_by_subagent[(subagent["id"], "custom")] = skills

        # Build skill details cache
        skill_details_cache = {}
        for key, assignments in skill_assignments_by_subagent.items():
            for assignment in assignments:
                skill_key = (assignment["skill_id"], assignment["skill_type"])
                if skill_key not in skill_details_cache:
                    if assignment["skill_type"] == "default":
                        skill = await self.skill_repo.get_default_skill(assignment["skill_id"])
                    else:
                        skill = await self.skill_repo.get_custom_skill(assignment["skill_id"])
                    if skill:
                        skill_details_cache[skill_key] = skill

        # Helper to build skill assignments list
        def build_skill_assignments(subagent_id: str, subagent_kind: str) -> List[SubagentSkillAssignment]:
            key = (subagent_id, subagent_kind)
            assignments = skill_assignments_by_subagent.get(key, [])
            result = []
            for assignment in assignments:
                skill_key = (assignment["skill_id"], assignment["skill_type"])
                skill = skill_details_cache.get(skill_key)
                if skill:
                    result.append(SubagentSkillAssignment(
                        skill_id=assignment["skill_id"],
                        skill_type=assignment["skill_type"],
                        skill_name=skill["name"],
                        skill_description=skill["description"],
                        skill_category=skill.get("category", "General"),
                        skill_file_name=skill.get("file_name", ""),
                        assigned_at=assignment.get("assigned_at")
                    ))
            return result

        # Organize subagents
        enabled = []
        available_default = []
        favorites = []

        for subagent in all_default_subagents:
            is_enabled = (subagent["id"], "default") in enabled_subagent_ids
            assigned_skills = build_skill_assignments(subagent["id"], "default")
            subagent_dto = self._to_subagent_dto(subagent, is_enabled, assigned_skills)

            available_default.append(subagent_dto)

            if subagent.get("is_favorite"):
                favorites.append(subagent_dto)

            if is_enabled:
                enabled.append(subagent_dto)

        custom_dtos = []
        for subagent in custom_subagents:
            is_enabled = (subagent["id"], "custom") in enabled_subagent_ids
            assigned_skills = build_skill_assignments(subagent["id"], "custom")
            subagent_dto = self._to_subagent_dto(subagent, is_enabled, assigned_skills)

            custom_dtos.append(subagent_dto)

            if subagent.get("is_favorite"):
                favorites.append(subagent_dto)

            if is_enabled:
                enabled.append(subagent_dto)

        return SubagentsResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_subagent(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        subagent_kind: str = "default"
    ) -> SubagentInDB:
        """Enable a subagent for a project."""

        # Get subagent
        if subagent_kind == "default":
            subagent = await self.repo.get_default_subagent(subagent_id)
        else:
            subagent = await self.repo.get_custom_subagent(subagent_id)

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Check if already enabled
        if await self.repo.is_subagent_enabled(project_id, subagent_id, subagent_kind):
            raise ValueError(f"Subagent already enabled for project")

        # Copy subagent file to project
        subagent_config = subagent.get("config") if subagent_kind == "custom" else None
        source_type = subagent_kind

        success = await self.file_service.copy_subagent_to_project(
            project_path=project_path,
            subagent_type=subagent["subagent_type"],
            subagent_config=subagent_config,
            source_type=source_type
        )

        if not success:
            raise RuntimeError(f"Failed to copy subagent file to project")

        # Enable in database
        await self.repo.enable_subagent(project_id, subagent_id, subagent_kind)

        logger.info(f"Enabled subagent {subagent['name']} for project {project_id}")

        return self._to_subagent_dto(subagent, True)

    async def disable_subagent(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        subagent_kind: str = "default"
    ):
        """Disable a subagent for a project."""

        # Get subagent
        if subagent_kind == "default":
            subagent = await self.repo.get_default_subagent(subagent_id)
        else:
            subagent = await self.repo.get_custom_subagent(subagent_id)

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Delete subagent file from project
        success = await self.file_service.delete_subagent_from_project(
            project_path=project_path,
            subagent_type=subagent["subagent_type"]
        )

        if not success:
            logger.warning(f"Failed to delete subagent file from project (may not exist)")

        # Disable in database
        await self.repo.disable_subagent(project_id, subagent_id, subagent_kind)

        logger.info(f"Disabled subagent {subagent['name']} for project {project_id}")

    async def create_custom_subagent(
        self,
        project_id: str,
        project_path: str,
        subagent_create: SubagentCreate
    ) -> SubagentInDB:
        """Create a custom subagent record."""

        # Validate subagent name
        if not self.creation_service.validate_agent_name(subagent_create.name):
            raise ValueError(f"Invalid subagent name: {subagent_create.name}")

        # Check for duplicate
        existing = await self.repo.get_custom_subagent_by_name(project_id, subagent_create.name)
        if existing:
            raise ValueError(f"Custom subagent with name '{subagent_create.name}' already exists")

        # Convert name to kebab-case
        subagent_type = subagent_create.name.lower().replace(' ', '-')

        # Create record
        subagent_id = await self.repo.create_custom_subagent({
            "project_id": project_id,
            "name": subagent_create.name,
            "description": subagent_create.description,
            "category": subagent_create.category or "Custom",
            "subagent_type": subagent_type,
            "config": subagent_create.config,
            "tools_available": subagent_create.tools_available or ["Read", "Write", "Edit", "Bash", "Grep"],
            "status": "creating",
            "created_by": "user"
        })

        subagent = await self.repo.get_custom_subagent(subagent_id)
        logger.info(f"Created custom subagent record {subagent_id} for project {project_id}")

        return self._to_subagent_dto(subagent, False)

    async def execute_subagent_creation_cli(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        agent_name: str,
        agent_description: str
    ):
        """Execute Claude Code CLI to create subagent (background task)."""
        try:
            safe_name = self.creation_service.sanitize_agent_input(agent_name)
            safe_description = self.creation_service.sanitize_agent_input(agent_description)

            result = await self.creation_service.create_subagent_via_claude_cli(
                project_path=project_path,
                agent_name=safe_name,
                agent_description=safe_description
            )

            if result["success"]:
                subagent = await self.repo.get_custom_subagent(subagent_id)
                if subagent:
                    await self.repo.update_custom_subagent(subagent_id, {
                        "status": "active",
                        "config": result.get("content", "")
                    })

                    # Archive custom subagent
                    await self.file_service.archive_custom_subagent(
                        project_path=project_path,
                        subagent_type=subagent["subagent_type"]
                    )

                    # Enable subagent
                    await self.repo.enable_subagent(project_id, subagent_id, "custom")

                    logger.info(f"Successfully created custom subagent {agent_name}")
            else:
                await self.repo.update_custom_subagent(subagent_id, {
                    "status": "failed",
                    "error_message": result.get("error", "Unknown error")
                })
                logger.error(f"Failed to create custom subagent {agent_name}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Exception in subagent creation: {e}", exc_info=True)
            try:
                await self.repo.update_custom_subagent(subagent_id, {
                    "status": "failed",
                    "error_message": str(e)
                })
            except Exception as update_error:
                logger.error(f"Failed to update subagent status: {update_error}")

    async def delete_custom_subagent(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str
    ):
        """Delete a custom subagent permanently."""

        subagent = await self.repo.get_custom_subagent(subagent_id)
        if not subagent:
            raise ValueError(f"Custom subagent {subagent_id} not found")

        if subagent.get("project_id") != project_id:
            raise ValueError(f"Custom subagent {subagent_id} not found for project {project_id}")

        # Delete files
        success = await self.file_service.permanently_delete_custom_subagent(
            project_path=project_path,
            subagent_type=subagent["subagent_type"]
        )

        if not success:
            logger.warning(f"Failed to delete subagent files")

        # Delete from database
        await self.repo.delete_custom_subagent(subagent_id)

        logger.info(f"Deleted custom subagent {subagent['name']} from project {project_id}")

    async def update_custom_subagent_status(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        status: str,
        error_message: str | None = None
    ):
        """Update custom subagent status."""

        subagent = await self.repo.get_custom_subagent(subagent_id)
        if not subagent:
            raise ValueError(f"Custom subagent {subagent_id} not found")

        if subagent.get("project_id") != project_id:
            raise ValueError(f"Custom subagent not found for project {project_id}")

        updates = {"status": status}
        if error_message:
            updates["error_message"] = error_message

        await self.repo.update_custom_subagent(subagent_id, updates)

        if status == "active":
            # Archive and enable
            await self.file_service.archive_custom_subagent(
                project_path=project_path,
                subagent_type=subagent["subagent_type"]
            )

            if not await self.repo.is_subagent_enabled(project_id, subagent_id, "custom"):
                await self.repo.enable_subagent(project_id, subagent_id, "custom")

        logger.info(f"Updated subagent {subagent['name']} status to '{status}'")

    async def get_default_subagents(self) -> List[SubagentInDB]:
        """Get all default subagents catalog."""
        subagents = await self.repo.get_all_default_subagents()
        return [self._to_subagent_dto(s, False) for s in subagents]

    async def save_to_favorites(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        subagent_kind: str = "custom"
    ) -> SubagentInDB:
        """Mark a subagent as favorite."""

        if subagent_kind == "default":
            subagent = await self.repo.get_default_subagent(subagent_id)
            if not subagent:
                raise ValueError(f"Default subagent {subagent_id} not found")

            if subagent.get("is_favorite"):
                raise ValueError(f"Subagent '{subagent['name']}' is already in favorites")

            await self.repo.update_default_subagent(subagent_id, {"is_favorite": True})
            subagent["is_favorite"] = True
        else:
            subagent = await self.repo.get_custom_subagent(subagent_id)
            if not subagent:
                raise ValueError(f"Custom subagent {subagent_id} not found")

            if subagent.get("is_favorite"):
                raise ValueError(f"Subagent '{subagent['name']}' is already in favorites")

            await self.repo.update_custom_subagent(subagent_id, {"is_favorite": True})
            subagent["is_favorite"] = True

        logger.info(f"Marked subagent '{subagent['name']}' as favorite")
        return self._to_subagent_dto(subagent, False)

    async def remove_from_favorites(
        self,
        project_id: str,
        subagent_id: str,
        subagent_kind: str = "custom"
    ):
        """Remove a subagent from favorites."""

        if subagent_kind == "default":
            subagent = await self.repo.get_default_subagent(subagent_id)
            if not subagent:
                raise ValueError(f"Default subagent {subagent_id} not found")

            if not subagent.get("is_favorite"):
                raise ValueError(f"Subagent '{subagent['name']}' is not in favorites")

            await self.repo.update_default_subagent(subagent_id, {"is_favorite": False})
        else:
            subagent = await self.repo.get_custom_subagent(subagent_id)
            if not subagent:
                raise ValueError(f"Custom subagent {subagent_id} not found")

            if not subagent.get("is_favorite"):
                raise ValueError(f"Subagent '{subagent['name']}' is not in favorites")

            await self.repo.update_custom_subagent(subagent_id, {"is_favorite": False})

        logger.info(f"Removed subagent from favorites")

    async def set_subagent_skills(
        self,
        project_id: str,
        project_path: str,
        subagent_id: str,
        subagent_kind: str,
        skill_ids: List[str],
        skill_types: List[str]
    ) -> List[SubagentSkillAssignment]:
        """Set skills for a subagent."""

        if len(skill_ids) != len(skill_types):
            raise ValueError("skill_ids and skill_types must have the same length")

        # Get subagent
        if subagent_kind == "default":
            subagent = await self.repo.get_default_subagent(subagent_id)
        else:
            subagent = await self.repo.get_custom_subagent(subagent_id)

        if not subagent:
            raise ValueError(f"Subagent {subagent_id} not found")

        # Clear existing skills
        await self.repo.clear_subagent_skills(subagent_id, subagent_kind)

        # Create new assignments
        new_assignments = []
        for skill_id, skill_type in zip(skill_ids, skill_types):
            if skill_type == "default":
                skill = await self.skill_repo.get_default_skill(skill_id)
            else:
                skill = await self.skill_repo.get_custom_skill(skill_id)

            if not skill:
                logger.warning(f"Skill {skill_id} not found, skipping")
                continue

            await self.repo.assign_skill(subagent_id, subagent_kind, skill_id, skill_type)

            new_assignments.append(SubagentSkillAssignment(
                skill_id=skill_id,
                skill_type=skill_type,
                skill_name=skill["name"],
                skill_description=skill["description"],
                skill_category=skill.get("category", "General"),
                skill_file_name=skill.get("file_name", ""),
                assigned_at=datetime.utcnow()
            ))

        logger.info(f"Set {len(new_assignments)} skills for subagent '{subagent['name']}'")

        # Update agent file
        if new_assignments:
            skills_data = [
                {
                    'name': s.skill_name,
                    'description': s.skill_description,
                    'category': s.skill_category,
                    'file_name': s.skill_file_name
                }
                for s in new_assignments
            ]
            await self.file_service.update_agent_skills(
                project_path=project_path,
                subagent_type=subagent["subagent_type"],
                skills=skills_data,
                source_type=subagent_kind
            )
        else:
            await self.file_service.update_agent_skills(
                project_path=project_path,
                subagent_type=subagent["subagent_type"],
                skills=[],
                source_type=subagent_kind
            )

        return new_assignments

    def _to_subagent_dto(
        self,
        subagent: Dict[str, Any],
        is_enabled: bool,
        assigned_skills: List[SubagentSkillAssignment] = None
    ) -> SubagentInDB:
        """Convert subagent dict to DTO."""
        return SubagentInDB(
            id=subagent["id"],
            name=subagent["name"],
            description=subagent["description"],
            category=subagent.get("category", "General"),
            subagent_type=subagent.get("subagent_type"),
            subagent_kind=subagent.get("subagent_kind", "default"),
            tools_available=subagent.get("tools_available", []),
            recommended_for=subagent.get("recommended_for", []),
            is_enabled=is_enabled,
            is_favorite=subagent.get("is_favorite", False),
            status=subagent.get("status"),
            created_by=subagent.get("created_by"),
            assigned_skills=assigned_skills or [],
            created_at=subagent.get("created_at"),
            updated_at=subagent.get("updated_at")
        )
