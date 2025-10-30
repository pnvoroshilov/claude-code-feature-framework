"""Service for skill file system operations"""

import os
import shutil
import logging
import aiofiles
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SkillFileService:
    """Service for skill file system operations"""

    def __init__(self):
        # Path to framework-assets/claude-skills/
        self.framework_skills_dir = self._get_framework_skills_dir()

    async def copy_skill_to_project(
        self,
        project_path: str,
        skill_file_name: str,
        source_type: str = "default"
    ) -> bool:
        """
        Copy skill file from framework-assets to project

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file (e.g., "business-requirements-analysis.md")
            source_type: "default" (from framework-assets) or "custom" (already in project)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Source path
            if source_type == "default":
                source_path = os.path.join(self.framework_skills_dir, skill_file_name)
            else:
                # For custom skills, source is same as destination (already created)
                return True

            # Destination path
            dest_dir = os.path.join(project_path, ".claude", "skills")
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, skill_file_name)

            # Verify source exists
            if not os.path.exists(source_path):
                logger.warning(f"Source skill file not found: {source_path}, creating placeholder")
                # Create a placeholder skill file if source doesn't exist
                # This allows enabling skills even if template files aren't created yet
                placeholder_content = f"""# {skill_file_name.replace('-', ' ').replace('.md', '').title()}

This is a placeholder skill file. The actual skill content will be generated when you use this skill.

## Purpose

This skill provides specialized functionality for your development workflow.

## Usage

This skill will be automatically invoked by Claude Code when relevant to your tasks.
"""
                async with aiofiles.open(dest_path, 'w', encoding='utf-8') as f:
                    await f.write(placeholder_content)

                logger.info(f"Created placeholder skill file at {dest_path}")
                return True

            # Copy file
            shutil.copy2(source_path, dest_path)

            logger.info(f"Copied skill file {skill_file_name} to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy skill file: {e}", exc_info=True)
            return False

    async def delete_skill_from_project(
        self,
        project_path: str,
        skill_file_name: str
    ) -> bool:
        """
        Delete skill file from project's .claude/skills/

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(project_path, ".claude", "skills", skill_file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted skill file {file_path}")
                return True
            else:
                logger.warning(f"Skill file not found (already deleted?): {file_path}")
                return True  # Consider it success if already deleted

        except Exception as e:
            logger.error(f"Failed to delete skill file: {e}", exc_info=True)
            return False

    async def read_skill_content(self, project_path: str, skill_file_name: str) -> Optional[str]:
        """Read skill file content"""
        try:
            file_path = os.path.join(project_path, ".claude", "skills", skill_file_name)

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()

            return content

        except Exception as e:
            logger.error(f"Failed to read skill file: {e}", exc_info=True)
            return None

    async def skill_exists_in_project(self, project_path: str, skill_file_name: str) -> bool:
        """Check if skill file exists in project"""
        file_path = os.path.join(project_path, ".claude", "skills", skill_file_name)
        return os.path.exists(file_path)

    def _get_framework_skills_dir(self) -> str:
        """Get path to framework-assets/claude-skills/"""
        # Navigate up from services directory to framework root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # backend/app/services -> backend -> claudetask -> project_root
        project_root = Path(current_dir).parent.parent.parent.parent
        framework_skills_dir = os.path.join(project_root, "framework-assets", "claude-skills")

        if not os.path.exists(framework_skills_dir):
            logger.warning(f"Framework skills directory not found: {framework_skills_dir}")

        return framework_skills_dir

    def validate_skill_file_path(self, project_path: str, skill_file_name: str) -> bool:
        """
        Validate that skill file path is within .claude/skills/ directory
        Prevents path traversal attacks
        """
        try:
            # Resolve absolute paths
            skills_dir = os.path.abspath(os.path.join(project_path, ".claude", "skills"))
            target_file = os.path.abspath(os.path.join(skills_dir, skill_file_name))

            # Ensure target is within skills_dir
            if not target_file.startswith(skills_dir):
                logger.error(f"Invalid skill file path (path traversal detected): {target_file}")
                return False

            return True
        except Exception as e:
            logger.error(f"Failed to validate skill file path: {e}")
            return False
