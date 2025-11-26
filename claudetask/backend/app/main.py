"""Main FastAPI application"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional
from collections import deque
import os
import logging
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from .database import get_db, init_db, seed_default_skills, seed_default_hooks, seed_default_mcp_configs, seed_default_subagents
from .models import Project, Task, TaskHistory, ProjectSettings, Agent, TaskStatus, TaskPriority
from .schemas import (
    ProjectCreate, ProjectInDB, ProjectUpdate,
    TaskCreate, TaskInDB, TaskUpdate, TaskStatusUpdate, TaskAnalysis,
    InitializeProjectRequest, InitializeProjectResponse,
    ConnectionStatus, TaskQueueResponse,
    AgentCreate, AgentInDB, AgentUpdate,
    ProjectSettingsUpdate, ProjectSettingsInDB, MCPTaskStatusUpdateResponse,
    StageResultAppend, TestingUrlsUpdate
)
from .services.mcp_service import mcp_service
from .services.project_service import ProjectService
from .services.git_workflow_service import GitWorkflowService
from .services.claude_session_service import ClaudeSessionService, SessionStatus
from .services.real_claude_service import real_claude_service
from .services.websocket_manager import task_websocket_manager
from .routers import skills, mcp_configs, subagents, editor, instructions, hooks, file_browser, mcp_logs, cloud_storage
from .api import claude_sessions, rag

# Import centralized config for paths
import sys
_claudetask_root = Path(__file__).parent.parent.parent.parent
if str(_claudetask_root) not in sys.path:
    sys.path.insert(0, str(_claudetask_root))
from claudetask.config import get_config
config = get_config()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ClaudeTask API",
    description="Task management framework for Claude Code integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router)
app.include_router(mcp_configs.router)
app.include_router(mcp_configs.search_router)
app.include_router(subagents.router)
app.include_router(hooks.router)
app.include_router(editor.router)
app.include_router(instructions.router)
app.include_router(file_browser.router)
app.include_router(mcp_logs.router)
app.include_router(claude_sessions.router, prefix="/api/claude-sessions", tags=["claude-sessions"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(cloud_storage.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    await seed_default_skills()
    await seed_default_hooks()
    await seed_default_mcp_configs()
    await seed_default_subagents()

    # Initialize MongoDB if configured (optional)
    try:
        if os.getenv("MONGODB_CONNECTION_STRING"):
            from .database_mongodb import mongodb_manager
            await mongodb_manager.connect()
            await mongodb_manager.create_indexes()
            logger.info("MongoDB Atlas initialized successfully")
    except Exception as e:
        logger.warning(f"MongoDB initialization skipped: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Disconnect MongoDB if connected
    try:
        from .database_mongodb import mongodb_manager
        await mongodb_manager.disconnect()
    except Exception:
        pass


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "claudetask-backend"}


# Project endpoints
@app.post("/api/projects/initialize", response_model=InitializeProjectResponse)
async def initialize_project(
    request: InitializeProjectRequest,
    db: AsyncSession = Depends(get_db)
):
    """Initialize a new project with ClaudeTask"""
    try:
        result = await ProjectService.initialize_project(
            db=db,
            project_path=request.project_path,
            project_name=request.project_name,
            github_repo=request.github_repo,
            force_reinitialize=request.force_reinitialize,
            project_mode=request.project_mode or 'simple'
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects", response_model=List[ProjectInDB])
async def get_projects(db: AsyncSession = Depends(get_db)):
    """Get all projects"""
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return projects


@app.get("/api/projects/active", response_model=Optional[ProjectInDB])
async def get_active_project(db: AsyncSession = Depends(get_db)):
    """Get the currently active project"""
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()
    return project


@app.get("/api/projects/{project_id}", response_model=ProjectInDB)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get project by ID"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/api/projects/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for field, value in project_update.dict(exclude_unset=True).items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    return project


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project - uses direct aiosqlite to bypass SQLAlchemy completely"""
    import aiosqlite
    from pathlib import Path

    # Get database path
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / "data" / "claudetask.db"

    # Use direct aiosqlite connection (bypasses ALL SQLAlchemy behavior)
    async with aiosqlite.connect(str(db_path)) as conn:
        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys=ON")

        # Check if project exists
        cursor = await conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,))
        exists = await cursor.fetchone()
        await cursor.close()

        if not exists:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete project - CASCADE DELETE will handle related records
        await conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await conn.commit()

    return {"message": "Project deleted successfully"}


@app.post("/api/projects/{project_id}/activate", response_model=ProjectInDB)
async def activate_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Activate a project (deactivate all others)"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Deactivate all other projects
    all_projects_result = await db.execute(select(Project))
    all_projects = all_projects_result.scalars().all()
    for p in all_projects:
        p.is_active = (p.id == project_id)
    
    await db.commit()
    await db.refresh(project)
    return project


@app.post("/api/projects/{project_id}/update-framework")
async def update_framework(project_id: str, db: AsyncSession = Depends(get_db)):
    """Update framework files in an existing project"""
    # Get project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Update framework files
        from .services.framework_update_service import FrameworkUpdateService
        result = await FrameworkUpdateService.update_framework(
            project_path=project.path,
            project_id=project_id,
            project_mode=project.project_mode or "simple"
        )

        # Sync subagent enabled status based on actual files in project
        if result.get("success"):
            from .services.subagent_service import SubagentService
            subagent_service = SubagentService(db)
            await subagent_service.sync_enabled_subagents_after_framework_update(
                project_id=project_id,
                project_path=project.path
            )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Task endpoints
@app.get("/api/projects/{project_id}/tasks", response_model=List[TaskInDB])
async def get_tasks(
    project_id: str,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get tasks for a project"""
    query = select(Task).where(Task.project_id == project_id)
    
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    
    result = await db.execute(query.order_by(Task.created_at.desc()))
    tasks = result.scalars().all()
    return tasks


@app.post("/api/projects/{project_id}/tasks", response_model=TaskInDB)
async def create_task(
    project_id: str,
    task_create: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task = Task(
        project_id=project_id,
        **task_create.dict(exclude={"project_id"})
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Broadcast task creation event
    await task_websocket_manager.broadcast_task_update(
        project_id=project_id,
        event_type="task_created",
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.type.value if task.type else None,
            "priority": task.priority.value if task.priority else None,
            "status": task.status.value if task.status else None,
            "created_at": task.created_at.isoformat() if task.created_at else None
        }
    )
    
    return task


@app.get("/api/tasks/{task_id}", response_model=TaskInDB)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get task by ID"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=TaskInDB)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Store old status for history
    old_status = task.status
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    # Add to history if status changed
    if task_update.status and task_update.status != old_status:
        history = TaskHistory(
            task_id=task_id,
            old_status=old_status,
            new_status=task_update.status,
            comment=f"Status changed from {old_status.value} to {task_update.status.value}"
        )
        db.add(history)
    
    await db.commit()
    await db.refresh(task)
    
    # Broadcast task update event
    await task_websocket_manager.broadcast_task_update(
        project_id=task.project_id,
        event_type="task_updated",
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.type.value if task.type else None,
            "priority": task.priority.value if task.priority else None,
            "status": task.status.value if task.status else None,
            "analysis": task.analysis,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    )
    
    return task


@app.post("/api/tasks/{task_id}/stage-result", response_model=TaskInDB)
async def append_stage_result(
    task_id: int,
    stage_result: StageResultAppend,
    db: AsyncSession = Depends(get_db)
):
    """Append a new stage result to task's cumulative results"""
    from datetime import datetime
    import json
    
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create new stage result entry
    new_stage_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": stage_result.status,
        "summary": stage_result.summary
    }
    
    # Add details if provided
    if stage_result.details:
        new_stage_result['details'] = stage_result.details
    
    # Get existing stage results or initialize empty list
    current_stage_results = task.stage_results or []
    
    # Append the new result
    current_stage_results.append(new_stage_result)
    
    # Update the task
    task.stage_results = current_stage_results
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"Appended stage result to task {task_id}: {stage_result.status} - {stage_result.summary}")
    
    return task


