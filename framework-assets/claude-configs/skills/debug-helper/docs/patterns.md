# Debugging Patterns and Anti-Patterns

Common debugging patterns that accelerate problem resolution, and anti-patterns to avoid that waste time and create confusion.

## Table of Contents

- [Effective Patterns](#effective-patterns)
  - [Binary Search Debugging](#binary-search-debugging)
  - [Divide and Conquer](#divide-and-conquer)
  - [Rubber Duck Debugging](#rubber-duck-debugging)
  - [Wolf Fence Algorithm](#wolf-fence-algorithm)
  - [Time Travel with Version Control](#time-travel-with-version-control)
  - [Differential Debugging](#differential-debugging)
  - [Logging Sandwich](#logging-sandwich)
  - [State Machine Tracing](#state-machine-tracing)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
  - [Random Change Debugging](#random-change-debugging)
  - [Superstition-Based Debugging](#superstition-based-debugging)
  - [Stack Overflow Copy-Paste](#stack-overflow-copy-paste)
  - [Comment Out Until It Works](#comment-out-until-it-works)
  - [The Big Rewrite](#the-big-rewrite)

## Effective Patterns

### Binary Search Debugging

**Pattern:** When you know a feature worked before and is broken now, use binary search through code changes to find the breaking change.

**When to Use:**
- Bug appeared after recent changes
- You have version control history
- Cannot immediately identify breaking change
- Large number of commits to check

**How It Works:**

```bash
# Git bisect automates binary search
git bisect start
git bisect bad                    # Current version is broken
git bisect good v1.2.0            # This version worked

# Git checks out middle commit
# Test if bug exists at this point
npm test                          # Or manual test

# If bug exists:
git bisect bad

# If bug doesn't exist:
git bisect good

# Git continues binary search
# Eventually identifies first bad commit
```

**Manual Binary Search Example:**

```javascript
// Problem: Function returns wrong value, but worked before

// Step 1: Binary search through the function
function complexCalculation(data) {
  // First half of function
  const step1 = processDataStep1(data);
  console.log('After step 1:', step1); // ✓ Correct

  const step2 = processDataStep2(step1);
  console.log('After step 2:', step2); // ✗ Wrong!

  // Second half would be tested if first half was correct
  const step3 = processDataStep3(step2);
  const step4 = processDataStep4(step3);

  return finalizeResult(step4);
}

// Bug is in step2, narrow down further:
function processDataStep2(data) {
  const filtered = data.filter(item => item.active);
  console.log('After filter:', filtered); // ✓ Correct

  const mapped = filtered.map(item => item.value * 2);
  console.log('After map:', mapped); // ✗ Wrong!

  return mapped.reduce((sum, val) => sum + val, 0);
}

// Bug found: multiplication by 2 should be division by 2
// Root cause: Typo in recent commit
```

**Benefits:**
- Logarithmic time complexity: O(log n) vs O(n)
- Works even with many commits
- Systematic, no guessing

**Limitations:**
- Requires ability to test at different points
- Works best with atomic commits
- Slower if builds take long time

### Divide and Conquer

**Pattern:** Break complex system into parts, test each part in isolation to identify which part contains the bug.

**When to Use:**
- Bug in complex system with multiple components
- Unclear which layer has the issue
- Integration between components works sometimes

**Example: Full-Stack Issue**

```
Issue: User registration fails with no error message

System layers:
┌─────────────────┐
│   Frontend      │  React form submission
├─────────────────┤
│   API Layer     │  Express endpoint
├─────────────────┤
│   Business Logic│  Validation and processing
├─────────────────┤
│   Database      │  Postgres insert
└─────────────────┘

Strategy: Test each layer independently

Layer 1: Frontend
```javascript
// Test: Can form data be captured?
function handleSubmit(e) {
  e.preventDefault();
  console.log('Form data:', formData); // ✓ Data correct

  // Test: Does API call execute?
  console.log('Calling API...');
  const response = await registerUser(formData);
  console.log('API response:', response); // ✗ No response!
}
```

Layer 2: API Endpoint
```javascript
// Test API directly with curl, bypassing frontend
// curl -X POST http://localhost:3000/api/register \
//   -H "Content-Type: application/json" \
//   -d '{"email":"test@example.com","password":"test123"}'

app.post('/api/register', async (req, res) => {
  console.log('API endpoint hit'); // ✗ Not logging!
  // Conclusion: Request not reaching endpoint
});
```

Layer 2.5: Network/CORS
```javascript
// Test: Check browser console for CORS errors
// Found: "CORS policy: No 'Access-Control-Allow-Origin' header"

// Test: Check network tab
// Found: Request shows as "CORS error"

// ROOT CAUSE: Missing CORS configuration on API
// FIX: Add CORS middleware
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
```

**Benefits:**
- Systematically narrows down issue
- Can test each layer independently
- Identifies integration issues vs layer issues

### Rubber Duck Debugging

**Pattern:** Explain your code and problem out loud (to a rubber duck, colleague, or written doc) to discover the issue through the explanation process.

**When to Use:**
- Stuck after trying multiple approaches
- Complex logic that's hard to reason about
- Intermittent bugs that don't make sense
- Need fresh perspective

**Why It Works:**
- Verbalizing forces clear thinking
- Explaining reveals assumptions
- Questions from "duck" (listener) highlight gaps
- Teaching mode activates different brain processes

**Example:**

```javascript
// Bug: Sum function returns NaN sometimes

function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Rubber duck explanation:
// "Okay duck, I have this function that calculates a total.
//  It takes an array of items and uses reduce.
//  The reducer adds each item's price to the sum...
//
//  Wait, what if item.price is undefined?
//  Or what if it's a string like '$19.99' instead of a number?
//  Let me check the data..."

console.log('Sample item:', items[0]);
// { name: 'Widget', price: '$19.99' } // ← AHA! Price is string!

// ROOT CAUSE: Prices are strings from database
// FIX: Parse prices as numbers
function calculateTotal(items) {
  return items.reduce((sum, item) => {
    const price = parseFloat(item.price.replace('$', ''));
    return sum + price;
  }, 0);
}
```

**Variations:**
- Write issue in bug ticket (explaining to future reader)
- Post on Stack Overflow (explaining to strangers)
- Create minimal reproduction (explaining to yourself)
- Code comments (explaining to future self)

### Wolf Fence Algorithm

**Pattern:** "There's one wolf in Alaska; how do you find it? First build a fence down the middle of the state, wait for the wolf to howl, determine which side of the fence it is on, then repeat the process on that side only, until you get to the point where you can see the wolf."

**When to Use:**
- Large codebase, unknown location of bug
- No clear starting point for investigation
- Intermittent issues that are hard to catch

**Example: Memory Leak in Large App**

```javascript
// Problem: Memory grows over time, but app has 50+ components

// Step 1: Fence the app in half
// Disable half of features, test if leak persists
const FEATURES = {
  dashboard: true,
  reporting: true,
  userManagement: true,
  settings: false,    // Disabled half
  notifications: false,
  analytics: false
};

// Test: Memory still leaking = bug in enabled half

// Step 2: Narrow down enabled half
const FEATURES = {
  dashboard: true,
  reporting: false,   // Narrow further
  userManagement: false,
  settings: false,
  notifications: false,
  analytics: false
};

// Test: Leak gone = bug in reporting or userManagement

// Step 3: Test just reporting
const FEATURES = {
  dashboard: false,
  reporting: true,    // Isolate
  userManagement: false,
  settings: false,
  notifications: false,
  analytics: false
};

// Test: Leak present = bug in reporting module

// Step 4: Binary search within reporting module
// Eventually find: WebSocket connection not cleaned up on unmount
```

### Time Travel with Version Control

**Pattern:** Use git to navigate to different points in time to understand when and how bug was introduced.

**When to Use:**
- Regression (worked before, broken now)
- Need to understand context of change
- Want to test fix against old version

**Commands:**

```bash
# See file as it was in specific commit
git show abc123:src/utils/helper.js

# Checkout old version temporarily
git checkout v1.2.0
npm install && npm test

# Return to current
git checkout main

# Compare current with old
git diff v1.2.0..HEAD -- src/

# See who changed specific lines
git blame -L 42,50 src/utils/helper.js

# See commits that touched file
git log --follow -- src/utils/helper.js

# Find commits that mentioned "authentication"
git log --grep="authentication" --oneline
```

**Example Investigation:**

```bash
# Issue: Login broken in current version
# Strategy: Find when it broke

# Step 1: Verify it was working before
git checkout v2.0.0
npm test  # Auth tests pass ✓

# Step 2: Verify it's broken now
git checkout main
npm test  # Auth tests fail ✗

# Step 3: Binary search between v2.0.0 and main
git bisect start
git bisect bad main
git bisect good v2.0.0
# ... bisect process identifies commit def456

# Step 4: Examine the breaking commit
git show def456
# Shows: JWT verification changed from 'HS256' to 'RS256'
# But private key not updated!

# Root cause found through time travel
```

### Differential Debugging

**Pattern:** Compare two similar scenarios - one that works and one that doesn't - to identify the difference causing the issue.

**When to Use:**
- Bug occurs in one environment but not another
- Works for some users but not others
- Works with some data but not other data

**Example: Works in Dev, Fails in Prod**

```javascript
// Symptom: File upload works in dev, fails in prod

// Strategy: Compare environments systematically

// Development (works):
Environment:
  NODE_ENV: development
  MAX_FILE_SIZE: 10485760 (10MB)
  TEMP_DIR: /tmp
  STORAGE: local filesystem

// Production (fails):
Environment:
  NODE_ENV: production
  MAX_FILE_SIZE: 1048576 (1MB) ← DIFFERENCE!
  TEMP_DIR: /app/tmp
  STORAGE: S3

// Test hypothesis: File size limit difference
// Upload 500KB file in prod: ✓ Works
// Upload 2MB file in prod: ✗ Fails
// ROOT CAUSE: Production has 1MB limit, dev has 10MB

// Fix: Update production config or add client-side validation
```

### Logging Sandwich

**Pattern:** Wrap suspicious code with detailed logging before and after to trace execution flow and state changes.

**When to Use:**
- Code executes but produces wrong result
- Need to trace execution path
- State changes unexpectedly
- Async operations timing unclear

**Example:**

```javascript
// Problem: Order total calculation wrong

// Wrap with logging sandwich
async function calculateOrderTotal(orderId) {
  // TOP BUN: Log inputs and initial state
  console.log('=== Calculate Total START ===');
  console.log('Order ID:', orderId);
  console.log('Timestamp:', new Date().toISOString());

  const order = await getOrder(orderId);

  // FILLING: Log intermediate states
  console.log('Order retrieved:', {
    items: order.items.length,
    subtotal: order.subtotal,
    discounts: order.discounts
  });

  let total = order.subtotal;
  console.log('Starting total:', total);

  // Apply discounts
  for (const discount of order.discounts) {
    console.log('Applying discount:', discount);
    total -= discount.amount;
    console.log('Total after discount:', total);
  }

  // Add tax
  const tax = total * TAX_RATE;
  console.log('Tax calculated:', tax, 'at rate', TAX_RATE);
  total += tax;

  // BOTTOM BUN: Log final state and output
  console.log('Final total:', total);
  console.log('=== Calculate Total END ===');

  return total;
}

// Output reveals: Discount applied twice!
// Logging sandwich caught the duplicate application
```

## Anti-Patterns to Avoid

### Random Change Debugging

**Anti-Pattern:** Making random code changes hoping something will fix the issue without understanding the root cause.

**Why It's Bad:**
- Wastes enormous amounts of time
- May accidentally "fix" by breaking something else
- Doesn't build understanding
- Creates technical debt
- May introduce new bugs

**Example:**

```javascript
// BAD: Trying random things
async function loadUserData() {
  // Try 1: Add await?
  await fetch('/api/user');

  // Try 2: Change timeout?
  fetch('/api/user', { timeout: 5000 });

  // Try 3: Try-catch?
  try {
    await fetch('/api/user');
  } catch(e) {}

  // Try 4: Different method?
  axios.get('/api/user');

  // None of these address root cause!
}

// GOOD: Understand first
async function loadUserData() {
  console.log('Fetching user data...');

  try {
    const response = await fetch('/api/user');

    // Check what's actually failing
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('Data received:', data);

    return data;

  } catch (error) {
    // Now we understand the actual error
    console.error('Fetch failed:', error.message);
    throw error;
  }
}
```

### Superstition-Based Debugging

**Anti-Pattern:** Believing certain actions fix issues without evidence, cargo-cult programming.

**Examples:**
```javascript
// "Adding delays always fixes race conditions"
await sleep(1000); // Hope this is enough?

// "Restarting the server fixes everything"
// (Without understanding why)

// "It works when I clear cache"
// (Without investigating why cache causes issues)

// "This magic comment makes it work"
// eslint-disable-next-line
const data = processData(); // No idea why this matters
```

**Why It's Bad:**
- Masks real issues
- Solutions are fragile and break unexpectedly
- Doesn't prevent recurrence
- Accumulates technical debt
- Wastes time on rituals instead of fixes

**GOOD: Understand the Why**

```javascript
// BAD: Superstitious delay
async function fetchData() {
  const data = await api.getData();
  await sleep(1000); // "Fixes" race condition?
  processData(data);
}

// GOOD: Understand and fix race condition
async function fetchData() {
  const data = await api.getData();

  // Wait for dependent operation to complete
  await ensureDependencyReady();

  // Now safe to process
  processData(data);
}

// EVEN BETTER: Fix architecture to eliminate race
async function fetchData() {
  // Use proper state management instead of racing
  const [data, dependency] = await Promise.all([
    api.getData(),
    getDependency()
  ]);

  processData(data, dependency);
}
```

### Stack Overflow Copy-Paste

**Anti-Pattern:** Copying code from Stack Overflow without understanding it, hoping it solves the problem.

**Why It's Bad:**
- May not address your specific issue
- Can introduce security vulnerabilities
- Creates code you can't maintain
- Might be outdated or wrong
- Doesn't build your skills

**Example:**

```javascript
// BAD: Copy-paste without understanding
// Problem: Need to deep clone object
// *searches Stack Overflow*
// *copies first answer*

const cloned = JSON.parse(JSON.stringify(obj));

// Problems with this:
// - Loses functions
// - Loses undefined values
// - Loses Date objects
// - Circular references throw error
// - You don't know when it breaks

// GOOD: Understand requirements first
// Q: What types of data does obj contain?
// Q: Does it have functions or only data?
// Q: Can it have circular references?
// Q: What's the performance requirement?

// Then choose appropriate solution:
// Simple data object? JSON parse/stringify fine
// Contains functions? Use structured clone or library
// Circular refs? Use library like lodash cloneDeep

// Learn WHY each solution works and when to use it
```

### Comment Out Until It Works

**Anti-Pattern:** Commenting out code until errors stop, without understanding what each piece does.

**Why It's Bad:**
- Removes potentially important code
- Doesn't fix root cause
- Creates incomplete functionality
- Difficult to recover later

**Example:**

```javascript
// BAD: Commenting out until it works
async function updateUser(userId, updates) {
  const user = await getUser(userId);

  // Validation causing errors? Comment it out!
  // if (!isValid(updates)) {
  //   throw new Error('Invalid updates');
  // }

  // This causing problems? Remove it!
  // await checkPermissions(userId);

  // Just update and hope for the best
  await db.update(userId, updates);
}

// GOOD: Understand why each line exists
async function updateUser(userId, updates) {
  const user = await getUser(userId);

  // Validation failing? Fix the validation logic
  if (!isValid(updates)) {
    console.log('Validation failed:', updates);
    // Debug WHY validation fails
    throw new Error('Invalid updates');
  }

  // Permissions failing? Fix permission logic
  const hasPermission = await checkPermissions(userId);
  if (!hasPermission) {
    // Debug permission system
    throw new Error('No permission');
  }

  await db.update(userId, updates);
}
```

### The Big Rewrite

**Anti-Pattern:** When debugging seems hard, rewrite everything from scratch "the right way."

**Why It's Bad:**
- Loses tribal knowledge embedded in existing code
- Takes much longer than expected
- Often recreates same bugs plus new ones
- Disrupts ongoing work
- May not address actual problem

**When Rewrite Might Be Justified:**
- Code is truly unsalvageable (rare)
- Technology is obsolete
- Business requirements changed fundamentally
- Cost of maintenance > cost of rewrite

**Usually Better:**
```javascript
// Instead of full rewrite:
// 1. Identify specific problematic areas
// 2. Refactor incrementally
// 3. Add tests as you go
// 4. Improve gradually

// NOT: "Throw it all away and start over"
// YES: "Refactor this module, add tests, improve next module"
```

## Pattern Selection Guide

```
Your Situation                     → Recommended Pattern
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Worked before, broken now          → Binary Search / Time Travel
Large codebase, unknown location   → Wolf Fence / Divide and Conquer
Complex logic, stuck               → Rubber Duck
Works in dev, fails in prod        → Differential Debugging
Wrong output, unclear why          → Logging Sandwich
Intermittent bug                   → State Machine Tracing
```

## Related Documentation

- [Core Concepts](core-concepts.md): Understand principles behind patterns
- [Best Practices](best-practices.md): Apply patterns systematically
- [Advanced Topics](advanced-topics.md): Complex pattern applications
- [Examples](../examples/): See patterns in action
