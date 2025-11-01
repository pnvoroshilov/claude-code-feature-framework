"""Project initialization and management service"""

import os
import json
import shutil
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from git import Repo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import Project, ProjectSettings, Agent, Task, DefaultSkill, ProjectSkill
from ..schemas import ProjectCreate, InitializeProjectResponse
from .claude_config_generator import generate_claude_md, get_default_agents
from .docker_file_service import DockerFileService
from .project_docker_service import create_project_structure_docker, configure_mcp_docker
from .skill_file_service import SkillFileService


class ProjectService:
    """Service for project management"""
    
    @staticmethod
    async def initialize_project(
        db: AsyncSession,
        project_path: str,
        project_name: str,
        github_repo: Optional[str] = None,
        force_reinitialize: bool = False
    ) -> InitializeProjectResponse:
        """Initialize a new project"""
        
        # Remove trailing slash from project path if present
        project_path = project_path.rstrip('/')
        
        # When running in Docker, use DockerFileService to check paths on host
        if os.getenv("RUNNING_IN_DOCKER"):
            if not DockerFileService.is_directory_on_host(project_path):
                raise ValueError(f"Project path does not exist or is not a directory: {project_path}")
            
            # Check if already initialized
            claudetask_dir = os.path.join(project_path, ".claudetask")
            if DockerFileService.check_path_exists_on_host(claudetask_dir):
                if not force_reinitialize:
                    raise ValueError("Project already initialized with ClaudeTask. Use force_reinitialize=true to reinitialize.")
                else:
                    # Clean up existing initialization
                    if os.path.exists(claudetask_dir):
                        shutil.rmtree(claudetask_dir)
        else:
            # Normal validation for non-Docker
            if not os.path.exists(project_path):
                raise ValueError(f"Project path does not exist: {project_path}")
            
            if not os.path.isdir(project_path):
                raise ValueError(f"Path must be a directory: {project_path}")
            
            claudetask_dir = os.path.join(project_path, ".claudetask")
            if os.path.exists(claudetask_dir):
                if not force_reinitialize:
                    raise ValueError("Project already initialized with ClaudeTask. Use force_reinitialize=true to reinitialize.")
                else:
                    # Clean up existing initialization
                    shutil.rmtree(claudetask_dir)
        
        # Generate project ID
        project_id = str(uuid.uuid4())
        
        # Detect technologies
        if os.getenv("RUNNING_IN_DOCKER"):
            tech_stack = ProjectService._detect_technologies_docker(project_path)
        else:
            tech_stack = ProjectService._detect_technologies(project_path)
        
        # Check if it's a git repo
        is_git_repo = os.path.exists(os.path.join(project_path, ".git"))
        
        # Check if project with this path already exists
        existing_project_result = await db.execute(select(Project).where(Project.path == project_path))
        existing_project = existing_project_result.scalar_one_or_none()
        
        if existing_project:
            if not force_reinitialize:
                # Project already exists, make it active and return early
                existing_project.is_active = True
                existing_project.name = project_name  # Update name in case it changed
                existing_project.github_repo = github_repo
                existing_project.tech_stack = tech_stack
                
                # Set other projects as inactive
                result = await db.execute(select(Project).where(Project.id != existing_project.id))
                other_projects = result.scalars().all()
                for p in other_projects:
                    p.is_active = False
                
                await db.commit()
                
                return InitializeProjectResponse(
                    project_id=existing_project.id,
                    mcp_configured=True,  # Assume already configured
                    files_created=[],  # No new files created
                    claude_restart_required=False
                )
            else:
                # Delete existing project from database for reinitialiation
                await db.delete(existing_project)
                await db.commit()
        
        # Create project in database
        project = Project(
            id=project_id,
            name=project_name,
            path=project_path,  # Store the path as provided
            github_repo=github_repo,
            tech_stack=tech_stack,
            is_active=True
        )
        
        # Set other projects as inactive
        result = await db.execute(select(Project).where(Project.id != project_id))
        other_projects = result.scalars().all()
        for p in other_projects:
            p.is_active = False
        
        db.add(project)
        
        # Create project settings
        settings = ProjectSettings(
            project_id=project_id,
            claude_config=generate_claude_md(project_name, project_path, tech_stack)
        )
        db.add(settings)
        
        # Create default agents
        for agent_config in get_default_agents():
            agent = Agent(
                project_id=project_id,
                **agent_config
            )
            db.add(agent)
        
        await db.commit()

        # Enable all default skills automatically
        await ProjectService._enable_all_default_skills(db, project_id, project_path)

        # Create file structure
        if os.getenv("RUNNING_IN_DOCKER"):
            # Use Docker version for creating files on host
            files_created = await create_project_structure_docker(
                project_path, project_id, project_name, tech_stack
            )
            # Configure MCP using Docker
            mcp_configured = configure_mcp_docker(project_path, project_id)
        else:
            # Use normal version for local development
            files_created = await ProjectService._create_project_structure(
                project_path, project_id, project_name, tech_stack
            )
            # Configure MCP normally
            mcp_configured = ProjectService._configure_mcp(project_path, project_id)
        
        return InitializeProjectResponse(
            project_id=project_id,
            mcp_configured=mcp_configured,
            files_created=files_created,
            claude_restart_required=True
        )
    
    @staticmethod
    def _detect_technologies(project_path: str) -> List[str]:
        """Detect technologies used in the project"""
        technologies = []
        
        # JavaScript/TypeScript
        package_json = os.path.join(project_path, "package.json")
        if os.path.exists(package_json):
            with open(package_json, "r") as f:
                try:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    
                    if "react" in deps:
                        technologies.append("React")
                    if "vue" in deps:
                        technologies.append("Vue")
                    if "angular" in deps:
                        technologies.append("Angular")
                    if "typescript" in deps:
                        technologies.append("TypeScript")
                    elif package_json:
                        technologies.append("JavaScript")
                    
                    if "next" in deps:
                        technologies.append("Next.js")
                    if "vite" in deps:
                        technologies.append("Vite")
                except:
                    pass
        
        # Python
        requirements_txt = os.path.join(project_path, "requirements.txt")
        if os.path.exists(requirements_txt):
            technologies.append("Python")
            with open(requirements_txt, "r") as f:
                content = f.read().lower()
                if "django" in content:
                    technologies.append("Django")
                if "fastapi" in content:
                    technologies.append("FastAPI")
                if "flask" in content:
                    technologies.append("Flask")
        
        # Java
        if os.path.exists(os.path.join(project_path, "pom.xml")):
            technologies.append("Java")
            technologies.append("Maven")
        
        if os.path.exists(os.path.join(project_path, "build.gradle")):
            technologies.append("Java")
            technologies.append("Gradle")
        
        # Go
        if os.path.exists(os.path.join(project_path, "go.mod")):
            technologies.append("Go")
        
        # Rust
        if os.path.exists(os.path.join(project_path, "Cargo.toml")):
            technologies.append("Rust")
        
        # .NET
        if any(f.endswith(".csproj") for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))):
            technologies.append(".NET")
            technologies.append("C#")
        
        return technologies
    
    @staticmethod
    def _detect_technologies_docker(project_path: str) -> List[str]:
        """Detect technologies used in the project using Docker operations"""
        technologies = []
        
        try:
            # Check for common files using Docker
            files = DockerFileService.list_files_on_host(project_path)
            
            if "package.json" in files:
                package_content = DockerFileService.read_file_from_host(
                    os.path.join(project_path, "package.json")
                )
                if package_content:
                    try:
                        pkg = json.loads(package_content)
                        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                        
                        if "react" in deps:
                            technologies.append("React")
                        if "vue" in deps:
                            technologies.append("Vue")
                        if "angular" in deps:
                            technologies.append("Angular")
                        if "typescript" in deps:
                            technologies.append("TypeScript")
                        elif "package.json" in files:
                            technologies.append("JavaScript")
                        
                        if "next" in deps:
                            technologies.append("Next.js")
                        if "vite" in deps:
                            technologies.append("Vite")
                    except:
                        technologies.append("JavaScript")
            
            if "requirements.txt" in files:
                technologies.append("Python")
                req_content = DockerFileService.read_file_from_host(
                    os.path.join(project_path, "requirements.txt")
                )
                if req_content:
                    content = req_content.lower()
                    if "django" in content:
                        technologies.append("Django")
                    if "fastapi" in content:
                        technologies.append("FastAPI")
                    if "flask" in content:
                        technologies.append("Flask")
            
            if "pom.xml" in files:
                technologies.extend(["Java", "Maven"])
            
            if "build.gradle" in files:
                technologies.extend(["Java", "Gradle"])
            
            if "go.mod" in files:
                technologies.append("Go")
            
            if "Cargo.toml" in files:
                technologies.append("Rust")
            
            # Check for .csproj files
            for f in files:
                if f.endswith(".csproj"):
                    technologies.extend([".NET", "C#"])
                    break
                    
        except Exception as e:
            print(f"Technology detection error in Docker mode: {e}")
            
        return technologies
    
    @staticmethod
    async def _create_project_structure(
        project_path: str,
        project_id: str,
        project_name: str,
        tech_stack: List[str]
    ) -> List[str]:
        """Create ClaudeTask structure in the project"""
        files_created = []
        
        # Create CLAUDE.md in project root (this is what Claude Code reads)
        claude_md_path = os.path.join(project_path, "CLAUDE.md")
        # Backup existing CLAUDE.md if it exists
        if os.path.exists(claude_md_path):
            backup_path = os.path.join(project_path, "CLAUDE.md.backup")
            shutil.copy2(claude_md_path, backup_path)
            files_created.append("CLAUDE.md.backup")
        
        with open(claude_md_path, "w") as f:
            f.write(generate_claude_md(project_name, project_path, tech_stack))
        files_created.append("CLAUDE.md")
        
        # Create .claude directory for Claude Code agents
        claude_dir = os.path.join(project_path, ".claude")
        os.makedirs(claude_dir, exist_ok=True)
        
        # Create agents directory in .claude
        agents_dir = os.path.join(claude_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)

        # Create skills directory in .claude
        skills_dir = os.path.join(claude_dir, "skills")
        os.makedirs(skills_dir, exist_ok=True)
        
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
                        with open(dest_file, "w") as dst:
                            dst.write(src.read())
                    files_created.append(f".claude/agents/{agent_file}")
        else:
            # Fallback to default agents if framework-assets not found
            for agent_config in get_default_agents():
                agent_path = os.path.join(agents_dir, f"{agent_config['name']}.md")
                with open(agent_path, "w") as f:
                    f.write(agent_config['config'])
                files_created.append(f".claude/agents/{agent_config['name']}.md")
        
        # Create commands directory in .claude
        commands_dir = os.path.join(claude_dir, "commands")
        os.makedirs(commands_dir, exist_ok=True)
        
        # Copy command files from framework-assets
        commands_source_dir = os.path.join(framework_path, "framework-assets", "claude-commands")
        if os.path.exists(commands_source_dir):
            for command_file in os.listdir(commands_source_dir):
                if command_file.endswith(".md") and command_file != "README.md":
                    source_file = os.path.join(commands_source_dir, command_file)
                    dest_file = os.path.join(commands_dir, command_file)
                    with open(source_file, "r") as src:
                        with open(dest_file, "w") as dst:
                            dst.write(src.read())
                    files_created.append(f".claude/commands/{command_file}")
        
        # Create .claudetask directory for internal metadata
        claudetask_dir = os.path.join(project_path, ".claudetask")
        os.makedirs(claudetask_dir, exist_ok=True)
        
        # Create project.json in .claudetask for metadata
        project_json_path = os.path.join(claudetask_dir, "project.json")
        project_meta = {
            "id": project_id,
            "name": project_name,
            "path": project_path,
            "tech_stack": tech_stack,
            "initialized_at": str(datetime.utcnow())
        }
        with open(project_json_path, "w") as f:
            json.dump(project_meta, f, indent=2)
        files_created.append(".claudetask/project.json")
        
        # Create worktrees directory
        worktrees_dir = os.path.join(project_path, "worktrees")
        os.makedirs(worktrees_dir, exist_ok=True)
        files_created.append("worktrees/")
        
        return files_created
    
    @staticmethod
    def _configure_mcp(project_path: str, project_id: str) -> bool:
        """Configure MCP by creating .mcp.json in project root"""
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
        
        # Load MCP template from framework assets
        framework_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        ))
        mcp_template_path = os.path.join(framework_path, "framework-assets", "mcp-configs", "mcp-template.json")
        
        # Read template
        try:
            with open(mcp_template_path, "r") as f:
                template_config = json.load(f)
        except Exception as e:
            print(f"Failed to read MCP template: {e}")
            return False
        
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
            claudetask_config["env"]["CLAUDETASK_PROJECT_ID"] = project_id
            claudetask_config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
            claudetask_config["env"]["CLAUDETASK_BACKEND_URL"] = "http://localhost:3333"
        
        # Merge: preserved servers + all template servers (including playwright and any others)
        new_config = {
            "mcpServers": {
                **preserved_servers,  # User's custom servers (non-claudetask)
                **template_servers    # All servers from template (claudetask, playwright, etc.)
            }
        }
        
        # Write config
        try:
            with open(mcp_config_path, "w") as f:
                json.dump(new_config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to create .mcp.json: {e}")
            return False

    @staticmethod
    async def _enable_all_default_skills(
        db: AsyncSession,
        project_id: str,
        project_path: str
    ) -> None:
        """
        Enable all default skills for a newly initialized project

        This copies all default skills to .claude/skills/ and adds them to project_skills table
        """
        # Get all default skills
        result = await db.execute(select(DefaultSkill))
        default_skills = result.scalars().all()

        if not default_skills:
            print("No default skills found to enable")
            return

        # Initialize file service
        file_service = SkillFileService()

        # Enable each skill
        enabled_count = 0
        for skill in default_skills:
            try:
                # Copy skill file to project
                success = await file_service.copy_skill_to_project(
                    project_path=project_path,
                    skill_file_name=skill.file_name,
                    source_type="default"
                )

                if success:
                    # Add to project_skills table
                    project_skill = ProjectSkill(
                        project_id=project_id,
                        skill_id=skill.id,
                        skill_type="default",
                        enabled_at=datetime.utcnow()
                    )
                    db.add(project_skill)
                    enabled_count += 1
                    print(f"Enabled default skill: {skill.name}")
                else:
                    print(f"Failed to copy skill file: {skill.name}")
            except Exception as e:
                print(f"Error enabling skill {skill.name}: {e}")

        # Commit all enabled skills
        await db.commit()
        print(f"Auto-enabled {enabled_count}/{len(default_skills)} default skills for project {project_id}")


from datetime import datetime