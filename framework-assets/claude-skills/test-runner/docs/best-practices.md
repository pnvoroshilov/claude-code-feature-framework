# Best Practices - Test Runner Excellence

## Table of Contents

- [Test Organization](#test-organization)
- [Naming Conventions](#naming-conventions)
- [Test Structure](#test-structure)
- [Mock and Stub Strategies](#mock-and-stub-strategies)
- [Performance Optimization](#performance-optimization)
- [Test Maintenance](#test-maintenance)
- [Code Coverage Strategy](#code-coverage-strategy)
- [Error Handling in Tests](#error-handling-in-tests)
- [Test Data Management](#test-data-management)
- [Continuous Testing](#continuous-testing)

## Test Organization

### Principle

Organize tests to mirror your source code structure, making tests easy to find and maintain. A well-organized test suite is essential for long-term project health.

### Why It Matters

Poor test organization leads to:
- Difficulty finding relevant tests
- Duplicate test logic
- Slow test discovery
- Maintenance nightmares
- Team confusion

### How to Apply

#### Directory Structure Pattern

```
src/
├── components/
│   ├── Button.tsx
│   ├── Header.tsx
│   └── UserProfile.tsx
└── services/
    ├── AuthService.ts
    ├── UserService.ts
    └── PaymentService.ts

tests/
├── unit/
│   ├── components/
│   │   ├── Button.test.tsx
│   │   ├── Header.test.tsx
│   │   └── UserProfile.test.tsx
│   └── services/
│       ├── AuthService.test.ts
│       ├── UserService.test.ts
│       └── PaymentService.test.ts
├── integration/
│   ├── api/
│   │   ├── auth.test.ts
│   │   └── users.test.ts
│   └── database/
│       └── migrations.test.ts
└── e2e/
    ├── authentication.test.ts
    ├── checkout.test.ts
    └── user-profile.test.ts
```

#### Co-located Tests

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx
│   │   ├── Button.styles.ts
│   │   └── index.ts
│   └── Header/
│       ├── Header.tsx
│       ├── Header.test.tsx
│       └── index.ts
```

### Good Example

```javascript
// tests/unit/services/UserService.test.ts
import { UserService } from '@/services/UserService';
import { createMockDatabase } from '@/tests/helpers/database';

describe('UserService', () => {
  describe('createUser', () => {
    test('should create user with valid data', () => {
      // Test implementation
    });

    test('should throw error for duplicate email', () => {
      // Test implementation
    });
  });

  describe('updateUser', () => {
    test('should update user profile', () => {
      // Test implementation
    });
  });
});
```

### Bad Example

```javascript
// tests/random-tests.test.ts ❌
test('test1', () => { /* ... */ });
test('test2', () => { /* ... */ });
test('user stuff', () => { /* ... */ });
test('button click', () => { /* ... */ });
```

### Exceptions

Small projects (<10 files) may use flat structure, but plan for growth.

### Related Practices

- [Naming Conventions](#naming-conventions)
- [Test Structure](#test-structure)

## Naming Conventions

### Principle

Use clear, descriptive names that explain what is being tested and what the expected outcome is. Test names should read like specifications.

### Why It Matters

Good naming provides:
- Self-documenting tests
- Clear failure messages
- Better test discovery
- Easier maintenance

### Naming Patterns

#### Test File Names

```
✅ Good:
- UserService.test.ts
- Button.test.tsx
- authentication.spec.ts
- user-profile.e2e.ts

❌ Bad:
- test1.ts
- mytest.js
- stuff.test.ts
```

#### Test Suite Names

```javascript
// ✅ Good: Noun (what you're testing)
describe('UserService', () => {});
describe('Authentication API', () => {});
describe('Button component', () => {});

// ❌ Bad: Vague or incorrect
describe('Tests', () => {});
describe('Service stuff', () => {});
```

#### Test Names

**Pattern**: "should [expected behavior] when [condition]"

```javascript
// ✅ Excellent: Clear, specific, reads like specification
describe('UserService', () => {
  describe('createUser', () => {
    test('should create user when data is valid', () => {});
    test('should throw ValidationError when email is invalid', () => {});
    test('should hash password when user is created', () => {});
    test('should send welcome email when user is created', () => {});
  });

  describe('deleteUser', () => {
    test('should delete user when user exists', () => {});
    test('should throw NotFoundError when user does not exist', () => {});
    test('should delete related data when user is deleted', () => {});
  });
});

// ✅ Alternative: BDD style
describe('UserService', () => {
  it('creates a user with valid data', () => {});
  it('rejects invalid email addresses', () => {});
  it('hashes passwords before storage', () => {});
});

// ❌ Bad: Vague, unclear expectations
test('user test', () => {});
test('it works', () => {});
test('test case 1', () => {});
```

### Python Naming

```python
# ✅ Good: Clear, descriptive
class TestUserService:
    def test_create_user_with_valid_data(self):
        pass

    def test_create_user_raises_error_with_duplicate_email(self):
        pass

    def test_update_user_profile_updates_database(self):
        pass

# ❌ Bad: Unclear
class TestUser:
    def test1(self):
        pass

    def test_stuff(self):
        pass
```

### Nested Describe Blocks

```javascript
describe('ShoppingCart', () => {
  describe('addItem', () => {
    describe('when item is in stock', () => {
      test('should add item to cart', () => {});
      test('should increment cart item count', () => {});
    });

    describe('when item is out of stock', () => {
      test('should throw OutOfStockError', () => {});
    });

    describe('when cart is full', () => {
      test('should throw CartFullError', () => {});
    });
  });
});
```

## Test Structure

### Principle: AAA Pattern

Every test should follow the Arrange-Act-Assert (AAA) pattern for clarity and consistency.

### AAA Pattern Explained

```javascript
test('should calculate total price with tax', () => {
  // ===== ARRANGE =====
  // Set up test data and dependencies
  const cart = new ShoppingCart();
  const item1 = { id: 1, price: 10.00 };
  const item2 = { id: 2, price: 15.00 };
  const taxRate = 0.1;

  cart.addItem(item1);
  cart.addItem(item2);

  // ===== ACT =====
  // Execute the behavior being tested
  const total = cart.calculateTotal(taxRate);

  // ===== ASSERT =====
  // Verify the expected outcome
  expect(total).toBe(27.50); // (10 + 15) * 1.1
});
```

### Detailed AAA Examples

#### Arrange Phase

```javascript
// Setup: Create objects, configure mocks, prepare data
const mockDatabase = createMockDatabase();
const userService = new UserService(mockDatabase);
const testUser = {
  email: 'test@example.com',
  password: 'SecurePass123',
  name: 'Test User'
};

mockDatabase.findByEmail.mockResolvedValue(null); // No existing user
```

#### Act Phase

```javascript
// Execute: Call the method/function being tested
const result = await userService.createUser(testUser);
```

#### Assert Phase

```javascript
// Verify: Check the results and side effects
expect(result).toBeDefined();
expect(result.email).toBe('test@example.com');
expect(result.name).toBe('Test User');
expect(mockDatabase.save).toHaveBeenCalledWith(
  expect.objectContaining({
    email: 'test@example.com',
    name: 'Test User'
  })
);
```

### Complete Example

```javascript
describe('PaymentProcessor', () => {
  test('should process payment successfully', async () => {
    // ARRANGE
    const mockGateway = {
      charge: jest.fn().mockResolvedValue({
        success: true,
        transactionId: 'txn_123'
      })
    };

    const processor = new PaymentProcessor(mockGateway);

    const paymentDetails = {
      amount: 100.00,
      currency: 'USD',
      cardToken: 'tok_visa'
    };

    // ACT
    const result = await processor.processPayment(paymentDetails);

    // ASSERT
    expect(result.success).toBe(true);
    expect(result.transactionId).toBe('txn_123');
    expect(mockGateway.charge).toHaveBeenCalledWith(
      100.00,
      'USD',
      'tok_visa'
    );
  });

  test('should handle payment failure gracefully', async () => {
    // ARRANGE
    const mockGateway = {
      charge: jest.fn().mockRejectedValue(
        new Error('Insufficient funds')
      )
    };

    const processor = new PaymentProcessor(mockGateway);

    const paymentDetails = {
      amount: 100.00,
      currency: 'USD',
      cardToken: 'tok_visa'
    };

    // ACT
    const result = await processor.processPayment(paymentDetails);

    // ASSERT
    expect(result.success).toBe(false);
    expect(result.error).toBe('Insufficient funds');
  });
});
```

### Python AAA Pattern

```python
def test_user_registration():
    # ARRANGE
    user_repository = MockUserRepository()
    email_service = MockEmailService()
    registration_service = RegistrationService(
        user_repository,
        email_service
    )

    user_data = {
        'email': 'test@example.com',
        'password': 'SecurePass123',
        'name': 'Test User'
    }

    # ACT
    result = registration_service.register_user(user_data)

    # ASSERT
    assert result.success is True
    assert user_repository.save_called is True
    assert email_service.welcome_email_sent is True
```

### One Assertion Per Test (When Possible)

```javascript
// ✅ Good: Focused tests
test('should return user ID', () => {
  const user = createUser({ name: 'John' });
  expect(user.id).toBeDefined();
});

test('should generate unique IDs', () => {
  const user1 = createUser({ name: 'John' });
  const user2 = createUser({ name: 'Jane' });
  expect(user1.id).not.toBe(user2.id);
});

// ⚠️ Acceptable: Related assertions
test('should create user with correct properties', () => {
  const userData = { name: 'John', email: 'john@example.com' };
  const user = createUser(userData);

  expect(user.name).toBe('John');
  expect(user.email).toBe('john@example.com');
  expect(user.createdAt).toBeInstanceOf(Date);
});

// ❌ Bad: Testing multiple behaviors
test('user functionality', () => {
  const user = createUser({ name: 'John' });
  expect(user.id).toBeDefined();

  user.updateEmail('new@example.com');
  expect(user.email).toBe('new@example.com');

  user.delete();
  expect(user.isDeleted).toBe(true);
});
```

## Mock and Stub Strategies

### Principle

Mock external dependencies to isolate the code under test. Use mocks strategically - don't mock everything.

### When to Mock

✅ **Always Mock**:
- External APIs and services
- Database connections
- File system operations
- Network requests
- Time-dependent operations
- Random number generation

❌ **Don't Mock**:
- Simple data structures
- Pure functions
- Code under test
- Standard library (usually)

### Mocking Strategies

#### Strategy 1: Manual Mocks

```javascript
// Create explicit mock objects
const mockEmailService = {
  sendEmail: jest.fn(),
  sendBulkEmail: jest.fn(),
  validateEmail: jest.fn()
};

test('sends welcome email', () => {
  const service = new UserService(mockEmailService);

  service.registerUser({ email: 'test@example.com' });

  expect(mockEmailService.sendEmail).toHaveBeenCalledWith(
    'test@example.com',
    'Welcome!'
  );
});
```

#### Strategy 2: Module Mocks

```javascript
// Mock entire module
jest.mock('axios');

import axios from 'axios';
import { fetchUserData } from './api';

test('fetches user data from API', async () => {
  axios.get.mockResolvedValue({
    data: { id: 1, name: 'John' }
  });

  const user = await fetchUserData(1);

  expect(user.name).toBe('John');
  expect(axios.get).toHaveBeenCalledWith('/users/1');
});
```

#### Strategy 3: Dependency Injection

```javascript
// Design for testability
class UserService {
  constructor(database, emailService, logger) {
    this.database = database;
    this.emailService = emailService;
    this.logger = logger;
  }

  async createUser(userData) {
    const user = await this.database.save(userData);
    await this.emailService.sendWelcomeEmail(user.email);
    this.logger.info(`User created: ${user.id}`);
    return user;
  }
}

// Easy to test with injected mocks
test('creates user with all side effects', async () => {
  const mockDB = { save: jest.fn().mockResolvedValue({ id: 1 }) };
  const mockEmail = { sendWelcomeEmail: jest.fn() };
  const mockLogger = { info: jest.fn() };

  const service = new UserService(mockDB, mockEmail, mockLogger);

  await service.createUser({ name: 'John' });

  expect(mockDB.save).toHaveBeenCalled();
  expect(mockEmail.sendWelcomeEmail).toHaveBeenCalled();
  expect(mockLogger.info).toHaveBeenCalled();
});
```

### Python Mocking

```python
from unittest.mock import Mock, patch, MagicMock

# Strategy 1: Manual mocks
def test_user_creation():
    mock_database = Mock()
    mock_database.save.return_value = User(id=1, name='John')

    service = UserService(mock_database)
    user = service.create_user({'name': 'John'})

    assert user.id == 1
    mock_database.save.assert_called_once()

# Strategy 2: Patch decorator
@patch('myapp.services.EmailService')
def test_sends_email(mock_email_service):
    service = UserService()
    service.register_user({'email': 'test@example.com'})

    mock_email_service.send.assert_called_with('test@example.com')

# Strategy 3: Context manager
def test_api_call():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'id': 1}

        result = fetch_user_data(1)

        assert result['id'] == 1
        mock_get.assert_called_with('https://api.example.com/users/1')
```

### Mock Best Practices

1. **Reset Mocks Between Tests**:
```javascript
afterEach(() => {
  jest.clearAllMocks();
});
```

2. **Verify Mock Calls**:
```javascript
expect(mockFunction).toHaveBeenCalledTimes(1);
expect(mockFunction).toHaveBeenCalledWith(expectedArg);
expect(mockFunction).not.toHaveBeenCalled();
```

3. **Use Specific Mocks**:
```javascript
// ✅ Good: Specific mock for the test
mockAPI.fetchUser.mockResolvedValue({ id: 1, name: 'John' });

// ❌ Bad: Overly generic mock
mockAPI.mockResolvedValue({});
```

## Performance Optimization

### Principle

Keep tests fast to maintain rapid feedback loops. Slow tests discourage running the full suite.

### Why It Matters

**Speed Goals**:
- Unit tests: <10ms per test
- Integration tests: <1s per test
- E2E tests: <30s per test
- Full suite: <5 minutes

### Optimization Strategies

#### Strategy 1: Parallel Execution

```bash
# Jest parallel execution
jest --maxWorkers=4

# pytest parallel
pytest -n 4

# Go parallel
go test -p 4 ./...
```

```javascript
// jest.config.js
module.exports = {
  maxWorkers: '50%', // Use half of CPU cores
  testTimeout: 10000
};
```

#### Strategy 2: Selective Test Running

```bash
# Run only changed tests
jest --onlyChanged

# Run related tests
jest --findRelatedTests src/UserService.ts

# Run specific pattern
pytest -k "user_authentication"
```

#### Strategy 3: Test Sharding

```yaml
# GitHub Actions - split tests across jobs
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: jest --shard=${{ matrix.shard }}/4
```

#### Strategy 4: Smart Setup/Teardown

```javascript
// ✅ Good: Suite-level setup for expensive operations
describe('Database tests', () => {
  let database;

  beforeAll(async () => {
    // Expensive: Run once per suite
    database = await createTestDatabase();
  });

  afterAll(async () => {
    await database.close();
  });

  // Fast test-level setup
  beforeEach(async () => {
    await database.clearData();
  });

  test('test 1', async () => { /* ... */ });
  test('test 2', async () => { /* ... */ });
});

// ❌ Bad: Expensive setup per test
describe('Database tests', () => {
  let database;

  beforeEach(async () => {
    // Expensive: Run before EVERY test
    database = await createTestDatabase();
  });

  afterEach(async () => {
    await database.close();
  });
});
```

#### Strategy 5: In-Memory Alternatives

```javascript
// ✅ Fast: In-memory database
import { createDatabase } from 'sqlite3-memory';

// ❌ Slow: Real database
import { createConnection } from 'postgresql';

// ✅ Fast: Mock API
const mockAPI = { fetchData: jest.fn() };

// ❌ Slow: Real API call
await axios.get('https://api.example.com');
```

### Performance Anti-Patterns

❌ **Sleep/Wait Statements**:
```javascript
// BAD
await new Promise(resolve => setTimeout(resolve, 1000));

// GOOD: Use fake timers
jest.useFakeTimers();
jest.advanceTimersByTime(1000);
```

❌ **Real Network Calls**:
```javascript
// BAD
const response = await fetch('https://api.example.com');

// GOOD: Mock network
jest.mock('node-fetch');
fetch.mockResolvedValue({ json: () => mockData });
```

❌ **File System Operations**:
```javascript
// BAD
fs.writeFileSync('test-file.txt', data);

// GOOD: Use in-memory file system
import { vol } from 'memfs';
jest.mock('fs', () => require('memfs'));
```

## Code Coverage Strategy

### Principle

Aim for high coverage of critical code paths, but don't obsess over 100% coverage. Focus on meaningful tests, not just coverage numbers.

### Coverage Goals by Code Type

```javascript
// Critical business logic: 95%+ coverage
function processPayment(amount, card) {
  if (amount <= 0) throw new Error('Invalid amount');
  if (!isValidCard(card)) throw new Error('Invalid card');

  const fee = calculateFee(amount);
  const total = amount + fee;

  return chargeCard(card, total);
}

// Utility functions: 80%+ coverage
function formatCurrency(amount) {
  return `$${amount.toFixed(2)}`;
}

// Simple getters/setters: Low priority
class User {
  getName() { return this.name; }
  setName(name) { this.name = name; }
}
```

### Coverage Configuration

```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{js,ts}',
    '!src/**/index.{js,ts}'
  ],
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/services/payment/': {
      // Higher threshold for critical code
      branches: 90,
      functions: 95,
      lines: 90,
      statements: 90
    },
    './src/utils/': {
      // Lower threshold for utilities
      branches: 60,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
};
```

### Coverage Improvement Workflow

1. **Generate Coverage Report**:
```bash
npm test -- --coverage
```

2. **Identify Gaps**:
```bash
# Open HTML report
open coverage/lcov-report/index.html
```

3. **Prioritize**:
- Critical business logic first
- High-complexity code second
- Simple code last

4. **Add Tests**:
```javascript
// Uncovered branch found
function validateUser(user) {
  if (!user.email) return false;
  if (!user.name) return false;  // ← Uncovered
  return true;
}

// Add test for uncovered branch
test('returns false when name is missing', () => {
  const user = { email: 'test@example.com' };
  expect(validateUser(user)).toBe(false);
});
```

### Coverage Exclusions

```javascript
// Exclude from coverage
/* istanbul ignore next */
function debugHelper() {
  console.log('Debug info');
}

// Exclude entire file
/* istanbul ignore file */
```

```python
# pytest coverage exclusions
# .coveragerc
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Related Best Practices

- **Continuous Testing**: See [Continuous Testing](#continuous-testing)
- **Test Maintenance**: See [Test Maintenance](#test-maintenance)
- **Patterns**: See [docs/patterns.md](patterns.md)
- **Troubleshooting**: See [docs/troubleshooting.md](troubleshooting.md)
