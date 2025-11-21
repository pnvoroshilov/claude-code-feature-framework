---
name: api-development
description: Comprehensive expertise in RESTful and GraphQL API design, implementation, testing, and deployment for building scalable, secure, and well-documented APIs
version: 1.0.0
tags: [api, rest, graphql, backend, development]
---

# API Development Skill

Comprehensive expertise in RESTful and GraphQL API design, implementation, testing, and deployment. This skill provides production-ready knowledge for building scalable, secure, and well-documented APIs.

## Overview

This skill covers the complete lifecycle of API development, from initial design and specification to deployment and monitoring. It encompasses both REST and GraphQL paradigms, industry best practices, security patterns, testing strategies, and operational excellence.

## Quick Start

### Basic REST API
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id, "name": "Sample Item"}

@app.post("/items")
async def create_item(item: Item):
    return {"id": 1, **item.dict()}
```

### Basic GraphQL API
```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: str = "World") -> str:
        return f"Hello, {name}!"

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
```

## Core Capabilities

This skill provides expert-level knowledge in:

### 1. API Design & Architecture
- RESTful API design principles and best practices
- GraphQL schema design and query optimization
- Resource modeling and URI design
- API versioning strategies (URI, header, content negotiation)
- HATEOAS and hypermedia-driven APIs
- API gateway patterns and service mesh integration
- Microservices communication patterns
- Event-driven API architecture

### 2. HTTP Protocol Mastery
- HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD)
- Status codes and their proper usage
- Headers and content negotiation
- Caching strategies (ETags, Cache-Control, Conditional requests)
- Range requests and partial responses
- Compression and encoding
- WebSockets and real-time communication
- Server-Sent Events (SSE)

### 3. Authentication & Authorization
- JWT token-based authentication
- OAuth 2.0 flows (Authorization Code, Client Credentials, etc.)
- API key management
- Basic and Bearer authentication
- Session-based authentication
- Role-based access control (RBAC)
- Attribute-based access control (ABAC)
- API rate limiting and throttling

### 4. Data Validation & Serialization
- Request validation with Pydantic, Marshmallow, or Joi
- Response serialization and deserialization
- Content type negotiation (JSON, XML, MessagePack)
- Schema validation (JSON Schema, OpenAPI)
- Input sanitization and XSS prevention
- Type coercion and conversion
- Custom validators and constraints

### 5. Error Handling & Status Codes
- Consistent error response formats
- Problem Details (RFC 7807)
- Validation error responses
- Exception handling middleware
- Logging and monitoring errors
- Retry strategies and idempotency
- Circuit breakers and fallbacks

### 6. API Documentation
- OpenAPI/Swagger specification
- API Blueprint and RAML
- GraphQL introspection and documentation
- Interactive API documentation (Swagger UI, ReDoc)
- SDK generation from specifications
- API versioning documentation
- Code examples and tutorials

### 7. Testing Strategies
- Unit testing API endpoints
- Integration testing with databases
- Contract testing (Pact, Spring Cloud Contract)
- Load testing (Locust, k6, JMeter)
- Security testing (OWASP API Security)
- Mocking and stubbing external services
- Test data management
- E2E testing strategies

### 8. Performance Optimization
- Database query optimization
- N+1 query problem solutions
- Response caching strategies
- Database connection pooling
- Async/await patterns
- Background task processing
- Rate limiting and backpressure
- Pagination and filtering

### 9. Security Best Practices
- OWASP API Security Top 10
- SQL injection prevention
- XSS and CSRF protection
- Input validation and sanitization
- Secure headers (CORS, CSP, HSTS)
- Secrets management
- Encryption at rest and in transit
- Security auditing and compliance

### 10. API Deployment & Operations
- Containerization (Docker)
- Orchestration (Kubernetes)
- CI/CD pipelines for APIs
- Blue-green and canary deployments
- API monitoring and observability
- Logging and tracing (OpenTelemetry)
- Health checks and readiness probes
- Disaster recovery and backup

## Documentation

### Core Learning Resources
- **[Core Concepts](docs/core-concepts.md)** - Fundamental API concepts, HTTP protocol, REST principles, GraphQL basics
- **[Best Practices](docs/best-practices.md)** - Industry standards, design guidelines, security practices, performance tips
- **[Patterns](docs/patterns.md)** - Common API patterns, anti-patterns, architectural patterns, integration patterns
- **[Advanced Topics](docs/advanced-topics.md)** - Advanced features, optimization techniques, distributed systems, event-driven APIs
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues, debugging strategies, error resolution, performance troubleshooting
- **[API Reference](docs/api-reference.md)** - Complete framework reference for FastAPI, GraphQL, testing tools

## Examples

### Basic Examples
Start here for fundamental API patterns:
- **[Example 1: Simple CRUD API](examples/basic/example-1.md)** - Basic create, read, update, delete operations
- **[Example 2: Request Validation](examples/basic/example-2.md)** - Input validation and error handling
- **[Example 3: Authentication Setup](examples/basic/example-3.md)** - JWT authentication implementation

### Intermediate Examples
More complex real-world scenarios:
- **[Pattern 1: Pagination & Filtering](examples/intermediate/pattern-1.md)** - Efficient data querying with pagination
- **[Pattern 2: File Upload API](examples/intermediate/pattern-2.md)** - Handling file uploads and downloads
- **[Pattern 3: Background Tasks](examples/intermediate/pattern-3.md)** - Async task processing and job queues

### Advanced Examples
Production-ready patterns for expert developers:
- **[Advanced 1: GraphQL with DataLoader](examples/advanced/advanced-pattern-1.md)** - Solving N+1 queries with DataLoader
- **[Advanced 2: Rate Limiting & Throttling](examples/advanced/advanced-pattern-2.md)** - Implementing distributed rate limiting
- **[Advanced 3: API Gateway Pattern](examples/advanced/advanced-pattern-3.md)** - Building an API gateway with routing and authentication

## Templates

Ready-to-use templates for quick project setup:
- **[Template 1: REST API Starter](templates/template-1.md)** - Complete REST API project structure with FastAPI
- **[Template 2: GraphQL API Starter](templates/template-2.md)** - Production-ready GraphQL API with Strawberry
- **[Template 3: Microservices API](templates/template-3.md)** - Microservices architecture with service discovery

## Resources

### Development Resources
- **[Quality Checklists](resources/checklists.md)** - Pre-deployment checklist, code review checklist, security audit
- **[Complete Glossary](resources/glossary.md)** - API terminology, HTTP terms, GraphQL vocabulary
- **[External References](resources/references.md)** - Official documentation, tutorials, community resources
- **[Step-by-Step Workflows](resources/workflows.md)** - Development workflows, testing workflows, deployment procedures

## Scripts

Utility scripts for API development:
- **[OpenAPI Generator](scripts/generate_openapi.py)** - Generate OpenAPI specification from code
- **[API Test Runner](scripts/run_api_tests.py)** - Automated API testing script

## Usage Examples

### Example 1: Building a REST API

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
import jwt

app = FastAPI(
    title="E-Commerce API",
    description="RESTful API for e-commerce platform",
    version="1.0.0"
)

# Models
class Product(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 0

# Authentication
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, "secret", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@app.get("/products", response_model=List[Product])
async def list_products(skip: int = 0, limit: int = 10):
    """List all products with pagination"""
    # Database query here
    return []

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a single product by ID"""
    # Database query here
    return Product(id=product_id, name="Sample", description="Test", price=9.99)

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    user: dict = Depends(verify_token)
):
    """Create a new product (requires authentication)"""
    # Database insert here
    return Product(id=1, **product.dict())

@app.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductCreate,
    user: dict = Depends(verify_token)
):
    """Update an existing product"""
    # Database update here
    return Product(id=product_id, **product.dict())

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    user: dict = Depends(verify_token)
):
    """Delete a product"""
    # Database delete here
    return None
```

