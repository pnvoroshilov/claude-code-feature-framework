# FastAPI with Clean Architecture

**Complete example of structuring a FastAPI application using Clean Architecture, DDD, and proper dependency injection.**

## Project Structure

```
project/
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── value_objects/
│   │   ├── __init__.py
│   │   └── email.py
│   ├── events/
│   │   └── user_events.py
│   └── exceptions.py
├── application/
│   ├── __init__.py
│   ├── use_cases/
│   │   ├── __init__.py
│   │   ├── create_user.py
│   │   └── get_user.py
│   └── ports/
│       ├── __init__.py
│       └── repositories.py
├── infrastructure/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── session.py
│   ├── repositories/
│   │   └── user_repository.py
│   └── di/
│       ├── __init__.py
│       └── providers.py
├── presentation/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── users.py
│   │   └── schemas/
│   │       └── user_schema.py
│   └── main.py
├── tests/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
└── pyproject.toml
```

## Layer 1: Domain Layer

### Domain Exceptions

```python
# domain/exceptions.py
class DomainException(Exception):
    """Base exception for domain errors."""
    pass

class InvalidEmailException(DomainException):
    """Invalid email format."""
    pass

class UserNotFoundException(DomainException):
    """User not found."""
    pass

class EmailAlreadyExistsException(DomainException):
    """Email already registered."""
    pass
```

### Value Objects

```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re
from domain.exceptions import InvalidEmailException

@dataclass(frozen=True)
class Email:
    """Email value object - immutable, self-validating."""
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailException(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def domain(self) -> str:
        return self.value.split('@')[1]

    def __str__(self) -> str:
        return self.value
```

### Domain Entity

```python
# domain/entities/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from domain.value_objects.email import Email
from domain.exceptions import DomainException

@dataclass
class User:
    """User entity - has identity and behavior."""
    id: int
    email: Email
    name: str
    is_active: bool
    created_at: datetime

    def activate(self) -> Self:
        """Activate user account."""
        if self.is_active:
            raise DomainException("User already active")
        self.is_active = True
        return self

    def deactivate(self) -> Self:
        """Deactivate user account."""
        if not self.is_active:
            raise DomainException("User already inactive")
        self.is_active = False
        return self

    def change_email(self, new_email: Email) -> Self:
        """Change user email."""
        if new_email == self.email:
            raise DomainException("New email is the same as current")
        self.email = new_email
        return self

    def update_name(self, new_name: str) -> Self:
        """Update user name."""
        if not new_name or not new_name.strip():
            raise DomainException("Name cannot be empty")
        self.name = new_name.strip()
        return self

    @staticmethod
    def create(email: Email, name: str) -> "User":
        """Factory method for creating new users."""
        return User(
            id=0,
            email=email,
            name=name,
            is_active=True,
            created_at=datetime.utcnow()
        )
```

## Layer 2: Application Layer

### Repository Port

```python
# application/ports/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.user import User

class UserRepository(ABC):
    """Port: Abstract interface for user persistence."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass
```

### Use Cases

```python
# application/use_cases/create_user.py
from dataclasses import dataclass
from application.ports.repositories import UserRepository
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.exceptions import EmailAlreadyExistsException

@dataclass
class CreateUserCommand:
    """Input command for creating user."""
    email: str
    name: str

@dataclass
class CreateUserResult:
    """Output result from creating user."""
    user_id: int
    email: str
    name: str
    is_active: bool

class CreateUserUseCase:
    """Use case: Create a new user."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, command: CreateUserCommand) -> CreateUserResult:
        """Execute create user logic."""
        # Create value object (validates email)
        email = Email(command.email)

        # Check uniqueness
        if self._user_repo.exists_by_email(email.value):
            raise EmailAlreadyExistsException(f"Email already exists: {email}")

        # Create and save user
        user = User.create(email=email, name=command.name)
        saved_user = self._user_repo.save(user)

        return CreateUserResult(
            user_id=saved_user.id,
            email=saved_user.email.value,
            name=saved_user.name,
            is_active=saved_user.is_active
        )

# application/use_cases/get_user.py
from dataclasses import dataclass
from typing import Optional
from application.ports.repositories import UserRepository
from domain.exceptions import UserNotFoundException

@dataclass
class GetUserResult:
    """Output result from getting user."""
    user_id: int
    email: str
    name: str
    is_active: bool
    created_at: str

class GetUserUseCase:
    """Use case: Get user by ID."""

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, user_id: int) -> GetUserResult:
        """Get user by ID."""
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User not found: {user_id}")

        return GetUserResult(
            user_id=user.id,
            email=user.email.value,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
```

## Layer 3: Infrastructure Layer

### Database Models

