# Test Patterns - Proven Testing Strategies

## Table of Contents

- [Test Organization Patterns](#test-organization-patterns)
- [Setup and Teardown Patterns](#setup-and-teardown-patterns)
- [Data-Driven Testing](#data-driven-testing)
- [Snapshot Testing](#snapshot-testing)
- [Property-Based Testing](#property-based-testing)
- [Test Factory Pattern](#test-factory-pattern)
- [Page Object Pattern](#page-object-pattern)
- [Builder Pattern for Test Data](#builder-pattern-for-test-data)
- [Shared Test Utilities](#shared-test-utilities)
- [Parameterized Tests](#parameterized-tests)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

## Test Organization Patterns

### Pattern: Feature-Based Organization

**When to Use**: Organizing tests by feature/domain rather than technical layers

**Benefits**:
- Tests grouped by business functionality
- Easy to find related tests
- Better for domain-driven design

**Implementation**:

```
tests/
├── authentication/
│   ├── login.test.ts
│   ├── logout.test.ts
│   ├── password-reset.test.ts
│   └── two-factor-auth.test.ts
├── user-management/
│   ├── user-registration.test.ts
│   ├── user-profile.test.ts
│   └── user-deletion.test.ts
└── payment/
    ├── checkout.test.ts
    ├── refunds.test.ts
    └── subscription.test.ts
```

### Pattern: Layer-Based Organization

**When to Use**: Organizing tests by technical architecture layers

**Benefits**:
- Clear separation of test types
- Easy to run specific layers
- Matches application architecture

**Implementation**:

```
tests/
├── unit/
│   ├── models/
│   ├── services/
│   └── utilities/
├── integration/
│   ├── api/
│   ├── database/
│   └── external-services/
└── e2e/
    ├── critical-paths/
    └── user-journeys/
```

### Pattern: Co-Located Tests

**When to Use**: Tests next to source code

**Benefits**:
- Tests always in sync with code
- Easy to find related tests
- Component-oriented

**Implementation**:

```javascript
// src/components/Button/Button.test.tsx
import { render, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  test('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    const { getByText } = render(
      <Button onClick={handleClick}>Click me</Button>
    );

    fireEvent.click(getByText('Click me'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('renders with correct text', () => {
    const { getByText } = render(<Button>Submit</Button>);
    expect(getByText('Submit')).toBeInTheDocument();
  });

  test('applies custom className', () => {
    const { container } = render(
      <Button className="custom-btn">Click</Button>
    );
    expect(container.firstChild).toHaveClass('custom-btn');
  });
});
```

## Setup and Teardown Patterns

### Pattern: Suite-Level Fixtures

**When to Use**: Expensive setup shared across all tests in a suite

**Example**:

```javascript
describe('Database integration tests', () => {
  let database;
  let connection;

  // Run once before all tests
  beforeAll(async () => {
    database = await DatabaseServer.start();
    connection = await database.connect();
    await connection.runMigrations();
  });

  // Run before each test
  beforeEach(async () => {
    await connection.clearAllTables();
    await connection.seedTestData();
  });

  // Run after each test
  afterEach(async () => {
    await connection.rollback();
  });

  // Run once after all tests
  afterAll(async () => {
    await connection.close();
    await database.stop();
  });

  test('creates user record', async () => {
    const user = await connection.createUser({ name: 'John' });
    expect(user.id).toBeDefined();
  });

  test('finds user by email', async () => {
    await connection.createUser({ email: 'test@example.com' });
    const user = await connection.findUserByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});
```

### Pattern: Factory Functions

**When to Use**: Creating test data with sensible defaults

**Example**:

```javascript
// test-helpers/factories.js
export function createTestUser(overrides = {}) {
  return {
    id: Math.random().toString(36),
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date(),
    isActive: true,
    ...overrides
  };
}

export function createTestOrder(overrides = {}) {
  return {
    id: Math.random().toString(36),
    userId: createTestUser().id,
    total: 100.00,
    status: 'pending',
    items: [],
    createdAt: new Date(),
    ...overrides
  };
}

// Usage in tests
test('processes order', () => {
  const order = createTestOrder({
    total: 250.00,
    status: 'confirmed'
  });

  const result = processOrder(order);

  expect(result.success).toBe(true);
});
```

### Pattern: Fixture Files

**When to Use**: Large, complex test data that's reused

**Example**:

```javascript
// tests/fixtures/users.json
{
  "validUser": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  },
  "adminUser": {
    "name": "Admin User",
    "email": "admin@example.com",
    "role": "admin",
    "permissions": ["read", "write", "delete"]
  },
  "inactiveUser": {
    "name": "Inactive User",
    "email": "inactive@example.com",
    "isActive": false
  }
}

// tests/userService.test.js
import userFixtures from './fixtures/users.json';

test('creates user from fixture', () => {
  const user = createUser(userFixtures.validUser);
  expect(user.name).toBe('John Doe');
});
```

## Data-Driven Testing

### Pattern: Parameterized Test Cases

**When to Use**: Testing same logic with different inputs

**JavaScript (Jest)**:

```javascript
describe('validateEmail', () => {
  test.each([
    ['user@example.com', true],
    ['test.user@company.co.uk', true],
    ['user+tag@example.com', true],
    ['invalid', false],
    ['@example.com', false],
    ['user@', false],
    ['user @example.com', false]
  ])('validateEmail(%s) returns %s', (email, expected) => {
    expect(validateEmail(email)).toBe(expected);
  });
});

// Or with objects for clarity
describe('calculateDiscount', () => {
  test.each([
    { price: 100, discount: 10, expected: 90 },
    { price: 50, discount: 20, expected: 40 },
    { price: 200, discount: 0, expected: 200 },
    { price: 75, discount: 100, expected: 0 }
  ])('price $price with $discount% discount = $expected',
    ({ price, discount, expected }) => {
      expect(calculateDiscount(price, discount)).toBe(expected);
    }
  );
});
```

**Python (pytest)**:

```python
import pytest

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("test.user@company.co.uk", True),
    ("user+tag@example.com", True),
    ("invalid", False),
    ("@example.com", False),
    ("user@", False),
    ("user @example.com", False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected

@pytest.mark.parametrize("price,discount,expected", [
    (100, 10, 90),
    (50, 20, 40),
    (200, 0, 200),
    (75, 100, 0),
])
def test_calculate_discount(price, discount, expected):
    assert calculate_discount(price, discount) == expected
```

### Pattern: Table-Driven Tests

**When to Use**: Complex test cases with multiple parameters

```javascript
const testCases = [
  {
    name: 'valid credit card',
    input: { cardNumber: '4532015112830366', cvv: '123' },
    expected: { valid: true, type: 'visa' }
  },
  {
    name: 'invalid card number',
    input: { cardNumber: '1234567890123456', cvv: '123' },
    expected: { valid: false, error: 'Invalid card number' }
  },
  {
    name: 'missing CVV',
    input: { cardNumber: '4532015112830366' },
    expected: { valid: false, error: 'CVV required' }
  }
];

describe('validatePaymentCard', () => {
  testCases.forEach(({ name, input, expected }) => {
    test(name, () => {
      const result = validatePaymentCard(input);
      expect(result).toEqual(expected);
    });
  });
});
```

## Snapshot Testing

### Pattern: Component Snapshots

**When to Use**: Testing React/Vue components for unexpected changes

**Example**:

```javascript
import { render } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile component', () => {
  test('renders correctly', () => {
    const user = {
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://example.com/avatar.jpg'
    };

    const { container } = render(<UserProfile user={user} />);

    expect(container.firstChild).toMatchSnapshot();
  });

  test('renders loading state', () => {
    const { container } = render(<UserProfile loading={true} />);
    expect(container.firstChild).toMatchSnapshot();
  });

  test('renders error state', () => {
    const { container } = render(
      <UserProfile error="Failed to load user" />
    );
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

### Pattern: Inline Snapshots

**When to Use**: Small, readable snapshots

```javascript
test('formats user data', () => {
  const user = { name: 'John', age: 30 };
  const formatted = formatUserData(user);

  expect(formatted).toMatchInlineSnapshot(`
    Object {
      "age": 30,
      "displayName": "John",
      "isAdult": true,
    }
  `);
});
```

### Snapshot Best Practices

```javascript
// ✅ Good: Small, focused snapshots
test('renders button text', () => {
  const { getByRole } = render(<Button>Click me</Button>);
  expect(getByRole('button')).toMatchSnapshot();
});

// ❌ Bad: Large snapshots with dynamic data
test('renders entire page', () => {
  const { container } = render(<ComplexPage />);
  expect(container).toMatchSnapshot(); // Changes frequently
});

// ✅ Good: Serialize custom data
test('formats API response', () => {
  const response = {
    users: [/* ... */],
    timestamp: Date.now() // Dynamic value
  };

  expect(response).toMatchSnapshot({
    timestamp: expect.any(Number) // Match type, not value
  });
});
```

## Property-Based Testing

### Pattern: Generative Testing

**When to Use**: Testing properties that should hold for any input

**JavaScript (fast-check)**:

```javascript
import * as fc from 'fast-check';

describe('Array utilities', () => {
  test('reverse twice returns original array', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        const reversed = reverse(reverse(arr));
        expect(reversed).toEqual(arr);
      })
    );
  });

  test('sort is idempotent', () => {
    fc.assert(
      fc.property(fc.array(fc.integer()), (arr) => {
        const sorted1 = sort(arr);
        const sorted2 = sort(sorted1);
        expect(sorted1).toEqual(sorted2);
      })
    );
  });

  test('map preserves length', () => {
    fc.assert(
      fc.property(
        fc.array(fc.integer()),
        fc.func(fc.integer()),
        (arr, fn) => {
          const mapped = arr.map(fn);
          expect(mapped.length).toBe(arr.length);
        }
      )
    );
  });
});
```

**Python (hypothesis)**:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_reverse_twice_returns_original(arr):
    assert reverse(reverse(arr)) == arr

@given(st.lists(st.integers()))
def test_sort_is_idempotent(arr):
    sorted1 = sort(arr)
    sorted2 = sort(sorted1)
    assert sorted1 == sorted2

@given(st.lists(st.integers()), st.functions())
def test_map_preserves_length(arr, fn):
    mapped = [fn(x) for x in arr]
    assert len(mapped) == len(arr)
```

## Test Factory Pattern

### Pattern: Builder Pattern for Complex Objects

**When to Use**: Creating test objects with many optional fields

```javascript
class UserBuilder {
  constructor() {
    this.user = {
      id: this.generateId(),
      name: 'Test User',
      email: 'test@example.com',
      age: 25,
      isActive: true,
      role: 'user',
      createdAt: new Date()
    };
  }

  generateId() {
    return Math.random().toString(36).substr(2, 9);
  }

  withName(name) {
    this.user.name = name;
    return this;
  }

  withEmail(email) {
    this.user.email = email;
    return this;
  }

  withRole(role) {
    this.user.role = role;
    return this;
  }

  inactive() {
    this.user.isActive = false;
    return this;
  }

  admin() {
    this.user.role = 'admin';
    return this;
  }

  build() {
    return { ...this.user };
  }
}

// Usage
test('admin users can delete posts', () => {
  const admin = new UserBuilder()
    .withName('Admin User')
    .admin()
    .build();

  expect(canDeletePost(admin)).toBe(true);
});

test('inactive users cannot login', () => {
  const user = new UserBuilder()
    .inactive()
    .build();

  expect(canLogin(user)).toBe(false);
});
```

## Page Object Pattern

### Pattern: Page Objects for E2E Tests

**When to Use**: Abstracting UI interactions in end-to-end tests

**Implementation**:

```javascript
// page-objects/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async navigate() {
    await this.page.goto('/login');
  }

  async fillEmail(email) {
    await this.page.fill('input[name="email"]', email);
  }

  async fillPassword(password) {
    await this.page.fill('input[name="password"]', password);
  }

  async clickSubmit() {
    await this.page.click('button[type="submit"]');
  }

  async login(email, password) {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickSubmit();
  }

  async getErrorMessage() {
    return await this.page.textContent('.error-message');
  }

  async isLoggedIn() {
    return await this.page.isVisible('.dashboard');
  }
}

// test
import { LoginPage } from './page-objects/LoginPage';

describe('Login flow', () => {
  let loginPage;

  beforeEach(async () => {
    loginPage = new LoginPage(page);
    await loginPage.navigate();
  });

  test('successful login', async () => {
    await loginPage.login('user@example.com', 'password123');
    expect(await loginPage.isLoggedIn()).toBe(true);
  });

  test('shows error for invalid credentials', async () => {
    await loginPage.login('user@example.com', 'wrongpassword');
    const error = await loginPage.getErrorMessage();
    expect(error).toBe('Invalid credentials');
  });
});
```

## Shared Test Utilities

### Pattern: Custom Matchers

**When to Use**: Reusable assertions across tests

```javascript
// test-utils/matchers.js
export const customMatchers = {
  toBeValidEmail(received) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const pass = emailRegex.test(received);

    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be a valid email`
          : `expected ${received} to be a valid email`
    };
  },

  toBeWithinRange(received, min, max) {
    const pass = received >= min && received <= max;

    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${min}-${max}`
          : `expected ${received} to be within range ${min}-${max}`
    };
  }
};

// test setup
import { customMatchers } from './test-utils/matchers';
expect.extend(customMatchers);

// usage
test('validates email format', () => {
  expect('user@example.com').toBeValidEmail();
  expect('invalid-email').not.toBeValidEmail();
});

test('checks age range', () => {
  expect(25).toBeWithinRange(18, 65);
  expect(10).not.toBeWithinRange(18, 65);
});
```

### Pattern: Test Helpers

```javascript
// test-utils/helpers.js
export async function waitFor(condition, timeout = 5000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  throw new Error('Timeout waiting for condition');
}

export function mockApiResponse(data, statusCode = 200) {
  return {
    status: statusCode,
    ok: statusCode >= 200 && statusCode < 300,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data))
  };
}

export function createMockStore(initialState = {}) {
  const state = { ...initialState };
  const listeners = [];

  return {
    getState: () => ({ ...state }),
    dispatch: (action) => {
      // Handle action
      listeners.forEach(listener => listener(state));
    },
    subscribe: (listener) => {
      listeners.push(listener);
      return () => {
        const index = listeners.indexOf(listener);
        listeners.splice(index, 1);
      };
    }
  };
}

// Usage
test('waits for async operation', async () => {
  startAsyncOperation();

  await waitFor(() => isOperationComplete());

  expect(getResult()).toBe('success');
});
```

## Anti-Patterns to Avoid

### Anti-Pattern: Testing Implementation Details

```javascript
// ❌ BAD: Tests internal implementation
test('uses specific algorithm', () => {
  const sorter = new Sorter();
  expect(sorter.algorithm).toBe('quicksort');
});

// ✅ GOOD: Tests behavior
test('sorts array correctly', () => {
  const sorter = new Sorter();
  const result = sorter.sort([3, 1, 2]);
  expect(result).toEqual([1, 2, 3]);
});
```

### Anti-Pattern: Overly Complex Tests

```javascript
// ❌ BAD: Too much logic in test
test('complex business logic', () => {
  let result;
  if (condition1) {
    result = doThing1();
  } else if (condition2) {
    result = doThing2();
  }

  for (let i = 0; i < result.length; i++) {
    // Complex verification
  }
});

// ✅ GOOD: Simple, focused test
test('processes valid input', () => {
  const result = processInput(validInput);
  expect(result).toEqual(expectedOutput);
});
```

### Anti-Pattern: Shared Mutable State

```javascript
// ❌ BAD: Shared state between tests
let sharedUser;

test('test 1', () => {
  sharedUser = { name: 'John' };
  sharedUser.name = 'Jane';
});

test('test 2', () => {
  expect(sharedUser.name).toBe('John'); // FAILS!
});

// ✅ GOOD: Isolated test data
test('test 1', () => {
  const user = { name: 'John' };
  user.name = 'Jane';
  expect(user.name).toBe('Jane');
});

test('test 2', () => {
  const user = { name: 'John' };
  expect(user.name).toBe('John');
});
```

### Anti-Pattern: Brittle Selectors (E2E)

```javascript
// ❌ BAD: Fragile selectors
await page.click('.MuiButton-root.MuiButton-contained');
await page.fill('#email-input-347', 'test@example.com');

// ✅ GOOD: Semantic selectors
await page.click('[data-testid="submit-button"]');
await page.fill('[aria-label="Email address"]', 'test@example.com');
```

### Anti-Pattern: Test Interdependence

```javascript
// ❌ BAD: Tests depend on each other
test('creates user', () => {
  globalUser = createUser({ name: 'John' });
});

test('updates user', () => {
  updateUser(globalUser.id, { name: 'Jane' }); // Depends on previous test
});

// ✅ GOOD: Independent tests
test('creates user', () => {
  const user = createUser({ name: 'John' });
  expect(user.name).toBe('John');
});

test('updates user', () => {
  const user = createUser({ name: 'John' });
  updateUser(user.id, { name: 'Jane' });

  const updated = getUser(user.id);
  expect(updated.name).toBe('Jane');
});
```

## Related Patterns

- **Setup Patterns**: See [docs/best-practices.md](best-practices.md)
- **Advanced Testing**: See [docs/advanced-topics.md](advanced-topics.md)
- **Troubleshooting**: See [docs/troubleshooting.md](troubleshooting.md)
