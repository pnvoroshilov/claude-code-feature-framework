# Advanced Integration Testing Patterns

Deep dive into sophisticated integration testing patterns and techniques.

## Contract Testing

Contract testing ensures that service boundaries and APIs maintain backward compatibility.

### Consumer-Driven Contracts with Pact

**Consumer Side (Python)**:
```python
# tests/pacts/test_user_service_consumer.py
import pytest
from pact import Consumer, Provider

pact = Consumer('UserWebApp').has_pact_with(
    Provider('UserService'),
    pact_dir='./pacts'
)

def test_get_user():
    expected = {
        'id': 1,
        'name': 'Alice',
        'email': 'alice@example.com'
    }

    (pact
     .given('user 1 exists')
     .upon_receiving('a request for user 1')
     .with_request('GET', '/users/1')
     .will_respond_with(200, body=expected))

    with pact:
        user_service = UserService('http://localhost:1234')
        user = user_service.get_user(1)
        assert user['name'] == 'Alice'
```

**Provider Side Verification**:
```python
# tests/pacts/verify_provider.py
from pact import Verifier

verifier = Verifier(provider='UserService', provider_base_url='http://localhost:8000')

def test_verify_pacts():
    success, logs = verifier.verify_pacts(
        './pacts/userwebapp-userservice.json',
        provider_states_setup_url='http://localhost:8000/_pact/provider_states'
    )
    assert success == 0
```

**Provider State Setup**:
```python
# app/pact_provider_states.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/_pact/provider_states', methods=['POST'])
def provider_states():
    state = request.json.get('state')

    if state == 'user 1 exists':
        # Setup: Create user with ID 1
        db.session.add(User(id=1, name='Alice', email='alice@example.com'))
        db.session.commit()

    return {'result': 'success'}
```

### Schema Contract Testing

**OpenAPI Schema Validation**:
```python
import pytest
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename
import yaml

def test_api_conforms_to_openapi_spec(client):
    # Load OpenAPI specification
    spec_dict, spec_url = read_from_filename('openapi.yaml')

    # Validate spec is valid
    validate_spec(spec_dict)

    # Test actual API responses match spec
    response = client.get('/users/1')
    user_data = response.json()

    # Get user schema from spec
    user_schema = spec_dict['components']['schemas']['User']

    # Validate response against schema
    from jsonschema import validate
    validate(instance=user_data, schema=user_schema)
```

## Test Data Builders

Advanced patterns for managing complex test data.

### Object Mother Pattern

```python
# tests/helpers/object_mothers.py
from datetime import datetime, timedelta
from app.models import User, Order, OrderItem, Product

class UserMother:
    @staticmethod
    def basic_user():
        return User(
            name="Test User",
            email="test@example.com",
            created_at=datetime.utcnow()
        )

    @staticmethod
    def premium_user():
        user = UserMother.basic_user()
        user.subscription_tier = "premium"
        user.subscription_expires = datetime.utcnow() + timedelta(days=365)
        return user

    @staticmethod
    def admin_user():
        user = UserMother.basic_user()
        user.role = "admin"
        user.permissions = ["read", "write", "delete", "admin"]
        return user

class OrderMother:
    @staticmethod
    def simple_order(user=None):
        if user is None:
            user = UserMother.basic_user()

        product = ProductMother.physical_product()

        order = Order(
            user=user,
            status="pending",
            total_amount=product.price,
            created_at=datetime.utcnow()
        )
        order.items = [
            OrderItem(product=product, quantity=1, price=product.price)
        ]
        return order

    @staticmethod
    def complex_order_with_multiple_items(user=None):
        if user is None:
            user = UserMother.basic_user()

        products = [
            ProductMother.physical_product(),
            ProductMother.digital_product(),
            ProductMother.physical_product()
        ]

        order = Order(user=user, status="pending")
        order.items = [
            OrderItem(product=p, quantity=i+1, price=p.price)
            for i, p in enumerate(products)
        ]
        order.total_amount = sum(item.price * item.quantity for item in order.items)
        return order

class ProductMother:
    @staticmethod
    def physical_product():
        return Product(
            name="Physical Item",
            price=29.99,
            stock=100,
            type="physical",
            weight=0.5
        )

    @staticmethod
    def digital_product():
        return Product(
            name="Digital Download",
            price=9.99,
            stock=999999,
            type="digital"
        )

# Usage in tests
def test_order_checkout(db_session):
    user = UserMother.premium_user()
    order = OrderMother.complex_order_with_multiple_items(user)

    db_session.add(user)
    db_session.add(order)
    db_session.commit()

    # Test checkout flow
    result = checkout_service.process_order(order.id)
    assert result.status == "completed"
```

