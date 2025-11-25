# Repository Pattern in Python

**Comprehensive guide to implementing the Repository pattern for abstracting data access and isolating SQLAlchemy ORM from business logic.**

## What is the Repository Pattern?

**Definition**: A Repository mediates between the domain and data mapping layers, acting like an in-memory collection of domain objects.

repository_pattern_benefits[7]{benefit,description,example}:
Abstraction,Hide data access implementation details,Switch from SQLAlchemy to raw SQL without changing use cases
Testability,Mock repositories for unit testing,Test use cases without database
Centralization,Single place for data access logic,All queries in repository not scattered
Domain focus,Business logic unaware of persistence,Domain entities don't know about ORM
Flexibility,Easy to swap data sources,PostgreSQL to MongoDB without domain changes
Query encapsulation,Complex queries hidden behind methods,find_active_users_by_role() not raw SQL
Consistency,Standard interface for all data access,All repos follow same pattern

## Repository Pattern Structure

### The Three Components

repository_components[3]{component,layer,responsibility}:
Repository Interface (Port),Application Layer,ABC defining contract for data access
Repository Implementation (Adapter),Infrastructure Layer,Concrete implementation using SQLAlchemy
Domain Entity,Domain Layer,Pure Python dataclass with business logic

### Directory Structure

```
project/
├── domain/
│   ├── entities/
│   │   └── user.py                    # Domain entity (dataclass)
│   └── value_objects/
│       └── email.py                   # Value objects
├── application/
│   └── ports/
│       └── repositories.py            # ABC interfaces (Ports)
└── infrastructure/
    ├── database/
    │   ├── models.py                  # SQLAlchemy ORM models
    │   └── session.py                 # Session management
    └── repositories/
        └── user_repository.py         # Concrete implementation (Adapter)
```

## Step-by-Step Implementation

### Step 1: Define Domain Entity (Domain Layer)

```python
# domain/entities/user.py
from dataclasses import dataclass
from typing import Self
from domain.value_objects.email import Email
from domain.exceptions import DomainException

@dataclass
class User:
    """Domain entity - pure Python, no ORM."""
    id: int
    email: Email
    name: str
    is_active: bool
    created_at: datetime

    def activate(self) -> Self:
        """Business rule: activate user."""
        if self.is_active:
            raise DomainException("User already active")
        self.is_active = True
        return self

    def deactivate(self) -> Self:
        """Business rule: deactivate user."""
        if not self.is_active:
            raise DomainException("User already inactive")
        self.is_active = False
        return self

    def change_email(self, new_email: Email) -> Self:
        """Business rule: email must be different."""
        if new_email == self.email:
            raise DomainException("Email unchanged")
        self.email = new_email
        return self
```

### Step 2: Define Repository Interface (Application Layer)

```python
# application/ports/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User

class UserRepository(ABC):
    """
    Port: Abstract interface for user persistence.
    Application layer defines the contract.
    Infrastructure layer provides implementation.
    """

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass

    @abstractmethod
    def find_all_active(self) -> List[User]:
        """Get all active users."""
        pass

    @abstractmethod
    def find_by_criteria(self, is_active: bool = None, name_contains: str = None) -> List[User]:
        """Find users by criteria."""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Save user (create or update). Returns saved user with generated ID."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Delete user by ID."""
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total users."""
        pass
```

### Step 3: Create ORM Model (Infrastructure Layer)

```python
# infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserORM(Base):
    """
    SQLAlchemy ORM model - Infrastructure concern.
    Lives only in Infrastructure layer.
    NOT used in Domain or Application layers.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<UserORM(id={self.id}, email={self.email})>"
```

### Step 4: Implement Repository (Infrastructure Layer)

