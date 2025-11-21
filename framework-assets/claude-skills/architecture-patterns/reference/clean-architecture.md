# Clean Architecture Reference

**Organize code by layers with dependency rule: dependencies point inward.**

## Overview

Clean Architecture organizes code into concentric layers where inner layers know nothing about outer layers.

clean_architecture_layers[4]{layer,position,responsibility,examples}:
Entities,Innermost,Enterprise business rules and core domain models,User Order Product domain entities
Use Cases,Inner,Application-specific business rules,CreateUser PlaceOrder ProcessPayment
Interface Adapters,Outer,Convert data between use cases and external systems,Controllers Presenters Gateways Repositories
Frameworks & Drivers,Outermost,External tools and frameworks,Database Web UI External APIs

## Dependency Rule

**THE FUNDAMENTAL RULE:**
- Dependencies point **INWARD** only
- Inner layers know **NOTHING** about outer layers
- Outer layers depend on inner layers
- Inner layers define interfaces, outer layers implement them

dependency_flow[4]{from_layer,to_layer,allowed,mechanism}:
Frameworks,Interface Adapters,Yes,Direct dependency on controllers/gateways
Interface Adapters,Use Cases,Yes,Direct dependency on use case interfaces
Use Cases,Entities,Yes,Direct dependency on domain entities
Entities,Use Cases,No,Entities don't know about use cases

---

## Layer 4: Entities (Core Domain)

**Purpose:** Encapsulate enterprise-wide business rules and core domain logic.

**Characteristics:**
- Pure business logic
- No framework dependencies
- No infrastructure dependencies
- Highly reusable across applications
- Changes least frequently

### Example - User Entity

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class UserStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

@dataclass
class User:
    """Core domain entity - pure business logic"""
    id: int
    email: str
    name: str
    status: UserStatus
    created_at: datetime
    last_login: datetime | None = None

    def is_active(self) -> bool:
        """Business rule: what makes user active"""
        return self.status == UserStatus.ACTIVE

    def can_login(self) -> bool:
        """Business rule: who can login"""
        return self.is_active()

    def suspend(self) -> None:
        """Business rule: suspend user"""
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot suspend deleted user")
        self.status = UserStatus.SUSPENDED

    def activate(self) -> None:
        """Business rule: activate user"""
        if self.status == UserStatus.DELETED:
            raise ValueError("Cannot activate deleted user")
        self.status = UserStatus.ACTIVE

    def record_login(self) -> None:
        """Business rule: record login time"""
        if not self.can_login():
            raise ValueError("User cannot login")
        self.last_login = datetime.now()


@dataclass
class Order:
    """Core domain entity with business rules"""
    id: str
    customer_id: str
    items: list['OrderItem']
    status: str
    created_at: datetime

    def total(self) -> float:
        """Business rule: calculate order total"""
        return sum(item.subtotal() for item in self.items)

    def can_be_cancelled(self) -> bool:
        """Business rule: when order can be cancelled"""
        return self.status in ["pending", "confirmed"]

    def cancel(self) -> None:
        """Business rule: cancel order"""
        if not self.can_be_cancelled():
            raise ValueError(f"Cannot cancel order with status {self.status}")
        self.status = "cancelled"


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

    def subtotal(self) -> float:
        return self.quantity * self.unit_price
```

---

## Layer 3: Use Cases (Application Business Rules)

**Purpose:** Contain application-specific business rules and orchestrate data flow.

**Characteristics:**
- Orchestrate entity interactions
- Implement application workflows
- Define interfaces for dependencies (repositories, gateways)
- Independent of UI or database
- Changes when application requirements change

### Example - Use Cases with Interface Definitions

```python
from abc import ABC, abstractmethod

# Use Case defines what it needs (interface)
class IUserRepository(ABC):
    """Interface defined by use case layer"""
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class IEmailGateway(ABC):
    """Interface defined by use case layer"""
    @abstractmethod
    def send_welcome_email(self, user: User) -> bool:
        pass


# Use Case implements application logic
class CreateUserUseCase:
    """Application-specific business rule: how to create user"""

    def __init__(
        self,
        user_repository: IUserRepository,
        email_gateway: IEmailGateway
    ):
        self.user_repository = user_repository
        self.email_gateway = email_gateway

    def execute(self, email: str, name: str) -> User:
        # Validate uniqueness (application rule)
        existing = self.user_repository.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        # Create entity
        user = User(
            id=0,  # Will be assigned by repository
            email=email,
            name=name,
            status=UserStatus.ACTIVE,
            created_at=datetime.now()
        )

        # Save to repository
        saved_user = self.user_repository.save(user)

        # Send welcome email (application rule)
        try:
            self.email_gateway.send_welcome_email(saved_user)
        except Exception as e:
            # Log but don't fail user creation
            print(f"Failed to send welcome email: {e}")

        return saved_user


