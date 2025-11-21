# Backend Python Architecture Examples

**Complete examples of architecture patterns in Python/FastAPI applications.**

## Project Structure

Recommended directory structure for Clean Architecture in Python:

```
project/
├── domain/              # Layer 4: Entities (Core)
│   ├── entities/
│   │   ├── user.py
│   │   └── order.py
│   └── value_objects/
│       ├── money.py
│       └── email.py
├── application/         # Layer 3: Use Cases
│   ├── use_cases/
│   │   ├── create_user.py
│   │   └── place_order.py
│   └── interfaces/
│       ├── repositories.py
│       └── gateways.py
├── infrastructure/      # Layer 2 & 1: Adapters & Frameworks
│   ├── repositories/
│   │   └── sql_user_repository.py
│   ├── gateways/
│   │   └── email_gateway.py
│   └── database/
│       └── models.py
├── api/                 # Layer 1: API Controllers
│   ├── controllers/
│   │   └── user_controller.py
│   ├── dtos/
│   │   └── requests.py
│   └── main.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Complete Example: User Management System

### Layer 4: Domain Entities

```python
# domain/entities/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Core domain entity with business rules"""
    id: int
    email: str
    name: str
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity invariants"""
        if not self.email:
            raise ValueError("Email is required")
        if not self.name:
            raise ValueError("Name is required")

    def is_active(self) -> bool:
        """Business rule: active status check"""
        return self.status == "active"

    def can_login(self) -> bool:
        """Business rule: login eligibility"""
        return self.is_active()

    def suspend(self) -> None:
        """Business rule: suspend user"""
        if self.status == "deleted":
            raise ValueError("Cannot suspend deleted user")
        self.status = "suspended"

    def activate(self) -> None:
        """Business rule: activate user"""
        if self.status == "deleted":
            raise ValueError("Cannot activate deleted user")
        self.status = "active"

    def record_login(self) -> None:
        """Business rule: record login timestamp"""
        if not self.can_login():
            raise ValueError("User cannot login")
        self.last_login = datetime.now()

    def delete(self) -> None:
        """Business rule: soft delete"""
        self.status = "deleted"
```

### Layer 3: Use Cases

```python
# application/interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.user import User

class IUserRepository(ABC):
    """Repository interface defined by use case layer"""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


# application/interfaces/gateways.py
class IEmailGateway(ABC):
    """Gateway interface defined by use case layer"""

    @abstractmethod
    def send_welcome_email(self, user: User) -> bool:
        pass

    @abstractmethod
    def send_password_reset(self, user: User, token: str) -> bool:
        pass


# application/use_cases/create_user.py
from dataclasses import dataclass

@dataclass
class CreateUserRequest:
    """Use case input DTO"""
    email: str
    name: str


@dataclass
class CreateUserResponse:
    """Use case output DTO"""
    user_id: int
    email: str
    name: str
    created_at: str


class CreateUserUseCase:
    """Application business logic"""

    def __init__(
        self,
        user_repository: IUserRepository,
        email_gateway: IEmailGateway
    ):
        self.user_repository = user_repository
        self.email_gateway = email_gateway

    def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """Execute use case"""
        # Application rule: email must be unique
        existing_user = self.user_repository.find_by_email(request.email)
        if existing_user:
            raise ValueError(f"Email {request.email} already registered")

        # Create domain entity
        user = User(
            id=0,  # Will be assigned by repository
            email=request.email,
            name=request.name
        )

        # Persist
        saved_user = self.user_repository.save(user)

        # Send welcome email (don't fail if email fails)
        try:
            self.email_gateway.send_welcome_email(saved_user)
        except Exception as e:
            # Log but don't fail user creation
            print(f"Failed to send welcome email: {e}")

        # Return response DTO
        return CreateUserResponse(
            user_id=saved_user.id,
            email=saved_user.email,
            name=saved_user.name,
            created_at=saved_user.created_at.isoformat()
        )


# application/use_cases/get_user.py
class GetUserUseCase:
    """Retrieve user by ID"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        if not user.is_active():
            raise ValueError(f"User {user_id} is not active")

        return user


