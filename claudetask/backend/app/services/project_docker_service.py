"""Docker version of project structure creation"""

import os
import subprocess
from typing import List
from datetime import datetime
import json
from .claude_config_generator import generate_claude_md, get_default_agents
from .docker_file_service import DockerFileService

# Embedded wrapper script content for portability
MCP_WRAPPER_SCRIPT = '''#!/bin/bash
# ClaudeTask MCP Docker Wrapper
# This script allows Claude Code to communicate with the MCP server running in Docker

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments - they come from .mcp.json configuration
PROJECT_ID=""
PROJECT_PATH=""
SERVER_URL="http://localhost:3333"

while [[ $# -gt 0 ]]; do
  case $1 in
    --project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    --project-path)
      PROJECT_PATH="$2"
      shift 2
      ;;
    --server)
      SERVER_URL="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Find docker-compose.yml by searching up the directory tree from the script location
COMPOSE_FILE=""
SEARCH_DIR="$SCRIPT_DIR"
while [[ "$SEARCH_DIR" != "/" ]]; do
    if [[ -f "$SEARCH_DIR/docker-compose.yml" ]]; then
        COMPOSE_FILE="$SEARCH_DIR/docker-compose.yml"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [[ -z "$COMPOSE_FILE" ]]; then
    echo "Error: Could not find docker-compose.yml" >&2
    exit 1
fi

# Ensure the MCP server image is built
docker-compose -f "$COMPOSE_FILE" build mcp_server 2>/dev/null

# Run the MCP server in Docker with stdio communication
exec docker run --rm -i \\
  --network claudecodefeatureframework_claudetask-network \\
  -v "$PROJECT_PATH:/project:rw" \\
  -v /var/run/docker.sock:/var/run/docker.sock \\
  -e PROJECT_ID="$PROJECT_ID" \\
  -e PROJECT_PATH="/project" \\
  -e SERVER_URL="http://backend:3333" \\
  claudetask-mcp:latest \\
  --project-id "$PROJECT_ID" \\
  --project-path "/project" \\
  --server "http://backend:3333"
'''


