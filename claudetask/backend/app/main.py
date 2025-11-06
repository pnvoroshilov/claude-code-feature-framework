"""Main FastAPI application"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
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

from .database import get_db, init_db, seed_default_skills, seed_default_mcp_configs
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
from .routers import skills, mcp_configs

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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    await seed_default_skills()
    await seed_default_mcp_configs()


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
            force_reinitialize=request.force_reinitialize
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
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    await db.delete(project)
    await db.commit()
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
            project_id=project_id
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
        
        # If status changed to Analysis, log it for potential notifications
        if status_update.status == TaskStatus.ANALYSIS and old_status != TaskStatus.ANALYSIS:
            logger.info(f"Task {task_id} needs analysis - status changed to Analysis")
        
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
        
        # Auto-create worktree when task moves to In Progress
        if status_update.status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            logger.info(f"Task {task_id} started - creating worktree")
            
            # Get project for context
            project_result = await db.execute(
                select(Project).where(Project.id == task.project_id)
            )
            project = project_result.scalar_one_or_none()
            
            if project:
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
        session_dict = {
            "id": session.id,
            "task_id": session.task_id,
            "task_title": task.title,
            "project_id": session.project_id,
            "status": session.status,
            "working_dir": session.working_dir,
            "context": session.context,
            "messages": session.messages,
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
    
    for field, value in settings_update.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
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
        db_session=db
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)