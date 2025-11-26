#!/usr/bin/env python3
"""
CLI tool for migrating ClaudeTask project from local to MongoDB Atlas storage.

This migration utility:
- Migrates all SQLite data to MongoDB Atlas
- Regenerates embeddings with voyage-3-large (1024d)
- Validates data integrity after migration
- Updates project settings to use MongoDB storage mode

Usage:
    python -m claudetask.migrations.migrate_to_mongodb --project-id=<id>
    python -m claudetask.migrations.migrate_to_mongodb --project-id=<id> --dry-run
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

console = Console()
logger = logging.getLogger(__name__)


async def load_project_from_sqlite(project_id: str) -> Dict[str, Any]:
    """
    Load all project data from SQLite database.

    Args:
        project_id: Project ID to migrate

    Returns:
        Dictionary containing:
        - project: Project model
        - settings: ProjectSettings model
        - tasks: List of Task models
        - messages: List of ConversationMemory records

    Raises:
        ValueError: If project not found
    """
    from claudetask.backend.app.database import AsyncSessionLocal
    from claudetask.backend.app.models import (
        Project, Task, TaskHistory, ProjectSettings
    )
    from sqlalchemy import select, text

    async with AsyncSessionLocal() as db:
        # Load project
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found in SQLite database")

        # Load project settings
        result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = result.scalar_one_or_none()

        # Load tasks
        result = await db.execute(
            select(Task).where(Task.project_id == project_id)
        )
        tasks = result.scalars().all()

        # Load task history
        result = await db.execute(
            select(TaskHistory).where(
                TaskHistory.task_id.in_([t.id for t in tasks])
            )
        )
        task_history = result.scalars().all()

        # Load conversation messages
        # Note: In production, this would load from ChromaDB
        # For now, query conversation_memory table if it exists
        messages = []
        try:
            query = text(
                "SELECT * FROM conversation_memory WHERE project_id = :project_id"
            )
            result = await db.execute(query, {"project_id": project_id})
            rows = result.fetchall()
            messages = [dict(row._mapping) for row in rows]
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load messages: {e}[/yellow]")

    return {
        "project": project,
        "settings": settings,
        "tasks": list(tasks),
        "task_history": list(task_history),
        "messages": messages
    }


async def migrate_to_mongodb(
    data: Dict[str, Any],
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Migrate data to MongoDB Atlas.

    Args:
        data: Data loaded from SQLite (project, tasks, messages)
        dry_run: If True, don't actually migrate (preview only)

    Returns:
        Dictionary with migration counts:
        - projects: Number of projects migrated
        - tasks: Number of tasks migrated
        - messages: Number of messages migrated

    Raises:
        ConnectionError: If MongoDB not connected
    """
    from claudetask.backend.app.database_mongodb import mongodb_manager
    from claudetask.backend.app.services.embedding_service import VoyageEmbeddingService

    # Connect to MongoDB
    await mongodb_manager.connect()
    db = mongodb_manager.get_database()

    # Initialize Voyage AI embedding service
    api_key = os.getenv("VOYAGE_AI_API_KEY")
    if not api_key:
        raise ValueError("VOYAGE_AI_API_KEY not set. Cannot generate embeddings.")

    embedding_service = VoyageEmbeddingService(api_key=api_key)

    counts = {"projects": 0, "tasks": 0, "task_history": 0, "messages": 0}

    if not dry_run:
        # Migrate project
        project = data["project"]
        await db.projects.insert_one({
            "_id": project.id,
            "name": project.name,
            "path": project.path,
            "github_repo": project.github_repo,
            "custom_instructions": project.custom_instructions,
            "tech_stack": project.tech_stack or [],
            "project_mode": project.project_mode,
            "is_active": project.is_active,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        })
        counts["projects"] = 1

        # Migrate project settings
        settings = data["settings"]
        if settings:
            await db.project_settings.insert_one({
                "project_id": settings.project_id,
                "auto_mode": settings.auto_mode,
                "auto_priority_threshold": settings.auto_priority_threshold.value,
                "max_parallel_tasks": settings.max_parallel_tasks,
                "test_command": settings.test_command,
                "build_command": settings.build_command,
                "lint_command": settings.lint_command,
                "worktree_enabled": settings.worktree_enabled,
                "manual_mode": settings.manual_mode,
                "test_directory": settings.test_directory,
                "test_framework": settings.test_framework.value if settings.test_framework else None,
                "auto_merge_tests": settings.auto_merge_tests,
                "test_staging_dir": settings.test_staging_dir,
                "storage_mode": "mongodb"  # Update to MongoDB mode
            })

        # Migrate tasks
        for task in data["tasks"]:
            await db.tasks.insert_one({
                "task_id": task.id,
                "project_id": task.project_id,
                "title": task.title,
                "description": task.description,
                "type": task.type.value,
                "priority": task.priority.value,
                "status": task.status.value,
                "analysis": task.analysis,
                "stage_results": task.stage_results or [],
                "testing_urls": task.testing_urls,
                "git_branch": task.git_branch,
                "worktree_path": task.worktree_path,
                "assigned_agent": task.assigned_agent,
                "estimated_hours": task.estimated_hours,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "completed_at": task.completed_at
            })
            counts["tasks"] += 1

        # Migrate task history
        for history in data["task_history"]:
            await db.task_history.insert_one({
                "task_id": history.task_id,
                "old_status": history.old_status.value if history.old_status else None,
                "new_status": history.new_status.value,
                "comment": history.comment,
                "changed_by": history.changed_by,
                "changed_at": history.changed_at
            })
            counts["task_history"] += 1

        # Migrate and re-embed messages with voyage-3-large
        messages = data["messages"]
        if messages:
            console.print(
                f"\n[cyan]Regenerating embeddings with voyage-3-large "
                f"({len(messages)} messages)...[/cyan]"
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                task_progress = progress.add_task(
                    "Embedding messages...",
                    total=len(messages)
                )

                # Process in batches (100 messages at a time)
                batch_size = 100
                for i in range(0, len(messages), batch_size):
                    batch = messages[i:i + batch_size]

                    # Extract text content
                    texts = [msg["content"] for msg in batch]

                    # Generate embeddings with voyage-3-large
                    embeddings = await embedding_service.generate_embeddings(texts)

                    # Insert to MongoDB
                    docs = []
                    for msg, embedding in zip(batch, embeddings):
                        docs.append({
                            "project_id": msg["project_id"],
                            "content": msg["content"],
                            "embedding": embedding,  # 1024-dimensional vector
                            "message_type": msg.get("message_type", "assistant"),
                            "session_id": msg.get("session_id"),
                            "task_id": msg.get("task_id"),
                            "timestamp": msg.get("timestamp", datetime.utcnow()),
                            "metadata": {}
                        })

                    await db.conversation_memory.insert_many(docs)
                    counts["messages"] += len(batch)

                    progress.update(task_progress, advance=len(batch))

    else:
        # Dry run - just count what would be migrated
        counts["projects"] = 1
        counts["tasks"] = len(data["tasks"])
        counts["task_history"] = len(data["task_history"])
        counts["messages"] = len(data["messages"])

    return counts


async def validate_migration(project_id: str, expected_counts: Dict[str, int]) -> bool:
    """
    Validate migration by checking record counts in MongoDB.

    Args:
        project_id: Project ID that was migrated
        expected_counts: Expected counts from SQLite

    Returns:
        True if validation successful, False otherwise
    """
    from claudetask.backend.app.database_mongodb import mongodb_manager

    db = mongodb_manager.get_database()

    # Count records in MongoDB
    actual_counts = {
        "projects": await db.projects.count_documents({"_id": project_id}),
        "tasks": await db.tasks.count_documents({"project_id": project_id}),
        "task_history": await db.task_history.count_documents({}),  # No project_id filter
        "messages": await db.conversation_memory.count_documents({"project_id": project_id})
    }

    # Create comparison table
    table = Table(title="Migration Validation")
    table.add_column("Entity", style="cyan")
    table.add_column("Expected", justify="right", style="yellow")
    table.add_column("Actual", justify="right", style="green")
    table.add_column("Status", justify="center")

    all_match = True
    for key in expected_counts:
        expected = expected_counts[key]
        actual = actual_counts[key]
        match = expected == actual
        all_match = all_match and match

        status = "✓" if match else "✗"
        status_color = "green" if match else "red"

        table.add_row(
            key.replace("_", " ").title(),
            str(expected),
            str(actual),
            f"[{status_color}]{status}[/{status_color}]"
        )

    console.print(table)

    return all_match


async def update_project_settings_storage_mode(project_id: str):
    """
    Update project settings to use MongoDB storage mode in SQLite.

    This ensures the framework uses MongoDB for this project going forward.

    Args:
        project_id: Project ID to update
    """
    from claudetask.backend.app.database import AsyncSessionLocal
    from claudetask.backend.app.models import ProjectSettings
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = result.scalar_one()
        settings.storage_mode = "mongodb"
        await db.commit()


@click.command()
@click.option(
    '--project-id',
    required=True,
    help='Project ID to migrate to MongoDB'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Preview migration without committing changes'
)
def migrate_project(project_id: str, dry_run: bool):
    """
    Migrate ClaudeTask project from local to MongoDB Atlas storage.

    This tool migrates:
    - Project and settings data
    - Tasks and task history
    - Conversation messages with regenerated embeddings (voyage-3-large)

    Example:
        python -m claudetask.migrations.migrate_to_mongodb --project-id=abc123
        python -m claudetask.migrations.migrate_to_mongodb --project-id=abc123 --dry-run
    """

    async def _migrate():
        # Print header
        console.print(
            Panel.fit(
                "[bold cyan]ClaudeTask MongoDB Migration Tool[/bold cyan]\n"
                f"Project ID: [yellow]{project_id}[/yellow]\n"
                f"Mode: [magenta]{'DRY RUN' if dry_run else 'LIVE MIGRATION'}[/magenta]",
                border_style="cyan"
            )
        )

        # Step 1: Load from SQLite
        console.print("\n[cyan]Step 1: Loading project from SQLite...[/cyan]")
        try:
            data = await load_project_from_sqlite(project_id)
            console.print(
                f"  ✓ Loaded: 1 project, {len(data['tasks'])} tasks, "
                f"{len(data['messages'])} messages"
            )
        except Exception as e:
            console.print(f"[red]Error loading project: {e}[/red]")
            return

        # Estimate time
        num_messages = len(data['messages'])
        estimated_minutes = num_messages // 100  # ~100 messages/minute
        if estimated_minutes > 0:
            console.print(
                f"[yellow]Estimated time: {estimated_minutes} minutes[/yellow]"
            )

        # Confirm if not dry run
        if not dry_run:
            if not click.confirm("\nProceed with migration?"):
                console.print("[yellow]Migration cancelled[/yellow]")
                return

        # Step 2: Migrate to MongoDB
        console.print("\n[cyan]Step 2: Migrating to MongoDB Atlas...[/cyan]")
        try:
            counts = await migrate_to_mongodb(data, dry_run=dry_run)

            if dry_run:
                console.print(
                    f"\n[yellow]DRY RUN - Would migrate:[/yellow]\n"
                    f"  - {counts['projects']} project\n"
                    f"  - {counts['tasks']} tasks\n"
                    f"  - {counts['task_history']} task history records\n"
                    f"  - {counts['messages']} messages (with voyage-3-large embeddings)"
                )
            else:
                console.print(
                    f"\n[green]✓ Migration complete![/green]\n"
                    f"  - {counts['projects']} project\n"
                    f"  - {counts['tasks']} tasks\n"
                    f"  - {counts['task_history']} task history records\n"
                    f"  - {counts['messages']} messages"
                )

        except Exception as e:
            console.print(f"[red]Migration failed: {e}[/red]")
            return

        # Step 3: Validate migration (only for live migration)
        if not dry_run:
            console.print("\n[cyan]Step 3: Validating migration...[/cyan]")
            try:
                expected_counts = {
                    "projects": 1,
                    "tasks": len(data['tasks']),
                    "task_history": len(data['task_history']),
                    "messages": len(data['messages'])
                }

                is_valid = await validate_migration(project_id, expected_counts)

                if is_valid:
                    console.print("\n[green]✓ Validation successful![/green]")

                    # Step 4: Update project settings
                    console.print("\n[cyan]Step 4: Updating project settings...[/cyan]")
                    await update_project_settings_storage_mode(project_id)
                    console.print(
                        "[green]✓ Project updated to use MongoDB storage[/green]"
                    )

                    console.print(
                        "\n[bold green]Migration completed successfully![/bold green]\n"
                        "Your project now uses MongoDB Atlas for storage."
                    )

                else:
                    console.print(
                        "\n[red]✗ Validation failed - record counts don't match[/red]\n"
                        "Please check MongoDB Atlas and verify data integrity."
                    )

            except Exception as e:
                console.print(f"[red]Validation failed: {e}[/red]")

    # Run async migration
    asyncio.run(_migrate())


if __name__ == "__main__":
    migrate_project()
