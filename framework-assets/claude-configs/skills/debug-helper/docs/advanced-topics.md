# Advanced Debugging Topics

Expert-level debugging techniques for complex scenarios including concurrency issues, memory problems, performance analysis, and production debugging.

## Table of Contents

- [Concurrency and Race Condition Debugging](#concurrency-and-race-condition-debugging)
- [Memory Leak Detection and Analysis](#memory-leak-detection-and-analysis)
- [Performance Profiling](#performance-profiling)
- [Production Debugging](#production-debugging)
- [Distributed Systems Debugging](#distributed-systems-debugging)
- [Heisenbug Investigation](#heisenbug-investigation)
- [Post-Mortem Analysis](#post-mortem-analysis)

## Concurrency and Race Condition Debugging

### Understanding Race Conditions

Race conditions occur when the correctness of a program depends on the timing or ordering of uncontrollable events.

**Common Scenarios:**
- Multiple async operations modifying shared state
- Event handlers firing in unexpected order
- Database transactions with insufficient isolation
- Parallel requests to same resource

### Detection Techniques

```javascript
// Example: Race condition in React state updates

// BUGGY CODE
function Counter() {
  const [count, setCount] = useState(0);

  const increment = async () => {
    // Simulate async operation
    await delay(100);

    // Race condition: count might be stale
    setCount(count + 1);  // ⚠️ Captures count at function call time
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>Increment</button>
    </div>
  );
}

// PROBLEM: Click twice rapidly
// Click 1: count=0, schedules setCount(0+1)
// Click 2: count=0, schedules setCount(0+1)
// Result: count=1 instead of 2

// DETECTION: Add logging
const increment = async () => {
  const capturedCount = count;
  console.log('Increment called with count:', capturedCount);

  await delay(100);

  console.log('Setting count from', capturedCount, 'to', capturedCount + 1);
  console.log('Current actual count:', count);

  setCount(capturedCount + 1);
};

// Logs reveal stale closure capturing old count

// FIX: Use functional update
const increment = async () => {
  await delay(100);

  // Function receives current state, not stale closure
  setCount(prevCount => prevCount + 1);
};
```

### Advanced Race Condition Patterns

```javascript
// Pattern 1: Race condition in data fetching

let requestInFlight = false;

async function fetchData() {
  if (requestInFlight) {
    console.log('Request already in flight, skipping');
    return;
  }

  requestInFlight = true;

  try {
    const data = await api.getData();
    updateUI(data);
  } finally {
    requestInFlight = false;
  }
}

// Pattern 2: Cancel previous requests
let abortController = null;

async function fetchData() {
  // Cancel previous request
  if (abortController) {
    abortController.abort();
  }

  abortController = new AbortController();

  try {
    const data = await fetch('/api/data', {
      signal: abortController.signal
    });
    updateUI(data);
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Request cancelled');
      return;
    }
    throw error;
  }
}

// Pattern 3: Use token to ignore stale responses
let requestToken = 0;

async function fetchData() {
  const currentToken = ++requestToken;

  const data = await api.getData();

  // Ignore if newer request started
  if (currentToken !== requestToken) {
    console.log('Stale response, ignoring');
    return;
  }

  updateUI(data);
}
```

## Memory Leak Detection and Analysis

### Identifying Memory Leaks

**Symptoms:**
- Application becomes slower over time
- Increased memory usage in task manager
- Browser tab becomes unresponsive
- "Out of memory" errors

### Using Chrome DevTools

```javascript
// Step 1: Take baseline heap snapshot
// DevTools → Memory → Heap Snapshot → Take Snapshot

// Step 2: Exercise the feature suspected of leaking
// Perform actions that should be cleaned up

// Step 3: Force garbage collection
// DevTools → Memory → Collect garbage icon

// Step 4: Take another heap snapshot

// Step 5: Compare snapshots
// Select second snapshot → Comparison dropdown → Select baseline

// Analysis: Look for growing object counts
// - Detached DOM nodes (should be 0)
// - Event listeners (should be cleaned up)
// - Large arrays/objects retained unexpectedly
```

### Common Memory Leak Patterns

```javascript
// LEAK 1: Event listeners not removed
class Component {
  constructor() {
    this.handleResize = () => {
      console.log('Window resized');
    };

    // LEAK: Added but never removed
    window.addEventListener('resize', this.handleResize);
  }

  // FIX: Clean up in unmount
  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}

// LEAK 2: Timers not cleared
function Component() {
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchData();
    }, 5000);

    // LEAK: No cleanup
    // Component unmounts but interval continues

    // FIX: Return cleanup function
    return () => clearInterval(intervalId);
  }, []);
}

// LEAK 3: Closure retaining large objects
function createHandler(largeData) {
  // LEAK: Closure captures largeData even if not used
  return function handler(event) {
    console.log('Event:', event.type);
    // largeData not used but retained in closure
  };
}

// FIX: Don't capture what you don't need
function createHandler() {
  return function handler(event) {
    console.log('Event:', event.type);
  };
}

// LEAK 4: Circular references in old IE
// (Modern browsers handle this, but good to know)
function Parent() {
  const child = new Child();
  child.parent = this;  // Circular reference
  this.child = child;

  // FIX in old environments: Break cycle on cleanup
  this.destroy = () => {
    this.child.parent = null;
    this.child = null;
  };
}
```

### Memory Profiling

```javascript
// Record memory timeline
// DevTools → Memory → Allocation instrumentation on timeline

// Observe patterns:
// - Sawtooth pattern (normal): GC cleaning up regularly
// - Steady climb (leak): Memory never reclaimed
// - Spikes (potential issue): Large allocations

// Analyze allocation stacks
// Drilling down shows exactly where objects were allocated
```

## Performance Profiling

### Identifying Performance Bottlenecks

```javascript
// 1. User Timing API
function expensiveOperation() {
  performance.mark('operation-start');

  // ... complex code ...

  performance.mark('operation-end');
  performance.measure('operation', 'operation-start', 'operation-end');

  const measure = performance.getEntriesByName('operation')[0];
  console.log('Operation took:', measure.duration, 'ms');
}

// 2. Console timing (simpler)
console.time('render-components');
renderAllComponents();
console.timeEnd('render-components');

// 3. Profiler in React DevTools
import { Profiler } from 'react';

<Profiler
  id="UserList"
  onRender={(id, phase, actualDuration) => {
    console.log(`${id} (${phase}) took ${actualDuration}ms`);
  }}
>
  <UserList />
</Profiler>
```

### Chrome Performance Timeline

```javascript
// Record performance profile:
// DevTools → Performance → Record

// Analyze flame graph:
// - Wide bars: Long-running functions
// - Tall stacks: Deep call hierarchies
// - Red in timeline: Frames taking > 16ms (janky)

// Common bottlenecks:
// 1. Scripting (yellow): JavaScript execution
//    → Optimize algorithms, reduce work

// 2. Rendering (purple): Style calculation, layout
//    → Reduce DOM size, avoid forced reflow

// 3. Painting (green): Drawing pixels
//    → Reduce paint complexity, use will-change

// 4. System (gray): Browser overhead
//    → Usually not controllable
```

### Analyzing Slow Renders

```javascript
// React: Detect slow renders
function useWhyDidYouUpdate(name, props) {
  const previousProps = useRef();

  useEffect(() => {
    if (previousProps.current) {
      const allKeys = Object.keys({ ...previousProps.current, ...props });
      const changedProps = {};

      allKeys.forEach(key => {
        if (previousProps.current[key] !== props[key]) {
          changedProps[key] = {
            from: previousProps.current[key],
            to: props[key]
          };
        }
      });

      if (Object.keys(changedProps).length > 0) {
        console.log('[why-did-you-update]', name, changedProps);
      }
    }

    previousProps.current = props;
  });
}

// Usage:
function MyComponent(props) {
  useWhyDidYouUpdate('MyComponent', props);
  // Component renders slowly - now you know which props changed
}
```

## Production Debugging

### Safe Production Debugging Practices

**Never in Production:**
- ❌ Attach debugger (pauses execution for all users)
- ❌ Add extensive console.logs (performance impact)
- ❌ Modify code directly on server
- ❌ Expose sensitive data in logs

**Safe for Production:**
- ✅ Feature flags to enable detailed logging for specific users
- ✅ Distributed tracing systems
- ✅ Error tracking services (Sentry, Rollbar)
- ✅ Metric collection and dashboards
- ✅ Log aggregation (minimal performance impact)

### Feature Flag Debugging

```javascript
// Enable verbose logging for specific users
function logDebug(message, data) {
  const user = getCurrentUser();

  // Only log for flagged users or in debug mode
  if (user.debugMode || process.env.DEBUG_USER_IDS?.includes(user.id)) {
    logger.debug(message, {
      ...data,
      userId: user.id,
      timestamp: Date.now(),
      sessionId: getSessionId()
    });
  }
}

// Usage:
async function processPayment(payment) {
  logDebug('Processing payment', { paymentId: payment.id });

  const result = await chargeCard(payment);

  logDebug('Payment result', { result });

  return result;
}
```

### Distributed Tracing

```javascript
// Add correlation IDs to track requests across services
import { v4 as uuidv4 } from 'uuid';

app.use((req, res, next) => {
  // Create or propagate correlation ID
  req.correlationId = req.headers['x-correlation-id'] || uuidv4();

  res.setHeader('x-correlation-id', req.correlationId);

  // Add to all logs
  req.logger = logger.child({ correlationId: req.correlationId });

  next();
});

// In business logic:
async function getUserData(userId, req) {
  req.logger.info('Fetching user data', { userId });

  const user = await db.users.findById(userId);

  req.logger.info('User data retrieved', {
    userId,
    found: user !== null
  });

  // When calling other services, propagate correlation ID
  const orders = await fetch('https://orders-api/user/' + userId, {
    headers: {
      'x-correlation-id': req.correlationId
    }
  });

  return { user, orders };
}

// Now can trace single request across all services
// Search logs by correlation ID to see full flow
```

## Distributed Systems Debugging

### Challenges

- Multiple services, unclear which is failing
- Network issues between services
- Timing issues across service boundaries
- Inconsistent state across databases

### Strategies

```javascript
// 1. Health checks on all services
app.get('/health', async (req, res) => {
  const health = {
    service: 'user-api',
    status: 'healthy',
    timestamp: Date.now(),
    dependencies: {}
  };

  try {
    // Check database
    await db.query('SELECT 1');
    health.dependencies.database = 'healthy';
  } catch (error) {
    health.dependencies.database = 'unhealthy';
    health.status = 'degraded';
  }

  try {
    // Check external service
    await fetch('https://auth-service/health');
    health.dependencies.authService = 'healthy';
  } catch (error) {
    health.dependencies.authService = 'unhealthy';
    health.status = 'degraded';
  }

  res.json(health);
});

// 2. Circuit breakers
class CircuitBreaker {
  constructor(service, { threshold = 5, timeout = 60000 }) {
    this.service = service;
    this.failureCount = 0;
    this.threshold = threshold;
    this.timeout = timeout;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.nextAttempt = Date.now();
  }

  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error(`Circuit breaker open for ${this.service}`);
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await fn();

      if (this.state === 'HALF_OPEN') {
        this.state = 'CLOSED';
        this.failureCount = 0;
      }

      return result;
    } catch (error) {
      this.failureCount++;

      if (this.failureCount >= this.threshold) {
        this.state = 'OPEN';
        this.nextAttempt = Date.now() + this.timeout;
        console.error(`Circuit breaker opened for ${this.service}`);
      }

      throw error;
    }
  }
}

// Usage:
const authServiceBreaker = new CircuitBreaker('auth-service');

async function validateToken(token) {
  return authServiceBreaker.call(async () => {
    return await fetch('https://auth-service/validate', {
      body: JSON.stringify({ token })
    });
  });
}
```

## Heisenbug Investigation

"Heisenbug": A bug that disappears when you try to observe it (like Heisenberg uncertainty principle).

### Causes

- Race conditions sensitive to timing
- Observer effect (adding logs changes timing)
- Dependent on external state (time, random, network)
- Optimization-sensitive bugs

### Investigation Strategies

```javascript
// 1. Passive observation (minimal invasiveness)
// Instead of console.log (synchronous, blocks execution):

// Use async logging that doesn't affect timing
const asyncLogger = {
  log: (...args) => {
    setImmediate(() => console.log(...args));
  }
};

// 2. Statistical analysis
// Run test many times, collect statistics
async function testForHeisenbug(iterations = 1000) {
  const results = {
    success: 0,
    failure: 0,
    errors: {}
  };

  for (let i = 0; i < iterations; i++) {
    try {
      await suspiciousFunction();
      results.success++;
    } catch (error) {
      results.failure++;
      results.errors[error.message] = (results.errors[error.message] || 0) + 1;
    }
  }

  console.log('Results:', results);
  console.log('Failure rate:', (results.failure / iterations * 100).toFixed(2) + '%');
  console.log('Error distribution:', results.errors);
}

// 3. Record and replay
// Capture inputs and state, replay deterministically
const testCases = [];

function recordTestCase(input, state) {
  testCases.push({ input, state, timestamp: Date.now() });
}

function replayTestCase(testCase) {
  // Reset to recorded state
  setState(testCase.state);

  // Replay with recorded input
  return suspiciousFunction(testCase.input);
}

// When heisenbug appears, you have exact reproduction
```

## Post-Mortem Analysis

### Purpose

Learn from incidents to prevent recurrence and improve system reliability.

### Post-Mortem Template

```markdown
## Incident Post-Mortem: [Title]

**Date:** 2025-10-30
**Duration:** 2 hours 15 minutes
**Impact:** 15% of users unable to log in
**Severity:** High

### Timeline (all times UTC)

- 14:32: First error alerts triggered
- 14:35: On-call engineer paged
- 14:40: Investigation began
- 14:55: Root cause identified
- 15:10: Fix deployed to canary
- 15:25: Fix deployed to production
- 16:47: Issue fully resolved, monitoring normalized

### Root Cause

Database connection pool exhausted due to connections not being properly released after failed queries. When query threw exception, connection was leaked instead of returned to pool.

### Impact

- 15,000 users affected
- 2,300 failed login attempts
- $12,000 estimated revenue impact
- 45 support tickets created

### Detection

- Automated monitoring alert: "Error rate exceeded threshold"
- User reports via support
- Health check endpoint returning degraded status

### Resolution

Immediate fix: Restart application servers to reset connection pools
Proper fix: Add `finally` block to ensure connections always released

### What Went Well

- Monitoring detected issue within 3 minutes
- On-call response time under SLA (5 minutes)
- Communication to stakeholders clear and timely
- Rollback plan available if fix failed

### What Went Wrong

- Missing unit test for error case
- No automated alert for connection pool exhaustion
- Deployment went to production without sufficient staging testing
- Documentation unclear on connection handling

### Action Items

1. [P0] Add connection pool monitoring and alerts - Assigned: @devops - Due: 2025-11-06
2. [P0] Add unit test for query error handling - Assigned: @backend - Due: 2025-11-03
3. [P1] Review all database code for similar pattern - Assigned: @backend - Due: 2025-11-10
4. [P1] Add connection pool metrics to dashboard - Assigned: @devops - Due: 2025-11-13
5. [P2] Update connection handling documentation - Assigned: @tech-writer - Due: 2025-11-15
6. [P2] Improve staging environment to match production - Assigned: @devops - Due: 2025-11-30

### Lessons Learned

- Always use try-finally for resource cleanup
- Monitor not just errors but resource utilization
- Staging environment must match production configuration
- Error cases are as important as happy path for testing
```

## Related Documentation

- [Core Concepts](core-concepts.md): Foundation for advanced techniques
- [Patterns](patterns.md): Patterns applicable to advanced scenarios
- [Troubleshooting](troubleshooting.md): Apply advanced techniques to specific issues
