"""Service for updating framework files in existing projects"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List


class FrameworkUpdateService:
    """Service to update framework files in existing projects"""
    
    @staticmethod
    async def update_framework(project_path: str, project_id: str) -> Dict:
        """Update framework files in an existing project"""
        
        # Get the framework source path
        framework_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        ))
        
        updated_files = []
        errors = []
        
        try:
            # 1. Update .mcp.json configuration (no need to copy MCP server files to project)
            mcp_config_path = os.path.join(project_path, ".mcp.json")
            
            # Read existing config if exists
            existing_config = {}
            if os.path.exists(mcp_config_path):
                try:
                    with open(mcp_config_path, "r") as f:
                        existing_config = json.load(f)
                except:
                    pass
            
            # Preserve existing servers except claudetask
            preserved_servers = {}
            if "mcpServers" in existing_config:
                for name, config in existing_config["mcpServers"].items():
                    if not name.startswith("claudetask"):
                        preserved_servers[name] = config
            
            # Load MCP template from framework assets and update with project values
            mcp_template_path = os.path.join(framework_path, "framework-assets", "mcp-configs", "mcp-template.json")
            
            # Read template
            try:
                with open(mcp_template_path, "r") as f:
                    template_config = json.load(f)
            except Exception as e:
                print(f"Failed to read MCP template: {e}")
                return {"success": False, "message": f"Failed to read MCP template: {e}"}
            
            # Update template with project-specific values
            mcp_server_dir = os.path.join(framework_path, "claudetask", "mcp_server")
            native_server_script = os.path.join(mcp_server_dir, "native_stdio_server.py")
            venv_python = os.path.join(mcp_server_dir, "venv", "bin", "python")
            
            # Get all MCP servers from template
            template_servers = template_config.get("mcpServers", {})
            
            # Update claudetask config specifically
            if "claudetask" in template_servers:
                claudetask_config = template_servers["claudetask"]
                claudetask_config["command"] = venv_python
                claudetask_config["args"] = [native_server_script]
                # Keep existing env values but update PROJECT_PATH
                claudetask_config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
            
            # Merge: preserved servers + all template servers (including playwright and any others)
            new_config = {
                "mcpServers": {
                    **preserved_servers,  # User's custom servers (non-claudetask)
                    **template_servers    # All servers from template (claudetask, playwright, etc.)
                }
            }
            
            # Write updated config
            with open(mcp_config_path, "w") as f:
                json.dump(new_config, f, indent=2)
            updated_files.append(".mcp.json")
            
            # 2. Update CLAUDE.md with new instructions
            from .claude_config_generator import generate_claude_md
            
            # Detect technologies
            from .project_service import ProjectService
            tech_stack = ProjectService._detect_technologies(project_path)
            
            # Get project name from .claudetask/project.json
            project_name = os.path.basename(project_path)
            claudetask_project_path = os.path.join(project_path, ".claudetask", "project.json")
            if os.path.exists(claudetask_project_path):
                try:
                    with open(claudetask_project_path, "r") as f:
                        project_meta = json.load(f)
                        project_name = project_meta.get("name", project_name)
                except:
                    pass
            
            # Generate and write CLAUDE.md
            claude_md_path = os.path.join(project_path, "CLAUDE.md")
            # Backup existing CLAUDE.md if it exists
            if os.path.exists(claude_md_path):
                backup_path = os.path.join(project_path, "CLAUDE.md.backup")
                shutil.copy2(claude_md_path, backup_path)
                updated_files.append("CLAUDE.md.backup")
            
            # Generate new CLAUDE.md from template
            generated_content = generate_claude_md(project_name, project_path, tech_stack)
            with open(claude_md_path, "w") as f:
                f.write(generated_content)
            updated_files.append("CLAUDE.md")
            
            # Log for debugging
            has_critical_restrictions = "🔴🔴🔴 ABSOLUTE CRITICAL RESTRICTIONS" in generated_content
            print(f"Generated CLAUDE.md: {len(generated_content)} chars, has critical restrictions: {has_critical_restrictions}")
            
            # 3. Update agent files in .claude/agents/ (force complete refresh)
            agents_source_dir = os.path.join(framework_path, "framework-assets", "claude-agents")
            if os.path.exists(agents_source_dir):
                agents_dest_dir = os.path.join(project_path, ".claude", "agents")
                
                # Remove existing agents directory to ensure clean update
                if os.path.exists(agents_dest_dir):
                    shutil.rmtree(agents_dest_dir)
                
                # Recreate directory
                os.makedirs(agents_dest_dir, exist_ok=True)
                
                # Copy all agent files
                source_agents = [f for f in os.listdir(agents_source_dir) if f.endswith(".md")]
                for agent_file in source_agents:
                    source_file = os.path.join(agents_source_dir, agent_file)
                    dest_file = os.path.join(agents_dest_dir, agent_file)
                    shutil.copy2(source_file, dest_file)
                    updated_files.append(f".claude/agents/{agent_file}")
                
                print(f"Updated {len(source_agents)} agent files: {source_agents[:5]}...")  # Log first 5 for debugging
            else:
                errors.append(f"Agents source directory not found: {agents_source_dir}")
            
            # 4. Copy claude-commands to .claude/commands/
            commands_source_dir = os.path.join(framework_path, "framework-assets", "claude-commands")
            if os.path.exists(commands_source_dir):
                commands_dest_dir = os.path.join(project_path, ".claude", "commands")
                os.makedirs(commands_dest_dir, exist_ok=True)
                
                for command_file in os.listdir(commands_source_dir):
                    if command_file.endswith(".md"):
                        source_file = os.path.join(commands_source_dir, command_file)
                        dest_file = os.path.join(commands_dest_dir, command_file)
                        shutil.copy2(source_file, dest_file)
                        updated_files.append(f".claude/commands/{command_file}")
            
            return {
                "success": True,
                "updated_files": updated_files,
                "errors": errors,
                "message": f"Successfully updated {len(updated_files)} framework files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "updated_files": updated_files,
                "errors": [str(e)],
                "message": f"Framework update failed: {str(e)}"
            }