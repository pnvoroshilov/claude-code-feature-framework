# Advanced Topics - Expert-Level Testing Strategies

## Table of Contents

- [Parallel Test Execution](#parallel-test-execution)
- [Test Sharding Strategies](#test-sharding-strategies)
- [Performance Testing](#performance-testing)
- [Load and Stress Testing](#load-and-stress-testing)
- [Contract Testing](#contract-testing)
- [Mutation Testing](#mutation-testing)
- [Visual Regression Testing](#visual-regression-testing)
- [Test Flakiness Management](#test-flakiness-management)
- [Custom Test Reporters](#custom-test-reporters)
- [Test Infrastructure as Code](#test-infrastructure-as-code)

## Parallel Test Execution

### Overview

Parallel test execution runs multiple tests simultaneously, dramatically reducing total test time. Modern test frameworks support parallelization at file, test, and worker levels.

### Configuration Strategies

#### Jest Parallel Configuration

```javascript
// jest.config.js
module.exports = {
  // Use 50% of available CPU cores
  maxWorkers: '50%',

  // Or specify exact number
  maxWorkers: 4,

  // Run tests in band (sequential) for debugging
  // maxWorkers: 1,

  // Test timeout for parallel execution
  testTimeout: 30000,

  // Bail on first failure (faster CI feedback)
  bail: 1,

  // Clear mocks between tests
  clearMocks: true,

  // Reset modules between tests
  resetModules: true
};
```

#### Pytest Parallel Configuration

```python
# pytest.ini
[pytest]
addopts =
    -n auto              # Auto-detect CPU cores
    --dist loadscope     # Distribute by test scope
    --maxfail=1          # Stop on first failure

# Or use specific number of workers
# -n 4
```

```bash
# Command line
pytest -n 4                    # Use 4 workers
pytest -n auto                 # Auto-detect
pytest -n auto --dist loadfile # Distribute by file
```

### Worker Isolation

```javascript
// Ensure worker isolation
describe('Database tests', () => {
  let database;
  let connection;

  beforeAll(async () => {
    // Each worker gets its own database
    const workerId = process.env.JEST_WORKER_ID || '1';
    database = await createTestDatabase(`test_db_${workerId}`);
    connection = await database.connect();
  });

  afterAll(async () => {
    await connection.close();
    await database.drop();
  });

  test('test 1', async () => {
    // Runs in isolated worker
  });

  test('test 2', async () => {
    // May run in different worker
  });
});
```

### Parallel-Safe Patterns

```javascript
// ✅ GOOD: Thread-safe, isolated
test('creates unique user', async () => {
  const uniqueEmail = `user-${Date.now()}-${Math.random()}@example.com`;
  const user = await createUser({ email: uniqueEmail });
  expect(user.email).toBe(uniqueEmail);
});

// ❌ BAD: Race condition
let sharedCounter = 0;
test('increments counter', () => {
  sharedCounter++; // Not thread-safe!
  expect(sharedCounter).toBe(1);
});

// ✅ GOOD: Port allocation for parallel tests
async function getFreePort() {
  const server = require('http').createServer();
  return new Promise((resolve) => {
    server.listen(0, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
}

test('starts server on free port', async () => {
  const port = await getFreePort();
  const server = await startTestServer(port);
  expect(server.isListening()).toBe(true);
});
```

### Performance Monitoring

```javascript
// Monitor parallel execution performance
const { performance } = require('perf_hooks');

describe('Performance tracking', () => {
  let startTime;

  beforeAll(() => {
    startTime = performance.now();
  });

  afterAll(() => {
    const duration = performance.now() - startTime;
    console.log(`Suite completed in ${duration}ms`);
  });

  // Tests...
});
```

## Test Sharding Strategies

### Overview

Test sharding splits test suite across multiple machines/processes, enabling massive parallelization in CI/CD environments.

### GitHub Actions Sharding

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4, 5, 6, 7, 8]
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests (shard ${{ matrix.shard }})
        run: npx jest --shard=${{ matrix.shard }}/8

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          flags: shard-${{ matrix.shard }}
```

### Jest Sharding

```bash
# Split tests into 4 shards
jest --shard=1/4  # Shard 1 of 4
jest --shard=2/4  # Shard 2 of 4
jest --shard=3/4  # Shard 3 of 4
jest --shard=4/4  # Shard 4 of 4
```

### Custom Sharding Logic

```javascript
// custom-shard-runner.js
const { execSync } = require('child_process');
const glob = require('glob');

function shardTests(shardIndex, totalShards) {
  // Get all test files
  const testFiles = glob.sync('**/*.test.js');

  // Sort for consistent distribution
  testFiles.sort();

  // Calculate shard
  const shardSize = Math.ceil(testFiles.length / totalShards);
  const startIdx = (shardIndex - 1) * shardSize;
  const endIdx = startIdx + shardSize;

  const shardFiles = testFiles.slice(startIdx, endIdx);

  console.log(`Running shard ${shardIndex}/${totalShards}`);
  console.log(`Files: ${shardFiles.length}`);

  // Run tests
  const result = execSync(`jest ${shardFiles.join(' ')}`, {
    stdio: 'inherit'
  });

  return result;
}

// Usage: node custom-shard-runner.js 1 4
const shardIndex = parseInt(process.argv[2]);
const totalShards = parseInt(process.argv[3]);
shardTests(shardIndex, totalShards);
```

### Dynamic Shard Balancing

```javascript
// Smart sharding based on test duration
const fs = require('fs');

function loadTestDurations() {
  // Load previous test durations
  if (fs.existsSync('test-durations.json')) {
    return JSON.parse(fs.readFileSync('test-durations.json'));
  }
  return {};
}

function balancedSharding(testFiles, totalShards, durations) {
  const shards = Array.from({ length: totalShards }, () => ({
    files: [],
    totalDuration: 0
  }));

  // Sort by duration (longest first)
  const sortedFiles = testFiles.sort((a, b) => {
    const durationA = durations[a] || 1000;
    const durationB = durations[b] || 1000;
    return durationB - durationA;
  });

  // Assign to shard with least total duration
  sortedFiles.forEach(file => {
    const shortestShard = shards.reduce((min, shard, idx) =>
      shard.totalDuration < shards[min].totalDuration ? idx : min
    , 0);

    const duration = durations[file] || 1000;
    shards[shortestShard].files.push(file);
    shards[shortestShard].totalDuration += duration;
  });

  return shards;
}
```

## Performance Testing

### Overview

Performance testing measures application response times, throughput, and resource usage under various conditions.

### Benchmark Testing

```javascript
// Using benchmark.js
const Benchmark = require('benchmark');
const suite = new Benchmark.Suite();

suite
  .add('Array.forEach', () => {
    const arr = [1, 2, 3, 4, 5];
    arr.forEach(x => x * 2);
  })
  .add('for loop', () => {
    const arr = [1, 2, 3, 4, 5];
    for (let i = 0; i < arr.length; i++) {
      arr[i] * 2;
    }
  })
  .add('Array.map', () => {
    const arr = [1, 2, 3, 4, 5];
    arr.map(x => x * 2);
  })
  .on('cycle', (event) => {
    console.log(String(event.target));
  })
  .on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').map('name'));
  })
  .run({ async: true });
```

### Response Time Testing

```javascript
// Performance testing with assertions
describe('API performance', () => {
  test('responds within 200ms', async () => {
    const start = Date.now();

    const response = await fetch('http://localhost:3000/api/users');

    const duration = Date.now() - start;

    expect(response.status).toBe(200);
    expect(duration).toBeLessThan(200);
  });

  test('bulk operations complete within 1s', async () => {
    const start = Date.now();

    await Promise.all([
      createUser({ name: 'User 1' }),
      createUser({ name: 'User 2' }),
      createUser({ name: 'User 3' }),
      createUser({ name: 'User 4' }),
      createUser({ name: 'User 5' })
    ]);

    const duration = Date.now() - start;
    expect(duration).toBeLessThan(1000);
  });
});
```

### Memory Leak Detection

```javascript
// Detect memory leaks
describe('Memory leak tests', () => {
  test('does not leak memory', async () => {
    const initialMemory = process.memoryUsage().heapUsed;

    // Perform operations
    for (let i = 0; i < 10000; i++) {
      await createAndDestroyObject();
    }

    // Force garbage collection (requires --expose-gc flag)
    if (global.gc) {
      global.gc();
    }

    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = finalMemory - initialMemory;

    // Allow some memory increase, but flag large leaks
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // 10MB
  });
});
```

## Load and Stress Testing

### Overview

Load testing verifies system behavior under expected load. Stress testing finds breaking points by exceeding expected capacity.

### Artillery Load Testing

```yaml
# load-test.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10      # 10 users per second
      name: Warm up
    - duration: 120
      arrivalRate: 50      # 50 users per second
      name: Sustained load
    - duration: 60
      arrivalRate: 100     # 100 users per second
      name: Peak load

scenarios:
  - name: User registration flow
    flow:
      - post:
          url: '/api/users'
          json:
            email: '{{ $randomEmail }}'
            password: '{{ $randomString }}'
      - think: 2
      - post:
          url: '/api/login'
          json:
            email: '{{ email }}'
            password: '{{ password }}'
```

```bash
# Run load test
artillery run load-test.yml

# Generate HTML report
artillery run --output report.json load-test.yml
artillery report report.json
```

### K6 Load Testing

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up to 20 users
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 100 },  // Peak at 100 users
    { duration: '30s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.1'],               // Error rate under 10%
  },
};

export default function () {
  const response = http.get('http://localhost:3000/api/users');

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  errorRate.add(!success);
  sleep(1);
}
```

```bash
# Run k6 test
k6 run load-test.js

# Run with custom options
k6 run --vus 100 --duration 60s load-test.js
```

### Locust Load Testing (Python)

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3s between tasks

    @task(3)  # Weight: 3x more likely than other tasks
    def view_users(self):
        self.client.get("/api/users")

    @task(2)
    def view_user_detail(self):
        user_id = random.randint(1, 1000)
        self.client.get(f"/api/users/{user_id}")

    @task(1)
    def create_user(self):
        self.client.post("/api/users", json={
            "name": f"User {random.randint(1, 10000)}",
            "email": f"user{random.randint(1, 10000)}@example.com"
        })

    def on_start(self):
        # Called when user starts
        self.client.post("/api/login", json={
            "username": "test@example.com",
            "password": "password"
        })
```

```bash
# Run locust
locust -f locustfile.py

# Headless mode
locust -f locustfile.py --headless -u 100 -r 10 --run-time 1m
```

## Contract Testing

### Overview

Contract testing verifies that services communicate according to agreed-upon contracts, catching integration issues early.

### Pact Contract Testing

```javascript
// consumer-test.js (Frontend testing backend contract)
const { Pact } = require('@pact-foundation/pact');
const { API } = require('./api');

describe('User API Contract', () => {
  const provider = new Pact({
    consumer: 'FrontendApp',
    provider: 'UserService',
    port: 1234,
  });

  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());
  afterEach(() => provider.verify());

  test('gets user by ID', async () => {
    // Define expected interaction
    await provider.addInteraction({
      state: 'user 123 exists',
      uponReceiving: 'a request for user 123',
      withRequest: {
        method: 'GET',
        path: '/users/123',
      },
      willRespondWith: {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
        body: {
          id: 123,
          name: 'John Doe',
          email: 'john@example.com',
        },
      },
    });

    // Make actual request
    const api = new API('http://localhost:1234');
    const user = await api.getUser(123);

    // Verify response
    expect(user.id).toBe(123);
    expect(user.name).toBe('John Doe');
  });

  test('handles user not found', async () => {
    await provider.addInteraction({
      state: 'user 999 does not exist',
      uponReceiving: 'a request for non-existent user',
      withRequest: {
        method: 'GET',
        path: '/users/999',
      },
      willRespondWith: {
        status: 404,
        body: {
          error: 'User not found',
        },
      },
    });

    const api = new API('http://localhost:1234');

    await expect(api.getUser(999)).rejects.toThrow('User not found');
  });
});
```

### Provider Verification

```javascript
// provider-verification.js (Backend verifying frontend's expectations)
const { Verifier } = require('@pact-foundation/pact');

describe('User Service Provider', () => {
  test('validates contracts', async () => {
    const options = {
      provider: 'UserService',
      providerBaseUrl: 'http://localhost:3000',
      pactUrls: ['./pacts/frontendapp-userservice.json'],
      stateHandlers: {
        'user 123 exists': async () => {
          // Setup: Create user 123 in test database
          await createTestUser({ id: 123, name: 'John Doe' });
        },
        'user 999 does not exist': async () => {
          // Setup: Ensure user 999 doesn't exist
          await deleteTestUser(999);
        },
      },
    };

    await new Verifier(options).verifyProvider();
  });
});
```

## Mutation Testing

### Overview

Mutation testing evaluates test suite quality by introducing bugs (mutations) and checking if tests catch them.

### Stryker Mutation Testing

```javascript
// stryker.conf.js
module.exports = {
  mutator: 'javascript',
  packageManager: 'npm',
  reporters: ['html', 'clear-text', 'progress'],
  testRunner: 'jest',
  coverageAnalysis: 'perTest',
  mutate: [
    'src/**/*.js',
    '!src/**/*.test.js',
  ],
  thresholds: {
    high: 80,
    low: 60,
    break: 50
  }
};
```

```bash
# Run mutation tests
npx stryker run

# View report
open reports/mutation/html/index.html
```

### Understanding Mutation Score

```javascript
// Original code
function isEligible(age) {
  return age >= 18;  // Original condition
}

// Mutant 1: Change >= to >
function isEligible(age) {
  return age > 18;   // Mutation: Boundary change
}

// Mutant 2: Change >= to <=
function isEligible(age) {
  return age <= 18;  // Mutation: Operator change
}

// Tests must kill these mutants
test('age 18 is eligible', () => {
  expect(isEligible(18)).toBe(true);  // Kills Mutant 1
});

test('age 17 is not eligible', () => {
  expect(isEligible(17)).toBe(false); // Kills Mutant 2
});
```

## Visual Regression Testing

### Overview

Visual regression testing captures screenshots and detects unintended visual changes.

### Percy Visual Testing

```javascript
// visual-test.js
const percySnapshot = require('@percy/puppeteer');

describe('Visual regression tests', () => {
  test('homepage renders correctly', async () => {
    await page.goto('http://localhost:3000');
    await percySnapshot(page, 'Homepage');
  });

  test('user profile displays correctly', async () => {
    await page.goto('http://localhost:3000/profile');
    await percySnapshot(page, 'User Profile');
  });

  test('mobile viewport', async () => {
    await page.setViewport({ width: 375, height: 667 });
    await page.goto('http://localhost:3000');
    await percySnapshot(page, 'Homepage - Mobile');
  });
});
```

### BackstopJS Configuration

```json
{
  "id": "visual_regression_test",
  "viewports": [
    {
      "label": "phone",
      "width": 375,
      "height": 667
    },
    {
      "label": "tablet",
      "width": 768,
      "height": 1024
    },
    {
      "label": "desktop",
      "width": 1920,
      "height": 1080
    }
  ],
  "scenarios": [
    {
      "label": "Homepage",
      "url": "http://localhost:3000",
      "selectors": ["document"],
      "delay": 500
    },
    {
      "label": "User Profile",
      "url": "http://localhost:3000/profile",
      "selectors": [".profile-container"],
      "delay": 1000
    }
  ],
  "paths": {
    "bitmaps_reference": "backstop_data/bitmaps_reference",
    "bitmaps_test": "backstop_data/bitmaps_test",
    "html_report": "backstop_data/html_report"
  }
}
```

```bash
# Create reference images
backstop reference

# Run visual tests
backstop test

# Approve changes
backstop approve
```

## Test Flakiness Management

### Overview

Flaky tests pass or fail inconsistently, undermining confidence in test suite. Systematic approaches identify and fix flaky tests.

### Detecting Flaky Tests

```bash
# Run tests multiple times to detect flakiness
for i in {1..10}; do
  npm test || echo "Failed on iteration $i"
done

# Jest retry
jest --testNamePattern="flaky test" --maxRetries=3
```

### Flakiness Patterns and Fixes

```javascript
// ❌ FLAKY: Race condition
test('updates user', async () => {
  updateUser(123, { name: 'Jane' });
  const user = await getUser(123);
  expect(user.name).toBe('Jane'); // May fail if update not complete
});

// ✅ FIXED: Await async operation
test('updates user', async () => {
  await updateUser(123, { name: 'Jane' });
  const user = await getUser(123);
  expect(user.name).toBe('Jane');
});

// ❌ FLAKY: Time-dependent
test('creates timestamp', () => {
  const timestamp = createTimestamp();
  expect(timestamp).toBe('2024-01-01T00:00:00.000Z'); // Fails at different times
});

// ✅ FIXED: Freeze time
test('creates timestamp', () => {
  jest.useFakeTimers();
  jest.setSystemTime(new Date('2024-01-01'));

  const timestamp = createTimestamp();
  expect(timestamp).toBe('2024-01-01T00:00:00.000Z');

  jest.useRealTimers();
});

// ❌ FLAKY: Non-deterministic order
test('returns sorted results', async () => {
  const results = await searchUsers();
  expect(results[0].name).toBe('Alice'); // Order may vary
});

// ✅ FIXED: Sort before assertion
test('returns sorted results', async () => {
  const results = await searchUsers();
  const sorted = results.sort((a, b) => a.name.localeCompare(b.name));
  expect(sorted[0].name).toBe('Alice');
});
```

### Flakiness Tracking

```javascript
// Track test flakiness
const testResults = new Map();

afterEach(() => {
  const testName = expect.getState().currentTestName;
  const result = expect.getState().testPath;

  if (!testResults.has(testName)) {
    testResults.set(testName, { pass: 0, fail: 0 });
  }

  const stats = testResults.get(testName);
  if (result === 'passed') {
    stats.pass++;
  } else {
    stats.fail++;
  }
});

afterAll(() => {
  // Report flaky tests
  testResults.forEach((stats, testName) => {
    const total = stats.pass + stats.fail;
    if (stats.fail > 0 && stats.pass > 0) {
      const flakiness = (stats.fail / total * 100).toFixed(2);
      console.warn(`Flaky test: ${testName} (${flakiness}% failure rate)`);
    }
  });
});
```

## Related Topics

- **Core Concepts**: See [docs/core-concepts.md](core-concepts.md)
- **Best Practices**: See [docs/best-practices.md](best-practices.md)
- **Patterns**: See [docs/patterns.md](patterns.md)
- **Troubleshooting**: See [docs/troubleshooting.md](troubleshooting.md)
