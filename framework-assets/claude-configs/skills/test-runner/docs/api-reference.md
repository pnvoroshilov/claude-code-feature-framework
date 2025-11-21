# API Reference - Test Framework Commands and APIs

## Table of Contents

- [Jest API Reference](#jest-api-reference)
- [Pytest API Reference](#pytest-api-reference)
- [Mocha API Reference](#mocha-api-reference)
- [Coverage Tool APIs](#coverage-tool-apis)
- [Reporter APIs](#reporter-apis)
- [Configuration Options](#configuration-options)
- [CLI Commands](#cli-commands)
- [Plugin Interfaces](#plugin-interfaces)

## Jest API Reference

### Test Definition

#### `describe(name, fn)`

Groups related tests together.

**Parameters:**
- `name` (string): Description of the test suite
- `fn` (function): Function containing tests

**Examples:**

```javascript
describe('UserService', () => {
  // Tests for UserService
});

describe('Array methods', () => {
  test('map doubles values', () => {
    expect([1, 2, 3].map(x => x * 2)).toEqual([2, 4, 6]);
  });
});

// Nested describes
describe('Calculator', () => {
  describe('addition', () => {
    test('adds positive numbers', () => {
      expect(2 + 2).toBe(4);
    });
  });

  describe('subtraction', () => {
    test('subtracts numbers', () => {
      expect(5 - 3).toBe(2);
    });
  });
});
```

#### `test(name, fn, timeout)`

**Alias:** `it(name, fn, timeout)`

Defines a single test case.

**Parameters:**
- `name` (string): Test description
- `fn` (function): Test function
- `timeout` (number, optional): Timeout in milliseconds

**Examples:**

```javascript
test('adds 1 + 2 to equal 3', () => {
  expect(1 + 2).toBe(3);
});

test('async operation', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});

test('long running test', async () => {
  await slowOperation();
}, 10000); // 10 second timeout
```

#### `test.only(name, fn)`

Runs only this test, skipping all others.

```javascript
test.only('run only this test', () => {
  expect(true).toBe(true);
});

test('this test is skipped', () => {
  expect(false).toBe(true);
});
```

#### `test.skip(name, fn)`

Skips this test.

```javascript
test.skip('skip this test', () => {
  // This test won't run
});

test('this test runs', () => {
  expect(true).toBe(true);
});
```

#### `test.each(table)(name, fn)`

Runs test multiple times with different data.

```javascript
test.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('adds %i + %i to equal %i', (a, b, expected) => {
  expect(a + b).toBe(expected);
});

// With objects
test.each([
  { a: 1, b: 1, expected: 2 },
  { a: 1, b: 2, expected: 3 },
  { a: 2, b: 1, expected: 3 },
])('adds $a + $b to equal $expected', ({ a, b, expected }) => {
  expect(a + b).toBe(expected);
});
```

### Lifecycle Hooks

#### `beforeAll(fn, timeout)`

Runs once before all tests in the describe block.

```javascript
describe('Database tests', () => {
  let database;

  beforeAll(async () => {
    database = await createTestDatabase();
  });

  test('query 1', () => {
    // Uses database
  });

  test('query 2', () => {
    // Uses same database
  });
});
```

#### `beforeEach(fn, timeout)`

Runs before each test in the describe block.

```javascript
describe('User tests', () => {
  let user;

  beforeEach(() => {
    user = createTestUser();
  });

  test('test 1', () => {
    // Fresh user instance
  });

  test('test 2', () => {
    // Another fresh user instance
  });
});
```

#### `afterEach(fn, timeout)`

Runs after each test.

```javascript
afterEach(() => {
  jest.clearAllMocks();
  jest.clearAllTimers();
});
```

#### `afterAll(fn, timeout)`

Runs once after all tests.

```javascript
afterAll(async () => {
  await database.close();
  await server.stop();
});
```

### Matchers

#### Equality Matchers

```javascript
// Strict equality (===)
expect(value).toBe(expected);

// Deep equality
expect(object).toEqual(expected);

// Strict deep equality
expect(object).toStrictEqual(expected);
```

#### Truthiness Matchers

```javascript
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();
```

#### Number Matchers

```javascript
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3.5);
expect(value).toBeLessThan(5);
expect(value).toBeLessThanOrEqual(4.5);

// Floating point equality
expect(0.1 + 0.2).toBeCloseTo(0.3); // Avoid expect(0.1 + 0.2).toBe(0.3)
```

#### String Matchers

```javascript
expect(string).toMatch(/pattern/);
expect(string).toMatch('substring');
expect(email).toContain('@');
expect(name).toHaveLength(5);
```

#### Array Matchers

```javascript
expect(array).toContain(item);
expect(array).toContainEqual(object);
expect(array).toHaveLength(3);
```

#### Object Matchers

```javascript
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('key', value);
expect(object).toMatchObject({ key: value });
```

#### Exception Matchers

```javascript
expect(() => {
  throwError();
}).toThrow();

expect(() => {
  throwError();
}).toThrow('Error message');

expect(() => {
  throwError();
}).toThrow(ErrorClass);
```

#### Async Matchers

```javascript
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();
```

#### Snapshot Matchers

```javascript
expect(value).toMatchSnapshot();
expect(value).toMatchInlineSnapshot(`"expected"`);
```

### Mock Functions

#### `jest.fn(implementation)`

Creates a mock function.

```javascript
const mockFn = jest.fn();
const mockFnWithImpl = jest.fn(x => x * 2);

// Call the mock
mockFn(1, 2, 3);

// Check calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith(1, 2, 3);
expect(mockFn).toHaveBeenLastCalledWith(1, 2, 3);
```

#### Mock Return Values

```javascript
const mock = jest.fn();

// Single return value
mock.mockReturnValue('value');

// Different returns for multiple calls
mock
  .mockReturnValueOnce('first')
  .mockReturnValueOnce('second')
  .mockReturnValue('default');

// Async returns
mock.mockResolvedValue('async value');
mock.mockRejectedValue(new Error('async error'));
```

#### Mock Implementation

```javascript
const mock = jest.fn();

// Set implementation
mock.mockImplementation(x => x * 2);

// One-time implementation
mock.mockImplementationOnce(x => x * 2);
```

#### Module Mocks

```javascript
// Mock entire module
jest.mock('./myModule');

// Mock with factory
jest.mock('./myModule', () => ({
  foo: jest.fn(),
  bar: 'mocked value'
}));

// Partial mock
jest.mock('./myModule', () => ({
  ...jest.requireActual('./myModule'),
  foo: jest.fn()
}));
```

#### Spy Functions

```javascript
const object = {
  method: () => 'real value'
};

// Spy on method
const spy = jest.spyOn(object, 'method');

// Method still works
expect(object.method()).toBe('real value');

// But calls are tracked
expect(spy).toHaveBeenCalled();

// Mock the implementation
spy.mockImplementation(() => 'mocked value');
expect(object.method()).toBe('mocked value');

// Restore original
spy.mockRestore();
```

### Timers

```javascript
// Use fake timers
jest.useFakeTimers();

// Advance by time
jest.advanceTimersByTime(1000);

// Run all timers
jest.runAllTimers();

// Run only pending timers
jest.runOnlyPendingTimers();

// Restore real timers
jest.useRealTimers();
```

## Pytest API Reference

### Test Definition

#### `def test_function():`

Defines a test function (must start with `test_`).

```python
def test_addition():
    assert 1 + 1 == 2

def test_string_length():
    assert len('hello') == 5

# Async tests
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await async_function()
    assert result == expected
```

### Fixtures

#### `@pytest.fixture`

Creates a reusable test fixture.

```python
import pytest

@pytest.fixture
def user():
    """Function-scoped fixture (default)"""
    return User(name='Test User')

@pytest.fixture(scope='module')
def database():
    """Module-scoped fixture (runs once per module)"""
    db = create_database()
    yield db
    db.close()

@pytest.fixture(scope='session')
def config():
    """Session-scoped fixture (runs once per test session)"""
    return load_config()

# Use fixtures in tests
def test_user_name(user):
    assert user.name == 'Test User'

def test_database_connection(database):
    assert database.is_connected()
```

#### Fixture Scopes

- `function`: Default, new instance per test
- `class`: New instance per test class
- `module`: New instance per module
- `session`: New instance per test session

#### Fixture Factories

```python
@pytest.fixture
def make_user():
    def _make_user(name='Default', email=None):
        return User(name=name, email=email)
    return _make_user

def test_custom_user(make_user):
    user = make_user(name='John', email='john@example.com')
    assert user.name == 'John'
```

### Parametrization

#### `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected

# Multiple parameters
@pytest.mark.parametrize("a", [1, 2])
@pytest.mark.parametrize("b", [3, 4])
def test_multiply(a, b):
    assert multiply(a, b) == a * b
    # Runs 4 times: (1,3), (1,4), (2,3), (2,4)

# With IDs
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
], ids=['case1', 'case2'])
def test_with_ids(input, expected):
    assert double(input) == expected
```

### Assertions

```python
# Basic assertions
assert value == expected
assert value != expected
assert value > 10
assert value in [1, 2, 3]
assert 'substring' in string

# Exception assertions
import pytest

def test_exception():
    with pytest.raises(ValueError):
        raise ValueError('error message')

    with pytest.raises(ValueError, match='error.*'):
        raise ValueError('error message')

# Approximate comparison
def test_floats():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

### Marks

```python
import pytest

# Skip test
@pytest.mark.skip(reason='Not implemented yet')
def test_feature():
    pass

# Skip conditionally
@pytest.mark.skipif(sys.version_info < (3, 8), reason='Requires Python 3.8+')
def test_python38_feature():
    pass

# Expected failure
@pytest.mark.xfail
def test_known_bug():
    assert buggy_function() == expected

# Custom marks
@pytest.mark.slow
def test_slow_operation():
    pass

# Run only marked tests
# pytest -m slow
```

## Mocha API Reference

### Test Definition

```javascript
describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when value is not present', function() {
      assert.equal([1, 2, 3].indexOf(4), -1);
    });
  });
});

// Async tests
it('async test', async function() {
  const result = await fetchData();
  assert.equal(result, expected);
});

// With timeout
it('slow test', function(done) {
  setTimeout(done, 5000);
}).timeout(10000);
```

### Hooks

```javascript
describe('Test suite', function() {
  before(function() {
    // Runs once before all tests
  });

  after(function() {
    // Runs once after all tests
  });

  beforeEach(function() {
    // Runs before each test
  });

  afterEach(function() {
    // Runs after each test
  });

  it('test 1', function() {
    // Test
  });

  it('test 2', function() {
    // Test
  });
});
```

### Exclusive and Inclusive Tests

```javascript
// Run only this test
describe.only('Only this suite', function() {
  it('test', function() {});
});

// Skip this test
describe.skip('Skip this suite', function() {
  it('test', function() {});
});
```

## Coverage Tool APIs

### Jest Coverage

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!**/*.test.{js,jsx,ts,tsx}',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['json', 'lcov', 'text', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### Istanbul (nyc) Coverage

```json
{
  "nyc": {
    "include": ["src/**/*.js"],
    "exclude": ["**/*.test.js"],
    "reporter": ["html", "text", "lcov"],
    "check-coverage": true,
    "branches": 80,
    "lines": 80,
    "functions": 80,
    "statements": 80
  }
}
```

### pytest-cov

```ini
# pytest.ini
[pytest]
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --cov-branch
```

## Reporter APIs

### Custom Jest Reporter

```javascript
// custom-reporter.js
class CustomReporter {
  constructor(globalConfig, options) {
    this._globalConfig = globalConfig;
    this._options = options;
  }

  onRunStart(results, options) {
    console.log('Test run started');
  }

  onTestStart(test) {
    console.log(`Starting: ${test.path}`);
  }

  onTestResult(test, testResult, results) {
    console.log(`Finished: ${test.path}`);
    console.log(`  Pass: ${testResult.numPassingTests}`);
    console.log(`  Fail: ${testResult.numFailingTests}`);
  }

  onRunComplete(contexts, results) {
    console.log('Test run complete');
    console.log(`Total tests: ${results.numTotalTests}`);
    console.log(`Passed: ${results.numPassedTests}`);
    console.log(`Failed: ${results.numFailedTests}`);
  }
}

module.exports = CustomReporter;
```

```javascript
// jest.config.js
module.exports = {
  reporters: [
    'default',
    ['./custom-reporter.js', { option: 'value' }]
  ]
};
```

### Pytest Plugin

```python
# conftest.py
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to access test results"""
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        if report.failed:
            print(f'FAILED: {item.nodeid}')
        elif report.passed:
            print(f'PASSED: {item.nodeid}')

def pytest_collection_modifyitems(config, items):
    """Modify or reorder test collection"""
    for item in items:
        # Add custom markers, modify items, etc.
        pass
```

## Configuration Options

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  // Test discovery
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/*.test.{js,ts}'],
  testPathIgnorePatterns: ['/node_modules/', '/build/'],

  // Execution
  maxWorkers: '50%',
  testTimeout: 5000,
  bail: false,

  // Mocking
  clearMocks: true,
  resetMocks: false,
  restoreMocks: false,

  // Coverage
  collectCoverage: false,
  coverageProvider: 'v8', // or 'babel'

  // Environment
  testEnvironment: 'node', // or 'jsdom'

  // Transforms
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },

  // Module resolution
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
# Test discovery
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Execution
addopts =
    -v
    --tb=short
    --strict-markers
    -n auto

# Markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests

# Coverage
[coverage:run]
source = src
omit =
    */tests/*
    */migrations/*
```

## CLI Commands

### Jest CLI

```bash
# Run all tests
jest

# Run specific file
jest path/to/test.js

# Run tests matching pattern
jest --testNamePattern="user authentication"

# Watch mode
jest --watch
jest --watchAll

# Coverage
jest --coverage
jest --coverage --collectCoverageFrom="src/**/*.js"

# Parallel execution
jest --maxWorkers=4
jest --runInBand  # Sequential execution

# Debugging
node --inspect-brk node_modules/.bin/jest --runInBand

# Update snapshots
jest --updateSnapshot

# Clear cache
jest --clearCache

# Show configuration
jest --showConfig
```

### Pytest CLI

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_user.py

# Run specific test
pytest tests/test_user.py::test_create_user

# Run tests matching pattern
pytest -k "user and create"

# Markers
pytest -m slow
pytest -m "not slow"

# Verbose output
pytest -v
pytest -vv

# Show output
pytest -s

# Stop on first failure
pytest -x
pytest --maxfail=3

# Parallel execution
pytest -n 4
pytest -n auto

# Coverage
pytest --cov=src
pytest --cov=src --cov-report=html

# Last failed
pytest --lf
pytest --last-failed

# Failed first
pytest --ff
pytest --failed-first
```

### Mocha CLI

```bash
# Run all tests
mocha

# Specific files
mocha test/user.test.js

# Pattern
mocha "test/**/*.test.js"

# Watch mode
mocha --watch

# Reporters
mocha --reporter spec
mocha --reporter json
mocha --reporter html > report.html

# Timeout
mocha --timeout 5000

# Slow threshold
mocha --slow 1000

# Grep (filter tests)
mocha --grep "user"

# Parallel
mocha --parallel

# Bail on first failure
mocha --bail
```

## Plugin Interfaces

### Jest Transform Plugin

```javascript
// custom-transformer.js
module.exports = {
  process(sourceText, sourcePath, options) {
    // Transform source code
    const transformedCode = transform(sourceText);

    return {
      code: transformedCode,
      map: null // Source map
    };
  },

  getCacheKey(sourceText, sourcePath, options) {
    // Return unique cache key
    return crypto
      .createHash('md5')
      .update(sourceText)
      .update(sourcePath)
      .digest('hex');
  }
};
```

### Pytest Plugin

```python
# pytest_plugin.py
import pytest

def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        '--custom-option',
        action='store',
        default='default',
        help='Custom option description'
    )

@pytest.fixture
def custom_fixture(request):
    """Custom fixture"""
    option = request.config.getoption('--custom-option')
    return option

def pytest_configure(config):
    """Configuration hook"""
    config.addinivalue_line(
        'markers',
        'custom: mark test as custom'
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        if 'custom' in item.keywords:
            item.add_marker(pytest.mark.slow)
```

## Related Documentation

- **Core Concepts**: See [docs/core-concepts.md](core-concepts.md)
- **Best Practices**: See [docs/best-practices.md](best-practices.md)
- **Patterns**: See [docs/patterns.md](patterns.md)
- **Troubleshooting**: See [docs/troubleshooting.md](troubleshooting.md)