### Test Data Builder Pattern

```python
# tests/builders/user_builder.py
class UserBuilder:
    def __init__(self):
        self._user = User(
            name="Default User",
            email="default@example.com"
        )

    def with_name(self, name):
        self._user.name = name
        return self

    def with_email(self, email):
        self._user.email = email
        return self

    def as_premium(self):
        self._user.subscription_tier = "premium"
        self._user.subscription_expires = datetime.utcnow() + timedelta(days=365)
        return self

    def as_admin(self):
        self._user.role = "admin"
        self._user.permissions = ["read", "write", "delete", "admin"]
        return self

    def with_posts(self, count):
        self._user.posts = [
            Post(title=f"Post {i}", content=f"Content {i}")
            for i in range(count)
        ]
        return self

    def build(self):
        return self._user

# Usage
def test_premium_user_features():
    user = (UserBuilder()
            .with_name("Premium User")
            .with_email("premium@example.com")
            .as_premium()
            .with_posts(5)
            .build())

    db.session.add(user)
    db.session.commit()

    assert user.subscription_tier == "premium"
    assert len(user.posts) == 5
```

## Database State Management

### Database Snapshots

```python
# tests/helpers/db_snapshot.py
import json
from sqlalchemy import inspect

class DatabaseSnapshot:
    def __init__(self, session):
        self.session = session
        self.snapshot = None

    def capture(self):
        """Capture current database state."""
        self.snapshot = {}

        for table in Base.metadata.sorted_tables:
            rows = self.session.execute(table.select()).fetchall()
            self.snapshot[table.name] = [
                dict(row._mapping) for row in rows
            ]

    def restore(self):
        """Restore database to captured state."""
        if not self.snapshot:
            raise ValueError("No snapshot captured")

        # Disable foreign key checks
        self.session.execute("SET FOREIGN_KEY_CHECKS=0")

        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())

        for table_name, rows in self.snapshot.items():
            table = Base.metadata.tables[table_name]
            if rows:
                self.session.execute(table.insert(), rows)

        # Re-enable foreign key checks
        self.session.execute("SET FOREIGN_KEY_CHECKS=1")
        self.session.commit()

# Usage
@pytest.fixture
def db_snapshot(db_session):
    snapshot = DatabaseSnapshot(db_session)
    snapshot.capture()
    yield
    snapshot.restore()

def test_with_snapshot(db_snapshot, db_session):
    # Make changes
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    # Changes are automatically rolled back by snapshot fixture
```

### Fixture Data Management

```yaml
# tests/fixtures/users.yaml
users:
  - id: 1
    name: Alice
    email: alice@example.com
    role: admin
    created_at: 2024-01-01T00:00:00Z

  - id: 2
    name: Bob
    email: bob@example.com
    role: user
    created_at: 2024-01-02T00:00:00Z

  - id: 3
    name: Charlie
    email: charlie@example.com
    role: user
    created_at: 2024-01-03T00:00:00Z

posts:
  - id: 1
    title: First Post
    content: Content here
    author_id: 1
    created_at: 2024-01-05T00:00:00Z

  - id: 2
    title: Second Post
    content: More content
    author_id: 2
    created_at: 2024-01-06T00:00:00Z
```

```python
# tests/helpers/fixture_loader.py
import yaml
from pathlib import Path
from datetime import datetime

class FixtureLoader:
    def __init__(self, db_session, fixtures_dir='tests/fixtures'):
        self.db_session = db_session
        self.fixtures_dir = Path(fixtures_dir)

    def load(self, fixture_name):
        """Load fixture data from YAML file."""
        fixture_path = self.fixtures_dir / f'{fixture_name}.yaml'

        with open(fixture_path) as f:
            data = yaml.safe_load(f)

        self._load_data(data)

    def _load_data(self, data):
        """Insert fixture data into database."""
        model_map = {
            'users': User,
            'posts': Post,
            'orders': Order,
        }

        for table_name, rows in data.items():
            model = model_map.get(table_name)
            if not model:
                continue

            for row_data in rows:
                # Convert ISO datetime strings
                for key, value in row_data.items():
                    if isinstance(value, str) and 'T' in value:
                        try:
                            row_data[key] = datetime.fromisoformat(
                                value.replace('Z', '+00:00')
                            )
                        except ValueError:
                            pass

                obj = model(**row_data)
                self.db_session.add(obj)

        self.db_session.commit()

# Usage
@pytest.fixture
def load_fixtures(db_session):
    loader = FixtureLoader(db_session)
    return loader.load

def test_with_fixtures(load_fixtures, db_session):
    load_fixtures('users')

    users = db_session.query(User).all()
    assert len(users) == 3
```

