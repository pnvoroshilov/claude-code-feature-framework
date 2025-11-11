"""Service for editing agents and skills via Claude CLI"""

import os
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EditorService:
    """Service for editing agents and skills using Claude CLI commands"""

    def __init__(self):
        pass

    async def edit_agent_via_claude(
        self,
        project_path: str,
        agent_name: str,
        edit_instructions: str
    ) -> Dict[str, Any]:
        """
        Edit an agent using Claude CLI /edit-agent command

        Args:
            project_path: Path to the project
            agent_name: Name of the agent to edit
            edit_instructions: Instructions for what to change

        Returns:
            Dict with success status and details
        """
        try:
            # Execute /edit-agent command via Claude CLI
            command = f'/edit-agent "{agent_name}" "{edit_instructions}"'

            result = await self._execute_claude_command(
                project_path=project_path,
                command=command,
                timeout=120  # 2 minutes timeout
            )

            return {
                "success": True,
                "agent_name": agent_name,
                "message": f"Agent '{agent_name}' edited successfully",
                "output": result.get("output", "")
            }

        except Exception as e:
            logger.error(f"Failed to edit agent '{agent_name}': {e}", exc_info=True)
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "message": f"Failed to edit agent: {str(e)}"
            }

    async def edit_skill_via_claude(
        self,
        project_path: str,
        skill_name: str,
        edit_instructions: str
    ) -> Dict[str, Any]:
        """
        Edit a skill using Claude CLI /edit-skill command

        Args:
            project_path: Path to the project
            skill_name: Name of the skill to edit
            edit_instructions: Instructions for what to change

        Returns:
            Dict with success status and details
        """
        try:
            # Execute /edit-skill command via Claude CLI
            command = f'/edit-skill "{skill_name}" "{edit_instructions}"'

            result = await self._execute_claude_command(
                project_path=project_path,
                command=command,
                timeout=120  # 2 minutes timeout
            )

            return {
                "success": True,
                "skill_name": skill_name,
                "message": f"Skill '{skill_name}' edited successfully",
                "output": result.get("output", "")
            }

        except Exception as e:
            logger.error(f"Failed to edit skill '{skill_name}': {e}", exc_info=True)
            return {
                "success": False,
                "skill_name": skill_name,
                "error": str(e),
                "message": f"Failed to edit skill: {str(e)}"
            }

    async def _execute_claude_command(
        self,
        project_path: str,
        command: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a Claude CLI command

        Args:
            project_path: Path to the project directory
            command: Claude CLI command to execute
            timeout: Command timeout in seconds

        Returns:
            Dict with execution result
        """
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)

            # Execute Claude CLI command
            # Note: This is a simplified version. In production, you would need to:
            # 1. Start a Claude terminal session
            # 2. Send the command
            # 3. Wait for completion
            # 4. Parse the output

            # For now, we'll use a subprocess approach
            # This assumes Claude CLI is available as a command
            process = await asyncio.create_subprocess_shell(
                f'echo "{command}" | claude',  # Simplified - actual implementation would be more complex
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                os.chdir(original_dir)

                if process.returncode != 0:
                    error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                    raise RuntimeError(f"Command failed with return code {process.returncode}: {error_msg}")

                output = stdout.decode('utf-8') if stdout else ""

                return {
                    "success": True,
                    "output": output,
                    "returncode": process.returncode
                }

            except asyncio.TimeoutError:
                process.kill()
                os.chdir(original_dir)
                raise RuntimeError(f"Command timed out after {timeout} seconds")

        except Exception as e:
            if 'original_dir' in locals():
                os.chdir(original_dir)
            logger.error(f"Failed to execute Claude command: {e}", exc_info=True)
            raise

    def validate_agent_name(self, agent_name: str) -> bool:
        """Validate agent name format"""
        if not agent_name:
            return False
        # Allow letters, numbers, hyphens, and spaces
        import re
        return bool(re.match(r'^[a-zA-Z0-9\s\-]+$', agent_name))

    def validate_skill_name(self, skill_name: str) -> bool:
        """Validate skill name format"""
        if not skill_name:
            return False
        # Allow letters, numbers, hyphens, and spaces
        import re
        return bool(re.match(r'^[a-zA-Z0-9\s\-]+$', skill_name))

    def sanitize_instructions(self, instructions: str) -> str:
        """Sanitize edit instructions to prevent command injection"""
        if not instructions:
            return ""

        # Remove any shell-dangerous characters
        # Keep only alphanumeric, spaces, and safe punctuation
        import re
        sanitized = re.sub(r'[`$\\;|&<>]', '', instructions)

        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    async def get_agent_content(self, project_path: str, agent_name: str) -> str:
        """
        Read agent file content

        Args:
            project_path: Path to the project
            agent_name: Name of the agent

        Returns:
            Agent file content as string
        """
        try:
            # Convert agent name to kebab-case for file search
            import re
            file_name = re.sub(r'[^\w\s-]', '', agent_name.lower())
            file_name = re.sub(r'[\s_]+', '-', file_name)

            agent_file = Path(project_path) / ".claude" / "agents" / f"{file_name}.md"

            if not agent_file.exists():
                raise FileNotFoundError(f"Agent file not found: {agent_file}")

            with open(agent_file, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Failed to read agent content: {e}", exc_info=True)
            raise

    async def get_skill_content(self, project_path: str, skill_name: str) -> str:
        """
        Read skill file content

        Args:
            project_path: Path to the project
            skill_name: Name of the skill

        Returns:
            Skill file content as string
        """
        try:
            # Convert skill name to kebab-case for file search
            import re
            file_name = re.sub(r'[^\w\s-]', '', skill_name.lower())
            file_name = re.sub(r'[\s_]+', '-', file_name)

            skill_file = Path(project_path) / ".claude" / "skills" / f"{file_name}.md"

            if not skill_file.exists():
                raise FileNotFoundError(f"Skill file not found: {skill_file}")

            with open(skill_file, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            logger.error(f"Failed to read skill content: {e}", exc_info=True)
            raise

    async def save_agent_content(
        self,
        project_path: str,
        agent_name: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Save agent file content (manual edit)

        Args:
            project_path: Path to the project
            agent_name: Name of the agent
            content: New content to save

        Returns:
            Dict with success status
        """
        try:
            # Convert agent name to kebab-case for file search
            import re
            file_name = re.sub(r'[^\w\s-]', '', agent_name.lower())
            file_name = re.sub(r'[\s_]+', '-', file_name)

            agent_file = Path(project_path) / ".claude" / "agents" / f"{file_name}.md"

            if not agent_file.exists():
                raise FileNotFoundError(f"Agent file not found: {agent_file}")

            # Create backup
            backup_file = agent_file.with_suffix('.md.backup')
            with open(agent_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)

            # Save new content
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved agent '{agent_name}' to {agent_file}")

            return {
                "success": True,
                "agent_name": agent_name,
                "file_path": str(agent_file),
                "message": f"Agent '{agent_name}' saved successfully"
            }

        except Exception as e:
            logger.error(f"Failed to save agent content: {e}", exc_info=True)
            return {
                "success": False,
                "agent_name": agent_name,
                "error": str(e),
                "message": f"Failed to save agent: {str(e)}"
            }

    async def save_skill_content(
        self,
        project_path: str,
        skill_name: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Save skill file content (manual edit)

        Args:
            project_path: Path to the project
            skill_name: Name of the skill
            content: New content to save

        Returns:
            Dict with success status
        """
        try:
            # Convert skill name to kebab-case for file search
            import re
            file_name = re.sub(r'[^\w\s-]', '', skill_name.lower())
            file_name = re.sub(r'[\s_]+', '-', file_name)

            skill_file = Path(project_path) / ".claude" / "skills" / f"{file_name}.md"

            if not skill_file.exists():
                raise FileNotFoundError(f"Skill file not found: {skill_file}")

            # Create backup
            backup_file = skill_file.with_suffix('.md.backup')
            with open(skill_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)

            # Save new content
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved skill '{skill_name}' to {skill_file}")

            return {
                "success": True,
                "skill_name": skill_name,
                "file_path": str(skill_file),
                "message": f"Skill '{skill_name}' saved successfully"
            }

        except Exception as e:
            logger.error(f"Failed to save skill content: {e}", exc_info=True)
            return {
                "success": False,
                "skill_name": skill_name,
                "error": str(e),
                "message": f"Failed to save skill: {str(e)}"
            }
