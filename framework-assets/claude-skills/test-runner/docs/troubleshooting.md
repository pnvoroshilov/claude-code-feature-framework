# Troubleshooting - Common Test Issues and Solutions

## Table of Contents

- [Test Failures](#test-failures)
- [Flaky Test Debugging](#flaky-test-debugging)
- [Performance Issues](#performance-issues)
- [Coverage Problems](#coverage-problems)
- [Framework-Specific Issues](#framework-specific-issues)
- [Mock and Stub Issues](#mock-and-stub-issues)
- [Async Test Problems](#async-test-problems)
- [CI/CD Test Failures](#cicd-test-failures)
- [Memory and Resource Leaks](#memory-and-resource-leaks)
- [Configuration Issues](#configuration-issues)

## Test Failures

### Problem: Tests Pass Locally But Fail in CI

**Symptoms**:
- All tests pass on developer machines
- Same tests fail in CI/CD pipeline
- Intermittent failures

**Root Causes**:
1. Environment differences
2. Timing issues
3. Resource constraints
4. Parallel execution conflicts

**Solutions**:

```javascript
// ✅ Solution 1: Match CI environment locally
// Use Docker to replicate CI environment
docker run -v $(pwd):/app -w /app node:18 npm test

// ✅ Solution 2: Make tests environment-agnostic
test('uses environment-specific configuration', () => {
  const config = {
    apiUrl: process.env.API_URL || 'http://localhost:3000',
    timeout: process.env.TIMEOUT || 5000
  };

  expect(config.apiUrl).toBeDefined();
});

// ✅ Solution 3: Increase timeouts for CI
// jest.config.js
module.exports = {
  testTimeout: process.env.CI ? 30000 : 5000
};
```

### Problem: Random Test Failures

**Symptoms**:
- Tests fail occasionally without code changes
- Different tests fail each time
- Rerunning tests sometimes passes

**Root Cause**: Non-deterministic behavior

**Solutions**:

```javascript
// ❌ Problem: Random data
test('processes user', () => {
  const user = { id: Math.random() };
  // Random IDs cause conflicts
});

// ✅ Solution: Deterministic data
let idCounter = 0;
beforeEach(() => {
  idCounter = 0;
});

test('processes user', () => {
  const user = { id: ++idCounter };
  // Predictable IDs
});

// ❌ Problem: Time-dependent tests
test('creates future date', () => {
  const future = new Date(Date.now() + 1000);
  expect(isFuture(future)).toBe(true);
  // May fail due to timing
});

// ✅ Solution: Mock time
test('creates future date', () => {
  jest.useFakeTimers();
  jest.setSystemTime(new Date('2024-01-01'));

  const future = new Date('2024-01-02');
  expect(isFuture(future)).toBe(true);

  jest.useRealTimers();
});
```

### Problem: Tests Fail After Specific Test Order

**Symptoms**:
- Tests pass individually
- Tests fail when run together
- Order-dependent failures

**Root Cause**: Shared state pollution

**Solutions**:

```javascript
// ❌ Problem: Global state
let globalUser;

test('test A', () => {
  globalUser = { id: 1 };
  globalUser.name = 'Changed';
});

test('test B', () => {
  expect(globalUser.name).toBe('Original'); // FAILS!
});

// ✅ Solution: Isolated state
describe('User tests', () => {
  let user;

  beforeEach(() => {
    user = { id: 1, name: 'Original' };
  });

  test('test A', () => {
    user.name = 'Changed';
    expect(user.name).toBe('Changed');
  });

  test('test B', () => {
    expect(user.name).toBe('Original');
  });
});

// ✅ Solution: Clean up after tests
afterEach(() => {
  jest.clearAllMocks();
  jest.resetModules();
});
```

## Flaky Test Debugging

### Problem: Intermittent Async Failures

**Symptoms**:
- Promise rejection errors
- "Cannot read property of undefined"
- Timing-related failures

**Debugging Strategy**:

```javascript
// Step 1: Add detailed logging
test('async operation', async () => {
  console.log('Starting test');

  const result = await fetchData();
  console.log('Fetched data:', result);

  expect(result).toBeDefined();
  console.log('Test passed');
});

// Step 2: Increase timeout temporarily
test('slow async operation', async () => {
  // Increase timeout to see if it's timing issue
  jest.setTimeout(30000);

  const result = await slowOperation();
  expect(result).toBeDefined();
}, 30000);

// Step 3: Add explicit waits
test('waits for async completion', async () => {
  const promise = asyncOperation();

  // Wait for all pending promises
  await new Promise(resolve => setImmediate(resolve));

  const result = await promise;
  expect(result).toBeDefined();
});

// ✅ Solution: Use proper async patterns
test('handles async correctly', async () => {
  // Ensure all async operations complete
  await expect(asyncOperation()).resolves.toBeDefined();

  // Or catch rejections
  await expect(failingOperation()).rejects.toThrow('Error');
});
```

### Problem: Network-Dependent Flakiness

**Symptoms**:
- Tests fail with network errors
- Timeouts in CI but not locally
- Inconsistent API responses

**Solutions**:

```javascript
// ✅ Solution 1: Mock network calls
jest.mock('axios');
import axios from 'axios';

test('fetches user data', async () => {
  axios.get.mockResolvedValue({
    data: { id: 1, name: 'John' }
  });

  const user = await fetchUser(1);
  expect(user.name).toBe('John');
});

// ✅ Solution 2: Use nock for HTTP mocking
const nock = require('nock');

test('API integration', async () => {
  nock('https://api.example.com')
    .get('/users/1')
    .reply(200, { id: 1, name: 'John' });

  const user = await fetchUser(1);
  expect(user.name).toBe('John');
});

// ✅ Solution 3: Retry with exponential backoff
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve =>
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

## Performance Issues

### Problem: Tests Running Very Slow

**Symptoms**:
- Test suite takes >10 minutes
- Individual tests take seconds
- Feedback loop too slow

**Diagnostic Commands**:

```bash
# Profile Jest tests
node --inspect-brk node_modules/.bin/jest --runInBand

# Show slowest tests
jest --verbose --detectOpenHandles

# pytest with duration report
pytest --durations=10

# pytest with profiling
pytest --profile
```

**Solutions**:

```javascript
// ✅ Solution 1: Parallel execution
// jest.config.js
module.exports = {
  maxWorkers: '50%' // Use half of CPU cores
};

// ✅ Solution 2: Optimize setup/teardown
describe('Database tests', () => {
  // ❌ Slow: Create DB per test
  beforeEach(async () => {
    database = await createDatabase();
  });

  // ✅ Fast: Create DB once per suite
  beforeAll(async () => {
    database = await createDatabase();
  });

  beforeEach(async () => {
    await database.clearData(); // Fast operation
  });
});

// ✅ Solution 3: Use in-memory alternatives
// ❌ Slow: Real database
const db = await createPostgresConnection();

// ✅ Fast: In-memory database
const db = await createSQLiteMemoryDB();

// ✅ Solution 4: Skip slow tests in development
test.skip('slow integration test', async () => {
  // Only run in CI
});

// Or use environment variable
const runSlowTests = process.env.RUN_SLOW_TESTS === 'true';

(runSlowTests ? test : test.skip)('slow test', async () => {
  // Test implementation
});
```

### Problem: Test Timeout Errors

**Symptoms**:
- "Timeout - Async callback was not invoked"
- Tests hang indefinitely
- Need to kill test process

**Solutions**:

```javascript
// ✅ Solution 1: Increase timeout
test('long running operation', async () => {
  const result = await longRunningTask();
  expect(result).toBeDefined();
}, 30000); // 30 second timeout

// ✅ Solution 2: Use fake timers
test('delayed operation', () => {
  jest.useFakeTimers();

  const callback = jest.fn();
  scheduleCallback(callback, 5000);

  jest.advanceTimersByTime(5000);

  expect(callback).toHaveBeenCalled();
  jest.useRealTimers();
});

// ✅ Solution 3: Detect hanging promises
test('detects open handles', async () => {
  const result = await operation();

  // Ensure all promises resolve
  await new Promise(resolve => setImmediate(resolve));

  expect(result).toBeDefined();
});

// Run with detection
// jest --detectOpenHandles
```

## Coverage Problems

### Problem: Low Coverage Despite Many Tests

**Symptoms**:
- Coverage reports show <50%
- Many files not covered
- Branch coverage lower than expected

**Diagnostic Steps**:

```bash
# Generate detailed coverage report
npm test -- --coverage --coverageReporters=html

# Open HTML report
open coverage/lcov-report/index.html

# View uncovered lines
npm test -- --coverage --coverageReporters=text
```

**Solutions**:

```javascript
// ✅ Solution 1: Cover all branches
function validateAge(age) {
  if (age < 0) {           // Branch 1
    return 'invalid';
  }
  if (age < 18) {          // Branch 2
    return 'minor';
  }
  return 'adult';          // Branch 3
}

// Test all branches
describe('validateAge', () => {
  test('handles negative age', () => {
    expect(validateAge(-1)).toBe('invalid');
  });

  test('handles minor age', () => {
    expect(validateAge(15)).toBe('minor');
  });

  test('handles adult age', () => {
    expect(validateAge(25)).toBe('adult');
  });

  test('handles boundary at 18', () => {
    expect(validateAge(18)).toBe('adult');
  });
});

// ✅ Solution 2: Test error paths
function divide(a, b) {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

test('handles division by zero', () => {
  expect(() => divide(10, 0)).toThrow('Division by zero');
});

// ✅ Solution 3: Configure coverage collection
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!**/node_modules/**'
  ]
};
```

### Problem: Coverage Report Not Updating

**Symptoms**:
- Coverage numbers stay the same
- New tests don't increase coverage
- Cached coverage data

**Solutions**:

```bash
# Clear Jest cache
jest --clearCache

# Delete coverage directory
rm -rf coverage/

# Run with no cache
jest --no-cache --coverage

# pytest clear cache
rm -rf .pytest_cache/
rm -rf .coverage
pytest --cache-clear
```

## Framework-Specific Issues

### Jest Issues

**Problem: "Cannot find module" errors**

```bash
# Solution: Clear module cache
jest --clearCache

# Or reset modules between tests
afterEach(() => {
  jest.resetModules();
});
```

**Problem: Mocks not working**

```javascript
// ❌ Mock after import
import { fetchData } from './api';
jest.mock('./api');

// ✅ Mock before import
jest.mock('./api');
import { fetchData } from './api';
```

### Pytest Issues

**Problem: "Fixture not found" errors**

```python
# ❌ Wrong fixture scope
@pytest.fixture(scope="module")
def user():
    return User()

def test_user(user):  # May get stale user
    pass

# ✅ Correct fixture scope
@pytest.fixture  # Default: function scope
def user():
    return User()
```

**Problem: Import errors**

```bash
# Solution: Install in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
pytest
```

## Mock and Stub Issues

### Problem: Mock Not Being Called

**Symptoms**:
- `expect(mock).toHaveBeenCalled()` fails
- Mock function never invoked
- Real function called instead

**Solutions**:

```javascript
// ❌ Problem: Mock not injected
class UserService {
  constructor() {
    this.api = new RealAPI(); // Always uses real API
  }
}

// ✅ Solution: Dependency injection
class UserService {
  constructor(api = new RealAPI()) {
    this.api = api;
  }
}

// Test with mock
const mockAPI = { fetchUser: jest.fn() };
const service = new UserService(mockAPI);

// ✅ Solution: Module mock
jest.mock('./api');
import { fetchUser } from './api';

// Mock is automatically injected
```

### Problem: Mock Returns Undefined

**Symptoms**:
- Mock function returns undefined
- Expected return value not provided
- Async mocks not resolving

**Solutions**:

```javascript
// ❌ Problem: No return value
const mockFn = jest.fn();
mockFn(); // Returns undefined

// ✅ Solution: Set return value
const mockFn = jest.fn().mockReturnValue('result');
mockFn(); // Returns 'result'

// ✅ For async functions
const mockAsync = jest.fn().mockResolvedValue('result');
await mockAsync(); // Resolves to 'result'

// ✅ Different returns for multiple calls
const mockFn = jest.fn()
  .mockReturnValueOnce('first')
  .mockReturnValueOnce('second')
  .mockReturnValue('default');

mockFn(); // 'first'
mockFn(); // 'second'
mockFn(); // 'default'
mockFn(); // 'default'
```

## Async Test Problems

### Problem: Test Finishes Before Async Operation

**Symptoms**:
- Assertions not run
- Test passes but shouldn't
- "Unhandled promise rejection" warnings

**Solutions**:

```javascript
// ❌ Problem: Not awaiting async
test('fetches data', () => {
  fetchData().then(result => {
    expect(result).toBeDefined(); // Never runs!
  });
});

// ✅ Solution 1: Use async/await
test('fetches data', async () => {
  const result = await fetchData();
  expect(result).toBeDefined();
});

// ✅ Solution 2: Return promise
test('fetches data', () => {
  return fetchData().then(result => {
    expect(result).toBeDefined();
  });
});

// ✅ Solution 3: Use resolves matcher
test('fetches data', () => {
  return expect(fetchData()).resolves.toBeDefined();
});
```

### Problem: "Cannot read property of undefined" in Async Tests

**Symptoms**:
- Properties accessed before data loaded
- Race conditions
- Timing issues

**Solutions**:

```javascript
// ❌ Problem: Not waiting for data
test('displays user name', async () => {
  const promise = fetchUser(1);
  expect(promise.name).toBeDefined(); // promise is pending!
});

// ✅ Solution: Await data
test('displays user name', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBeDefined();
});

// ✅ Solution: Use waitFor utility
import { waitFor } from '@testing-library/react';

test('displays user name', async () => {
  render(<UserProfile userId={1} />);

  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
```

## CI/CD Test Failures

### Problem: Tests Pass Locally, Fail in GitHub Actions

**Diagnostic Steps**:

```yaml
# .github/workflows/test.yml
- name: Debug environment
  run: |
    echo "Node version: $(node --version)"
    echo "NPM version: $(npm --version)"
    echo "Working directory: $(pwd)"
    echo "Environment variables:"
    env | sort

- name: Run tests with verbose output
  run: npm test -- --verbose --no-coverage
```

**Solutions**:

```yaml
# ✅ Solution 1: Match Node version
- uses: actions/setup-node@v3
  with:
    node-version: '18' # Match local version

# ✅ Solution 2: Use consistent package manager
- name: Install dependencies
  run: npm ci # Instead of npm install

# ✅ Solution 3: Set environment variables
- name: Run tests
  env:
    NODE_ENV: test
    CI: true
  run: npm test
```

### Problem: Timeout in CI

**Solutions**:

```yaml
# Increase timeout
- name: Run tests
  run: npm test
  timeout-minutes: 30

# Split tests
- name: Run unit tests
  run: npm run test:unit

- name: Run integration tests
  run: npm run test:integration
```

## Memory and Resource Leaks

### Problem: Tests Consume Excessive Memory

**Symptoms**:
- Memory usage grows during test run
- Out of memory errors
- Slow performance over time

**Diagnostic**:

```javascript
// Monitor memory usage
describe('Memory monitoring', () => {
  afterEach(() => {
    const usage = process.memoryUsage();
    console.log('Heap used:', usage.heapUsed / 1024 / 1024, 'MB');
  });
});
```

**Solutions**:

```javascript
// ✅ Solution 1: Clean up after tests
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
  jest.clearAllTimers();
});

// ✅ Solution 2: Limit test data size
// ❌ Creates large arrays
const bigArray = Array(1000000).fill({ data: 'x' });

// ✅ Use reasonable test data
const testArray = Array(100).fill({ data: 'x' });

// ✅ Solution 3: Run garbage collection
// Run with: node --expose-gc
afterEach(() => {
  if (global.gc) {
    global.gc();
  }
});
```

## Configuration Issues

### Problem: Jest Configuration Not Loading

**Symptoms**:
- Custom matchers not available
- Coverage not collected
- Wrong files being tested

**Solutions**:

```javascript
// Check configuration is valid
// jest.config.js
module.exports = {
  // Explicitly set roots
  roots: ['<rootDir>/src', '<rootDir>/tests'],

  // Set test match patterns
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/*.{spec,test}.{js,jsx,ts,tsx}'
  ],

  // Verify setup files
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js']
};

// Validate configuration
// npx jest --showConfig
```

### Problem: Module Resolution Errors

```javascript
// jest.config.js
module.exports = {
  // Add module name mapper
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  },

  // Transform specific modules
  transformIgnorePatterns: [
    'node_modules/(?!(module-to-transform)/)'
  ]
};
```

## Quick Reference

### Common Error Messages and Solutions

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| "Timeout" | Async not awaited | Add `await` or increase timeout |
| "Cannot find module" | Import path wrong | Check path, clear cache |
| "Mock not called" | Mock not injected | Use dependency injection |
| "Test finishes early" | Promise not returned | Return or await promise |
| "Random failures" | Shared state | Isolate test data |
| "Memory leak" | Resources not cleaned | Add cleanup in afterEach |

## Related Resources

- **Core Concepts**: See [docs/core-concepts.md](core-concepts.md)
- **Best Practices**: See [docs/best-practices.md](best-practices.md)
- **Advanced Topics**: See [docs/advanced-topics.md](advanced-topics.md)
- **API Reference**: See [docs/api-reference.md](api-reference.md)
