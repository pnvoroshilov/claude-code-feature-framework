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
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    CODE_REVIEW = "Code Review"
    PR = "PR"  # Pull Request created, awaiting manual review
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


class StageResultAppend(BaseModel):
    status: str = Field(..., description="Current status/stage of the task")
    summary: str = Field(..., description="Summary of what was accomplished in this stage")
    details: Optional[str] = Field(None, description="Optional detailed information about this stage")


class TestingUrlsUpdate(BaseModel):
    testing_urls: Dict[str, str] = Field(..., description="Dictionary of environment names to their URLs")


class TaskInDB(TaskBase):
    id: int
    project_id: str
    status: TaskStatus
    analysis: Optional[str] = None
    stage_results: Optional[List[Dict[str, Any]]] = None
    testing_urls: Optional[Dict[str, str]] = None
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
    force_reinitialize: bool = False


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
    
    
# MCP Task Status Update Response
class MCPTaskStatusUpdateResponse(BaseModel):
    task: TaskInDB
    status: str
    comment: Optional[str] = None
    next_steps: List[str] = []
    worktree: Optional[Dict[str, Any]] = None


# Connection verification
class ConnectionStatus(BaseModel):
    connected: bool
    project_name: Optional[str] = None
    project_path: Optional[str] = None
    tasks_count: int = 0
    active_task: Optional[TaskInDB] = None
    error: Optional[str] = None


# Skill Schemas
class SkillBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)


class SkillCreate(SkillBase):
    """Schema for creating a custom skill"""
    pass


class SkillInDB(SkillBase):
    id: int
    skill_type: str  # "default" or "custom"
    category: str  # e.g., "Analysis", "Development", "Testing"
    file_path: Optional[str] = None
    is_enabled: bool = False
    status: Optional[str] = None  # For custom skills: "creating", "active", "failed"
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SkillsResponse(BaseModel):
    """Response schema for getting project skills"""
    enabled: List[SkillInDB]
    available_default: List[SkillInDB]
    custom: List[SkillInDB]


class AgentSkillRecommendation(BaseModel):
    agent_name: str
    skill_id: int
    priority: int  # 1-5 (1 = highest priority)
    reason: Optional[str] = None