class GetUserUseCase:
    """Application-specific business rule: how to retrieve user"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        if not user.is_active():
            raise ValueError(f"User {user_id} is not active")

        return user


class UpdateUserEmailUseCase:
    """Application-specific business rule: how to update email"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, new_email: str) -> User:
        # Check email uniqueness
        existing = self.user_repository.find_by_email(new_email)
        if existing and existing.id != user_id:
            raise ValueError("Email already in use")

        # Get and update user
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.email = new_email
        return self.user_repository.save(user)
```

---

## Layer 2: Interface Adapters

**Purpose:** Convert data between use cases and external systems.

**Characteristics:**
- Controllers (API handlers)
- Presenters (format output)
- Gateways (external services)
- Repositories (data access)
- Implement interfaces defined by use cases
- Convert between domain models and external formats

### Example - Controllers (API Layer)

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

# DTOs for API layer
class CreateUserRequest(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    status: str
    created_at: str

    @staticmethod
    def from_entity(user: User) -> 'UserResponse':
        """Convert domain entity to API response"""
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            status=user.status.value,
            created_at=user.created_at.isoformat()
        )


# Controller - converts HTTP to use case calls
class UserController:
    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        get_user_use_case: GetUserUseCase
    ):
        self.create_user_use_case = create_user_use_case
        self.get_user_use_case = get_user_use_case

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """Adapter: HTTP request → Use Case → HTTP response"""
        try:
            user = self.create_user_use_case.execute(
                email=request.email,
                name=request.name
            )
            return UserResponse.from_entity(user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user(self, user_id: int) -> UserResponse:
        """Adapter: HTTP request → Use Case → HTTP response"""
        try:
            user = self.get_user_use_case.execute(user_id)
            return UserResponse.from_entity(user)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
```

### Example - Repository Implementation

```python
from sqlalchemy.orm import Session

# Database model (ORM)
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    last_login = Column(DateTime, nullable=True)


# Repository - implements interface from use case layer
class SQLAlchemyUserRepository(IUserRepository):
    """Adapter: Use case interface → Database"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def save(self, user: User) -> User:
        """Convert domain entity to database model"""
        if user.id == 0:
            # Create new
            db_user = UserModel(
                email=user.email,
                name=user.name,
                status=user.status.value,
                created_at=user.created_at,
                last_login=user.last_login
            )
            self.db.add(db_user)
        else:
            # Update existing
            db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
            db_user.email = user.email
            db_user.name = user.name
            db_user.status = user.status.value
            db_user.last_login = user.last_login

        self.db.commit()
        self.db.refresh(db_user)

        # Convert back to domain entity
        return self._to_entity(db_user)

    def find_by_id(self, user_id: int) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(db_user) if db_user else None

    def find_by_email(self, email: str) -> User | None:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_user) if db_user else None

    def delete(self, user_id: int) -> bool:
        result = self.db.query(UserModel).filter(UserModel.id == user_id).delete()
        self.db.commit()
        return result > 0

    def _to_entity(self, db_user: UserModel) -> User:
        """Convert database model to domain entity"""
        return User(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            status=UserStatus(db_user.status),
            created_at=db_user.created_at,
            last_login=db_user.last_login
        )
```

---

## Layer 1: Frameworks & Drivers

**Purpose:** External tools, frameworks, and infrastructure.

**Characteristics:**
- Database (PostgreSQL, MongoDB)
- Web framework (FastAPI, Flask)
- UI framework (React)
- External APIs
- Most volatile layer (changes most frequently)

### Example - Application Wiring

```python
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Framework setup
app = FastAPI()
engine = create_engine("postgresql://localhost/mydb")
SessionLocal = sessionmaker(bind=engine)

# Dependency injection setup
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Session = Depends(get_db)):
    return SQLAlchemyUserRepository(db)


def get_email_gateway():
    return SMTPEmailGateway(smtp_config)


def get_create_user_use_case(
    repository: IUserRepository = Depends(get_user_repository),
    email_gateway: IEmailGateway = Depends(get_email_gateway)
):
    return CreateUserUseCase(repository, email_gateway)


def get_user_controller(
    create_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    get_use_case: GetUserUseCase = Depends(get_user_use_case)
):
    return UserController(create_use_case, get_use_case)


# API routes
@app.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.create_user(request)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.get_user(user_id)
```

---

## Benefits of Clean Architecture

architecture_benefits[8]{benefit,description,impact}:
Independence,Core business logic independent of frameworks,Easy to change frameworks without rewriting business logic
Testability,Business rules can be tested without UI or database,Fast comprehensive unit tests
Flexibility,Easy to swap implementations,Change database or UI without affecting use cases
Maintainability,Clear separation of concerns,Easy to locate and modify code
Scalability,Well-defined boundaries,Can scale individual layers independently
Team collaboration,Teams can work on different layers,Reduced merge conflicts clearer responsibilities
Technology agnostic,Core logic doesn't depend on specific technologies,Migrate technologies without rewriting business logic
Domain-focused,Architecture emphasizes business rules,Better alignment with business needs

---

**File Size**: 248/500 lines max ✅