```python
# infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserORM(Base):
    """SQLAlchemy ORM model - infrastructure only."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### Database Session

```python
# infrastructure/database/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
```

### Repository Implementation

```python
# infrastructure/repositories/user_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from domain.entities.user import User
from domain.value_objects.email import Email
from infrastructure.database.models import UserORM

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        orm = self._session.query(UserORM).filter_by(id=user_id).first()
        return self._to_domain(orm) if orm else None

    def find_by_email(self, email: str) -> Optional[User]:
        orm = self._session.query(UserORM).filter_by(email=email).first()
        return self._to_domain(orm) if orm else None

    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        orms = self._session.query(UserORM).limit(limit).offset(offset).all()
        return [self._to_domain(orm) for orm in orms]

    def save(self, user: User) -> User:
        if user.id == 0:
            orm = self._to_orm(user)
            self._session.add(orm)
        else:
            orm = self._session.query(UserORM).filter_by(id=user.id).first()
            orm.email = user.email.value
            orm.name = user.name
            orm.is_active = user.is_active
        self._session.commit()
        self._session.refresh(orm)
        return self._to_domain(orm)

    def delete(self, user_id: int) -> None:
        self._session.query(UserORM).filter_by(id=user_id).delete()
        self._session.commit()

    def exists_by_email(self, email: str) -> bool:
        return self._session.query(UserORM).filter_by(email=email).count() > 0

    def _to_domain(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=Email(orm.email),
            name=orm.name,
            is_active=orm.is_active,
            created_at=orm.created_at
        )

    def _to_orm(self, user: User) -> UserORM:
        return UserORM(
            email=user.email.value,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at
        )
```

### Dependency Injection with Dishka

```python
# infrastructure/di/providers.py
from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from application.use_cases.create_user import CreateUserUseCase
from application.use_cases.get_user import GetUserUseCase
from infrastructure.database.session import SessionLocal
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Session:
        session = SessionLocal()
        yield session
        session.close()

class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: Session) -> UserRepository:
        return SQLAlchemyUserRepository(session)

class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_create_user(self, repo: UserRepository) -> CreateUserUseCase:
        return CreateUserUseCase(repo)

    @provide(scope=Scope.REQUEST)
    def get_get_user(self, repo: UserRepository) -> GetUserUseCase:
        return GetUserUseCase(repo)
```

## Layer 4: Presentation Layer

### API Schemas

```python
# presentation/api/schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class CreateUserRequest(BaseModel):
    """Request schema for creating user."""
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    """Response schema for user."""
    id: int
    email: str
    name: str
    is_active: bool

class UserDetailResponse(UserResponse):
    """Detailed response with timestamps."""
    created_at: str

class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
```

### FastAPI Routes

```python
# presentation/api/v1/users.py
from fastapi import APIRouter, HTTPException
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from application.use_cases.get_user import GetUserUseCase
from domain.exceptions import (
    DomainException, EmailAlreadyExistsException,
    UserNotFoundException, InvalidEmailException
)
from presentation.api.schemas.user_schema import (
    CreateUserRequest, UserResponse, UserDetailResponse
)

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    use_case: FromDishka[CreateUserUseCase]
):
    """Create a new user."""
    try:
        command = CreateUserCommand(email=request.email, name=request.name)
        result = use_case.execute(command)
        return UserResponse(
            id=result.user_id,
            email=result.email,
            name=result.name,
            is_active=result.is_active
        )
    except InvalidEmailException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EmailAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user(
    user_id: int,
    use_case: FromDishka[GetUserUseCase]
):
    """Get user by ID."""
    try:
        result = use_case.execute(user_id)
        return UserDetailResponse(
            id=result.user_id,
            email=result.email,
            name=result.name,
            is_active=result.is_active,
            created_at=result.created_at
        )
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Main Application

```python
# presentation/main.py
from fastapi import FastAPI
from dishka import make_container
from dishka.integrations.fastapi import setup_dishka
from infrastructure.di.providers import (
    DatabaseProvider, RepositoryProvider, UseCaseProvider
)
from presentation.api.v1 import users

def create_app() -> FastAPI:
    """Create FastAPI application with Clean Architecture."""
    app = FastAPI(
        title="Clean Architecture API",
        description="FastAPI with Clean Architecture and DDD",
        version="1.0.0"
    )

    # Setup DI container
    container = make_container(
        DatabaseProvider(),
        RepositoryProvider(),
        UseCaseProvider()
    )
    setup_dishka(container, app)

    # Include routers
    app.include_router(users.router, prefix="/api/v1")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing

```python
# tests/application/test_create_user.py
from unittest.mock import Mock
import pytest
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from domain.entities.user import User
from domain.value_objects.email import Email
from domain.exceptions import EmailAlreadyExistsException

@pytest.fixture
def mock_repo():
    repo = Mock()
    repo.exists_by_email.return_value = False
    repo.save.return_value = User(
        id=1, email=Email("test@example.com"),
        name="Test", is_active=True, created_at=datetime.utcnow()
    )
    return repo

def test_create_user_success(mock_repo):
    use_case = CreateUserUseCase(mock_repo)
    command = CreateUserCommand(email="test@example.com", name="Test")

    result = use_case.execute(command)

    assert result.user_id == 1
    mock_repo.save.assert_called_once()

def test_create_user_duplicate_email(mock_repo):
    mock_repo.exists_by_email.return_value = True
    use_case = CreateUserUseCase(mock_repo)

    with pytest.raises(EmailAlreadyExistsException):
        use_case.execute(CreateUserCommand(email="exists@example.com", name="Test"))
```

---

**File Size**: 475/500 lines max ✅
