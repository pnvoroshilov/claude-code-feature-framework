# Troubleshooting Guide

Quick reference for debugging common issues across the stack, with symptoms, diagnostic steps, and solutions.

## Table of Contents

- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Database Issues](#database-issues)
- [Network and API Issues](#network-and-api-issues)
- [Build and Deployment Issues](#build-and-deployment-issues)
- [Performance Issues](#performance-issues)

## Frontend Issues

### React Component Not Rendering

**Symptoms:**
- Component doesn't appear on screen
- No errors in console
- React DevTools shows component mounted

**Diagnostic Steps:**

1. Check if component returns null conditionally
2. Verify props passed correctly
3. Check CSS for `display: none` or `visibility: hidden`
4. Verify keys in list rendering
5. Check React DevTools for component hierarchy

**Common Causes & Fixes:**

```javascript
// Cause 1: Conditional render returning null
function UserProfile({ user }) {
  if (!user) {
    return null; // Component renders nothing
  }
  return <div>{user.name}</div>;
}
// Fix: Render loading state or placeholder

// Cause 2: CSS hiding component
.profile {
  display: none; /* Component rendered but hidden */
}
// Fix: Check computed styles in DevTools

// Cause 3: Key causing React to skip render
{users.map(user => (
  <UserCard key={user.name} user={user} /> // Non-unique key!
))}
// Fix: Use unique ID as key

// Cause 4: Props not passed down
<UserProfile /> // Missing user prop!
// Fix: Pass required props
```

### State Not Updating

**Symptoms:**
- Call to setState/dispatch but UI doesn't change
- State appears correct in DevTools
- Manual refresh shows correct data

**Diagnostic Steps:**

1. Verify not mutating state directly
2. Check if creating new object references
3. Verify component subscribed to correct state
4. Check for PureComponent/memo blocking updates

**Common Causes & Fixes:**

```javascript
// Cause 1: Direct mutation
const [items, setItems] = useState([]);

function addItem(item) {
  items.push(item); // WRONG: Direct mutation
  setItems(items); // Same reference, no re-render
}

// Fix: Create new array
function addItem(item) {
  setItems([...items, item]); // New reference
}

// Cause 2: Nested object mutation
const [user, setUser] = useState({ name: 'John', settings: {} });

function updateSettings(key, value) {
  user.settings[key] = value; // WRONG: Mutates nested object
  setUser(user); // React doesn't detect change
}

// Fix: Deep clone
function updateSettings(key, value) {
  setUser({
    ...user,
    settings: {
      ...user.settings,
      [key]: value
    }
  });
}

// Cause 3: Async setState with stale closure
function Counter() {
  const [count, setCount] = useState(0);

  const increment = async () => {
    await someAsyncOperation();
    setCount(count + 1); // Stale `count` from closure
  };
}

// Fix: Use functional update
setCount(prev => prev + 1);
```

### Infinite Render Loop

**Symptoms:**
- Browser freezes or becomes very slow
- Console floods with logs
- "Maximum update depth exceeded" error

**Diagnostic Steps:**

1. Check useEffect dependencies
2. Verify no setState in render function
3. Check for object/array creation in dependencies
4. Look for circular component updates

**Common Causes & Fixes:**

```javascript
// Cause 1: setState in render
function Component() {
  const [count, setCount] = useState(0);

  setCount(count + 1); // WRONG: Causes infinite loop

  return <div>{count}</div>;
}

// Fix: Move to event handler or useEffect

// Cause 2: Missing useEffect dependencies
function Component({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }); // WRONG: No dependency array, runs every render

  return <div>{user?.name}</div>;
}

// Fix: Add dependency array
useEffect(() => {
  fetchUser(userId).then(setUser);
}, [userId]); // Only re-run when userId changes

// Cause 3: New object in dependency array
function Component() {
  const options = { sort: 'asc' }; // New object every render

  useEffect(() => {
    fetchData(options);
  }, [options]); // WRONG: options is new every time, infinite loop

  return <div>...</div>;
}

// Fix: useMemo or move outside component
const options = useMemo(() => ({ sort: 'asc' }), []); // Stable reference
```

### Event Handler Not Firing

**Symptoms:**
- Click/change/submit doesn't trigger expected behavior
- No errors in console
- Component renders correctly

**Diagnostic Steps:**

1. Check if event listener actually attached
2. Verify event propagation not stopped
3. Check for CSS `pointer-events: none`
4. Verify correct event name (onClick vs onclick)

**Common Causes & Fixes:**

```javascript
// Cause 1: Wrong event name
<button onclick={handleClick}>  // WRONG: lowercase
  Click me
</button>

// Fix: Use camelCase
<button onClick={handleClick}>  // CORRECT
  Click me
</button>

// Cause 2: Calling function immediately
<button onClick={handleClick()}> // WRONG: Calls on render
  Click me
</button>

// Fix: Pass function reference
<button onClick={handleClick}> // CORRECT
  Click me
</button>

// Cause 3: Event bubbling stopped
function ParentComponent() {
  const handleParentClick = () => {
    console.log('Parent clicked');
  };

  return (
    <div onClick={handleParentClick}>
      <button onClick={(e) => {
        e.stopPropagation(); // Stops bubbling to parent
        console.log('Button clicked');
      }}>
        Click me
      </button>
    </div>
  );
}

// Fix: Don't stop propagation unless necessary
```

## Backend Issues

### API Endpoint Returns 500 Error

**Symptoms:**
- Request returns 500 Internal Server Error
- Error message vague or missing
- Works sometimes, fails other times

**Diagnostic Steps:**

1. Check server logs for full error + stack trace
2. Verify request payload is valid
3. Check database connection
4. Look for unhandled promise rejections
5. Check for missing error handling

**Common Causes & Fixes:**

```javascript
// Cause 1: Unhandled async error
app.post('/api/users', async (req, res) => {
  // WRONG: If this throws, express doesn't catch it
  const user = await db.users.create(req.body);
  res.json(user);
});

// Fix: Add error handling
app.post('/api/users', async (req, res) => {
  try {
    const user = await db.users.create(req.body);
    res.json(user);
  } catch (error) {
    console.error('Create user failed:', error);
    res.status(500).json({
      error: 'Failed to create user',
      message: error.message
    });
  }
});

// Or use express-async-errors package

// Cause 2: Accessing property on null/undefined
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);

  // WRONG: user might be null
  const name = user.name; // TypeError!

  res.json({ name });
});

// Fix: Check existence
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json({ name: user.name });
});
```

### Database Query Failing

**Symptoms:**
- Database operation throws error
- Timeout errors
- "Too many connections" error

**Diagnostic Steps:**

1. Check database server is running
2. Verify connection string correct
3. Check database logs
4. Verify query syntax
5. Check connection pool settings

**Common Causes & Fixes:**

```javascript
// Cause 1: Connection not released
async function getUser(id) {
  const connection = await pool.getConnection();

  const user = await connection.query(
    'SELECT * FROM users WHERE id = ?',
    [id]
  );

  return user; // WRONG: Connection never released!
}

// Fix: Always release in finally
async function getUser(id) {
  const connection = await pool.getConnection();

  try {
    const user = await connection.query(
      'SELECT * FROM users WHERE id = ?',
      [id]
    );
    return user;
  } finally {
    connection.release(); // Always executes
  }
}

// Cause 2: SQL injection vulnerability
async function searchUsers(name) {
  // WRONG: Vulnerable to SQL injection
  const users = await db.query(
    `SELECT * FROM users WHERE name = '${name}'`
  );
  return users;
}

// Fix: Use parameterized queries
async function searchUsers(name) {
  const users = await db.query(
    'SELECT * FROM users WHERE name = ?',
    [name]
  );
  return users;
}

// Cause 3: N+1 query problem
async function getUsersWithPosts() {
  const users = await db.users.findAll();

  // WRONG: Queries database for each user
  for (const user of users) {
    user.posts = await db.posts.findByUserId(user.id);
  }

  return users;
}

// Fix: Use JOIN or bulk query
async function getUsersWithPosts() {
  const users = await db.query(`
    SELECT u.*, p.id as post_id, p.title as post_title
    FROM users u
    LEFT JOIN posts p ON p.user_id = u.id
  `);

  // Group posts by user
  return groupPostsByUser(users);
}
```

## Network and API Issues

### CORS Error

**Symptoms:**
- "CORS policy: No 'Access-Control-Allow-Origin' header"
- Request shows as "(failed)" in Network tab
- Status code is 0 or blank

**Diagnostic Steps:**

1. Check browser console for exact CORS error
2. Verify request origin vs server configuration
3. Check if preflight request (OPTIONS) succeeding
4. Test with curl to verify server-side works

**Common Causes & Fixes:**

```javascript
// Backend not configured for CORS
// Fix: Add CORS middleware (Express)
const cors = require('cors');

app.use(cors({
  origin: 'http://localhost:3000', // Frontend origin
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Or manually:
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', req.headers.origin);
  res.header('Access-Control-Allow-Credentials', 'true');
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE');
  res.header('Access-Control-Allow-Headers', 'Content-Type,Authorization');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }

  next();
});
```

### Request Timeout

**Symptoms:**
- Request takes very long then fails
- "net::ERR_CONNECTION_TIMED_OUT"
- No response from server

**Diagnostic Steps:**

1. Check if server is running
2. Verify correct URL and port
3. Check firewall/network restrictions
4. Look for slow database queries
5. Check server CPU/memory usage

**Common Causes & Fixes:**

```javascript
// Cause 1: No timeout set, waits forever
fetch('/api/slow-endpoint');

// Fix: Add timeout
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000);

try {
  const response = await fetch('/api/slow-endpoint', {
    signal: controller.signal
  });
  clearTimeout(timeoutId);
  return response;
} catch (error) {
  if (error.name === 'AbortError') {
    console.error('Request timed out');
  }
  throw error;
}

// Cause 2: Server-side blocking operation
app.get('/api/data', async (req, res) => {
  // WRONG: Synchronous, blocks event loop
  const data = expensiveComputationSync();
  res.json(data);
});

// Fix: Make async or offload to worker
app.get('/api/data', async (req, res) => {
  const data = await expensiveComputationAsync();
  res.json(data);
});
```

## Database Issues

### Slow Query Performance

**Symptoms:**
- Queries take seconds instead of milliseconds
- Application becomes slow under load
- Database CPU usage high

**Diagnostic Steps:**

1. Use EXPLAIN to analyze query plan
2. Check for missing indexes
3. Look for N+1 query patterns
4. Check query complexity

**Common Causes & Fixes:**

```sql
-- Cause 1: Missing index
SELECT * FROM users WHERE email = 'test@example.com';
-- If no index on email, full table scan

-- Fix: Add index
CREATE INDEX idx_users_email ON users(email);

-- Cause 2: SELECT * returning too much data
SELECT * FROM posts; -- Returns all columns, all rows

-- Fix: Select only needed columns and use pagination
SELECT id, title, created_at
FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;

-- Cause 3: Complex JOIN on large tables
SELECT u.*, p.*, c.*
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
LEFT JOIN comments c ON c.post_id = p.id;

-- Fix: Add appropriate indexes and limit results
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);

SELECT u.*, p.*, c.*
FROM users u
LEFT JOIN posts p ON p.user_id = u.id
LEFT JOIN comments c ON c.post_id = p.id
WHERE u.id = ?  -- Limit to specific user
LIMIT 100;  -- Limit results
```

## Build and Deployment Issues

### Build Fails in CI but Works Locally

**Symptoms:**
- Build succeeds on developer machine
- CI/CD pipeline fails
- Different errors in different environments

**Diagnostic Steps:**

1. Check Node/npm versions match
2. Verify all dependencies in package.json
3. Check for environment-specific code
4. Look for global packages being used
5. Check for case-sensitive file paths

**Common Causes & Fixes:**

```bash
# Cause 1: Different Node versions
# Local: Node 18, CI: Node 16
# Some features not available in older version

# Fix: Specify Node version in CI config
# .github/workflows/build.yml
- uses: actions/setup-node@v3
  with:
    node-version: '18'

# Or use .nvmrc
echo "18" > .nvmrc

# Cause 2: Dependency not in package.json
# Locally: Globally installed package
# CI: Package not available

# Fix: Add to package.json
npm install --save-dev missing-package

# Cause 3: Case sensitivity
# Local (Mac/Windows): Case-insensitive
import Component from './Component';  // Works

# CI (Linux): Case-sensitive
# File is actually ./component.tsx  // Fails in CI!

# Fix: Match case exactly
import Component from './component';
```

### Docker Container Won't Start

**Symptoms:**
- Container exits immediately
- docker ps shows no running container
- docker logs shows error

**Diagnostic Steps:**

1. Check container logs: `docker logs <container>`
2. Verify Dockerfile CMD/ENTRYPOINT
3. Check for missing environment variables
4. Verify all files copied into image

**Common Causes & Fixes:**

```dockerfile
# Cause 1: CMD syntax error
CMD npm start  # WRONG: Shell form doesn't handle signals

# Fix: Use exec form
CMD ["npm", "start"]  # CORRECT: Exec form

# Cause 2: Missing dependencies in container
FROM node:18
WORKDIR /app
COPY package.json ./
# WRONG: Forgot to run npm install
COPY . .
CMD ["npm", "start"]  # Fails: node_modules missing

# Fix: Install dependencies
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm ci  # Install dependencies
COPY . .
CMD ["npm", "start"]

# Cause 3: Wrong working directory
FROM node:18
COPY . /app
CMD ["npm", "start"]  # Fails: Not in /app directory

# Fix: Set WORKDIR
FROM node:18
WORKDIR /app  # Set working directory
COPY . .
CMD ["npm", "start"]  # Now works
```

## Performance Issues

### Page Load Slow

**Symptoms:**
- Initial page load takes several seconds
- Users complain about slowness
- Lighthouse score poor

**Diagnostic Steps:**

1. Run Lighthouse audit
2. Check Network tab for large resources
3. Analyze bundle size
4. Check for render-blocking resources

**Common Causes & Fixes:**

```javascript
// Cause 1: Large bundle size
// webpack-bundle-analyzer shows lodash is 200KB

// Fix: Use specific imports
// WRONG: Imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 100);

// CORRECT: Import only what you need
import debounce from 'lodash/debounce';
const result = debounce(fn, 100);

// Cause 2: No code splitting
// One giant bundle.js with all routes

// Fix: Lazy load routes
// React Router with lazy loading
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
  </Routes>
</Suspense>

// Cause 3: Unoptimized images
<img src="photo.jpg" />  // 5MB uncompressed image

// Fix: Optimize and use correct formats
<picture>
  <source srcSet="photo.webp" type="image/webp" />
  <source srcSet="photo.jpg" type="image/jpeg" />
  <img src="photo.jpg" loading="lazy" width="800" height="600" />
</picture>
```

## Related Documentation

- [Core Concepts](core-concepts.md): Understand underlying principles
- [Best Practices](best-practices.md): Prevent issues before they occur
- [Patterns](patterns.md): Systematic approaches to debugging
- [Advanced Topics](advanced-topics.md): Complex debugging scenarios
