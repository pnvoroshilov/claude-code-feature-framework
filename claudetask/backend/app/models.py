"""Database models for ClaudeTask"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Boolean, ForeignKey, UniqueConstraint
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
    IN_PROGRESS = "In Progress"
    TESTING = "Testing"
    CODE_REVIEW = "Code Review"  # Code Review + PR creation (combined)
    DONE = "Done"
    BLOCKED = "Blocked"


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False, unique=True)
    github_repo = Column(String, nullable=True)
    custom_instructions = Column(Text, nullable=True, default="")
    tech_stack = Column(JSON, default=list)
    project_mode = Column(String, nullable=False, default="simple")  # "simple" or "development"
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # passive_deletes=True lets database handle CASCADE DELETE
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan", passive_deletes=True)
    settings = relationship("ProjectSettings", back_populates="project", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    agents = relationship("Agent", cascade="all, delete-orphan", passive_deletes=True)
    claude_sessions = relationship("ClaudeSession", back_populates="project", cascade="all, delete-orphan", passive_deletes=True)

    # Additional relationships with back_populates for proper CASCADE DELETE
    # passive_deletes='all' tells SQLAlchemy to let database handle ALL deletion (no UPDATE first)
    # lazy='noload' prevents SQLAlchemy from loading these relationships automatically
    project_skills = relationship("ProjectSkill", back_populates="project", passive_deletes='all', lazy='noload')
    custom_skills = relationship("CustomSkill", back_populates="project", passive_deletes='all', lazy='noload')
    custom_mcp_configs = relationship("CustomMCPConfig", back_populates="project", passive_deletes='all', lazy='noload')
    enabled_mcp_configs = relationship("ProjectMCPConfig", back_populates="project", passive_deletes='all', lazy='noload')
    custom_subagents = relationship("CustomSubagent", back_populates="project", passive_deletes='all', lazy='noload')
    enabled_subagents = relationship("ProjectSubagent", back_populates="project", passive_deletes='all', lazy='noload')
    custom_hooks = relationship("CustomHook", back_populates="project", passive_deletes='all', lazy='noload')
    enabled_hooks = relationship("ProjectHook", back_populates="project", passive_deletes='all', lazy='noload')


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(TaskType), default=TaskType.FEATURE)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.BACKLOG)
    analysis = Column(Text, nullable=True)
    stage_results = Column(JSON, default=list)  # Cumulative stage results
    testing_urls = Column(JSON, nullable=True)  # Testing environment URLs
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
    claude_sessions = relationship("ClaudeSession", back_populates="task", cascade="all, delete-orphan")


class TaskHistory(Base):
    """Task history model for tracking status changes"""
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum(TaskStatus), nullable=True)
    new_status = Column(Enum(TaskStatus), nullable=False)
    comment = Column(Text, nullable=True)
    changed_by = Column(String, default="system")
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="history")


class ClaudeSession(Base):
    """Claude Code session model for task-based development"""
    __tablename__ = "claude_sessions"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, nullable=True, index=True)  # Added session_id field
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="idle")  # idle, initializing, active, paused, completed, error
    mode = Column(String, nullable=False, default="terminal")  # terminal, embedded, websocket
    working_dir = Column(String, nullable=True)
    context_file = Column(String, nullable=True)  # Path to context file
    launch_command = Column(String, nullable=True)  # Command used to launch
    context = Column(Text, nullable=True)
    messages = Column(JSON, nullable=True)  # Store message history as JSON
    session_metadata = Column(JSON, nullable=True)  # Store metadata like tools used, errors, etc
    summary = Column(Text, nullable=True)
    statistics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    task = relationship("Task", back_populates="claude_sessions")
    project = relationship("Project", back_populates="claude_sessions")


class TestFramework(str, enum.Enum):
    """Test framework enumeration"""
    PYTEST = "pytest"
    JEST = "jest"
    VITEST = "vitest"
    MOCHA = "mocha"
    UNITTEST = "unittest"
    CUSTOM = "custom"


class ProjectSettings(Base):
    """Project settings model"""
    __tablename__ = "project_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    auto_mode = Column(Boolean, default=False)
    auto_priority_threshold = Column(Enum(TaskPriority), default=TaskPriority.HIGH)
    max_parallel_tasks = Column(Integer, default=3)
    test_command = Column(String, nullable=True)
    build_command = Column(String, nullable=True)
    lint_command = Column(String, nullable=True)
    worktree_enabled = Column(Boolean, default=True, nullable=False)  # Enable/disable git worktrees
    manual_mode = Column(Boolean, default=False, nullable=False)  # Manual (True) vs Automated (False) for UC-04 Testing & UC-05 Code Review

    # New testing configuration fields
    test_directory = Column(String, nullable=True, default="tests")  # Main test directory (e.g., "tests", "src/__tests__")
    test_framework = Column(Enum(TestFramework, values_callable=lambda x: [e.value for e in x]), nullable=True, default=TestFramework.PYTEST)  # Test framework
    auto_merge_tests = Column(Boolean, default=True, nullable=False)  # Auto-merge new tests after PR approval
    test_staging_dir = Column(String, nullable=True, default="tests/staging")  # Staging directory for new task tests

    # Relationships
    project = relationship("Project", back_populates="settings")


class Agent(Base):
    """Agent configuration model"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # frontend, backend, ai, tester, reviewer
    config = Column(Text, nullable=False)  # Agent markdown content
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DefaultSkill(Base):
    """Default skills provided by the framework"""
    __tablename__ = "default_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    file_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    skill_metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomSkill(Base):
    """Custom skills created by users"""
    __tablename__ = "custom_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    file_name = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # creating, active, failed
    error_message = Column(Text, nullable=True)
    created_by = Column(String(100), default="user")
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="custom_skills")


