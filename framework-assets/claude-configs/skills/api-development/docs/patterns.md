# Patterns - API Development

This document covers common design patterns, anti-patterns, and architectural patterns for API development. Understanding these patterns helps you build robust, scalable APIs and avoid common pitfalls.

## Table of Contents

- [1. Repository Pattern](#1-repository-pattern)
- [2. Service Layer Pattern](#2-service-layer-pattern)
- [3. Dependency Injection Pattern](#3-dependency-injection-pattern)
- [4. Circuit Breaker Pattern](#4-circuit-breaker-pattern)
- [5. Saga Pattern](#5-saga-pattern)
- [6. API Gateway Pattern](#6-api-gateway-pattern)
- [7. Backend for Frontend (BFF) Pattern](#7-backend-for-frontend-bff-pattern)
- [8. Data Transfer Object (DTO) Pattern](#8-data-transfer-object-dto-pattern)
- [9. Pagination Patterns](#9-pagination-patterns)
- [10. Bulk Operations Pattern](#10-bulk-operations-pattern)
- [11. Async Processing Pattern](#11-async-processing-pattern)
- [12. Anti-Patterns to Avoid](#12-anti-patterns-to-avoid)

---

## 1. Repository Pattern

### What It Is

The Repository pattern abstracts data access logic, providing a collection-like interface for accessing domain objects.

### When to Use

- Complex database queries
- Multiple data sources
- Need to swap data layers (e.g., SQL to NoSQL)
- Testing with mock data

### Implementation

```python
# repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from models import User

class UserRepository(ABC):
    """Abstract repository interface"""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class SQLAlchemyUserRepository(UserRepository):
    """Concrete repository implementation"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False


# Usage in endpoints
from fastapi import Depends

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    repo: UserRepository = Depends(get_user_repository)
):
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Benefits

- ✅ Separation of concerns
- ✅ Easy to test with mock repositories
- ✅ Database-agnostic code
- ✅ Centralized data access logic

### When Not to Use

- ❌ Simple CRUD operations
- ❌ Single data source with no plans to change
- ❌ Very small applications

---

## 2. Service Layer Pattern

### What It Is

The Service Layer pattern encapsulates business logic, separating it from HTTP concerns and data access.

### When to Use

- Complex business logic
- Multiple repository interactions
- Transaction management
- Reusable business operations

### Implementation

```python
# services/user_service.py
from typing import Optional
from repositories import UserRepository
from schemas import UserCreate, UserUpdate
from models import User
from utils import hash_password, send_welcome_email

class UserService:
    """Business logic for user operations"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> User:
        """Create user with business logic"""
        # Check if email exists
        if self.repository.get_by_email(user_data.email):
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        user = self.repository.create(user)

        # Send welcome email (async task)
        send_welcome_email.delay(user.email)

        return user

    def update_user(self, user_id: int, updates: UserUpdate) -> User:
        """Update user with validation"""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Validate email uniqueness if changing
        if updates.email and updates.email != user.email:
            if self.repository.get_by_email(updates.email):
                raise ValueError("Email already in use")

        # Apply updates
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(user, field, value)

        return self.repository.update(user)

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user (soft delete)"""
        user = self.repository.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        self.repository.update(user)

        # Cancel user subscriptions
        cancel_subscriptions(user_id)

        # Send deactivation email
        send_deactivation_email.delay(user.email)

        return True


# Dependency
def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)

# Usage in endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Endpoint delegates to service layer"""
    try:
        user = service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Benefits

- ✅ Business logic separated from HTTP layer
- ✅ Reusable across different interfaces (REST, GraphQL, CLI)
- ✅ Easy to test in isolation
- ✅ Clear transaction boundaries

---

## 3. Dependency Injection Pattern

### What It Is

Dependency Injection provides dependencies to components rather than having components create them.

### When to Use

- Need to swap implementations (e.g., testing)
- Complex dependency graphs
- Configuration management
- Cross-cutting concerns

### Implementation

```python
# dependencies.py
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Optional

# Database dependency
def get_db():
    """Provide database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = authorization.replace("Bearer ", "")
    user = verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Authorization dependency
def require_admin(current_user = Depends(get_current_user)):
    """Require admin role"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Settings dependency
from functools import lru_cache

@lru_cache()
def get_settings():
    """Cached settings"""
    return Settings()

# Complex dependency chain
class Pagination:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100)
    ):
        self.skip = skip
        self.limit = limit

# Usage with multiple dependencies
@app.get("/admin/users")
async def list_users_admin(
    pagination: Pagination = Depends(),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """Multiple injected dependencies"""
    users = db.query(User)\
        .offset(pagination.skip)\
        .limit(pagination.limit)\
        .all()
    return users
```

### Testing with DI

```python
# test_api.py
from fastapi.testclient import TestClient

def override_get_db():
    """Test database"""
    return TestDB()

def override_get_current_user():
    """Mock user"""
    return User(id=1, username="test", is_admin=True)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_protected_endpoint():
    """Test with overridden dependencies"""
    response = client.get("/protected")
    assert response.status_code == 200
```

---

## 4. Circuit Breaker Pattern

### What It Is

Circuit Breaker prevents cascading failures by stopping requests to failing services.

### When to Use

- Calling external APIs
- Microservices communication
- Database connections
- Any fallible external dependency

### Implementation

```python
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Exception = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to retry"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.timeout)
        )

# Usage
import httpx

payment_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

async def process_payment(payment_data: dict):
    """Call external payment API with circuit breaker"""
    async with httpx.AsyncClient() as client:
        response = await payment_breaker.call(
            client.post,
            "https://payment-api.example.com/charge",
            json=payment_data
        )
        return response.json()

@app.post("/orders/{order_id}/pay")
async def pay_order(order_id: int, payment_data: PaymentData):
    try:
        result = await process_payment(payment_data.dict())
        return {"status": "success", "transaction": result}
    except Exception as e:
        # Circuit is open or payment failed
        return {"status": "failed", "message": "Payment service unavailable"}
```

---

## 5. Saga Pattern

### What It Is

Saga pattern manages distributed transactions across multiple services using compensating transactions.

### When to Use

- Microservices transactions
- Multi-step business processes
- Need rollback capability
- Eventual consistency acceptable

### Implementation

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum

class SagaStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"

class SagaStep(ABC):
    """Abstract saga step"""

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the step"""
        pass

    @abstractmethod
    async def compensate(self, context: Dict[str, Any]):
        """Compensate (rollback) the step"""
        pass

class Saga:
    """Saga orchestrator"""

    def __init__(self):
        self.steps: List[SagaStep] = []
        self.executed_steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING

    def add_step(self, step: SagaStep):
        """Add step to saga"""
        self.steps.append(step)

    async def execute(self, initial_context: Dict[str, Any]):
        """Execute all steps"""
        context = initial_context.copy()

        try:
            for step in self.steps:
                result = await step.execute(context)
                context.update(result)
                self.executed_steps.append(step)

            self.status = SagaStatus.COMPLETED
            return context

        except Exception as e:
            self.status = SagaStatus.FAILED
            await self._compensate(context)
            raise

    async def _compensate(self, context: Dict[str, Any]):
        """Rollback executed steps in reverse order"""
        self.status = SagaStatus.COMPENSATING

        for step in reversed(self.executed_steps):
            try:
                await step.compensate(context)
            except Exception as e:
                # Log compensation failure
                print(f"Compensation failed for {step}: {e}")

# Example: Order processing saga
class ReserveInventoryStep(SagaStep):
    async def execute(self, context: Dict[str, Any]):
        order = context['order']
        # Reserve inventory
        reservation_id = await inventory_service.reserve(order.items)
        return {'reservation_id': reservation_id}

    async def compensate(self, context: Dict[str, Any]):
        # Release inventory
        await inventory_service.release(context['reservation_id'])

class ChargePaymentStep(SagaStep):
    async def execute(self, context: Dict[str, Any]):
        payment = context['payment']
        # Charge payment
        transaction_id = await payment_service.charge(payment)
        return {'transaction_id': transaction_id}

    async def compensate(self, context: Dict[str, Any]):
        # Refund payment
        await payment_service.refund(context['transaction_id'])

class CreateShipmentStep(SagaStep):
    async def execute(self, context: Dict[str, Any]):
        order = context['order']
        # Create shipment
        shipment_id = await shipping_service.create(order)
        return {'shipment_id': shipment_id}

    async def compensate(self, context: Dict[str, Any]):
        # Cancel shipment
        await shipping_service.cancel(context['shipment_id'])

# Usage
@app.post("/orders")
async def create_order(order: OrderCreate):
    """Create order using saga pattern"""
    saga = Saga()
    saga.add_step(ReserveInventoryStep())
    saga.add_step(ChargePaymentStep())
    saga.add_step(CreateShipmentStep())

    try:
        context = await saga.execute({
            'order': order,
            'payment': order.payment_info
        })
        return {
            "status": "success",
            "order_id": context.get('order_id')
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": "Order creation failed, all changes rolled back"
        }
```

---

## 6. API Gateway Pattern

### What It Is

API Gateway provides a single entry point for multiple backend services, handling routing, authentication, rate limiting, and aggregation.

### When to Use

- Microservices architecture
- Multiple backend services
- Need centralized authentication
- API composition required

### Implementation

```python
from fastapi import FastAPI, Request, HTTPException
from httpx import AsyncClient
from typing import Dict, Any

app = FastAPI(title="API Gateway")

# Service registry
SERVICES = {
    "users": "http://users-service:8001",
    "orders": "http://orders-service:8002",
    "products": "http://products-service:8003"
}

async def forward_request(
    service: str,
    path: str,
    method: str,
    headers: Dict[str, str],
    body: Any = None
):
    """Forward request to backend service"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    async with AsyncClient() as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=body
        )
        return response

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(
    service: str,
    path: str,
    request: Request
):
    """Route requests to appropriate service"""
    # Extract headers
    headers = dict(request.headers)

    # Authenticate request
    user = await authenticate(headers.get("authorization"))
    if not user:
        raise HTTPException(status_code=401)

    # Add user context to headers
    headers["X-User-ID"] = str(user.id)

    # Forward request
    body = await request.json() if request.method in ["POST", "PUT"] else None
    response = await forward_request(
        service,
        f"/{path}",
        request.method,
        headers,
        body
    )

    return response.json()

# Aggregation endpoint
@app.get("/dashboard")
async def get_dashboard(user = Depends(get_current_user)):
    """Aggregate data from multiple services"""
    async with AsyncClient() as client:
        # Concurrent requests to multiple services
        user_resp = await client.get(f"{SERVICES['users']}/users/{user.id}")
        orders_resp = await client.get(f"{SERVICES['orders']}/users/{user.id}/orders")
        recommendations_resp = await client.get(
            f"{SERVICES['products']}/recommendations",
            params={"user_id": user.id}
        )

    return {
        "user": user_resp.json(),
        "recent_orders": orders_resp.json(),
        "recommendations": recommendations_resp.json()
    }
```

---

## 7. Backend for Frontend (BFF) Pattern

### What It Is

BFF creates dedicated backend services for each frontend (mobile, web, desktop), tailored to their specific needs.

### When to Use

- Multiple frontend platforms
- Different data requirements per platform
- Performance optimization per platform
- Platform-specific business logic

### Implementation

```python
# Mobile BFF - Optimized for mobile constraints
mobile_app = FastAPI(title="Mobile BFF")

@mobile_app.get("/feed")
async def get_mobile_feed(user_id: int):
    """Mobile-optimized feed with minimal data"""
    posts = await get_posts(user_id, limit=10)

    # Minimal response for mobile
    return [
        {
            "id": post.id,
            "text": post.text[:100],  # Truncated
            "author": post.author.username,
            "timestamp": post.created_at,
            "thumbnail": post.image_thumbnail_url  # Thumbnail, not full image
        }
        for post in posts
    ]

# Web BFF - Full-featured for web browsers
web_app = FastAPI(title="Web BFF")

@web_app.get("/feed")
async def get_web_feed(user_id: int):
    """Web-optimized feed with full data"""
    posts = await get_posts(user_id, limit=50)

    # Rich response for web
    return [
        {
            "id": post.id,
            "text": post.text,
            "html": post.html_content,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "avatar": post.author.avatar_url,
                "verified": post.author.is_verified
            },
            "media": [
                {"url": m.url, "type": m.type}
                for m in post.media
            ],
            "stats": {
                "likes": post.like_count,
                "comments": post.comment_count,
                "shares": post.share_count
            },
            "timestamp": post.created_at
        }
        for post in posts
    ]
```

---

## 8. Data Transfer Object (DTO) Pattern

### What It Is

DTOs define data structures for transferring data between layers, keeping internal models separate from API contracts.

### When to Use

- Separate internal models from API
- Different views of same data
- Version multiple API versions
- Protect sensitive fields

### Implementation

```python
# Internal model
class UserModel(Base):
    """Database model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    is_admin = Column(Boolean)
    created_at = Column(DateTime)
    last_login = Column(DateTime)

# DTOs for different contexts
class UserCreateDTO(BaseModel):
    """DTO for creating user"""
    username: str
    email: EmailStr
    password: str  # Plain password

class UserResponseDTO(BaseModel):
    """DTO for API response"""
    id: int
    username: str
    email: str
    created_at: datetime
    # Note: No password or admin flag

    class Config:
        orm_mode = True

class UserAdminDTO(BaseModel):
    """DTO for admin view"""
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    # Still no password

class UserUpdateDTO(BaseModel):
    """DTO for updates"""
    username: Optional[str]
    email: Optional[EmailStr]
    # Partial update, all optional

# Usage
@app.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user(user_id: int):
    """Returns DTO, not internal model"""
    user = db.query(UserModel).get(user_id)
    return UserResponseDTO.from_orm(user)

@app.get("/admin/users/{user_id}", response_model=UserAdminDTO)
async def get_user_admin(user_id: int, admin=Depends(require_admin)):
    """Admin view with more fields"""
    user = db.query(UserModel).get(user_id)
    return UserAdminDTO.from_orm(user)
```

---

## 9. Pagination Patterns

### Offset-Based Pagination

**Best for**: Traditional page numbers, small datasets

```python
@app.get("/items")
async def list_items(skip: int = 0, limit: int = 20):
    """Offset pagination"""
    items = db.query(Item).offset(skip).limit(limit).all()
    total = db.query(Item).count()

    return {
        "items": items,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
```

### Cursor-Based Pagination

**Best for**: Large datasets, real-time data, social feeds

```python
from typing import Optional

@app.get("/feed")
async def get_feed(cursor: Optional[str] = None, limit: int = 20):
    """Cursor-based pagination"""
    query = db.query(Post).order_by(Post.created_at.desc())

    if cursor:
        # Decode cursor to get last seen ID
        last_id = decode_cursor(cursor)
        query = query.filter(Post.id < last_id)

    items = query.limit(limit + 1).all()

    has_next = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_next and items:
        next_cursor = encode_cursor(items[-1].id)

    return {
        "items": items,
        "pagination": {
            "cursor": cursor,
            "next_cursor": next_cursor,
            "has_next": has_next
        }
    }
```

### Keyset Pagination

**Best for**: Consistent ordering, performance at scale

```python
@app.get("/items")
async def list_items(
    last_id: Optional[int] = None,
    last_created: Optional[datetime] = None,
    limit: int = 20
):
    """Keyset pagination using multiple columns"""
    query = db.query(Item).order_by(
        Item.created_at.desc(),
        Item.id.desc()
    )

    if last_id and last_created:
        query = query.filter(
            or_(
                Item.created_at < last_created,
                and_(
                    Item.created_at == last_created,
                    Item.id < last_id
                )
            )
        )

    items = query.limit(limit).all()

    return {
        "items": items,
        "next": {
            "last_id": items[-1].id if items else None,
            "last_created": items[-1].created_at if items else None
        }
    }
```

---

## 10. Bulk Operations Pattern

### What It Is

Efficiently handle multiple operations in a single request.

### Implementation

```python
from typing import List
from pydantic import BaseModel

class BulkCreateRequest(BaseModel):
    items: List[ItemCreate]

class BulkCreateResponse(BaseModel):
    created: List[Item]
    failed: List[dict]

@app.post("/items/bulk", response_model=BulkCreateResponse)
async def bulk_create_items(request: BulkCreateRequest):
    """Create multiple items efficiently"""
    created = []
    failed = []

    # Process in batches
    for i in range(0, len(request.items), 100):
        batch = request.items[i:i+100]

        for idx, item_data in enumerate(batch):
            try:
                item = Item(**item_data.dict())
                db.add(item)
                created.append(item)
            except Exception as e:
                failed.append({
                    "index": i + idx,
                    "item": item_data.dict(),
                    "error": str(e)
                })

        # Commit batch
        db.commit()

    return BulkCreateResponse(created=created, failed=failed)
```

---

## 11. Async Processing Pattern

### What It Is

Offload long-running operations to background tasks.

### Implementation

```python
from celery import Celery
from fastapi import BackgroundTasks

celery_app = Celery('tasks', broker='redis://localhost:6379')

# Celery task
@celery_app.task
def process_large_file(file_id: int):
    """Long-running file processing"""
    file = get_file(file_id)
    # Process file...
    update_file_status(file_id, "completed")

# FastAPI endpoint
@app.post("/files/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    """Accept file and process async"""
    # Save file
    file_id = save_file(file)

    # Queue background task
    process_large_file.delay(file_id)

    return {
        "file_id": file_id,
        "status": "processing",
        "message": "File is being processed"
    }

# Check status
@app.get("/files/{file_id}/status")
async def get_file_status(file_id: int):
    """Check processing status"""
    file = get_file(file_id)
    return {"status": file.status}
```

---

## 12. Anti-Patterns to Avoid

### Anti-Pattern: Chatty API

❌ **Problem**: Too many small requests

```python
# Bad: Requires 3 requests
GET /users/1
GET /users/1/profile
GET /users/1/settings
```

✅ **Solution**: Aggregate data

```python
# Good: One request with includes
GET /users/1?include=profile,settings
```

### Anti-Pattern: Overfetching

❌ **Problem**: Returning unnecessary data

```python
# Bad: Always returns all fields
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_full_user(user_id)  # 50+ fields
    return user
```

✅ **Solution**: Field selection

```python
# Good: Let client specify fields
@app.get("/users/{user_id}")
async def get_user(user_id: int, fields: Optional[str] = None):
    user = get_user_from_db(user_id)
    if fields:
        requested_fields = fields.split(",")
        return {k: v for k, v in user.dict().items() if k in requested_fields}
    return user
```

### Anti-Pattern: Ignoring HTTP Status Codes

❌ **Problem**: Always returning 200

```python
# Bad
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_or_none(user_id)
    if not user:
        return {"error": "Not found"}  # Returns 200!
    return user
```

✅ **Solution**: Proper status codes

```python
# Good
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = get_user_or_none(user_id)
    if not user:
        raise HTTPException(status_code=404)
    return user
```

### Anti-Pattern: No Pagination

❌ **Problem**: Returning all records

```python
# Bad: Can return millions of records
@app.get("/users")
async def list_users():
    return db.query(User).all()  # Memory explosion!
```

✅ **Solution**: Always paginate

```python
# Good
@app.get("/users")
async def list_users(skip: int = 0, limit: int = Query(20, le=100)):
    return db.query(User).offset(skip).limit(limit).all()
```

---

## Pattern Selection Guide

| Use Case | Recommended Pattern |
|----------|-------------------|
| Data access abstraction | Repository Pattern |
| Business logic organization | Service Layer Pattern |
| Testing and modularity | Dependency Injection |
| External service calls | Circuit Breaker |
| Distributed transactions | Saga Pattern |
| Microservices routing | API Gateway |
| Platform-specific APIs | BFF Pattern |
| API contracts | DTO Pattern |
| Large datasets | Cursor Pagination |
| Batch operations | Bulk Operations |
| Long-running tasks | Async Processing |

Choose patterns based on your specific requirements, team expertise, and system complexity.
