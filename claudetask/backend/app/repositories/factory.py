"""Repository factory for storage mode selection"""

from typing import Union, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseRepository
from .project_repository import SQLiteProjectRepository, MongoDBProjectRepository
from .task_repository import SQLiteTaskRepository, MongoDBTaskRepository
from .memory_repository import SQLiteMemoryRepository, MongoDBMemoryRepository
from ..models import ProjectSettings


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
            db: SQLAlchemy async session (to query project settings)

        Returns:
            Storage mode: "local" or "mongodb"

        Notes:
            - Returns "local" for new projects (default)
            - Returns "local" if project settings not found
            - Queries project_settings table for existing projects
        """
        # Default to local storage for new projects
        if not project_id:
            return "local"

        # Query project settings to determine storage mode
        if db:
            try:
                result = await db.execute(
                    select(ProjectSettings).where(
                        ProjectSettings.project_id == project_id
                    )
                )
                settings = result.scalar_one_or_none()

                if settings and hasattr(settings, 'storage_mode'):
                    return settings.storage_mode

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