## Testing Asynchronous Operations

### Async Test Patterns (Python asyncio)

```python
# tests/integration/test_async_operations.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test handling multiple concurrent requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 10 concurrent requests
        tasks = [
            client.post("/users", json={"name": f"User{i}", "email": f"user{i}@test.com"})
            for i in range(10)
        ]

        responses = await asyncio.gather(*tasks)

        # Verify all succeeded
        for response in responses:
            assert response.status_code == 201

@pytest.mark.asyncio
async def test_async_database_operations(async_db_session):
    """Test async database operations."""
    from sqlalchemy import select

    # Insert users concurrently
    users = [
        User(name=f"User{i}", email=f"user{i}@test.com")
        for i in range(5)
    ]

    async_db_session.add_all(users)
    await async_db_session.commit()

    # Query concurrently
    result = await async_db_session.execute(select(User))
    all_users = result.scalars().all()

    assert len(all_users) == 5

@pytest.mark.asyncio
async def test_background_task_completion():
    """Test background task completes successfully."""
    task_id = await start_background_task()

    # Poll for completion
    max_attempts = 10
    for _ in range(max_attempts):
        status = await get_task_status(task_id)
        if status == "completed":
            break
        await asyncio.sleep(0.5)
    else:
        pytest.fail("Task did not complete in time")

    result = await get_task_result(task_id)
    assert result["success"] is True
```

### Event-Driven Testing

```python
# tests/integration/test_event_driven.py
import pytest
from unittest.mock import Mock, patch
from app.events import EventBus, UserCreatedEvent

@pytest.fixture
def event_bus():
    return EventBus()

def test_event_subscribers_triggered(event_bus):
    """Test event triggers all subscribers."""
    handler1 = Mock()
    handler2 = Mock()

    event_bus.subscribe(UserCreatedEvent, handler1)
    event_bus.subscribe(UserCreatedEvent, handler2)

    event = UserCreatedEvent(user_id=1, email="test@example.com")
    event_bus.publish(event)

    handler1.assert_called_once_with(event)
    handler2.assert_called_once_with(event)

@pytest.mark.asyncio
async def test_async_event_handling(event_bus):
    """Test asynchronous event processing."""
    received_events = []

    async def async_handler(event):
        await asyncio.sleep(0.1)  # Simulate async work
        received_events.append(event)

    event_bus.subscribe(UserCreatedEvent, async_handler)

    # Publish multiple events
    events = [
        UserCreatedEvent(user_id=i, email=f"user{i}@test.com")
        for i in range(5)
    ]

    for event in events:
        await event_bus.publish_async(event)

    # Wait for all handlers
    await asyncio.sleep(0.6)

    assert len(received_events) == 5

def test_event_order_preservation(event_bus):
    """Test events are processed in order."""
    results = []

    def handler(event):
        results.append(event.user_id)

    event_bus.subscribe(UserCreatedEvent, handler)

    for i in range(10):
        event_bus.publish(UserCreatedEvent(user_id=i, email=f"user{i}@test.com"))

    assert results == list(range(10))
```

## Testing Distributed Systems

### Service Mesh Testing

```python
# tests/integration/test_service_mesh.py
import pytest
from testcontainers.compose import DockerCompose

@pytest.fixture(scope="session")
def service_mesh():
    """Start multiple interconnected services."""
    with DockerCompose(
        "tests/docker-compose.test.yaml",
        compose_file_name="docker-compose.test.yaml",
        pull=True
    ) as compose:
        # Wait for services to be healthy
        compose.wait_for("http://localhost:8001/health")
        compose.wait_for("http://localhost:8002/health")
        compose.wait_for("http://localhost:8003/health")

        yield {
            "api_gateway": "http://localhost:8001",
            "user_service": "http://localhost:8002",
            "order_service": "http://localhost:8003"
        }

def test_service_to_service_communication(service_mesh):
    """Test services communicate correctly."""
    import requests

    # Create user via API gateway
    response = requests.post(
        f"{service_mesh['api_gateway']}/users",
        json={"name": "Test User", "email": "test@example.com"}
    )
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Create order for user (order service calls user service)
    order_response = requests.post(
        f"{service_mesh['api_gateway']}/orders",
        json={"user_id": user_id, "items": [{"product_id": 1, "quantity": 2}]}
    )
    assert order_response.status_code == 201

    # Verify order has user data
    order = order_response.json()
    assert order["user"]["id"] == user_id

def test_circuit_breaker_activation(service_mesh):
    """Test circuit breaker trips on service failure."""
    import requests

    # Simulate service failure
    requests.post(f"{service_mesh['user_service']}/_test/simulate_failure")

    # Multiple failed requests should trip circuit breaker
    for _ in range(10):
        response = requests.get(
            f"{service_mesh['api_gateway']}/users/1",
            timeout=1
        )

    # Circuit should be open, returning 503
    response = requests.get(f"{service_mesh['api_gateway']}/users/1")
    assert response.status_code == 503
    assert "circuit breaker open" in response.json()["error"].lower()
```