@app.patch("/api/tasks/{task_id}/testing-urls", response_model=TaskInDB)
async def update_testing_urls(
    task_id: int,
    urls_update: TestingUrlsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update testing URLs for a task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update the testing URLs
    task.testing_urls = urls_update.testing_urls
    task.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"Updated testing URLs for task {task_id}: {urls_update.testing_urls}")
    
    return task


@app.patch("/api/tasks/{task_id}/status", response_model=MCPTaskStatusUpdateResponse)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update task status"""
    try:
        logger.info(f"Updating task {task_id} status to {status_update.status}")
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        old_status = task.status
        task.status = status_update.status
        
        # Add to history
        history = TaskHistory(
            task_id=task_id,
            old_status=old_status,
            new_status=status_update.status,
            comment=status_update.comment or f"Status changed to {status_update.status.value}"
        )
        db.add(history)
        
        # Sync worktree with main if task has a worktree and is transitioning to a new work phase
        sync_statuses = [TaskStatus.IN_PROGRESS, TaskStatus.TESTING, TaskStatus.CODE_REVIEW]
        if (status_update.status in sync_statuses and 
            old_status != status_update.status and 
            task.worktree_path and 
            os.path.exists(task.worktree_path)):
            
            logger.info(f"Syncing worktree for task {task_id} before starting {status_update.status.value} phase")
            
            # Get project for context
            project_result = await db.execute(
                select(Project).where(Project.id == task.project_id)
            )
            project = project_result.scalar_one_or_none()
            
            if project:
                from .services.worktree_service import WorktreeService
                
                sync_result = await WorktreeService.sync_worktree_with_main(
                    worktree_path=task.worktree_path,
                    project_path=project.path
                )
                
                if sync_result["success"]:
                    logger.info(f"Successfully synced worktree for task {task_id}")
                    # Add sync info to history comment
                    history.comment += f" (Worktree synced with latest main)"
                else:
                    logger.warning(f"Failed to sync worktree for task {task_id}: {sync_result.get('error')}")
                    if sync_result.get("conflicts"):
                        # Add warning about conflicts
                        history.comment += f" (WARNING: Merge conflicts detected - manual resolution required)"
        
        # If status changed to Analysis, create worktree and Analyse folder
        if status_update.status == TaskStatus.ANALYSIS and old_status != TaskStatus.ANALYSIS:
            logger.info(f"Task {task_id} needs analysis - status changed to Analysis")

            # Get project for context
            project_result = await db.execute(
                select(Project).where(Project.id == task.project_id)
            )
            project = project_result.scalar_one_or_none()

            # Get project settings to check worktree_enabled
            settings_result = await db.execute(
                select(ProjectSettings).where(ProjectSettings.project_id == task.project_id)
            )
            settings = settings_result.scalar_one_or_none()
            worktree_enabled = settings.worktree_enabled if settings else True

            # Create worktree in development mode with worktrees enabled
            if project and project.project_mode == 'development' and worktree_enabled:
                logger.info(f"Creating worktree for task {task_id} in Analysis phase")
                from .services.worktree_service import WorktreeService

                worktree_result = await WorktreeService.create_worktree(
                    task_id=task_id,
                    project_path=project.path
                )

                if worktree_result["success"]:
                    # Update task with worktree information
                    task.git_branch = worktree_result["branch_name"]
                    task.worktree_path = worktree_result["worktree_path"]
                    logger.info(f"Worktree created for task {task_id}: {worktree_result['branch_name']}")

                    # Now create Analyse folder in the worktree
                    folder_result = await WorktreeService.create_task_folders(
                        worktree_path=task.worktree_path,
                        folder_name="Analyse"
                    )

                    if folder_result["success"]:
                        logger.info(f"Created Analyse folder for task {task_id}: {folder_result['folder_path']}")
                    else:
                        logger.error(f"Failed to create Analyse folder for task {task_id}: {folder_result.get('error')}")
                else:
                    logger.error(f"Failed to create worktree for task {task_id}: {worktree_result.get('error')}")
            elif project and project.project_mode == 'simple':
                logger.info(f"Project in simple mode - skipping worktree creation for task {task_id}")
            elif project and not worktree_enabled:
                logger.info(f"Worktrees disabled - skipping worktree creation for task {task_id}")
        
        # Initialize response data with instructions for next steps
        response_data = {
            "status": status_update.status.value, 
            "comment": status_update.comment,
            "next_steps": []
        }
        
        # Add status-specific instructions
        if status_update.status == TaskStatus.ANALYSIS:
            response_data["next_steps"] = [
                "Analyze task requirements and technical approach",
                "Use mcp:analyze_task to perform detailed analysis",
                "Save analysis with mcp:update_task_analysis",
                "Update status to 'In Progress' when ready to start development"
            ]
        elif status_update.status == TaskStatus.IN_PROGRESS:
            response_data["next_steps"] = [
                "Implement the feature/fix in the worktree",
                "Write tests for your changes",
                "Update documentation if needed",
                "Move to 'Testing' when implementation is complete"
            ]
        elif status_update.status == TaskStatus.TESTING:
            # Create Tests folder if worktree exists
            if old_status != TaskStatus.TESTING and task.worktree_path and os.path.exists(task.worktree_path):
                from .services.worktree_service import WorktreeService

                folder_result = await WorktreeService.create_task_folders(
                    worktree_path=task.worktree_path,
                    folder_name="Tests"
                )

                if folder_result["success"]:
                    logger.info(f"Created Tests folder for task {task_id}: {folder_result['folder_path']}")
                else:
                    logger.error(f"Failed to create Tests folder for task {task_id}: {folder_result.get('error')}")

            response_data["next_steps"] = [
                "Run all test suites",
                "Verify functionality works as expected",
                "Fix any failing tests",
                "Move to 'Code Review' when tests pass"
            ]
        elif status_update.status == TaskStatus.CODE_REVIEW:
            response_data["next_steps"] = [
                "Review code for quality and standards",
                "Check for potential issues",
                "Ensure tests cover edge cases",
                "Move to 'Done' when review is complete"
            ]
        elif status_update.status == TaskStatus.DONE:
            response_data["next_steps"] = [
                "Task completed successfully",
                "Changes will be merged to main branch",
                "Worktree will be cleaned up",
                "You can start working on the next task"
            ]
        elif status_update.status == TaskStatus.BLOCKED:
            response_data["next_steps"] = [
                "Document what is blocking the task",
                "Seek help or clarification",
                "Move back to appropriate status when unblocked"
            ]
        
        # Auto-create worktree when task moves to In Progress ONLY if worktree doesn't already exist
        # (worktree may have been created in Analysis phase)
        if status_update.status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            logger.info(f"Task {task_id} started")

            # Check if worktree already exists
            if task.worktree_path and os.path.exists(task.worktree_path):
                logger.info(f"Worktree already exists for task {task_id}: {task.worktree_path}")
                response_data["worktree"] = {
                    "exists": True,
                    "branch": task.git_branch,
                    "path": task.worktree_path
                }
            else:
                # Get project for context
                project_result = await db.execute(
                    select(Project).where(Project.id == task.project_id)
                )
                project = project_result.scalar_one_or_none()

                # Get project settings to check worktree_enabled
                settings_result = await db.execute(
                    select(ProjectSettings).where(ProjectSettings.project_id == task.project_id)
                )
                settings = settings_result.scalar_one_or_none()
                worktree_enabled = settings.worktree_enabled if settings else True

                # Only create worktree in development mode AND if worktree_enabled is True
                if project and project.project_mode == 'development' and worktree_enabled:
                    logger.info(f"Project in development mode with worktrees enabled - creating worktree for task {task_id}")
                    # Create worktree for the task
                    from .services.worktree_service import WorktreeService

                    worktree_result = await WorktreeService.create_worktree(
                        task_id=task_id,
                        project_path=project.path
                    )

                    if worktree_result["success"]:
                        # Update task with worktree information
                        task.git_branch = worktree_result["branch_name"]
                        task.worktree_path = worktree_result["worktree_path"]
                        logger.info(f"Worktree created for task {task_id}: {worktree_result['branch_name']}")
                        # Add worktree info to response
                        response_data["worktree"] = {
                            "created": True,
                            "branch": worktree_result["branch_name"],
                            "path": worktree_result["worktree_path"]
                        }
                    else:
                        logger.error(f"Failed to create worktree for task {task_id}: {worktree_result.get('error')}")
                        # Check if worktree already exists
                        if "already exists" in str(worktree_result.get("error", "")):
                            response_data["worktree"] = {
                                "exists": True,
                                "branch": task.git_branch,
                                "path": task.worktree_path
                            }
                elif project and project.project_mode == 'development' and not worktree_enabled:
                    logger.info(f"Project in development mode but worktrees disabled - skipping worktree creation for task {task_id}")
                elif project and project.project_mode == 'simple':
                    logger.info(f"Project in simple mode - skipping worktree creation for task {task_id}")
        
        # If status changed to Done, trigger automatic merge and cleanup
        if status_update.status == TaskStatus.DONE and old_status != TaskStatus.DONE:
            if task.git_branch:
                logger.info(f"Task {task_id} marked as Done - triggering automatic merge and cleanup")
                
                # Get project for path
                project_result = await db.execute(
                    select(Project).where(Project.id == task.project_id)
                )
                project = project_result.scalar_one_or_none()
                
                if project:
                    # Trigger merge and cleanup in background
                    merge_result = await GitWorkflowService.merge_and_cleanup(
                        project_path=project.path,
                        task_id=task_id,
                        branch_name=task.git_branch,
                        worktree_path=task.worktree_path,
                        create_pr=False  # Direct merge when marking as Done
                    )
                    
                    if merge_result["success"]:
                        # Clear worktree path if it was removed
                        if merge_result["worktree_removed"]:
                            task.worktree_path = None
                        
                        # Clear git branch if it was deleted  
                        if merge_result["branch_deleted"]:
                            task.git_branch = None
                        
                        logger.info(f"Task {task_id} successfully merged and cleaned up")
                    else:
                        logger.error(f"Failed to merge task {task_id}: {merge_result.get('errors')}")
        
        await db.commit()
        await db.refresh(task)
        
        # Broadcast status change
        await task_websocket_manager.broadcast_task_update(
            project_id=task.project_id,
            event_type="task_status_changed",
            task_data={
                "id": task.id,
                "title": task.title,
                "status": task.status.value if task.status else None,
                "old_status": old_status.value if old_status else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
        )
        
        # Create response with task and instructions
        return MCPTaskStatusUpdateResponse(
            task=task,
            status=status_update.status.value,
            comment=status_update.comment,
            next_steps=response_data["next_steps"],
            worktree=response_data.get("worktree")
        )
    except Exception as e:
        logger.error(f"Error updating task {task_id} status to {status_update.status}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task status: {str(e)}")


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Delete task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project_id = task.project_id
    task_data = {
        "id": task.id,
        "title": task.title
    }
    
    await db.delete(task)
    await db.commit()
    
    # Broadcast task deletion event
    await task_websocket_manager.broadcast_task_update(
        project_id=project_id,
        event_type="task_deleted",
        task_data=task_data
    )
    
    return {"message": "Task deleted successfully"}


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    request: dict = {},
    db: AsyncSession = Depends(get_db)
):
    """Complete a task by merging to main and cleaning up worktree"""
    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.git_branch:
        raise HTTPException(
            status_code=400, 
            detail="Task has no associated git branch"
        )
    
    # Get project for path
    project_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Perform merge and cleanup
    create_pr = request.get("create_pr", False)
    
    merge_result = await GitWorkflowService.merge_and_cleanup(
        project_path=project.path,
        task_id=task_id,
        branch_name=task.git_branch,
        worktree_path=task.worktree_path,
        create_pr=create_pr
    )
    
    if merge_result["success"]:
        # Update task status to Done if merged
        if merge_result["merged"]:
            task.status = TaskStatus.DONE
            
            # Add history entry
            history = TaskHistory(
                task_id=task_id,
                old_status=task.status,
                new_status=TaskStatus.DONE,
                comment=f"Task completed and merged to main"
            )
            db.add(history)
        
        # Clear worktree path if it was removed
        if merge_result["worktree_removed"]:
            task.worktree_path = None
        
        # Clear git branch if it was deleted
        if merge_result["branch_deleted"]:
            task.git_branch = None
        
        await db.commit()
        await db.refresh(task)
    
    return merge_result


# Claude Session endpoints
claude_service = ClaudeSessionService()


@app.post("/api/tasks/{task_id}/session/start")
async def start_claude_session(
    task_id: int,
    request: dict = {},
    db: AsyncSession = Depends(get_db)
):
    """Start a new Claude session for a task"""
    # Get task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get project
    project_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create session
    session_result = await claude_service.create_session(
        task_id=task_id,
        project_path=project.path,
        worktree_path=task.worktree_path,
        initial_context=request.get("context", f"Working on task: {task.title}\n\n{task.description}")
    )
    
    if session_result["success"]:
        # Save to database
        from .models import ClaudeSession
        
        session_data = session_result["session"]
        db_session = ClaudeSession(
            id=session_data["id"],
            task_id=task_id,
            project_id=task.project_id,
            status=session_data["status"],
            working_dir=session_data["working_dir"],
            context=session_data["context"],
            messages=session_data["messages"],
            session_metadata=session_data["metadata"]
        )
        db.add(db_session)
        await db.commit()
        
    return session_result


@app.post("/api/tasks/{task_id}/session/message")
async def send_session_message(
    task_id: int,
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to Claude session"""
    message = request.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    result = await claude_service.send_message(
        task_id=task_id,
        message=message,
        role=request.get("role", "user")
    )
    
    # Update session in database if successful
    if result.get("success"):
        session_data = await claude_service.get_session(task_id)
        if session_data:
            from .models import ClaudeSession
            
            db_result = await db.execute(
                select(ClaudeSession).where(ClaudeSession.task_id == task_id)
            )
            db_session = db_result.scalar_one_or_none()
            
            if db_session:
                db_session.messages = session_data["messages"]
                db_session.session_metadata = session_data["metadata"]
                db_session.updated_at = datetime.utcnow()
                await db.commit()
    
    return result