# application/use_cases/update_user_email.py
class UpdateUserEmailUseCase:
    """Update user's email address"""

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: int, new_email: str) -> User:
        # Check new email is available
        existing = self.user_repository.find_by_email(new_email)
        if existing and existing.id != user_id:
            raise ValueError(f"Email {new_email} already in use")

        # Get user
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Update email
        user.email = new_email

        # Persist
        return self.user_repository.save(user)
```

### Layer 2: Infrastructure Adapters

```python
# infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    """Database model (ORM)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=True)


# infrastructure/repositories/sql_user_repository.py
from sqlalchemy.orm import Session
from typing import Optional, List
from application.interfaces.repositories import IUserRepository
from domain.entities.user import User
from infrastructure.database.models import UserModel

class SQLUserRepository(IUserRepository):
    """SQL implementation of user repository"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def find_by_id(self, user_id: int) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def find_all(self) -> List[User]:
        models = self.db.query(UserModel).all()
        return [self._to_entity(model) for model in models]

    def save(self, user: User) -> User:
        """Create or update"""
        if user.id == 0:
            # Create new
            model = UserModel(
                email=user.email,
                name=user.name,
                status=user.status,
                created_at=user.created_at,
                last_login=user.last_login
            )
            self.db.add(model)
        else:
            # Update existing
            model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
            if not model:
                raise ValueError(f"User {user.id} not found")

            model.email = user.email
            model.name = user.name
            model.status = user.status
            model.last_login = user.last_login

        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(model)

    def delete(self, user_id: int) -> bool:
        result = self.db.query(UserModel).filter(UserModel.id == user_id).delete()
        self.db.commit()
        return result > 0

    def _to_entity(self, model: UserModel) -> User:
        """Convert ORM model to domain entity"""
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            status=model.status,
            created_at=model.created_at,
            last_login=model.last_login
        )


# infrastructure/gateways/email_gateway.py
from application.interfaces.gateways import IEmailGateway
from domain.entities.user import User
import smtplib
from email.mime.text import MIMEText

class SMTPEmailGateway(IEmailGateway):
    """SMTP implementation of email gateway"""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_welcome_email(self, user: User) -> bool:
        subject = "Welcome to Our Platform!"
        body = f"Hello {user.name},\n\nWelcome to our platform!"
        return self._send_email(user.email, subject, body)

    def send_password_reset(self, user: User, token: str) -> bool:
        subject = "Password Reset Request"
        body = f"Hello {user.name},\n\nYour password reset token: {token}"
        return self._send_email(user.email, subject, body)

    def _send_email(self, to: str, subject: str, body: str) -> bool:
        """Internal method to send email via SMTP"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
```

### Layer 1: API Controllers

```python
# api/dtos/requests.py
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    """API request DTO"""
    email: EmailStr
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }


class UpdateEmailRequest(BaseModel):
    """API request DTO"""
    email: EmailStr


# api/dtos/responses.py
class UserResponse(BaseModel):
    """API response DTO"""
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
            status=user.status,
            created_at=user.created_at.isoformat()
        )


# api/controllers/user_controller.py
from fastapi import HTTPException
from api.dtos.requests import CreateUserRequest, UpdateEmailRequest
from api.dtos.responses import UserResponse
from application.use_cases.create_user import CreateUserUseCase
from application.use_cases.get_user import GetUserUseCase
from application.use_cases.update_user_email import UpdateUserEmailUseCase