```python
# infrastructure/repositories/user_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from domain.entities.user import User
from domain.value_objects.email import Email
from infrastructure.database.models import UserORM

class SQLAlchemyUserRepository(UserRepository):
    """
    Adapter: Concrete implementation of UserRepository using SQLAlchemy.
    Maps between Domain entities and ORM models.
    """

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        orm_user = self._session.query(UserORM).filter_by(id=user_id).first()
        return self._to_domain(orm_user) if orm_user else None

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        orm_user = self._session.query(UserORM).filter_by(email=email).first()
        return self._to_domain(orm_user) if orm_user else None

    def find_all_active(self) -> List[User]:
        """Get all active users."""
        orm_users = self._session.query(UserORM).filter_by(is_active=True).all()
        return [self._to_domain(u) for u in orm_users]

    def find_by_criteria(self, is_active: bool = None, name_contains: str = None) -> List[User]:
        """Find users by criteria - complex query encapsulated."""
        query = self._session.query(UserORM)

        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        if name_contains:
            query = query.filter(UserORM.name.contains(name_contains))

        orm_users = query.all()
        return [self._to_domain(u) for u in orm_users]

    def save(self, user: User) -> User:
        """Save user (create or update)."""
        if user.id == 0:
            # Create new user
            orm_user = self._to_orm(user)
            orm_user.id = None  # Let DB generate ID
            self._session.add(orm_user)
        else:
            # Update existing user
            orm_user = self._session.query(UserORM).filter_by(id=user.id).first()
            if not orm_user:
                raise ValueError(f"User {user.id} not found")
            self._update_orm(orm_user, user)

        self._session.commit()
        self._session.refresh(orm_user)
        return self._to_domain(orm_user)

    def delete(self, user_id: int) -> None:
        """Delete user by ID."""
        deleted = self._session.query(UserORM).filter_by(id=user_id).delete()
        if deleted == 0:
            raise ValueError(f"User {user_id} not found")
        self._session.commit()

    def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists."""
        return self._session.query(UserORM).filter_by(email=email).count() > 0

    def count(self) -> int:
        """Count total users."""
        return self._session.query(UserORM).count()

    def _to_domain(self, orm_user: UserORM) -> User:
        """
        Map ORM model to domain entity.
        This is the boundary - VO construction happens here.
        """
        return User(
            id=orm_user.id,
            email=Email(orm_user.email),  # Reconstruct VO
            name=orm_user.name,
            is_active=orm_user.is_active,
            created_at=orm_user.created_at
        )

    def _to_orm(self, user: User) -> UserORM:
        """
        Map domain entity to ORM model.
        Extract primitive values from VOs.
        """
        return UserORM(
            id=user.id if user.id != 0 else None,
            email=user.email.value,  # Extract primitive from VO
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at
        )

    def _update_orm(self, orm_user: UserORM, user: User) -> None:
        """Update ORM model from domain entity."""
        orm_user.email = user.email.value
        orm_user.name = user.name
        orm_user.is_active = user.is_active
        # Don't update id or created_at
```

### Step 5: Database Session Management

```python
# infrastructure/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures session is closed even if exception occurs.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_session() -> Session:
    """Get database session (for dependency injection)."""
    return SessionLocal()
```

## Advanced Repository Patterns

### Pattern 1: Specification Pattern

**Encapsulate query logic in reusable specifications.**

```python
# application/specifications/user_specifications.py
from abc import ABC, abstractmethod
from typing import TypeVar
from sqlalchemy.orm import Query

T = TypeVar('T')

class Specification(ABC):
    """Base specification for query criteria."""

    @abstractmethod
    def to_sqlalchemy(self, query: Query) -> Query:
        """Convert specification to SQLAlchemy query."""
        pass

class ActiveUserSpec(Specification):
    """Specification for active users."""

    def to_sqlalchemy(self, query: Query) -> Query:
        from infrastructure.database.models import UserORM
        return query.filter(UserORM.is_active == True)

class EmailDomainSpec(Specification):
    """Specification for users with specific email domain."""

    def __init__(self, domain: str):
        self.domain = domain

    def to_sqlalchemy(self, query: Query) -> Query:
        from infrastructure.database.models import UserORM
        return query.filter(UserORM.email.endswith(f"@{self.domain}"))

# Usage in repository
class SQLAlchemyUserRepository(UserRepository):
    def find_by_specification(self, spec: Specification) -> List[User]:
        """Find users matching specification."""
        query = self._session.query(UserORM)
        query = spec.to_sqlalchemy(query)
        orm_users = query.all()
        return [self._to_domain(u) for u in orm_users]

# Usage in application
active_gmail_users = repo.find_by_specification(
    AndSpec(ActiveUserSpec(), EmailDomainSpec("gmail.com"))
)
```

