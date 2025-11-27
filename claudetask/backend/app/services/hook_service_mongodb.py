"""Service for managing hooks with MongoDB backend"""

import os
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..repositories.hook_repository import MongoDBHookRepository
from ..schemas import HookInDB, HookCreate, HooksResponse
from .hook_file_service import HookFileService
from .hook_creation_service import HookCreationService

logger = logging.getLogger(__name__)


class HookServiceMongoDB:
    """Service for managing hooks with MongoDB storage"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = MongoDBHookRepository(db)
        self.file_service = HookFileService()
        self.creation_service = HookCreationService()

    async def get_project_hooks(self, project_id: str, project_path: str) -> HooksResponse:
        """
        Get all hooks for a project organized by type.

        Args:
            project_id: Project ID
            project_path: Project filesystem path

        Returns:
            HooksResponse with enabled, available_default, custom, favorites
        """
        # Get enabled hook IDs
        enabled_ids = await self.repo.get_enabled_hook_ids(project_id)

        # Get all default hooks
        all_default = await self.repo.get_all_default_hooks()

        # Get custom hooks for this project
        custom_hooks = await self.repo.get_custom_hooks(project_id)

        # Get favorites
        favorite_default = await self.repo.get_favorite_default_hooks()
        favorite_custom = await self.repo.get_favorite_custom_hooks()

        # Process results
        enabled = []
        available_default = []
        custom_dtos = []
        favorites = []

        enabled_names = set()

        # Process default hooks
        for hook in all_default:
            is_enabled = (hook["id"], "default") in enabled_ids
            hook_dto = self._to_hook_dto(hook, is_enabled)
            available_default.append(hook_dto)

            if hook.get("is_favorite"):
                favorites.append(hook_dto)

            if is_enabled and hook["name"] not in enabled_names:
                enabled.append(hook_dto)
                enabled_names.add(hook["name"])

        # Process custom hooks
        for hook in custom_hooks:
            is_enabled = (hook["id"], "custom") in enabled_ids
            hook_dto = self._to_hook_dto(hook, is_enabled)
            custom_dtos.append(hook_dto)

            if is_enabled and hook["name"] not in enabled_names:
                enabled.append(hook_dto)
                enabled_names.add(hook["name"])

        # Process favorites
        favorite_names = {s.name for s in favorites}
        for hook in favorite_custom:
            if hook["name"] not in favorite_names:
                is_enabled = (hook["id"], "custom") in enabled_ids
                hook_dto = self._to_hook_dto(hook, is_enabled)
                favorites.append(hook_dto)

        return HooksResponse(
            enabled=enabled,
            available_default=available_default,
            custom=custom_dtos,
            favorites=favorites
        )

    async def enable_hook(
        self,
        project_id: str,
        project_path: str,
        hook_id: str,
        hook_type: str = "default"
    ) -> HookInDB:
        """
        Enable a hook by merging it into settings.json.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_id: Hook ID
            hook_type: "default" or "custom"

        Returns:
            Enabled hook DTO
        """
        # Get hook
        if hook_type == "default":
            hook = await self.repo.get_default_hook(hook_id)
        else:
            hook = await self.repo.get_custom_hook(hook_id)

        if not hook:
            raise ValueError(f"Hook {hook_id} not found")

        # Check if already enabled
        if await self.repo.is_hook_enabled(project_id, hook_id, hook_type):
            logger.info(f"Hook {hook['name']} already enabled for project {project_id}")
            return self._to_hook_dto(hook, True)

        # Copy script file if hook uses separate script
        if hook.get("script_file"):
            script_copy_success = await self.file_service.copy_hook_script(
                project_path=project_path,
                script_file_name=hook["script_file"]
            )
            if not script_copy_success:
                logger.warning(f"Failed to copy script file {hook['script_file']}")

        # Apply hook to settings.json
        success = await self.file_service.apply_hook_to_settings(
            project_path=project_path,
            hook_name=hook["name"],
            hook_config=hook["hook_config"]
        )

        if not success:
            raise RuntimeError("Failed to apply hook to settings.json")

        # Enable in database
        await self.repo.enable_hook(project_id, hook_id, hook_type)

        logger.info(f"Enabled hook {hook['name']} for project {project_id}")

        return self._to_hook_dto(hook, True)

    async def disable_hook(
        self,
        project_id: str,
        project_path: str,
        hook_id: str,
        hook_type: str = "default"
    ):
        """
        Disable a hook by removing it from settings.json.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_id: Hook ID
            hook_type: "default" or "custom"
        """
        # Get hook for name
        if hook_type == "default":
            hook = await self.repo.get_default_hook(hook_id)
        else:
            hook = await self.repo.get_custom_hook(hook_id)

        if not hook:
            raise ValueError(f"Hook {hook_id} not found")

        # Disable in database first
        await self.repo.disable_hook(project_id, hook_id, hook_type)

        # Rebuild settings.json with remaining enabled hooks
        await self._rebuild_settings_json(project_id, project_path)

        logger.info(f"Disabled hook {hook['name']} for project {project_id}")

    async def create_custom_hook(
        self,
        project_id: str,
        project_path: str,
        hook_create: HookCreate
    ) -> HookInDB:
        """
        Create a custom hook record (step 1 of 2).

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_create: Hook creation data

        Returns:
            Created hook DTO (status: "creating")
        """
        # Validate hook name
        if not self.creation_service.validate_hook_name(hook_create.name):
            raise ValueError(f"Invalid hook name: {hook_create.name}")

        # Check for duplicate name
        existing = await self.repo.get_custom_hook_by_name(project_id, hook_create.name)
        if existing:
            raise ValueError(f"Hook with name '{hook_create.name}' already exists")

        # Generate file name
        file_name = self._generate_hook_file_name(hook_create.name)

        # Create custom hook record
        hook_id = await self.repo.create_custom_hook({
            "project_id": project_id,
            "name": hook_create.name,
            "description": hook_create.description,
            "category": hook_create.category or "Custom",
            "file_name": file_name,
            "hook_config": hook_create.hook_config or {},
            "setup_instructions": hook_create.setup_instructions,
            "dependencies": hook_create.dependencies,
            "status": "creating",
            "created_by": "user"
        })

        hook = await self.repo.get_custom_hook(hook_id)
        logger.info(f"Created custom hook record {hook_id} for project {project_id}")

        return self._to_hook_dto(hook, False)

    async def execute_hook_creation_cli(
        self,
        project_id: str,
        project_path: str,
        hook_id: str,
        hook_name: str,
        hook_description: str
    ):
        """
        Execute Claude Code CLI to create hook (background task).

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_id: Hook ID in database
            hook_name: Hook name
            hook_description: Hook description
        """
        try:
            logger.info(f"Background task started: execute_hook_creation_cli")
            logger.info(f"Project ID: {project_id}, Hook ID: {hook_id}")

            # Sanitize inputs
            safe_name = self.creation_service.sanitize_hook_input(hook_name)
            safe_description = self.creation_service.sanitize_hook_input(hook_description)

            # Execute CLI command
            result = await self.creation_service.create_hook_via_claude_cli(
                project_path=project_path,
                hook_name=safe_name,
                hook_description=safe_description
            )

            if result["success"]:
                hook_config = result.get("hook_config", {})

                # Update hook status
                await self.repo.update_custom_hook(hook_id, {
                    "status": "active",
                    "hook_config": hook_config
                })

                # Apply hook to settings.json
                settings_applied = await self.file_service.apply_hook_to_settings(
                    project_path=project_path,
                    hook_name=hook_name,
                    hook_config=hook_config
                )

                if not settings_applied:
                    logger.error(f"Failed to apply hook {hook_name} to settings.json")
                    await self.repo.update_custom_hook(hook_id, {
                        "status": "failed",
                        "error_message": "Failed to apply hook to settings.json"
                    })
                    return

                # Enable hook
                await self.repo.enable_hook(project_id, hook_id, "custom")

                logger.info(f"Custom hook '{hook_name}' created successfully")
            else:
                await self.repo.update_custom_hook(hook_id, {
                    "status": "failed",
                    "error_message": result.get("error", "Unknown error")
                })
                logger.error(f"Custom hook '{hook_name}' creation failed")

        except Exception as e:
            logger.error(f"Exception in hook creation: {e}", exc_info=True)
            await self.repo.update_custom_hook(hook_id, {
                "status": "failed",
                "error_message": str(e)
            })

    async def update_hook(
        self,
        project_id: str,
        project_path: str,
        hook_id: str,
        hook_update: HookCreate
    ) -> HookInDB:
        """
        Update a hook.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_id: Hook ID
            hook_update: Updated hook data

        Returns:
            Updated hook DTO
        """
        # Try custom first
        hook = await self.repo.get_custom_hook(hook_id)
        hook_type = "custom"

        if not hook:
            hook = await self.repo.get_default_hook(hook_id)
            hook_type = "default"

        if not hook:
            raise ValueError(f"Hook {hook_id} not found")

        # Update hook
        updates = {
            "name": hook_update.name,
            "description": hook_update.description,
            "category": hook_update.category,
            "hook_config": hook_update.hook_config,
            "setup_instructions": hook_update.setup_instructions,
            "dependencies": hook_update.dependencies
        }

        if hook_type == "default":
            await self.repo.update_default_hook(hook_id, updates)
        else:
            await self.repo.update_custom_hook(hook_id, updates)

        # If enabled, rebuild settings.json
        if await self.repo.is_hook_enabled(project_id, hook_id, hook_type):
            await self._rebuild_settings_json(project_id, project_path)

        # Get updated hook
        if hook_type == "default":
            hook = await self.repo.get_default_hook(hook_id)
        else:
            hook = await self.repo.get_custom_hook(hook_id)

        is_enabled = await self.repo.is_hook_enabled(project_id, hook_id, hook_type)
        return self._to_hook_dto(hook, is_enabled)

    async def delete_custom_hook(
        self,
        project_id: str,
        project_path: str,
        hook_id: str
    ):
        """
        Delete a custom hook permanently.

        Args:
            project_id: Project ID
            project_path: Project filesystem path
            hook_id: Hook ID
        """
        hook = await self.repo.get_custom_hook(hook_id)
        if not hook:
            raise ValueError(f"Custom hook {hook_id} not found")

        if hook.get("project_id") != project_id:
            raise ValueError("Hook belongs to different project")

        # Remove hook from settings.json
        await self.file_service.remove_hook_from_settings(
            project_path=project_path,
            hook_name=hook["name"]
        )

        # Delete from database
        await self.repo.delete_custom_hook(hook_id)

        logger.info(f"Permanently deleted custom hook {hook['name']}")

    async def get_default_hooks(self) -> List[HookInDB]:
        """Get all default hooks catalog."""
        hooks = await self.repo.get_all_default_hooks()
        return [self._to_hook_dto(h, False) for h in hooks]

    async def save_to_favorites(
        self,
        project_id: str,
        project_path: str,
        hook_id: str,
        hook_type: str = "custom"
    ) -> HookInDB:
        """Mark a hook as favorite."""
        if hook_type == "default":
            hook = await self.repo.get_default_hook(hook_id)
            if not hook:
                raise ValueError(f"Default hook {hook_id} not found")
            if hook.get("is_favorite"):
                raise ValueError(f"Hook '{hook['name']}' is already in favorites")
            await self.repo.update_default_hook(hook_id, {"is_favorite": True})
        else:
            hook = await self.repo.get_custom_hook(hook_id)
            if not hook or hook.get("project_id") != project_id:
                raise ValueError(f"Custom hook {hook_id} not found in this project")
            if hook.get("is_favorite"):
                raise ValueError(f"Hook '{hook['name']}' is already in favorites")
            await self.repo.update_custom_hook(hook_id, {"is_favorite": True})

        logger.info(f"Marked hook '{hook['name']}' as favorite")

        hook["is_favorite"] = True
        return self._to_hook_dto(hook, False)

    async def remove_from_favorites(
        self,
        project_id: str,
        hook_id: str,
        hook_type: str = "custom"
    ):
        """Remove a hook from favorites."""
        if hook_type == "default":
            hook = await self.repo.get_default_hook(hook_id)
            if not hook:
                raise ValueError(f"Default hook {hook_id} not found")
            if not hook.get("is_favorite"):
                raise ValueError(f"Hook '{hook['name']}' is not in favorites")
            await self.repo.update_default_hook(hook_id, {"is_favorite": False})
        else:
            hook = await self.repo.get_custom_hook(hook_id)
            if not hook or hook.get("project_id") != project_id:
                raise ValueError(f"Custom hook {hook_id} not found in this project")
            if not hook.get("is_favorite"):
                raise ValueError(f"Hook '{hook['name']}' is not in favorites")
            await self.repo.update_custom_hook(hook_id, {"is_favorite": False})

        logger.info(f"Removed hook '{hook['name']}' from favorites")

    # ==================
    # Helper Methods
    # ==================

    def _to_hook_dto(self, hook: Dict[str, Any], is_enabled: bool) -> HookInDB:
        """Convert hook dict to DTO."""
        return HookInDB(
            id=hook.get("id"),
            name=hook["name"],
            description=hook["description"],
            hook_type=hook.get("hook_type", "default"),
            category=hook.get("category", "General"),
            hook_config=hook.get("hook_config", {}),
            setup_instructions=hook.get("setup_instructions"),
            dependencies=hook.get("dependencies"),
            is_enabled=is_enabled,
            is_favorite=hook.get("is_favorite", False),
            status=hook.get("status"),
            created_by=hook.get("created_by", "system"),
            created_at=hook.get("created_at"),
            updated_at=hook.get("updated_at")
        )

    def _generate_hook_file_name(self, hook_name: str) -> str:
        """Generate file name from hook name."""
        file_name = hook_name.lower().replace(" ", "-")
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.json"

    async def _rebuild_settings_json(self, project_id: str, project_path: str):
        """
        Rebuild .claude/settings.json from all enabled hooks in database.
        """
        # Get all enabled hooks for this project
        enabled_project_hooks = await self.repo.get_all_enabled_project_hooks(project_id)

        # Build complete hooks configuration
        merged_hooks_config = {}

        for project_hook in enabled_project_hooks:
            hook_id = project_hook["hook_id"]
            hook_type = project_hook["hook_type"]

            # Get hook configuration
            if hook_type == "default":
                hook = await self.repo.get_default_hook(hook_id)
            else:
                hook = await self.repo.get_custom_hook(hook_id)

            if not hook:
                continue

            # Merge hook config
            hook_config = hook.get("hook_config", {})
            for event_type, event_hooks in hook_config.items():
                if event_type not in merged_hooks_config:
                    merged_hooks_config[event_type] = []

                for matcher_config in event_hooks:
                    # Avoid duplicates
                    hook_exists = False
                    for existing_hook in merged_hooks_config[event_type]:
                        if existing_hook.get("matcher") == matcher_config.get("matcher"):
                            existing_commands = [h.get("command") for h in existing_hook.get("hooks", [])]
                            new_commands = [h.get("command") for h in matcher_config.get("hooks", [])]
                            if existing_commands == new_commands:
                                hook_exists = True
                                break

                    if not hook_exists:
                        merged_hooks_config[event_type].append(matcher_config)

        # Apply the merged configuration to settings.json
        await self.file_service.apply_hooks_to_settings(
            project_path=project_path,
            hooks=merged_hooks_config
        )

        logger.info(f"Rebuilt settings.json for project {project_id} with {len(enabled_project_hooks)} hooks")
