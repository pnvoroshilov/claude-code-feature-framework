# Core Concepts - API Development

This document covers fundamental concepts essential for API development. Understanding these concepts is critical for building robust, scalable, and maintainable APIs.

## Table of Contents

- [1. REST Architecture](#1-rest-architecture)
- [2. HTTP Protocol](#2-http-protocol)
- [3. GraphQL Fundamentals](#3-graphql-fundamentals)
- [4. API Resources and Endpoints](#4-api-resources-and-endpoints)
- [5. Request and Response Lifecycle](#5-request-and-response-lifecycle)
- [6. Data Modeling](#6-data-modeling)
- [7. Authentication vs Authorization](#7-authentication-vs-authorization)
- [8. API Versioning](#8-api-versioning)
- [9. Content Negotiation](#9-content-negotiation)
- [10. Idempotency](#10-idempotency)
- [11. Caching Strategies](#11-caching-strategies)
- [12. Rate Limiting](#12-rate-limiting)

---

## 1. REST Architecture

### What It Is

REST (Representational State Transfer) is an architectural style for designing networked applications. It relies on a stateless, client-server protocol (typically HTTP) and treats resources as the core abstraction.

### Core Principles

1. **Client-Server Separation** - Clear separation between client and server concerns
2. **Statelessness** - Each request contains all information needed to process it
3. **Cacheability** - Responses must define themselves as cacheable or non-cacheable
4. **Uniform Interface** - Consistent way to interact with resources
5. **Layered System** - Client cannot tell if connected directly to end server
6. **Code on Demand** (optional) - Servers can extend client functionality

### Why It Matters

RESTful APIs are:
- Easy to understand and use
- Highly scalable due to statelessness
- Cacheable for improved performance
- Platform and language independent

### How It Works

REST uses HTTP methods to perform operations on resources:

```python
# RESTful resource design
GET    /users          # List all users
GET    /users/123      # Get user 123
POST   /users          # Create new user
PUT    /users/123      # Update user 123 (full replacement)
PATCH  /users/123      # Update user 123 (partial update)
DELETE /users/123      # Delete user 123
```

### Examples

#### Example 1: Basic REST Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Resource model
class User(BaseModel):
    id: int
    name: str
    email: str

# In-memory storage (use database in production)
users_db = {}

@app.get("/users", response_model=List[User])
async def list_users():
    """List all users - Stateless, cacheable"""
    return list(users_db.values())

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get single user - Uniform interface"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]
```

#### Example 2: RESTful CRUD Operations

```python
@app.post("/users", response_model=User, status_code=201)
async def create_user(user: User):
    """Create new user"""
    if user.id in users_db:
        raise HTTPException(status_code=409, detail="User already exists")
    users_db[user.id] = user
    return user

@app.put("/users/{user_id}", response_model=User)
async def replace_user(user_id: int, user: User):
    """Replace entire user resource"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    user.id = user_id  # Ensure ID matches
    users_db[user_id] = user
    return user

@app.patch("/users/{user_id}")
async def update_user(user_id: int, updates: dict):
    """Partial update of user resource"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    user = users_db[user_id]
    for key, value in updates.items():
        if hasattr(user, key):
            setattr(user, key, value)
    return user
```

### Common Patterns

- **Collection Resources**: `/users` (plural noun)
- **Singleton Resources**: `/users/123` (collection + identifier)
- **Sub-resources**: `/users/123/posts` (nested resources)
- **Actions**: POST to `/users/123/verify` (when CRUD doesn't fit)

### Common Mistakes

❌ **Using verbs in URLs**: `/getUser/123` or `/createUser`
✅ **Use nouns + HTTP methods**: `GET /users/123`, `POST /users`

❌ **Making APIs stateful**: Storing session data on server
✅ **Keep stateless**: Include auth token in each request

❌ **Ignoring HTTP status codes**: Always returning 200
✅ **Use appropriate codes**: 201 for created, 404 for not found, etc.

---

## 2. HTTP Protocol

### What It Is

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the web. It's a request-response protocol where clients send requests and servers return responses.

### HTTP Methods

| Method | Purpose | Idempotent | Safe | Cacheable |
|--------|---------|------------|------|-----------|
| GET | Retrieve resource | Yes | Yes | Yes |
| POST | Create resource | No | No | Rarely |
| PUT | Replace resource | Yes | No | No |
| PATCH | Update resource | No | No | No |
| DELETE | Remove resource | Yes | No | No |
| HEAD | Get headers only | Yes | Yes | Yes |
| OPTIONS | Get supported methods | Yes | Yes | No |

### HTTP Status Codes

#### 2xx Success
- **200 OK** - Request succeeded
- **201 Created** - Resource created successfully
- **202 Accepted** - Request accepted for processing
- **204 No Content** - Success with no response body

#### 3xx Redirection
- **301 Moved Permanently** - Resource permanently moved
- **302 Found** - Resource temporarily moved
- **304 Not Modified** - Cached version is still valid

#### 4xx Client Errors
- **400 Bad Request** - Invalid request syntax
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Server refuses request
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Request conflicts with current state
- **422 Unprocessable Entity** - Validation failed
- **429 Too Many Requests** - Rate limit exceeded

#### 5xx Server Errors
- **500 Internal Server Error** - Generic server error
- **502 Bad Gateway** - Invalid response from upstream
- **503 Service Unavailable** - Server temporarily unavailable
- **504 Gateway Timeout** - Upstream server timeout

### Examples

#### Example 1: Proper Status Code Usage

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """Returns 200 OK with item or 404 Not Found"""
    item = get_from_db(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """Returns 201 Created for successful creation"""
    db_item = save_to_db(item)
    return db_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Returns 204 No Content after successful deletion"""
    if not exists_in_db(item_id):
        raise HTTPException(status_code=404)
    delete_from_db(item_id)
    return None  # No content returned
```

#### Example 2: Custom Error Responses

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Custom 422 validation error response"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_failed",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Generic 500 error handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )
```

### HTTP Headers

#### Common Request Headers

```python
# Content negotiation
"Accept": "application/json"
"Accept-Language": "en-US"
"Accept-Encoding": "gzip, deflate"

# Authentication
"Authorization": "Bearer eyJhbGc..."

# Caching
"If-None-Match": "abc123"
"If-Modified-Since": "Wed, 21 Oct 2015 07:28:00 GMT"

# Content
"Content-Type": "application/json"
"Content-Length": "348"
```

#### Common Response Headers

```python
from fastapi import Response

@app.get("/items/{item_id}")
async def get_item(item_id: int, response: Response):
    """Set response headers"""
    item = get_from_db(item_id)

    # Caching headers
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["ETag"] = f'"{item.version}"'

    # CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"

    return item
```

---

## 3. GraphQL Fundamentals

### What It Is

GraphQL is a query language for APIs and a runtime for executing those queries. Unlike REST, clients can request exactly the data they need in a single request.

### Core Concepts

1. **Schema** - Defines types and operations
2. **Queries** - Read operations
3. **Mutations** - Write operations
4. **Subscriptions** - Real-time updates
5. **Resolvers** - Functions that fetch data
6. **Types** - Strongly typed schema

### Why It Matters

GraphQL solves common REST problems:
- **Over-fetching** - REST returns all fields, GraphQL only requested fields
- **Under-fetching** - REST needs multiple requests, GraphQL gets all in one
- **API versioning** - GraphQL evolves schema without versions

### How It Works

```graphql
# Schema definition
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  user(id: ID!): User
  posts(limit: Int): [Post!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
  updateUser(id: ID!, name: String): User!
}
```

### Examples

#### Example 1: Basic GraphQL Setup

```python
import strawberry
from typing import List, Optional

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Post:
    id: int
    title: str
    content: str
    author_id: int

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get user by ID"""
        return get_user_from_db(id)

    @strawberry.field
    def posts(self, limit: int = 10) -> List[Post]:
        """Get posts with limit"""
        return get_posts_from_db(limit)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, email: str) -> User:
        """Create new user"""
        return create_user_in_db(name, email)

schema = strawberry.Schema(query=Query, mutation=Mutation)
```

#### Example 2: GraphQL Query Examples

```graphql
# Query: Get user with specific fields
query GetUser {
  user(id: 1) {
    id
    name
    email
  }
}

# Query: Get user with nested posts
query GetUserWithPosts {
  user(id: 1) {
    name
    posts {
      title
      content
    }
  }
}

# Mutation: Create user
mutation CreateUser {
  createUser(name: "John Doe", email: "john@example.com") {
    id
    name
  }
}

# Query with variables
query GetUserById($userId: ID!) {
  user(id: $userId) {
    name
    email
  }
}
```

#### Example 3: Resolvers with DataLoader

```python
from strawberry.dataloader import DataLoader
from typing import List

async def load_users(keys: List[int]) -> List[User]:
    """Batch load users - solves N+1 problem"""
    users = await db.fetch_users_by_ids(keys)
    user_map = {user.id: user for user in users}
    return [user_map.get(key) for key in keys]

@strawberry.type
class Post:
    id: int
    title: str
    author_id: int

    @strawberry.field
    async def author(self, info) -> User:
        """Efficiently load author using DataLoader"""
        loader = info.context["user_loader"]
        return await loader.load(self.author_id)

# Setup with FastAPI
from strawberry.fastapi import GraphQLRouter

async def get_context():
    return {
        "user_loader": DataLoader(load_fn=load_users)
    }

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)
```

---

## 4. API Resources and Endpoints

### What It Is

Resources are the fundamental concept in RESTful APIs. A resource is any object, data, or service that can be accessed by the client.

### Resource Naming Conventions

```python
# Good resource names (nouns, plural)
GET /users
GET /products
GET /orders
GET /invoices

# Bad resource names (verbs, actions)
GET /getUsers      # ❌
GET /createProduct # ❌
POST /addOrder     # ❌
```

### URI Design Patterns

```python
# Collection
GET /users                    # List all users

# Singleton
GET /users/123                # Get specific user

# Sub-collection
GET /users/123/posts          # Get posts for user 123

# Sub-resource
GET /users/123/profile        # Get profile for user 123

# Actions (when CRUD doesn't fit)
POST /users/123/verify        # Verify user 123
POST /orders/456/cancel       # Cancel order 456
```

### Examples

#### Example 1: Resource Hierarchy

```python
from fastapi import FastAPI, Path
from typing import List

app = FastAPI()

# Top-level collection
@app.get("/users")
async def list_users():
    return []

# Singleton resource
@app.get("/users/{user_id}")
async def get_user(user_id: int = Path(..., ge=1)):
    return {"id": user_id}

# Sub-collection
@app.get("/users/{user_id}/posts")
async def get_user_posts(user_id: int):
    return []

# Sub-resource singleton
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}

# Nested sub-collection
@app.get("/users/{user_id}/posts/{post_id}/comments")
async def get_post_comments(user_id: int, post_id: int):
    return []
```

#### Example 2: Resource Actions

```python
# Action that doesn't fit CRUD
@app.post("/users/{user_id}/verify")
async def verify_user(user_id: int, verification_code: str):
    """Verify user email - not a simple CRUD operation"""
    user = get_user(user_id)
    if user.verification_code == verification_code:
        user.verified = True
        save_user(user)
        return {"status": "verified"}
    raise HTTPException(status_code=400, detail="Invalid code")

@app.post("/orders/{order_id}/cancel")
async def cancel_order(order_id: int, reason: str):
    """Cancel order - business action"""
    order = get_order(order_id)
    order.status = "cancelled"
    order.cancellation_reason = reason
    save_order(order)
    return {"status": "cancelled"}

@app.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: int, amount: float):
    """Process refund - external system interaction"""
    payment = get_payment(payment_id)
    refund = process_refund_with_gateway(payment, amount)
    return refund
```

---

## 5. Request and Response Lifecycle

### What It Is

Understanding the complete lifecycle of an API request helps in debugging, optimization, and error handling.

### Lifecycle Stages

1. **Client sends request** - HTTP request created
2. **Network transmission** - Request travels to server
3. **Server receives request** - Web server accepts connection
4. **Middleware processing** - Authentication, logging, validation
5. **Route matching** - Find handler for endpoint
6. **Request validation** - Validate input data
7. **Business logic** - Execute core functionality
8. **Database operations** - Query/update data
9. **Response preparation** - Format response data
10. **Middleware post-processing** - Add headers, logging
11. **Network transmission** - Response travels to client
12. **Client receives response** - Client processes response

### Examples

#### Example 1: Request Lifecycle with Middleware

```python
from fastapi import FastAPI, Request
from time import time
import logging

app = FastAPI()

# Middleware: Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request"""
    start_time = time()

    # Before request processing
    logging.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # After request processing
    duration = time() - start_time
    logging.info(f"Response: {response.status_code} ({duration:.3f}s)")

    return response

# Middleware: Authentication
@app.middleware("http")
async def authenticate(request: Request, call_next):
    """Authenticate requests"""
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing authentication"}
            )

    response = await call_next(request)
    return response

# Endpoint
@app.get("/api/data")
async def get_data():
    """Endpoint with middleware protection"""
    return {"data": "protected content"}
```

#### Example 2: Error Handling in Lifecycle

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions in lifecycle"""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "path": request.url.path,
            "method": request.method
        }
    )

# Custom exception
class DatabaseError(Exception):
    pass

@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle database errors"""
    return JSONResponse(
        status_code=503,
        content={
            "error": "database_unavailable",
            "message": "Database is temporarily unavailable"
        }
    )
```

---

## 6. Data Modeling

### What It Is

Data modeling defines the structure of data in your API - request bodies, response bodies, and database models.

### Model Types

1. **Request Models** - Validate incoming data
2. **Response Models** - Define response structure
3. **Database Models** - Map to database tables
4. **Domain Models** - Business logic entities

### Examples

#### Example 1: Pydantic Models for Validation

```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    """Request model for creating user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strength(cls, v):
        """Custom validation for password"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

class UserResponse(BaseModel):
    """Response model for user"""
    id: int
    username: str
    email: str
    created_at: datetime
    # Note: password not included in response

    class Config:
        orm_mode = True  # Allow conversion from ORM models

class UserUpdate(BaseModel):
    """Request model for updating user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    # All fields optional for partial updates
```

#### Example 2: Nested Models

```python
class Address(BaseModel):
    """Nested address model"""
    street: str
    city: str
    country: str
    postal_code: str

class OrderItem(BaseModel):
    """Nested order item model"""
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Order(BaseModel):
    """Complex nested model"""
    id: int
    customer_id: int
    items: List[OrderItem]
    shipping_address: Address
    billing_address: Optional[Address] = None
    total: float
    status: str = Field(default="pending")

    @validator('total')
    def validate_total(cls, v, values):
        """Validate total matches items"""
        if 'items' in values:
            calculated = sum(
                item.price * item.quantity
                for item in values['items']
            )
            if abs(calculated - v) > 0.01:
                raise ValueError('Total does not match items')
        return v
```

---

## 7. Authentication vs Authorization

### What It Is

- **Authentication** - Verifying WHO you are (identity)
- **Authorization** - Verifying WHAT you can do (permissions)

### Authentication Methods

1. **Basic Auth** - Username/password in header
2. **Bearer Token** - JWT or opaque token
3. **API Keys** - Static keys for identification
4. **OAuth 2.0** - Delegated authorization

### Authorization Patterns

1. **RBAC** - Role-Based Access Control
2. **ABAC** - Attribute-Based Access Control
3. **ACL** - Access Control Lists

### Examples

#### Example 1: JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_token(user_id: int) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Protected endpoint
@app.get("/protected")
async def protected_route(token_data: dict = Depends(verify_token)):
    """Requires valid JWT token"""
    return {"user_id": token_data["user_id"]}
```

#### Example 2: Role-Based Authorization

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user from token"""
    user = get_user_from_db(token_data["user_id"])
    return user

def require_role(*allowed_roles: Role):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user=Depends(get_current_user), **kwargs):
            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Requires one of: {allowed_roles}"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

@app.delete("/users/{user_id}")
@require_role(Role.ADMIN)
async def delete_user(user_id: int, user = Depends(get_current_user)):
    """Only admins can delete users"""
    delete_user_from_db(user_id)
    return {"status": "deleted"}

@app.post("/posts/{post_id}/moderate")
@require_role(Role.ADMIN, Role.MODERATOR)
async def moderate_post(post_id: int, user = Depends(get_current_user)):
    """Admins and moderators can moderate"""
    moderate_post_in_db(post_id)
    return {"status": "moderated"}
```

---

## 8. API Versioning

### What It Is

API versioning allows you to make breaking changes while supporting existing clients.

### Versioning Strategies

1. **URI Versioning** - `/v1/users`, `/v2/users`
2. **Header Versioning** - `API-Version: 1`
3. **Query Parameter** - `/users?version=1`
4. **Content Negotiation** - `Accept: application/vnd.api.v1+json`

### Examples

#### Example 1: URI Versioning

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Version 1 router
v1_router = APIRouter(prefix="/v1")

@v1_router.get("/users/{user_id}")
async def get_user_v1(user_id: int):
    """Version 1: Returns basic user info"""
    return {
        "id": user_id,
        "name": "John Doe"
    }

# Version 2 router
v2_router = APIRouter(prefix="/v2")

@v2_router.get("/users/{user_id}")
async def get_user_v2(user_id: int):
    """Version 2: Returns enhanced user info"""
    return {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }

app.include_router(v1_router)
app.include_router(v2_router)
```

#### Example 2: Header Versioning

```python
from fastapi import Header, HTTPException

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    api_version: str = Header(default="1", alias="API-Version")
):
    """Handle multiple versions via header"""
    if api_version == "1":
        return {"id": user_id, "name": "John Doe"}
    elif api_version == "2":
        return {
            "id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported API version: {api_version}"
        )
```

---

## 9. Content Negotiation

### What It Is

Content negotiation allows the same endpoint to return different representations based on client preferences.

### Examples

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import xmltodict

@app.get("/data")
async def get_data(request: Request):
    """Return JSON or XML based on Accept header"""
    data = {"name": "John", "age": 30}

    accept = request.headers.get("accept", "application/json")

    if "application/xml" in accept:
        xml_data = xmltodict.unparse({"data": data})
        return Response(content=xml_data, media_type="application/xml")
    else:
        return JSONResponse(content=data)
```

---

## 10. Idempotency

### What It Is

An idempotent operation produces the same result regardless of how many times it's performed.

### Idempotent Methods

- **GET** - Always idempotent (doesn't modify state)
- **PUT** - Idempotent (replaces entire resource)
- **DELETE** - Idempotent (deleting twice has same effect)
- **POST** - NOT idempotent (creates new resource each time)
- **PATCH** - Generally NOT idempotent

### Examples

```python
# Idempotent: PUT replaces entire resource
@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    """Calling multiple times has same result"""
    users_db[user_id] = user
    return user

# NOT idempotent: POST creates new resource
@app.post("/orders")
async def create_order(order: Order):
    """Calling twice creates two orders"""
    order.id = generate_id()
    orders_db[order.id] = order
    return order

# Making POST idempotent with idempotency key
@app.post("/payments")
async def create_payment(
    payment: Payment,
    idempotency_key: str = Header(...)
):
    """Use idempotency key to prevent duplicates"""
    existing = get_by_idempotency_key(idempotency_key)
    if existing:
        return existing  # Return cached result

    result = process_payment(payment)
    cache_with_key(idempotency_key, result)
    return result
```

---

## 11. Caching Strategies

### What It Is

Caching stores copies of responses to improve performance and reduce server load.

### Cache Types

1. **Browser Cache** - Client-side caching
2. **CDN Cache** - Edge caching
3. **Application Cache** - Server-side caching
4. **Database Cache** - Query result caching

### Examples

```python
from fastapi import Response
from datetime import datetime, timedelta

@app.get("/products/{product_id}")
async def get_product(product_id: int, response: Response):
    """Set caching headers"""
    product = get_from_db(product_id)

    # Cache for 1 hour
    response.headers["Cache-Control"] = "public, max-age=3600"

    # ETag for validation
    response.headers["ETag"] = f'"{product.version}"'

    # Last-Modified for conditional requests
    response.headers["Last-Modified"] = product.updated_at.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    return product

@app.get("/data")
async def get_data(
    request: Request,
    response: Response
):
    """Handle conditional requests"""
    data = get_from_db()
    etag = generate_etag(data)

    # Check If-None-Match header
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)  # Not Modified

    response.headers["ETag"] = etag
    return data
```

---

## 12. Rate Limiting

### What It Is

Rate limiting restricts the number of requests a client can make within a time window.

### Common Algorithms

1. **Fixed Window** - X requests per minute/hour
2. **Sliding Window** - More accurate than fixed
3. **Token Bucket** - Allows bursts
4. **Leaky Bucket** - Smooth request rate

### Examples

```python
from fastapi import HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    """Limit to 10 requests per minute per IP"""
    return {"data": "value"}

@app.post("/api/upload")
@limiter.limit("5/hour")
async def upload_file(request: Request):
    """Limit to 5 uploads per hour"""
    return {"status": "uploaded"}
```

---

## Summary

These core concepts form the foundation of API development:

1. **REST Architecture** - Resource-based design with HTTP methods
2. **HTTP Protocol** - Methods, status codes, and headers
3. **GraphQL** - Query language for flexible data fetching
4. **Resources** - Proper URI design and naming
5. **Lifecycle** - Understanding request/response flow
6. **Data Modeling** - Structured input/output validation
7. **Auth** - Authentication (who) vs Authorization (what)
8. **Versioning** - Supporting multiple API versions
9. **Content Negotiation** - Multiple response formats
10. **Idempotency** - Safe retry behavior
11. **Caching** - Performance optimization
12. **Rate Limiting** - Protecting API resources

Master these concepts to build robust, scalable APIs.
