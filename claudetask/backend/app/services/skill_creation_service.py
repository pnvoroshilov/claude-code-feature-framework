"""Service for creating skills via Claude Code CLI"""

import os
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from .claude_terminal_service import ClaudeTerminalSession

# Setup logger with file handler for skill creation
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
def setup_skill_creation_logger():
    """Setup file handler for skill creation logs"""
    # Get project root (4 levels up from this file)
    backend_dir = Path(__file__).parent.parent.parent
    logs_dir = backend_dir / "logs" / "skill_creation"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Create file handler with daily rotation
    log_file = logs_dir / f"skill_creation_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Create formatter with detailed info
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger if not already added
    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

    return log_file

# Initialize logger on module load
skill_creation_log_file = setup_skill_creation_logger()
logger.info(f"Skill creation logger initialized. Log file: {skill_creation_log_file}")


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

            logger.info(f"=" * 80)
            logger.info(f"Starting skill creation process")
            logger.info(f"Skill name: {skill_name}")
            logger.info(f"Description: {skill_description}")
            logger.info(f"Project path: {project_path}")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"=" * 80)

            # Start Claude terminal session
            logger.debug(f"Creating ClaudeTerminalSession instance")
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=0,  # No task associated
                working_dir=project_path,
                skip_permissions=True  # Use dangerous mode for skill creation (directory already trusted)
            )

            logger.debug(f"Starting Claude terminal session...")
            session_started = await session.start()

            if not session_started:
                error_msg = "Failed to start Claude terminal session"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }

            logger.info(f"✓ Claude session {session_id} started successfully")

            # Claude already initialized in session.start() with 5 second delay
            # No additional wait needed here

            # Handle MCP server selection prompt (if appears)
            # Send Enter to confirm default selection and proceed
            logger.debug("Sending Enter key to handle MCP prompt")
            await session.send_key("enter")
            logger.info("✓ Sent Enter key to handle MCP prompt")

            # Wait a bit for prompt to process
            logger.debug("Waiting 1 second for prompt to process")
            await asyncio.sleep(1)

            # Send /create-skill command with arguments
            # Format: /create-skill "Skill Name" "Skill Description"
            command = f'/create-skill "{skill_name}" "{skill_description}"'
            logger.info(f"Preparing to send command: {command}")

            await session.send_input(command)
            logger.info(f"✓ Command sent to Claude session")

            # Ensure command is executed by sending Enter key
            logger.debug("Waiting 0.5 seconds before sending Enter")
            await asyncio.sleep(0.5)
            await session.send_key("enter")
            logger.info("✓ Enter key sent to execute command")

            # Session will run until agent calls MCP complete_skill_creation_session
            # or timeout is reached (30 minutes)
            logger.info(f"{'='*80}")
            logger.info(f"Skill creation session {session_id} is now running")
            logger.info(f"Waiting for agent to complete skill creation...")
            logger.info(f"Will check for skill files every 10 seconds")
            logger.info(f"Timeout: 30 minutes (1800 seconds)")
            logger.info(f"Agent should call mcp__claudetask__complete_skill_creation_session when done")
            logger.info(f"{'='*80}")

            # Wait for timeout (30 minutes = 1800 seconds)
            # BUT check for skill files every 10 seconds
            timeout = 1800
            check_interval = 10  # Check every 10 seconds
            elapsed = 0

            skill_dir_name = self._generate_skill_dir_name(skill_name)
            skill_dir_path = os.path.join(project_path, ".claude", "skills", skill_dir_name)
            skill_file_path = os.path.join(skill_dir_path, "SKILL.md")
            legacy_file_name = self._generate_skill_file_name(skill_name)
            legacy_file_path = os.path.join(project_path, ".claude", "skills", legacy_file_name)

            skill_created = False

            # Periodically check for skill files
            while elapsed < timeout:
                await asyncio.sleep(check_interval)
                elapsed += check_interval

                # Check if skill files were created
                if os.path.exists(skill_file_path) or os.path.exists(legacy_file_path):
                    logger.info(f"{'='*80}")
                    logger.info(f"✓ SKILL FILES DETECTED after {elapsed}s!")
                    logger.info(f"Skill creation completed successfully")
                    logger.info(f"Stopping session...")
                    logger.info(f"{'='*80}")
                    skill_created = True
                    break

                # Log progress every 60 seconds
                if elapsed % 60 == 0:
                    remaining = timeout - elapsed
                    logger.debug(f"Progress: {elapsed}s elapsed, {remaining}s remaining (session: {session_id})")

            # Stop session
            if not skill_created:
                # Timeout occurred
                logger.warning(f"{'='*80}")
                logger.warning(f"TIMEOUT: Skill creation session {session_id} timed out after {timeout}s")
                logger.warning(f"Agent did not complete skill creation within 30 minutes")
                logger.warning(f"Stopping session...")
                logger.warning(f"{'='*80}")

            await session.stop()
            logger.info(f"✓ Session stopped (skill_created={skill_created})")

            # Read skill file content if created
            skill_path = None
            content = None

            if skill_created:
                # Files already exist - we checked in the loop
                logger.info("Reading skill file content...")
                logger.debug(f"Checking multi-file skill path: {skill_file_path}")
                logger.debug(f"Checking legacy skill path: {legacy_file_path}")

                if os.path.exists(skill_file_path):
                    skill_path = skill_file_path
                    logger.info(f"✓ Found multi-file skill at: {skill_file_path}")
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.debug(f"Skill file size: {len(content)} characters")
                elif os.path.exists(legacy_file_path):
                    skill_path = legacy_file_path
                    logger.info(f"✓ Found legacy skill at: {legacy_file_path}")
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.debug(f"Skill file size: {len(content)} characters")

                if skill_path:
                    logger.info(f"{'='*80}")
                    logger.info(f"SUCCESS: Skill created successfully")
                    logger.info(f"Skill path: {skill_path}")
                    logger.info(f"Content length: {len(content)} characters")
                    logger.info(f"Time taken: {elapsed}s")
                    logger.info(f"{'='*80}")
                    return {
                        "success": True,
                        "skill_path": skill_path,
                        "content": content,
                        "timeout": False
                    }
                else:
                    # Files disappeared between detection and reading (race condition)
                    logger.error("ERROR: Skill files disappeared after detection!")

            # If we're here, skill was not created or files disappeared
            error_msg = f"Skill creation {'timed out' if not skill_created else 'failed'} after {elapsed}s. No skill file was created."
            logger.error(f"{'='*80}")
            logger.error(f"FAILED: {error_msg}")
            logger.error(f"{'='*80}")
            return {
                "success": False,
                "skill_path": None,
                "content": None,
                "timeout": not skill_created,
                "error": error_msg
            }

        except Exception as e:
            logger.error(f"{'='*80}")
            logger.error(f"EXCEPTION in skill creation via CLI")
            logger.error(f"Error: {e}", exc_info=True)
            logger.error(f"{'='*80}")

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

    def _generate_skill_dir_name(self, skill_name: str) -> str:
        """Generate directory name from skill name (for multi-file skills)"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        dir_name = skill_name.lower().replace(" ", "-")
        # Remove special characters
        dir_name = re.sub(r'[^a-z0-9-_]', '', dir_name)
        return dir_name

    def _generate_skill_file_name(self, skill_name: str) -> str:
        """Generate file name from skill name (for legacy single-file skills)"""
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

        Note: Allows Unicode characters (Cyrillic, Chinese, etc.)
        """
        # Remove control characters but allow Unicode printable characters
        # Keep characters with ord >= 32 (includes ASCII printable + Unicode)
        sanitized = ''.join(char for char in user_input if ord(char) >= 32 or char in ['\t'])

        # Remove shell metacharacters (but NOT Unicode text)
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')

        # Remove literal newlines and carriage returns (but preserve as spaces)
        sanitized = sanitized.replace('\n', ' ').replace('\r', ' ')

        return sanitized.strip()

    def validate_skill_name(self, name: str) -> bool:
        """
        Validate skill name to prevent:
        - Path traversal (../, ../../, etc.)
        - Command injection (; &, |, etc.)
        - Special characters that could break file systems

        Allows Unicode characters (Cyrillic, Chinese, etc.)
        """
        import re

        # Check if name is not empty
        if not name or not name.strip():
            return False

        # Check length
        if len(name) < 3 or len(name) > 100:
            return False

        # Prevent path traversal
        if ".." in name or "/" in name or "\\" in name:
            return False

        # Prevent shell metacharacters and dangerous chars
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
        if any(char in name for char in dangerous_chars):
            return False

        return True
