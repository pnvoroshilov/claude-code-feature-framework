"""Service for hook file system operations"""

import os
import json
import logging
import aiofiles
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class HookFileService:
    """Service for hook file system operations"""

    def __init__(self):
        # Path to framework-assets/claude-hooks/
        self.framework_hooks_dir = self._get_framework_hooks_dir()

    def _convert_to_absolute_path(self, command: str, project_path: str) -> str:
        """
        Convert relative hook script path to absolute path.

        This is critical for worktree support - relative paths like .claude/hooks/script.sh
        won't work when Claude Code runs from a worktree directory.

        Args:
            command: The command string (may be relative or absolute path)
            project_path: The project root path

        Returns:
            Absolute path if command was relative .claude/hooks/ path, otherwise unchanged.
            Paths with spaces are wrapped in quotes for shell compatibility.
        """
        if command.startswith(".claude/hooks/"):
            # Convert relative path to absolute
            absolute_path = os.path.join(project_path, command)
            logger.debug(f"Converted relative hook path '{command}' to absolute '{absolute_path}'")

            # Wrap in quotes if path contains spaces (for shell compatibility)
            if ' ' in absolute_path:
                absolute_path = f'"{absolute_path}"'
                logger.debug(f"Added quotes for path with spaces: {absolute_path}")

            return absolute_path

        # For existing absolute paths, check if they need quotes
        if command.startswith("/") and ' ' in command and not command.startswith('"'):
            return f'"{command}"'

        return command

    def _convert_hook_config_to_absolute(self, hook_config: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """
        Convert all relative paths in hook config to absolute paths.

        Args:
            hook_config: Hook configuration with potentially relative paths
            project_path: The project root path

        Returns:
            Hook configuration with absolute paths
        """
        import copy
        converted_config = copy.deepcopy(hook_config)

        for event_type, event_hooks in converted_config.items():
            for hook_matcher in event_hooks:
                if "hooks" in hook_matcher:
                    for hook in hook_matcher["hooks"]:
                        if "command" in hook:
                            hook["command"] = self._convert_to_absolute_path(hook["command"], project_path)

        return converted_config

    async def apply_hook_to_settings(
        self,
        project_path: str,
        hook_name: str,
        hook_config: Dict[str, Any]
    ) -> bool:
        """
        Apply hook configuration to .claude/settings.json

        Args:
            project_path: Path to project root
            hook_name: Name of the hook (for tracking)
            hook_config: Hook configuration JSON (events, matchers, commands)

        Returns:
            True if successful, False otherwise

        Note: Hooks are stored in settings.json, NOT as separate files
        Note: Relative paths (.claude/hooks/...) are converted to absolute paths
              to support worktree environments
        """
        try:
            settings_path = os.path.join(project_path, ".claude", "settings.json")

            # Ensure .claude directory exists
            claude_dir = os.path.join(project_path, ".claude")
            os.makedirs(claude_dir, exist_ok=True)

            # Read existing settings or create new
            settings = {}
            if os.path.exists(settings_path):
                async with aiofiles.open(settings_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        settings = json.loads(content)

            # Initialize hooks section if doesn't exist
            if "hooks" not in settings:
                settings["hooks"] = {}

            # Convert relative paths to absolute paths for worktree support
            converted_hook_config = self._convert_hook_config_to_absolute(hook_config, project_path)

            # Merge hook configuration into settings
            for event_type, event_hooks in converted_hook_config.items():
                # Initialize event type if doesn't exist
                if event_type not in settings["hooks"]:
                    settings["hooks"][event_type] = []

                # Add hooks to event type (merge, don't replace)
                for hook_matcher in event_hooks:
                    # Check if this exact hook configuration already exists to avoid duplicates
                    # Need to check the full hook structure, not just matcher
                    # because multiple hooks can have the same matcher (e.g., "Bash")
                    hook_exists = False
                    for existing_hook in settings["hooks"][event_type]:
                        # Compare matcher AND the command inside hooks
                        if existing_hook.get("matcher") == hook_matcher.get("matcher"):
                            # Check if commands are the same
                            existing_commands = [h.get("command") for h in existing_hook.get("hooks", [])]
                            new_commands = [h.get("command") for h in hook_matcher.get("hooks", [])]
                            if existing_commands == new_commands:
                                hook_exists = True
                                break

                    if not hook_exists:
                        settings["hooks"][event_type].append(hook_matcher)

            # Write settings back to file
            async with aiofiles.open(settings_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(settings, indent=2))

            logger.info(f"Applied hook '{hook_name}' to settings.json with absolute paths")
            return True

        except Exception as e:
            logger.error(f"Failed to apply hook to settings.json: {e}", exc_info=True)
            return False

    async def remove_hook_from_settings(
        self,
        project_path: str,
        hook_name: str
    ) -> bool:
        """
        Remove hook configuration from .claude/settings.json

        Strategy: We'll remove ALL hooks and let the enable process re-add only active ones.
        This is simpler and more reliable than trying to identify specific hook configs.

        Args:
            project_path: Path to project root
            hook_name: Name of the hook to remove (for logging)

        Returns:
            True if successful, False otherwise
        """
        try:
            settings_path = os.path.join(project_path, ".claude", "settings.json")

            # Read existing settings
            if not os.path.exists(settings_path):
                logger.warning(f"Settings file not found: {settings_path}")
                return True  # Consider success if file doesn't exist

            async with aiofiles.open(settings_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                if not content.strip():
                    return True
                settings = json.loads(content)

            # Check if hooks section exists
            if "hooks" not in settings:
                return True  # Nothing to remove

            # Clear the entire hooks section
            # The enable process will re-add only the hooks that should be active
            settings["hooks"] = {}

            # Write settings back to file
            async with aiofiles.open(settings_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(settings, indent=2))

            logger.info(f"Cleared hooks from settings.json (hook '{hook_name}' removal)")
            return True

        except Exception as e:
            logger.error(f"Failed to remove hook from settings.json: {e}", exc_info=True)
            return False

    async def read_hook_file(
        self,
        hook_file_name: str,
        source_type: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Read hook configuration from file

        Args:
            hook_file_name: Name of hook file (e.g., "file-protection.json")
            source_type: "default" (from framework-assets) or "custom" (from project)

        Returns:
            Hook configuration dict or None if failed
        """
        try:
            if source_type == "default":
                file_path = os.path.join(self.framework_hooks_dir, hook_file_name)
            else:
                # Custom hooks could be stored elsewhere if needed
                logger.warning(f"Custom hook file reading not yet implemented")
                return None

            if not os.path.exists(file_path):
                logger.error(f"Hook file not found: {file_path}")
                return None

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                hook_data = json.loads(content)

            return hook_data

        except Exception as e:
            logger.error(f"Failed to read hook file: {e}", exc_info=True)
            return None

    async def write_hook_file(
        self,
        hook_file_name: str,
        hook_data: Dict[str, Any]
    ) -> bool:
        """
        Write hook configuration to file (for custom hooks)

        Args:
            hook_file_name: Name of hook file
            hook_data: Hook configuration data

        Returns:
            True if successful, False otherwise

        Note: This is for storing custom hook definitions as JSON files
        """
        try:
            # Custom hooks could be stored in a custom location
            # For now, we'll store them in framework-assets/custom-hooks/
            custom_hooks_dir = self.framework_hooks_dir.replace("claude-hooks", "custom-hooks")
            os.makedirs(custom_hooks_dir, exist_ok=True)

            file_path = os.path.join(custom_hooks_dir, hook_file_name)

            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(hook_data, indent=2))

            logger.info(f"Wrote hook file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to write hook file: {e}", exc_info=True)
            return False

    async def delete_hook_file(
        self,
        hook_file_name: str
    ) -> bool:
        """
        Delete custom hook file

        Args:
            hook_file_name: Name of hook file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            custom_hooks_dir = self.framework_hooks_dir.replace("claude-hooks", "custom-hooks")
            file_path = os.path.join(custom_hooks_dir, hook_file_name)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted hook file: {file_path}")
            else:
                logger.warning(f"Hook file not found (already deleted?): {file_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete hook file: {e}", exc_info=True)
            return False

    async def read_settings_hooks(self, project_path: str) -> Optional[Dict[str, Any]]:
        """
        Read current hooks configuration from .claude/settings.json

        Args:
            project_path: Path to project root

        Returns:
            Hooks configuration dict or None if not found
        """
        try:
            settings_path = os.path.join(project_path, ".claude", "settings.json")

            if not os.path.exists(settings_path):
                return None

            async with aiofiles.open(settings_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                if not content.strip():
                    return None
                settings = json.loads(content)

            return settings.get("hooks", {})

        except Exception as e:
            logger.error(f"Failed to read settings hooks: {e}", exc_info=True)
            return None

    async def apply_hooks_to_settings(
        self,
        project_path: str,
        hooks: Dict[str, Any]
    ) -> bool:
        """
        Apply multiple hooks to settings.json at once

        Args:
            project_path: Path to project root
            hooks: Complete hooks configuration to set

        Returns:
            True if successful, False otherwise

        Note: Relative paths (.claude/hooks/...) are converted to absolute paths
              to support worktree environments
        """
        try:
            settings_path = os.path.join(project_path, ".claude", "settings.json")

            # Ensure .claude directory exists
            claude_dir = os.path.join(project_path, ".claude")
            os.makedirs(claude_dir, exist_ok=True)

            # Read existing settings or create new
            settings = {}
            if os.path.exists(settings_path):
                async with aiofiles.open(settings_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        settings = json.loads(content)

            # Convert relative paths to absolute paths for worktree support
            converted_hooks = self._convert_hook_config_to_absolute(hooks, project_path)

            # Replace hooks section entirely
            settings["hooks"] = converted_hooks

            # Write settings back to file
            async with aiofiles.open(settings_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(settings, indent=2))

            logger.info(f"Applied hooks configuration to settings.json with absolute paths")
            return True

        except Exception as e:
            logger.error(f"Failed to apply hooks to settings.json: {e}", exc_info=True)
            return False

    async def copy_hook_script(
        self,
        project_path: str,
        script_file_name: str
    ) -> bool:
        """
        Copy hook script file from framework to project .claude/hooks/

        Args:
            project_path: Path to project root
            script_file_name: Name of script file (e.g., "post-push-docs.sh")

        Returns:
            True if successful, False otherwise
        """
        try:
            # Source: framework-assets/claude-hooks/SCRIPT_FILE
            source_path = os.path.join(self.framework_hooks_dir, script_file_name)

            # Destination: project/.claude/hooks/SCRIPT_FILE
            hooks_dir = os.path.join(project_path, ".claude", "hooks")
            os.makedirs(hooks_dir, exist_ok=True)
            dest_path = os.path.join(hooks_dir, script_file_name)

            # Check if source exists
            if not os.path.exists(source_path):
                logger.error(f"Hook script not found in framework: {source_path}")
                return False

            # Copy file
            async with aiofiles.open(source_path, 'r', encoding='utf-8') as source_file:
                content = await source_file.read()

            async with aiofiles.open(dest_path, 'w', encoding='utf-8') as dest_file:
                await dest_file.write(content)

            # Make script executable (important for shell scripts)
            os.chmod(dest_path, 0o755)

            logger.info(f"Copied hook script {script_file_name} to {dest_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to copy hook script: {e}", exc_info=True)
            return False

    def _get_framework_hooks_dir(self) -> str:
        """Get path to framework-assets/claude-hooks/"""
        # Navigate up from services directory to framework root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # backend/app/services -> backend -> claudetask -> project_root
        project_root = Path(current_dir).parent.parent.parent.parent
        framework_hooks_dir = os.path.join(project_root, "framework-assets", "claude-hooks")

        if not os.path.exists(framework_hooks_dir):
            logger.warning(f"Framework hooks directory not found: {framework_hooks_dir}")

        return framework_hooks_dir

    def validate_hook_config(self, hook_config: Dict[str, Any]) -> bool:
        """
        Validate hook configuration structure

        Args:
            hook_config: Hook configuration to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if hook_config has required structure
            if not isinstance(hook_config, dict):
                return False

            # Each key should be an event type (e.g., "PreToolUse", "PostToolUse")
            for event_type, event_hooks in hook_config.items():
                if not isinstance(event_hooks, list):
                    return False

                for hook_matcher in event_hooks:
                    if not isinstance(hook_matcher, dict):
                        return False

                    # Should have "matcher" and "hooks" keys
                    if "matcher" not in hook_matcher or "hooks" not in hook_matcher:
                        return False

                    if not isinstance(hook_matcher["hooks"], list):
                        return False

                    # Each hook should have "type" and "command" keys
                    for hook in hook_matcher["hooks"]:
                        if not isinstance(hook, dict):
                            return False
                        if "type" not in hook or "command" not in hook:
                            return False

            return True

        except Exception as e:
            logger.error(f"Hook config validation error: {e}")
            return False