@app.post("/api/tasks/{task_id}/session/pause")
async def pause_claude_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Pause Claude session"""
    result = await claude_service.pause_session(task_id)
    
    # Update database
    if result.get("success"):
        from .models import ClaudeSession
        
        db_result = await db.execute(
            select(ClaudeSession).where(ClaudeSession.task_id == task_id)
        )
        db_session = db_result.scalar_one_or_none()
        
        if db_session:
            db_session.status = SessionStatus.PAUSED.value
            db_session.updated_at = datetime.utcnow()
            await db.commit()
    
    return result


@app.post("/api/tasks/{task_id}/session/resume")
async def resume_claude_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Resume Claude session"""
    result = await claude_service.resume_session(task_id)
    
    # Update database
    if result.get("success"):
        from .models import ClaudeSession
        
        db_result = await db.execute(
            select(ClaudeSession).where(ClaudeSession.task_id == task_id)
        )
        db_session = db_result.scalar_one_or_none()
        
        if db_session:
            db_session.status = SessionStatus.ACTIVE.value
            db_session.updated_at = datetime.utcnow()
            await db.commit()
    
    return result


@app.get("/api/tasks/{task_id}/session")
async def get_claude_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get Claude session status and messages"""
    from .models import ClaudeSession
    
    db_result = await db.execute(
        select(ClaudeSession).where(ClaudeSession.task_id == task_id)
    )
    db_session = db_result.scalar_one_or_none()
    
    if not db_session:
        # Try to get from memory
        session_data = await claude_service.get_session(task_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="No session found for this task")
        return session_data
    
    return {
        "id": db_session.id,
        "task_id": db_session.task_id,
        "status": db_session.status,
        "messages": db_session.messages or [],
        "metadata": db_session.session_metadata or {},
        "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
        "updated_at": db_session.updated_at.isoformat() if db_session.updated_at else None
    }


@app.get("/api/tasks/{task_id}/session/messages")
async def get_session_messages(
    task_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get Claude session messages"""
    messages = await claude_service.get_session_messages(task_id, limit)
    
    if not messages:
        # Try from database
        from .models import ClaudeSession
        
        db_result = await db.execute(
            select(ClaudeSession).where(ClaudeSession.task_id == task_id)
        )
        db_session = db_result.scalar_one_or_none()
        
        if db_session and db_session.messages:
            messages = db_session.messages[-limit:] if limit else db_session.messages
    
    return {"messages": messages}


