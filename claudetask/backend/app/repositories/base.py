"""Abstract base repository for database operations"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict


class BaseRepository(ABC):
    """
    Abstract base repository defining the contract for database operations.

    This interface enables storage abstraction following the Repository pattern
    and Dependency Inversion principle (SOLID). Concrete implementations can use
    SQLite, MongoDB, or any other storage backend.
    """

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Any]:
        """
        Retrieve entity by ID.

        Args:
            id: Unique identifier for the entity

        Returns:
            Entity object if found, None otherwise
        """
        pass

    @abstractmethod
    async def create(self, entity: Any) -> str:
        """
        Create new entity.

        Args:
            entity: Entity object to create

        Returns:
            ID of created entity
        """
        pass

    @abstractmethod
    async def update(self, entity: Any) -> None:
        """
        Update existing entity.

        Args:
            entity: Entity object with updated values

        Raises:
            NotFoundError: If entity doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        """
        Delete entity by ID.

        Args:
            id: Unique identifier for the entity

        Raises:
            NotFoundError: If entity doesn't exist
        """
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        List entities with pagination and optional filters.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Optional filtering criteria

        Returns:
            List of entity objects
        """
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching optional filters.

        Args:
            filters: Optional filtering criteria

        Returns:
            Total count of matching entities
        """
        pass
