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
        source_type: str = "default",
        source_project_path: str = None
    ) -> bool:
        """
        Copy skill file from framework-assets or custom archive to project

        Args:
            project_path: Path to destination project root
            skill_file_name: Name of skill file (e.g., "business-requirements-analysis.md")
            source_type: "default" (from framework-assets) or "custom" (from .claudetask/custom-skills/)
            source_project_path: For custom skills from other projects, path to the source project

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"copy_skill_to_project called: project_path={project_path}, skill_file_name={skill_file_name}, source_type={source_type}, source_project_path={source_project_path}")
            # Source path
            if source_type == "default":
                # Check if skill_file_name contains a directory (e.g., "api-development/skill.md")
                if '/' in skill_file_name:
                    # Extract directory name (e.g., "api-development")
                    skill_dir = skill_file_name.split('/')[0]
                    # Source is the entire skill directory
                    source_path = os.path.join(self.framework_skills_dir, skill_dir)
                    logger.info(f"Detected directory-based skill: source_path={source_path}")
                else:
                    # Single file skill
                    source_path = os.path.join(self.framework_skills_dir, skill_file_name)
                    logger.info(f"Detected single-file skill: source_path={source_path}")
            else:
                # For custom skills, determine the source project path
                # If source_project_path is provided, use that (for favorites from other projects)
                # Otherwise, use current project path (for skills from current project)
                actual_source_project = source_project_path if source_project_path else project_path

                # Source is in .claudetask/custom-skills/ (archive)
                archive_dir = os.path.join(actual_source_project, ".claudetask", "custom-skills")
                if '/' in skill_file_name:
                    # Directory-based custom skill
                    skill_dir = skill_file_name.split('/')[0]
                    source_path = os.path.join(archive_dir, skill_dir)
                else:
                    # Single file custom skill
                    source_path = os.path.join(archive_dir, skill_file_name)
                logger.info(f"Custom skill source from archive: source_path={source_path} (source_project={actual_source_project})")

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

            # Check if source is a directory (for skills like api-development/skill.md)
            if os.path.isdir(source_path):
                # Copy entire skill directory
                # Extract directory name from skill_file_name (e.g., "test-runner" from "test-runner/skill.md")
                if '/' in skill_file_name:
                    skill_name = skill_file_name.split('/')[0]
                else:
                    skill_name = os.path.splitext(os.path.basename(skill_file_name))[0]

                logger.info(f"Copying skill directory: source={source_path}, skill_name={skill_name}")
                dest_skill_dir = os.path.join(dest_dir, skill_name)

                # Remove destination if exists
                if os.path.exists(dest_skill_dir):
                    shutil.rmtree(dest_skill_dir)

                # Copy entire directory
                shutil.copytree(source_path, dest_skill_dir)
                logger.info(f"Copied skill directory {skill_file_name} to {dest_skill_dir}")
                return True
            else:
                # Copy single file
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
        Delete skill file or directory from project's .claude/skills/ (active skills)

        NOTE: This only removes from .claude/skills/ (active directory).
        For custom skills, the original remains in .claudetask/skills/ (archive).

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file to delete (e.g., "api-development/skill.md")

        Returns:
            True if successful, False otherwise
        """
        try:
            # For directory-based skills (e.g., "api-development/skill.md"),
            # delete the entire directory, not just the file
            if '/' in skill_file_name:
                # Extract directory name (e.g., "api-development")
                skill_dir = skill_file_name.split('/')[0]
                dir_path = os.path.join(project_path, ".claude", "skills", skill_dir)

                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                    logger.info(f"Deleted skill directory {dir_path}")
                    return True
                else:
                    logger.warning(f"Skill directory not found (already deleted?): {dir_path}")
                    return True
            else:
                # Single file skill
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

    async def archive_custom_skill(
        self,
        project_path: str,
        skill_file_name: str
    ) -> bool:
        """
        Archive custom skill to .claudetask/custom-skills/ for persistent storage

        This creates a backup of custom skills so they can be re-enabled later.
        Called after skill creation is complete.

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file (e.g., "my-custom-skill.md")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Source: .claude/skills/
            source_dir = os.path.join(project_path, ".claude", "skills")

            # Destination: .claudetask/custom-skills/
            archive_dir = os.path.join(project_path, ".claudetask", "custom-skills")
            os.makedirs(archive_dir, exist_ok=True)

            if '/' in skill_file_name:
                # Directory-based skill
                skill_dir = skill_file_name.split('/')[0]
                source_path = os.path.join(source_dir, skill_dir)
                dest_path = os.path.join(archive_dir, skill_dir)

                # Remove old archive if exists
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)

                # Copy to archive
                if os.path.exists(source_path):
                    shutil.copytree(source_path, dest_path)
                    logger.info(f"Archived custom skill directory to .claudetask/custom-skills/: {skill_dir}")
                    return True
                else:
                    logger.warning(f"Source skill directory not found: {source_path}")
                    return False
            else:
                # Single file skill
                source_path = os.path.join(source_dir, skill_file_name)
                dest_path = os.path.join(archive_dir, skill_file_name)

                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Archived custom skill file to .claudetask/custom-skills/: {skill_file_name}")
                    return True
                else:
                    logger.warning(f"Source skill file not found: {source_path}")
                    return False

        except Exception as e:
            logger.error(f"Failed to archive custom skill: {e}", exc_info=True)
            return False

    async def update_skill_content_in_archive(
        self,
        project_path: str,
        skill_file_name: str,
        new_content: str
    ) -> bool:
        """
        Update skill content in archive (.claudetask/custom-skills/)

        This is called when user edits skill content through UI.
        Updates the archived copy so it can be re-enabled later with new content.

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file (e.g., "my-skill.md" or "my-skill/SKILL.md")
            new_content: New skill content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            # Archive directory: .claudetask/custom-skills/
            archive_dir = os.path.join(project_path, ".claudetask", "custom-skills")
            os.makedirs(archive_dir, exist_ok=True)

            if '/' in skill_file_name:
                # Directory-based skill (e.g., "ui-web-designer-hub/SKILL.md")
                # Extract directory and file parts
                parts = skill_file_name.split('/')
                skill_dir = parts[0]
                file_in_dir = parts[1] if len(parts) > 1 else "SKILL.md"
                
                # Full path to file in archive
                archive_file_path = os.path.join(archive_dir, skill_dir, file_in_dir)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(archive_file_path), exist_ok=True)
            else:
                # Single file skill
                archive_file_path = os.path.join(archive_dir, skill_file_name)

            # Write new content to archive
            async with aiofiles.open(archive_file_path, 'w', encoding='utf-8') as f:
                await f.write(new_content)

            logger.info(f"Updated skill content in archive: {archive_file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to update skill content in archive: {e}", exc_info=True)
            return False

    async def permanently_delete_custom_skill(
        self,
        project_path: str,
        skill_file_name: str
    ) -> bool:
        """
        Permanently delete custom skill from both .claude/skills/ and .claudetask/custom-skills/

        This is used when user explicitly deletes a custom skill (not just disables).

        Args:
            project_path: Path to project root
            skill_file_name: Name of skill file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            success = True

            # Delete from active skills (.claude/skills/)
            if not await self.delete_skill_from_project(project_path, skill_file_name):
                success = False

            # Delete from archive (.claudetask/custom-skills/)
            archive_dir = os.path.join(project_path, ".claudetask", "custom-skills")

            if '/' in skill_file_name:
                # Directory-based skill
                skill_dir = skill_file_name.split('/')[0]
                archive_path = os.path.join(archive_dir, skill_dir)

                if os.path.exists(archive_path):
                    shutil.rmtree(archive_path)
                    logger.info(f"Permanently deleted skill archive: {archive_path}")
            else:
                # Single file skill
                archive_path = os.path.join(archive_dir, skill_file_name)

                if os.path.exists(archive_path):
                    os.remove(archive_path)
                    logger.info(f"Permanently deleted skill archive: {archive_path}")

            return success

        except Exception as e:
            logger.error(f"Failed to permanently delete custom skill: {e}", exc_info=True)
            return False

    async def read_skill_content(self, project_path: str, skill_file_name: str) -> Optional[str]:
        """Read skill file content

        Supports both formats:
        - Direct .md file: skills/skill-name.md
        - Directory with SKILL.md: skills/skill-name/SKILL.md
        """
        try:
            skills_dir = os.path.join(project_path, ".claude", "skills")

            # Remove .md extension if present to get base name
            base_name = skill_file_name.replace('.md', '')

            # Try directory format first (multi-file skill package)
            dir_path = os.path.join(skills_dir, base_name, "SKILL.md")
            if os.path.exists(dir_path):
                async with aiofiles.open(dir_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return content

            # Try direct file format (single file skill)
            file_path = os.path.join(skills_dir, skill_file_name)
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return content

            logger.error(f"Skill file not found: tried {dir_path} and {file_path}")
            return None

        except Exception as e:
            logger.error(f"Failed to read skill file: {e}", exc_info=True)
            return None

    async def skill_exists_in_project(self, project_path: str, skill_file_name: str) -> bool:
        """Check if skill file exists in project

        Supports both formats:
        - Direct .md file: skills/skill-name.md
        - Directory with SKILL.md: skills/skill-name/SKILL.md
        """
        skills_dir = os.path.join(project_path, ".claude", "skills")

        # Remove .md extension if present to get base name
        base_name = skill_file_name.replace('.md', '')

        # Check directory format first (multi-file skill package)
        dir_path = os.path.join(skills_dir, base_name, "SKILL.md")
        if os.path.exists(dir_path):
            return True

        # Check direct file format (single file skill)
        file_path = os.path.join(skills_dir, skill_file_name)
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