### Pattern 2: Unit of Work Pattern

**Manage transactions across multiple repositories.**

```python
# application/ports/unit_of_work.py
from abc import ABC, abstractmethod
from typing import ContextManager
from application.ports.repositories import UserRepository, OrderRepository

class UnitOfWork(ABC):
    """Unit of Work pattern for transaction management."""

    users: UserRepository
    orders: OrderRepository

    @abstractmethod
    def __enter__(self):
        """Enter transaction context."""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction."""
        pass

# infrastructure/unit_of_work.py
from sqlalchemy.orm import Session
from application.ports.unit_of_work import UnitOfWork
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from infrastructure.repositories.order_repository import SQLAlchemyOrderRepository

class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work."""

    def __init__(self, session: Session):
        self._session = session

    def __enter__(self):
        self.users = SQLAlchemyUserRepository(self._session)
        self.orders = SQLAlchemyOrderRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self._session.close()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

# Usage in use case
class CreateOrderUseCase:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def execute(self, command: CreateOrderCommand):
        with self._uow:
            # Both repos share same transaction
            user = self._uow.users.find_by_id(command.user_id)
            order = Order(...)
            self._uow.orders.save(order)
            self._uow.commit()
```

### Pattern 3: Read Model Pattern (CQRS)

**Separate read and write models for performance.**

```python
# application/ports/read_models.py
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class UserListDTO:
    """Read-only DTO for user list."""
    id: int
    email: str
    name: str
    is_active: bool

class UserReadModel(ABC):
    """Read model for user queries."""

    @abstractmethod
    def get_user_list(self, limit: int, offset: int) -> List[UserListDTO]:
        """Get paginated user list."""
        pass

    @abstractmethod
    def get_active_user_count(self) -> int:
        """Get count of active users."""
        pass

# infrastructure/read_models/user_read_model.py
class SQLAlchemyUserReadModel(UserReadModel):
    """Optimized read model using raw SQL."""

    def __init__(self, session: Session):
        self._session = session

    def get_user_list(self, limit: int, offset: int) -> List[UserListDTO]:
        """Raw SQL for performance - no ORM overhead."""
        query = """
            SELECT id, email, name, is_active
            FROM users
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """
        result = self._session.execute(query, {"limit": limit, "offset": offset})
        return [UserListDTO(**row) for row in result.mappings()]

    def get_active_user_count(self) -> int:
        """Simple count query."""
        query = "SELECT COUNT(*) FROM users WHERE is_active = true"
        return self._session.execute(query).scalar()
```

## Testing Repository Implementations

### Unit Test (Mock Repository)

```python
# tests/application/test_create_user_use_case.py
from unittest.mock import Mock
import pytest
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from domain.entities.user import User
from domain.value_objects.email import Email

def test_create_user_success():
    # Arrange: Mock repository
    mock_repo = Mock()
    mock_repo.find_by_email.return_value = None  # Email doesn't exist
    mock_repo.save.return_value = User(
        id=1,
        email=Email("test@example.com"),
        name="Test User",
        is_active=True,
        created_at=datetime.now()
    )

    use_case = CreateUserUseCase(mock_repo)
    command = CreateUserCommand(email="test@example.com", name="Test User")

    # Act
    result = use_case.execute(command)

    # Assert
    assert result.user_id == 1
    assert result.email == "test@example.com"
    mock_repo.save.assert_called_once()

def test_create_user_email_exists():
    # Arrange: Mock repository with existing user
    mock_repo = Mock()
    mock_repo.find_by_email.return_value = User(...)  # Email exists

    use_case = CreateUserUseCase(mock_repo)
    command = CreateUserCommand(email="existing@example.com", name="Test")

    # Act & Assert
    with pytest.raises(DomainException, match="Email already exists"):
        use_case.execute(command)
```

### Integration Test (Real Repository)

