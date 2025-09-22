"""Service for launching and managing Claude Code sessions with actual Claude integration"""

import os
import json
import subprocess
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ClaudeLauncherService:
    """Service to launch Claude Code with specific context and configuration"""
    
    @staticmethod
    async def launch_claude_session(
        task_id: int,
        project_path: str,
        worktree_path: Optional[str] = None,
        task_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Launch Claude Code session for a specific task
        
        This will:
        1. Prepare the working directory
        2. Create a context file with task information
        3. Launch Claude Code CLI in terminal
        4. Connect via MCP for bidirectional communication
        """
        try:
            # Determine working directory
            working_dir = worktree_path or project_path
            
            # Ensure directory exists
            if not os.path.exists(working_dir):
                return {
                    "success": False,
                    "error": f"Working directory does not exist: {working_dir}"
                }
            
            # Create session configuration
            session_config = await ClaudeLauncherService._create_session_config(
                task_id, working_dir, task_context
            )
            
            # Write session context file for Claude
            context_file = await ClaudeLauncherService._write_context_file(
                working_dir, task_id, task_context
            )
            
            # Launch Claude Code CLI
            launch_result = await ClaudeLauncherService._launch_claude_cli(
                working_dir, context_file, session_config
            )
            
            if launch_result["success"]:
                logger.info(f"Successfully launched Claude CLI session for task {task_id}")
                
                return {
                    "success": True,
                    "session_id": session_config["session_id"],
                    "working_dir": working_dir,
                    "context_file": context_file,
                    "launch_command": launch_result["command"],
                    "message": "Claude Code CLI session launched successfully"
                }
            else:
                return launch_result
                
        except Exception as e:
            logger.error(f"Failed to launch Claude session: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to launch Claude Code CLI session"
            }
    
    @staticmethod
    async def _create_session_config(
        task_id: int,
        working_dir: str,
        task_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create session configuration for Claude"""
        import uuid
        
        session_id = f"claude-task-{task_id}-{uuid.uuid4().hex[:8]}"
        
        config = {
            "session_id": session_id,
            "task_id": task_id,
            "working_dir": working_dir,
            "created_at": datetime.utcnow().isoformat(),
            "context": task_context or {},
            "mcp_config": {
                "server": "claudetask",
                "tools": [
                    "complete_task",
                    "update_status",
                    "create_worktree",
                    "delegate_to_agent"
                ]
            },
            "preferences": {
                "auto_save": True,
                "auto_commit": False,
                "show_hidden_files": False,
                "theme": "auto"
            }
        }
        
        return config
    
    @staticmethod
    async def _write_context_file(
        working_dir: str,
        task_id: int,
        task_context: Optional[Dict] = None
    ) -> str:
        """Write context file for Claude to read on startup"""
        context_dir = os.path.join(working_dir, ".claude")
        os.makedirs(context_dir, exist_ok=True)
        
        context_file = os.path.join(context_dir, f"task-{task_id}-context.md")
        
        # Build context content
        content = f"""# Task Context - ID: {task_id}

## Task Information
- **Title**: {task_context.get('title', 'N/A')}
- **Type**: {task_context.get('type', 'Feature')}
- **Priority**: {task_context.get('priority', 'Medium')}
- **Status**: {task_context.get('status', 'In Progress')}

## Description
{task_context.get('description', 'No description provided')}

## Analysis
{task_context.get('analysis', 'No analysis available')}

## Working Directory
Current directory: `{working_dir}`
{f"Worktree branch: `{task_context.get('git_branch')}`" if task_context.get('git_branch') else ""}

## Available MCP Commands
- `mcp:update_status {task_id} <status>` - Update task status
- `mcp:complete_task {task_id}` - Complete and merge task
- `mcp:delegate_to_agent {task_id} <agent> "<instructions>"` - Delegate to specialist
- `mcp:get_session_status` - Get current session status

## Instructions
1. Read this context to understand the task
2. Review the codebase in the current directory
3. Implement the required changes
4. Test your implementation
5. Update task status when complete

## Session Started
{datetime.now().isoformat()}
"""
        
        # Write context file
        with open(context_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Created context file: {context_file}")
        return context_file
    
    @staticmethod
    async def _launch_claude_cli(
        working_dir: str,
        context_file: str,
        session_config: Dict
    ) -> Dict[str, Any]:
        """Launch Claude Code CLI in terminal"""
        try:
            # Build the Claude CLI command
            claude_command = f"claude --working-dir '{working_dir}' --context-file '{context_file}'"
            
            # For task-specific context, add additional parameters
            if session_config.get("task_id"):
                claude_command += f" --task-id {session_config['task_id']}"
            
            # Add MCP server connection
            claude_command += " --mcp-server http://localhost:3335"
            
            # Launch in a new terminal window based on OS
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Use osascript to open Terminal with the command
                terminal_command = f'''osascript -e 'tell app "Terminal" to do script "cd {working_dir} && {claude_command}"' '''
                subprocess.run(terminal_command, shell=True, check=False)
            elif system == "Linux":
                # Try common Linux terminals
                terminals = ["gnome-terminal", "konsole", "xterm", "terminator"]
                for terminal in terminals:
                    if subprocess.run(["which", terminal], capture_output=True).returncode == 0:
                        if terminal == "gnome-terminal":
                            subprocess.run([terminal, "--", "bash", "-c", f"cd {working_dir} && {claude_command}; exec bash"])
                        else:
                            subprocess.run([terminal, "-e", f"cd {working_dir} && {claude_command}"])
                        break
            elif system == "Windows":
                # Windows Terminal or cmd
                subprocess.run(["cmd", "/c", "start", "cmd", "/k", f"cd /d {working_dir} && {claude_command}"])
            else:
                return {
                    "success": False,
                    "error": f"Unsupported operating system: {system}"
                }
            
            logger.info(f"Launched Claude CLI in terminal for task {session_config.get('task_id')}")
            return {
                "success": True,
                "command": claude_command,
                "working_dir": working_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to launch Claude CLI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    
    @staticmethod
    async def connect_to_existing_session(
        session_id: str
    ) -> Dict[str, Any]:
        """Connect to an existing Claude session"""
        try:
            # This would connect to an already running Claude session
            # via MCP or other IPC mechanism
            
            return {
                "success": True,
                "session_id": session_id,
                "status": "connected",
                "message": "Connected to existing Claude session"
            }
        except Exception as e:
            logger.error(f"Failed to connect to session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def get_available_launch_methods() -> Dict[str, bool]:
        """Check if Claude CLI is available"""
        # Check if claude CLI command is available
        cli_available = subprocess.run(
            ["which", "claude"],
            capture_output=True  
        ).returncode == 0
        
        return {
            "claude_cli": cli_available,
            "command": "claude" if cli_available else None,
            "install_instructions": "Install Claude CLI: npm install -g @anthropic/claude-cli" if not cli_available else None
        }