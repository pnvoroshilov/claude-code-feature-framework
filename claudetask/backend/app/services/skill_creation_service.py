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
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Create a skill using Claude Code CLI's /create-skill command

        Process:
        1. Start Claude terminal session in project directory
        2. Send /create-skill command
        3. Wait for skill name prompt
        4. Send skill name
        5. Wait for description prompt
        6. Send skill description
        7. Wait for completion (timeout: 60s)
        8. Stop session
        9. Verify skill file was created

        Args:
            project_path: Path to project root
            skill_name: Name of the skill to create
            skill_description: Description of the skill
            timeout: Timeout in seconds (default: 60)

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

            # Send /create-skill command
            await session.send_input("/create-skill")
            logger.info("Sent /create-skill command")

            # Wait for skill name prompt (look for specific pattern in output)
            await asyncio.sleep(3)  # Give Claude time to respond

            # Send skill name
            await session.send_input(skill_name)
            logger.info(f"Sent skill name: {skill_name}")

            # Wait for description prompt
            await asyncio.sleep(2)

            # Send skill description
            await session.send_input(skill_description)
            logger.info(f"Sent skill description")

            # Wait for completion (check for success message in output)
            start_time = asyncio.get_event_loop().time()
            skill_created = False

            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Check if skill file was created
                skill_file_name = self._generate_skill_file_name(skill_name)
                skill_path = os.path.join(project_path, ".claude", "skills", skill_file_name)

                if os.path.exists(skill_path):
                    skill_created = True
                    logger.info(f"Skill file created: {skill_path}")
                    break

                await asyncio.sleep(2)  # Check every 2 seconds

            # Stop session
            await session.stop()

            if skill_created:
                # Read skill content
                with open(skill_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                return {
                    "success": True,
                    "skill_path": skill_path,
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": f"Skill creation timed out after {timeout}s"
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