# Helper functions for session message retrieval
DEFAULT_MESSAGE_LIMIT = 100  # Default limit for message retrieval


def parse_jsonl_messages(jsonl_path: Path, limit: int = DEFAULT_MESSAGE_LIMIT, _skip_validation: bool = False) -> List[dict]:
    """
    Parse messages from Claude Code JSONL file with security validation.

    Security: All paths are validated to ensure they stay within ~/.claude directory.
    Path traversal attempts are logged and rejected.

    Args:
        jsonl_path: Path to the JSONL file (must be within ~/.claude directory)
        limit: Maximum number of messages to return
        _skip_validation: Skip path validation (INTERNAL USE ONLY - for testing)

    Returns:
        List of message dictionaries with role, content, and timestamp

    Raises:
        ValueError: If path is outside ~/.claude directory (security check)
        FileNotFoundError: If file doesn't exist
    """
    # Security: Validate path is within .claude directory (defense in depth)
    if not _skip_validation:
        try:
            resolved = jsonl_path.resolve()
            claude_base = (Path.home() / ".claude").resolve()
            if not str(resolved).startswith(str(claude_base)):
                logger.error(f"Security: Attempted to parse file outside .claude: {resolved}")
                raise ValueError("Invalid file path - security check failed")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Path validation failed: {e}")
            raise ValueError(f"Path validation failed: {e}")

    # Use deque with maxlen to efficiently keep last N messages
    messages = deque(maxlen=limit)
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entry_type = entry.get("type")

                    if entry_type in ["user", "assistant"]:
                        # Extract content properly
                        content = ""
                        if "message" in entry and isinstance(entry["message"], dict):
                            content = entry["message"].get("content", "")
                        else:
                            content = entry.get("content", "")

                        # Skip empty messages (align with claude_sessions.py:167-175)
                        if not content or (isinstance(content, str) and not content.strip()):
                            continue

                        messages.append({
                            "role": entry_type,
                            "content": content,
                            "timestamp": entry.get("timestamp"),
                        })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSONL line: {e}")
                    continue
    except Exception as e:
        logger.error(f"Failed to read JSONL file {jsonl_path}: {e}")
        raise

    return list(messages)


def get_session_jsonl_path(project_id: str, session_id: str) -> Optional[Path]:
    """
    Construct path to session JSONL file with security validation

    Args:
        project_id: Project identifier (may be a file path)
        session_id: Session identifier

    Returns:
        Path to JSONL file if it exists and is valid, None otherwise
    """
    # Try different path constructions based on project_id format
    claude_projects_dir = Path.home() / ".claude" / "projects"

    # Try with encoded project path (slashes replaced with dashes)
    project_encoded = project_id.replace('/', '-').replace(os.sep, '-')
    jsonl_path = claude_projects_dir / project_encoded / f"{session_id}.jsonl"

    if jsonl_path.exists():
        # Security: Validate path stays within .claude directory
        try:
            resolved = jsonl_path.resolve()
            claude_base = (Path.home() / ".claude").resolve()
            if str(resolved).startswith(str(claude_base)):
                return jsonl_path
            else:
                logger.warning(f"Security: JSONL path {resolved} is outside .claude directory")
        except Exception as e:
            logger.error(f"Failed to resolve JSONL path: {e}")

    return None