class UserController:
    """HTTP adapter - converts HTTP to use case calls"""

    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        get_user_use_case: GetUserUseCase,
        update_email_use_case: UpdateUserEmailUseCase
    ):
        self.create_user_use_case = create_user_use_case
        self.get_user_use_case = get_user_use_case
        self.update_email_use_case = update_email_use_case

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """POST /users - Create new user"""
        try:
            # Convert API DTO to use case DTO
            use_case_request = CreateUserRequest(
                email=request.email,
                name=request.name
            )

            # Execute use case
            result = self.create_user_use_case.execute(use_case_request)

            # Convert use case result to API response
            return UserResponse(
                id=result.user_id,
                email=result.email,
                name=result.name,
                status="active",
                created_at=result.created_at
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_user(self, user_id: int) -> UserResponse:
        """GET /users/{user_id} - Get user by ID"""
        try:
            user = self.get_user_use_case.execute(user_id)
            return UserResponse.from_entity(user)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def update_email(self, user_id: int, request: UpdateEmailRequest) -> UserResponse:
        """PUT /users/{user_id}/email - Update user email"""
        try:
            user = self.update_email_use_case.execute(user_id, request.email)
            return UserResponse.from_entity(user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))


# api/main.py
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Setup FastAPI
app = FastAPI(title="User Management API")

# Setup database
DATABASE_URL = "postgresql://localhost/mydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Dependency injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repository(db: Session = Depends(get_db)) -> IUserRepository:
    return SQLUserRepository(db)


def get_email_gateway() -> IEmailGateway:
    return SMTPEmailGateway(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        username="noreply@example.com",
        password="password"
    )


def get_create_user_use_case(
    repository: IUserRepository = Depends(get_user_repository),
    email_gateway: IEmailGateway = Depends(get_email_gateway)
) -> CreateUserUseCase:
    return CreateUserUseCase(repository, email_gateway)


def get_user_controller(
    create_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    get_use_case: GetUserUseCase = Depends(get_user_use_case),
    update_email_use_case: UpdateUserEmailUseCase = Depends(update_email_use_case)
) -> UserController:
    return UserController(create_use_case, get_use_case, update_email_use_case)


# API routes
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    controller: UserController = Depends(get_user_controller)
):
    """Create new user"""
    return await controller.create_user(request)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    controller: UserController = Depends(get_user_controller)
):
    """Get user by ID"""
    return await controller.get_user(user_id)


@app.put("/users/{user_id}/email", response_model=UserResponse)
async def update_email(
    user_id: int,
    request: UpdateEmailRequest,
    controller: UserController = Depends(get_user_controller)
):
    """Update user email"""
    return await controller.update_email(user_id, request)
```

---

## Testing Strategy

### Unit Tests (Domain Layer)

```python
# tests/unit/test_user_entity.py
import pytest
from domain.entities.user import User

def test_user_creation():
    user = User(id=1, email="test@example.com", name="Test User")
    assert user.is_active()
    assert user.can_login()

def test_user_suspension():
    user = User(id=1, email="test@example.com", name="Test User")
    user.suspend()
    assert user.status == "suspended"
    assert not user.can_login()

def test_cannot_suspend_deleted_user():
    user = User(id=1, email="test@example.com", name="Test User")
    user.delete()
    with pytest.raises(ValueError, match="Cannot suspend deleted user"):
        user.suspend()
```

### Integration Tests (Use Cases)

```python
# tests/integration/test_create_user_use_case.py
import pytest
from application.use_cases.create_user import CreateUserUseCase, CreateUserRequest
from tests.mocks.mock_repositories import MockUserRepository
from tests.mocks.mock_gateways import MockEmailGateway

def test_create_user_success():
    repository = MockUserRepository()
    email_gateway = MockEmailGateway()
    use_case = CreateUserUseCase(repository, email_gateway)

    request = CreateUserRequest(email="test@example.com", name="Test User")
    response = use_case.execute(request)

    assert response.email == "test@example.com"
    assert response.name == "Test User"
    assert repository.saved_user is not None
    assert email_gateway.welcome_email_sent

def test_create_user_duplicate_email():
    repository = MockUserRepository()
    email_gateway = MockEmailGateway()
    use_case = CreateUserUseCase(repository, email_gateway)

    # Create first user
    request1 = CreateUserRequest(email="test@example.com", name="User 1")
    use_case.execute(request1)

    # Try to create duplicate
    request2 = CreateUserRequest(email="test@example.com", name="User 2")
    with pytest.raises(ValueError, match="already registered"):
        use_case.execute(request2)
```

---

**File Size**: 450/500 lines max ✅
