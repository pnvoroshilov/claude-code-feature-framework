"""Service for MCP config file system operations"""

import os
import json
import shutil
import logging
import aiofiles
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPConfigFileService:
    """Service for MCP config file system operations"""

    def __init__(self):
        # Path to framework-assets/mcp-configs/
        self.framework_mcp_configs_dir = self._get_framework_mcp_configs_dir()

    async def merge_mcp_config_to_project(
        self,
        project_path: str,
        mcp_config_name: str,
        config_data: Dict[str, Any]
    ) -> bool:
        """
        Merge MCP config into project's .mcp.json file

        Args:
            project_path: Path to project root
            mcp_config_name: Name of the MCP config (used as key in mcpServers)
            config_data: MCP server configuration to merge

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"merge_mcp_config_to_project called: project_path={project_path}, mcp_config_name={mcp_config_name}")

            # Path to project's .mcp.json
            mcp_file_path = os.path.join(project_path, ".mcp.json")

            # Create backup if file exists
            if os.path.exists(mcp_file_path):
                backup_path = f"{mcp_file_path}.backup"
                shutil.copy2(mcp_file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

            # Read existing .mcp.json or create new one
            if os.path.exists(mcp_file_path):
                async with aiofiles.open(mcp_file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    mcp_data = json.loads(content) if content.strip() else {}
            else:
                mcp_data = {}

            # Ensure mcpServers key exists
            if "mcpServers" not in mcp_data:
                mcp_data["mcpServers"] = {}

            # Merge the new config
            mcp_data["mcpServers"][mcp_config_name] = config_data

            # Write back to file with pretty formatting
            async with aiofiles.open(mcp_file_path, 'w', encoding='utf-8') as f:
                json_content = json.dumps(mcp_data, indent=2, ensure_ascii=False)
                await f.write(json_content)

            logger.info(f"Merged MCP config '{mcp_config_name}' to {mcp_file_path}")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in .mcp.json: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Failed to merge MCP config: {e}", exc_info=True)
            return False

    async def remove_mcp_config_from_project(
        self,
        project_path: str,
        mcp_config_name: str
    ) -> bool:
        """
        Remove MCP config from project's .mcp.json file

        Args:
            project_path: Path to project root
            mcp_config_name: Name of the MCP config to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            mcp_file_path = os.path.join(project_path, ".mcp.json")

            # Check if file exists
            if not os.path.exists(mcp_file_path):
                logger.warning(f".mcp.json not found: {mcp_file_path}")
                return True  # Consider it success if file doesn't exist

            # Create backup
            backup_path = f"{mcp_file_path}.backup"
            shutil.copy2(mcp_file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")

            # Read existing .mcp.json
            async with aiofiles.open(mcp_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                mcp_data = json.loads(content) if content.strip() else {}

            # Remove the config
            if "mcpServers" in mcp_data and mcp_config_name in mcp_data["mcpServers"]:
                del mcp_data["mcpServers"][mcp_config_name]
                logger.info(f"Removed MCP config '{mcp_config_name}' from mcpServers")
            else:
                logger.warning(f"MCP config '{mcp_config_name}' not found in .mcp.json")
                return True  # Consider it success if already removed

            # Write back to file
            async with aiofiles.open(mcp_file_path, 'w', encoding='utf-8') as f:
                json_content = json.dumps(mcp_data, indent=2, ensure_ascii=False)
                await f.write(json_content)

            logger.info(f"Removed MCP config '{mcp_config_name}' from {mcp_file_path}")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in .mcp.json: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Failed to remove MCP config: {e}", exc_info=True)
            return False

    async def read_project_mcp_config(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Read project's .mcp.json file"""
        try:
            mcp_file_path = os.path.join(project_path, ".mcp.json")

            if not os.path.exists(mcp_file_path):
                logger.info(f".mcp.json not found: {mcp_file_path}")
                return {"mcpServers": {}}

            async with aiofiles.open(mcp_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                mcp_data = json.loads(content) if content.strip() else {"mcpServers": {}}

            return mcp_data

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in .mcp.json: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Failed to read .mcp.json: {e}", exc_info=True)
            return None

    async def mcp_config_exists_in_project(self, project_path: str, mcp_config_name: str) -> bool:
        """Check if MCP config exists in project's .mcp.json"""
        try:
            mcp_data = await self.read_project_mcp_config(project_path)
            if mcp_data is None:
                return False

            return mcp_config_name in mcp_data.get("mcpServers", {})

        except Exception as e:
            logger.error(f"Failed to check MCP config existence: {e}", exc_info=True)
            return False

    async def read_default_mcp_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Read default MCP config from framework-assets"""
        try:
            # Path to framework-assets/mcp-configs/.mcp.json
            default_file_path = os.path.join(self.framework_mcp_configs_dir, ".mcp.json")

            if not os.path.exists(default_file_path):
                logger.warning(f"Default MCP configs file not found: {default_file_path}")
                return None

            async with aiofiles.open(default_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                mcp_data = json.loads(content)

            # Extract specific config
            if "mcpServers" in mcp_data and config_name in mcp_data["mcpServers"]:
                return mcp_data["mcpServers"][config_name]
            else:
                logger.warning(f"MCP config '{config_name}' not found in default configs")
                return None

        except Exception as e:
            logger.error(f"Failed to read default MCP config: {e}", exc_info=True)
            return None

    def _get_framework_mcp_configs_dir(self) -> str:
        """Get path to framework-assets/mcp-configs/"""
        # Navigate up from services directory to framework root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # backend/app/services -> backend -> claudetask -> project_root
        project_root = Path(current_dir).parent.parent.parent.parent
        framework_mcp_configs_dir = os.path.join(project_root, "framework-assets", "mcp-configs")

        if not os.path.exists(framework_mcp_configs_dir):
            logger.warning(f"Framework MCP configs directory not found: {framework_mcp_configs_dir}")

        return framework_mcp_configs_dir

    def validate_mcp_config_json(self, config_data: Dict[str, Any]) -> bool:
        """
        Validate MCP config JSON structure

        Args:
            config_data: MCP server configuration to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - ensure it's a dict and has required fields
            if not isinstance(config_data, dict):
                logger.error("MCP config must be a dictionary")
                return False

            # Check for common MCP config fields
            # (command, args, env are typical fields)
            if "command" not in config_data:
                logger.error("MCP config must contain 'command' field")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate MCP config: {e}", exc_info=True)
            return False
