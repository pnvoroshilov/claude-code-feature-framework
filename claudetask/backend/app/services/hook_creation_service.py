"""Service for creating hooks via Claude Code CLI"""

import os
import asyncio
import logging
from typing import Dict, Any
from .claude_terminal_service import ClaudeTerminalSession

logger = logging.getLogger(__name__)


class HookCreationService:
    """Service for creating hooks using Claude Code CLI's /create-hook command"""

    async def create_hook_via_claude_cli(
        self,
        project_path: str,
        hook_name: str,
        hook_description: str,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Create a hook using Claude Code CLI's /create-hook command

        Process:
        1. Start Claude terminal session in project directory
        2. Send command: /create-hook "Name" "Description"
        3. Claude Code executes /create-hook slash command
        4. Command delegates to hooks-creator agent
        5. Wait for hook to be created (NO TIMEOUT - waits indefinitely)
        6. Stop session when hook is created
        7. Verify hook was created and read its configuration

        Args:
            project_path: Path to project root
            hook_name: Name of the hook to create
            hook_description: Description of the hook
            timeout: Timeout in seconds (None = no timeout, waits indefinitely)

        Returns:
            {
                "success": bool,
                "hook_path": str,      # Path to created hook file
                "hook_config": dict,   # Hook configuration JSON
                "error": str           # Error message if failed
            }
        """
        session = None

        try:
            # Create session ID
            session_id = f"hook-creation-{hook_name}-{asyncio.get_event_loop().time()}"

            # Start Claude terminal session
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=0,  # No task associated
                working_dir=project_path,
                skip_permissions=True  # Use dangerous mode for hook creation (directory already trusted)
            )

            if not await session.start():
                return {
                    "success": False,
                    "error": "Failed to start Claude terminal session"
                }

            logger.info(f"Started Claude session {session_id} for hook creation")

            # Claude already initialized in session.start() with 5 second delay
            # No additional wait needed here

            # Handle MCP server selection prompt (if appears)
            # Send Enter to confirm default selection and proceed
            await session.send_key("enter")
            logger.info("Sent Enter key to handle MCP prompt")

            # Wait a bit for prompt to process
            await asyncio.sleep(1)

            # Send /create-hook command with arguments
            # Format: /create-hook "Hook Name" "Hook Description"
            command = f'/create-hook "{hook_name}" "{hook_description}"'

            await session.send_input(command)
            logger.info(f"Sent command: {command}")

            # Ensure command is executed by sending Enter key
            await asyncio.sleep(0.5)
            await session.send_key("enter")
            logger.info("Sent Enter to execute command")

            # Session will run until agent calls MCP complete_hook_creation_session
            # or timeout is reached (30 minutes)
            logger.info(f"Hook creation session {session_id} started")
            logger.info(f"Session will be stopped by agent via MCP or after 30 minute timeout")

            # Wait for timeout (30 minutes = 1800 seconds)
            # Agent should call mcp__claudetask__complete_hook_creation_session before timeout
            timeout = 1800
            await asyncio.sleep(timeout)

            # If we reach here, timeout occurred - stop session
            logger.warning(f"Hook creation session {session_id} timed out after {timeout}s")
            await session.stop()

            # Try to find created hook file
            hook_file_name = self._generate_hook_file_name(hook_name)

            # Check in framework-assets/custom-hooks/ first
            custom_hooks_dir = os.path.join(project_path, "..", "..", "framework-assets", "custom-hooks")
            custom_hook_path = os.path.join(custom_hooks_dir, hook_file_name)

            # Also check in project's .claude directory
            project_hook_path = os.path.join(project_path, ".claude", "hooks", hook_file_name)

            # Determine which path to use
            hook_path = None
            hook_config = None

            if os.path.exists(custom_hook_path):
                hook_path = custom_hook_path
            elif os.path.exists(project_hook_path):
                hook_path = project_hook_path

            if hook_path:
                import json
                with open(hook_path, 'r', encoding='utf-8') as f:
                    hook_data = json.load(f)
                    hook_config = hook_data.get("hook_config", {})

            return {
                "success": hook_path is not None,
                "hook_path": hook_path,
                "hook_config": hook_config,
                "timeout": True
            }

        except Exception as e:
            logger.error(f"Error creating hook via CLI: {e}", exc_info=True)

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

    def _generate_hook_file_name(self, hook_name: str) -> str:
        """Generate file name from hook name"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        file_name = hook_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.json"

    def sanitize_hook_input(self, user_input: str) -> str:
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

    def validate_hook_name(self, name: str) -> bool:
        """
        Validate hook name to prevent:
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
