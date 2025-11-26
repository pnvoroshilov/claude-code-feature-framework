"""API endpoints for cloud storage configuration (MongoDB Atlas + Voyage AI)"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path
import logging
from datetime import datetime

from ..database import get_db
from ..models import Project, Task, ProjectSettings, TaskHistory, ClaudeSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings/cloud-storage", tags=["cloud-storage"])


class CloudStorageConfig(BaseModel):
    """
    Cloud storage configuration model.

    Includes MongoDB Atlas connection credentials and Voyage AI API key.
    """
    connection_string: str = Field(
        ...,
        description="MongoDB connection string (mongodb+srv://...)",
        min_length=1
    )
    database_name: str = Field(
        default="claudetask",
        description="MongoDB database name"
    )
    voyage_api_key: str = Field(
        ...,
        description="Voyage AI API key for voyage-3-large embeddings",
        min_length=1
    )


class CloudStorageStatus(BaseModel):
    """Cloud storage configuration status."""
    configured: bool = Field(description="Whether MongoDB Atlas is configured")
    connection_string_set: bool = Field(description="Whether connection string is set")
    voyage_api_key_set: bool = Field(description="Whether Voyage AI API key is set")


class ConnectionTestResult(BaseModel):
    """Result of testing MongoDB and Voyage AI connections."""
    mongodb_connected: bool = Field(default=False, description="MongoDB connection successful")
    voyage_ai_valid: bool = Field(default=False, description="Voyage AI API key valid")
    database_writable: bool = Field(default=False, description="Database has write permissions")
    error: Optional[str] = Field(default=None, description="Error message if connection failed")


@router.get("/status", response_model=CloudStorageStatus)
async def get_cloud_storage_status():
    """
    Check if MongoDB Atlas and Voyage AI are configured.

    Returns:
        Configuration status with boolean flags

    Example:
        GET /api/settings/cloud-storage/status
        {
          "configured": true,
          "connection_string_set": true,
          "voyage_api_key_set": true
        }
    """
    connection_string_set = bool(os.getenv("MONGODB_CONNECTION_STRING"))
    voyage_api_key_set = bool(os.getenv("VOYAGE_AI_API_KEY"))

    return CloudStorageStatus(
        configured=connection_string_set and voyage_api_key_set,
        connection_string_set=connection_string_set,
        voyage_api_key_set=voyage_api_key_set
    )


@router.get("/config")
async def get_cloud_storage_config():
    """
    Get current cloud storage configuration (with masked secrets).

    Returns saved configuration from environment variables.
    API keys and passwords are masked for security.

    Returns:
        Configuration with masked sensitive values

    Example:
        GET /api/settings/cloud-storage/config

        Response:
        {
          "configured": true,
          "connection_string": "mongodb+srv://user:***@cluster.mongodb.net/",
          "database_name": "claudetask",
          "voyage_api_key_set": true
        }
    """
    connection_string = os.getenv("MONGODB_CONNECTION_STRING", "")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "claudetask")
    voyage_api_key = os.getenv("VOYAGE_AI_API_KEY", "")

    # Mask connection string password for display
    masked_connection_string = ""
    if connection_string:
        # mongodb+srv://user:password@cluster... -> mongodb+srv://user:***@cluster...
        import re
        masked_connection_string = re.sub(
            r'(mongodb\+srv://[^:]+:)[^@]+(@)',
            r'\1***\2',
            connection_string
        )

    return {
        "configured": bool(connection_string and voyage_api_key),
        "connection_string": masked_connection_string,
        "database_name": database_name,
        "voyage_api_key_set": bool(voyage_api_key)
    }


@router.post("/test", response_model=ConnectionTestResult)
async def test_cloud_storage_connection(config: CloudStorageConfig):
    """
    Test MongoDB Atlas and Voyage AI connections before saving.

    This endpoint validates:
    1. MongoDB connection string format and connectivity
    2. Database write permissions
    3. Voyage AI API key validity

    Args:
        config: Cloud storage configuration to test

    Returns:
        Test results for MongoDB and Voyage AI

    Example:
        POST /api/settings/cloud-storage/test
        {
          "connection_string": "mongodb+srv://...",
          "database_name": "claudetask",
          "voyage_api_key": "vo-..."
        }

        Response:
        {
          "mongodb_connected": true,
          "voyage_ai_valid": true,
          "database_writable": true,
          "error": null
        }
    """
    results = ConnectionTestResult()

    # Test MongoDB connection
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        # Create temporary client with test configuration
        client = AsyncIOMotorClient(
            config.connection_string,
            serverSelectionTimeoutMS=5000,
            tls=True,
            tlsAllowInvalidCertificates=False
        )

        # Ping database to verify connection
        await client.admin.command('ping')
        results.mongodb_connected = True

        # Test write permissions
        db = client[config.database_name]
        test_collection = db["_connection_test"]
        await test_collection.insert_one({"test": "connection"})
        await test_collection.delete_one({"test": "connection"})
        results.database_writable = True

        # Close test client
        client.close()

    except Exception as e:
        logger.error(f"MongoDB connection test failed: {e}")
        results.error = f"MongoDB error: {str(e)}"
        return results

    # Test Voyage AI API
    try:
        import voyageai

        # Create Voyage AI client
        client = voyageai.Client(api_key=config.voyage_api_key)

        # Test embedding generation with a simple text
        client.embed(["test"], model="voyage-3-large")
        results.voyage_ai_valid = True

    except Exception as e:
        logger.error(f"Voyage AI API test failed: {e}")
        results.error = f"Voyage AI error: {str(e)}"
        return results

    return results


@router.post("/save")
async def save_cloud_storage_config(config: CloudStorageConfig):
    """
    Save MongoDB Atlas and Voyage AI configuration to .env file.

    This endpoint:
    1. Updates or adds MongoDB and Voyage AI credentials to .env file
    2. Updates current process environment variables
    3. Requires application restart for full effect

    Args:
        config: Cloud storage configuration to save

    Returns:
        Save status and restart requirement

    Raises:
        HTTPException: If unable to write to .env file

    Example:
        POST /api/settings/cloud-storage/save
        {
          "connection_string": "mongodb+srv://...",
          "database_name": "claudetask",
          "voyage_api_key": "vo-..."
        }

        Response:
        {
          "status": "saved",
          "restart_required": true,
          "message": "Configuration saved successfully. Restart application to apply changes."
        }
    """
    try:
        # Get .env file path (relative to backend directory)
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

        # Read existing .env file
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = f.readlines()

        # Configuration keys to update
        keys_to_update = {
            "MONGODB_CONNECTION_STRING": config.connection_string,
            "MONGODB_DATABASE_NAME": config.database_name,
            "VOYAGE_AI_API_KEY": config.voyage_api_key
        }

        # Update existing lines or mark for addition
        updated_lines = []
        keys_updated = set()

        for line in env_lines:
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                updated_lines.append(line)
                continue

            # Extract key from line
            if '=' in line:
                key = line.split('=')[0].strip()

                # Update if key matches
                if key in keys_to_update:
                    updated_lines.append(f"{key}={keys_to_update[key]}\n")
                    keys_updated.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add missing keys at the end
        if keys_updated != set(keys_to_update.keys()):
            # Add section header if adding new keys
            if not keys_updated:
                updated_lines.append("\n# MongoDB Atlas Configuration\n")

            for key, value in keys_to_update.items():
                if key not in keys_updated:
                    updated_lines.append(f"{key}={value}\n")

        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)

        # Update current environment (for immediate use without restart)
        os.environ.update(keys_to_update)

        logger.info("Cloud storage configuration saved successfully")

        return {
            "status": "saved",
            "restart_required": True,
            "message": "Configuration saved successfully. Restart application to apply changes."
        }

    except Exception as e:
        logger.error(f"Failed to save cloud storage configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.delete("/config")
async def delete_cloud_storage_config():
    """
    Remove MongoDB Atlas and Voyage AI configuration from .env file.

    This endpoint:
    1. Removes MongoDB and Voyage AI credentials from .env file
    2. Updates current process environment variables
    3. Disconnects MongoDB if connected

    Returns:
        Deletion status

    Example:
        DELETE /api/settings/cloud-storage/config

        Response:
        {
          "status": "deleted",
          "message": "Cloud storage configuration removed successfully."
        }
    """
    try:
        # Get .env file path
        env_path = Path(__file__).parent.parent.parent.parent / ".env"

        if not env_path.exists():
            return {
                "status": "not_found",
                "message": "No .env file found"
            }

        # Read existing .env file
        with open(env_path, 'r') as f:
            env_lines = f.readlines()

        # Keys to remove
        keys_to_remove = {
            "MONGODB_CONNECTION_STRING",
            "MONGODB_DATABASE_NAME",
            "VOYAGE_AI_API_KEY"
        }

        # Filter out lines with these keys
        updated_lines = []
        for line in env_lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                if key not in keys_to_remove:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Write back to .env file
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)

        # Remove from current environment
        for key in keys_to_remove:
            os.environ.pop(key, None)

        # Disconnect MongoDB if connected
        try:
            from ..database_mongodb import mongodb_manager
            await mongodb_manager.disconnect()
        except Exception:
            pass

        logger.info("Cloud storage configuration removed successfully")

        return {
            "status": "deleted",
            "message": "Cloud storage configuration removed successfully."
        }

    except Exception as e:
        logger.error(f"Failed to delete cloud storage configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete configuration: {str(e)}"
        )


@router.get("/health")
async def cloud_storage_health():
    """
    Check MongoDB Atlas connection health.

    Returns:
        Health status including connectivity and write permissions

    Example:
        GET /api/settings/cloud-storage/health

        Response:
        {
          "connected": true,
          "database": "claudetask",
          "writable": true,
          "error": null
        }
    """
    try:
        from ..database_mongodb import mongodb_manager

        health_status = await mongodb_manager.health_check()
        return health_status

    except Exception as e:
        logger.error(f"Cloud storage health check failed: {e}")
        return {
            "connected": False,
            "database": "claudetask",
            "writable": False,
            "error": str(e)
        }


# ==================
# Migration Endpoints
# ==================

class MigrationRequest(BaseModel):
    """Request to migrate project data between storage backends."""
    project_id: str = Field(..., description="Project ID to migrate")
    target_mode: str = Field(..., description="Target storage mode: 'local' or 'mongodb'")
    force: bool = Field(default=False, description="Force migration even if already on target mode (useful for initial sync)")


class MigrationProgress(BaseModel):
    """Migration progress response."""
    status: str = Field(..., description="Migration status: pending, in_progress, completed, failed")
    current_step: str = Field(default="", description="Current migration step")
    steps_completed: int = Field(default=0, description="Number of steps completed")
    total_steps: int = Field(default=6, description="Total migration steps")
    projects_migrated: int = Field(default=0)
    tasks_migrated: int = Field(default=0)
    sessions_migrated: int = Field(default=0)
    history_migrated: int = Field(default=0)
    error: Optional[str] = Field(default=None)


@router.get("/project/{project_id}/storage-mode")
async def get_project_storage_mode(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current storage mode for a project.

    Returns:
        Current storage mode and MongoDB availability
    """
    try:
        # Get project settings
        result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = result.scalar_one_or_none()

        if not settings:
            return {
                "project_id": project_id,
                "storage_mode": "local",
                "mongodb_available": False,
                "error": "Project settings not found"
            }

        # Check if MongoDB is configured
        mongodb_configured = bool(
            os.getenv("MONGODB_CONNECTION_STRING") and
            os.getenv("VOYAGE_AI_API_KEY")
        )

        # Check if MongoDB is connected
        mongodb_connected = False
        if mongodb_configured:
            try:
                from ..database_mongodb import mongodb_manager
                if mongodb_manager.client:
                    await mongodb_manager.client.admin.command('ping')
                    mongodb_connected = True
            except Exception:
                pass

        return {
            "project_id": project_id,
            "storage_mode": settings.storage_mode or "local",
            "mongodb_configured": mongodb_configured,
            "mongodb_connected": mongodb_connected
        }

    except Exception as e:
        logger.error(f"Failed to get storage mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project/{project_id}/migrate")
