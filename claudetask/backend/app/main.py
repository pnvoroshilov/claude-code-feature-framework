"""Main FastAPI application"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import os
import logging

from .database import get_db, init_db
from .models import Project, Task, TaskHistory, ProjectSettings, Agent, TaskStatus, TaskPriority
from .schemas import (
    ProjectCreate, ProjectInDB, ProjectUpdate,
    TaskCreate, TaskInDB, TaskUpdate, TaskStatusUpdate, TaskAnalysis,
    InitializeProjectRequest, InitializeProjectResponse,
    ConnectionStatus, TaskQueueResponse,
    AgentCreate, AgentInDB, AgentUpdate,
    ProjectSettingsUpdate, ProjectSettingsInDB
)
from .services.mcp_service import mcp_service
from .services.project_service import ProjectService
from .services.git_workflow_service import GitWorkflowService
from .services.claude_session_service import ClaudeSessionService, SessionStatus

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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


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
            github_repo=request.github_repo
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
    return task


@app.patch("/api/tasks/{task_id}/status", response_model=TaskInDB)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update task status"""
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
    
    # If status changed to Analysis, log it for potential notifications
    if status_update.status == TaskStatus.ANALYSIS and old_status != TaskStatus.ANALYSIS:
        logger.info(f"Task {task_id} needs analysis - status changed to Analysis")
    
    # Auto-start Claude session when task moves to In Progress
    if status_update.status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
        logger.info(f"Task {task_id} started - launching Claude session")
        
        # Get project for context
        project_result = await db.execute(
            select(Project).where(Project.id == task.project_id)
        )
        project = project_result.scalar_one_or_none()
        
        if project:
            # Prepare task context
            task_context = {
                "title": task.title,
                "description": task.description,
                "type": task.type.value if task.type else "Feature",
                "priority": task.priority.value if task.priority else "Medium",
                "status": task.status.value if task.status else "In Progress",
                "analysis": task.analysis,
                "git_branch": task.git_branch
            }
            
            # Launch Claude session
            from .services.claude_launcher_service import ClaudeLauncherService
            
            launch_result = await ClaudeLauncherService.launch_claude_session(
                task_id=task_id,
                project_path=project.path,
                worktree_path=task.worktree_path,
                task_context=task_context
            )
            
            if launch_result["success"]:
                # Also create internal session tracking
                session_result = await claude_service.create_session(
                    task_id=task_id,
                    project_path=project.path,
                    worktree_path=task.worktree_path,
                    initial_context=f"Task: {task.title}\n\n{task.description}"
                )
                
                if session_result["success"]:
                    from .models import ClaudeSession
                    
                    session_data = session_result["session"]
                    db_session = ClaudeSession(
                        id=session_data["id"],
                        task_id=task_id,
                        project_id=task.project_id,
                        status="active",
                        working_dir=launch_result.get("working_dir"),
                        context=json.dumps(task_context),
                        messages=[],
                        session_metadata={
                            "launch_method": launch_result.get("launch_method"),
                            "context_file": launch_result.get("context_file")
                        }
                    )
                    db.add(db_session)
                    
                logger.info(f"Claude session launched for task {task_id} via {launch_result.get('launch_method')}")
            else:
                logger.error(f"Failed to launch Claude session: {launch_result.get('error')}")
    
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
    return task


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Delete task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
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


@app.post("/api/sessions/launch")
async def launch_claude_session(request: dict, db: AsyncSession = Depends(get_db)):
    """Launch a new Claude session for a task"""
    task_id = request.get("task_id")
    
    # Get task details
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Get project
    project_result = await db.execute(select(Project).where(Project.id == task.project_id))
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found")
    
    # Prepare task context
    task_context = {
        "title": task.title,
        "description": task.description,
        "type": task.type.value if task.type else "Feature",
        "priority": task.priority.value if task.priority else "Medium",
        "status": task.status.value if task.status else "In Progress",
        "analysis": task.analysis,
        "git_branch": task.git_branch
    }
    
    # Launch Claude session
    from .services.claude_launcher_service import ClaudeLauncherService
    
    launch_result = await ClaudeLauncherService.launch_claude_session(
        task_id=task_id,
        project_path=project.path,
        worktree_path=task.worktree_path,
        task_context=task_context
    )
    
    if launch_result["success"]:
        # Create or update session record
        from .models import ClaudeSession
        
        # Check if session already exists
        existing_result = await db.execute(
            select(ClaudeSession).where(ClaudeSession.task_id == task_id)
        )
        existing_session = existing_result.scalar_one_or_none()
        
        if existing_session:
            existing_session.status = "active"
            existing_session.working_dir = launch_result.get("working_dir")
            existing_session.session_metadata = {
                "launch_command": launch_result.get("launch_command"),
                "context_file": launch_result.get("context_file")
            }
        else:
            db_session = ClaudeSession(
                id=launch_result.get("session_id", f"session-{task_id}-{datetime.utcnow().timestamp()}"),
                task_id=task_id,
                project_id=task.project_id,
                status="active",
                working_dir=launch_result.get("working_dir"),
                context=json.dumps(task_context),
                messages=[],
                session_metadata={
                    "launch_command": launch_result.get("launch_command"),
                    "context_file": launch_result.get("context_file")
                }
            )
            db.add(db_session)
        
        await db.commit()
        return launch_result
    else:
        raise HTTPException(status_code=500, detail=launch_result.get("error"))


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
        .where(Task.status.in_([TaskStatus.BACKLOG, TaskStatus.ANALYSIS, TaskStatus.READY]))
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)