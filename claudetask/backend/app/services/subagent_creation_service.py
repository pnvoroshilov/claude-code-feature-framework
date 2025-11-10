"""Service for creating custom subagents via Claude Code CLI"""

import os
import asyncio
import logging
from typing import Dict, Any
from .claude_terminal_service import ClaudeTerminalSession

logger = logging.getLogger(__name__)


class SubagentCreationService:
    """Service for creating custom subagents using Claude Code CLI's /create-agent command"""

    async def create_subagent_via_claude_cli(
        self,
        project_path: str,
        agent_name: str,
        agent_description: str,
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Create a custom subagent using Claude Code CLI's /create-agent command

        Process:
        1. Start Claude terminal session in project directory
        2. Send command: /create-agent "Name" "Description"
        3. Claude Code executes /create-agent slash command
        4. Command delegates to agent-creator specialist
        5. Wait for agent file to be created (NO TIMEOUT - waits indefinitely)
        6. Stop session when file is created
        7. Verify agent file was created and read its content

        Args:
            project_path: Path to project root
            agent_name: Name of the agent to create
            agent_description: Description of the agent
            timeout: Timeout in seconds (None = no timeout, waits indefinitely)

        Returns:
            {
                "success": bool,
                "agent_path": str,  # Path to created agent file
                "content": str,     # Content of agent file
                "error": str        # Error message if failed
            }
        """
        session = None

        try:
            # Create session ID
            session_id = f"subagent-creation-{agent_name}-{asyncio.get_event_loop().time()}"

            # Start Claude terminal session
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=0,  # No task associated
                working_dir=project_path,
                skip_permissions=True  # Use dangerous mode for agent creation (directory already trusted)
            )

            if not await session.start():
                return {
                    "success": False,
                    "error": "Failed to start Claude terminal session"
                }

            logger.info(f"Started Claude session {session_id} for subagent creation")

            # Claude already initialized in session.start() with 5 second delay
            # No additional wait needed here

            # Handle MCP server selection prompt (if appears)
            # Send Enter to confirm default selection and proceed
            await session.send_key("enter")
            logger.info("Sent Enter key to handle MCP prompt")

            # Wait a bit for prompt to process
            await asyncio.sleep(1)

            # Send /create-agent command with arguments
            # Format: /create-agent "Agent Name" "Agent Description"
            command = f'/create-agent "{agent_name}" "{agent_description}"'

            await session.send_input(command)
            logger.info(f"Sent command: {command}")

            # Ensure command is executed by sending Enter key
            await asyncio.sleep(0.5)
            await session.send_key("enter")
            logger.info("Sent Enter to execute command")

            # Session will run until agent calls MCP complete_agent_creation_session
            # or timeout is reached (30 minutes)
            logger.info(f"Subagent creation session {session_id} started")
            logger.info(f"Session will be stopped by agent via MCP or after 30 minute timeout")

            # Wait for timeout (30 minutes = 1800 seconds)
            # Agent should call completion MCP before timeout
            timeout = 1800
            await asyncio.sleep(timeout)

            # If we reach here, timeout occurred - stop session
            logger.warning(f"Subagent creation session {session_id} timed out after {timeout}s")
            await session.stop()

            # Try to find created agent file
            agent_file_name = self._generate_agent_file_name(agent_name)
            agent_file_path = os.path.join(project_path, ".claude", "agents", agent_file_name)

            # Check if agent was created
            agent_path = None
            content = None
            if os.path.exists(agent_file_path):
                agent_path = agent_file_path
                with open(agent_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            return {
                "success": agent_path is not None,
                "agent_path": agent_path,
                "content": content,
                "timeout": True
            }

        except Exception as e:
            logger.error(f"Error creating subagent via CLI: {e}", exc_info=True)

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

    def _generate_agent_file_name(self, agent_name: str) -> str:
        """Generate file name from agent name (kebab-case)"""
        import re
        # Convert to lowercase, replace spaces with hyphens
        file_name = agent_name.lower().replace(" ", "-")
        # Remove special characters
        file_name = re.sub(r'[^a-z0-9-_]', '', file_name)
        return f"{file_name}.md"

    def sanitize_agent_input(self, user_input: str) -> str:
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

    def validate_agent_name(self, name: str) -> bool:
        """
        Validate agent name to prevent:
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
