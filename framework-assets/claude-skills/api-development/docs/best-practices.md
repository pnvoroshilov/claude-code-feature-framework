# Best Practices - API Development

This document outlines industry-standard best practices for building production-ready APIs. Following these guidelines ensures your APIs are secure, maintainable, scalable, and developer-friendly.

## Table of Contents

- [1. API Design Principles](#1-api-design-principles)
- [2. RESTful Design Guidelines](#2-restful-design-guidelines)
- [3. Error Handling Standards](#3-error-handling-standards)
- [4. Security Best Practices](#4-security-best-practices)
- [5. Performance Optimization](#5-performance-optimization)
- [6. Documentation Standards](#6-documentation-standards)
- [7. Versioning Strategy](#7-versioning-strategy)
- [8. Testing Practices](#8-testing-practices)
- [9. Logging and Monitoring](#9-logging-and-monitoring)
- [10. Code Organization](#10-code-organization)

---

## 1. API Design Principles

### Principle: Design for Developers

Your API's primary users are developers. Design with their experience in mind.

**Why It Matters**: Developer-friendly APIs are adopted faster, have fewer support issues, and generate positive word-of-mouth.

### How to Apply

✅ **Do**: Use clear, consistent naming
```python
# Good: Clear, predictable endpoints
GET /users
GET /users/{id}
POST /users
PUT /users/{id}
DELETE /users/{id}
```

❌ **Don't**: Use inconsistent or cryptic names
```python
# Bad: Inconsistent and unclear
GET /getUsers
GET /user_detail/{id}
POST /createNewUser
PUT /updateUserById/{id}
DELETE /removeUser/{id}
```

✅ **Do**: Provide helpful error messages
```python
from fastapi import HTTPException

@app.post("/users")
async def create_user(user: UserCreate):
    if email_exists(user.email):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "email_already_exists",
                "message": "A user with this email already exists",
                "field": "email",
                "suggestion": "Use a different email or try logging in"
            }
        )
```

❌ **Don't**: Return vague errors
```python
# Bad: Unhelpful error message
raise HTTPException(status_code=400, detail="Error")
```

---

## 2. RESTful Design Guidelines

### Guideline: Use HTTP Methods Correctly

Each HTTP method has specific semantics that should be respected.

**Why It Matters**: Correct method usage makes APIs predictable and enables proper caching, idempotency, and safety.

### HTTP Method Usage

| Method | Usage | Body | Idempotent | Safe |
|--------|-------|------|------------|------|
| GET | Retrieve resources | No | Yes | Yes |
| POST | Create new resources | Yes | No | No |
| PUT | Replace entire resource | Yes | Yes | No |
| PATCH | Partial update | Yes | No | No |
| DELETE | Remove resource | Optional | Yes | No |

### Examples

✅ **Good Example: Proper Method Usage**

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

# GET - Retrieve (safe, idempotent, cacheable)
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Retrieve user - no side effects"""
    return get_user_from_db(user_id)

# POST - Create (not idempotent)
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Create new user - returns 201"""
    return save_user_to_db(user)

# PUT - Replace (idempotent)
@app.put("/users/{user_id}", response_model=User)
async def replace_user(user_id: int, user: User):
    """Replace entire user - multiple calls have same effect"""
    user.id = user_id
    return replace_in_db(user)

# PATCH - Partial update
@app.patch("/users/{user_id}")
async def update_user(user_id: int, updates: dict):
    """Update specific fields"""
    return update_in_db(user_id, updates)

# DELETE - Remove (idempotent)
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete user - multiple calls have same effect"""
    delete_from_db(user_id)
    return None
```

❌ **Bad Example: Incorrect Method Usage**

```python
# Bad: Using GET for operations with side effects
@app.get("/users/{user_id}/delete")  # Should be DELETE
async def delete_user(user_id: int):
    delete_from_db(user_id)

# Bad: Using POST for everything
@app.post("/users/get/{user_id}")  # Should be GET
async def get_user(user_id: int):
    return get_from_db(user_id)

# Bad: Using PUT for partial updates
@app.put("/users/{user_id}")  # Should be PATCH
async def update_email(user_id: int, email: str):
    # Only updates email, not full replacement
    update_field(user_id, "email", email)
```

### Guideline: Use Plural Nouns for Collections

**Why It Matters**: Consistency makes APIs intuitive and predictable.

✅ **Do**: Use plural nouns
```python
GET /users          # Collection
GET /users/123      # Single resource
GET /products       # Collection
POST /orders        # Create in collection
```

❌ **Don't**: Mix singular and plural
```python
GET /user           # Unclear if single or collection
GET /product/list   # Redundant 'list'
POST /new_order     # Don't use verbs
```

### Guideline: Nest Resources Appropriately

**Why It Matters**: Shows relationships and maintains clear hierarchy.

✅ **Good Nesting**
```python
# Logical parent-child relationships
GET /users/123/posts           # Posts belonging to user 123
GET /posts/456/comments        # Comments on post 456
GET /companies/789/employees   # Employees of company 789

@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int, limit: int = 10):
    """Get posts for specific user"""
    return get_posts_by_user(user_id, limit)
```

❌ **Bad Nesting**
```python
# Too deep nesting - hard to maintain
GET /countries/1/states/2/cities/3/streets/4/houses/5

# Unrelated nesting - no logical relationship
GET /users/123/settings/theme/posts  # Confusing hierarchy
```

**Best Practice**: Limit nesting to 2 levels. For deeper relationships, use query parameters:
```python
# Instead of: /users/1/posts/2/comments/3/replies
# Use: /replies/3?post_id=2&user_id=1
```

---

## 3. Error Handling Standards

### Standard: Consistent Error Response Format

**Why It Matters**: Consistent errors are easier to handle programmatically and debug.

### RFC 7807 Problem Details Format

✅ **Good Error Response**
```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime

class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: dict = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.example.com/errors/{exc.error_code}",
            "title": exc.message,
            "status": exc.status_code,
            "detail": exc.message,
            "instance": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
            **exc.details
        }
    )

# Usage
@app.post("/users")
async def create_user(user: UserCreate):
    if email_exists(user.email):
        raise APIError(
            status_code=409,
            error_code="email_conflict",
            message="Email address already in use",
            details={
                "field": "email",
                "value": user.email,
                "suggestion": "Use a different email address"
            }
        )
```

### Validation Errors

✅ **Good Validation Error Response**
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"],
            "input": error.get("input")
        })

    return JSONResponse(
        status_code=422,
        content={
            "type": "https://api.example.com/errors/validation",
            "title": "Validation Error",
            "status": 422,
            "errors": errors,
            "instance": request.url.path
        }
    )
```

---

## 4. Security Best Practices

### Practice: Never Trust User Input

**Why It Matters**: Input validation prevents injection attacks, data corruption, and security vulnerabilities.

✅ **Good Input Validation**
```python
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex="^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr  # Validates email format
    password: str = Field(..., min_length=8, max_length=128)
    age: Optional[int] = Field(None, ge=13, le=150)

    @validator('username')
    def username_no_special_chars(cls, v):
        """Additional username validation"""
        if v.lower() in ['admin', 'root', 'system']:
            raise ValueError('Reserved username')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Enforce password complexity"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

### Practice: Implement Rate Limiting

**Why It Matters**: Protects against brute force attacks, DDoS, and resource exhaustion.

✅ **Good Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Different limits for different endpoints
@app.post("/login")
@limiter.limit("5/minute")  # Strict limit for auth
async def login(request: Request, credentials: LoginCredentials):
    return authenticate(credentials)

@app.get("/products")
@limiter.limit("100/minute")  # More lenient for reads
async def get_products(request: Request):
    return get_all_products()

@app.post("/upload")
@limiter.limit("10/hour")  # Very strict for expensive operations
async def upload_file(request: Request, file: UploadFile):
    return process_upload(file)
```

### Practice: Use HTTPS Everywhere

**Why It Matters**: Encrypts data in transit, prevents man-in-the-middle attacks.

✅ **Good: Force HTTPS**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.example.com", "*.example.com"]
)

# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### Practice: Implement Proper CORS

**Why It Matters**: Controls which domains can access your API.

✅ **Good CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://app.example.com"
    ],  # Specific origins, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)
```

❌ **Bad CORS Configuration**
```python
# Don't do this in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows any origin
    allow_credentials=True,  # With credentials = security risk!
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### Practice: Never Log Sensitive Data

**Why It Matters**: Prevents credential leakage in logs.

✅ **Good Logging**
```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

SENSITIVE_FIELDS = {"password", "token", "secret", "api_key", "credit_card"}

def safe_log(data: dict[str, Any]) -> dict[str, Any]:
    """Remove sensitive fields before logging"""
    safe_data = data.copy()
    for field in SENSITIVE_FIELDS:
        if field in safe_data:
            safe_data[field] = "***REDACTED***"
    return safe_data

@app.post("/users")
async def create_user(user: UserCreate):
    logger.info(f"Creating user: {safe_log(user.dict())}")
    # Log shows: "Creating user: {'username': 'john', 'password': '***REDACTED***'}"
```

❌ **Bad Logging**
```python
# Don't do this!
@app.post("/users")
async def create_user(user: UserCreate):
    logger.info(f"Creating user: {user.dict()}")
    # Logs password in plain text!
```

---

## 5. Performance Optimization

### Practice: Implement Efficient Pagination

**Why It Matters**: Prevents memory issues and slow responses with large datasets.

✅ **Good Pagination**
```python
from fastapi import Query
from typing import List

class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip"),
        limit: int = Query(20, ge=1, le=100, description="Max items to return")
    ):
        self.skip = skip
        self.limit = limit

@app.get("/users")
async def list_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """Efficient pagination with limit"""
    users = db.query(User)\
        .offset(pagination.skip)\
        .limit(pagination.limit)\
        .all()

    total = db.query(User).count()

    return {
        "items": users,
        "pagination": {
            "skip": pagination.skip,
            "limit": pagination.limit,
            "total": total,
            "has_more": pagination.skip + pagination.limit < total
        }
    }
```

### Practice: Use Database Indexes

**Why It Matters**: Dramatically improves query performance.

✅ **Good Indexing**
```python
from sqlalchemy import Column, Integer, String, Index

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Indexed for fast lookup
    username = Column(String, index=True)  # Frequently queried
    created_at = Column(DateTime, index=True)  # Used in sorting

    # Composite index for common query pattern
    __table_args__ = (
        Index('idx_user_status_created', 'status', 'created_at'),
    )
```

### Practice: Implement Caching

**Why It Matters**: Reduces database load and improves response times.

✅ **Good Caching**
```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
import redis

# Initialize Redis cache
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis_client), prefix="api-cache")

# Cache expensive queries
@app.get("/products/{product_id}")
@cache(expire=3600)  # Cache for 1 hour
async def get_product(product_id: int):
    """Cached product endpoint"""
    return get_expensive_product_data(product_id)

# In-memory cache for config
@lru_cache()
def get_settings():
    """Cache settings in memory"""
    return Settings()
```

### Practice: Use Async Operations

**Why It Matters**: Improves concurrency and handles more requests.

✅ **Good Async Usage**
```python
import asyncio
from httpx import AsyncClient

@app.get("/dashboard")
async def get_dashboard():
    """Fetch multiple data sources concurrently"""
    async with AsyncClient() as client:
        # Run requests concurrently
        user_task = client.get("https://api.example.com/user")
        orders_task = client.get("https://api.example.com/orders")
        analytics_task = client.get("https://api.example.com/analytics")

        # Wait for all to complete
        user_resp, orders_resp, analytics_resp = await asyncio.gather(
            user_task,
            orders_task,
            analytics_task
        )

    return {
        "user": user_resp.json(),
        "orders": orders_resp.json(),
        "analytics": analytics_resp.json()
    }
```

---

## 6. Documentation Standards

### Practice: Use OpenAPI/Swagger

**Why It Matters**: Auto-generated, interactive documentation improves developer experience.

✅ **Good Documentation**
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="E-Commerce API",
    description="Complete API for e-commerce platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class Product(BaseModel):
    """Product model with detailed field descriptions"""
    id: int = Field(..., description="Unique product identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    price: float = Field(..., gt=0, description="Price in USD")
    stock: int = Field(default=0, ge=0, description="Available stock quantity")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop",
                "price": 999.99,
                "stock": 50
            }
        }

@app.post(
    "/products",
    response_model=Product,
    status_code=201,
    summary="Create new product",
    description="Create a new product in the catalog. Requires admin authentication.",
    response_description="Successfully created product"
)
async def create_product(
    product: Product,
    user: User = Depends(get_current_admin_user)
):
    """
    Create a new product with the following information:

    - **name**: Product name (1-200 characters)
    - **price**: Price in USD (must be positive)
    - **stock**: Initial stock quantity (non-negative)

    Returns the created product with assigned ID.
    """
    return save_product(product)
```

---

## 7. Versioning Strategy

### Practice: Version from Day One

**Why It Matters**: Enables breaking changes without disrupting existing clients.

✅ **Good Versioning**
```python
from fastapi import APIRouter

# Version 1
v1_router = APIRouter(prefix="/v1", tags=["v1"])

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    return {"id": user_id, "name": "John"}

# Version 2 with breaking changes
v2_router = APIRouter(prefix="/v2", tags=["v2"])

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    return {
        "id": user_id,
        "profile": {
            "first_name": "John",
            "last_name": "Doe"
        }
    }

app.include_router(v1_router)
app.include_router(v2_router)
```

---

## 8. Testing Practices

### Practice: Write Comprehensive Tests

**Why It Matters**: Prevents regressions and ensures reliability.

✅ **Good Test Coverage**
```python
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

class TestProductAPI:
    """Comprehensive test suite"""

    def test_create_product_success(self):
        """Happy path: Create product successfully"""
        response = client.post("/products", json={
            "name": "Test Product",
            "price": 9.99,
            "stock": 10
        })
        assert response.status_code == 201
        assert response.json()["name"] == "Test Product"

    def test_create_product_invalid_price(self):
        """Error case: Invalid price"""
        response = client.post("/products", json={
            "name": "Test Product",
            "price": -10,  # Invalid
            "stock": 10
        })
        assert response.status_code == 422

    def test_create_product_unauthorized(self):
        """Auth case: No authentication"""
        response = client.post("/products", json={
            "name": "Test Product",
            "price": 9.99
        })
        assert response.status_code == 401

    def test_get_product_not_found(self):
        """Error case: Product doesn't exist"""
        response = client.get("/products/99999")
        assert response.status_code == 404
```

---

## 9. Logging and Monitoring

### Practice: Structured Logging

**Why It Matters**: Makes logs searchable and analyzable.

✅ **Good Logging**
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        """Log structured data"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_data))

logger = StructuredLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.log(
        "info",
        "Request started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )

    response = await call_next(request)

    duration = time.time() - start_time

    logger.log(
        "info",
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

    return response
```

---

## 10. Code Organization

### Practice: Use Dependency Injection

**Why It Matters**: Makes code testable and maintainable.

✅ **Good Organization**
```python
# dependencies.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Current user dependency"""
    user = verify_token_and_get_user(token, db)
    if not user:
        raise HTTPException(status_code=401)
    return user

# routes.py
@app.get("/me")
async def get_current_user_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uses injected dependencies"""
    return user
```

### Practice: Separate Concerns

✅ **Good Structure**
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # App initialization
│   ├── config.py         # Configuration
│   ├── dependencies.py   # Shared dependencies
│   ├── models/          # Database models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/         # API routes
│   │   ├── __init__.py
│   │   └── users.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py
│   └── tests/           # Tests
│       ├── __init__.py
│       └── test_users.py
```

---

## Summary Checklist

### Before Deploying Your API:

- ✅ All endpoints use appropriate HTTP methods
- ✅ Consistent error response format
- ✅ Input validation on all endpoints
- ✅ Authentication and authorization implemented
- ✅ Rate limiting configured
- ✅ HTTPS enforced
- ✅ Security headers set
- ✅ CORS properly configured
- ✅ Pagination implemented for collections
- ✅ Database queries optimized with indexes
- ✅ Caching strategy implemented
- ✅ Comprehensive test coverage (>80%)
- ✅ OpenAPI documentation complete
- ✅ Structured logging implemented
- ✅ Monitoring and alerting configured
- ✅ API versioning strategy in place
- ✅ No sensitive data in logs
- ✅ Dependency injection used throughout
- ✅ Code organized by concern
- ✅ Performance tested under load

Following these best practices ensures your API is secure, performant, maintainable, and developer-friendly.
