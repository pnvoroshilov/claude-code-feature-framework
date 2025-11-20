"""
Regenerate CLAUDE.md for a specific project
Usage: python migrations/regenerate_claude_md.py <project_id>
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

# Now add backend directory for app imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import Project, ProjectSettings
from app.services.claude_config_generator import generate_claude_md

async def regenerate_claude_md(project_id: str):
    """Regenerate CLAUDE.md for a project"""
    config = get_config()

    # Create async engine
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{config.sqlite_db_path}",
        echo=False
    )

    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as db:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            print(f"✗ Project {project_id} not found")
            return False

        print(f"Project: {project.name}")
        print(f"Path: {project.path}")
        print(f"Mode: {project.project_mode}")

        # Get project settings
        settings_result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = settings_result.scalar_one_or_none()
        worktree_enabled = settings.worktree_enabled if settings else True

        print(f"Worktree enabled: {worktree_enabled}")

        # Generate CLAUDE.md
        claude_md_content = generate_claude_md(
            project_name=project.name,
            project_path=project.path,
            tech_stack=project.tech_stack or [],
            custom_instructions=project.custom_instructions or "",
            project_mode=project.project_mode or "simple",
            worktree_enabled=worktree_enabled
        )

        # Write to file
        claude_md_path = os.path.join(project.path, "CLAUDE.md")

        # Backup existing file
        if os.path.exists(claude_md_path):
            backup_path = claude_md_path + ".backup"
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"✓ Backed up existing CLAUDE.md to {backup_path}")

        # Write new content
        with open(claude_md_path, 'w', encoding='utf-8') as f:
            f.write(claude_md_content)

        print(f"✓ Successfully regenerated {claude_md_path}")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python regenerate_claude_md.py <project_id>")
        print("\nExample: python regenerate_claude_md.py b6f10718-1a73-4b62-96a4-132ff1684a76")
        sys.exit(1)

    project_id = sys.argv[1]
    success = asyncio.run(regenerate_claude_md(project_id))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
