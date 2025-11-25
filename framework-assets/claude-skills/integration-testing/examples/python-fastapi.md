# Python FastAPI Integration Testing Examples

Complete examples demonstrating integration testing patterns for FastAPI applications.

## Basic FastAPI Application

```python
# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, database

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", status_code=201)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.main import app, get_db
from app.database import Base

@pytest.fixture(scope="session")
def postgres_container():
    """Start PostgreSQL container once per test session."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def engine(postgres_container):
    """Create SQLAlchemy engine."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    """Provide a transactional database session per test."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Provide a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## API Integration Tests

```python
# tests/integration/test_users_api.py
import pytest

def test_create_user_success(client):
    """Test successful user creation."""
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data

def test_create_user_duplicate_email(client, db_session):
    """Test duplicate email validation."""
    # Create first user
    client.post("/users", json={"name": "Alice", "email": "alice@example.com"})

    # Try to create duplicate
    response = client.post(
        "/users",
        json={"name": "Alice2", "email": "alice@example.com"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_user_success(client):
    """Test retrieving an existing user."""
    # Create user first
    create_response = client.post(
        "/users",
        json={"name": "Bob", "email": "bob@example.com"}
    )
    user_id = create_response.json()["id"]

    # Retrieve user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Bob"
    assert data["id"] == user_id

def test_get_user_not_found(client):
    """Test 404 for non-existent user."""
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
```

## Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
from app.models import User, Post
from sqlalchemy import text

def test_user_crud_operations(db_session):
    """Test basic CRUD operations."""
    # Create
    user = User(name="Charlie", email="charlie@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None

    # Read
    retrieved = db_session.query(User).filter(User.id == user.id).first()
    assert retrieved.name == "Charlie"

    # Update
    retrieved.name = "Charlie Updated"
    db_session.commit()
    db_session.refresh(retrieved)
    assert retrieved.name == "Charlie Updated"

    # Delete
    db_session.delete(retrieved)
    db_session.commit()
    deleted = db_session.query(User).filter(User.id == user.id).first()
    assert deleted is None

def test_foreign_key_constraint(db_session):
    """Test foreign key relationships."""
    user = User(name="David", email="david@example.com")
    db_session.add(user)
    db_session.commit()

    post = Post(title="Test Post", content="Content", author_id=user.id)
    db_session.add(post)
    db_session.commit()

    # Verify relationship
    assert post.author.name == "David"
    assert user.posts[0].title == "Test Post"

def test_unique_constraint_violation(db_session):
    """Test unique email constraint."""
    user1 = User(name="Eve", email="eve@example.com")
    db_session.add(user1)
    db_session.commit()

    user2 = User(name="Eve2", email="eve@example.com")
    db_session.add(user2)

    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()
```

## Authentication Integration Tests

```python
# tests/integration/test_auth.py
import pytest
from datetime import datetime, timedelta
import jwt

@pytest.fixture
def auth_token():
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": "test_user_123",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")

@pytest.fixture
def expired_token():
    """Generate an expired JWT token."""
    payload = {
        "sub": "test_user_123",
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")

def test_protected_endpoint_with_valid_token(client, auth_token):
    """Test accessing protected endpoint with valid token."""
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

def test_protected_endpoint_without_token(client):
    """Test 401 when no token provided."""
    response = client.get("/api/protected")
    assert response.status_code == 401

def test_protected_endpoint_with_expired_token(client, expired_token):
    """Test 401 with expired token."""
    response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_login_flow(client, db_session):
    """Test complete login flow."""
    # Create user
    from app.auth import hash_password
    user = User(
        name="LoginUser",
        email="login@example.com",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()

    # Login
    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Use token
    token = data["access_token"]
    protected_response = client.get(
        "/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == 200
```

## External Service Mocking

```python
# tests/integration/test_external_services.py
import pytest
import responses
from app.services import ExternalAPIService

@responses.activate
def test_fetch_external_user_data():
    """Test fetching data from external API."""
    responses.add(
        responses.GET,
        'https://api.external.com/users/123',
        json={'id': 123, 'name': 'External User', 'status': 'active'},
        status=200
    )

    service = ExternalAPIService()
    user_data = service.fetch_user(123)

    assert user_data['name'] == 'External User'
    assert user_data['status'] == 'active'

@responses.activate
def test_external_api_error_handling():
    """Test handling external API errors."""
    responses.add(
        responses.GET,
        'https://api.external.com/users/123',
        json={'error': 'Not found'},
        status=404
    )

    service = ExternalAPIService()
    with pytest.raises(Exception) as exc_info:
        service.fetch_user(123)

    assert "Not found" in str(exc_info.value)

@responses.activate
def test_external_api_retry_logic():
    """Test retry logic on transient failures."""
    # First call fails, second succeeds
    responses.add(
        responses.GET,
        'https://api.external.com/users/123',
        json={'error': 'Server error'},
        status=500
    )
    responses.add(
        responses.GET,
        'https://api.external.com/users/123',
        json={'id': 123, 'name': 'Success'},
        status=200
    )

    service = ExternalAPIService(max_retries=2)
    user_data = service.fetch_user(123)

    assert user_data['name'] == 'Success'
    assert len(responses.calls) == 2
```

## Factory Pattern for Test Data

```python
# tests/factories.py
import factory
from factory import fuzzy
from app.models import User, Post
from datetime import datetime

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None  # Will be set in fixture

    name = factory.Faker('name')
    email = factory.Faker('email')
    created_at = factory.LazyFunction(datetime.utcnow)

class PostFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session = None

    title = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('text', max_nb_chars=500)
    author = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)

# tests/conftest.py
@pytest.fixture
def factories(db_session):
    """Configure factories with current database session."""
    UserFactory._meta.sqlalchemy_session = db_session
    PostFactory._meta.sqlalchemy_session = db_session
    return {
        "User": UserFactory,
        "Post": PostFactory
    }

# tests/integration/test_with_factories.py
def test_user_with_posts(factories, client):
    """Test retrieving user with related posts."""
    # Create user with 3 posts
    user = factories["User"].create()
    posts = factories["Post"].create_batch(3, author=user)

    response = client.get(f"/users/{user.id}/posts")
    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) == 3

def test_bulk_user_creation(factories, db_session):
    """Test creating multiple users efficiently."""
    users = factories["User"].create_batch(10)

    user_count = db_session.query(User).count()
    assert user_count == 10
```

## Redis Integration Tests

```python
# tests/integration/test_redis.py
import pytest
import redis
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def redis_container():
    """Start Redis container."""
    with RedisContainer() as redis_cont:
        yield redis_cont

@pytest.fixture
def redis_client(redis_container):
    """Provide Redis client."""
    client = redis.from_url(redis_container.get_connection_url())
    yield client
    client.flushdb()  # Clean up after test
    client.close()

def test_cache_user_data(redis_client, client):
    """Test caching user data in Redis."""
    # Create user
    response = client.post(
        "/users",
        json={"name": "CachedUser", "email": "cached@example.com"}
    )
    user_id = response.json()["id"]

    # First request (cache miss)
    response1 = client.get(f"/users/{user_id}")
    assert response1.status_code == 200
    assert response1.headers.get("X-Cache") == "MISS"

    # Second request (cache hit)
    response2 = client.get(f"/users/{user_id}")
    assert response2.status_code == 200
    assert response2.headers.get("X-Cache") == "HIT"

    # Verify data matches
    assert response1.json() == response2.json()

def test_cache_invalidation(redis_client, client):
    """Test cache invalidation on update."""
    # Create and cache user
    response = client.post(
        "/users",
        json={"name": "Original", "email": "original@example.com"}
    )
    user_id = response.json()["id"]

    client.get(f"/users/{user_id}")  # Cache it

    # Update user
    client.put(f"/users/{user_id}", json={"name": "Updated"})

    # Verify cache was invalidated
    response = client.get(f"/users/{user_id}")
    assert response.headers.get("X-Cache") == "MISS"
    assert response.json()["name"] == "Updated"
```

## Background Tasks and Celery

```python
# tests/integration/test_background_tasks.py
import pytest
from celery import Celery
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def celery_broker(redis_container):
    """Configure Celery with test Redis broker."""
    return redis_container.get_connection_url()

@pytest.fixture
def celery_app(celery_broker):
    """Create Celery app for testing."""
    app = Celery('test', broker=celery_broker, backend=celery_broker)
    app.conf.task_always_eager = True  # Execute tasks synchronously
    app.conf.task_eager_propagates = True  # Propagate exceptions
    return app

def test_send_email_task(celery_app, client):
    """Test background email sending task."""
    response = client.post(
        "/users",
        json={"name": "TaskUser", "email": "task@example.com"}
    )
    assert response.status_code == 201

    # Verify task was queued and executed
    # (In eager mode, task runs synchronously)
    # Check email was sent (mock email service)

def test_long_running_task(celery_app):
    """Test long-running background task."""
    from app.tasks import process_large_file

    result = process_large_file.delay(file_id=123)
    assert result.successful()
    assert result.result == {"processed": 123, "status": "complete"}
```

## Complete Test Suite Example

```python
# tests/integration/test_user_lifecycle.py
import pytest

class TestUserLifecycle:
    """Test complete user lifecycle in integration."""

    def test_user_registration_and_login(self, client, db_session):
        """Test user can register and login."""
        # Register
        register_response = client.post(
            "/auth/register",
            json={
                "name": "NewUser",
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # Login
        login_response = client.post(
            "/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Access protected resource
        profile_response = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200

    def test_user_creates_content(self, client, auth_token):
        """Test authenticated user can create content."""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # Create post
        post_response = client.post(
            "/posts",
            json={"title": "My Post", "content": "Post content"},
            headers=headers
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]

        # Retrieve post
        get_response = client.get(f"/posts/{post_id}")
        assert get_response.status_code == 200

    def test_user_updates_profile(self, client, factories, auth_token):
        """Test user can update their profile."""
        user = factories["User"].create()
        headers = {"Authorization": f"Bearer {auth_token}"}

        update_response = client.put(
            f"/users/{user.id}",
            json={"name": "Updated Name"},
            headers=headers
        )
        assert update_response.status_code == 200

        # Verify update
        get_response = client.get(f"/users/{user.id}")
        assert get_response.json()["name"] == "Updated Name"

    def test_user_deletion_cascades(self, client, factories, db_session):
        """Test deleting user cascades to related content."""
        user = factories["User"].create()
        posts = factories["Post"].create_batch(3, author=user)

        # Delete user
        delete_response = client.delete(f"/users/{user.id}")
        assert delete_response.status_code == 204

        # Verify posts were deleted (cascade)
        for post in posts:
            response = client.get(f"/posts/{post.id}")
            assert response.status_code == 404
```
