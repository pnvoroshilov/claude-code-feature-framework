"""
Repository Pattern Template

This template includes:
1. Repository ABC (Port) - goes in application/ports/repositories.py
2. Repository Implementation (Adapter) - goes in infrastructure/repositories/

Copy and customize for your entity.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from dataclasses import dataclass

# ==================== Port (Application Layer) ====================
# Location: application/ports/repositories.py

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """
    Base repository interface.

    Generic repository ABC that can be extended for specific entities.
    Prefer specific repository interfaces over generic ones for type safety.
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save entity (create or update)."""
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """Delete entity by ID."""
        pass


class EntityNameRepository(ABC):
    """
    Repository interface for [EntityName] aggregate.

    This ABC defines the contract for data persistence.
    Lives in Application layer, implemented in Infrastructure layer.

    Location: application/ports/repositories.py
    """

    @abstractmethod
    def find_by_id(self, entity_id: int) -> Optional["EntityName"]:
        """
        Find entity by ID.

        Args:
            entity_id: The entity ID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_unique_field(self, value: str) -> Optional["EntityName"]:
        """
        Find entity by unique field (e.g., email, code).

        Args:
            value: The unique field value

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List["EntityName"]:
        """
        Find all entities with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    def find_by_criteria(
        self,
        is_active: Optional[bool] = None,
        name_contains: Optional[str] = None
    ) -> List["EntityName"]:
        """
        Find entities matching criteria.

        Args:
            is_active: Filter by active status
            name_contains: Filter by name substring

        Returns:
            List of matching entities
        """
        pass

    @abstractmethod
    def save(self, entity: "EntityName") -> "EntityName":
        """
        Save entity (create if id=0, update otherwise).

        Args:
            entity: The entity to save

        Returns:
            Saved entity with generated ID (if new)
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        """
        Delete entity by ID.

        Args:
            entity_id: The entity ID

        Raises:
            ValueError: If entity not found
        """
        pass

    @abstractmethod
    def exists_by_unique_field(self, value: str) -> bool:
        """
        Check if entity with unique field exists.

        Args:
            value: The unique field value

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Count total entities.

        Returns:
            Total count
        """
        pass


# ==================== Adapter (Infrastructure Layer) ====================
# Location: infrastructure/repositories/{entity_name}_repository.py

from sqlalchemy.orm import Session

# Import your domain entity and value objects
# from domain.entities.entity_name import EntityName
# from domain.value_objects.email import Email

# Import ORM model
# from infrastructure.database.models import EntityNameORM


class SQLAlchemyEntityNameRepository(EntityNameRepository):
    """
    SQLAlchemy implementation of EntityNameRepository.

    This adapter implements the repository interface using SQLAlchemy ORM.
    Maps between domain entities and ORM models.

    Location: infrastructure/repositories/{entity_name}_repository.py
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy session for database operations
        """
        self._session = session

    def find_by_id(self, entity_id: int) -> Optional["EntityName"]:
        """Find entity by ID."""
        orm = self._session.query(EntityNameORM).filter_by(id=entity_id).first()
        return self._to_domain(orm) if orm else None

    def find_by_unique_field(self, value: str) -> Optional["EntityName"]:
        """Find entity by unique field."""
        orm = self._session.query(EntityNameORM).filter_by(
            unique_field=value
        ).first()
        return self._to_domain(orm) if orm else None

    def find_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List["EntityName"]:
        """Find all entities with pagination."""
        orms = (
            self._session.query(EntityNameORM)
            .order_by(EntityNameORM.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_domain(orm) for orm in orms]

    def find_by_criteria(
        self,
        is_active: Optional[bool] = None,
        name_contains: Optional[str] = None
    ) -> List["EntityName"]:
        """Find entities matching criteria."""
        query = self._session.query(EntityNameORM)

        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        if name_contains:
            query = query.filter(
                EntityNameORM.name.ilike(f"%{name_contains}%")
            )

        orms = query.all()
        return [self._to_domain(orm) for orm in orms]

    def save(self, entity: "EntityName") -> "EntityName":
        """Save entity (create or update)."""
        if entity.id == 0:
            # Create new
            orm = self._to_orm(entity)
            self._session.add(orm)
        else:
            # Update existing
            orm = self._session.query(EntityNameORM).filter_by(
                id=entity.id
            ).first()
            if not orm:
                raise ValueError(f"Entity {entity.id} not found")
            self._update_orm(orm, entity)

        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, entity_id: int) -> None:
        """Delete entity by ID."""
        deleted = self._session.query(EntityNameORM).filter_by(
            id=entity_id
        ).delete()
        if deleted == 0:
            raise ValueError(f"Entity {entity_id} not found")
        self._session.commit()

    def exists_by_unique_field(self, value: str) -> bool:
        """Check if entity exists by unique field."""
        return (
            self._session.query(EntityNameORM)
            .filter_by(unique_field=value)
            .count() > 0
        )

    def count(self) -> int:
        """Count total entities."""
        return self._session.query(EntityNameORM).count()

    # ==================== Mapping Methods ====================

    def _to_domain(self, orm: "EntityNameORM") -> "EntityName":
        """
        Map ORM model to domain entity.

        This is the boundary where ORM models become domain objects.
        Value objects are reconstructed here.
        """
        return EntityName(
            id=orm.id,
            # email=Email(orm.email),  # Reconstruct Value Object
            name=orm.name,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at
        )

    def _to_orm(self, entity: "EntityName") -> "EntityNameORM":
        """
        Map domain entity to ORM model.

        Extract primitive values from Value Objects.
        """
        return EntityNameORM(
            # email=entity.email.value,  # Extract primitive from VO
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at
        )

    def _update_orm(
        self,
        orm: "EntityNameORM",
        entity: "EntityName"
    ) -> None:
        """Update ORM model from domain entity."""
        # orm.email = entity.email.value
        orm.name = entity.name
        orm.is_active = entity.is_active
        orm.updated_at = entity.updated_at
        # Don't update id or created_at


# ==================== ORM Model Template ====================
# Location: infrastructure/database/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class EntityNameORM(Base):
    """
    SQLAlchemy ORM model for [EntityName].

    ORM models live only in Infrastructure layer.
    They are never used in Domain or Application layers.

    Location: infrastructure/database/models.py
    """
    __tablename__ = "entity_names"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # unique_field = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, name={self.name})>"
