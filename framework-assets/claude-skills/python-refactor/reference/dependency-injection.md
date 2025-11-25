# Dependency Injection in Python

**Comprehensive guide to implementing Dependency Injection (DI) for Clean Architecture applications using framework-agnostic patterns and Dishka DI framework.**

## Why Dependency Injection?

**Core Problem**: Hard-coded dependencies create tightly coupled code that's difficult to test and maintain.

di_benefits[7]{benefit,description,example}:
Testability,Replace real dependencies with mocks,Test use cases without database
Flexibility,Swap implementations without changing code,Switch from PostgreSQL to MongoDB
Decoupling,Modules don't know concrete implementations,Use case depends on ABC not SQLAlchemy
Single Responsibility,Objects don't create their dependencies,Factory handles object creation
Configuration,Centralized dependency configuration,All wiring in one place
Lifecycle Management,Control scope of dependencies (singleton request etc),Session per request not per call
Transparency,Dependencies explicit in constructor,Easy to see what a class needs

## Dependency Injection Patterns

### Pattern 1: Constructor Injection (Preferred)

**Inject dependencies through constructor - explicit and testable.**

```python
# ✅ PREFERRED: Constructor injection
class CreateUserUseCase:
    """Dependencies injected via constructor."""

    def __init__(
        self,
        user_repo: UserRepository,
        email_service: EmailService
    ):
        self._user_repo = user_repo
        self._email_service = email_service

    def execute(self, command: CreateUserCommand) -> CreateUserResult:
        user = User(...)
        self._user_repo.save(user)
        self._email_service.send_welcome(user)
        return CreateUserResult(user.id)
```

**Benefits:**
- Dependencies explicit and visible
- Easy to test with mocks
- Immutable after construction
- IDE autocomplete works

### Pattern 2: Method Injection

**Inject dependencies per method call - useful for request-scoped data.**

```python
# Method injection for request-scoped data
class AuditService:
    def log_action(
        self,
        action: str,
        user_context: UserContext  # Injected per call
    ) -> None:
        """user_context is request-specific, injected per call."""
        self._log(action, user_context.user_id, user_context.ip_address)
```

### Pattern 3: Abstract Factory

**Create dependencies through factory interface.**

```python
# application/ports/factories.py
from abc import ABC, abstractmethod

class RepositoryFactory(ABC):
    """Factory for creating repositories."""

    @abstractmethod
    def create_user_repository(self) -> UserRepository:
        pass

    @abstractmethod
    def create_order_repository(self) -> OrderRepository:
        pass

# infrastructure/factories.py
class SQLAlchemyRepositoryFactory(RepositoryFactory):
    """SQLAlchemy implementation of repository factory."""

    def __init__(self, session: Session):
        self._session = session

    def create_user_repository(self) -> UserRepository:
        return SQLAlchemyUserRepository(self._session)

    def create_order_repository(self) -> OrderRepository:
        return SQLAlchemyOrderRepository(self._session)
```

## Manual DI Implementation

### Simple Manual DI Container

```python
# infrastructure/di/container.py
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

class DIContainer:
    """Simple manual DI container."""

    def __init__(self):
        self._factories: dict[type, Callable] = {}
        self._singletons: dict[type, object] = {}

    def register(self, interface: type, factory: Callable, singleton: bool = False):
        """Register a factory for an interface."""
        self._factories[interface] = (factory, singleton)

    def resolve(self, interface: type[T]) -> T:
        """Resolve an instance of the interface."""
        if interface in self._singletons:
            return self._singletons[interface]

        factory, singleton = self._factories.get(interface, (None, False))
        if factory is None:
            raise ValueError(f"No factory registered for {interface}")

        instance = factory(self)  # Pass container for nested resolution

        if singleton:
            self._singletons[interface] = instance

        return instance

# Setup
container = DIContainer()

# Register infrastructure
container.register(Session, lambda c: SessionLocal(), singleton=False)
container.register(UserRepository, lambda c: SQLAlchemyUserRepository(c.resolve(Session)))
container.register(EmailService, lambda c: SMTPEmailService(), singleton=True)

# Register use cases
container.register(CreateUserUseCase, lambda c: CreateUserUseCase(
    c.resolve(UserRepository),
    c.resolve(EmailService)
))

# Usage
use_case = container.resolve(CreateUserUseCase)
result = use_case.execute(command)
```

## Dishka DI Framework

**Modern, type-safe DI framework for Python with FastAPI integration.**

### Installation

```bash
pip install dishka
```

### Basic Dishka Setup

