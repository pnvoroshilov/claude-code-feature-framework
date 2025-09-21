"""Database models for ClaudeTask"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TaskType(str, enum.Enum):
    """Task type enumeration"""
    FEATURE = "Feature"
    BUG = "Bug"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    BACKLOG = "Backlog"
    ANALYSIS = "Analysis"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    CODE_REVIEW = "Code Review"
    DONE = "Done"
    BLOCKED = "Blocked"


class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    github_repo = Column(String, nullable=True)
    tech_stack = Column(JSON, default=list)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    settings = relationship("ProjectSettings", back_populates="project", uselist=False, cascade="all, delete-orphan")
    agents = relationship("Agent", cascade="all, delete-orphan")


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TaskType), default=TaskType.FEATURE)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.BACKLOG)
    analysis = Column(Text, nullable=True)
    git_branch = Column(String, nullable=True)
    worktree_path = Column(String, nullable=True)
    assigned_agent = Column(String, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")


class TaskHistory(Base):
    """Task history model for tracking status changes"""
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    old_status = Column(Enum(TaskStatus), nullable=True)
    new_status = Column(Enum(TaskStatus), nullable=False)
    comment = Column(Text, nullable=True)
    changed_by = Column(String, default="system")
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="history")


class ProjectSettings(Base):
    """Project settings model"""
    __tablename__ = "project_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), unique=True, nullable=False)
    claude_config = Column(Text, nullable=True)  # CLAUDE.md content
    auto_mode = Column(Boolean, default=False)
    auto_priority_threshold = Column(Enum(TaskPriority), default=TaskPriority.HIGH)
    max_parallel_tasks = Column(Integer, default=3)
    test_command = Column(String, nullable=True)
    build_command = Column(String, nullable=True)
    lint_command = Column(String, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="settings")


class Agent(Base):
    """Agent configuration model"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # frontend, backend, ai, tester, reviewer
    config = Column(Text, nullable=False)  # Agent markdown content
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)