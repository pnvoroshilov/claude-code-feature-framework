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