```python
# infrastructure/di/providers.py
from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from application.use_cases.create_user import CreateUserUseCase
from infrastructure.database.session import SessionLocal
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

class InfrastructureProvider(Provider):
    """Provider for infrastructure dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Session:
        """Database session - per request."""
        return SessionLocal()

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: Session) -> UserRepository:
        """User repository - depends on session."""
        return SQLAlchemyUserRepository(session)

class ApplicationProvider(Provider):
    """Provider for application layer dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_create_user_use_case(
        self,
        user_repo: UserRepository
    ) -> CreateUserUseCase:
        """Create user use case with dependencies."""
        return CreateUserUseCase(user_repo)

# infrastructure/di/container.py
from dishka import make_container
from infrastructure.di.providers import InfrastructureProvider, ApplicationProvider

def create_container():
    """Create DI container with all providers."""
    return make_container(
        InfrastructureProvider(),
        ApplicationProvider()
    )

# Global container
container = create_container()
```

### Dishka Scopes

dishka_scopes[4]{scope,lifetime,use_case}:
Scope.APP,Application lifetime (singleton),Configuration services loggers
Scope.REQUEST,Single request/transaction,Database sessions repositories
Scope.ACTION,Single action within request,Temporary processing objects
Scope.STEP,Single step within action,Fine-grained short-lived objects

### Dishka with FastAPI

```python
# presentation/main.py
from fastapi import FastAPI
from dishka.integrations.fastapi import DishkaRoute, setup_dishka
from infrastructure.di.container import create_container

app = FastAPI()
container = create_container()
setup_dishka(container, app)

# presentation/api/v1/users.py
from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from presentation.api.schemas.user_schema import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"], route_class=DishkaRoute)

@router.post("/", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    use_case: FromDishka[CreateUserUseCase]  # Injected by Dishka
):
    """Create user endpoint with dependency injection."""
    command = CreateUserCommand(email=request.email, name=request.name)
    result = use_case.execute(command)
    return UserResponse(id=result.user_id, email=result.email, name=result.name)
```

### Complete Dishka Configuration

```python
# infrastructure/di/providers.py
from dishka import Provider, Scope, provide
from typing import AsyncIterator
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

class DatabaseProvider(Provider):
    """Database-related dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Session:
        """Synchronous database session."""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @provide(scope=Scope.REQUEST)
    async def get_async_session(self) -> AsyncIterator[AsyncSession]:
        """Async database session for async use cases."""
        async with async_session_maker() as session:
            yield session

class RepositoryProvider(Provider):
    """Repository implementations."""

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, session: Session) -> UserRepository:
        return SQLAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_order_repository(self, session: Session) -> OrderRepository:
        return SQLAlchemyOrderRepository(session)

class ServiceProvider(Provider):
    """External service adapters."""

    @provide(scope=Scope.APP)  # Singleton
    def get_email_service(self) -> EmailService:
        return SMTPEmailService(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT
        )

    @provide(scope=Scope.APP)
    def get_cache_service(self) -> CacheService:
        return RedisCacheService(settings.REDIS_URL)

class UseCaseProvider(Provider):
    """Application use cases."""

    @provide(scope=Scope.REQUEST)
    def get_create_user_use_case(
        self,
        user_repo: UserRepository,
        email_service: EmailService
    ) -> CreateUserUseCase:
        return CreateUserUseCase(user_repo, email_service)

    @provide(scope=Scope.REQUEST)
    def get_get_user_use_case(self, user_repo: UserRepository) -> GetUserUseCase:
        return GetUserUseCase(user_repo)

# infrastructure/di/container.py
from dishka import make_container

def create_container():
    """Create fully configured DI container."""
    return make_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
        UseCaseProvider()
    )
```

## Alternative DI Frameworks

### dependency-injector

```python
# Using dependency-injector library
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """DI container using dependency-injector."""

    config = providers.Configuration()

    # Database
    session = providers.Factory(SessionLocal)

    # Repositories
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=session
    )

    # Use cases
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        user_repo=user_repository
    )

# Usage
container = Container()
use_case = container.create_user_use_case()
```

### Pure FastAPI Depends

```python
# presentation/api/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from application.ports.repositories import UserRepository
from application.use_cases.create_user import CreateUserUseCase
from infrastructure.database.session import get_session
from infrastructure.repositories.user_repository import SQLAlchemyUserRepository

def get_user_repository(
    session: Session = Depends(get_session)
) -> UserRepository:
    """Get user repository with session."""
    return SQLAlchemyUserRepository(session)

def get_create_user_use_case(
    user_repo: UserRepository = Depends(get_user_repository)
) -> CreateUserUseCase:
    """Get create user use case with dependencies."""
    return CreateUserUseCase(user_repo)

# presentation/api/v1/users.py
@router.post("/")
def create_user(
    request: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """Endpoint with FastAPI Depends injection."""
    return use_case.execute(CreateUserCommand(...))
```

