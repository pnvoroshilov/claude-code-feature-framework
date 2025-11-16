"""Service for managing hooks"""

import os
import logging
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from ..models import (
    Project, DefaultHook, CustomHook, ProjectHook
)
from ..schemas import HookInDB, HookCreate, HooksResponse
from .hook_file_service import HookFileService
from .hook_creation_service import HookCreationService

logger = logging.getLogger(__name__)


class HookService:
    """Service for managing hooks"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.file_service = HookFileService()
        self.creation_service = HookCreationService()

    async def get_project_hooks(self, project_id: str) -> HooksResponse:
        """
        Get all hooks for a project organized by type

        Returns:
        HooksResponse with:
        - enabled: Currently enabled hooks
        - available_default: Default hooks that can be enabled
        - custom: User-created custom hooks
        - favorites: User favorite hooks (cross-project)
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get all default hooks
        default_hooks_result = await self.db.execute(
            select(DefaultHook).where(DefaultHook.is_active == True)
        )
        all_default_hooks = default_hooks_result.scalars().all()

        # Get enabled hooks for this project
        enabled_hooks_result = await self.db.execute(
            select(ProjectHook).where(ProjectHook.project_id == project_id)
        )
        enabled_project_hooks = enabled_hooks_result.scalars().all()
        enabled_hook_ids = {
            (ph.hook_id, ph.hook_type) for ph in enabled_project_hooks
        }

        # Get custom hooks for this project only
        custom_hooks_result = await self.db.execute(
            select(CustomHook).where(CustomHook.project_id == project_id)
        )
        custom_hooks = custom_hooks_result.scalars().all()

        # Get ALL favorite custom hooks from ALL projects (for Favorites tab)
        favorite_custom_hooks_result = await self.db.execute(
            select(CustomHook).where(CustomHook.is_favorite == True)
        )
        all_favorite_custom_hooks = favorite_custom_hooks_result.scalars().all()

        # Organize hooks
        enabled = []
        enabled_names = set()  # Track names to avoid duplicates in enabled list
        available_default = []
        favorites = []

        # Process default hooks
        for hook in all_default_hooks:
            is_enabled = (hook.id, "default") in enabled_hook_ids
            hook_dto = self._to_hook_dto(hook, "default", is_enabled)

            # Add to available_default (show all default hooks)
            available_default.append(hook_dto)

            # Also add to favorites if marked as favorite
            if hook.is_favorite:
                favorites.append(hook_dto)

            # Add to enabled only if enabled and not already added
            if is_enabled and hook.name not in enabled_names:
                enabled.append(hook_dto)
                enabled_names.add(hook.name)

        # Process custom hooks (for this project only)
        custom_dtos = []
        for hook in custom_hooks:
            is_enabled = (hook.id, "custom") in enabled_hook_ids
            hook_dto = self._to_hook_dto(hook, "custom", is_enabled)

            # Add to custom list (always show in Custom Hooks)
            custom_dtos.append(hook_dto)

            # Add to enabled only if not already added (avoid duplicates)
            if is_enabled and hook.name not in enabled_names:
                enabled.append(hook_dto)
                enabled_names.add(hook.name)

        # Process ALL favorite custom hooks (from all projects) for Favorites tab
        favorite_names = set()  # Track names to avoid duplicates in favorites list
        for hook in all_favorite_custom_hooks:
            # Check if enabled in current project
            is_enabled = (hook.id, "custom") in enabled_hook_ids
            hook_dto = self._to_hook_dto(hook, "custom", is_enabled)

            # Add to favorites if not already added (avoid duplicates by name)
            if hook.name not in favorite_names:
                favorites.append(hook_dto)
                favorite_names.add(hook.name)

        return HooksResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_hook(self, project_id: str, hook_id: int) -> HookInDB:
        """
        Enable a default hook by merging it into settings.json

        Process:
        1. Validate hook exists
        2. Merge hook configuration into .claude/settings.json
        3. Insert into project_hooks junction table
        4. Return enabled hook
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get hook (assume default for now, can extend to custom)
        hook_result = await self.db.execute(
            select(DefaultHook).where(DefaultHook.id == hook_id)
        )
        hook = hook_result.scalar_one_or_none()

        if not hook:
            raise ValueError(f"Hook {hook_id} not found")

        # Check if already enabled (idempotent - return success if already enabled)
        existing = await self.db.execute(
            select(ProjectHook).where(
                and_(
                    ProjectHook.project_id == project_id,
                    ProjectHook.hook_id == hook_id,
                    ProjectHook.hook_type == "default"
                )
            )
        )
        existing_hook = existing.scalar_one_or_none()
        if existing_hook:
            logger.info(f"Hook {hook.name} already enabled for project {project_id}")
            return self._to_hook_dto(hook, "default", True)

        # Copy script file if hook uses separate script (e.g., post-push-docs.sh)
        if hasattr(hook, 'script_file') and hook.script_file:
            script_copy_success = await self.file_service.copy_hook_script(
                project_path=project.path,
                script_file_name=hook.script_file
            )
            if not script_copy_success:
                logger.warning(f"Failed to copy script file {hook.script_file}, but continuing with hook activation")

        # Apply hook to settings.json
        success = await self.file_service.apply_hook_to_settings(
            project_path=project.path,
            hook_name=hook.name,
            hook_config=hook.hook_config
        )

        if not success:
            raise RuntimeError(f"Failed to apply hook to settings.json")

        # Insert into project_hooks
        project_hook = ProjectHook(
            project_id=project_id,
            hook_id=hook_id,
            hook_type="default",
            enabled_at=datetime.utcnow(),
            enabled_by="user"
        )
        self.db.add(project_hook)
        await self.db.commit()

        logger.info(f"Enabled hook {hook.name} for project {project_id}")

        return self._to_hook_dto(hook, "default", True)

    async def disable_hook(self, project_id: str, hook_id: int):
        """
        Disable a hook by removing it from settings.json

        Process:
        1. Delete from project_hooks junction table
        2. Remove hook configuration from .claude/settings.json
        3. Keep record in custom_hooks if custom (don't delete)
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get project_hook record
        result = await self.db.execute(
            select(ProjectHook).where(
                and_(
                    ProjectHook.project_id == project_id,
                    ProjectHook.hook_id == hook_id
                )
            )
        )
        project_hook = result.scalar_one_or_none()

        if not project_hook:
            raise ValueError(f"Hook not enabled for project")

        # Get hook details
        if project_hook.hook_type == "default":
            hook_result = await self.db.execute(
                select(DefaultHook).where(DefaultHook.id == hook_id)
            )
            hook = hook_result.scalar_one_or_none()
        else:
            hook_result = await self.db.execute(
                select(CustomHook).where(CustomHook.id == hook_id)
            )
            hook = hook_result.scalar_one_or_none()

        if not hook:
            raise ValueError(f"Hook {hook_id} not found")

        # Remove hook from settings.json
        success = await self.file_service.remove_hook_from_settings(
            project_path=project.path,
            hook_name=hook.name
        )

        if not success:
            logger.warning(f"Failed to remove hook from settings.json (may not exist)")

        # Delete from project_hooks
        await self.db.delete(project_hook)
        await self.db.commit()

        logger.info(f"Disabled hook {hook.name} for project {project_id}")

    async def create_custom_hook(
        self,
        project_id: str,
        hook_create: HookCreate
    ) -> HookInDB:
        """
        Create a custom hook record (step 1 of 2)

        This creates the database record with status "creating".
        The actual CLI interaction happens in background task.
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Validate hook name
        if not self.creation_service.validate_hook_name(hook_create.name):
            raise ValueError(f"Invalid hook name: {hook_create.name}")

        # Check for duplicate name
        existing = await self.db.execute(
            select(CustomHook).where(
                and_(
                    CustomHook.project_id == project_id,
                    CustomHook.name == hook_create.name
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Hook with name '{hook_create.name}' already exists")

        # Generate file name
        file_name = self._generate_hook_file_name(hook_create.name)

        # Create custom hook record
        custom_hook = CustomHook(
            project_id=project_id,
            name=hook_create.name,
            description=hook_create.description,
            category=hook_create.category,
            file_name=file_name,
            hook_config=hook_create.hook_config,
            setup_instructions=hook_create.setup_instructions,
            dependencies=hook_create.dependencies,
            status="creating",  # Will be updated by background task
            created_by="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(custom_hook)
        await self.db.commit()
        await self.db.refresh(custom_hook)

        logger.info(f"Created custom hook record {custom_hook.id} for project {project_id}")

        return self._to_hook_dto(custom_hook, "custom", False)

    async def execute_hook_creation_cli(
        self,
        project_id: str,
        hook_id: int,
        hook_name: str,
        hook_description: str
    ):
        """
        Execute Claude Code CLI to create hook (background task)

        This is step 2 of 2 for custom hook creation.
        """
        try:
            # Get project
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Sanitize inputs
            safe_name = self.creation_service.sanitize_hook_input(hook_name)
            safe_description = self.creation_service.sanitize_hook_input(hook_description)

            # Execute CLI command
            result = await self.creation_service.create_hook_via_claude_cli(
                project_path=project.path,
                hook_name=safe_name,
                hook_description=safe_description
            )

            if result["success"]:
                # Update hook status to active
                hook_result = await self.db.execute(
                    select(CustomHook).where(CustomHook.id == hook_id)
                )
                custom_hook = hook_result.scalar_one_or_none()

                if custom_hook:
                    custom_hook.status = "active"
                    hook_config = result.get("hook_config", {})
                    custom_hook.hook_config = hook_config
                    custom_hook.updated_at = datetime.utcnow()

                    # 🔴 CRITICAL: Apply hook to .claude/settings.json
                    settings_applied = await self.file_service.apply_hook_to_settings(
                        project_path=project.path,
                        hook_name=hook_name,
                        hook_config=hook_config
                    )

                    if not settings_applied:
                        logger.error(f"Failed to apply hook {hook_name} to settings.json")
                        custom_hook.status = "failed"
                        custom_hook.error_message = "Failed to apply hook to settings.json"
                        await self.db.commit()
                        return

                    # Enable hook immediately (add to ProjectHook table)
                    project_hook = ProjectHook(
                        project_id=project_id,
                        hook_id=hook_id,
                        hook_type="custom",
                        enabled_at=datetime.utcnow(),
                        enabled_by="user"
                    )
                    self.db.add(project_hook)

                    await self.db.commit()

                    logger.info(f"Successfully created custom hook {hook_name} and applied to settings.json for project {project_id}")
            else:
                # Update hook status to failed
                hook_result = await self.db.execute(
                    select(CustomHook).where(CustomHook.id == hook_id)
                )
                custom_hook = hook_result.scalar_one_or_none()

                if custom_hook:
                    custom_hook.status = "failed"
                    custom_hook.error_message = result.get("error", "Unknown error")
                    custom_hook.updated_at = datetime.utcnow()
                    await self.db.commit()

                    logger.error(f"Failed to create custom hook {hook_name}: {result.get('error')}")

        except Exception as e:
            logger.error(f"Exception in hook creation CLI execution: {e}", exc_info=True)

            # Update hook status to failed
            try:
                hook_result = await self.db.execute(
                    select(CustomHook).where(CustomHook.id == hook_id)
                )
                custom_hook = hook_result.scalar_one_or_none()

                if custom_hook:
                    custom_hook.status = "failed"
                    custom_hook.error_message = str(e)
                    custom_hook.updated_at = datetime.utcnow()
                    await self.db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update hook status: {update_error}")

    async def update_hook(self, project_id: str, hook_id: int, hook_update: HookCreate) -> HookInDB:
        """
        Update a hook (custom or default)

        Process:
        1. Verify hook exists
        2. Update hook metadata in database
        3. If hook is enabled, update .claude/settings.json with new config
        4. Return updated hook details
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Try to find hook in custom_hooks first
        result = await self.db.execute(
            select(CustomHook).where(
                and_(
                    CustomHook.id == hook_id,
                    CustomHook.project_id == project_id
                )
            )
        )
        custom_hook = result.scalar_one_or_none()

        if custom_hook:
            # Save old name for settings.json cleanup
            old_hook_name = custom_hook.name

            # Update custom hook
            custom_hook.name = hook_update.name
            custom_hook.description = hook_update.description
            custom_hook.category = hook_update.category
            custom_hook.hook_config = hook_update.hook_config
            custom_hook.setup_instructions = hook_update.setup_instructions
            custom_hook.dependencies = hook_update.dependencies
            custom_hook.updated_at = datetime.utcnow()

            # Check if hook is enabled
            project_hook_result = await self.db.execute(
                select(ProjectHook).where(
                    and_(
                        ProjectHook.project_id == project_id,
                        ProjectHook.hook_id == hook_id,
                        ProjectHook.hook_type == "custom"
                    )
                )
            )
            project_hook = project_hook_result.scalar_one_or_none()

            # If enabled, update settings.json
            if project_hook:
                # Rebuild entire settings.json from all enabled hooks
                await self._rebuild_settings_json(project_id, project.path)

            await self.db.commit()
            await self.db.refresh(custom_hook)

            # Return as HookInDB
            is_enabled = project_hook is not None
            return self._to_hook_dto(custom_hook, "custom", is_enabled)

        # Try to find in default_hooks
        result = await self.db.execute(
            select(DefaultHook).where(DefaultHook.id == hook_id)
        )
        default_hook = result.scalar_one_or_none()

        if default_hook:
            # Save old name for settings.json cleanup
            old_hook_name = default_hook.name

            # Update default hook (only admins should be able to do this)
            default_hook.name = hook_update.name
            default_hook.description = hook_update.description
            default_hook.category = hook_update.category
            default_hook.hook_config = hook_update.hook_config
            default_hook.setup_instructions = hook_update.setup_instructions
            default_hook.dependencies = hook_update.dependencies
            default_hook.updated_at = datetime.utcnow()

            # Check if hook is enabled
            project_hook_result = await self.db.execute(
                select(ProjectHook).where(
                    and_(
                        ProjectHook.project_id == project_id,
                        ProjectHook.hook_id == hook_id,
                        ProjectHook.hook_type == "default"
                    )
                )
            )
            project_hook = project_hook_result.scalar_one_or_none()

            # If enabled, update settings.json
            if project_hook:
                # Rebuild entire settings.json from all enabled hooks
                await self._rebuild_settings_json(project_id, project.path)

            await self.db.commit()
            await self.db.refresh(default_hook)

            # Return as HookInDB
            is_enabled = project_hook is not None
            return self._to_hook_dto(default_hook, "default", is_enabled)

        raise ValueError(f"Hook {hook_id} not found")

    async def delete_custom_hook(self, project_id: str, hook_id: int):
        """
        Delete a custom hook permanently

        Process:
        1. Verify hook is custom (not default)
        2. Remove from project_hooks junction table
        3. Remove hook from .claude/settings.json
        4. Delete record from custom_hooks table
        """
        # Get project
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get custom hook
        result = await self.db.execute(
            select(CustomHook).where(
                and_(
                    CustomHook.id == hook_id,
                    CustomHook.project_id == project_id
                )
            )
        )
        custom_hook = result.scalar_one_or_none()

        if not custom_hook:
            raise ValueError(f"Custom hook {hook_id} not found")

        # Delete from project_hooks if enabled
        project_hook_result = await self.db.execute(
            select(ProjectHook).where(
                and_(
                    ProjectHook.project_id == project_id,
                    ProjectHook.hook_id == hook_id,
                    ProjectHook.hook_type == "custom"
                )
            )
        )
        project_hook = project_hook_result.scalar_one_or_none()

        if project_hook:
            await self.db.delete(project_hook)

        # Remove hook from settings.json
        await self.file_service.remove_hook_from_settings(
            project_path=project.path,
            hook_name=custom_hook.name
        )

        # Delete custom_hooks record
        await self.db.delete(custom_hook)
        await self.db.commit()

        logger.info(f"Deleted custom hook {custom_hook.name} from project {project_id}")

    async def get_default_hooks(self) -> List[HookInDB]:
        """Get all default hooks catalog"""
        result = await self.db.execute(
            select(DefaultHook).where(DefaultHook.is_active == True)
        )
        hooks = result.scalars().all()

        return [
            self._to_hook_dto(hook, "default", False)
            for hook in hooks
        ]

    async def save_to_favorites(self, project_id: str, hook_id: int, hook_type: str = "custom") -> HookInDB:
        """
        Mark a hook as favorite

        Process:
        1. Get hook (default or custom)
        2. Verify not already a favorite
        3. Set is_favorite = True

        Args:
            project_id: Project ID (for validation)
            hook_id: ID of the hook to favorite
            hook_type: Type of hook ("default" or "custom")

        This makes the hook appear in Favorites tab
        """
        # Get project (for validation)
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if hook_type == "default":
            # Get default hook
            default_hook_result = await self.db.execute(
                select(DefaultHook).where(DefaultHook.id == hook_id)
            )
            hook = default_hook_result.scalar_one_or_none()

            if not hook:
                raise ValueError(f"Default hook {hook_id} not found")

            # Check if already a favorite
            if hook.is_favorite:
                raise ValueError(f"Hook '{hook.name}' is already in favorites")

            # Mark as favorite
            hook.is_favorite = True
            hook.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(hook)

            logger.info(f"Marked default hook '{hook.name}' as favorite (ID: {hook.id})")

            return self._to_hook_dto(hook, "default", False)
        else:
            # Get custom hook for this project only
            custom_hook_result = await self.db.execute(
                select(CustomHook).where(
                    and_(
                        CustomHook.id == hook_id,
                        CustomHook.project_id == project_id
                    )
                )
            )
            hook = custom_hook_result.scalar_one_or_none()

            if not hook:
                raise ValueError(f"Custom hook {hook_id} not found in this project")

            # Check if already a favorite
            if hook.is_favorite:
                raise ValueError(f"Hook '{hook.name}' is already in favorites")

            # Mark as favorite
            hook.is_favorite = True
            hook.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(hook)

            logger.info(f"Marked custom hook '{hook.name}' as favorite (ID: {hook.id})")

            return self._to_hook_dto(hook, "custom", False)

    async def remove_from_favorites(self, project_id: str, hook_id: int, hook_type: str = "custom") -> None:
        """
        Unmark a hook as favorite

        Process:
        1. Get hook (default or custom)
        2. Verify it's marked as favorite
        3. Set is_favorite = False

        Args:
            project_id: Project ID (for validation)
            hook_id: ID of the hook to unfavorite
            hook_type: Type of hook ("default" or "custom")
        """
        # Get project (for validation)
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if hook_type == "default":
            # Get default hook
            default_hook_result = await self.db.execute(
                select(DefaultHook).where(DefaultHook.id == hook_id)
            )
            hook = default_hook_result.scalar_one_or_none()

            if not hook:
                raise ValueError(f"Default hook {hook_id} not found")

            # Check if it's marked as favorite
            if not hook.is_favorite:
                raise ValueError(f"Hook '{hook.name}' is not in favorites")

            # Unmark as favorite
            hook.is_favorite = False
            hook.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed default hook '{hook.name}' from favorites (ID: {hook_id})")
        else:
            # Get custom hook for this project only
            custom_hook_result = await self.db.execute(
                select(CustomHook).where(
                    and_(
                        CustomHook.id == hook_id,
                        CustomHook.project_id == project_id
                    )
                )
            )
            hook = custom_hook_result.scalar_one_or_none()

            if not hook:
                raise ValueError(f"Custom hook {hook_id} not found in this project")

            # Check if it's marked as favorite
            if not hook.is_favorite:
                raise ValueError(f"Hook '{hook.name}' is not in favorites")

            # Unmark as favorite
            hook.is_favorite = False
            hook.updated_at = datetime.utcnow()

            await self.db.commit()

            logger.info(f"Removed custom hook '{hook.name}' from favorites (ID: {hook_id})")

    # Helper methods

    async def _get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    def _to_hook_dto(
        self,
        hook: Any,
        hook_type: str,
        is_enabled: bool
    ) -> HookInDB:
        """Convert database model to DTO"""
        return HookInDB(
            id=hook.id,
            name=hook.name,
            description=hook.description,
            hook_type=hook_type,
            category=hook.category,
            hook_config=hook.hook_config,
            setup_instructions=getattr(hook, "setup_instructions", None),
            dependencies=getattr(hook, "dependencies", None),
            is_enabled=is_enabled,
            is_favorite=getattr(hook, "is_favorite", False),
            status=getattr(hook, "status", None),
            created_by=getattr(hook, "created_by", "system"),
            created_at=hook.created_at,
            updated_at=hook.updated_at
        )

    def _generate_hook_file_name(self, hook_name: str) -> str:
        """Generate file name from hook name"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        file_name = hook_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.json"

    async def _rebuild_settings_json(self, project_id: str, project_path: str):
        """
        Rebuild .claude/settings.json from all enabled hooks in database

        This is called when a hook is updated to ensure settings.json reflects
        the current state of all enabled hooks.
        """
        # Get all enabled hooks for this project
        enabled_hooks_result = await self.db.execute(
            select(ProjectHook).where(ProjectHook.project_id == project_id)
        )
        enabled_project_hooks = enabled_hooks_result.scalars().all()

        # Build complete hooks configuration
        merged_hooks_config = {}

        for project_hook in enabled_project_hooks:
            # Get hook configuration
            if project_hook.hook_type == "default":
                hook_result = await self.db.execute(
                    select(DefaultHook).where(DefaultHook.id == project_hook.hook_id)
                )
                hook = hook_result.scalar_one_or_none()
            else:
                hook_result = await self.db.execute(
                    select(CustomHook).where(CustomHook.id == project_hook.hook_id)
                )
                hook = hook_result.scalar_one_or_none()

            if not hook:
                continue

            # Merge hook config into merged_hooks_config
            for event_type, event_hooks in hook.hook_config.items():
                if event_type not in merged_hooks_config:
                    merged_hooks_config[event_type] = []

                # Add all matchers from this hook
                for matcher_config in event_hooks:
                    # Avoid duplicates by checking matcher name
                    existing_matchers = [m.get("matcher") for m in merged_hooks_config[event_type]]
                    if matcher_config.get("matcher") not in existing_matchers:
                        merged_hooks_config[event_type].append(matcher_config)

        # Apply the merged configuration to settings.json
        await self.file_service.apply_hooks_to_settings(
            project_path=project_path,
            hooks=merged_hooks_config
        )

        logger.info(f"Rebuilt settings.json for project {project_id} with {len(enabled_project_hooks)} hooks")
