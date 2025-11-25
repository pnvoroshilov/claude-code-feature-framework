"""
Use Case (Interactor) Template

Use cases contain application-specific business logic.
They orchestrate domain entities and call repository ports.

Location: application/use_cases/{use_case_name}.py
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

# Import ports (ABCs)
from application.ports.repositories import EntityNameRepository

# Import domain entities and value objects
# from domain.entities.entity_name import EntityName
# from domain.value_objects.email import Email

# Import domain exceptions
from domain.exceptions import DomainException


# ==================== Command/Query Objects ====================

@dataclass(frozen=True)
class CreateEntityCommand:
    """
    Input command for creating entity.

    Commands represent user intent and contain input data.
    Use frozen=True for immutability.
    """
    name: str
    # email: str
    # Add other required fields


@dataclass(frozen=True)
class UpdateEntityCommand:
    """Input command for updating entity."""
    entity_id: int
    name: Optional[str] = None
    # Add other updatable fields


@dataclass(frozen=True)
class GetEntityQuery:
    """Query for getting entity by ID."""
    entity_id: int


@dataclass(frozen=True)
class ListEntitiesQuery:
    """Query for listing entities with pagination."""
    limit: int = 100
    offset: int = 0
    is_active: Optional[bool] = None


# ==================== Result Objects ====================

@dataclass(frozen=True)
class EntityResult:
    """
    Output result for entity operations.

    Results are DTOs that cross layer boundaries.
    They contain only primitive types, not domain objects.
    """
    entity_id: int
    name: str
    is_active: bool
    created_at: str


@dataclass(frozen=True)
class EntityListResult:
    """Output result for entity list."""
    entities: List[EntityResult]
    total: int


# ==================== Create Use Case ====================

class CreateEntityUseCase:
    """
    Use Case: Create a new entity.

    This use case handles the creation of new entities,
    including validation and persistence.

    Location: application/use_cases/create_entity.py
    """

    def __init__(
        self,
        entity_repo: EntityNameRepository,
        # email_service: EmailService,  # Add other dependencies
    ):
        """
        Initialize use case with dependencies.

        All dependencies are injected through constructor.
        Dependencies are abstract ports (ABCs), not concrete implementations.
        """
        self._entity_repo = entity_repo
        # self._email_service = email_service

    def execute(self, command: CreateEntityCommand) -> EntityResult:
        """
        Execute the create entity use case.

        Args:
            command: Input command with creation data

        Returns:
            EntityResult with created entity data

        Raises:
            DomainException: If validation fails
            EmailAlreadyExistsException: If email already exists
        """
        # 1. Validate and create value objects
        # email = Email(command.email)  # VO validates format

        # 2. Check business rules
        # if self._entity_repo.exists_by_email(email.value):
        #     raise EmailAlreadyExistsException(f"Email exists: {email}")

        # 3. Create domain entity using factory method
        entity = EntityName.create(
            name=command.name,
            # email=email,
        )

        # 4. Persist through repository
        saved_entity = self._entity_repo.save(entity)

        # 5. Handle side effects (events, notifications)
        # self._email_service.send_welcome(saved_entity)

        # 6. Return result DTO
        return EntityResult(
            entity_id=saved_entity.id,
            name=saved_entity.name,
            is_active=saved_entity.is_active,
            created_at=saved_entity.created_at.isoformat()
        )


# ==================== Get Use Case ====================

class GetEntityUseCase:
    """
    Use Case: Get entity by ID.

    Simple query use case for retrieving a single entity.
    """

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, query: GetEntityQuery) -> EntityResult:
        """
        Execute the get entity use case.

        Args:
            query: Query with entity ID

        Returns:
            EntityResult with entity data

        Raises:
            EntityNotFoundException: If entity not found
        """
        entity = self._entity_repo.find_by_id(query.entity_id)

        if not entity:
            raise DomainException(f"Entity not found: {query.entity_id}")

        return EntityResult(
            entity_id=entity.id,
            name=entity.name,
            is_active=entity.is_active,
            created_at=entity.created_at.isoformat()
        )


# ==================== List Use Case ====================

class ListEntitiesUseCase:
    """
    Use Case: List entities with pagination.

    Query use case for retrieving multiple entities.
    """

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, query: ListEntitiesQuery) -> EntityListResult:
        """
        Execute the list entities use case.

        Args:
            query: Query with pagination and filters

        Returns:
            EntityListResult with list of entities
        """
        entities = self._entity_repo.find_by_criteria(
            is_active=query.is_active
        )

        # Apply pagination
        paginated = entities[query.offset:query.offset + query.limit]

        results = [
            EntityResult(
                entity_id=e.id,
                name=e.name,
                is_active=e.is_active,
                created_at=e.created_at.isoformat()
            )
            for e in paginated
        ]

        return EntityListResult(
            entities=results,
            total=len(entities)
        )


# ==================== Update Use Case ====================

class UpdateEntityUseCase:
    """
    Use Case: Update existing entity.

    Handles partial updates to entity fields.
    """

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, command: UpdateEntityCommand) -> EntityResult:
        """
        Execute the update entity use case.

        Args:
            command: Command with entity ID and fields to update

        Returns:
            EntityResult with updated entity data

        Raises:
            EntityNotFoundException: If entity not found
            DomainException: If validation fails
        """
        # 1. Fetch existing entity
        entity = self._entity_repo.find_by_id(command.entity_id)
        if not entity:
            raise DomainException(f"Entity not found: {command.entity_id}")

        # 2. Apply updates through domain methods
        if command.name is not None:
            entity.update_name(command.name)

        # 3. Persist changes
        saved_entity = self._entity_repo.save(entity)

        # 4. Return result
        return EntityResult(
            entity_id=saved_entity.id,
            name=saved_entity.name,
            is_active=saved_entity.is_active,
            created_at=saved_entity.created_at.isoformat()
        )


# ==================== Delete Use Case ====================

class DeleteEntityUseCase:
    """
    Use Case: Delete entity.

    Handles entity deletion with business rules.
    """

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, entity_id: int) -> None:
        """
        Execute the delete entity use case.

        Args:
            entity_id: ID of entity to delete

        Raises:
            EntityNotFoundException: If entity not found
            DomainException: If deletion not allowed
        """
        # 1. Verify entity exists
        entity = self._entity_repo.find_by_id(entity_id)
        if not entity:
            raise DomainException(f"Entity not found: {entity_id}")

        # 2. Check business rules for deletion
        # if entity.has_active_orders():
        #     raise DomainException("Cannot delete entity with active orders")

        # 3. Delete through repository
        self._entity_repo.delete(entity_id)


# ==================== Activate/Deactivate Use Case ====================

class ActivateEntityUseCase:
    """Use Case: Activate entity."""

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, entity_id: int) -> EntityResult:
        """Activate entity by ID."""
        entity = self._entity_repo.find_by_id(entity_id)
        if not entity:
            raise DomainException(f"Entity not found: {entity_id}")

        # Domain method enforces business rule
        entity.activate()

        saved = self._entity_repo.save(entity)

        return EntityResult(
            entity_id=saved.id,
            name=saved.name,
            is_active=saved.is_active,
            created_at=saved.created_at.isoformat()
        )


class DeactivateEntityUseCase:
    """Use Case: Deactivate entity."""

    def __init__(self, entity_repo: EntityNameRepository):
        self._entity_repo = entity_repo

    def execute(self, entity_id: int) -> EntityResult:
        """Deactivate entity by ID."""
        entity = self._entity_repo.find_by_id(entity_id)
        if not entity:
            raise DomainException(f"Entity not found: {entity_id}")

        # Domain method enforces business rule
        entity.deactivate()

        saved = self._entity_repo.save(entity)

        return EntityResult(
            entity_id=saved.id,
            name=saved.name,
            is_active=saved.is_active,
            created_at=saved.created_at.isoformat()
        )