### Example 2: Building a GraphQL API

```python
import strawberry
from typing import List, Optional
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

# Types
@strawberry.type
class Product:
    id: int
    name: str
    description: str
    price: float
    stock: int

@strawberry.input
class ProductInput:
    name: str
    description: str
    price: float
    stock: int = 0

# Query
@strawberry.type
class Query:
    @strawberry.field
    def products(self, limit: int = 10) -> List[Product]:
        """Get all products"""
        return []

    @strawberry.field
    def product(self, id: int) -> Optional[Product]:
        """Get product by ID"""
        return None

# Mutation
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_product(self, input: ProductInput) -> Product:
        """Create a new product"""
        return Product(
            id=1,
            name=input.name,
            description=input.description,
            price=input.price,
            stock=input.stock
        )

    @strawberry.mutation
    def update_product(self, id: int, input: ProductInput) -> Product:
        """Update an existing product"""
        return Product(
            id=id,
            name=input.name,
            description=input.description,
            price=input.price,
            stock=input.stock
        )

    @strawberry.mutation
    def delete_product(self, id: int) -> bool:
        """Delete a product"""
        return True

# Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# FastAPI integration
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```

### Example 3: API Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestProductAPI:
    """Test suite for Product API endpoints"""

    def test_list_products(self):
        """Test listing products"""
        response = client.get("/products")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_product(self):
        """Test getting a single product"""
        response = client.get("/products/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data

    def test_create_product_unauthorized(self):
        """Test creating product without authentication"""
        product = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 9.99
        }
        response = client.post("/products", json=product)
        assert response.status_code == 403

    def test_create_product_with_auth(self):
        """Test creating product with authentication"""
        token = "valid_jwt_token_here"
        headers = {"Authorization": f"Bearer {token}"}
        product = {
            "name": "Test Product",
            "description": "Test Description",
            "price": 9.99
        }
        response = client.post("/products", json=product, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product["name"]

    def test_invalid_product_data(self):
        """Test validation error handling"""
        product = {
            "name": "",  # Invalid: empty name
            "price": -10  # Invalid: negative price
        }
        response = client.post("/products", json=product)
        assert response.status_code == 422  # Validation error
```

### Example 4: Database Integration

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API with database
@app.get("/products", response_model=List[Product])
async def list_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List products from database"""
    products = db.query(ProductModel).offset(skip).limit(limit).all()
    return products

@app.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    """Create product in database"""
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
```

### Example 5: Error Handling

```python
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI()

# Custom exception
class ProductNotFoundException(Exception):
    def __init__(self, product_id: int):
        self.product_id = product_id

# Exception handlers
@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "product_not_found",
            "message": f"Product with ID {exc.product_id} not found",
            "product_id": exc.product_id
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": errors
        }
    )

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    # Simulate product lookup
    if product_id > 1000:
        raise ProductNotFoundException(product_id)
    return {"id": product_id, "name": "Sample Product"}
```

## When to Use This Skill

Use this skill when you need to:

1. **Design a new API** - Plan endpoints, resources, and data models
2. **Implement API endpoints** - Build REST or GraphQL APIs
3. **Add authentication** - Implement JWT, OAuth, or API keys
4. **Optimize performance** - Improve query performance, add caching
5. **Enhance security** - Apply OWASP best practices
6. **Write API tests** - Unit, integration, and E2E testing
7. **Document APIs** - Generate OpenAPI specs, write guides
8. **Debug API issues** - Troubleshoot errors, performance problems
9. **Deploy APIs** - Containerize and deploy to production
10. **Scale APIs** - Handle high traffic, implement rate limiting

## Integration with Other Skills

This skill works well with:
- **Database Design** - Design database schemas for API data
- **Authentication & Security** - Implement advanced security patterns
- **Testing** - Comprehensive API testing strategies
- **DevOps** - Deploy and monitor APIs in production
- **Frontend Development** - Build API clients and integrations

## Limitations

This skill focuses on API development. It does **not** cover:
- Frontend UI development (use frontend skills)
- Database administration (use database skills)
- Infrastructure management (use DevOps skills)
- Business logic design (use domain modeling skills)

## Getting Help

If you encounter issues:
1. Check **[Troubleshooting Guide](docs/troubleshooting.md)** for common problems
2. Review **[Best Practices](docs/best-practices.md)** for design guidance
3. Explore **[Examples](examples/)** for code patterns
4. Consult **[API Reference](docs/api-reference.md)** for framework details

## Next Steps

1. **Start with basics** - Read [Core Concepts](docs/core-concepts.md)
2. **Learn best practices** - Study [Best Practices](docs/best-practices.md)
3. **Try examples** - Build the [Basic Examples](examples/basic/)
4. **Use templates** - Start a project with [Templates](templates/)
5. **Go advanced** - Explore [Advanced Topics](docs/advanced-topics.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-01-31
**Maintainer**: Claude Code Skills Team