# Claude Session endpoints
@app.get("/api/projects/{project_id}/sessions")
async def get_project_sessions(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get all Claude sessions for a project"""
    from .models import ClaudeSession, Task

    result = await db.execute(
        select(ClaudeSession, Task)
        .join(Task, ClaudeSession.task_id == Task.id)
        .where(ClaudeSession.project_id == project_id)
        .order_by(ClaudeSession.created_at.desc())
    )

    sessions = []
    for session, task in result:
        # Try to get messages from JSONL file
        messages = []

        # Try session.id first, then session.session_id
        for sid in [session.id, session.session_id]:
            if sid:
                jsonl_path = get_session_jsonl_path(project_id, sid)
                if jsonl_path:
                    try:
                        messages = parse_jsonl_messages(jsonl_path)
                        logger.info(f"Loaded {len(messages)} messages from JSONL for session {sid}")
                        break  # Found messages, stop searching
                    except Exception as e:
                        logger.warning(f"Failed to parse JSONL for session {sid}: {e}")

        # Fallback to database messages if JSONL not found
        if not messages and session.messages:
            messages = session.messages
            logger.info(f"Using database messages for session {session.id}")

        session_dict = {
            "id": session.id,
            "task_id": session.task_id,
            "task_title": task.title,
            "project_id": session.project_id,
            "status": session.status,
            "working_dir": session.working_dir,
            "context": session.context,
            "messages": messages,  # Now populated from JSONL!
            "session_metadata": session.session_metadata,
            "summary": session.summary,
            "statistics": session.statistics,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
        sessions.append(session_dict)

    return sessions



@app.post("/api/sessions/{task_id}/pause")
async def pause_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Pause a Claude session"""
    from .models import ClaudeSession
    
    result = await db.execute(
        select(ClaudeSession).where(ClaudeSession.task_id == task_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "paused"
    await db.commit()
    
    return {"success": True, "status": "paused"}


@app.post("/api/sessions/{task_id}/resume")
async def resume_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Resume a paused Claude session"""
    from .models import ClaudeSession
    
    result = await db.execute(
        select(ClaudeSession).where(ClaudeSession.task_id == task_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "active"
    await db.commit()
    
    return {"success": True, "status": "active"}


@app.post("/api/sessions/{task_id}/complete")
async def complete_session(task_id: int, db: AsyncSession = Depends(get_db)):
    """Complete a Claude session"""
    from .models import ClaudeSession
    
    result = await db.execute(
        select(ClaudeSession).where(ClaudeSession.task_id == task_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    # Calculate duration
    if session.created_at:
        duration = (session.completed_at - session.created_at).total_seconds() / 60
        if not session.statistics:
            session.statistics = {}
        session.statistics["duration_minutes"] = round(duration, 2)
    
    await db.commit()
    
    return {"success": True, "status": "completed"}


# MCP Integration endpoints
@app.get("/api/mcp/next-task", response_model=Optional[TaskInDB])
async def get_next_task(db: AsyncSession = Depends(get_db)):
    """Get the highest priority task from backlog"""
    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="No active project found")
    
    # Get highest priority task from backlog
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project.id)
        .where(Task.status == TaskStatus.BACKLOG)
        .order_by(
            Task.priority == TaskPriority.HIGH,
            Task.priority == TaskPriority.MEDIUM,
            Task.priority == TaskPriority.LOW,
            Task.created_at
        )
    )
    task = result.scalar_one_or_none()
    return task


@app.get("/api/mcp/tasks/queue", response_model=TaskQueueResponse)
async def get_task_queue(db: AsyncSession = Depends(get_db)):
    """Get task queue status"""
    # Get active project
    result = await db.execute(select(Project).where(Project.is_active == True))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="No active project found")
    
    # Get pending tasks
    pending_result = await db.execute(
        select(Task)
        .where(Task.project_id == project.id)
        .where(Task.status.in_([TaskStatus.BACKLOG, TaskStatus.ANALYSIS]))
    )
    pending_tasks = pending_result.scalars().all()
    
    # Get in progress tasks
    progress_result = await db.execute(
        select(Task)
        .where(Task.project_id == project.id)
        .where(Task.status.in_([TaskStatus.IN_PROGRESS, TaskStatus.TESTING, TaskStatus.CODE_REVIEW]))
    )
    in_progress_tasks = progress_result.scalars().all()
    
    # Get completed today count
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    completed_result = await db.execute(
        select(Task)
        .where(Task.project_id == project.id)
        .where(Task.status == TaskStatus.DONE)
        .where(Task.completed_at >= today)
    )
    completed_today = len(completed_result.scalars().all())
    
    return TaskQueueResponse(
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_today=completed_today
    )


@app.get("/api/mcp/connection", response_model=ConnectionStatus)
async def verify_connection(db: AsyncSession = Depends(get_db)):
    """Verify MCP connection and get project status"""
    try:
        # Get active project
        result = await db.execute(select(Project).where(Project.is_active == True))
        project = result.scalar_one_or_none()
        
        if not project:
            return ConnectionStatus(
                connected=False,
                error="No active project found"
            )
        
        # Get tasks count
        tasks_result = await db.execute(
            select(Task).where(Task.project_id == project.id)
        )
        tasks_count = len(tasks_result.scalars().all())
        
        # Get active task
        active_result = await db.execute(
            select(Task)
            .where(Task.project_id == project.id)
            .where(Task.status == TaskStatus.IN_PROGRESS)
        )
        active_task = active_result.scalar_one_or_none()
        
        return ConnectionStatus(
            connected=True,
            project_name=project.name,
            project_path=project.path,
            tasks_count=tasks_count,
            active_task=active_task
        )
    
    except Exception as e:
        return ConnectionStatus(
            connected=False,
            error=str(e)
        )



# Agent endpoints
@app.get("/api/projects/{project_id}/agents", response_model=List[AgentInDB])
async def get_agents(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get agents for a project"""
    result = await db.execute(
        select(Agent)
        .where(Agent.project_id == project_id)
        .where(Agent.is_active == True)
    )
    agents = result.scalars().all()
    return agents


@app.post("/api/projects/{project_id}/agents", response_model=AgentInDB)
async def create_agent(
    project_id: str,
    agent_create: AgentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""
    agent = Agent(
        project_id=project_id,
        **agent_create.dict(exclude={"project_id"})
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


# Project Settings endpoints
@app.get("/api/projects/{project_id}/settings", response_model=ProjectSettingsInDB)
async def get_project_settings(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get project settings"""
    result = await db.execute(
        select(ProjectSettings).where(ProjectSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Project settings not found")
    return settings


@app.patch("/api/projects/{project_id}/settings", response_model=ProjectSettingsInDB)
async def update_project_settings(
    project_id: str,
    settings_update: ProjectSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update project settings"""
    result = await db.execute(
        select(ProjectSettings).where(ProjectSettings.project_id == project_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise HTTPException(status_code=404, detail="Project settings not found")

    # Track if worktree_enabled changed
    worktree_changed = False
    old_worktree_enabled = settings.worktree_enabled

    for field, value in settings_update.dict(exclude_unset=True).items():
        if field == "worktree_enabled" and value != old_worktree_enabled:
            worktree_changed = True
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)

    # If worktree_enabled changed, regenerate CLAUDE.md
    if worktree_changed:
        try:
            # Get project to regenerate CLAUDE.md
            project_result = await db.execute(
                select(Project).where(Project.id == project_id)
            )
            project = project_result.scalar_one_or_none()

            if project:
                logger.info(f"Regenerating CLAUDE.md for project {project_id} due to worktree_enabled change")
                await ProjectService.regenerate_claude_md(db, project_id)
        except Exception as e:
            logger.error(f"Failed to regenerate CLAUDE.md: {e}")
            # Don't fail the request if regeneration fails

    # Broadcast settings update via WebSocket
    await task_websocket_manager.broadcast_message({
        "type": "project_settings_updated",
        "project_id": project_id,
        "settings": {
            "worktree_enabled": settings.worktree_enabled,
            "auto_mode": settings.auto_mode,
            "max_parallel_tasks": settings.max_parallel_tasks
        }
    })

    return settings


# Embedded Claude Mode endpoints
@app.post("/api/sessions/launch/embedded")
async def launch_embedded_claude_session(request: dict, db: AsyncSession = Depends(get_db)):
    """Launch or reconnect to embedded Claude session for a task"""
    task_id = request.get("task_id")
    
    # Get task details
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Check for existing active session first
    from .services.real_claude_service import real_claude_service
    
    # Log all active sessions for debugging
    logger.info(f"Checking for existing sessions. Total active: {len(real_claude_service.sessions)}")
    for sid, sess in real_claude_service.sessions.items():
        logger.info(f"  Session {sid}: task_id={sess.task_id}, is_running={sess.is_running}")
    
    # Look for existing session in service
    for session_id, session in real_claude_service.sessions.items():
        if session.task_id == task_id and session.is_running:
            logger.info(f"Found existing active session for task {task_id}: {session_id}")
            return {
                "success": True,
                "session_id": session_id,
                "working_dir": session.working_dir,
                "mode": "embedded",
                "message": "Reconnected to existing Claude session",
                "info": {
                    "pid": session.child.pid if session.child else None,
                    "working_dir": session.working_dir
                }
            }
    
    logger.info(f"No existing session found for task {task_id}, creating new one")
    
    # Get project
    project_result = await db.execute(select(Project).where(Project.id == task.project_id))
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found")

    # Get project mode from project (not settings)
    project_mode = project.project_mode if project.project_mode else "simple"

    # Determine working directory
    working_dir = task.worktree_path or project.path

    # Create new session configuration
    import uuid
    session_id = f"claude-task-{task_id}-{uuid.uuid4().hex[:8]}"

    # Start embedded process
    # Pass both the worktree path and the root project path
    result = await real_claude_service.create_session(
        task_id=task_id,
        project_path=working_dir,  # This is the worktree path
        session_id=session_id,
        root_project_path=project.path,  # Root project directory with .claude
        db_session=db,
        project_mode=project_mode  # Pass project mode
    )
    
    if result["success"]:
        # Create or update session record
        from .models import ClaudeSession
        
        # Check if session already exists in DB
        existing_result = await db.execute(
            select(ClaudeSession).where(ClaudeSession.task_id == task_id)
        )
        existing_session = existing_result.scalar_one_or_none()
        
        if existing_session:
            # Update existing session
            existing_session.session_id = session_id
            existing_session.status = "active"
            existing_session.working_dir = working_dir
            existing_session.mode = "embedded"
        else:
            # Create new session
            db_session = ClaudeSession(
                id=f"embedded-{session_id}",
                session_id=session_id,
                task_id=task_id,
                project_id=task.project_id,
                status="active",
                mode="embedded",
                working_dir=working_dir
            )
            db.add(db_session)
        
        await db.commit()
        
        return {
            "success": True,
            "session_id": session_id,
            "working_dir": working_dir,
            "mode": "embedded",
            "message": "Embedded Claude session started successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start embedded Claude session")


@app.post("/api/sessions/embedded/{session_id}/input")
async def send_input_to_embedded_session(session_id: str, request: dict):
    """Send input to an embedded Claude session"""
    user_input = request.get("input", "")
    
    from .services.real_claude_service import real_claude_service
    
    success = await real_claude_service.send_input(session_id, user_input)
    
    if success:
        return {"success": True, "message": "Input sent successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found or not running")


@app.post("/api/sessions/embedded/{session_id}/key")
async def send_key_to_embedded_session(session_id: str, request: dict):
    """Send special key to an embedded Claude session (arrow keys, enter, escape, etc.)"""
    key = request.get("key", "")
    
    from .services.real_claude_service import real_claude_service
    
    success = await real_claude_service.send_input(session_id, key)
    
    if success:
        return {"success": True, "message": f"Key {key} sent successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found or not running")


@app.get("/api/sessions/embedded/{session_id}/stream")
async def stream_embedded_session_messages(session_id: str):
    """Stream messages from an embedded Claude session"""
    from .services.real_claude_service import real_claude_service
    
    # Check if session exists
    session = real_claude_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def generate_messages():
        async for message in session.stream_messages():
            # Convert message object to dict
            message_dict = message.__dict__ if hasattr(message, '__dict__') else message
            # Skip heartbeat messages for the stream
            if isinstance(message_dict, dict) and message_dict.get("type") != "heartbeat":
                yield f"data: {json.dumps(message_dict)}\n\n"
    
    return StreamingResponse(
        generate_messages(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@app.post("/api/sessions/embedded/{session_id}/stop")
async def stop_embedded_session(session_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Stop an embedded Claude session"""
    try:
        from .services.real_claude_service import real_claude_service
        from .models import ClaudeSession
        
        logger.info(f"Stopping embedded session: {session_id}")
        
        # Update database immediately to mark as stopping
        try:
            result = await db.execute(
                select(ClaudeSession).where(ClaudeSession.session_id == session_id)
            )
            db_session = result.scalar_one_or_none()
            
            if db_session:
                db_session.status = "inactive"
                db_session.completed_at = datetime.utcnow()
                await db.commit()
                logger.info(f"Database updated: session {session_id} marked as inactive")
        except Exception as db_error:
            logger.error(f"Database error when stopping session: {db_error}")
        
        # Stop the actual session in the background to not block
        async def stop_session_background():
            try:
                # Very short timeout to not block
                await asyncio.wait_for(
                    real_claude_service.stop_session(session_id),
                    timeout=0.5  # 0.5 second timeout
                )
                logger.info(f"Session {session_id} stopped successfully")
            except asyncio.TimeoutError:
                logger.warning(f"Session {session_id} stop timed out, forcing cleanup")
                # Force remove from sessions dict
                if session_id in real_claude_service.sessions:
                    del real_claude_service.sessions[session_id]
            except Exception as e:
                logger.error(f"Error stopping session {session_id}: {e}")
                # Force remove from sessions dict anyway
                if session_id in real_claude_service.sessions:
                    del real_claude_service.sessions[session_id]
        
        # Add to background tasks
        background_tasks.add_task(stop_session_background)
        
        return {"success": True, "status": "inactive"}
    except Exception as e:
        logger.error(f"Failed to stop embedded session {session_id}: {e}")
        return {"success": True, "error": str(e), "status": "inactive"}


@app.get("/api/sessions/embedded/status")
async def get_embedded_sessions_status():
    """Get status of all embedded sessions"""
    from .services.real_claude_service import real_claude_service
    
    running_sessions = real_claude_service.get_active_sessions()
    
    return {
        "running_sessions": running_sessions,
        "total_running": len(running_sessions)
    }




@app.get("/api/pick-folder")
async def pick_folder_native():
    """Open native folder picker dialog on server"""
    try:
        from .services.folder_picker_service import folder_picker
        
        # Open native folder picker
        selected_path = folder_picker.pick_folder_sync()
        
        if selected_path:
            folder_name = Path(selected_path).name
            return {
                "success": True,
                "path": selected_path,
                "name": folder_name
            }
        else:
            return {
                "success": False,
                "message": "No folder selected"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to open folder picker. Please enter path manually."
        }


@app.post("/api/browse-directory")
async def browse_directory(request: dict):
    """Browse directory and return subdirectories"""
    try:
        path = request.get("path", "")
        
        # If no path provided, use home directory
        if not path:
            path = str(Path.home())
        
        path_obj = Path(path)
        
        # Check if path exists and is a directory
        if not path_obj.exists():
            return {"error": "Path does not exist", "path": path}
        
        if not path_obj.is_dir():
            return {"error": "Path is not a directory", "path": path}
        
        # Get subdirectories
        directories = []
        try:
            for item in path_obj.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    directories.append({
                        "name": item.name,
                        "path": str(item.absolute()),
                        "is_git": (item / ".git").exists()
                    })
        except PermissionError:
            return {"error": "Permission denied", "path": path}
        
        # Sort directories by name
        directories.sort(key=lambda x: x["name"].lower())
        
        return {
            "current_path": str(path_obj.absolute()),
            "parent_path": str(path_obj.parent.absolute()) if path_obj != path_obj.parent else None,
            "directories": directories[:50],  # Limit to 50 directories
            "home_path": str(Path.home())
        }
    except Exception as e:
        return {"error": str(e), "path": path}


@app.websocket("/api/sessions/embedded/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time Claude terminal streaming"""
    from .services.real_claude_service import real_claude_service
    
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    # Get the session
    session = real_claude_service.get_session(session_id)
    if not session:
        await websocket.send_json({
            "type": "error",
            "content": "Session not found"
        })
        await websocket.close()
        return
    
    # Add WebSocket to session for real-time updates
    session.add_websocket_client(websocket)
    
    try:
        while True:
            # Receive commands from WebSocket
            data = await websocket.receive_json()
            command_type = data.get("type")
            
            if command_type == "input":
                # Send input to Claude
                user_input = data.get("content", "")
                await session.send_input(user_input)
                
            elif command_type == "key":
                # Send special key
                key = data.get("key", "")
                await session.send_input(key)
                
            elif command_type == "ping":
                # Respond to ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        session.remove_websocket_client(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        session.remove_websocket_client(websocket)
        try:
            await websocket.close()
        except:
            pass


@app.get("/api/sessions/embedded/active")
async def get_active_embedded_sessions():
    """Get all active embedded Claude sessions"""
    return {
        "sessions": real_claude_service.get_active_sessions()
    }


@app.get("/api/sessions/embedded/{session_id}/info")
async def get_embedded_session_info(session_id: str):
    """Get information about a specific embedded session"""
    from .services.real_claude_service import real_claude_service
    
    session = real_claude_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "task_id": session.task_id,
        "is_running": session.is_running,
        "working_dir": session.working_dir,
        "clients": len(session.websocket_clients)
    }


@app.get("/api/sessions/embedded/{session_id}/history")
async def get_embedded_session_history(session_id: str, limit: Optional[int] = None):
    """Get message history for an embedded session"""
    from .services.real_claude_service import real_claude_service
    
    session = real_claude_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": []
    }


@app.websocket("/api/projects/{project_id}/tasks/ws")
async def task_websocket_endpoint(websocket: WebSocket, project_id: str, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time task updates"""
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        await websocket.close(code=1008, reason="Project not found")
        return
    
    # Connect the WebSocket
    await task_websocket_manager.connect(websocket, project_id)
    
    try:
        while True:
            # Receive and handle messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "ping":
                await task_websocket_manager.handle_ping(websocket)
            elif message_type == "subscribe":
                # Already subscribed to project tasks
                await websocket.send_json({
                    "type": "subscribed",
                    "project_id": project_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                logger.warning(f"Unknown WebSocket message type: {message_type}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error for project {project_id}: {e}")
    finally:
        await task_websocket_manager.disconnect(websocket)


@app.get("/api/projects/{project_id}/tasks/ws/status")
async def get_websocket_status(project_id: str):
    """Get WebSocket connection status for a project"""
    return {
        "project_id": project_id,
        "connected_clients": task_websocket_manager.get_connection_count(project_id),
        "total_connections": task_websocket_manager.get_connection_count(),
        "connected_projects": task_websocket_manager.get_connected_projects()
    }


# ==========================
# Memory Management Endpoints
# ==========================

@app.post("/api/projects/{project_id}/memory/messages")
async def save_conversation_message(
    project_id: str,
    message: dict,
    db: AsyncSession = Depends(get_db)
):
    """Save a conversation message to project memory"""
    from sqlalchemy import text
    import json
    from datetime import datetime

    try:
        # Insert message into database
        query = text("""
            INSERT INTO conversation_memory
            (project_id, session_id, task_id, message_type, content, timestamp, metadata)
            VALUES (:project_id, :session_id, :task_id, :message_type, :content, :timestamp, :metadata)
        """)

        result = await db.execute(query, {
            "project_id": project_id,
            "session_id": message.get("session_id"),
            "task_id": message.get("task_id"),
            "message_type": message["message_type"],
            "content": message["content"],
            "timestamp": datetime.utcnow(),
            "metadata": json.dumps(message.get("metadata", {}))
        })

        await db.commit()

        # Get the inserted ID
        message_id = result.lastrowid

        # Index in RAG asynchronously
        try:
            # Import with absolute path from project root
            import sys
            from pathlib import Path
            mcp_path = Path(__file__).parent.parent.parent / "mcp_server"
            if str(mcp_path) not in sys.path:
                sys.path.insert(0, str(mcp_path))

            from rag.rag_service import RAGService, RAGConfig

            # Initialize RAG service with centralized config path
            rag_config = RAGConfig(
                chromadb_path=str(config.chromadb_dir)
            )
            rag_service = RAGService(rag_config)
            await rag_service.initialize()

            # Index the message with full metadata
            message_metadata = {
                "message_type": message.get("message_type", "unknown"),
                "session_id": message.get("session_id"),
                "task_id": message.get("task_id"),
                **message.get("metadata", {})
            }
            await rag_service.index_conversation_message(
                project_id=project_id,
                message_id=message_id,
                content=message["content"],
                metadata=message_metadata
            )
            logger.info(f"Message {message_id} indexed in RAG for project {project_id[:8]}")
        except ImportError as ie:
            logger.warning(f"RAG module not available: {ie}")
        except Exception as rag_error:
            logger.warning(f"RAG indexing failed for message {message_id}: {rag_error}")
            # Don't fail the request if RAG indexing fails

        return {"id": message_id, "status": "saved"}

    except Exception as e:
        logger.error(f"Failed to save conversation message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/summary")
async def get_project_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get project summary"""
    from sqlalchemy import text

    try:
        query = text("""
            SELECT summary, key_decisions, tech_stack, patterns, gotchas, last_updated
            FROM project_summaries
            WHERE project_id = :project_id
        """)

        result = await db.execute(query, {"project_id": project_id})
        row = result.first()

        if row:
            return {
                "summary": row.summary,
                "key_decisions": json.loads(row.key_decisions) if row.key_decisions else [],
                "tech_stack": json.loads(row.tech_stack) if row.tech_stack else [],
                "patterns": json.loads(row.patterns) if row.patterns else [],
                "gotchas": json.loads(row.gotchas) if row.gotchas else [],
                "last_updated": row.last_updated.isoformat() if row.last_updated and hasattr(row.last_updated, 'isoformat') else str(row.last_updated) if row.last_updated else None
            }
        else:
            # Create initial summary if not exists
            insert_query = text("""
                INSERT INTO project_summaries
                (project_id, summary, key_decisions, tech_stack, patterns, gotchas)
                VALUES (:project_id, :summary, '[]', '[]', '[]', '[]')
            """)

            await db.execute(insert_query, {
                "project_id": project_id,
                "summary": "Project initialized. No summary available yet."
            })
            await db.commit()

            return {
                "summary": "Project initialized. No summary available yet.",
                "key_decisions": [],
                "tech_stack": [],
                "patterns": [],
                "gotchas": [],
                "last_updated": None
            }

    except Exception as e:
        logger.error(f"Failed to get project summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/messages")
async def get_conversation_messages(
    project_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get conversation messages for a project"""
    from sqlalchemy import text

    try:
        query = text("""
            SELECT id, session_id, task_id, message_type, content, timestamp, metadata
            FROM conversation_memory
            WHERE project_id = :project_id
            ORDER BY timestamp DESC
            LIMIT :limit OFFSET :offset
        """)

        result = await db.execute(query, {
            "project_id": project_id,
            "limit": limit,
            "offset": offset
        })

        messages = []
        for row in result:
            messages.append({
                "id": row.id,
                "session_id": row.session_id,
                "task_id": row.task_id,
                "message_type": row.message_type,
                "content": row.content,
                "timestamp": row.timestamp.isoformat() if row.timestamp and hasattr(row.timestamp, 'isoformat') else str(row.timestamp) if row.timestamp else None,
                "metadata": json.loads(row.metadata) if row.metadata else {}
            })

        return messages

    except Exception as e:
        logger.error(f"Failed to get conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects/{project_id}/memory/summary/update")
async def update_project_summary(
    project_id: str,
    update_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update project summary with new insights"""
    from sqlalchemy import text
    from datetime import datetime

    try:
        trigger = update_data["trigger"]
        new_insights = update_data["new_insights"]
        # Optional: update last_summarized_message_id if provided
        last_message_id = update_data.get("last_summarized_message_id")

        # Get current summary
        query = text("SELECT summary FROM project_summaries WHERE project_id = :project_id")
        result = await db.execute(query, {"project_id": project_id})
        row = result.first()

        if row:
            # Update existing summary
            current_summary = row.summary or ""

            # Simple append for now - in production would use Claude for intelligent merge
            updated_summary = f"{current_summary}\n\n[{datetime.utcnow().isoformat()}] {trigger}:\n{new_insights}"

            # Limit to ~5 pages (15000 chars)
            if len(updated_summary) > 15000:
                updated_summary = updated_summary[-15000:]

            if last_message_id:
                update_query = text("""
                    UPDATE project_summaries
                    SET summary = :summary, last_updated = :last_updated, version = version + 1,
                        last_summarized_message_id = :last_message_id
                    WHERE project_id = :project_id
                """)
                await db.execute(update_query, {
                    "project_id": project_id,
                    "summary": updated_summary,
                    "last_updated": datetime.utcnow(),
                    "last_message_id": last_message_id
                })
            else:
                update_query = text("""
                    UPDATE project_summaries
                    SET summary = :summary, last_updated = :last_updated, version = version + 1
                    WHERE project_id = :project_id
                """)
                await db.execute(update_query, {
                    "project_id": project_id,
                    "summary": updated_summary,
                    "last_updated": datetime.utcnow()
                })
        else:
            # Create new summary
            if last_message_id:
                insert_query = text("""
                    INSERT INTO project_summaries
                    (project_id, summary, key_decisions, tech_stack, patterns, gotchas, last_updated, last_summarized_message_id)
                    VALUES (:project_id, :summary, '[]', '[]', '[]', '[]', :last_updated, :last_message_id)
                """)
                await db.execute(insert_query, {
                    "project_id": project_id,
                    "summary": new_insights,
                    "last_updated": datetime.utcnow(),
                    "last_message_id": last_message_id
                })
            else:
                insert_query = text("""
                    INSERT INTO project_summaries
                    (project_id, summary, key_decisions, tech_stack, patterns, gotchas, last_updated)
                    VALUES (:project_id, :summary, '[]', '[]', '[]', '[]', :last_updated)
                """)
                await db.execute(insert_query, {
                    "project_id": project_id,
                    "summary": new_insights,
                    "last_updated": datetime.utcnow()
                })

        await db.commit()
        return {"status": "updated", "trigger": trigger}

    except Exception as e:
        logger.error(f"Failed to update project summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test/memory-search")
async def test_memory_search():
    """Test endpoint to verify search works"""
    return {"status": "ok", "message": "Search endpoint test works!"}

@app.get("/api/projects/{project_id}/memory/stats")
async def get_memory_stats(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get memory statistics for a project"""
    from sqlalchemy import text

    try:
        # Count messages
        count_query = text("""
            SELECT COUNT(*) as total_messages
            FROM conversation_memory
            WHERE project_id = :project_id
        """)

        result = await db.execute(count_query, {"project_id": project_id})
        count = result.first().total_messages

        # Get summary info
        summary_query = text("""
            SELECT last_updated, version
            FROM project_summaries
            WHERE project_id = :project_id
        """)

        summary_result = await db.execute(summary_query, {"project_id": project_id})
        summary_row = summary_result.first()

        return {
            "total_messages": count,
            "summary_last_updated": summary_row.last_updated.isoformat() if summary_row and summary_row.last_updated and hasattr(summary_row.last_updated, 'isoformat') else str(summary_row.last_updated) if summary_row and summary_row.last_updated else None,
            "summary_version": summary_row.version if summary_row else 0,
            "status": "active"
        }

    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/should-summarize")
async def should_summarize(
    project_id: str,
    threshold: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Check if project needs summarization (messages since last summary >= threshold)"""
    from sqlalchemy import text

    try:
        # Get last summarized message id from project_summaries
        summary_query = text("""
            SELECT last_summarized_message_id, last_updated
            FROM project_summaries
            WHERE project_id = :project_id
        """)
        summary_result = await db.execute(summary_query, {"project_id": project_id})
        summary_row = summary_result.first()

        last_summarized_id = summary_row.last_summarized_message_id if summary_row and summary_row.last_summarized_message_id else 0

        # Count messages since last summarization
        if last_summarized_id > 0:
            count_query = text("""
                SELECT COUNT(*) as count
                FROM conversation_memory
                WHERE project_id = :project_id AND id > :last_id
            """)
            result = await db.execute(count_query, {"project_id": project_id, "last_id": last_summarized_id})
        else:
            count_query = text("""
                SELECT COUNT(*) as count
                FROM conversation_memory
                WHERE project_id = :project_id
            """)
            result = await db.execute(count_query, {"project_id": project_id})

        messages_since = result.first().count
        should_run = messages_since >= threshold

        return {
            "should_summarize": should_run,
            "messages_since_last_summary": messages_since,
            "threshold": threshold,
            "last_summarized_message_id": last_summarized_id
        }

    except Exception as e:
        logger.error(f"Failed to check summarization status: {e}")
        # On error, don't block - return false
        return {
            "should_summarize": False,
            "messages_since_last_summary": 0,
            "threshold": threshold,
            "error": str(e)
        }


@app.post("/api/projects/{project_id}/memory/rebuild-index")
async def rebuild_memory_index(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Rebuild the RAG index for project memory from existing messages"""
    from sqlalchemy import text

    try:
        logger.info(f"Rebuilding memory index for project {project_id}")

        # Get all messages for this project
        query = text("""
            SELECT id, session_id, task_id, message_type, content, timestamp, metadata
            FROM conversation_memory
            WHERE project_id = :project_id
            ORDER BY timestamp ASC
        """)

        result = await db.execute(query, {"project_id": project_id})

        messages = []
        for row in result:
            messages.append({
                "id": row.id,
                "session_id": row.session_id,
                "task_id": row.task_id,
                "message_type": row.message_type,
                "content": row.content,
                "timestamp": row.timestamp.isoformat() if row.timestamp and hasattr(row.timestamp, 'isoformat') else str(row.timestamp) if row.timestamp else None,
                "metadata": json.loads(row.metadata) if row.metadata else {}
            })

        if not messages:
            return {"status": "no_messages", "message": "No messages found to index"}

        # Initialize RAG service
        import sys
        from pathlib import Path
        mcp_path = Path(__file__).parent.parent.parent / "mcp_server"
        if str(mcp_path) not in sys.path:
            sys.path.insert(0, str(mcp_path))

        from rag.rag_service import RAGService, RAGConfig

        rag_config = RAGConfig(
            chromadb_path=str(config.chromadb_dir)
        )
        rag_service = RAGService(rag_config)
        await rag_service.initialize()

        # Rebuild the index
        await rag_service.rebuild_memory_index(project_id, messages)

        logger.info(f"Rebuilt memory index with {len(messages)} messages for project {project_id[:8]}")

        return {
            "status": "success",
            "messages_indexed": len(messages),
            "project_id": project_id
        }

    except Exception as e:
        logger.error(f"Failed to rebuild memory index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/search2")
async def search_memories_v2(
    project_id: str,
    query: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Simple memory search without RAG"""
    from sqlalchemy import text

    try:
        logger.info(f"Memory search v2 for project {project_id}: {query}")

        sql = text("""
            SELECT id, message_type, content, timestamp, metadata
            FROM conversation_memory
            WHERE project_id = :project_id
            AND content LIKE :pattern
            ORDER BY timestamp DESC
            LIMIT :limit
        """)

        result = await db.execute(
            sql,
            {"project_id": project_id, "pattern": f"%{query}%", "limit": limit}
        )

        messages = []
        for row in result:
            messages.append({
                "id": row.id,
                "message_type": row.message_type,
                "content": row.content,
                "timestamp": str(row.timestamp) if row.timestamp else None,
                "metadata": json.loads(row.metadata) if row.metadata else {},
                "score": 0.5
            })

        return messages

    except Exception as e:
        logger.error(f"Search v2 failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/search")
async def search_project_memories(
    project_id: str,
    query: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search project memories using RAG semantic search"""
    try:
        logger.info(f"Searching memories for project {project_id}: {query}")

        # Try RAG service first
        try:
            # Import with absolute path from project root
            import sys
            from pathlib import Path
            mcp_path = Path(__file__).parent.parent.parent / "mcp_server"
            if str(mcp_path) not in sys.path:
                sys.path.insert(0, str(mcp_path))

            from rag.rag_service import RAGService, RAGConfig

            # Initialize RAG service with centralized config path
            rag_config = RAGConfig(
                chromadb_path=str(config.chromadb_dir)
            )
            rag_service = RAGService(rag_config)
            await rag_service.initialize()

            # Perform semantic search
            results = await rag_service.search_memories(
                project_id=project_id,
                query=query,
                limit=limit
            )

            logger.info(f"Found {len(results)} results for query: {query}")
            return results

        except Exception as rag_error:
            logger.warning(f"RAG service not available: {rag_error}, falling back to text search")

            # Fallback to simple text search - use raw SQL to avoid import issues
            search_query = """
                SELECT id, message_type, content, timestamp, metadata
                FROM conversation_memory
                WHERE project_id = :project_id
                AND content LIKE :pattern
                ORDER BY timestamp DESC
                LIMIT :limit
            """

            # Use raw execute without text() wrapper
            from sqlalchemy import text as sql_text
            result = await db.execute(
                sql_text(search_query),
                {
                    "project_id": project_id,
                    "pattern": f"%{query}%",
                    "limit": limit
                }
            )

            messages = []
            for row in result:
                messages.append({
                    "id": row.id,
                    "message_type": row.message_type,
                    "content": row.content,
                    "timestamp": row.timestamp.isoformat() if row.timestamp and hasattr(row.timestamp, 'isoformat') else str(row.timestamp),
                    "metadata": json.loads(row.metadata) if row.metadata else {},
                    "score": 0.5  # Default score for text search
                })

            return messages

    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/sessions/current")
async def get_current_session(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent session ID for a project"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT session_id, MAX(timestamp) as last_activity
            FROM conversation_memory
            WHERE project_id = :project_id
            AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY last_activity DESC
            LIMIT 1
        """)

        result = await db.execute(sql, {"project_id": project_id})
        row = result.fetchone()

        if row:
            return {
                "session_id": row.session_id,
                "last_activity": str(row.last_activity)
            }
        else:
            return {"session_id": None, "message": "No sessions found"}

    except Exception as e:
        logger.error(f"Failed to get current session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/sessions/last")
async def get_last_session(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the previous (second most recent) session ID for a project"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT session_id, MAX(timestamp) as last_activity
            FROM conversation_memory
            WHERE project_id = :project_id
            AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY last_activity DESC
            LIMIT 2
        """)

        result = await db.execute(sql, {"project_id": project_id})
        rows = result.fetchall()

        if len(rows) >= 2:
            # Return second most recent session
            return {
                "session_id": rows[1].session_id,
                "last_activity": str(rows[1].last_activity)
            }
        elif len(rows) == 1:
            # Only one session exists, return it
            return {
                "session_id": rows[0].session_id,
                "last_activity": str(rows[0].last_activity),
                "message": "Only one session exists"
            }
        else:
            return {"session_id": None, "message": "No sessions found"}

    except Exception as e:
        logger.error(f"Failed to get last session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/sessions")
async def list_sessions(
    project_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """List all sessions for a project with message counts"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT
                session_id,
                MIN(timestamp) as start_time,
                MAX(timestamp) as end_time,
                COUNT(*) as message_count
            FROM conversation_memory
            WHERE project_id = :project_id
            AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY end_time DESC
            LIMIT :limit
        """)

        result = await db.execute(sql, {"project_id": project_id, "limit": limit})
        rows = result.fetchall()

        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row.session_id,
                "start_time": str(row.start_time),
                "end_time": str(row.end_time),
                "message_count": row.message_count
            })

        return {"sessions": sessions, "total": len(sessions)}

    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}/memory/sessions/{session_id}/messages")
async def get_session_messages(
    project_id: str,
    session_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a specific session"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT id, message_type, content, timestamp, metadata
            FROM conversation_memory
            WHERE project_id = :project_id
            AND session_id = :session_id
            ORDER BY timestamp ASC
            LIMIT :limit
        """)

        result = await db.execute(sql, {
            "project_id": project_id,
            "session_id": session_id,
            "limit": limit
        })
        rows = result.fetchall()

        messages = []
        for row in rows:
            messages.append({
                "id": row.id,
                "message_type": row.message_type,
                "content": row.content,
                "timestamp": str(row.timestamp),
                "metadata": json.loads(row.metadata) if row.metadata else {}
            })

        return {"messages": messages, "total": len(messages), "session_id": session_id}

    except Exception as e:
        logger.error(f"Failed to get session messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for frontend
frontend_build_path = Path(__file__).parent.parent.parent / "frontend" / "build"
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")
    logger.info(f"Serving frontend from: {frontend_build_path}")
else:
    logger.warning(f"Frontend build directory not found: {frontend_build_path}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)