## Testing with DI

### Testing Use Cases with Mock Dependencies

```python
# tests/application/test_create_user.py
from unittest.mock import Mock, AsyncMock
import pytest
from application.use_cases.create_user import CreateUserUseCase, CreateUserCommand
from domain.entities.user import User
from domain.value_objects.email import Email

@pytest.fixture
def mock_user_repo():
    """Create mock user repository."""
    repo = Mock()
    repo.find_by_email.return_value = None
    repo.save.return_value = User(
        id=1,
        email=Email("test@example.com"),
        name="Test",
        is_active=True
    )
    return repo

@pytest.fixture
def mock_email_service():
    """Create mock email service."""
    service = Mock()
    service.send_welcome.return_value = None
    return service

def test_create_user_success(mock_user_repo, mock_email_service):
    """Test successful user creation with mocked dependencies."""
    # Arrange
    use_case = CreateUserUseCase(mock_user_repo, mock_email_service)
    command = CreateUserCommand(email="test@example.com", name="Test")

    # Act
    result = use_case.execute(command)

    # Assert
    assert result.user_id == 1
    mock_user_repo.save.assert_called_once()
    mock_email_service.send_welcome.assert_called_once()
```

### Testing with Dishka Container

```python
# tests/conftest.py
import pytest
from dishka import make_container, Provider, provide, Scope
from unittest.mock import Mock

class TestProvider(Provider):
    """Test provider with mocked dependencies."""

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self) -> UserRepository:
        mock = Mock()
        mock.find_by_email.return_value = None
        return mock

@pytest.fixture
def test_container():
    """Create test container with mocks."""
    return make_container(TestProvider())

@pytest.fixture
def use_case(test_container):
    """Get use case from test container."""
    with test_container() as request_container:
        return request_container.get(CreateUserUseCase)
```

## DI Best Practices

di_best_practices[10]{practice,description,example}:
Constructor injection,Prefer constructor injection over property/method,All deps in __init__
Interface segregation,Depend on small focused interfaces,EmailSender not MonolithicService
Explicit dependencies,All dependencies visible in constructor,No hidden service locator
Scope awareness,Use appropriate scope for each dependency,Session per request not singleton
Late binding,Resolve dependencies at runtime not import time,Container.resolve() not global instance
Test doubles,Design for easy mocking and stubbing,ABC allows Mock implementation
Avoid service locator,Don't pass container around,Inject specific deps not container
Single responsibility,Each provider handles one concern,DatabaseProvider ServiceProvider
Configuration isolation,Keep config separate from DI wiring,Use environment variables
Graceful cleanup,Handle resource cleanup properly,Context managers or finally blocks

## Common DI Mistakes

### Mistake 1: Service Locator Anti-pattern

```python
# ❌ WRONG: Passing container around
class CreateUserUseCase:
    def __init__(self, container: DIContainer):
        self._container = container

    def execute(self, command):
        # Resolving inside method - hidden dependency!
        repo = self._container.resolve(UserRepository)
```

**Fix**: Inject concrete dependencies

```python
# ✅ CORRECT: Explicit dependencies
class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
```

### Mistake 2: Wrong Scope

```python
# ❌ WRONG: Singleton session
@provide(scope=Scope.APP)  # Session as singleton!
def get_session(self) -> Session:
    return SessionLocal()
```

**Fix**: Request scope for sessions

```python
# ✅ CORRECT: Session per request
@provide(scope=Scope.REQUEST)
def get_session(self) -> Session:
    return SessionLocal()
```

### Mistake 3: Circular Dependencies

```python
# ❌ WRONG: Circular dependency
class ServiceA:
    def __init__(self, service_b: ServiceB): pass

class ServiceB:
    def __init__(self, service_a: ServiceA): pass
```

**Fix**: Introduce interface or restructure

```python
# ✅ CORRECT: Break cycle with interface
class ServiceA:
    def __init__(self, service_b: ServiceBInterface): pass

class ServiceB(ServiceBInterface):
    def __init__(self): pass  # No dependency on A
```

## DI Checklist

di_checklist[12]{check,requirement}:
Constructor injection used,All dependencies injected via constructor
ABCs for dependencies,Depend on abstract interfaces not concrete classes
Explicit dependencies,No hidden dependencies or service locators
Correct scopes,Session request-scoped services app-scoped
No circular dependencies,Dependency graph is acyclic
Testable design,Can create instances with mocks
Single container,One container configured at startup
Provider organization,Providers organized by layer/concern
Resource cleanup,Sessions and connections properly closed
Configuration separate,Settings not hard-coded in providers
Type hints,All dependencies properly typed
Documentation,Complex DI setups documented

---

**File Size**: 460/500 lines max ✅
