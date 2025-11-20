"""Project initialization and management service"""

import os
import json
import shutil
import uuid
import asyncio
import logging
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

logger = logging.getLogger(__name__)


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

        # Initialize git repository if not present
        if not is_git_repo:
            logger.info(f"No git repository found at {project_path}, initializing...")
            try:
                git_init_result = await ProjectService._initialize_git_repository(
                    project_path,
                    project_name,
                    github_repo
                )
                if git_init_result:
                    logger.info(f"Git repository initialized successfully at {project_path}")
                    is_git_repo = True
            except Exception as e:
                logger.warning(f"Failed to initialize git repository: {e}")
                # Continue without git - non-fatal error

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
                # First, delete related records to avoid foreign key constraints
                from ..models import ProjectMCPConfig, CustomMCPConfig, ProjectSkill

                # Delete project_mcp_configs
                await db.execute(
                    select(ProjectMCPConfig).where(ProjectMCPConfig.project_id == existing_project.id)
                )
                project_configs = (await db.execute(
                    select(ProjectMCPConfig).where(ProjectMCPConfig.project_id == existing_project.id)
                )).scalars().all()
                for config in project_configs:
                    await db.delete(config)

                # Delete custom_mcp_configs
                custom_configs = (await db.execute(
                    select(CustomMCPConfig).where(CustomMCPConfig.project_id == existing_project.id)
                )).scalars().all()
                for config in custom_configs:
                    await db.delete(config)

                # Delete project_skills
                project_skills = (await db.execute(
                    select(ProjectSkill).where(ProjectSkill.project_id == existing_project.id)
                )).scalars().all()
                for skill in project_skills:
                    await db.delete(skill)

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

        # Import existing .mcp.json configs into database
        await ProjectService._import_existing_mcp_configs(db, project_id, project_path)

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
        
        # Initialize directory trust for Claude Code
        # This must be done BEFORE any skill creation sessions
        await ProjectService._initialize_directory_trust(project_path)

        return InitializeProjectResponse(
            project_id=project_id,
            mcp_configured=mcp_configured,
            files_created=files_created,
            claude_restart_required=True
        )

    @staticmethod
    async def _initialize_directory_trust(project_path: str):
        """
        Initialize directory trust for Claude Code by launching in normal mode.

        This is required for MCP servers to be visible in new projects.
        The first launch must be in normal mode (without --dangerously-skip-permissions)
        to allow the user to accept the directory trust prompt.

        Process:
        1. Launch Claude in normal mode (no --dangerously-skip-permissions)
        2. Wait 10 seconds for trust prompt and auto-acceptance
        3. Close the session
        4. Future sessions can use --dangerously-skip-permissions
        """
        try:
            from .claude_terminal_service import ClaudeTerminalSession

            logger.info(f"Initializing directory trust for {project_path}")

            # Create a special session for directory trust initialization
            # skip_permissions=False to show the trust prompt
            session_id = f"dir-trust-init-{uuid.uuid4()}"
            session = ClaudeTerminalSession(
                session_id=session_id,
                task_id=0,  # No task associated
                working_dir=project_path,
                skip_permissions=False  # CRITICAL: Must be False for first launch
            )

            # Start the session
            if await session.start():
                logger.info(f"Directory trust session started, waiting 10s for trust prompt")

                # Wait 10 seconds for Claude to show trust prompt and auto-accept
                # The user should see and accept the prompt during this time
                await asyncio.sleep(10)

                # Stop the session
                await session.stop()
                logger.info(f"Directory trust initialization completed for {project_path}")
            else:
                logger.warning(f"Failed to start directory trust session for {project_path}")

        except Exception as e:
            logger.error(f"Error initializing directory trust: {e}", exc_info=True)
            # Don't fail project initialization if this fails
            # User can manually trust the directory later

    @staticmethod
    async def _initialize_git_repository(
        project_path: str,
        project_name: str,
        github_repo: Optional[str] = None
    ) -> bool:
        """
        Initialize a git repository in the project directory.

        This creates a new git repository with:
        - Initial .gitignore for framework files
        - Git configuration (user.name, user.email)
        - Initial commit with project files
        - Optional remote origin (if github_repo provided)

        Args:
            project_path: Path to project directory
            project_name: Name of the project
            github_repo: Optional GitHub repository URL

        Returns:
            bool: True if initialization successful, False otherwise
        """
        import subprocess

        try:
            # Run git init
            result = subprocess.run(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.error(f"git init failed: {result.stderr}")
                return False

            logger.info(f"Git repository initialized at {project_path}")

            # Create .gitignore if it doesn't exist
            gitignore_path = os.path.join(project_path, ".gitignore")
            if not os.path.exists(gitignore_path):
                gitignore_content = """# ClaudeTask Framework
.claudetask/
.mcp.json.backup
*.pyc
__pycache__/
.env
.venv/
venv/
env/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
yarn-error.log

# Python
*.egg-info/
dist/
build/
"""
                with open(gitignore_path, "w") as f:
                    f.write(gitignore_content)
                logger.info("Created .gitignore file")

            # Configure git user if not already configured
            # Check global config first
            check_name = subprocess.run(
                ["git", "config", "user.name"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            check_email = subprocess.run(
                ["git", "config", "user.email"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            # Set local config if global not set
            if not check_name.stdout.strip():
                subprocess.run(
                    ["git", "config", "user.name", "ClaudeTask Framework"],
                    cwd=project_path,
                    timeout=5
                )
                logger.info("Set git user.name")

            if not check_email.stdout.strip():
                subprocess.run(
                    ["git", "config", "user.email", "claudetask@framework.local"],
                    cwd=project_path,
                    timeout=5
                )
                logger.info("Set git user.email")

            # Add all files for initial commit
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                timeout=10
            )

            # Create initial commit
            commit_result = subprocess.run(
                ["git", "commit", "-m", f"Initial commit: {project_name} project initialized with ClaudeTask Framework"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if commit_result.returncode == 0:
                logger.info("Created initial git commit")
            else:
                # Commit might fail if nothing to commit, that's ok
                logger.debug(f"Initial commit status: {commit_result.stderr}")

            # Add remote origin if github_repo provided
            if github_repo:
                try:
                    subprocess.run(
                        ["git", "remote", "add", "origin", github_repo],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    logger.info(f"Added git remote origin: {github_repo}")
                except Exception as e:
                    logger.warning(f"Failed to add remote origin: {e}")

            return True

        except subprocess.TimeoutExpired:
            logger.error("Git initialization timed out")
            return False
        except FileNotFoundError:
            logger.error("Git command not found - is git installed?")
            return False
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}", exc_info=True)
            return False

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

        # Create hooks directory
        hooks_dir = os.path.join(claude_dir, "hooks")
        os.makedirs(hooks_dir, exist_ok=True)

        # Copy hook files from framework-assets
        hooks_source_dir = os.path.join(framework_path, "framework-assets", "claude-hooks")
        hook_configs = {}

        if os.path.exists(hooks_source_dir):
            for hook_file in os.listdir(hooks_source_dir):
                if hook_file.endswith(".json"):
                    source_file = os.path.join(hooks_source_dir, hook_file)
                    dest_file = os.path.join(hooks_dir, hook_file)
                    with open(source_file, "r") as src:
                        with open(dest_file, "w") as dst:
                            dst.write(src.read())
                    files_created.append(f".claude/hooks/{hook_file}")

                    # Read hook config for settings.json
                    try:
                        with open(source_file, 'r') as f:
                            hook_data = json.load(f)
                            if "hook_config" in hook_data:
                                # Merge hook configs
                                for event_type, event_hooks in hook_data["hook_config"].items():
                                    if event_type not in hook_configs:
                                        hook_configs[event_type] = []
                                    hook_configs[event_type].extend(event_hooks)
                    except Exception as e:
                        print(f"Failed to read hook config from {hook_file}: {e}")

                elif hook_file.endswith(".sh"):
                    # Copy shell script hooks and make them executable
                    source_file = os.path.join(hooks_source_dir, hook_file)
                    dest_file = os.path.join(hooks_dir, hook_file)
                    with open(source_file, "r") as src:
                        with open(dest_file, "w") as dst:
                            dst.write(src.read())
                    # Make script executable
                    os.chmod(dest_file, 0o755)
                    files_created.append(f".claude/hooks/{hook_file}")

            # Create/update .claude/settings.json with hook configurations
            settings_file = os.path.join(claude_dir, "settings.json")
            settings_data = {"hooks": hook_configs}

            # Merge with existing settings if file exists
            if os.path.exists(settings_file):
                try:
                    with open(settings_file, 'r') as f:
                        existing_settings = json.load(f)
                        existing_settings["hooks"] = hook_configs
                        settings_data = existing_settings
                except Exception as e:
                    print(f"Failed to read existing settings.json: {e}")

            with open(settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
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
        with open(settings_local_file, 'w') as f:
            json.dump(settings_local_data, f, indent=2)
        files_created.append(".claude/settings.local.json")

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

    @staticmethod
    async def _import_existing_mcp_configs(
        db: AsyncSession,
        project_id: str,
        project_path: str
    ) -> None:
        """
        Import existing .mcp.json configs from project into database as custom configs

        This reads the project's existing .mcp.json file and creates custom MCP config
        records in the database, so they appear in the UI and are properly tracked.
        """
        import json
        from pathlib import Path
        from ..models import CustomMCPConfig, ProjectMCPConfig

        mcp_file_path = Path(project_path) / ".mcp.json"

        # Check if .mcp.json exists
        if not mcp_file_path.exists():
            print(f"No .mcp.json found at {mcp_file_path}, skipping import")
            return

        try:
            # Read existing .mcp.json
            with open(mcp_file_path, 'r') as f:
                mcp_data = json.load(f)

            mcp_servers = mcp_data.get("mcpServers", {})

            if not mcp_servers:
                print(f"No MCP servers found in .mcp.json, skipping import")
                return

            # Import each MCP server config
            imported_count = 0
            for server_name, server_config in mcp_servers.items():
                try:
                    # Update config with current project ID (for claudetask MCP)
                    import copy
                    config_to_save = copy.deepcopy(server_config)

                    if server_name == "claudetask" and "env" in config_to_save:
                        # Update environment variables with current project ID and path
                        config_to_save["env"]["CLAUDETASK_PROJECT_ID"] = project_id
                        config_to_save["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
                        print(f"Updated claudetask MCP config with project_id={project_id}")

                    # Create custom MCP config record
                    custom_mcp_config = CustomMCPConfig(
                        project_id=project_id,
                        name=server_name,
                        description=f"Imported from existing .mcp.json - {server_name} MCP server",
                        category="imported",
                        config=config_to_save,
                        status="active",
                        created_by="system_import",
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(custom_mcp_config)
                    await db.flush()  # Get the ID

                    # Create project_mcp_configs junction record (mark as enabled)
                    project_mcp_config = ProjectMCPConfig(
                        project_id=project_id,
                        mcp_config_id=custom_mcp_config.id,
                        mcp_config_type="custom",
                        enabled_at=datetime.utcnow(),
                        enabled_by="system_import"
                    )
                    db.add(project_mcp_config)

                    imported_count += 1
                    print(f"Imported MCP config: {server_name}")

                except Exception as e:
                    print(f"Error importing MCP config {server_name}: {e}")
                    continue

            # Commit all imported configs
            await db.commit()
            print(f"Imported {imported_count}/{len(mcp_servers)} MCP configs from .mcp.json for project {project_id}")

        except json.JSONDecodeError as e:
            print(f"Error parsing .mcp.json: {e}")
        except Exception as e:
            print(f"Error importing MCP configs: {e}")

    @staticmethod
    async def regenerate_claude_md(db: AsyncSession, project_id: str):
        """
        Regenerate CLAUDE.md file with current project data including custom instructions

        Args:
            db: Database session
            project_id: Project ID
        """
        from sqlalchemy import select
        from ..models import Project, ProjectSettings
        from .claude_config_generator import generate_claude_md
        import os

        # Get project from database
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get project settings to retrieve worktree_enabled
        settings_result = await db.execute(select(ProjectSettings).where(ProjectSettings.project_id == project_id))
        settings = settings_result.scalar_one_or_none()
        worktree_enabled = settings.worktree_enabled if settings else True

        # Generate CLAUDE.md with custom instructions, project mode, and worktree settings
        claude_md_content = generate_claude_md(
            project_name=project.name,
            project_path=project.path,
            tech_stack=project.tech_stack or [],
            custom_instructions=project.custom_instructions or "",
            project_mode=project.project_mode or "simple",
            worktree_enabled=worktree_enabled
        )

        # Write to CLAUDE.md file
        claude_md_path = os.path.join(project.path, "CLAUDE.md")

        # Backup existing file
        if os.path.exists(claude_md_path):
            backup_path = os.path.join(project.path, "CLAUDE.md.backup")
            import shutil
            shutil.copy2(claude_md_path, backup_path)

        # Write new content
        with open(claude_md_path, "w", encoding="utf-8") as f:
            f.write(claude_md_content)

        print(f"Regenerated CLAUDE.md for project {project_id} with custom instructions")
