# Clean Architecture in Python

**Comprehensive guide to implementing Clean Architecture (also known as Hexagonal Architecture, Ports and Adapters, or Onion Architecture) in Python applications.**

## The Core Principle: The Dependency Rule

**"Dependencies must point inward only, toward higher-level policies."**

dependency_flow[4]{from_layer,to_layer,allowed,explanation}:
Infrastructure,Application,YES,Infrastructure implements Application interfaces
Infrastructure,Domain,YES,Infrastructure can use Domain entities
Application,Domain,YES,Application orchestrates Domain logic
Domain,Any outer layer,NO,Domain must have zero external dependencies

## The Four Layers

### Layer 1: Domain Layer (Innermost)

**The heart of your application - pure business logic with no dependencies.**

domain_layer_contents[7]{component,description,python_implementation}:
Entities,Objects with identity that can change over time,dataclass with id field
Value Objects,Immutable objects defined by attributes,dataclass(frozen=True)
Domain Events,Events representing business state changes,dataclass event objects
Business Rules,Invariants and constraints,Methods on entities or separate validators
Domain Exceptions,Business rule violations,Custom exception classes
Aggregates,Consistency boundaries,Entity as aggregate root
Domain Services,Stateless operations on domain objects,Functions or classes with no infrastructure deps

**Key Rules:**
- NO imports from outer layers
- NO framework dependencies (FastAPI, SQLAlchemy, etc.)
- NO infrastructure concerns (database, HTTP, files)
- Pure Python only

**Example Structure:**
```
domain/
├── __init__.py
├── entities/
│   ├── __init__.py
│   ├── user.py
│   └── order.py
├── value_objects/
│   ├── __init__.py
│   ├── email.py
│   └── money.py
├── events/
│   ├── __init__.py
│   └── user_events.py
├── exceptions.py
└── services/
    ├── __init__.py
    └── pricing_service.py
```

### Layer 2: Application Layer

**Orchestrates domain logic and defines abstractions (Ports) for outer layers.**

application_layer_contents[5]{component,description,python_implementation}:
Use Cases (Interactors),Application-specific business rules,Classes with execute() method
Ports (Interfaces),Abstract interfaces for infrastructure,ABC classes with abstractmethod
DTOs,Data transfer between layers,dataclass or Pydantic models
Application Services,Orchestrate multiple use cases,Classes coordinating use cases
Command/Query Objects,Input data for use cases,dataclass request objects

**Key Rules:**
- Depends ONLY on Domain layer
- Defines ABCs that Infrastructure implements
- Contains application-specific business rules
- No framework code (FastAPI, SQLAlchemy)

**Example Structure:**
```
application/
├── __init__.py
├── use_cases/
│   ├── __init__.py
│   ├── create_user.py
│   └── place_order.py
├── ports/
│   ├── __init__.py
│   ├── repositories.py  # ABC interfaces
│   └── services.py      # ABC interfaces
└── dtos/
    ├── __init__.py
    ├── user_dto.py
    └── order_dto.py
```

### Layer 3: Infrastructure Layer

**Implements the abstractions defined by Application layer.**

infrastructure_layer_contents[6]{component,description,python_implementation}:
Repository Implementations,Concrete data access,SQLAlchemyUserRepository implements UserRepository ABC
ORM Models,Database schema mapping,SQLAlchemy declarative models
Database Connection,Connection and session management,SQLAlchemy engine and sessionmaker
External Service Adapters,Third-party API clients,Stripe payment adapter
File System Access,File operations,S3 adapter for file storage
Framework Integration,Web framework setup,FastAPI app configuration

**Key Rules:**
- Implements Application port ABCs
- Contains all framework-specific code
- Can depend on Domain and Application layers
- Volatile - easy to replace

**Example Structure:**
```
infrastructure/
├── __init__.py
├── database/
│   ├── __init__.py
│   ├── models.py        # SQLAlchemy ORM
│   ├── session.py       # Session management
│   └── migrations/      # Alembic migrations
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py
│   └── order_repository.py
└── adapters/
    ├── __init__.py
    ├── email_adapter.py
    └── payment_adapter.py
```

### Layer 4: Presentation Layer

**Handles external communication (HTTP, CLI, GraphQL, etc.).**

presentation_layer_contents[5]{component,description,python_implementation}:
Controllers (Route Handlers),HTTP endpoint handlers,FastAPI route functions
Request/Response Schemas,API contracts,Pydantic models for validation
Middleware,Request/response processing,FastAPI middleware
Error Handlers,Convert exceptions to responses,Exception handlers for HTTP errors
Dependency Injection Setup,DI container configuration,FastAPI Depends or Dishka setup

**Key Rules:**
- Thin layer - delegates to Application use cases
- Handles protocol concerns (HTTP, JSON, etc.)
- Maps between external formats and internal DTOs
- No business logic

**Example Structure:**
```
presentation/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── users.py     # User endpoints
│   │   └── orders.py    # Order endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   └── order_schema.py
│   └── dependencies.py  # DI setup
└── middleware/
    ├── __init__.py
    └── auth_middleware.py
```

