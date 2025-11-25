# Integration Testing Skill

Comprehensive guide for creating, maintaining, and running integration tests that verify component interactions, APIs, databases, and external services.

## Quick Start

**When to use this skill:**
- Writing tests for API endpoints and HTTP interactions
- Testing database operations with real databases
- Validating message queue and event-driven systems
- Testing integrations with external services
- Setting up test environments with Docker
- Creating test data factories and fixtures

**Key files:**
- `SKILL.md` - Main reference with patterns and best practices
- `examples/` - Complete working examples for Python/FastAPI and JavaScript/Express
- `reference/` - Advanced patterns and techniques
- `templates/` - Ready-to-use configuration files

## Core Concepts

integration_test_fundamentals[5]{concept,description}:
Real interactions,Test actual component interactions not mocked units
Test pyramid,More than unit tests fewer than E2E (20-30% of tests)
Fast feedback,Each test should complete in <2 seconds ideally
Isolated state,Tests must be independent and clean up properly
Reproducible,Should work on any developer machine and CI/CD

## What's Included

skill_contents[7]{section,file,description}:
Main Guide,SKILL.md,Complete integration testing reference with TOON format examples
Python Examples,examples/python-fastapi.md,FastAPI integration tests with testcontainers pytest
JavaScript Examples,examples/javascript-express.md,Express.js tests with Jest supertest testcontainers
Advanced Patterns,reference/advanced-patterns.md,Contract testing performance testing distributed systems
Pytest Config,templates/pytest-config.py,Complete pytest configuration with fixtures and factories
Jest Config,templates/jest-config.js,Complete Jest configuration with setup and helpers
Docker Config,templates/docker-compose.test.yml,Docker Compose for test dependencies

## Quick Examples

### Python FastAPI Test

```python
import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest.fixture
def client(postgres_container):
    # Setup test client with real database
    return TestClient(app)

def test_create_user(client):
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

### JavaScript Express Test

```javascript
const request = require('supertest');
const { GenericContainer } = require('testcontainers');

describe('User API', () => {
  let container, app;

  beforeAll(async () => {
    container = await new GenericContainer('postgres:15-alpine')
      .withExposedPorts(5432)
      .start();

    // Setup app with test database
  });

  test('creates user', async () => {
    const response = await request(app)
      .post('/users')
      .send({ name: 'Alice', email: 'alice@example.com' })
      .expect(201);

    expect(response.body.name).toBe('Alice');
  });
});
```

## Test Categories

This skill covers:

test_categories[6]{category,examples,complexity}:
API Tests,HTTP endpoints authentication validation,Basic-Intermediate
Database Tests,CRUD transactions migrations,Basic-Intermediate
Message Queue Tests,Pub/sub work queues dead letters,Intermediate
External Service Tests,Third-party APIs mocking VCR,Intermediate-Advanced
Contract Tests,API versioning breaking changes,Advanced
Performance Tests,Load testing concurrent requests,Advanced

## Common Patterns

### Transaction Rollback Pattern

Most common database testing pattern - wrap each test in a transaction and rollback:

```python
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### Test Containers Pattern

Use Docker containers for real service dependencies:

```python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres
```

### Factory Pattern

Generate test data efficiently:

```python
class UserFactory:
    @staticmethod
    def create(**overrides):
        return User(
            name=faker.name(),
            email=faker.email(),
            **overrides
        )
```

## Getting Started

getting_started_steps[5]{step,action}:
1. Choose framework,Select Python/pytest or JavaScript/Jest based on your stack
2. Copy templates,Use templates/ configs as starting point
3. Start containers,Run docker-compose -f docker-compose.test.yml up -d
4. Write first test,Follow examples/ for your chosen framework
5. Run tests,Execute pytest tests/integration/ or npm test

## Best Practices

integration_test_best_practices[8]{practice,explanation}:
Use real databases,Test with actual DB not mocks - use containers
Fast setup/teardown,Keep tests under 2 seconds - use transactions
Independent tests,Each test should work in isolation
Clean state,Always clean up - rollback or truncate
Meaningful assertions,Test behavior not implementation details
Mock external APIs,Use WireMock nock responses for third-party APIs
Parallel execution,Run tests in parallel with xdist or Jest workers
Health checks in CI,Wait for services before running tests

## Tools and Libraries

### Python Stack

python_tools[6]{tool,purpose}:
pytest,Test framework with powerful fixtures
testcontainers,Docker containers for dependencies
httpx,Async HTTP client for API testing
factory_boy,Test data factories
responses,Mock HTTP requests
freezegun,Mock datetime for time-dependent tests

### JavaScript Stack

javascript_tools[6]{tool,purpose}:
Jest,Test framework with built-in mocking
supertest,HTTP assertions for Express
testcontainers-node,Docker containers for Node.js
@faker-js/faker,Generate fake test data
nock,HTTP request mocking
ioredis-mock,Redis mocking

## CI/CD Integration

ci_cd_considerations[5]{aspect,approach}:
Service dependencies,Use docker-compose or GitHub Actions services
Health checks,Wait for services before running tests
Parallel execution,Use test parallelization to speed up CI
Test isolation,Ensure tests work independently
Caching,Cache Docker images and dependencies

## Common Pitfalls

pitfalls_to_avoid[6]{pitfall,solution}:
Shared state between tests,Use transaction rollback or clean database per test
Slow tests,Use tmpfs for databases run in parallel
Flaky tests,Ensure proper cleanup add waits for async operations
Mocking too much,Use real services where practical
Port conflicts,Use dynamic ports or different ports for test services
Missing cleanup,Always cleanup resources in teardown

## Performance Tips

performance_tips[5]{tip,benefit}:
Session-scoped containers,Start containers once reuse across tests
Transaction rollback,Faster than truncating or recreating DB
Connection pooling,Reuse database connections
Parallel execution,Run tests across multiple workers
tmpfs for databases,Store test DB in memory not disk

## Resources

- Main skill documentation: `SKILL.md`
- Python examples: `examples/python-fastapi.md`
- JavaScript examples: `examples/javascript-express.md`
- Advanced patterns: `reference/advanced-patterns.md`
- Test configurations: `templates/`

## Need Help?

**Common questions:**

1. **How do I setup test database?**
   - Use testcontainers or docker-compose
   - See `templates/docker-compose.test.yml`

2. **How do I make tests fast?**
   - Use transaction rollback pattern
   - Session-scoped containers
   - Run tests in parallel

3. **How do I test external APIs?**
   - Use response mocking libraries (responses, nock)
   - Consider VCR pattern for recording/replaying
   - Use contract tests for API changes

4. **How do I handle authentication in tests?**
   - Generate test tokens in fixtures
   - Use test user credentials
   - Mock authentication middleware

## File Size Information

skill_file_sizes[6]{file,lines,status}:
SKILL.md,485,Within limit (500 max)
python-fastapi.md,475,Within limit
javascript-express.md,470,Within limit
advanced-patterns.md,495,Within limit
pytest-config.py,315,Within limit
jest-config.js,340,Within limit

All files are optimized and within the 500-line limit per file requirement.
