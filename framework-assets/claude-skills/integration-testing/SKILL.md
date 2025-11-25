---
name: integration-testing
description: Comprehensive integration testing best practices for testing component interactions, APIs, databases, and external services. Use when writing integration tests, setting up test environments, testing microservices, or validating system interactions.
version: 1.0.0
tags: [testing, integration-tests, api-testing, database-testing, quality]
---

# Integration Testing Expert

Comprehensive guide for creating, maintaining, and running integration tests that verify component interactions, APIs, databases, and external services.

## What is Integration Testing?

Integration testing validates that different parts of your system work correctly together. Unlike unit tests (isolated components) and E2E tests (full user workflows), integration tests focus on verifying interactions between components.

test_types_comparison[3]{test_type,scope,examples,speed}:
Unit Tests,Single component in isolation,Function with mocked dependencies,Very Fast (ms)
Integration Tests,Multiple components interacting,API + Database + Cache,Fast-Medium (100ms-2s)
E2E Tests,Complete user workflow,Browser automation full stack,Slow (5-30s)

## Test Pyramid Placement

```
     /\
    /E2E\      <- Few (5-10%)
   /------\
  / Integ \   <- More (20-30%)
 /----------\
/   Unit     \ <- Most (60-75%)
--------------
```

integration_test_principles[5]{principle,description}:
Test real interactions,Use actual databases message queues not all mocks
Isolated state,Each test should be independent and clean up after itself
Fast enough to run often,Target <2 seconds per test for quick feedback
Test contracts not implementations,Focus on API contracts and data formats
Environment reproducibility,Tests should work on any developer machine and CI

## Integration Test Categories

test_categories[4]{category,focus,typical_tools}:
API Tests,HTTP endpoints authentication validation,supertest httpx TestClient
Database Tests,CRUD transactions migrations constraints,testcontainers SQLAlchemy Sequelize
Message Queue Tests,Pub/sub work queues event streaming,RabbitMQ Kafka Redis
External Service Tests,Third-party APIs webhooks OAuth,responses nock WireMock

## Quick Start Guide

quickstart_steps[6]{step,action}:
1. Choose framework,Python/pytest or JavaScript/Jest based on your stack
2. Setup containers,Use docker-compose.test.yml for service dependencies
3. Configure tests,Copy pytest-config.py or jest-config.js to your project
4. Write first test,Start with simple API or database test
5. Add factories,Use factory pattern for test data generation
6. Run in CI,Add health checks and parallel execution

## Test Environment Setup Options

environment_options[3]{approach,pros,cons}:
Docker Compose,Easy setup multiple services,Requires Docker slower startup
Testcontainers,Programmatic control per-test isolation,Requires Docker programming overhead
In-memory DBs,Very fast no dependencies,Not production-like limited features

## Core Patterns

### 1. Transaction Rollback Pattern (Most Common)

**Python SQLAlchemy:**
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

**Benefits**: Fast, guaranteed isolation, simple cleanup.

### 2. Test Containers Pattern

**Start services on-demand:**
```python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres
```

**Benefits**: Real service instances, automatic cleanup, works everywhere.

### 3. Factory Pattern for Test Data

**Generate test data efficiently:**
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

**Benefits**: DRY, flexible, realistic data.

## API Testing Quick Reference

api_testing_checklist[8]{aspect,what_to_verify}:
Status codes,200 201 400 404 500 codes are correct
Response structure,JSON schema matches expected format
Authentication,Tokens validated 401 on missing/invalid auth
Request validation,400 errors for invalid inputs
Error messages,Clear actionable error messages
Pagination,Page size total count navigation links
Rate limiting,429 responses retry-after headers
CORS,Correct access-control headers

## Database Testing Quick Reference

database_testing_checklist[7]{aspect,what_to_verify}:
CRUD operations,Create Read Update Delete work correctly
Transactions,Commit rollback isolation work as expected
Constraints,Foreign keys unique constraints enforced
Cascade deletes,Related records deleted when parent removed
Connection pooling,Multiple connections handled correctly
Query performance,Queries complete within acceptable time
Migrations,Schema changes apply and rollback cleanly

## Mocking External Services

mocking_strategies[4]{strategy,when_to_use,tools}:
Response mocking,Fast CI tests known responses,responses (Python) nock (JS)
VCR recording,Real API responses replay in tests,VCR.py nock recorder
Contract testing,API version compatibility,Pact Postman Contract Testing
Service virtualization,Complex stateful interactions,WireMock MockServer

## Performance Optimization

performance_tips[8]{technique,impact}:
Session-scoped containers,10-50x faster startup
Transaction rollback,5-10x faster than truncate
tmpfs for databases,2-5x faster disk operations
Parallel execution,Nx faster (N = number of workers)
Connection pooling,Reduces connection overhead
Fixture scoping,Reuse expensive setup across tests
Selective test running,Run only affected tests
Mock heavy external calls,Avoid network latency

## Common Pitfalls and Solutions

common_pitfalls[8]{pitfall,solution}:
Tests share state,Use transaction rollback or clean DB per test
Flaky tests,Add proper waits ensure cleanup verify test isolation
Slow test suite,Use tmpfs parallel execution session fixtures
Port conflicts,Use dynamic ports or unique ports per service
Missing cleanup,Always use try/finally or fixture teardown
Over-mocking,Use real services where practical
Unclear failures,Add descriptive assertions log relevant state
CI failures,Ensure health checks proper timeouts adequate resources