## Dependency Inversion Principle (DIP)

**The key to Clean Architecture is proper dependency inversion.**

### Without DIP (Wrong)

```python
# ❌ Use case depends on concrete implementation
class CreateUserUseCase:
    def __init__(self):
        self.repo = SQLAlchemyUserRepository()  # Hard dependency!

    def execute(self, data):
        user = User(...)
        self.repo.save(user)  # Coupled to SQLAlchemy
```

**Problems:**
- Cannot test without database
- Cannot swap implementations
- Violates dependency rule

### With DIP (Correct)

```python
# ✅ Application layer defines interface
from abc import ABC, abstractmethod

class UserRepository(ABC):  # Port (interface)
    @abstractmethod
    def save(self, user: User) -> None:
        pass

# ✅ Use case depends on abstraction
class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, data):
        user = User(...)
        self._user_repo.save(user)

# ✅ Infrastructure implements interface
class SQLAlchemyUserRepository(UserRepository):  # Adapter
    def __init__(self, session: Session):
        self._session = session

    def save(self, user: User) -> None:
        orm_user = self._to_orm(user)
        self._session.add(orm_user)
        self._session.commit()
```

**Benefits:**
- Use case testable with mock repository
- Can swap SQLAlchemy for another ORM
- Dependency points inward (Infrastructure → Application)

## Practical Implementation Patterns

### Pattern 1: Domain Entity

```python
# domain/entities/user.py
from dataclasses import dataclass
from typing import Self
from domain.value_objects.email import Email
from domain.exceptions import DomainException

@dataclass
class User:
    """Domain entity with identity and behavior."""
    id: int
    email: Email
    name: str
    is_active: bool

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

### Pattern 2: Value Object

```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re
from domain.exceptions import InvalidEmailException