class ProjectSkill(Base):
    """Junction table for project-skill many-to-many relationship"""
    __tablename__ = "project_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, nullable=False)
    skill_type = Column(String(10), nullable=False)  # "default" or "custom"
    enabled_at = Column(DateTime, default=datetime.utcnow)
    enabled_by = Column(String(100), default="user")

    # Relationships
    project = relationship("Project", back_populates="project_skills")


class AgentSkillRecommendation(Base):
    """Recommended skills for each agent"""
    __tablename__ = "agent_skill_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(100), nullable=False)
    skill_id = Column(Integer, nullable=False)
    skill_type = Column(String(10), nullable=False)
    priority = Column(Integer, default=3)  # 1-5
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DefaultMCPConfig(Base):
    """Default MCP configurations provided by the framework"""
    __tablename__ = "default_mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # development, testing, productivity, etc.
    config = Column(JSON, nullable=False)  # MCP server configuration JSON
    mcp_metadata = Column(JSON, nullable=True)  # Additional metadata (version, author, etc.)
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomMCPConfig(Base):
    """Custom MCP configurations created by users (project-specific)"""
    __tablename__ = "custom_mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)  # Required: project-specific
    name = Column(String(100), nullable=False)  # Unique per project, not globally
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    config = Column(JSON, nullable=False)  # MCP server configuration JSON
    status = Column(String(20), default="active")  # active, inactive, error
    error_message = Column(Text, nullable=True)
    created_by = Column(String(100), default="user")
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="custom_mcp_configs")

    # Unique constraint: name must be unique per project
    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uix_project_mcp_name'),
    )


class ProjectMCPConfig(Base):
    """Junction table for project-mcp config many-to-many relationship"""
    __tablename__ = "project_mcp_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    mcp_config_id = Column(Integer, nullable=False)
    mcp_config_type = Column(String(10), nullable=False)  # "default" or "custom"
    enabled_at = Column(DateTime, default=datetime.utcnow)
    enabled_by = Column(String(100), default="user")

    # Relationships
    project = relationship("Project", back_populates="enabled_mcp_configs")