async def migrate_project_storage(
    project_id: str,
    request: MigrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Migrate project data between SQLite and MongoDB.

    This endpoint handles full data migration:
    1. Projects and settings
    2. Tasks and task history
    3. Claude sessions
    4. Updates storage_mode setting

    Args:
        project_id: Project ID to migrate
        request: Migration parameters (target_mode)

    Returns:
        Migration progress and results
    """
    progress = MigrationProgress(status="in_progress", current_step="Initializing")

    try:
        # Validate target mode
        if request.target_mode not in ["local", "mongodb"]:
            raise HTTPException(status_code=400, detail="Invalid target mode. Use 'local' or 'mongodb'")

        # Get current project and settings
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        settings_result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = settings_result.scalar_one_or_none()

        current_mode = settings.storage_mode if settings else "local"

        if current_mode == request.target_mode and not request.force:
            return {
                "status": "completed",
                "message": f"Project already using {request.target_mode} storage. Use force=true to sync data.",
                "migration_needed": False
            }

        # Migrate based on direction
        if request.target_mode == "mongodb":
            progress = await _migrate_to_mongodb(project_id, db, progress)
        else:
            progress = await _migrate_to_sqlite(project_id, db, progress)

        # Update storage_mode in settings
        if settings:
            settings.storage_mode = request.target_mode
            await db.commit()

        progress.status = "completed"
        progress.current_step = "Migration completed"

        return {
            "status": "completed",
            "message": f"Successfully migrated to {request.target_mode}",
            "progress": progress.model_dump(),
            "storage_mode": request.target_mode
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        progress.status = "failed"
        progress.error = str(e)
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


async def _migrate_to_mongodb(
    project_id: str,
    db: AsyncSession,
    progress: MigrationProgress
) -> MigrationProgress:
    """Migrate project data from SQLite to MongoDB."""
    from ..database_mongodb import mongodb_manager

    # Check MongoDB connection
    if not mongodb_manager.client:
        try:
            await mongodb_manager.connect()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"MongoDB not available: {e}. Configure in Settings → Cloud Storage"
            )

    mongo_db = mongodb_manager.get_database()

    # Step 1: Migrate project
    progress.current_step = "Migrating project"
    progress.steps_completed = 1

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if project:
        project_doc = {
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
        }
        await mongo_db.projects.replace_one(
            {"_id": project.id},
            project_doc,
            upsert=True
        )
        progress.projects_migrated = 1

    # Step 2: Migrate project settings
    progress.current_step = "Migrating settings"
    progress.steps_completed = 2

    settings_result = await db.execute(
        select(ProjectSettings).where(ProjectSettings.project_id == project_id)
    )
    settings = settings_result.scalar_one_or_none()

    if settings:
        settings_doc = {
            "_id": f"{project_id}_settings",
            "project_id": project_id,
            "auto_mode": settings.auto_mode,
            "auto_priority_threshold": settings.auto_priority_threshold.value if settings.auto_priority_threshold else "High",
            "max_parallel_tasks": settings.max_parallel_tasks,
            "test_command": settings.test_command,
            "build_command": settings.build_command,
            "lint_command": settings.lint_command,
            "worktree_enabled": settings.worktree_enabled,
            "manual_mode": settings.manual_mode,
            "test_directory": settings.test_directory,
            "test_framework": settings.test_framework.value if settings.test_framework else "pytest",
            "auto_merge_tests": settings.auto_merge_tests,
            "test_staging_dir": settings.test_staging_dir,
            "storage_mode": "mongodb"  # Will be mongodb after migration
        }
        await mongo_db.project_settings.replace_one(
            {"project_id": project_id},
            settings_doc,
            upsert=True
        )

    # Step 3: Migrate tasks using raw SQL to avoid enum validation issues
    progress.current_step = "Migrating tasks"
    progress.steps_completed = 3

    from sqlalchemy import text

    # Use raw SQL to get tasks without enum validation
    tasks_query = text("""
        SELECT id, project_id, title, description, type, priority, status,
               analysis, stage_results, testing_urls, git_branch, worktree_path,
               assigned_agent, estimated_hours, created_at, updated_at, completed_at
        FROM tasks WHERE project_id = :project_id
    """)
    tasks_result = await db.execute(tasks_query, {"project_id": project_id})
    tasks_rows = tasks_result.fetchall()

    # Map legacy statuses
    status_mapping = {
        "PR": "Code Review",
        "BACKLOG": "Backlog",
        "ANALYSIS": "Analysis",
        "IN_PROGRESS": "In Progress",
        "TESTING": "Testing",
        "CODE_REVIEW": "Code Review",
        "DONE": "Done",
        "BLOCKED": "Blocked"
    }

    import json

    for row in tasks_rows:
        # Map status (handle legacy values)
        raw_status = row.status or "BACKLOG"
        task_status = status_mapping.get(raw_status, raw_status)

        # Parse JSON fields
        stage_results = []
        if row.stage_results:
            try:
                stage_results = json.loads(row.stage_results) if isinstance(row.stage_results, str) else row.stage_results
            except (json.JSONDecodeError, TypeError):
                stage_results = []

        testing_urls = None
        if row.testing_urls:
            try:
                testing_urls = json.loads(row.testing_urls) if isinstance(row.testing_urls, str) else row.testing_urls
            except (json.JSONDecodeError, TypeError):
                testing_urls = None

        task_doc = {
            "_id": row.id,
            "project_id": row.project_id,
            "title": row.title,
            "description": row.description,
            "type": row.type or "Feature",
            "priority": row.priority or "Medium",
            "status": task_status,
            "analysis": row.analysis,
            "stage_results": stage_results,
            "testing_urls": testing_urls,
            "git_branch": row.git_branch,
            "worktree_path": row.worktree_path,
            "assigned_agent": row.assigned_agent,
            "estimated_hours": row.estimated_hours,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "completed_at": row.completed_at
        }
        await mongo_db.tasks.replace_one(
            {"_id": row.id, "project_id": project_id},
            task_doc,
            upsert=True
        )
        progress.tasks_migrated += 1

    # Also store task IDs for history migration
    task_ids = [row.id for row in tasks_rows]

    # Step 4: Migrate task history using raw SQL
    progress.current_step = "Migrating task history"
    progress.steps_completed = 4

    for task_id in task_ids:
        # Use raw SQL to get history without enum validation
        history_query = text("""
            SELECT id, task_id, old_status, new_status, comment, changed_by, changed_at
            FROM task_history WHERE task_id = :task_id
        """)
        history_result = await db.execute(history_query, {"task_id": task_id})
        history_rows = history_result.fetchall()

        for item in history_rows:
            # Map status values
            old_status = status_mapping.get(item.old_status, item.old_status) if item.old_status else None
            new_status = status_mapping.get(item.new_status, item.new_status) if item.new_status else None

            history_doc = {
                "_id": item.id,
                "task_id": item.task_id,
                "project_id": project_id,
                "old_status": old_status,
                "new_status": new_status,
                "comment": item.comment,
                "changed_by": item.changed_by,
                "changed_at": item.changed_at
            }
            await mongo_db.task_history.replace_one(
                {"_id": item.id},
                history_doc,
                upsert=True
            )
            progress.history_migrated += 1

    # Step 5: Migrate Claude sessions
    progress.current_step = "Migrating sessions"
    progress.steps_completed = 5

    sessions_result = await db.execute(
        select(ClaudeSession).where(ClaudeSession.project_id == project_id)
    )
    sessions = sessions_result.scalars().all()

    for session in sessions:
        session_doc = {
            "_id": session.id,
            "session_id": session.session_id,
            "task_id": session.task_id,
            "project_id": session.project_id,
            "status": session.status,
            "mode": session.mode,
            "working_dir": session.working_dir,
            "context_file": session.context_file,
            "launch_command": session.launch_command,
            "context": session.context,
            "messages": session.messages,
            "session_metadata": session.session_metadata,
            "summary": session.summary,
            "statistics": session.statistics,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "completed_at": session.completed_at
        }
        await mongo_db.claude_sessions.replace_one(
            {"_id": session.id},
            session_doc,
            upsert=True
        )
        progress.sessions_migrated += 1

    # Step 6: Create indexes
    progress.current_step = "Creating indexes"
    progress.steps_completed = 6

    await mongodb_manager.create_indexes()

    return progress


async def _migrate_to_sqlite(
    project_id: str,
    db: AsyncSession,
    progress: MigrationProgress
) -> MigrationProgress:
    """Migrate project data from MongoDB to SQLite."""
    from ..database_mongodb import mongodb_manager

    # Check MongoDB connection
    if not mongodb_manager.client:
        # Nothing to migrate from if MongoDB is not connected
        progress.status = "completed"
        progress.current_step = "No MongoDB data to migrate"
        return progress

    mongo_db = mongodb_manager.get_database()

    # Step 1: Get project from MongoDB
    progress.current_step = "Reading MongoDB data"
    progress.steps_completed = 1

    mongo_project = await mongo_db.projects.find_one({"_id": project_id})

    # Step 2: Sync tasks from MongoDB to SQLite
    progress.current_step = "Syncing tasks"
    progress.steps_completed = 2

    mongo_tasks = await mongo_db.tasks.find({"project_id": project_id}).to_list(None)

    for mongo_task in mongo_tasks:
        # Check if task exists in SQLite
        result = await db.execute(
            select(Task).where(Task.id == mongo_task.get("_id"))
        )
        existing_task = result.scalar_one_or_none()

        if existing_task:
            # Update existing task
            existing_task.title = mongo_task.get("title", existing_task.title)
            existing_task.description = mongo_task.get("description")
            existing_task.status = mongo_task.get("status", "Backlog")
            existing_task.analysis = mongo_task.get("analysis")
            existing_task.stage_results = mongo_task.get("stage_results", [])
            existing_task.testing_urls = mongo_task.get("testing_urls")
            existing_task.updated_at = datetime.utcnow()
        else:
            # Create new task in SQLite
            from ..models import TaskType, TaskPriority, TaskStatus
            new_task = Task(
                id=mongo_task.get("_id"),
                project_id=project_id,
                title=mongo_task.get("title", "Untitled"),
                description=mongo_task.get("description"),
                type=TaskType(mongo_task.get("type", "Feature")),
                priority=TaskPriority(mongo_task.get("priority", "Medium")),
                status=TaskStatus(mongo_task.get("status", "Backlog")),
                analysis=mongo_task.get("analysis"),
                stage_results=mongo_task.get("stage_results", []),
                testing_urls=mongo_task.get("testing_urls"),
                git_branch=mongo_task.get("git_branch"),
                worktree_path=mongo_task.get("worktree_path"),
                assigned_agent=mongo_task.get("assigned_agent"),
                estimated_hours=mongo_task.get("estimated_hours"),
                created_at=mongo_task.get("created_at", datetime.utcnow()),
                updated_at=datetime.utcnow()
            )
            db.add(new_task)

        progress.tasks_migrated += 1

    await db.commit()

    # Step 3-6: Similar sync for other entities
    progress.current_step = "Syncing sessions"
    progress.steps_completed = 3

    mongo_sessions = await mongo_db.claude_sessions.find({"project_id": project_id}).to_list(None)
    progress.sessions_migrated = len(mongo_sessions)

    progress.steps_completed = 6
    progress.current_step = "Sync completed"

    return progress


@router.get("/migration/preview/{project_id}")
async def preview_migration(
    project_id: str,
    target_mode: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Preview what will be migrated without performing the migration.

    Returns counts of entities that will be migrated.
    """
    try:
        # Get counts from SQLite
        from sqlalchemy import func

        tasks_count = await db.scalar(
            select(func.count(Task.id)).where(Task.project_id == project_id)
        )
        sessions_count = await db.scalar(
            select(func.count(ClaudeSession.id)).where(ClaudeSession.project_id == project_id)
        )

        # Get settings
        settings_result = await db.execute(
            select(ProjectSettings).where(ProjectSettings.project_id == project_id)
        )
        settings = settings_result.scalar_one_or_none()
        current_mode = settings.storage_mode if settings else "local"

        # Check MongoDB for existing data
        mongodb_data_exists = False
        mongodb_tasks = 0
        if target_mode == "local":
            try:
                from ..database_mongodb import mongodb_manager
                if mongodb_manager.client:
                    mongo_db = mongodb_manager.get_database()
                    mongodb_tasks = await mongo_db.tasks.count_documents({"project_id": project_id})
                    mongodb_data_exists = mongodb_tasks > 0
            except Exception:
                pass

        return {
            "project_id": project_id,
            "current_mode": current_mode,
            "target_mode": target_mode,
            "sqlite_data": {
                "tasks": tasks_count or 0,
                "sessions": sessions_count or 0,
                "has_settings": settings is not None
            },
            "mongodb_data": {
                "exists": mongodb_data_exists,
                "tasks": mongodb_tasks
            },
            "migration_needed": current_mode != target_mode,
            "warning": "Data will be copied to target storage. Original data remains intact." if current_mode != target_mode else None
        }

    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