```python
# tests/infrastructure/test_user_repository.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database.models import Base, UserORM
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from domain.entities.user import User
from domain.value_objects.email import Email

@pytest.fixture
def session():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repo(session):
    """Create repository with test session."""
    return SQLAlchemyUserRepository(session)

def test_save_and_find_user(repo):
    """Test saving and finding user."""
    # Arrange
    user = User(
        id=0,  # New user
        email=Email("test@example.com"),
        name="Test User",
        is_active=True,
        created_at=datetime.now()
    )

    # Act: Save
    saved_user = repo.save(user)

    # Assert: Has ID
    assert saved_user.id > 0

    # Act: Find
    found_user = repo.find_by_id(saved_user.id)

    # Assert: Found correct user
    assert found_user is not None
    assert found_user.id == saved_user.id
    assert found_user.email.value == "test@example.com"
    assert found_user.name == "Test User"

def test_find_by_email(repo):
    """Test finding user by email."""
    # Arrange
    user = User(
        id=0,
        email=Email("unique@example.com"),
        name="Test",
        is_active=True,
        created_at=datetime.now()
    )
    repo.save(user)

    # Act
    found = repo.find_by_email("unique@example.com")

    # Assert
    assert found is not None
    assert found.email.value == "unique@example.com"

def test_find_all_active(repo):
    """Test finding all active users."""
    # Arrange: Create active and inactive users
    active_user = User(id=0, email=Email("active@example.com"), name="Active", is_active=True, created_at=datetime.now())
    inactive_user = User(id=0, email=Email("inactive@example.com"), name="Inactive", is_active=False, created_at=datetime.now())
    repo.save(active_user)
    repo.save(inactive_user)

    # Act
    active_users = repo.find_all_active()

    # Assert
    assert len(active_users) == 1
    assert active_users[0].email.value == "active@example.com"
```

## Common Repository Mistakes

### Mistake 1: Leaking ORM Models to Domain

```python
# ❌ WRONG: Use case depends on ORM
from infrastructure.database.models import UserORM

class CreateUserUseCase:
    def execute(self, data):
        orm_user = UserORM(...)  # ORM in use case!
        self.session.add(orm_user)
```

**Fix**: Use domain entities and repository

```python
# ✅ CORRECT: Use domain entity
class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    def execute(self, data):
        user = User(...)  # Domain entity
        self._repo.save(user)  # Repository handles ORM
```

### Mistake 2: Complex Queries in Use Cases

```python
# ❌ WRONG: Query logic in use case
class GetUsersUseCase:
    def execute(self):
        return self.session.query(UserORM)\
            .filter(UserORM.is_active == True)\
            .filter(UserORM.email.contains("@gmail"))\
            .all()
```

**Fix**: Encapsulate in repository

```python
# ✅ CORRECT: Query in repository
class UserRepository(ABC):
    @abstractmethod
    def find_active_gmail_users(self) -> List[User]:
        pass

class GetUsersUseCase:
    def execute(self):
        return self._repo.find_active_gmail_users()
```

### Mistake 3: Generic Repository

```python
# ❌ WRONG: Generic repository loses type safety
class GenericRepository:
    def find_by_id(self, entity_type, id):
        return self.session.query(entity_type).filter_by(id=id).first()
```

**Fix**: Specific repository per aggregate

```python
# ✅ CORRECT: Specific typed repository
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
```

## Repository Pattern Checklist

repository_checklist[12]{check,requirement}:
ABC in Application,Repository interface defined as ABC in Application layer
Implementation in Infrastructure,Concrete repository in Infrastructure layer
Domain entity used,Repository works with domain entities not ORM models
Mapping layer exists,_to_domain() and _to_orm() methods for conversion
No ORM leakage,ORM models never escape Infrastructure layer
Query encapsulation,Complex queries hidden behind repository methods
Collection-like interface,Methods like find save delete (not SQL terms)
Aggregate per repository,One repository per aggregate root
Unit tests with mocks,Use cases tested with mocked repositories
Integration tests with DB,Repositories tested with real test database
Session management,Session passed to repository or Unit of Work
Transaction boundaries,Clear transaction management (commit/rollback)

---

**File Size**: 490/500 lines max ✅
