# Core Concepts - Test Runner Fundamentals

## Table of Contents

- [Test Types and Hierarchy](#test-types-and-hierarchy)
- [Test Lifecycle](#test-lifecycle)
- [Test Execution Models](#test-execution-models)
- [Coverage Metrics](#coverage-metrics)
- [Test Isolation](#test-isolation)
- [Test Doubles](#test-doubles)
- [Assertions](#assertions)
- [Test Organization](#test-organization)
- [Test Configuration](#test-configuration)
- [Quality Metrics](#quality-metrics)
- [Test Discovery](#test-discovery)
- [Test Filtering](#test-filtering)

## Test Types and Hierarchy

### What It Is

The testing pyramid represents different levels of testing, from fast unit tests at the base to slower end-to-end tests at the top. Each level serves a specific purpose and has different characteristics in terms of speed, isolation, and scope.

### Why It Matters

Understanding test types helps you design an effective testing strategy. Different test types catch different kinds of bugs, and a balanced mix provides comprehensive coverage while maintaining fast feedback loops. The pyramid guides resource allocation - more unit tests, fewer E2E tests.

### Test Type Hierarchy

#### 1. Unit Tests (Base - 70%)

**Purpose**: Test individual functions, methods, or classes in isolation

**Characteristics**:
- Extremely fast (milliseconds per test)
- Highly isolated (no external dependencies)
- Easy to write and maintain
- High volume (hundreds to thousands)

**Example**:
```javascript
// Jest unit test
describe('calculateTotal', () => {
  test('should sum array of numbers', () => {
    const numbers = [1, 2, 3, 4, 5];
    const result = calculateTotal(numbers);
    expect(result).toBe(15);
  });

  test('should return 0 for empty array', () => {
    const result = calculateTotal([]);
    expect(result).toBe(0);
  });

  test('should handle negative numbers', () => {
    const numbers = [10, -5, 3];
    const result = calculateTotal(numbers);
    expect(result).toBe(8);
  });
});
```

```python
# pytest unit test
import pytest
from calculator import calculate_total

def test_sum_array_of_numbers():
    numbers = [1, 2, 3, 4, 5]
    result = calculate_total(numbers)
    assert result == 15

def test_return_zero_for_empty_array():
    result = calculate_total([])
    assert result == 0

def test_handle_negative_numbers():
    numbers = [10, -5, 3]
    result = calculate_total(numbers)
    assert result == 8
```

#### 2. Integration Tests (Middle - 20%)

**Purpose**: Test interactions between multiple components or modules

**Characteristics**:
- Moderate speed (seconds per test)
- Partially isolated (may use test databases)
- More complex setup
- Medium volume (dozens to hundreds)

**Example**:
```javascript
// Integration test with database
describe('UserService integration', () => {
  let database;
  let userService;

  beforeEach(async () => {
    database = await createTestDatabase();
    userService = new UserService(database);
  });

  afterEach(async () => {
    await database.cleanup();
  });

  test('should create and retrieve user', async () => {
    // Create user
    const user = await userService.createUser({
      name: 'John Doe',
      email: 'john@example.com'
    });

    // Retrieve user
    const retrieved = await userService.getUserById(user.id);

    expect(retrieved.name).toBe('John Doe');
    expect(retrieved.email).toBe('john@example.com');
  });

  test('should update user email', async () => {
    const user = await userService.createUser({
      name: 'Jane Smith',
      email: 'jane@example.com'
    });

    await userService.updateEmail(user.id, 'jane.smith@example.com');

    const updated = await userService.getUserById(user.id);
    expect(updated.email).toBe('jane.smith@example.com');
  });
});
```

#### 3. End-to-End Tests (Top - 10%)

**Purpose**: Test complete user workflows through the entire application stack

**Characteristics**:
- Slow (seconds to minutes per test)
- No isolation (full application running)
- Complex setup and maintenance
- Low volume (dozens at most)

**Example**:
```javascript
// E2E test with Playwright
describe('User authentication flow', () => {
  test('should allow user to sign up and login', async () => {
    await page.goto('http://localhost:3000');

    // Sign up
    await page.click('text=Sign Up');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');

    // Verify redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome')).toBeVisible();

    // Logout
    await page.click('text=Logout');

    // Login again
    await page.click('text=Login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');

    // Verify successful login
    await expect(page).toHaveURL('/dashboard');
  });
});
```

### Common Patterns

**Balanced Pyramid**:
- 70% unit tests for fast feedback
- 20% integration tests for component interaction
- 10% E2E tests for critical user paths

**Anti-Pyramid (Ice Cream Cone)** ❌:
- Too many E2E tests
- Few unit tests
- Slow, brittle test suite

**Hourglass** ⚠️:
- Many unit and E2E tests
- Few integration tests
- Missing middle layer validation

### Common Mistakes

1. **Too Many E2E Tests**: Slow feedback, flaky tests, high maintenance
2. **No Integration Tests**: Miss component interaction bugs
3. **Testing Implementation Details**: Brittle tests that break on refactoring

## Test Lifecycle

### What It Is

The test lifecycle defines the stages a test goes through from setup to teardown. Understanding this lifecycle is crucial for writing reliable tests that properly manage resources and state.

### Lifecycle Stages

#### 1. Setup (Before)

Prepare test environment and dependencies before test execution.

**Levels**:
- **Suite Setup** (beforeAll/setUpClass): Runs once before all tests
- **Test Setup** (beforeEach/setUp): Runs before each test

```javascript
// Jest lifecycle
describe('UserService', () => {
  let database;
  let userService;

  // Suite setup - runs once
  beforeAll(async () => {
    database = await createTestDatabase();
  });

  // Test setup - runs before each test
  beforeEach(() => {
    userService = new UserService(database);
  });

  // Tests...

  afterEach(() => {
    userService = null;
  });

  afterAll(async () => {
    await database.close();
  });
});
```

```python
# pytest lifecycle
import pytest

@pytest.fixture(scope="module")
def database():
    """Suite setup - runs once per module"""
    db = create_test_database()
    yield db
    db.close()

@pytest.fixture
def user_service(database):
    """Test setup - runs before each test"""
    return UserService(database)

def test_create_user(user_service):
    user = user_service.create_user("John")
    assert user.name == "John"
```

#### 2. Execution

Run the actual test code with assertions.

```javascript
test('should validate email format', () => {
  // Arrange
  const validator = new EmailValidator();
  const validEmail = 'user@example.com';
  const invalidEmail = 'invalid-email';

  // Act
  const validResult = validator.isValid(validEmail);
  const invalidResult = validator.isValid(invalidEmail);

  // Assert
  expect(validResult).toBe(true);
  expect(invalidResult).toBe(false);
});
```

#### 3. Teardown (After)

Clean up resources and reset state after test execution.

```javascript
afterEach(async () => {
  // Clean up test data
  await database.clearTestData();

  // Reset mocks
  jest.clearAllMocks();

  // Close connections
  await closeTestConnections();
});
```

### Best Practices

1. **Isolate Each Test**: No shared state between tests
2. **Clean Up Resources**: Prevent memory leaks and port conflicts
3. **Fast Setup**: Keep setup/teardown lightweight
4. **Idempotent Tests**: Can run in any order

## Coverage Metrics

### What Coverage Measures

Coverage metrics quantify how much of your code is executed during test runs. Different coverage types measure different aspects of code execution.

### Coverage Types

#### 1. Line Coverage

**Definition**: Percentage of code lines executed during tests

**Example**:
```javascript
function calculateDiscount(price, isVIP) {
  let discount = 0;                    // ✓ Covered

  if (price > 100) {                   // ✓ Covered
    discount = 10;                     // ✓ Covered
  }

  if (isVIP) {                         // ✓ Covered
    discount += 5;                     // ✗ NOT Covered
  }

  return price - discount;             // ✓ Covered
}

// Test only covers non-VIP case
test('applies discount for orders over $100', () => {
  expect(calculateDiscount(150, false)).toBe(140);
});

// Line coverage: 6/7 = 85.7%
```

#### 2. Branch Coverage

**Definition**: Percentage of conditional branches executed

**Example**:
```javascript
function validateAge(age) {
  if (age < 0) {                       // Branch 1: True path ✗ NOT tested
    return 'Invalid';                  // Branch 1: False path ✓ tested
  }

  if (age < 18) {                      // Branch 2: True path ✓ tested
    return 'Minor';                    // Branch 2: False path ✓ tested
  }

  return 'Adult';
}

test('returns Adult for age 25', () => {
  expect(validateAge(25)).toBe('Adult');
});

test('returns Minor for age 15', () => {
  expect(validateAge(15)).toBe('Minor');
});

// Branch coverage: 3/4 = 75%
// Missing: negative age test
```

#### 3. Function Coverage

**Definition**: Percentage of functions called during tests

```javascript
class Calculator {
  add(a, b) {                          // ✓ Covered
    return a + b;
  }

  subtract(a, b) {                     // ✓ Covered
    return a - b;
  }

  multiply(a, b) {                     // ✗ NOT Covered
    return a * b;
  }

  divide(a, b) {                       // ✗ NOT Covered
    if (b === 0) throw new Error('Division by zero');
    return a / b;
  }
}

// Function coverage: 2/4 = 50%
```

#### 4. Statement Coverage

**Definition**: Percentage of statements executed

```javascript
function processOrder(order) {
  const total = order.items.reduce((sum, item) => sum + item.price, 0);  // Statement 1
  const tax = total * 0.1;                                                // Statement 2
  const shipping = total > 50 ? 0 : 5;                                   // Statement 3
  return total + tax + shipping;                                          // Statement 4
}

// All statements executed = 100% statement coverage
```

### Coverage Goals

**Recommended Thresholds**:
- Line Coverage: **≥80%**
- Branch Coverage: **≥75%**
- Function Coverage: **≥80%**
- Statement Coverage: **≥80%**

**Reality Check**:
- 100% coverage ≠ bug-free code
- Focus on critical paths first
- Some code may not need tests (getters/setters)

### Configuration Examples

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/critical/': {
      branches: 90,
      functions: 95,
      lines: 90,
      statements: 90
    }
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/tests/',
    '\\.config\\.js$'
  ]
};
```

```python
# pytest.ini
[pytest]
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --cov-branch

[coverage:run]
omit =
    */tests/*
    */migrations/*
    */__init__.py
```

## Test Isolation

### What It Is

Test isolation ensures that tests don't interfere with each other. Each test should be completely independent, capable of running in any order without affecting results.

### Why It Matters

Isolated tests are reliable and maintainable. Non-isolated tests create "test interdependencies" where one test's failure causes cascading failures, making debugging extremely difficult.

### Isolation Techniques

#### 1. Fresh Test Data

```javascript
// BAD: Shared mutable state
let testUser;

beforeAll(() => {
  testUser = { id: 1, name: 'John' };
});

test('modifies user name', () => {
  testUser.name = 'Jane';  // Mutates shared state
  expect(testUser.name).toBe('Jane');
});

test('checks original name', () => {
  expect(testUser.name).toBe('John');  // FAILS! Was modified
});

// GOOD: Fresh data per test
beforeEach(() => {
  testUser = { id: 1, name: 'John' };
});
```

#### 2. Database Isolation

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    """Create isolated database session per test"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.rollback()
    session.close()

def test_create_user(db_session):
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()

    assert db_session.query(User).count() == 1

def test_user_count_starts_at_zero(db_session):
    # Independent of previous test
    assert db_session.query(User).count() == 0
```

#### 3. Time Isolation

```javascript
// Freeze time for consistent testing
import { jest } from '@jest/globals';

describe('time-sensitive operations', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2024-01-01'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('creates timestamp', () => {
    const result = createTimestamp();
    expect(result).toBe('2024-01-01T00:00:00.000Z');
  });
});
```

### Common Isolation Violations

1. **Global State Pollution**: Modifying global variables
2. **File System Side Effects**: Creating files without cleanup
3. **Network Dependencies**: Real API calls
4. **Shared Database State**: Not cleaning up between tests

## Test Doubles

### What They Are

Test doubles are objects that simulate real dependencies in tests. They allow you to test code in isolation without relying on external systems.

### Types of Test Doubles

#### 1. Mocks

**Purpose**: Objects that verify interactions (calls, arguments)

```javascript
// Mock example - verify behavior
const emailService = {
  sendEmail: jest.fn()
};

function registerUser(userData, emailService) {
  const user = createUser(userData);
  emailService.sendEmail(user.email, 'Welcome!');
  return user;
}

test('sends welcome email on registration', () => {
  const userData = { email: 'user@example.com' };

  registerUser(userData, emailService);

  // Verify interaction
  expect(emailService.sendEmail).toHaveBeenCalledWith(
    'user@example.com',
    'Welcome!'
  );
  expect(emailService.sendEmail).toHaveBeenCalledTimes(1);
});
```

#### 2. Stubs

**Purpose**: Provide predefined responses to calls

```python
from unittest.mock import Mock

def test_process_payment():
    # Stub payment gateway
    payment_gateway = Mock()
    payment_gateway.charge.return_value = {
        'success': True,
        'transaction_id': '12345'
    }

    processor = PaymentProcessor(payment_gateway)
    result = processor.process(100.00)

    assert result['success'] is True
    assert result['transaction_id'] == '12345'
```

#### 3. Spies

**Purpose**: Record information about calls while maintaining real behavior

```javascript
const calculator = {
  add: (a, b) => a + b
};

test('tracks calculations', () => {
  const spy = jest.spyOn(calculator, 'add');

  const result = calculator.add(2, 3);

  expect(result).toBe(5);  // Real behavior
  expect(spy).toHaveBeenCalledWith(2, 3);  // Tracked

  spy.mockRestore();
});
```

#### 4. Fakes

**Purpose**: Simplified implementations for testing

```javascript
class FakeDatabase {
  constructor() {
    this.data = new Map();
  }

  async save(id, value) {
    this.data.set(id, value);
  }

  async find(id) {
    return this.data.get(id);
  }

  async clear() {
    this.data.clear();
  }
}

test('uses fake database', async () => {
  const db = new FakeDatabase();
  const service = new UserService(db);

  await service.createUser({ id: 1, name: 'Alice' });
  const user = await service.getUser(1);

  expect(user.name).toBe('Alice');
});
```

### When to Use Each

- **Mocks**: When you need to verify interactions
- **Stubs**: When you need specific return values
- **Spies**: When you want to verify calls but keep real behavior
- **Fakes**: When you need a working implementation without external dependencies

## Assertions

### What They Are

Assertions are statements that verify expected outcomes. They form the core of test validation.

### Common Assertion Patterns

#### Equality Assertions

```javascript
// Primitive equality
expect(result).toBe(42);
expect(name).toBe('John');

// Object equality
expect(user).toEqual({ id: 1, name: 'John' });

// Array equality
expect(numbers).toEqual([1, 2, 3]);
```

#### Truthiness Assertions

```javascript
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();
```

#### Comparison Assertions

```javascript
expect(age).toBeGreaterThan(18);
expect(score).toBeGreaterThanOrEqual(100);
expect(price).toBeLessThan(1000);
expect(discount).toBeLessThanOrEqual(50);
```

#### String Assertions

```javascript
expect(email).toContain('@');
expect(url).toMatch(/^https:\/\//);
expect(message).toHaveLength(100);
```

#### Array/Collection Assertions

```javascript
expect(users).toHaveLength(3);
expect(tags).toContain('javascript');
expect(numbers).toContainEqual(42);
```

#### Exception Assertions

```javascript
expect(() => {
  divide(10, 0);
}).toThrow('Division by zero');

expect(async () => {
  await fetchData();
}).rejects.toThrow();
```

### Assertion Best Practices

1. **One Assertion Per Test** (when possible): Focused, clear failures
2. **Use Specific Assertions**: `toBeNull()` vs `toBe(null)`
3. **Descriptive Messages**: Custom failure messages for clarity
4. **Avoid Logic in Assertions**: Keep assertions simple

```javascript
// GOOD: Specific assertion
expect(user.email).toBe('test@example.com');

// BAD: Logic in assertion
expect(user.email.includes('@') && user.email.includes('.')).toBe(true);
```

## Related Concepts

- **Test Organization**: See [Test Organization](#test-organization)
- **Quality Metrics**: See [Quality Metrics](#quality-metrics)
- **Test Configuration**: See [Test Configuration](#test-configuration)
- **Best Practices**: See [docs/best-practices.md](best-practices.md)
- **Patterns**: See [docs/patterns.md](patterns.md)
