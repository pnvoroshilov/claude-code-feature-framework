"""Service for creating skills via Claude Code CLI"""

import os
import asyncio
import logging
from typing import Dict, Any
from .claude_terminal_service import ClaudeTerminalSession

logger = logging.getLogger(__name__)


class SkillCreationService:
    """Service for creating skills using Claude Code CLI's /create-skill command"""

    async def create_skill_via_claude_cli(
        self,
        project_path: str,
        skill_name: str,
        skill_description: str,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Create a skill using Claude Code CLI's /create-skill command

        Process:
        1. Start Claude terminal session in project directory
        2. Send command: /create-skill "Name" "Description"
        3. Claude Code executes /create-skill slash command
        4. Command delegates to skills-creator agent
        5. Wait for skill file to be created (NO TIMEOUT - waits indefinitely)
        6. Stop session when file is created
        7. Verify skill file was created and read its content

        Args:
            project_path: Path to project root
            skill_name: Name of the skill to create
            skill_description: Description of the skill
            timeout: Timeout in seconds (None = no timeout, waits indefinitely)

        Returns:
            {
                "success": bool,
                "skill_path": str,  # Path to created skill file
                "content": str,     # Content of skill file
                "error": str        # Error message if failed
            }
        """
        session = None

        try:
            # Create session ID
            session_id = f"skill-creation-{skill_name}-{asyncio.get_event_loop().time()}"

            # Start Claude terminal session
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=0,  # No task associated
                working_dir=project_path
            )

            if not await session.start():
                return {
                    "success": False,
                    "error": "Failed to start Claude terminal session"
                }

            logger.info(f"Started Claude session {session_id} for skill creation")

            # Wait for Claude to initialize
            await asyncio.sleep(2)

            # Send /create-skill command with arguments
            # Format: /create-skill "Skill Name" "Skill Description"
            command = f'/create-skill "{skill_name}" "{skill_description}"'

            await session.send_input(command)
            logger.info(f"Sent command: {command}")

            # Wait for completion - NO TIMEOUT, wait indefinitely until file is created
            skill_file_name = self._generate_skill_file_name(skill_name)
            skill_path = os.path.join(project_path, ".claude", "skills", skill_file_name)

            logger.info(f"Waiting for skill file to be created: {skill_path}")
            logger.info(f"No timeout - will wait as long as needed...")

            check_count = 0
            while True:
                # Check if skill file was created
                if os.path.exists(skill_path):
                    logger.info(f"Skill file created after {check_count * 2} seconds: {skill_path}")
                    break

                check_count += 1
                if check_count % 30 == 0:  # Log every minute
                    logger.info(f"Still waiting for skill file... ({check_count * 2}s elapsed)")

                await asyncio.sleep(2)  # Check every 2 seconds

            # Stop session
            await session.stop()

            # Read skill content
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "skill_path": skill_path,
                "content": content
            }

        except Exception as e:
            logger.error(f"Error creating skill via CLI: {e}", exc_info=True)

            # Ensure session is stopped
            if session:
                try:
                    await session.stop()
                except:
                    pass

            return {
                "success": False,
                "error": str(e)
            }

    def _generate_skill_file_name(self, skill_name: str) -> str:
        """Generate file name from skill name"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        file_name = skill_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.md"

    def sanitize_skill_input(self, user_input: str) -> str:
        """
        Sanitize user input before sending to Claude CLI

        Prevent:
        - Command injection (;, &&, ||, |, `, $(), etc.)
        - Escape sequences that could break terminal
        - Control characters
        """
        # Remove control characters
        sanitized = ''.join(char for char in user_input if ord(char) >= 32)

        # Remove shell metacharacters
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        return sanitized

    def validate_skill_name(self, name: str) -> bool:
        """
        Validate skill name to prevent:
        - Path traversal (../, ../../, etc.)
        - Command injection (; &, |, etc.)
        - Special characters that could break file systems
        """
        import re
        # Only allow alphanumeric, hyphens, underscores, spaces
        if not re.match(r'^[a-zA-Z0-9-_\s]+$', name):
            return False

        # Check length
        if len(name) < 3 or len(name) > 100:
            return False

        # Prevent path traversal
        if ".." in name or "/" in name or "\\" in name:
            return False

        return True