@dataclass(frozen=True)  # Immutable!
class Email:
    """Email value object - immutable and defined by value."""
    value: str

    def __post_init__(self):
        """Validate on creation."""
        if not self._is_valid(self.value):
            raise InvalidEmailException(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        """Business rule: email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value
```

### Pattern 3: Repository Interface (Port)

```python
# application/ports/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User

class UserRepository(ABC):
    """Port: Abstract interface for user persistence."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Save user (create or update)."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Delete user by ID."""
        pass
```

### Pattern 4: Use Case (Interactor)

```python
# application/use_cases/create_user.py
from dataclasses import dataclass
from application.ports.repositories import UserRepository
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.exceptions import DomainException

@dataclass
class CreateUserCommand:
    """Input DTO for use case."""
    email: str
    name: str

@dataclass
class CreateUserResult:
    """Output DTO for use case."""
    user_id: int
    email: str
    name: str

class CreateUserUseCase:
    """Application use case: create new user."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, command: CreateUserCommand) -> CreateUserResult:
        """Execute use case logic."""
        # Validate email not already exists
        email = Email(command.email)
        existing = self._user_repo.find_by_email(email.value)
        if existing:
            raise DomainException("Email already exists")

        # Create domain entity
        user = User(
            id=0,  # Will be set by repository
            email=email,
            name=command.name,
            is_active=True
        )

        # Persist
        saved_user = self._user_repo.save(user)

        # Return result DTO
        return CreateUserResult(
            user_id=saved_user.id,
            email=saved_user.email.value,
            name=saved_user.name
        )
```

### Pattern 5: Repository Implementation (Adapter)

```python
# infrastructure/repositories/user_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from domain.entities.user import User
from domain.value_objects.email import Email
from infrastructure.database.models import UserORM

class SQLAlchemyUserRepository(UserRepository):
    """Adapter: SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        orm_user = self._session.query(UserORM).filter_by(id=user_id).first()
        return self._to_domain(orm_user) if orm_user else None

    def find_by_email(self, email: str) -> Optional[User]:
        orm_user = self._session.query(UserORM).filter_by(email=email).first()
        return self._to_domain(orm_user) if orm_user else None

    def find_all(self) -> List[User]:
        orm_users = self._session.query(UserORM).all()
        return [self._to_domain(u) for u in orm_users]

    def save(self, user: User) -> User:
        orm_user = self._to_orm(user)
        if user.id == 0:
            self._session.add(orm_user)
        else:
            existing = self._session.query(UserORM).filter_by(id=user.id).first()
            if existing:
                existing.email = orm_user.email
                existing.name = orm_user.name
                existing.is_active = orm_user.is_active
        self._session.commit()
        self._session.refresh(orm_user)
        return self._to_domain(orm_user)

    def delete(self, user_id: int) -> None:
        self._session.query(UserORM).filter_by(id=user_id).delete()
        self._session.commit()

    def _to_domain(self, orm_user: UserORM) -> User:
        """Map ORM model to domain entity."""
        return User(
            id=orm_user.id,
            email=Email(orm_user.email),
            name=orm_user.name,
            is_active=orm_user.is_active
        )

    def _to_orm(self, user: User) -> UserORM:
        """Map domain entity to ORM model."""
        return UserORM(
            id=user.id if user.id != 0 else None,
            email=user.email.value,
            name=user.name,
            is_active=user.is_active
        )
```

### Pattern 6: FastAPI Controller (Thin)

```python
# presentation/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException
from presentation.api.schemas.user_schema import CreateUserRequest, UserResponse
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from domain.exceptions import DomainException

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """
    Thin controller - delegates to use case.
    """
    try:
        command = CreateUserCommand(
            email=request.email,
            name=request.name
        )
        result = use_case.execute(command)
        return UserResponse(
            id=result.user_id,
            email=result.email,
            name=result.name
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Common Violations and Fixes

### Violation 1: Domain Depends on Infrastructure

```python
# ❌ WRONG: Domain importing SQLAlchemy
from sqlalchemy.orm import Session
from domain.entities.user import User

class UserService:
    def __init__(self, session: Session):  # Domain depends on SQLAlchemy!
        self.session = session
```

**Fix**: Move to Infrastructure, use ABC in Application

```python
# ✅ CORRECT: Application defines ABC
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

# Infrastructure implements
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session
```

### Violation 2: Use Case Contains HTTP Logic

```python
# ❌ WRONG: Use case knows about HTTP
from fastapi import HTTPException

class CreateUserUseCase:
    def execute(self, request):
        if not request.email:
            raise HTTPException(status_code=400, detail="Email required")
```

**Fix**: Use domain exceptions, convert in controller

```python
# ✅ CORRECT: Use case raises domain exception
class CreateUserUseCase:
    def execute(self, command):
        if not command.email:
            raise DomainException("Email required")

# Controller converts to HTTP
@router.post("/users")
def create_user(request):
    try:
        use_case.execute(...)
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Violation 3: Anemic Domain Model

```python
# ❌ WRONG: Entity is just data container
@dataclass
class User:
    id: int
    email: str
    is_active: bool

# Business logic in service
class UserService:
    def activate_user(self, user: User):
        user.is_active = True
```

**Fix**: Move business logic to entity

```python
# ✅ CORRECT: Rich domain model
@dataclass
class User:
    id: int
    email: Email
    is_active: bool

    def activate(self) -> Self:
        """Business rule in entity."""
        if self.is_active:
            raise DomainException("Already active")
        self.is_active = True
        return self
```

## Testing Strategy by Layer

### Domain Layer Tests (Pure Unit Tests)

```python
# tests/domain/test_user.py
import pytest
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.exceptions import DomainException

def test_user_activation():
    user = User(id=1, email=Email("test@example.com"), name="Test", is_active=False)
    user.activate()
    assert user.is_active

def test_cannot_activate_already_active_user():
    user = User(id=1, email=Email("test@example.com"), name="Test", is_active=True)
    with pytest.raises(DomainException, match="already active"):
        user.activate()
```

### Application Layer Tests (Mock Repositories)

```python
# tests/application/test_create_user.py
from unittest.mock import Mock
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from domain.entities.user import User

def test_create_user_success():
    # Mock repository
    mock_repo = Mock()
    mock_repo.find_by_email.return_value = None
    mock_repo.save.return_value = User(id=1, email=Email("test@example.com"), name="Test", is_active=True)

    # Execute use case
    use_case = CreateUserUseCase(mock_repo)
    command = CreateUserCommand(email="test@example.com", name="Test")
    result = use_case.execute(command)

    assert result.user_id == 1
    mock_repo.save.assert_called_once()
```

### Infrastructure Layer Tests (Integration Tests)

```python
# tests/infrastructure/test_user_repository.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from infrastructure.database.models import Base, UserORM
from domain.entities.user import User
from domain.value_objects.email import Email

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_repository_save_and_find(session):
    repo = SQLAlchemyUserRepository(session)
    user = User(id=0, email=Email("test@example.com"), name="Test", is_active=True)

    saved = repo.save(user)
    assert saved.id > 0

    found = repo.find_by_id(saved.id)
    assert found is not None
    assert found.email.value == "test@example.com"
```

## Checklist for Clean Architecture

clean_architecture_checklist[15]{check,requirement}:
Domain independence,Domain layer has zero external dependencies
Dependency direction,All dependencies point inward
ABC usage,Application defines ABCs Infrastructure implements
No framework in domain,No FastAPI SQLAlchemy imports in Domain
No framework in application,No FastAPI SQLAlchemy imports in Application
Rich domain model,Business logic in entities not services
Immutable value objects,Value objects use frozen=True
Repository abstraction,Data access through ABC interfaces
Thin controllers,Controllers delegate to use cases
Use case focused,Each use case has single responsibility
Domain exceptions,Business errors as domain exceptions
DTO usage,Clear boundaries with DTOs
Testable domain,Can test domain without mocks
Testable application,Can test use cases with mock repos
Integration tests,Test repositories with real database

---

**File Size**: 444/500 lines max ✅