async def create_project_structure_docker(
    project_path: str,
    project_id: str,
    project_name: str,
    tech_stack: List[str]
) -> List[str]:
    """Create ClaudeTask structure in the project using Docker"""
    files_created = []
    dfs = DockerFileService()
    
    # Create CLAUDE.md in project root
    claude_md_content = generate_claude_md(project_name, project_path, tech_stack)
    claude_md_path = os.path.join(project_path, "CLAUDE.md")
    
    if dfs.write_file_to_host(claude_md_path, claude_md_content):
        files_created.append("CLAUDE.md")
    
    # Create .claude directory
    claude_dir = os.path.join(project_path, ".claude")
    dfs.create_directory_on_host(claude_dir)
    
    # Create agents directory
    agents_dir = os.path.join(claude_dir, "agents")
    dfs.create_directory_on_host(agents_dir)
    
    # Copy agent files from framework-assets
    framework_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    ))
    agents_source_dir = os.path.join(framework_path, "framework-assets", "claude-agents")

    if os.path.exists(agents_source_dir):
        for agent_file in os.listdir(agents_source_dir):
            if agent_file.endswith(".md"):
                source_file = os.path.join(agents_source_dir, agent_file)
                dest_file = os.path.join(agents_dir, agent_file)
                with open(source_file, "r") as src:
                    content = src.read()
                    if dfs.write_file_to_host(dest_file, content):
                        files_created.append(f".claude/agents/{agent_file}")
    else:
        # Fallback to default agents if framework-assets not found
        for agent_config in get_default_agents():
            agent_path = os.path.join(agents_dir, f"{agent_config['name']}.md")
            if dfs.write_file_to_host(agent_path, agent_config['config']):
                files_created.append(f".claude/agents/{agent_config['name']}.md")

    # Create skills directory
    skills_dir = os.path.join(claude_dir, "skills")
    dfs.create_directory_on_host(skills_dir)

    # Create commands directory
    commands_dir = os.path.join(claude_dir, "commands")
    dfs.create_directory_on_host(commands_dir)

    # Copy command files from framework-assets
    commands_source_dir = os.path.join(framework_path, "framework-assets", "claude-commands")
    if os.path.exists(commands_source_dir):
        for command_file in os.listdir(commands_source_dir):
            if command_file.endswith(".md") and command_file != "README.md":
                source_file = os.path.join(commands_source_dir, command_file)
                dest_file = os.path.join(commands_dir, command_file)
                with open(source_file, "r") as src:
                    content = src.read()
                    if dfs.write_file_to_host(dest_file, content):
                        files_created.append(f".claude/commands/{command_file}")

    # Create hooks directory
    hooks_dir = os.path.join(claude_dir, "hooks")
    dfs.create_directory_on_host(hooks_dir)

    # Copy hook SCRIPTS from framework-assets (but don't enable hooks yet)
    hooks_source_dir = os.path.join(framework_path, "framework-assets", "claude-hooks")

    if os.path.exists(hooks_source_dir):
        for hook_file in os.listdir(hooks_source_dir):
            # Only copy shell scripts - hooks will be enabled via UI
            if hook_file.endswith(".sh"):
                source_file = os.path.join(hooks_source_dir, hook_file)
                dest_file = os.path.join(hooks_dir, hook_file)
                with open(source_file, "r") as src:
                    content = src.read()
                    if dfs.write_file_to_host(dest_file, content):
                        # Make script executable using Docker
                        import subprocess
                        try:
                            subprocess.run(
                                ["docker", "run", "--rm", "-v", f"{project_path}:{project_path}",
                                 "alpine", "chmod", "755", dest_file],
                                check=True,
                                capture_output=True
                            )
                        except Exception as e:
                            print(f"Failed to make {hook_file} executable: {e}")
                        files_created.append(f".claude/hooks/{hook_file}")

    # Create empty .claude/settings.json (hooks will be added when user enables them)
    settings_file = os.path.join(claude_dir, "settings.json")
    settings_data = {"hooks": {}}  # Empty hooks - user will enable via UI

    if dfs.write_file_to_host(settings_file, json.dumps(settings_data, indent=2)):
        files_created.append(".claude/settings.json")

        # Create .claude/settings.local.json for MCP server configuration
        settings_local_file = os.path.join(claude_dir, "settings.local.json")
        settings_local_data = {
            "enabledMcpjsonServers": [
                "playwright",
                "claudetask",
                "serena"
            ],
            "enableAllProjectMcpServers": True
        }
        if dfs.write_file_to_host(settings_local_file, json.dumps(settings_local_data, indent=2)):
            files_created.append(".claude/settings.local.json")

    # Create .claudetask directory
    claudetask_dir = os.path.join(project_path, ".claudetask")
    dfs.create_directory_on_host(claudetask_dir)
    
    # Create project.json
    project_meta = {
        "id": project_id,
        "name": project_name,
        "path": project_path,
        "tech_stack": tech_stack,
        "initialized_at": str(datetime.utcnow())
    }
    project_json_path = os.path.join(claudetask_dir, "project.json")
    if dfs.write_file_to_host(project_json_path, json.dumps(project_meta, indent=2)):
        files_created.append(".claudetask/project.json")
    
    # Create worktrees directory
    worktrees_dir = os.path.join(project_path, "worktrees")
    dfs.create_directory_on_host(worktrees_dir)
    files_created.append("worktrees/")
    
    return files_created


def configure_mcp_docker(project_path: str, project_id: str) -> bool:
    """Configure MCP by creating .mcp.json in project root using local Python server"""
    dfs = DockerFileService()
    
    # Get the absolute path to the MCP server for local development
    mcp_server_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
        "mcp_server"
    ))
    python_executable = os.path.join(mcp_server_dir, "venv", "bin", "python")
    bridge_script = os.path.join(mcp_server_dir, "claudetask_mcp_bridge.py")
    
    mcp_config = {
        "mcpServers": {
            "claudetask": {
                "command": python_executable,
                "args": [
                    bridge_script,
                    "--project-id", project_id,
                    "--project-path", project_path,
                    "--server", "http://localhost:3333"
                ]
            }
        }
    }
    
    mcp_config_path = os.path.join(project_path, ".mcp.json")
    return dfs.write_file_to_host(mcp_config_path, json.dumps(mcp_config, indent=2))