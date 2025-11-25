# pytest.ini - Place in project root
"""
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Directories to search for tests
testpaths = tests

# Markers for categorizing tests
markers =
    integration: Integration tests (require external services)
    slow: Slow-running tests (> 5 seconds)
    database: Tests that require database
    redis: Tests that require Redis
    rabbitmq: Tests that require RabbitMQ
    external_api: Tests that call external APIs
    contract: Contract tests with Pact

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml

# Timeout settings (requires pytest-timeout)
timeout = 300
timeout_method = thread

# Parallel execution (requires pytest-xdist)
# Uncomment to run tests in parallel
# addopts = -n auto

# Logging
log_cli = true
log_cli_level = INFO
log_file = tests/logs/pytest.log
log_file_level = DEBUG

# Asyncio configuration
asyncio_mode = auto
"""

# conftest.py - Place in tests/ directory
"""
Pytest configuration and shared fixtures for integration tests.
"""

import pytest
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
import redis
from fastapi.testclient import TestClient

# Import your application
from app.main import app
from app.database import Base, get_db
from app.config import Settings


# ============================================================================
# Session-Scoped Fixtures (Created Once Per Test Session)
# ============================================================================

@pytest.fixture(scope="session")
def postgres_container():
    """
    Start PostgreSQL container once per test session.
    Reused across all tests for performance.
    """
    with PostgresContainer(
        "postgres:15-alpine",
        username="test_user",
        password="test_pass",
        dbname="test_db"
    ) as postgres:
        # Optionally run initialization scripts
        # postgres.exec(["psql", "-U", "test_user", "-f", "/init.sql"])
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """Start Redis container once per test session."""
    with RedisContainer("redis:7-alpine") as redis_cont:
        yield redis_cont


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """
    Create SQLAlchemy engine connected to test database.
    Creates all tables once at session start.
    """
    engine = create_engine(
        postgres_container.get_connection_url(),
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Drop all tables at end of session
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def redis_client(redis_container):
    """Create Redis client connected to test Redis."""
    client = redis.from_url(
        redis_container.get_connection_url(),
        decode_responses=True
    )
    yield client
    client.close()


# ============================================================================
# Function-Scoped Fixtures (Created Per Test)
# ============================================================================

@pytest.fixture
def db_session(db_engine):
    """
    Provide a transactional database session for each test.
    All changes are rolled back after the test completes.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    # Create session bound to this connection
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    # Ensure nested transactions work with savepoints
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    session.begin_nested()

    yield session

    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """
    Provide FastAPI test client with database dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def redis_test_client(redis_client):
    """
    Provide Redis client that flushes data before and after each test.
    """
    redis_client.flushdb()
    yield redis_client
    redis_client.flushdb()


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def auth_token(db_session):
    """Generate valid JWT token for testing."""
    from datetime import datetime, timedelta
    import jwt
    from app.config import settings

    payload = {
        "sub": "test_user_id",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def auth_headers(auth_token):
    """Provide authentication headers for requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def authenticated_client(client, auth_headers):
    """Provide client with authentication already configured."""
    client.headers.update(auth_headers)
    return client


# ============================================================================
# Factory Fixtures
# ============================================================================

@pytest.fixture
def user_factory(db_session):
    """Factory for creating test users."""
    from faker import Faker
    from app.models import User

    fake = Faker()

    def create_user(**kwargs):
        defaults = {
            "name": fake.name(),
            "email": fake.email(),
            "password": "test_password_123"
        }
        defaults.update(kwargs)

        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return create_user


@pytest.fixture
def post_factory(db_session, user_factory):
    """Factory for creating test posts."""
    from faker import Faker
    from app.models import Post

    fake = Faker()

    def create_post(**kwargs):
        if 'user_id' not in kwargs:
            user = user_factory()
            kwargs['user_id'] = user.id

        defaults = {
            "title": fake.sentence(),
            "content": fake.text(max_nb_chars=500)
        }
        defaults.update(kwargs)

        post = Post(**defaults)
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        return post

    return create_post


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def sample_data(db_session, user_factory, post_factory):
    """
    Load sample data for tests that need pre-populated database.
    """
    users = [user_factory() for _ in range(5)]

    for user in users:
        for _ in range(3):
            post_factory(user_id=user.id)

    return {"users": users}


@pytest.fixture
def mock_external_api():
    """
    Mock external API responses using responses library.
    """
    import responses

    with responses.RequestsMock() as rsps:
        # Add default mocks
        rsps.add(
            responses.GET,
            "https://api.external.com/health",
            json={"status": "ok"},
            status=200
        )
        yield rsps


# ============================================================================
# Environment Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def test_env_vars():
    """
    Set test environment variables for all tests.
    autouse=True means this runs automatically for every test.
    """
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "test"  # Will be overridden by fixtures
    os.environ["REDIS_URL"] = "test"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"

    yield

    # Cleanup (optional)
    # del os.environ["ENVIRONMENT"]


# ============================================================================
# Async Fixtures (for async tests)
# ============================================================================

@pytest.fixture
async def async_client(db_session):
    """
    Provide async test client for async endpoints.
    Requires httpx and pytest-asyncio.
    """
    from httpx import AsyncClient

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def benchmark_timer():
    """
    Simple benchmark timer for performance-sensitive tests.
    """
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()


# ============================================================================
# Marker Helpers
# ============================================================================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow-running"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically add markers based on test location or name.
    """
    for item in items:
        # Add 'integration' marker to all tests in tests/integration/
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add 'slow' marker to tests with 'slow' in name
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)


# ============================================================================
# Hooks for Better Output
# ============================================================================

def pytest_runtest_makereport(item, call):
    """
    Add custom information to test reports.
    """
    if call.when == "call":
        # Log test duration for slow tests
        if call.duration > 5:
            print(f"\n⚠️  Slow test: {item.name} took {call.duration:.2f}s")