## CI/CD Integration Checklist

ci_cd_checklist[6]{item,implementation}:
Service dependencies,Use GitHub Actions services or docker-compose
Health checks,Wait for services before running tests
Parallel execution,Use pytest-xdist or Jest maxWorkers
Test isolation,Ensure tests work independently
Caching,Cache Docker images and dependencies
Test reporting,Upload coverage and test results

## Testing Different Components

### API Integration Tests

```python
def test_user_creation(client):
    response = client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

### Database Integration Tests

```python
def test_user_crud(db_session):
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### Message Queue Tests

```python
def test_message_delivery(queue_service):
    queue_service.publish("test_queue", {"data": "test"})
    message = queue_service.consume("test_queue")
    assert message["data"] == "test"
```

### External Service Tests

```python
@responses.activate
def test_external_api():
    responses.add(responses.GET, 'https://api.example.com/users/1',
                  json={'name': 'Alice'}, status=200)
    result = external_service.get_user(1)
    assert result['name'] == 'Alice'
```

## Test Data Management

test_data_strategies[4]{strategy,use_case,tools}:
Factories,Generate objects on-demand,factory_boy faker.js
Fixtures,Pre-defined test data,YAML JSON files
Builders,Fluent test data creation,Custom builder classes
Object Mothers,Predefined common scenarios,Helper functions

## Language-Specific Quick Tips

### Python with pytest

```python
# Run specific tests
pytest tests/integration/test_api.py

# Run with markers
pytest -m "integration and not slow"

# Parallel execution
pytest -n auto

# With coverage
pytest --cov=app --cov-report=html
```

### JavaScript with Jest

```javascript
// Run specific tests
npm test -- tests/integration/api.test.js

// Run with pattern
npm test -- --testNamePattern="user creation"

// Parallel execution (default)
npm test -- --maxWorkers=4

// With coverage
npm test -- --coverage
```

## File Organization

integration_test_structure[5]{path,contents}:
tests/integration/,Main integration test directory
tests/conftest.py (pytest),Shared fixtures and configuration
tests/setup.js (Jest),Global setup and teardown
tests/factories/,Test data factories
tests/fixtures/,Static test data files

## Advanced Topics

For advanced patterns see:

advanced_topics[5]{topic,file}:
Contract Testing,reference/advanced-patterns.md
Performance Testing,reference/advanced-patterns.md
Distributed Systems,reference/advanced-patterns.md
Async Operations,reference/advanced-patterns.md
Event-Driven Testing,reference/advanced-patterns.md

## Practical Examples

Complete working examples available:

example_files[3]{language,file,coverage}:
Python/FastAPI,examples/python-fastapi.md,API DB auth Redis Celery factories
JavaScript/Express,examples/javascript-express.md,API DB auth Redis RabbitMQ factories
TypeScript,examples/javascript-express.md,Same as JS with type safety

## Configuration Templates

Ready-to-use templates:

template_files[3]{template,file,purpose}:
Pytest Configuration,templates/pytest-config.py,Complete pytest setup with fixtures
Jest Configuration,templates/jest-config.js,Complete Jest setup with helpers
Docker Compose,templates/docker-compose.test.yml,All test service dependencies

## Markers and Tags

Test organization with markers:

test_markers[7]{marker,purpose}:
@pytest.mark.integration,Mark as integration test
@pytest.mark.slow,Tests taking >5 seconds
@pytest.mark.database,Requires database
@pytest.mark.redis,Requires Redis
@pytest.mark.external_api,Calls external APIs
@pytest.mark.contract,Contract test
@pytest.mark.skip,Temporarily skip test

## Key Metrics

integration_test_metrics[5]{metric,target}:
Test execution time,< 2 seconds per test
Test suite time,< 5 minutes total
Code coverage,> 70% for integration paths
Flaky test rate,< 1% failure rate
CI build time,< 10 minutes including tests

## Troubleshooting Guide

troubleshooting[6]{problem,diagnosis,solution}:
Tests fail locally,Check Docker running ports available,Start services verify health
Tests fail in CI,Different environment resources,Match CI environment add health checks
Slow tests,Identify bottlenecks,Use profiling add parallel execution tmpfs
Flaky tests,Random failures timeouts,Add waits fix cleanup verify isolation
Memory issues,Container resource limits,Increase limits clean up properly
Port conflicts,Services use same ports,Use dynamic ports different ranges

## Best Practices Summary

best_practices_summary[10]{practice,why}:
Use real services,Catch integration issues early
Fast feedback,Run tests frequently during development
Test isolation,Prevent test interdependencies
Clean state,Ensure reproducible results
Meaningful assertions,Clear failure messages
Mock external only,Test real internal interactions
Parallel execution,Faster feedback cycles
Document setup,Help team run tests
Health checks,Ensure services ready
Continuous improvement,Refactor slow flaky tests

## See Also

- **[README.md](README.md)** - Overview and quick start
- **[examples/python-fastapi.md](examples/python-fastapi.md)** - Complete Python examples
- **[examples/javascript-express.md](examples/javascript-express.md)** - Complete JavaScript examples
- **[reference/advanced-patterns.md](reference/advanced-patterns.md)** - Advanced testing patterns
- **[templates/](templates/)** - Configuration templates

---

**Need more details?** Check the examples and reference directories for comprehensive code samples and advanced patterns.
