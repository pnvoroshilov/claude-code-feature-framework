# Core Debugging Concepts

This document covers fundamental debugging principles, mental models, and core concepts that form the foundation of effective problem-solving in software development.

## Table of Contents

- [The Scientific Method in Debugging](#the-scientific-method-in-debugging)
- [Hypothesis-Driven Investigation](#hypothesis-driven-investigation)
- [System Mental Models](#system-mental-models)
- [State and State Transitions](#state-and-state-transitions)
- [Error Propagation](#error-propagation)
- [Causality and Correlation](#causality-and-correlation)
- [Observability and Instrumentation](#observability-and-instrumentation)
- [Reproducibility](#reproducibility)
- [Isolation and Simplification](#isolation-and-simplification)
- [Debugging Mindset](#debugging-mindset)
- [Information Gathering](#information-gathering)
- [Time Travel and History](#time-travel-and-history)

## The Scientific Method in Debugging

### What It Is

Debugging is fundamentally the application of the scientific method to software problems. Just as scientists test hypotheses about natural phenomena, developers test hypotheses about why code behaves unexpectedly.

### The Process

1. **Observation**: Notice unexpected behavior or error
2. **Question**: What is causing this behavior?
3. **Hypothesis**: Form educated guesses about the cause
4. **Prediction**: If hypothesis X is true, then Y should happen
5. **Test**: Run experiments to validate predictions
6. **Analysis**: Evaluate test results
7. **Conclusion**: Confirm or reject hypothesis
8. **Iteration**: Refine hypothesis if rejected

### Why It Matters

Random debugging (changing things and hoping they work) wastes time and can introduce new bugs. A systematic scientific approach:
- Reduces time to resolution by 60-80%
- Ensures you understand the root cause
- Prevents similar bugs in the future
- Builds debugging skill through structured learning

### Examples

**Bad Approach (Random Debugging):**
```javascript
// Error: User data not saving
// Random changes without understanding:
async function saveUser(user) {
  // Try adding await? Maybe that's it?
  await db.save(user);

  // Try adding error handling? Maybe that helps?
  try {
    await db.save(user);
  } catch (e) {
    console.log(e);
  }

  // Try changing the method? Who knows...
  await db.insert(user);
}
```

**Good Approach (Scientific Method):**
```javascript
// OBSERVATION: User data not saving to database

// HYPOTHESIS 1: Database connection failing
// Test: Check if connection is established
console.log('DB connected:', db.isConnected());

// HYPOTHESIS 2: user object missing required fields
// Test: Validate user object structure
console.log('User object:', JSON.stringify(user));
console.log('Required fields present:',
  user.hasOwnProperty('email') && user.hasOwnProperty('name'));

// HYPOTHESIS 3: Async timing issue - function returns before save completes
// Test: Add await and verify completion
async function saveUser(user) {
  console.log('Before save');
  const result = await db.save(user);
  console.log('After save, result:', result);
  return result;
}

// ANALYSIS: Console shows function returning before await
// CONCLUSION: Missing await keyword in calling code
// FIX: Ensure caller uses await
```

### Common Mistakes

1. **Changing multiple things at once**: Can't tell which change fixed it
2. **Not recording results**: Forget what you've already tried
3. **Skipping hypothesis formation**: No clear direction for investigation
4. **Not validating assumptions**: Build tests on faulty foundations

## Hypothesis-Driven Investigation

### What It Is

A structured approach where you generate ranked hypotheses about potential causes, then systematically test them from most to least likely.

### How It Works

1. **Generate hypotheses** based on:
   - Error messages and stack traces
   - Recent code changes
   - Common bug patterns
   - System architecture knowledge

2. **Rank by probability**:
   - Most likely causes first
   - Consider Occam's Razor (simplest explanation)
   - Use past experience with similar issues

3. **Design tests** that can prove/disprove each hypothesis:
   - Quick tests first (high information, low effort)
   - Binary tests when possible (yes/no answers)
   - Isolate variables in each test

4. **Execute and evaluate**:
   - Run tests in priority order
   - Document results
   - Update hypothesis rankings based on findings

### Example: API Endpoint Returns 500 Error

```
OBSERVATIONS:
- Endpoint /api/users/:id returns 500
- Works in development, fails in production
- Started after deployment 2 hours ago
- Error log shows "TypeError: Cannot read property 'name' of null"

HYPOTHESES (ranked):

1. [85% probability] Database user record not found, code doesn't handle null
   - Prediction: Error occurs when userId doesn't exist in production DB
   - Test: Call endpoint with known valid ID vs invalid ID
   - Quick test: Check if new users (created in last 2 hours) work

2. [10% probability] Environment variable missing/different in production
   - Prediction: Code relies on env var that's not set in prod
   - Test: Log all env vars in endpoint handler
   - Quick test: Compare .env files dev vs prod

3. [5% probability] Database connection intermittent in production
   - Prediction: Query sometimes returns null due to connection issues
   - Test: Add connection health logging before query
   - Quick test: Check database monitoring dashboard

TESTING HYPOTHESIS 1:
```javascript
// Add defensive logging
app.get('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  console.log('Fetching user:', userId);

  const user = await db.users.findById(userId);
  console.log('User found:', user !== null);

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  // This line crashes if user is null
  const name = user.name; // TypeError here!
  res.json({ name });
});
```

RESULT: Logs show user is null for certain IDs
ROOT CAUSE: Production database missing some user records that exist in dev
FIX: Add null check and return 404 for missing users
```

## System Mental Models

### What It Is

A mental representation of how the system works - data flow, component interactions, state changes, and execution order. Accurate mental models are crucial for predicting behavior and identifying issues.

### Building Mental Models

1. **Architecture diagram**: Draw components and connections
2. **Data flow**: Trace how data moves through system
3. **Execution order**: Understand async operations and timing
4. **State locations**: Know where state is stored and managed
5. **External dependencies**: Map integrations and third-party services

### Example: React Application Mental Model

```
USER INTERACTION
     ↓
EVENT HANDLER (onClick)
     ↓
DISPATCH ACTION (Redux/Context)
     ↓
REDUCER (State Update)
     ↓
STORE NOTIFICATION
     ↓
COMPONENT RE-RENDER (if subscribed)
     ↓
VIRTUAL DOM DIFF
     ↓
REAL DOM UPDATE
     ↓
BROWSER REPAINT
```

**Using This Model to Debug:**

Problem: "Button click doesn't update UI"

Mental model helps narrow down where breakdown occurs:
1. Is event handler firing? (Add console.log in onClick)
2. Is action dispatched? (Check Redux DevTools)
3. Does reducer update state? (Log reducer input/output)
4. Is component subscribed? (Check useSelector/connect)
5. Does component re-render? (React DevTools profiler)
6. Is DOM actually updated? (Browser inspect element)

Each step maps to a specific part of the mental model, making debugging systematic rather than random.

### Common Mental Model Mistakes

```javascript
// WRONG MENTAL MODEL: setState is synchronous
function handleClick() {
  setState({ count: count + 1 });
  console.log(count); // Expects new value immediately - WRONG!
}

// CORRECT MENTAL MODEL: setState is asynchronous
function handleClick() {
  setState({ count: count + 1 });
  // State update scheduled, not immediate
  // Console will log old value

  // To use new value, use useEffect or callback
  setState(prev => {
    const newCount = prev.count + 1;
    console.log(newCount); // Correct approach
    return { count: newCount };
  });
}
```

## State and State Transitions

### What It Is

State represents the current condition of your application at a specific point in time. State transitions are the changes from one state to another. Many bugs occur when state transitions don't happen as expected or when state becomes inconsistent.

### Types of State

1. **Application State**: Global app data (Redux, Context)
2. **Component State**: Local component data (useState, this.state)
3. **Server State**: Data from backend (cached queries)
4. **URL State**: Route parameters and query strings
5. **Form State**: Input values and validation
6. **UI State**: Loading, error, success states

### State Debugging Strategies

**1. State Inspection**
```javascript
// Add state logging to track changes
useEffect(() => {
  console.log('State changed:', state);
}, [state]);

// Use Redux DevTools for time-travel debugging
// Browser DevTools: React components tab
```

**2. State Transition Tracking**
```javascript
// Log state before and after updates
function updateUser(newData) {
  console.log('Before update:', currentUser);
  const updated = { ...currentUser, ...newData };
  console.log('After update:', updated);
  setUser(updated);
}
```

**3. State Consistency Validation**
```javascript
// Assert expected state properties
function processOrder(order) {
  if (!order.items || order.items.length === 0) {
    throw new Error('Invalid state: Order has no items');
  }

  if (order.total !== calculateTotal(order.items)) {
    console.error('State inconsistency detected:');
    console.error('Order total:', order.total);
    console.error('Calculated total:', calculateTotal(order.items));
    throw new Error('Order total does not match item sum');
  }

  // Process order...
}
```

### Example: Debugging State Mutation

```javascript
// BUG: State appears to update but UI doesn't change

// WRONG: Direct mutation (doesn't trigger re-render)
function addItem(item) {
  state.items.push(item); // Mutation - React doesn't detect change
  setState(state); // Same reference, no re-render triggered
}

// CORRECT: Create new reference
function addItem(item) {
  setState({
    ...state,
    items: [...state.items, item] // New array reference
  });
}

// DEBUGGING TECHNIQUE: Check reference equality
function addItem(item) {
  const oldItems = state.items;

  // Wrong approach
  state.items.push(item);
  setState(state);

  // Debug check
  console.log('Same reference?', oldItems === state.items); // true = BUG!
  // React uses reference equality to detect changes
  // Same reference = no re-render
}
```

## Error Propagation

### What It Is

Understanding how errors flow through your system - where they originate, how they propagate, and where they're caught (or not caught). Many bugs are actually error handling failures.

### Error Flow Layers

```
1. ERROR ORIGIN (lowest level)
   - Database query fails
   - Network request times out
   - File not found
   - Invalid input

2. ERROR DETECTION
   - Try-catch blocks
   - Error callbacks
   - Promise .catch()
   - Error boundaries (React)

3. ERROR HANDLING
   - Retry logic
   - Fallback values
   - User notification
   - Logging/monitoring

4. ERROR RECOVERY
   - Graceful degradation
   - Alternative flows
   - State cleanup
   - User guidance
```

### Debugging Error Propagation

**Example: Silent Failure**

```javascript
// BAD: Error swallowed silently
async function loadUserData() {
  try {
    const response = await fetch('/api/user');
    const data = await response.json();
    setUser(data);
  } catch (error) {
    // Error caught but ignored - SILENT FAILURE
    console.log('Error loading user');
  }
}

// RESULT: UI shows no data, no error message, user confused
// DEBUGGING: Check console for log, but no indication of what went wrong
```

**Good: Proper Error Handling**

```javascript
async function loadUserData() {
  try {
    const response = await fetch('/api/user');

    // Check HTTP status
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    setUser(data);
    setError(null);

  } catch (error) {
    // Log full error details
    console.error('Failed to load user:', error);

    // Set error state for UI
    setError('Unable to load user data. Please try again.');

    // Optional: Report to monitoring service
    reportError(error, { context: 'loadUserData' });

    // Optional: Retry logic
    if (retryCount < 3) {
      setTimeout(() => loadUserData(), 1000 * retryCount);
    }
  }
}

// DEBUGGING: Clear error message, detailed logs, error state visible
```

### Tracing Error Origins

```javascript
// Add context to errors as they propagate
class DatabaseError extends Error {
  constructor(message, query, params) {
    super(message);
    this.name = 'DatabaseError';
    this.query = query;
    this.params = params;
    this.timestamp = new Date().toISOString();
  }
}

async function executeQuery(sql, params) {
  try {
    return await db.query(sql, params);
  } catch (error) {
    // Enrich error with context
    throw new DatabaseError(
      error.message,
      sql,
      params
    );
  }
}

// Higher level
async function getUser(userId) {
  try {
    return await executeQuery(
      'SELECT * FROM users WHERE id = ?',
      [userId]
    );
  } catch (error) {
    if (error instanceof DatabaseError) {
      // Have full context: query, params, original error
      console.error('DB Error Details:', {
        query: error.query,
        params: error.params,
        originalError: error.message
      });
    }
    throw error; // Propagate with context preserved
  }
}
```

## Causality and Correlation

### What It Is

Understanding the difference between causation (A directly causes B) and correlation (A and B happen together, but one doesn't cause the other). Confusing these leads to fixing symptoms instead of root causes.

### Distinguishing Causation from Correlation

**Correlation Does NOT Imply Causation**

```
OBSERVATION: App crashes when user count exceeds 1000

CORRELATION: High user count and crashes occur together

CAUSATION INVESTIGATION:
- Does adding users CAUSE crashes? (Test by adding users)
- Or does something else cause both? (Time of day? Server load?)
- Or is timing coincidental? (Deployment happened at same time?)

ACTUAL ROOT CAUSE: Memory leak that takes time to manifest
- More users → more memory usage → faster leak manifestation
- User count correlates with crashes but doesn't cause them
- Real cause: Unclosed database connections accumulate over time
```

### Testing Causality

```javascript
// HYPOTHESIS: Feature X causes memory leak

// TEST 1: Isolate the feature
// Create test with ONLY feature X active, nothing else
function testFeatureX() {
  // Start with clean state
  resetApp();

  // Take baseline measurement
  const baseline = measureMemory();

  // Exercise ONLY feature X
  for (let i = 0; i < 100; i++) {
    useFeatureX();
  }

  // Measure again
  const afterTest = measureMemory();

  // Compare
  if (afterTest - baseline > THRESHOLD) {
    console.log('Feature X CAUSES memory leak');
  } else {
    console.log('Feature X does NOT cause memory leak');
  }
}

// TEST 2: Remove feature and verify leak disappears
function testWithoutFeatureX() {
  // Disable feature X
  FEATURE_X_ENABLED = false;

  // Run normal app usage
  simulateNormalUsage();

  // Check memory
  // If leak still occurs, feature X was correlated but not causal
}
```

### Example: Spurious Correlation

```javascript
// OBSERVATION: App crashes every Friday afternoon

// WRONG ASSUMPTION: "Something about Fridays causes crashes"
// (Correlation without investigation)

// INVESTIGATION:
// - What happens on Fridays? Weekly data export job runs
// - What does export job do? Queries all user records
// - What's different about data on Fridays? Week's worth accumulated
// - Actual cause: Query timeout on large dataset

// ROOT CAUSE: Not Friday itself, but data volume growth
// FIX: Optimize query, add indexes, implement pagination
```

## Observability and Instrumentation

### What It Is

The ability to understand internal system state by examining external outputs. Without proper observability, debugging is like trying to fix a car with the hood welded shut.

### Three Pillars of Observability

1. **Logs**: Discrete event records
2. **Metrics**: Aggregated measurements over time
3. **Traces**: Request flow through distributed systems

### Strategic Logging for Debugging

```javascript
// BAD: Uninformative logging
function processPayment(payment) {
  console.log('Processing payment');
  // ... complex logic ...
  console.log('Done');
}

// GOOD: Structured, contextual logging
function processPayment(payment) {
  const correlationId = generateId();

  logger.info('Payment processing started', {
    correlationId,
    paymentId: payment.id,
    amount: payment.amount,
    currency: payment.currency,
    userId: payment.userId,
    timestamp: Date.now()
  });

  try {
    // Step 1
    logger.debug('Validating payment', { correlationId });
    validatePayment(payment);

    // Step 2
    logger.debug('Charging payment method', {
      correlationId,
      method: payment.method
    });
    const result = await chargePaymentMethod(payment);

    // Step 3
    logger.debug('Updating order status', { correlationId });
    await updateOrderStatus(payment.orderId, 'paid');

    logger.info('Payment processing completed', {
      correlationId,
      duration: Date.now() - startTime,
      result: 'success'
    });

    return result;

  } catch (error) {
    logger.error('Payment processing failed', {
      correlationId,
      error: error.message,
      stack: error.stack,
      payment: payment
    });
    throw error;
  }
}
```

### Adding Observability to Existing Code

```javascript
// BEFORE: Black box function
function calculateDiscount(cart) {
  let discount = 0;
  for (const item of cart.items) {
    if (item.promotional) {
      discount += item.price * 0.1;
    }
  }
  return discount;
}

// AFTER: Observable function
function calculateDiscount(cart) {
  const context = { cartId: cart.id, itemCount: cart.items.length };

  let discount = 0;
  const promoItems = [];

  for (const item of cart.items) {
    if (item.promotional) {
      const itemDiscount = item.price * 0.1;
      discount += itemDiscount;
      promoItems.push({
        id: item.id,
        discount: itemDiscount
      });
    }
  }

  logger.debug('Discount calculated', {
    ...context,
    totalDiscount: discount,
    promoItemsCount: promoItems.length,
    promoItems
  });

  return discount;
}

// NOW WHEN DEBUGGING: Can see exactly which items contributed to discount
```

## Related Concepts

- [Best Practices](best-practices.md): Apply these concepts systematically
- [Patterns](patterns.md): Common debugging patterns using these concepts
- [Advanced Topics](advanced-topics.md): Deep dive into complex scenarios
- [Troubleshooting](troubleshooting.md): Apply concepts to specific problems