class DefaultSubagent(Base):
    """Default subagents provided by the framework (from Claude Code Task tool)"""
    __tablename__ = "default_subagents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "Analysis", "Development", "Testing", "Architecture", "DevOps"
    subagent_type = Column(String(100), nullable=False)  # The actual subagent_type used in Task tool (e.g., "frontend-developer", "backend-architect")
    tools_available = Column(JSON, nullable=True)  # List of tools this agent has access to
    recommended_for = Column(JSON, nullable=True)  # List of task types/scenarios this agent is recommended for
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomSubagent(Base):
    """Custom subagent configurations created by users"""
    __tablename__ = "custom_subagents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    subagent_type = Column(String(100), nullable=False)  # Custom subagent_type name
    config = Column(Text, nullable=True)  # Optional: Agent configuration/instructions (file is created in .claude/agents/)
    tools_available = Column(JSON, nullable=True)
    status = Column(String(20), default="active")  # creating, active, failed
    error_message = Column(Text, nullable=True)
    created_by = Column(String(100), default="user")
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="custom_subagents")


class ProjectSubagent(Base):
    """Junction table for project-subagent many-to-many relationship"""
    __tablename__ = "project_subagents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    subagent_id = Column(Integer, nullable=False)
    subagent_type = Column(String(10), nullable=False)  # "default" or "custom"
    enabled_at = Column(DateTime, default=datetime.utcnow)
    enabled_by = Column(String(100), default="user")

    # Relationships
    project = relationship("Project", back_populates="enabled_subagents")


class DefaultHook(Base):
    """Default hooks provided by the framework"""
    __tablename__ = "default_hooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "logging", "formatting", "notifications", "security", "version-control"
    file_name = Column(String(100), nullable=False)
    script_file = Column(String(100), nullable=True)  # Optional separate script file (e.g., post-push-docs.sh)
    hook_config = Column(JSON, nullable=False)  # Hook configuration JSON (events, matchers, commands)
    setup_instructions = Column(Text, nullable=True)
    dependencies = Column(JSON, nullable=True)  # List of required dependencies (jq, git, prettier, etc.)
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomHook(Base):
    """Custom hooks created by users"""
    __tablename__ = "custom_hooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    file_name = Column(String(100), nullable=False)
    script_file = Column(String(100), nullable=True)  # Optional separate script file (e.g., custom-hook.sh)
    hook_config = Column(JSON, nullable=False)  # Hook configuration JSON
    setup_instructions = Column(Text, nullable=True)
    dependencies = Column(JSON, nullable=True)
    status = Column(String(20), default="active")  # creating, active, failed
    error_message = Column(Text, nullable=True)
    created_by = Column(String(100), default="user")
    is_favorite = Column(Boolean, default=False)  # Mark as favorite (shows in Favorites tab)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="custom_hooks")


class ProjectHook(Base):
    """Junction table for project-hook many-to-many relationship"""
    __tablename__ = "project_hooks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    hook_id = Column(Integer, nullable=False)
    hook_type = Column(String(10), nullable=False)  # "default" or "custom"
    enabled_at = Column(DateTime, default=datetime.utcnow)
    enabled_by = Column(String(100), default="user")

    # Relationships
    project = relationship("Project", back_populates="enabled_hooks")


class SubagentSkill(Base):
    """Junction table for subagent-skill many-to-many relationship"""
    __tablename__ = "subagent_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subagent_id = Column(Integer, nullable=False)
    subagent_type = Column(String(10), nullable=False)  # "default" or "custom"
    skill_id = Column(Integer, nullable=False)
    skill_type = Column(String(10), nullable=False)  # "default" or "custom"
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(String(100), default="user")

    # Unique constraint: one skill can only be assigned to one subagent once
    __table_args__ = (
        UniqueConstraint('subagent_id', 'subagent_type', 'skill_id', 'skill_type', name='uix_subagent_skill'),
    )