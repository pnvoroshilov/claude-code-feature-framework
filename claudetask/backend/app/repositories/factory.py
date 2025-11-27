"""Repository factory for storage mode selection"""

from typing import Union, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseRepository
from .project_repository import SQLiteProjectRepository, MongoDBProjectRepository
from .task_repository import SQLiteTaskRepository, MongoDBTaskRepository
from .memory_repository import SQLiteMemoryRepository, MongoDBMemoryRepository
from .codebase_repository import MongoDBCodebaseRepository
from .skill_repository import MongoDBSkillRepository
from .hook_repository import MongoDBHookRepository
from .mcp_config_repository import MongoDBMCPConfigRepository
from .subagent_repository import MongoDBSubagentRepository
from ..models import Project


class RepositoryFactory:
    """
    Factory for creating storage-specific repository implementations.

    This factory follows the Abstract Factory pattern, determining which
    concrete repository to instantiate based on the project's storage mode.

    Storage modes:
    - "local": SQLite + ChromaDB (default)
    - "mongodb": MongoDB Atlas + Vector Search
    """

    @staticmethod
    async def get_project_repository(
        project_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Union[SQLiteProjectRepository, MongoDBProjectRepository]:
        """
        Get project repository based on storage mode.

        Args:
            project_id: Project ID to determine storage mode (optional for new projects)
            db: SQLAlchemy async session (required for SQLite mode)

        Returns:
            Appropriate project repository implementation

        Raises:
            ValueError: If storage mode is unknown or required dependencies missing
        """
        storage_mode = await RepositoryFactory._get_storage_mode(project_id, db)

        if storage_mode == "local":
            if not db:
                raise ValueError("SQLite repository requires database session")
            return SQLiteProjectRepository(db)

        elif storage_mode == "mongodb":
            from ..database_mongodb import mongodb_manager

            if not mongodb_manager.client:
                raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

            mongodb = mongodb_manager.get_database()
            return MongoDBProjectRepository(mongodb)

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")

    @staticmethod
    async def get_task_repository(
        project_id: str,
        db: Optional[AsyncSession] = None
    ) -> Union[SQLiteTaskRepository, MongoDBTaskRepository]:
        """
        Get task repository based on project's storage mode.

        Args:
            project_id: Project ID to determine storage mode
            db: SQLAlchemy async session (required for SQLite mode)

        Returns:
            Appropriate task repository implementation

        Raises:
            ValueError: If storage mode is unknown or required dependencies missing
        """
        storage_mode = await RepositoryFactory._get_storage_mode(project_id, db)

        if storage_mode == "local":
            if not db:
                raise ValueError("SQLite repository requires database session")
            return SQLiteTaskRepository(db)

        elif storage_mode == "mongodb":
            from ..database_mongodb import mongodb_manager

            if not mongodb_manager.client:
                raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

            mongodb = mongodb_manager.get_database()
            return MongoDBTaskRepository(mongodb)

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")

    @staticmethod
    async def get_memory_repository(
        project_id: str,
        db: Optional[AsyncSession] = None
    ) -> Union[SQLiteMemoryRepository, MongoDBMemoryRepository]:
        """
        Get memory repository based on project's storage mode.

        Args:
            project_id: Project ID to determine storage mode
            db: SQLAlchemy async session (required for SQLite mode)

        Returns:
            Appropriate memory repository implementation

        Raises:
            ValueError: If storage mode is unknown or required dependencies missing
        """
        storage_mode = await RepositoryFactory._get_storage_mode(project_id, db)

        if storage_mode == "local":
            if not db:
                raise ValueError("SQLite repository requires database session")
            return SQLiteMemoryRepository(db)

        elif storage_mode == "mongodb":
            from ..database_mongodb import mongodb_manager

            if not mongodb_manager.client:
                raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

            mongodb = mongodb_manager.get_database()
            return MongoDBMemoryRepository(mongodb)

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")

    @staticmethod
    async def _get_storage_mode(
        project_id: Optional[str],
        db: Optional[AsyncSession]
    ) -> str:
        """
        Determine storage mode for a project.

        Args:
            project_id: Project ID (None for new projects)
            db: SQLAlchemy async session (to query project)

        Returns:
            Storage mode: "local" or "mongodb"

        Notes:
            - Returns "local" for new projects (default)
            - Returns "local" if project not found
            - storage_mode is now part of Project model (merged from ProjectSettings)
        """
        # Default to local storage for new projects
        if not project_id:
            return "local"

        # Query project to determine storage mode
        if db:
            try:
                result = await db.execute(
                    select(Project).where(Project.id == project_id)
                )
                project = result.scalar_one_or_none()

                if project and hasattr(project, 'storage_mode'):
                    return project.storage_mode or "local"

            except Exception:
                # If query fails, default to local
                pass

        # Default to local storage
        return "local"

    @staticmethod
    async def get_storage_mode_for_project(
        project_id: str,
        db: AsyncSession
    ) -> str:
        """
        Public method to get storage mode for a project.

        Args:
            project_id: Project ID
            db: SQLAlchemy async session

        Returns:
            Storage mode: "local" or "mongodb"
        """
        return await RepositoryFactory._get_storage_mode(project_id, db)

    @staticmethod
    async def get_codebase_repository(
        project_id: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[MongoDBCodebaseRepository]:
        """
        Get codebase repository for MongoDB storage mode.

        Note: Codebase repository only available for MongoDB mode.
        For local mode, use the existing ChromaDB-based RAG service.

        Args:
            project_id: Project ID to determine storage mode
            db: SQLAlchemy async session

        Returns:
            MongoDBCodebaseRepository if MongoDB mode, None for local mode

        Raises:
            ValueError: If MongoDB not connected
        """
        storage_mode = await RepositoryFactory._get_storage_mode(project_id, db)

        if storage_mode == "mongodb":
            from ..database_mongodb import mongodb_manager

            if not mongodb_manager.client:
                raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

            mongodb = mongodb_manager.get_database()
            return MongoDBCodebaseRepository(mongodb)

        # Return None for local mode - caller should use ChromaDB RAG
        return None

    @staticmethod
    async def get_skill_repository() -> MongoDBSkillRepository:
        """
        Get skill repository (always uses MongoDB).

        Skills are stored in MongoDB regardless of project storage mode because:
        - Default skills are global (shared across all projects)
        - Custom skills need cross-project favorites support
        - Only skill FILES are stored locally in .claude/skills/

        Returns:
            MongoDBSkillRepository instance

        Raises:
            ValueError: If MongoDB not connected
        """
        from ..database_mongodb import mongodb_manager

        if not mongodb_manager.client:
            raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

        mongodb = mongodb_manager.get_database()
        return MongoDBSkillRepository(mongodb)

    @staticmethod
    async def get_hook_repository() -> MongoDBHookRepository:
        """
        Get hook repository (always uses MongoDB).

        Hooks are stored in MongoDB regardless of project storage mode because:
        - Default hooks are global (shared across all projects)
        - Custom hooks need cross-project favorites support
        - Hook configurations are synced to .claude/settings.json

        Returns:
            MongoDBHookRepository instance

        Raises:
            ValueError: If MongoDB not connected
        """
        from ..database_mongodb import mongodb_manager

        if not mongodb_manager.client:
            raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

        mongodb = mongodb_manager.get_database()
        return MongoDBHookRepository(mongodb)

    @staticmethod
    async def get_mcp_config_repository() -> MongoDBMCPConfigRepository:
        """
        Get MCP config repository (always uses MongoDB).

        MCP configs are stored in MongoDB regardless of project storage mode because:
        - Default configs are global (shared across all projects)
        - Custom configs need cross-project favorites support
        - Config data is synced to .mcp.json file

        Returns:
            MongoDBMCPConfigRepository instance

        Raises:
            ValueError: If MongoDB not connected
        """
        from ..database_mongodb import mongodb_manager

        if not mongodb_manager.client:
            raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

        mongodb = mongodb_manager.get_database()
        return MongoDBMCPConfigRepository(mongodb)

    @staticmethod
    async def get_subagent_repository() -> MongoDBSubagentRepository:
        """
        Get subagent repository (always uses MongoDB).

        Subagents are stored in MongoDB regardless of project storage mode because:
        - Default subagents are global (shared across all projects)
        - Custom subagents need cross-project favorites support
        - Subagent files are stored locally in .claude/commands/

        Returns:
            MongoDBSubagentRepository instance

        Raises:
            ValueError: If MongoDB not connected
        """
        from ..database_mongodb import mongodb_manager

        if not mongodb_manager.client:
            raise ValueError("MongoDB not connected. Configure MongoDB Atlas first.")

        mongodb = mongodb_manager.get_database()
        return MongoDBSubagentRepository(mongodb)
