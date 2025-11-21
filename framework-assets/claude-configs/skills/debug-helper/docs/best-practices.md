# Debugging Best Practices

Industry-standard approaches and proven methodologies for effective debugging across all types of software issues.

## Table of Contents

- [Reproduce First, Fix Later](#reproduce-first-fix-later)
- [Systematic Over Random](#systematic-over-random)
- [Understand Before Changing](#understand-before-changing)
- [Change One Thing at a Time](#change-one-thing-at-a-time)
- [Document Your Investigation](#document-your-investigation)
- [Use Version Control Effectively](#use-version-control-effectively)
- [Leverage Debugging Tools](#leverage-debugging-tools)
- [Read Error Messages Carefully](#read-error-messages-carefully)
- [Check Your Assumptions](#check-your-assumptions)
- [Know When to Ask for Help](#know-when-to-ask-for-help)
- [Prevent Future Issues](#prevent-future-issues)
- [Time-Box Your Investigation](#time-box-your-investigation)

## Reproduce First, Fix Later

### Principle

Never attempt to fix a bug you cannot reliably reproduce. Reproduction is the foundation of effective debugging.

### Why It Matters

Without reliable reproduction:
- Cannot verify if your fix actually works
- Cannot write regression tests
- May be fixing a different issue than the reported one
- Waste time on random changes

### How to Apply

**Step 1: Document Reproduction Steps**

```markdown
## Reproduction Steps

Environment:
- Browser: Chrome 118
- OS: MacOS 13.6
- User account: test@example.com
- Time: Peak hours (2-4 PM EST)

Steps:
1. Log in as standard user
2. Navigate to /dashboard
3. Click "Export Data" button
4. Select date range > 90 days
5. Click "Download"

Expected: CSV file downloads
Actual: 500 error, no download

Frequency: 100% reproducible with steps above
```

**Step 2: Create Minimal Reproduction**

```javascript
// Original complex scenario (hard to debug)
// Multiple features, state, user interactions

// Minimal reproduction (isolated issue)
test('Export fails for date ranges > 90 days', async () => {
  const user = createTestUser();
  const startDate = '2025-01-01';
  const endDate = '2025-10-31'; // 304 days

  const response = await request
    .post('/api/export')
    .send({ userId: user.id, startDate, endDate });

  expect(response.status).toBe(200); // FAILS with 500
});
```

**Step 3: Verify Consistency**

```javascript
// Run reproduction multiple times
for (let i = 0; i < 10; i++) {
  const result = await reproduceIssue();
  console.log(`Attempt ${i + 1}: ${result.success ? 'PASS' : 'FAIL'}`);
}

// 10/10 failures = reliable reproduction
// 5/10 failures = intermittent (need more investigation)
// 0/10 failures = cannot reproduce (environment difference?)
```

### Good Example

```javascript
// GOOD: Reliable reproduction before fixing
describe('Bug #1234: Cart total incorrect', () => {
  it('reproduces the issue', () => {
    const cart = createCart();
    cart.addItem({ price: 10.00, quantity: 2 });
    cart.addItem({ price: 5.50, quantity: 3 });

    const total = cart.calculateTotal();

    // Expected: 10.00 * 2 + 5.50 * 3 = 36.50
    // Actual: 35.50 (BUG REPRODUCED)
    expect(total).toBe(36.50);
  });

  // Now we can confidently fix, knowing we can verify
});
```

### Bad Example

```javascript
// BAD: Attempting fix without reproduction
// User reports: "sometimes cart total is wrong"

// Random changes without understanding:
function calculateTotal() {
  // Maybe rounding? Let's try toFixed...
  return items.reduce((sum, item) =>
    sum + (item.price * item.quantity).toFixed(2), 0
  );
}

// Problem: Cannot verify fix works because cannot reproduce
```

## Systematic Over Random

### Principle

Follow a systematic debugging process rather than randomly changing code and hoping something works.

### Why It Matters

Random debugging:
- Takes 3-5x longer to resolve issues
- Often fixes symptoms, not root causes
- Can introduce new bugs
- Doesn't build debugging skills
- Wastes team time

Systematic debugging:
- Consistently faster resolution
- Identifies root causes
- Builds transferable knowledge
- Enables prevention strategies

### Systematic Debugging Process

```
1. GATHER INFORMATION
   ↓
2. FORM HYPOTHESES (ranked by probability)
   ↓
3. DESIGN TESTS (binary tests when possible)
   ↓
4. EXECUTE TESTS (highest probability first)
   ↓
5. ANALYZE RESULTS
   ↓
6. REFINE HYPOTHESES
   ↓
7. REPEAT until root cause found
   ↓
8. IMPLEMENT FIX
   ↓
9. VERIFY FIX
   ↓
10. PREVENT RECURRENCE
```

### Example: Systematic Approach

```javascript
// ISSUE: API endpoint returns stale data after update

// STEP 1: GATHER INFORMATION
/*
- Endpoint: PUT /api/users/:id
- Behavior: Update appears to succeed (200 OK)
- Follow-up GET returns old data
- Database shows new data correctly
- Only happens with certain fields
*/

// STEP 2: HYPOTHESES (ranked)
/*
1. [70%] Cache not invalidated after update
2. [20%] GET reading from read replica with lag
3. [10%] Client caching response
*/

// STEP 3: TEST HYPOTHESIS 1 - Cache issue
// Check if cached response is being returned
app.put('/api/users/:id', async (req, res) => {
  const userId = req.params.id;

  // Update database
  await db.users.update(userId, req.body);

  // Check cache
  const cached = await cache.get(`user:${userId}`);
  console.log('Cache after update:', cached); // Shows old data!

  // HYPOTHESIS 1 CONFIRMED: Cache not invalidated
});

// STEP 4: FIX
app.put('/api/users/:id', async (req, res) => {
  const userId = req.params.id;

  await db.users.update(userId, req.body);

  // Invalidate cache
  await cache.del(`user:${userId}`);

  res.json({ success: true });
});

// STEP 5: VERIFY
/*
- Manual test: Update user, GET shows new data ✓
- Automated test: Added regression test ✓
- Monitor: No stale data reports after deployment ✓
*/
```

## Understand Before Changing

### Principle

Fully understand why the bug occurs before attempting a fix. Premature fixing leads to symptom treatment rather than root cause resolution.

### Why It Matters

Fixing without understanding:
- Often fixes symptoms, leaving root cause
- May create new bugs
- Prevents learning and skill development
- Wastes time on ineffective solutions

### How to Apply

**Ask These Questions Before Fixing:**

1. **What is the root cause?** (Not just the symptom)
2. **Why does the root cause exist?** (Design flaw, logic error, missing validation?)
3. **What is the failure mode?** (How does it manifest?)
4. **What are the side effects?** (What else might break?)
5. **Is this the only place it can occur?** (Similar issues elsewhere?)

### Example: Understanding vs Fixing

```javascript
// SYMPTOM: Users can delete other users' posts

// BAD: Quick fix without understanding
app.delete('/api/posts/:id', async (req, res) => {
  const postId = req.params.id;

  // Just add auth check, ship it
  if (!req.user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  await db.posts.delete(postId);
  res.json({ success: true });
});

// PROBLEM: Still broken! Any logged-in user can delete any post

// GOOD: Understand the requirement first
/*
UNDERSTANDING:
- Q: Who should be able to delete posts?
  A: Only post author OR admin users

- Q: How do we identify post author?
  A: posts.authorId matches req.user.id

- Q: How do we identify admins?
  A: users.role === 'admin'

- Q: What about posts without authors? (system posts)
  A: Only admins can delete system posts

ROOT CAUSE: No authorization check (authN vs authZ issue)
DESIGN: Need to verify user owns resource OR has admin privilege
*/

// PROPER FIX based on understanding
app.delete('/api/posts/:id', async (req, res) => {
  const postId = req.params.id;
  const userId = req.user.id;

  // Fetch post to check ownership
  const post = await db.posts.findById(postId);

  if (!post) {
    return res.status(404).json({ error: 'Post not found' });
  }

  // Authorization logic based on understanding
  const isAuthor = post.authorId === userId;
  const isAdmin = req.user.role === 'admin';

  if (!isAuthor && !isAdmin) {
    return res.status(403).json({
      error: 'Forbidden: You can only delete your own posts'
    });
  }

  await db.posts.delete(postId);
  res.json({ success: true });
});

// Now also add to other endpoints (PUT, etc.) based on understanding
```

## Change One Thing at a Time

### Principle

Make isolated changes and test each change individually. Changing multiple things simultaneously makes it impossible to determine what fixed (or broke) the issue.

### Why It Matters

Multiple simultaneous changes:
- Cannot determine which change was effective
- May combine working and non-working solutions
- Makes rollback difficult
- Complicates code review

Single changes:
- Clear cause-effect relationship
- Easy to verify effectiveness
- Simple to rollback if needed
- Easier code review and testing

### How to Apply

```javascript
// BAD: Multiple changes at once
async function fetchUserData(userId) {
  // Change 1: Added error handling
  try {
    // Change 2: Changed endpoint
    const response = await fetch(`/api/v2/users/${userId}`);

    // Change 3: Added timeout
    const data = await Promise.race([
      response.json(),
      timeout(5000)
    ]);

    // Change 4: Added caching
    cache.set(`user:${userId}`, data);

    // Change 5: Changed data structure
    return {
      id: data.id,
      name: data.fullName, // was data.name
      email: data.email
    };
  } catch (error) {
    // Change 6: Added fallback
    return cache.get(`user:${userId}`) || DEFAULT_USER;
  }
}

// PROBLEM: If this fixes the issue, which change did it?
// If it breaks something, which change caused it?
```

**GOOD: Incremental approach**

```javascript
// COMMIT 1: Baseline - reproduce issue
async function fetchUserData(userId) {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}
// Test: Issue reproduced ✓

// COMMIT 2: Add error handling
async function fetchUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  } catch (error) {
    console.error('Fetch failed:', error);
    throw error;
  }
}
// Test: Issue still occurs, but now logged ✓

// COMMIT 3: Add timeout
async function fetchUserData(userId) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`/api/users/${userId}`, {
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    return response.json();
  } catch (error) {
    console.error('Fetch failed:', error);
    throw error;
  }
}
// Test: ISSUE FIXED! Timeout was the solution ✓
// Now we know exactly what fixed it

// Can stop here, or continue with additional improvements
// Each as separate commit with testing
```

## Document Your Investigation

### Principle

Record your debugging process, findings, hypotheses tested, and results. Documentation helps you avoid repeating work and helps teammates learn from your experience.

### Why It Matters

Without documentation:
- Forget what you've already tried
- Repeat failed approaches
- Cannot share knowledge with team
- Lose context when returning to issue later

With documentation:
- Track investigation progress
- Avoid circular testing
- Enable team collaboration
- Create knowledge base for future issues

### What to Document

```markdown
## Bug Investigation: User Authentication Timeout

### Issue Description
Users intermittently logged out during active sessions
Frequency: ~10% of sessions
Impact: High - users lose work in progress

### Environment
- Production only (cannot reproduce in dev/staging)
- All browsers affected
- Started: 2025-10-28 after deployment
- Error: "Session expired" message

### Hypotheses Tested

#### Hypothesis 1: Token expiration time misconfigured ❌
**Test:** Examined JWT expiration claim
**Result:** Token shows correct 24h expiration
**Conclusion:** Not the cause

#### Hypothesis 2: Server clock skew ❌
**Test:** Checked system time across all servers
**Result:** All servers synchronized within 100ms
**Conclusion:** Not the cause

#### Hypothesis 3: Redis session store losing data ✓
**Test:** Added logging before/after Redis calls
**Result:** Redis returning null for valid session IDs
**Analysis:** Redis maxmemory-policy was 'volatile-lru'
**Root Cause:** Redis evicting session keys under memory pressure

### Solution
Changed Redis maxmemory-policy to 'allkeys-lru'
Added session keys to monitoring
Increased Redis memory allocation

### Verification
- No session loss reports in 48 hours
- Redis memory usage within limits
- Session monitoring showing healthy retention

### Prevention
- Added Redis memory monitoring alerts
- Documented session store configuration
- Added integration test for session persistence

### Time Spent
- Investigation: 4 hours
- Fix implementation: 30 minutes
- Verification: 48 hours monitoring

### References
- Deployment log: https://...
- Error tracking: https://...
- Related issue: #1234
```

## Use Version Control Effectively

### Principle

Leverage git to understand when bugs were introduced, what changed, and enable easy testing of different code versions.

### Why It Matters

Version control provides:
- History of all changes
- Ability to bisect and find breaking changes
- Easy rollback to working state
- Blame/annotate to find context

### Debugging with Git

**1. Find When Bug Was Introduced**

```bash
# Binary search through commits to find when bug appeared
git bisect start
git bisect bad  # Current code has bug
git bisect good v2.3.0  # This version was good

# Git checks out middle commit
# Test if bug exists
# Mark as good or bad
git bisect good  # or git bisect bad

# Repeat until git identifies the breaking commit
# Result: "commit abc123 is the first bad commit"

# See what changed
git show abc123
```

**2. Examine File History**

```bash
# See all changes to problematic file
git log -p -- path/to/buggy-file.js

# See who last modified specific lines
git blame path/to/buggy-file.js

# See changes in specific date range
git log --since="2025-10-01" --until="2025-10-31" -- path/to/file.js
```

**3. Compare Working vs Broken State**

```bash
# Compare current (broken) with last working version
git diff v2.3.0..HEAD -- src/auth/

# Create branch to test fix without affecting main work
git checkout -b debug/auth-issue
# Make debugging changes, test, experiment
# If fix works, clean up and merge
# If not working, abandon branch
```

**4. Temporary Debug Changes**

```bash
# Stash debug logging before committing fix
git stash  # Save debug code

# Commit actual fix
git add src/auth/login.js
git commit -m "Fix session timeout issue"

# Optionally restore debug code if needed
git stash pop  # Or git stash drop to discard
```

## Leverage Debugging Tools

### Principle

Master the debugging tools available for your stack. Tools enable much faster diagnosis than manual logging.

### Essential Tools by Category

**Browser DevTools (Frontend)**

```javascript
// Console API - beyond console.log
console.table(arrayOfObjects);  // Tabular display
console.group('API Calls');     // Grouping
console.time('render');         // Performance timing
console.trace();                // Stack trace

// Debugger statement - programmatic breakpoint
function processData(data) {
  if (data.length > 1000) {
    debugger;  // Execution pauses here
  }
  // ...
}

// Network tab usage
// - Inspect request/response headers
// - Check payload size and timing
// - Throttle network to test slow connections
// - Block requests to test offline behavior

// Performance profiling
// - Record performance profile
// - Identify expensive operations
// - Find reflow/repaint issues
// - Analyze memory usage
```

**IDE Debugger (Backend/Frontend)**

```javascript
// Set breakpoints with conditions
// Breakpoint condition: userId === 'test@example.com'
// Only pauses when condition is true

// Watch expressions
// Watch: req.user.id
// Watch: items.length
// Watch: state.errors.length > 0

// Call stack inspection
// See full path of function calls that led to current point

// Variable inspection
// Hover to see values
// Expand objects to inspect properties
// Modify values during debugging to test hypotheses
```

**Command Line Tools**

```bash
# Network debugging
curl -v https://api.example.com/users  # Verbose output
tcpdump -i any port 3000  # Monitor network traffic

# Process debugging
lsof -i :3000  # What's using port 3000?
ps aux | grep node  # Find node processes
strace -p <pid>  # System call tracing (Linux)

# Log analysis
tail -f app.log | grep ERROR  # Follow logs filtering errors
grep -r "UserNotFound" logs/  # Search all log files
awk '{print $1}' access.log | sort | uniq -c  # Count occurrences
```

## Read Error Messages Carefully

### Principle

Error messages contain valuable clues. Read them completely, including stack traces, error codes, and context.

### Why It Matters

Developers often:
- Skim error messages instead of reading carefully
- Ignore stack traces that show exactly where error occurred
- Miss important details in error context
- Jump to conclusions based on error type alone

### How to Read Errors

**Anatomy of an Error Message**

```
TypeError: Cannot read property 'name' of undefined
    at getUserName (src/utils/user.js:42:18)
    at UserProfile (src/components/UserProfile.tsx:28:22)
    at renderComponent (src/framework/render.js:103:5)
    at commitWork (src/framework/commit.js:89:7)

Important parts:
1. Error type: TypeError (wrong type used)
2. Error message: "Cannot read property 'name' of undefined"
   - Trying to access 'name' property
   - On undefined value (not null, not object - undefined)
3. Stack trace shows call path:
   - Started in UserProfile component (line 28)
   - Called getUserName function (line 42)
   - Line 42 in user.js is where error occurred
4. File locations: Exact files and line numbers
```

**Extract Maximum Information**

```javascript
// Example error in console:
/*
Uncaught TypeError: Cannot read property 'map' of undefined
    at TaskList (TaskList.tsx:15)
*/

// What this tells us:
// 1. "Uncaught" - no error boundary catching this
// 2. "TypeError" - type-related issue, not logic error
// 3. "Cannot read property 'map'" - trying to use .map()
// 4. "of undefined" - the value is undefined (not null, not [])
// 5. "at TaskList (TaskList.tsx:15)" - exact location

// Go to TaskList.tsx line 15:
function TaskList({ tasks }) {
  return tasks.map(task => <TaskCard task={task} />);  // Line 15
  //           ↑
  //         tasks is undefined
}

// ROOT CAUSE: tasks prop not passed or is undefined
// FIX: Add default value or null check
function TaskList({ tasks = [] }) {
  return tasks.map(task => <TaskCard task={task} />);
}
```

### Common Error Patterns

```javascript
// "Cannot read property 'X' of undefined"
// → Trying to access property on undefined value
// Check: Where does the value come from? Why is it undefined?

// "Cannot read property 'X' of null"
// → Similar but null was explicitly set or returned
// Check: What returns null? Is this expected?

// "X is not a function"
// → Trying to call something that isn't a function
// Check: Was function imported correctly? Is property name correct?

// "Maximum call stack size exceeded"
// → Infinite recursion
// Check: Does recursive function have base case? Correct termination condition?

// "CORS policy: No 'Access-Control-Allow-Origin' header"
// → Backend not configured to accept requests from frontend origin
// Check: Backend CORS configuration

// "Failed to fetch" / "Network Error"
// → Network connectivity issue
// Check: Is backend running? Correct URL? Network connectivity?
```

## Check Your Assumptions

### Principle

Bugs often hide in unverified assumptions. Question everything, especially things you're "certain" about.

### Common False Assumptions

```javascript
// ASSUMPTION: "This function always returns an array"
const users = await getUsers();
users.map(u => u.name);  // Crashes if getUsers() returns null

// VERIFY: Check return type
console.log('getUsers returned:', typeof users, users);

// ASSUMPTION: "The user is always logged in on this page"
const userName = req.user.name;  // Crashes if req.user is undefined

// VERIFY: Check existence
if (!req.user) {
  return res.redirect('/login');
}

// ASSUMPTION: "IDs are always numbers"
const userId = req.params.id;
const user = await db.query('SELECT * FROM users WHERE id = ?', [userId]);

// VERIFY: Type and format
console.log('User ID type:', typeof userId);  // Might be string!
const numericId = parseInt(userId, 10);
if (isNaN(numericId)) {
  return res.status(400).json({ error: 'Invalid user ID' });
}

// ASSUMPTION: "This code runs synchronously"
function saveData(data) {
  db.save(data);  // Assuming synchronous
  console.log('Data saved');  // Might log before save completes!
}

// VERIFY: Check if async
async function saveData(data) {
  await db.save(data);  // Properly wait
  console.log('Data saved');  // Now accurate
}
```

### Verification Techniques

```javascript
// 1. Add assertions to verify assumptions
function divide(a, b) {
  console.assert(typeof a === 'number', 'a must be number');
  console.assert(typeof b === 'number', 'b must be number');
  console.assert(b !== 0, 'b cannot be zero');

  return a / b;
}

// 2. Add type checking in TypeScript
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

// 3. Add runtime validation
function processOrder(order) {
  // Verify assumption: order has required fields
  const required = ['id', 'items', 'total'];
  for (const field of required) {
    if (!(field in order)) {
      throw new Error(`Order missing required field: ${field}`);
    }
  }

  // Process order...
}
```

## Related Practices

- [Core Concepts](core-concepts.md): Fundamental principles behind these practices
- [Patterns](patterns.md): Apply best practices through common patterns
- [Troubleshooting](troubleshooting.md): Use best practices for specific issues
- [Advanced Topics](advanced-topics.md): Advanced best practices for complex scenarios
