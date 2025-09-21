"""Pydantic schemas for API validation"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    FEATURE = "Feature"
    BUG = "Bug"


class TaskPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskStatus(str, Enum):
    BACKLOG = "Backlog"
    ANALYSIS = "Analysis"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    CODE_REVIEW = "Code Review"
    DONE = "Done"
    BLOCKED = "Blocked"


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    path: str
    github_repo: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    github_repo: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectInDB(ProjectBase):
    id: str
    tech_stack: List[str] = []
    is_active: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: TaskType = TaskType.FEATURE
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    project_id: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    analysis: Optional[str] = None
    git_branch: Optional[str] = None
    assigned_agent: Optional[str] = None
    estimated_hours: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    comment: Optional[str] = None


class TaskAnalysis(BaseModel):
    task_id: int
    analysis: str
    affected_files: List[str] = []
    complexity: str
    estimated_hours: Optional[int] = None
    risks: List[str] = []
    implementation_plan: str


class TaskInDB(TaskBase):
    id: int
    project_id: str
    status: TaskStatus
    analysis: Optional[str] = None
    git_branch: Optional[str] = None
    worktree_path: Optional[str] = None
    assigned_agent: Optional[str] = None
    estimated_hours: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Project Settings Schemas
class ProjectSettingsBase(BaseModel):
    claude_config: Optional[str] = None
    auto_mode: bool = False
    auto_priority_threshold: TaskPriority = TaskPriority.HIGH
    max_parallel_tasks: int = 3
    test_command: Optional[str] = None
    build_command: Optional[str] = None
    lint_command: Optional[str] = None


class ProjectSettingsCreate(ProjectSettingsBase):
    project_id: str


class ProjectSettingsUpdate(ProjectSettingsBase):
    pass


class ProjectSettingsInDB(ProjectSettingsBase):
    id: int
    project_id: str

    class Config:
        from_attributes = True


# Agent Schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    config: str
    is_active: bool = True


class AgentCreate(AgentBase):
    project_id: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None


class AgentInDB(AgentBase):
    id: int
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# MCP Integration Schemas
class MCPConfig(BaseModel):
    server_url: str = "http://localhost:3333"
    project_id: str
    project_path: str


class InitializeProjectRequest(BaseModel):
    project_path: str
    project_name: str
    github_repo: Optional[str] = None


class InitializeProjectResponse(BaseModel):
    project_id: str
    mcp_configured: bool
    files_created: List[str]
    claude_restart_required: bool = True


# Task Queue Schema
class TaskQueueResponse(BaseModel):
    pending_tasks: List[TaskInDB]
    in_progress_tasks: List[TaskInDB]
    completed_today: int
    
    
# Connection verification
class ConnectionStatus(BaseModel):
    connected: bool
    project_name: Optional[str] = None
    project_path: Optional[str] = None
    tasks_count: int = 0
    active_task: Optional[TaskInDB] = None
    error: Optional[str] = None