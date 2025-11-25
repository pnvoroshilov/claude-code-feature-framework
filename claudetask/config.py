"""
Centralized configuration for ClaudeTask Framework

This module defines all paths and configurations used across the project.
All services MUST use these paths to ensure consistency.
"""

import os
from pathlib import Path
from typing import Optional


class ClaudeTaskConfig:
    """
    Centralized configuration for ClaudeTask Framework.

    All paths are resolved relative to the project root directory.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            project_root: Absolute path to project root. If None, auto-detects.
        """
        if project_root:
            self.project_root = Path(project_root).resolve()
        else:
            # Auto-detect: go up from this file to project root
            # config.py is at: {project_root}/claudetask/config.py
            self.project_root = Path(__file__).parent.parent.resolve()

        # Ensure project root exists
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {self.project_root}")

    # =================================================================
    # DATA DIRECTORIES
    # =================================================================

    @property
    def data_dir(self) -> Path:
        """Main data directory for all persistent data"""
        return self.project_root / ".claudetask"

    @property
    def backend_data_dir(self) -> Path:
        """Backend-specific data directory"""
        return self.project_root / "claudetask" / "backend" / "data"

    # =================================================================
    # DATABASE PATHS
    # =================================================================

    @property
    def sqlite_db_path(self) -> Path:
        """SQLite database path (tasks, projects, sessions)"""
        return self.backend_data_dir / "claudetask.db"

    @property
    def sqlite_db_url(self) -> str:
        """SQLite database URL for SQLAlchemy (async)"""
        return f"sqlite+aiosqlite:///{self.sqlite_db_path}"

    @property
    def sqlite_db_url_sync(self) -> str:
        """SQLite database URL for SQLAlchemy (sync)"""
        return f"sqlite:///{self.sqlite_db_path}"

    # =================================================================
    # RAG / CHROMADB PATHS (CENTRALIZED FOR ALL PROJECTS)
    # =================================================================

    @property
    def framework_root(self) -> Path:
        """
        Framework root directory (where ClaudeTask is installed).
        This is ALWAYS the same regardless of which project is active.
        Used for centralized storage like ChromaDB.
        """
        # This file is at: {framework_root}/claudetask/config.py
        return Path(__file__).parent.parent.resolve()

    @property
    def chromadb_dir(self) -> Path:
        """
        ChromaDB directory for vector embeddings.
        CENTRALIZED: Always in framework's .claude/data/chromadb folder.
        This ensures all projects share the same vector database.
        """
        return self.framework_root / ".claude" / "data" / "chromadb"

    @property
    def rag_index_metadata_path(self) -> Path:
        """RAG index metadata file (file hashes, timestamps)"""
        return self.data_dir / "index_metadata.json"

    # =================================================================
    # WORKTREE PATHS
    # =================================================================

    @property
    def worktrees_dir(self) -> Path:
        """Git worktrees directory for task isolation"""
        return self.project_root / "worktrees"

    def get_task_worktree_path(self, task_id: int) -> Path:
        """Get worktree path for specific task"""
        return self.worktrees_dir / f"task-{task_id}"

    # =================================================================
    # INITIALIZATION
    # =================================================================

    def ensure_directories(self) -> None:
        """Create all necessary directories if they don't exist"""
        directories = [
            self.data_dir,
            self.backend_data_dir,
            self.chromadb_dir,
            self.worktrees_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    # =================================================================
    # ENVIRONMENT OVERRIDES
    # =================================================================

    @classmethod
    def from_env(cls) -> "ClaudeTaskConfig":
        """
        Create config from environment variables.

        Environment variables:
        - CLAUDETASK_PROJECT_ROOT: Project root directory
        """
        project_root = os.getenv("CLAUDETASK_PROJECT_ROOT")
        return cls(project_root=project_root)

    # =================================================================
    # STRING REPRESENTATION
    # =================================================================

    def __repr__(self) -> str:
        return f"""ClaudeTaskConfig(
    project_root={self.project_root}
    data_dir={self.data_dir}
    sqlite_db={self.sqlite_db_path}
    chromadb={self.chromadb_dir}
    worktrees={self.worktrees_dir}
)"""


# =================================================================
# SINGLETON INSTANCE
# =================================================================

# Global singleton instance
_config_instance: Optional[ClaudeTaskConfig] = None


def get_config(project_root: Optional[str] = None) -> ClaudeTaskConfig:
    """
    Get the global configuration instance.

    Args:
        project_root: Optional project root path. Only used on first call.

    Returns:
        ClaudeTaskConfig instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = ClaudeTaskConfig(project_root=project_root)
        _config_instance.ensure_directories()

    return _config_instance


def reset_config() -> None:
    """Reset the global configuration (useful for testing)"""
    global _config_instance
    _config_instance = None


# =================================================================
# CONVENIENCE EXPORTS
# =================================================================

# For backward compatibility and convenience
def get_project_root() -> Path:
    """Get project root path"""
    return get_config().project_root


def get_sqlite_db_url() -> str:
    """Get SQLite database URL (async)"""
    return get_config().sqlite_db_url


def get_chromadb_path() -> Path:
    """Get ChromaDB directory path"""
    return get_config().chromadb_dir
