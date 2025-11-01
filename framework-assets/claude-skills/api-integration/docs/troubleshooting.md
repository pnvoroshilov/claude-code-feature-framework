# Troubleshooting - API Integration

Common issues, root causes, and solutions for API integration problems.

## Table of Contents

- [CORS Errors](#cors-errors)
- [Authentication Failures](#authentication-failures)
- [Network Timeouts](#network-timeouts)
- [4xx Client Errors](#4xx-client-errors)
- [5xx Server Errors](#5xx-server-errors)
- [Type Mismatch Issues](#type-mismatch-issues)
- [Environment Configuration Problems](#environment-configuration-problems)
- [React Query Cache Issues](#react-query-cache-issues)
- [Common FastAPI Errors](#common-fastapi-errors)
- [WebSocket Connection Issues](#websocket-connection-issues)

## CORS Errors

### Error Message

```
Access to XMLHttpRequest at 'http://localhost:8000/api/users'
from origin 'http://localhost:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause

CORS (Cross-Origin Resource Sharing) policy prevents frontend from accessing backend on different origin.

### Solutions

**1. Configure FastAPI CORS Middleware:**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**2. Verify Frontend URL:**

```typescript
// Ensure you're using correct API URL
const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Must match backend
});
```

**3. Check Preflight Requests:**

```
If using custom headers or methods, browser sends OPTIONS request first.
FastAPI CORS middleware handles this automatically.
```

### Prevention

- Always configure CORS middleware in FastAPI
- Use environment variables for CORS origins
- Test with actual frontend URL, not just Postman

## Authentication Failures

### Error: 401 Unauthorized

```
POST /api/users 401 Unauthorized
{
  "detail": "Could not validate credentials"
}
```

### Root Causes

1. Missing or expired JWT token
2. Token not included in request
3. Invalid token format
4. Token expired

### Solutions

**1. Verify Token is Sent:**

```typescript
// Check request interceptor
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  console.log('Token:', token); // Debug
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**2. Implement Token Refresh:**

```typescript
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        // Attempt refresh
        const newToken = await refreshToken();
        error.config.headers.Authorization = `Bearer ${newToken}`;
        return apiClient.request(error.config);
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    throw error;
  }
);
```

**3. Check Token Format:**

```typescript
// Correct format
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

// Incorrect
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... // Missing "Bearer "
```

### Prevention

- Always implement token refresh
- Store tokens securely
- Handle 401 errors globally
- Test token expiration scenarios

## Network Timeouts

### Error Message

```
Error: timeout of 10000ms exceeded
```

### Root Causes

1. Backend server slow or unresponsive
2. Network connectivity issues
3. Timeout set too low
4. Large request/response payload

### Solutions

**1. Increase Timeout:**

```typescript
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 30000, // 30 seconds instead of 10
});

// Or per-request
await apiClient.get('/users', { timeout: 60000 });
```

**2. Implement Retry Logic:**

```typescript
const retryInterceptor = new RetryInterceptor({
  maxRetries: 3,
  retryDelay: 1000,
});
retryInterceptor.apply(apiClient);
```

**3. Optimize Backend:**

```python
# Add pagination for large datasets
@app.get("/users")
async def get_users(skip: int = 0, limit: int = 100):
    return users[skip:skip + limit]
```

**4. Use AbortController:**

```typescript
const controller = new AbortController();

apiClient.get('/users', {
  signal: controller.signal,
  timeout: 5000,
}).catch(error => {
  if (error.code === 'ECONNABORTED') {
    console.log('Request timed out');
  }
});

// Cancel if needed
controller.abort();
```

### Prevention

- Set reasonable timeouts
- Implement pagination
- Use loading indicators
- Monitor backend performance

## 4xx Client Errors

### 400 Bad Request

**Cause:** Invalid request data

```typescript
// Missing required field
await apiClient.post('/users', {
  // name is required but missing
  email: 'john@example.com'
});
```

**Solution:**

```typescript
// Validate before sending
interface CreateUserDto {
  name: string;
  email: string;
}

const validateUser = (data: any): data is CreateUserDto => {
  return typeof data.name === 'string' && typeof data.email === 'string';
};

if (!validateUser(userData)) {
  throw new Error('Invalid user data');
}

await apiClient.post('/users', userData);
```

### 404 Not Found

**Cause:** Resource doesn't exist

```typescript
// User ID 999 doesn't exist
await apiClient.get('/users/999');
```

**Solution:**

```typescript
try {
  const user = await apiClient.get(`/users/${id}`);
  return user.data;
} catch (error) {
  if (error.response?.status === 404) {
    return null; // Or show "User not found" message
  }
  throw error;
}
```

### 422 Unprocessable Entity

**Cause:** Validation error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**Solution:**

```typescript
// Handle validation errors
try {
  await apiClient.post('/users', userData);
} catch (error) {
  if (error.response?.status === 422) {
    const errors = error.response.data.detail;
    errors.forEach((err: any) => {
      console.error(`${err.loc.join('.')}: ${err.msg}`);
    });
  }
}
```

### 429 Too Many Requests

**Cause:** Rate limiting

**Solution:**

```typescript
// Respect Retry-After header
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      if (retryAfter) {
        await new Promise(resolve =>
          setTimeout(resolve, parseInt(retryAfter) * 1000)
        );
        return apiClient.request(error.config);
      }
    }
    throw error;
  }
);
```

## 5xx Server Errors

### 500 Internal Server Error

**Cause:** Backend code error

**Frontend Handling:**

```typescript
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 500) {
      // Log to error tracking service
      console.error('Server error:', error.response.data);

      // Show user-friendly message
      alert('Something went wrong. Please try again later.');
    }
    throw error;
  }
);
```

**Backend Debugging:**

```python
# Check FastAPI logs
uvicorn app.main:app --reload --log-level debug

# Add exception handling
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 503 Service Unavailable

**Cause:** Server temporarily unavailable

**Solution:**

```typescript
// Retry with exponential backoff
const retryInterceptor = new RetryInterceptor({
  maxRetries: 5,
  retryableStatuses: [503],
});
retryInterceptor.apply(apiClient);
```

## Type Mismatch Issues

### Error: Type mismatch between frontend and backend

**Cause:** Frontend types don't match backend response

```typescript
// Frontend expects
interface User {
  id: number;
  name: string;
}

// Backend returns
{
  "id": "1",  // String instead of number
  "name": "John"
}
```

**Solutions:**

**1. Runtime Validation with Zod:**

```typescript
import { z } from 'zod';

const userSchema = z.object({
  id: z.number(),
  name: z.string(),
});

const response = await apiClient.get('/users/1');
const user = userSchema.parse(response.data); // Throws if invalid
```

**2. Transform in Interceptor:**

```typescript
apiClient.interceptors.response.use(response => {
  // Transform string IDs to numbers
  if (Array.isArray(response.data)) {
    response.data = response.data.map(item => ({
      ...item,
      id: typeof item.id === 'string' ? parseInt(item.id) : item.id,
    }));
  }
  return response;
});
```

**3. Fix Backend:**

```python
# Ensure correct types in Pydantic model
from pydantic import BaseModel

class User(BaseModel):
    id: int  # Not str
    name: str
```

## Environment Configuration Problems

### Error: API calls failing in production

**Cause:** Incorrect environment variables

**Solutions:**

**1. Verify Environment Variables:**

```bash
# .env.production
REACT_APP_API_URL=https://api.myapp.com

# NOT http://localhost:8000
```

**2. Check Build:**

```bash
# Environment vars are embedded at build time
npm run build

# Verify
grep -r "REACT_APP_API_URL" build/
```

**3. Runtime Configuration:**

```typescript
// For runtime config, use public/config.json
fetch('/config.json')
  .then(res => res.json())
  .then(config => {
    const apiClient = axios.create({
      baseURL: config.apiUrl,
    });
  });
```

## React Query Cache Issues

### Problem: Stale data shown

**Cause:** Cache not invalidated after mutation

**Solution:**

```typescript
const createUser = useMutation({
  mutationFn: userService.create,
  onSuccess: () => {
    // Invalidate and refetch
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

### Problem: Data refetching too often

**Cause:** staleTime too low

**Solution:**

```typescript
const { data } = useQuery({
  queryKey: ['users'],
  queryFn: userService.getAll,
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});
```

## Common FastAPI Errors

### Error: Pydantic validation error

```
422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

**Solution:**

```python
# backend/app/models.py
from pydantic import BaseModel, validator

class CreateUserRequest(BaseModel):
    name: str
    age: int

    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('age must be between 0 and 150')
        return v
```

### Error: CORS preflight failed

**Cause:** OPTIONS request not handled

**Solution:**

```python
# FastAPI handles OPTIONS automatically with CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],  # Includes OPTIONS
    allow_headers=["*"],
)
```

## WebSocket Connection Issues

### Error: WebSocket connection failed

**Causes:**
1. WebSocket server not running
2. Incorrect WebSocket URL
3. CORS issues
4. Firewall blocking

**Solutions:**

**1. Verify WebSocket URL:**

```typescript
// Correct
const ws = new WebSocket('ws://localhost:8000/ws');

// Production
const ws = new WebSocket('wss://api.myapp.com/ws'); // wss for HTTPS
```

**2. Add Error Handling:**

```typescript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);

  // Reconnect
  setTimeout(() => {
    console.log('Reconnecting...');
    connect();
  }, 5000);
};
```

**3. FastAPI WebSocket Setup:**

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

## Debugging Checklist

When encountering API issues:

- [ ] Check browser console for errors
- [ ] Inspect Network tab in DevTools
- [ ] Verify API URL is correct
- [ ] Check request headers (especially Authorization)
- [ ] Verify request payload format
- [ ] Check backend logs
- [ ] Test API with curl/Postman
- [ ] Verify CORS configuration
- [ ] Check environment variables
- [ ] Test with simplified request
- [ ] Review recent code changes
- [ ] Check backend server is running

---

For prevention strategies, see [docs/best-practices.md](best-practices.md). For implementation examples, see [examples/](../examples/).