## Performance and Load Testing Integration

```python
# tests/integration/test_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_response_time_under_load(client):
    """Test response times remain acceptable under load."""
    def make_request():
        start = time.time()
        response = client.get('/api/users')
        duration = time.time() - start
        return response.status_code, duration

    # Make 100 concurrent requests
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in as_completed(futures)]

    # Verify all succeeded
    statuses = [r[0] for r in results]
    assert all(s == 200 for s in statuses)

    # Verify P95 response time
    durations = sorted([r[1] for r in results])
    p95_duration = durations[int(len(durations) * 0.95)]

    assert p95_duration < 1.0, f"P95 response time {p95_duration}s exceeds 1s threshold"

def test_database_connection_pool(db_engine):
    """Test connection pool handles concurrent queries."""
    def query_database():
        with db_engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM users")
            return result.scalar()

    # Make many concurrent queries
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(query_database) for _ in range(100)]
        results = [f.result() for f in as_completed(futures)]

    # All queries should complete successfully
    assert len(results) == 100

@pytest.mark.slow
def test_sustained_load(client):
    """Test system stability under sustained load."""
    duration_seconds = 60
    requests_per_second = 10

    start_time = time.time()
    request_count = 0
    errors = 0

    while time.time() - start_time < duration_seconds:
        cycle_start = time.time()

        for _ in range(requests_per_second):
            try:
                response = client.get('/api/health')
                if response.status_code != 200:
                    errors += 1
                request_count += 1
            except Exception:
                errors += 1

        # Sleep to maintain rate
        elapsed = time.time() - cycle_start
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

    error_rate = errors / request_count
    assert error_rate < 0.01, f"Error rate {error_rate:.2%} exceeds 1% threshold"
```

## Advanced Mocking Patterns

### Time Travel Testing

```python
# tests/integration/test_time_dependent.py
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_subscription_expiration(db_session, client):
    """Test subscription expiration logic."""
    user = User(
        name="Test User",
        email="test@example.com",
        subscription_expires=datetime(2024, 1, 1, 11, 59, 59)  # Just expired
    )
    db_session.add(user)
    db_session.commit()

    response = client.get(f'/users/{user.id}/subscription')

    assert response.json()['status'] == 'expired'

def test_scheduled_task_execution():
    """Test scheduled task runs at correct time."""
    with freeze_time("2024-01-01 00:00:00") as frozen_time:
        scheduler.start()

        # Advance time to trigger task
        frozen_time.move_to("2024-01-01 09:00:00")

        # Verify task executed
        assert scheduler.get_task_log("daily_report")['last_run'] == datetime(2024, 1, 1, 9, 0, 0)
```

### Advanced Response Mocking

```python
# tests/integration/test_advanced_mocking.py
import pytest
import responses
from responses import matchers

@responses.activate
def test_conditional_mocking():
    """Test different responses based on request parameters."""

    def request_callback(request):
        user_id = request.url.split('/')[-1]

        if user_id == '1':
            return (200, {}, '{"name": "Alice", "status": "active"}')
        elif user_id == '999':
            return (404, {}, '{"error": "Not found"}')
        else:
            return (200, {}, f'{{"name": "User {user_id}", "status": "active"}}')

    responses.add_callback(
        responses.GET,
        'https://api.example.com/users/',
        callback=request_callback,
        content_type='application/json',
    )

    # Test different scenarios
    service = ExternalService()
    user1 = service.get_user(1)
    assert user1['name'] == 'Alice'

    with pytest.raises(Exception):
        service.get_user(999)

@responses.activate
def test_stateful_mocking():
    """Test mock that maintains state across calls."""
    call_count = {'count': 0}

    def stateful_callback(request):
        call_count['count'] += 1

        if call_count['count'] == 1:
            return (503, {}, '{"error": "Service unavailable"}')
        else:
            return (200, {}, '{"status": "success"}')

    responses.add_callback(
        responses.GET,
        'https://api.example.com/status',
        callback=stateful_callback
    )

    service = ExternalService(retry_count=2)
    result = service.check_status()  # First call fails, retry succeeds

    assert result['status'] == 'success'
    assert call_count['count'] == 2
```
