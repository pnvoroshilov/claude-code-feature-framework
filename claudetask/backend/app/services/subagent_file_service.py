"""Service for subagent file system operations"""

import os
import shutil
import logging
import aiofiles
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SubagentFileService:
    """Service for subagent file system operations"""

    def __init__(self):
        # Path to framework-assets/claude-agents/
        self.framework_subagents_dir = self._get_framework_subagents_dir()

    async def copy_subagent_to_project(
        self,
        project_path: str,
        subagent_type: str,
        subagent_config: Optional[str] = None
    ) -> bool:
        """
        Copy or create subagent file in project's .claude/agents/

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent (e.g., "frontend-developer")
            subagent_config: Optional custom configuration content

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"copy_subagent_to_project: project_path={project_path}, subagent_type={subagent_type}")

            # Destination path
            dest_dir = os.path.join(project_path, ".claude", "agents")
            os.makedirs(dest_dir, exist_ok=True)

            # Subagent file name (e.g., "frontend-developer.md")
            file_name = f"{subagent_type}.md"
            dest_path = os.path.join(dest_dir, file_name)

            # If custom config provided, use it
            if subagent_config:
                async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                    await f.write(subagent_config)
                logger.info(f"Created custom subagent file at {dest_path}")
                return True

            # Check if source exists in framework-assets
            source_path = os.path.join(self.framework_subagents_dir, file_name)

            if os.path.exists(source_path):
                # Copy from framework-assets
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied subagent from {source_path} to {dest_path}")
                return True
            else:
                # Create placeholder for default subagents without templates
                placeholder_content = f"""# {subagent_type.replace('-', ' ').title()} Subagent

This is a default subagent configuration managed by the ClaudeTask framework.

## Type
`{subagent_type}`

## Purpose
This subagent provides specialized functionality for your development workflow and is invoked through the Claude Code Task tool.

## Usage
This subagent will be automatically available when you use the Task tool with:
```
subagent_type="{subagent_type}"
```
"""
                async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                    await f.write(placeholder_content)

                logger.info(f"Created placeholder subagent file at {dest_path}")
                return True

        except Exception as e:
            logger.error(f"Error copying subagent to project: {e}")
            return False

    async def delete_subagent_from_project(
        self,
        project_path: str,
        subagent_type: str
    ) -> bool:
        """
        Delete subagent file from project's .claude/agents/

        Args:
            project_path: Path to project root
            subagent_type: Type identifier of subagent to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Subagent file path
            file_name = f"{subagent_type}.md"
            file_path = os.path.join(project_path, ".claude", "agents", file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted subagent file {file_path}")
                return True
            else:
                logger.warning(f"Subagent file not found (already deleted?): {file_path}")
                return True  # Consider it success if already deleted

        except Exception as e:
            logger.error(f"Error deleting subagent from project: {e}")
            return False

    def _get_framework_subagents_dir(self) -> str:
        """Get path to framework-assets/claude-agents/"""
        # Get path relative to this file
        # Structure: claudetask/backend/app/services/subagent_file_service.py
        # We need: framework-assets/claude-agents/ (in project root, not in claudetask/)
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        claudetask_root = os.path.dirname(backend_dir)
        project_root = os.path.dirname(claudetask_root)
        framework_assets_dir = os.path.join(project_root, "framework-assets", "claude-agents")

        logger.info(f"Framework agents directory: {framework_assets_dir}")
        return framework_assets_dir
