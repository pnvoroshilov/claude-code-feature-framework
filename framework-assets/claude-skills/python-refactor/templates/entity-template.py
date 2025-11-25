"""
Domain Entity Template

Copy and customize this template for creating domain entities.
Domain entities have identity, behavior, and encapsulate business rules.

Location: domain/entities/{entity_name}.py
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self, Optional, List
from domain.exceptions import DomainException

# Import your value objects
# from domain.value_objects.email import Email


@dataclass
class EntityName:
    """
    [Entity description - what this entity represents in the domain]

    Attributes:
        id: Unique identifier (0 for new unsaved entities)
        [attribute]: [description]

    Business Rules:
        - [List key business rules this entity enforces]
        - [Example: "Cannot be activated if already active"]
    """

    # Identity
    id: int

    # Required attributes (use Value Objects for complex types)
    # email: Email
    name: str

    # State
    status: str = "ACTIVE"
    is_active: bool = True

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Collections (if aggregate root)
    # items: List[ChildEntity] = field(default_factory=list)

    # Private fields
    # _events: List[DomainEvent] = field(default_factory=list, init=False)

    def __post_init__(self):
        """Validate entity state on creation."""
        self._validate()

    def _validate(self) -> None:
        """Validate invariants."""
        if not self.name or not self.name.strip():
            raise DomainException("Name cannot be empty")
        # Add more validations

    # ==================== Business Methods ====================

    def activate(self) -> Self:
        """
        Activate the entity.

        Business Rule: Cannot activate if already active.

        Returns:
            Self for method chaining

        Raises:
            DomainException: If already active
        """
        if self.is_active:
            raise DomainException(f"{self.__class__.__name__} already active")
        self.is_active = True
        self._mark_updated()
        return self

    def deactivate(self) -> Self:
        """
        Deactivate the entity.

        Business Rule: Cannot deactivate if already inactive.

        Returns:
            Self for method chaining

        Raises:
            DomainException: If already inactive
        """
        if not self.is_active:
            raise DomainException(f"{self.__class__.__name__} already inactive")
        self.is_active = False
        self._mark_updated()
        return self

    def update_name(self, new_name: str) -> Self:
        """
        Update entity name.

        Args:
            new_name: The new name

        Returns:
            Self for method chaining

        Raises:
            DomainException: If name is empty or unchanged
        """
        if not new_name or not new_name.strip():
            raise DomainException("Name cannot be empty")
        if new_name.strip() == self.name:
            raise DomainException("Name unchanged")
        self.name = new_name.strip()
        self._mark_updated()
        return self

    # ==================== Aggregate Methods (if root) ====================

    # def add_item(self, item: ChildEntity) -> Self:
    #     """Add item to aggregate."""
    #     if self.status != "ACTIVE":
    #         raise DomainException("Cannot modify inactive aggregate")
    #     self.items.append(item)
    #     self._mark_updated()
    #     return self

    # ==================== Domain Events ====================

    # def _emit_event(self, event: DomainEvent) -> None:
    #     """Record domain event."""
    #     self._events.append(event)

    # def collect_events(self) -> List[DomainEvent]:
    #     """Collect and clear events."""
    #     events = self._events.copy()
    #     self._events.clear()
    #     return events

    # ==================== Private Helpers ====================

    def _mark_updated(self) -> None:
        """Mark entity as updated."""
        self.updated_at = datetime.utcnow()

    # ==================== Equality ====================

    def __eq__(self, other: object) -> bool:
        """Entities are equal by ID."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    # ==================== Factory Methods ====================

    @classmethod
    def create(cls, name: str) -> "EntityName":
        """
        Factory method for creating new entities.

        Args:
            name: Entity name
            # Add other required args

        Returns:
            New entity instance with id=0
        """
        return cls(
            id=0,
            name=name,
            is_active=True,
            created_at=datetime.utcnow()
        )


# ==================== Value Object Template ====================

@dataclass(frozen=True)  # Immutable!
class ValueObjectName:
    """
    Value Object Template.

    Value Objects are immutable and defined by their attributes.
    Equality is by value, not by identity.

    Location: domain/value_objects/{vo_name}.py
    """

    value: str

    def __post_init__(self):
        """Validate on creation."""
        if not self._is_valid(self.value):
            raise DomainException(f"Invalid {self.__class__.__name__}: {self.value}")

    @staticmethod
    def _is_valid(value: str) -> bool:
        """Validate value."""
        return bool(value and value.strip())

    def __str__(self) -> str:
        return self.value
