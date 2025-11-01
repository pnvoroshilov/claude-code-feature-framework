# Core Concepts - API Integration

Fundamental concepts for building robust API integrations between React frontends and Python FastAPI backends.

## Table of Contents

- [HTTP and REST Fundamentals](#http-and-rest-fundamentals)
- [Axios Library Architecture](#axios-library-architecture)
- [Request/Response Lifecycle](#requestresponse-lifecycle)
- [CORS and Preflight Requests](#cors-and-preflight-requests)
- [Content Negotiation](#content-negotiation)
- [API Contracts and OpenAPI](#api-contracts-and-openapi)
- [Authentication and Authorization](#authentication-and-authorization)
- [State Management for APIs](#state-management-for-apis)
- [Error Handling Philosophy](#error-handling-philosophy)
- [TypeScript and Type Safety](#typescript-and-type-safety)
- [Environment Configuration](#environment-configuration)
- [Asynchronous JavaScript](#asynchronous-javascript)

## HTTP and REST Fundamentals

### What It Is

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the web. REST (Representational State Transfer) is an architectural style for designing networked applications using HTTP methods to perform CRUD operations.

### Why It Matters

Understanding HTTP and REST is essential for API integration because:
- Every API call is an HTTP request/response cycle
- REST principles guide API design and usage
- HTTP status codes communicate success/failure
- HTTP methods (GET, POST, PUT, DELETE) have semantic meaning
- Proper HTTP usage ensures scalable, maintainable APIs

### How It Works

**HTTP Methods:**
- `GET`: Retrieve data (idempotent, safe)
- `POST`: Create new resource
- `PUT`: Update entire resource (idempotent)
- `PATCH`: Partial update of resource
- `DELETE`: Remove resource (idempotent)

**HTTP Status Codes:**
- `2xx`: Success (200 OK, 201 Created, 204 No Content)
- `3xx`: Redirection (301 Moved, 304 Not Modified)
- `4xx`: Client errors (400 Bad Request, 401 Unauthorized, 404 Not Found)
- `5xx`: Server errors (500 Internal Server Error, 503 Service Unavailable)

### Examples

**GET Request:**
```typescript
// Fetch user list
const response = await axios.get('/api/users');
// Status: 200 OK
// Body: [{ id: 1, name: "John" }, ...]
```

**POST Request:**
```typescript
// Create new user
const response = await axios.post('/api/users', {
  name: "Jane Doe",
  email: "jane@example.com"
});
// Status: 201 Created
// Body: { id: 2, name: "Jane Doe", ... }
```

**PUT Request:**
```typescript
// Update entire user
const response = await axios.put('/api/users/2', {
  name: "Jane Smith",
  email: "jane.smith@example.com"
});
// Status: 200 OK
```

**DELETE Request:**
```typescript
// Delete user
const response = await axios.delete('/api/users/2');
// Status: 204 No Content
```

### Common Patterns

**RESTful Resource URLs:**
```
GET    /api/users          # List all users
GET    /api/users/1        # Get specific user
POST   /api/users          # Create user
PUT    /api/users/1        # Update user
DELETE /api/users/1        # Delete user
```

**Nested Resources:**
```
GET    /api/users/1/posts  # Get user's posts
POST   /api/users/1/posts  # Create post for user
```

### Common Mistakes

❌ **Using GET for mutations:**
```typescript
// WRONG: GET should not modify data
await axios.get('/api/users/delete/1');
```

✅ **Use appropriate HTTP method:**
```typescript
// CORRECT: DELETE for removing resources
await axios.delete('/api/users/1');
```

❌ **Ignoring idempotency:**
```typescript
// WRONG: PUT should be idempotent
// Don't use counter increments in PUT
await axios.put('/api/users/1', { loginCount: user.loginCount + 1 });
```

✅ **Use PATCH for non-idempotent updates:**
```typescript
// CORRECT: PATCH for partial updates
await axios.patch('/api/users/1/increment-login');
```

### Related Concepts

- [Request/Response Lifecycle](#requestresponse-lifecycle)
- [API Contracts and OpenAPI](#api-contracts-and-openapi)
- [Error Handling Philosophy](#error-handling-philosophy)

## Axios Library Architecture

### What It Is

Axios is a promise-based HTTP client for the browser and Node.js. It provides a simple, elegant API for making HTTP requests with features like interceptors, automatic JSON transformation, and request/response configuration.

### Why It Matters

Axios is the de facto standard for React API integration because:
- Promise-based API works seamlessly with async/await
- Automatic request/response transformation
- Interceptor support for global request/response handling
- Built-in CSRF protection
- Request cancellation support
- TypeScript support with types
- Works in both browser and Node.js

### How It Works

**Axios Instance Architecture:**

```typescript
// Create configured instance
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Request interceptor (runs before request sent)
apiClient.interceptors.request.use(
  config => {
    // Modify config (add auth token, etc.)
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor (runs after response received)
apiClient.interceptors.response.use(
  response => {
    // Transform response data
    return response;
  },
  error => {
    // Handle errors globally
    return Promise.reject(error);
  }
);
```

### Examples

**Basic Axios Usage:**
```typescript
import axios from 'axios';

// Simple GET
const users = await axios.get('http://localhost:8000/api/users');

// GET with query parameters
const filteredUsers = await axios.get('/api/users', {
  params: { role: 'admin', active: true }
});
// Generates: /api/users?role=admin&active=true

// POST with data
const newUser = await axios.post('/api/users', {
  name: 'John',
  email: 'john@example.com'
});

// Custom headers
const response = await axios.get('/api/users', {
  headers: {
    'Authorization': 'Bearer token123',
    'X-Custom-Header': 'value'
  }
});
```

**Axios Instance Pattern:**
```typescript
// src/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Now use apiClient everywhere
// src/api/users.ts
import { apiClient } from './client';

export const getUsers = () => apiClient.get('/users');
export const createUser = (data) => apiClient.post('/users', data);
```

**Request Configuration:**
```typescript
const response = await apiClient.get('/users', {
  params: { page: 1, limit: 10 },      // Query string
  headers: { 'X-Custom': 'value' },     // Custom headers
  timeout: 5000,                        // Request timeout
  responseType: 'json',                 // Response type
  maxRedirects: 5,                      // Max redirects
  validateStatus: (status) => status < 500, // Custom validation
});
```

### Common Patterns

**Service Layer Pattern:**
```typescript
// src/api/services/userService.ts
class UserService {
  private client = apiClient;

  async getUsers() {
    const response = await this.client.get('/users');
    return response.data;
  }

  async getUser(id: number) {
    const response = await this.client.get(`/users/${id}`);
    return response.data;
  }

  async createUser(data: CreateUserDto) {
    const response = await this.client.post('/users', data);
    return response.data;
  }
}

export const userService = new UserService();
```

### Common Mistakes

❌ **Creating new axios instance for every request:**
```typescript
// WRONG: Don't do this
const getUsers = async () => {
  const client = axios.create({ baseURL: '...' });
  return client.get('/users');
};
```

✅ **Reuse configured instance:**
```typescript
// CORRECT: Create once, reuse everywhere
const apiClient = axios.create({ baseURL: '...' });

const getUsers = async () => apiClient.get('/users');
```

❌ **Not handling errors:**
```typescript
// WRONG: Unhandled promise rejection
const data = await axios.get('/users');
```

✅ **Always handle errors:**
```typescript
// CORRECT: Try-catch or .catch()
try {
  const data = await axios.get('/users');
} catch (error) {
  console.error('Failed to fetch users:', error);
  throw error;
}
```

### Related Concepts

- [Request/Response Lifecycle](#requestresponse-lifecycle)
- [TypeScript and Type Safety](#typescript-and-type-safety)
- See [docs/patterns.md](patterns.md) for advanced patterns

## Request/Response Lifecycle

### What It Is

The request/response lifecycle describes the complete journey of an HTTP request from initiation in the React app to receiving and processing the response from the FastAPI backend.

### Why It Matters

Understanding the lifecycle helps you:
- Know where to add authentication headers
- Understand when interceptors run
- Debug request/response issues
- Implement loading states correctly
- Handle errors at the right stage
- Optimize performance

### How It Works

**Complete Lifecycle:**

```
1. User Action (button click, form submit)
   ↓
2. React Component (setState, dispatch)
   ↓
3. API Call Function (userService.getUsers())
   ↓
4. Request Interceptor (add auth, logging)
   ↓
5. Axios Adapter (browser fetch/XHR)
   ↓
6. Browser Network Layer (DNS, TCP, TLS)
   ↓
7. CORS Preflight (if needed)
   ↓
8. FastAPI Server (receive request)
   ↓
9. FastAPI Middleware (CORS, auth)
   ↓
10. Route Handler (business logic)
   ↓
11. Pydantic Validation (serialize response)
   ↓
12. HTTP Response (sent to client)
   ↓
13. Axios Response (parse JSON)
   ↓
14. Response Interceptor (transform, log)
   ↓
15. API Call Function (return data)
   ↓
16. React Component (setState, render)
```

### Examples

**Lifecycle with Interceptors:**
```typescript
// 1. Setup interceptors
apiClient.interceptors.request.use(config => {
  console.log('Request interceptor:', config.url);
  config.headers.Authorization = `Bearer ${getToken()}`;
  return config;
});

apiClient.interceptors.response.use(
  response => {
    console.log('Response interceptor:', response.status);
    return response.data; // Extract data
  },
  error => {
    console.error('Error interceptor:', error.message);
    throw error;
  }
);

// 2. Make request
const fetchUsers = async () => {
  try {
    console.log('Starting request');
    const users = await apiClient.get('/users');
    console.log('Request complete:', users);
    return users;
  } catch (error) {
    console.error('Request failed:', error);
    throw error;
  }
};

// Console output:
// Starting request
// Request interceptor: /users
// Response interceptor: 200
// Request complete: [...]
```

**Request with Loading State:**
```typescript
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);  // Stage 2: UI update
    setError(null);

    try {
      const data = await apiClient.get('/users'); // Stages 3-15
      setUsers(data);  // Stage 16: Update state
    } catch (err) {
      setError(err.message); // Stage 16: Error state
    } finally {
      setLoading(false); // Stage 16: Complete
    }
  };

  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {users.map(user => <div key={user.id}>{user.name}</div>)}
    </div>
  );
}
```

### Common Patterns

**Request Lifecycle Monitoring:**
```typescript
apiClient.interceptors.request.use(config => {
  config.metadata = { startTime: Date.now() };
  console.log(`→ ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

apiClient.interceptors.response.use(
  response => {
    const duration = Date.now() - response.config.metadata.startTime;
    console.log(`← ${response.status} ${response.config.url} (${duration}ms)`);
    return response;
  },
  error => {
    const duration = Date.now() - error.config.metadata.startTime;
    console.error(`✗ ${error.config.url} (${duration}ms):`, error.message);
    throw error;
  }
);
```

### Common Mistakes

❌ **Not cleaning up async requests:**
```typescript
// WRONG: Request continues after unmount
useEffect(() => {
  apiClient.get('/users').then(setUsers);
}, []);
```

✅ **Cancel requests on unmount:**
```typescript
// CORRECT: Cleanup with AbortController
useEffect(() => {
  const controller = new AbortController();

  apiClient.get('/users', { signal: controller.signal })
    .then(setUsers)
    .catch(error => {
      if (error.name !== 'AbortError') {
        console.error(error);
      }
    });

  return () => controller.abort();
}, []);
```

### Related Concepts

- [Axios Library Architecture](#axios-library-architecture)
- [Asynchronous JavaScript](#asynchronous-javascript)
- See [docs/advanced-topics.md](advanced-topics.md) for interceptor chains

## CORS and Preflight Requests

### What It Is

CORS (Cross-Origin Resource Sharing) is a security mechanism that allows or restricts resources to be requested from another domain. Preflight requests are OPTIONS requests that browsers send before certain cross-origin requests.

### Why It Matters

CORS is the #1 source of API integration issues. Understanding CORS helps you:
- Configure FastAPI CORS middleware correctly
- Avoid "blocked by CORS policy" errors
- Understand when preflight requests occur
- Debug cross-origin issues
- Implement secure API access

### How It Works

**Same-Origin vs Cross-Origin:**

```
Same-Origin (no CORS):
Frontend: http://localhost:3000
Backend:  http://localhost:3000/api  ✓ Same origin

Cross-Origin (CORS required):
Frontend: http://localhost:3000
Backend:  http://localhost:8000      ✗ Different port = different origin
```

**CORS Headers:**
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

**Preflight Request:**
```
Browser automatically sends OPTIONS request when:
- HTTP method is not GET, HEAD, or POST
- Custom headers are present
- Content-Type is not application/x-www-form-urlencoded, multipart/form-data, or text/plain
```

### Examples

**FastAPI CORS Configuration:**
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "https://myapp.com",      # Production frontend
    ],
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

@app.get("/api/users")
async def get_users():
    return [{"id": 1, "name": "John"}]
```

**React Axios Request (Triggers Preflight):**
```typescript
// This triggers OPTIONS preflight because of Authorization header
const response = await apiClient.get('/users', {
  headers: {
    'Authorization': 'Bearer token123'
  }
});

// Network tab shows:
// 1. OPTIONS /users (preflight)
// 2. GET /users (actual request)
```

**Axios with Credentials:**
```typescript
// Include cookies in cross-origin requests
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // Send cookies
});

// FastAPI must set allow_credentials=True
```

### Common Patterns

**Development vs Production CORS:**
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    class Config:
        env_file = ".env"

settings = Settings()

# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Conditional CORS:**
```python
# Only allow CORS in development
import os

origins = []
if os.getenv("ENV") == "development":
    origins = ["http://localhost:3000"]
else:
    origins = ["https://myapp.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Common Mistakes

❌ **Using wildcard with credentials:**
```python
# WRONG: Can't use * with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Error!
)
```

✅ **Specify exact origins:**
```python
# CORRECT: List specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
)
```

❌ **Forgetting to handle OPTIONS:**
```python
# WRONG: Manually handling OPTIONS (not needed)
@app.options("/users")
async def options_users():
    return {}
```

✅ **Let CORS middleware handle it:**
```python
# CORRECT: Middleware handles OPTIONS automatically
app.add_middleware(CORSMiddleware, ...)
# No need for OPTIONS route
```

### Related Concepts

- [Authentication and Authorization](#authentication-and-authorization)
- See [docs/troubleshooting.md](troubleshooting.md) for CORS errors

## Content Negotiation

### What It Is

Content negotiation is the mechanism for serving different representations of a resource based on client preferences (JSON, XML, etc.) and server capabilities.

### Why It Matters

Content negotiation ensures:
- Clients receive data in expected format
- Server can return different representations
- Proper character encoding
- Compression support
- Version negotiation

### How It Works

**HTTP Headers:**
```
Request Headers:
  Accept: application/json
  Accept-Encoding: gzip, deflate
  Accept-Language: en-US
  Content-Type: application/json

Response Headers:
  Content-Type: application/json; charset=utf-8
  Content-Encoding: gzip
  Content-Length: 1234
```

### Examples

**JSON Content Negotiation:**
```typescript
// Axios automatically sets Content-Type and Accept
const response = await apiClient.post('/users', {
  name: 'John'
});

// Request headers:
// Content-Type: application/json
// Accept: application/json, text/plain, */*

// Response headers:
// Content-Type: application/json; charset=utf-8
```

**Custom Content Types:**
```typescript
// Request CSV export
const response = await apiClient.get('/users/export', {
  headers: {
    'Accept': 'text/csv'
  },
  responseType: 'blob'
});

// FastAPI returns CSV
const blob = new Blob([response.data], { type: 'text/csv' });
const url = window.URL.createObjectURL(blob);
```

**Form Data:**
```typescript
const formData = new FormData();
formData.append('file', fileBlob);
formData.append('name', 'John');

const response = await apiClient.post('/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

// Axios automatically sets boundary
// Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
```

### Common Patterns

**FastAPI Content Negotiation:**
```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, PlainTextResponse

@app.get("/users")
async def get_users(accept: str = Header(None)):
    users = [{"id": 1, "name": "John"}]

    if accept == "text/csv":
        csv_data = "id,name\n1,John"
        return PlainTextResponse(csv_data, media_type="text/csv")

    return JSONResponse(users)
```

### Related Concepts

- [HTTP and REST Fundamentals](#http-and-rest-fundamentals)
- See [docs/advanced-topics.md](advanced-topics.md) for file uploads

## API Contracts and OpenAPI

### What It Is

API contracts define the interface between frontend and backend using schemas. OpenAPI (formerly Swagger) is a specification for documenting RESTful APIs that FastAPI generates automatically.

### Why It Matters

API contracts provide:
- Single source of truth for API structure
- Automatic validation
- Interactive documentation
- TypeScript type generation
- Contract testing
- Client SDK generation

### How It Works

FastAPI automatically generates OpenAPI documentation from your route definitions and Pydantic models.

### Examples

**FastAPI with OpenAPI:**
```python
from fastapi import FastAPI
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

app = FastAPI(
    title="My API",
    description="API for user management",
    version="1.0.0"
)

@app.get("/users", response_model=list[User])
async def get_users():
    """Get all users."""
    return [{"id": 1, "name": "John", "email": "john@example.com"}]

# OpenAPI docs available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
# http://localhost:8000/openapi.json (JSON schema)
```

**TypeScript Types from OpenAPI:**
```typescript
// Generated from OpenAPI schema
export interface User {
  id: number;
  name: string;
  email: string;
}

export interface CreateUserRequest {
  name: string;
  email: string;
}

// Use in API calls
const getUsers = async (): Promise<User[]> => {
  const response = await apiClient.get<User[]>('/users');
  return response.data;
};
```

**Schema Validation:**
```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

@app.post("/users")
async def create_user(user: CreateUserRequest):
    # FastAPI validates request automatically
    # Returns 422 if validation fails
    return {"id": 1, **user.dict()}
```

### Common Patterns

**Shared Type Definitions:**
```typescript
// src/types/api.ts
// Keep in sync with FastAPI models

export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface CreateUserDto {
  name: string;
  email: string;
}

export interface UpdateUserDto {
  name?: string;
  email?: string;
}
```

### Related Concepts

- [TypeScript and Type Safety](#typescript-and-type-safety)
- [Error Handling Philosophy](#error-handling-philosophy)

## Authentication and Authorization

### What It Is

Authentication verifies user identity ("who are you?"), while authorization determines access rights ("what can you do?"). In API integration, this typically involves tokens (JWT) or session cookies.

### Why It Matters

Proper auth implementation:
- Protects sensitive data
- Ensures secure API access
- Maintains user sessions
- Handles token refresh
- Prevents unauthorized access

### How It Works

**JWT Flow:**
```
1. User logs in → POST /auth/login
2. Server validates credentials
3. Server returns JWT token
4. Client stores token (localStorage/sessionStorage)
5. Client includes token in all requests
6. Server validates token
7. Token expires → Refresh token flow
```

### Examples

**Login Flow:**
```typescript
// src/api/auth.ts
interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>('/auth/login', credentials);

  // Store tokens
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);

  return response.data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
```

**Auth Interceptor:**
```typescript
// Add token to every request
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, try refresh
      try {
        await refreshToken();
        // Retry original request
        return apiClient.request(error.config);
      } catch (refreshError) {
        // Refresh failed, logout user
        logout();
        window.location.href = '/login';
      }
    }
    throw error;
  }
);
```

**FastAPI Authentication:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401)

@app.get("/users/me")
async def get_me(user_id: int = Depends(get_current_user)):
    return {"user_id": user_id}
```

### Common Patterns

**Token Refresh:**
```typescript
let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (callback) => {
  refreshSubscribers.push(callback);
};

const onTokenRefreshed = (token) => {
  refreshSubscribers.forEach(callback => callback(token));
  refreshSubscribers = [];
};

const refreshToken = async () => {
  if (isRefreshing) {
    return new Promise(resolve => {
      subscribeTokenRefresh(token => {
        resolve(token);
      });
    });
  }

  isRefreshing = true;

  const refreshToken = localStorage.getItem('refresh_token');
  const response = await apiClient.post('/auth/refresh', { refreshToken });
  const { access_token } = response.data;

  localStorage.setItem('access_token', access_token);
  isRefreshing = false;
  onTokenRefreshed(access_token);

  return access_token;
};
```

### Common Mistakes

❌ **Storing tokens in localStorage with XSS vulnerability:**
```typescript
// VULNERABLE: XSS can access localStorage
localStorage.setItem('token', token);
```

✅ **Use httpOnly cookies when possible:**
```python
# FastAPI sets httpOnly cookie
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,  # Not accessible via JavaScript
    secure=True,    # HTTPS only
    samesite="lax"
)
```

### Related Concepts

- [CORS and Preflight Requests](#cors-and-preflight-requests)
- See [docs/patterns.md](patterns.md) for auth patterns
- See [examples/intermediate/pattern-1.md](../examples/intermediate/pattern-1.md)

## State Management for APIs

### What It Is

State management for APIs involves handling loading states, caching responses, synchronizing server state with UI, and managing background updates.

### Why It Matters

Proper API state management:
- Prevents unnecessary API calls
- Provides instant UI feedback
- Handles loading and error states
- Synchronizes data across components
- Enables offline-first apps

### How It Works

**React Query (TanStack Query) manages server state:**
- Automatic caching
- Background refetching
- Stale-while-revalidate
- Optimistic updates
- Mutation handling

### Examples

**React Query Setup:**
```typescript
// src/index.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  );
}
```

**Using useQuery:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { getUsers } from './api/users';

function UserList() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['users'],
    queryFn: getUsers,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {data.map(user => <div key={user.id}>{user.name}</div>)}
      <button onClick={() => refetch()}>Refresh</button>
    </div>
  );
}
```

**Using useMutation:**
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function CreateUser() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleSubmit = (data) => {
    mutation.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      {mutation.isLoading && <p>Creating...</p>}
      {mutation.isError && <p>Error: {mutation.error.message}</p>}
      {mutation.isSuccess && <p>User created!</p>}
      {/* form fields */}
    </form>
  );
}
```

### Common Patterns

**Optimistic Updates:**
```typescript
const mutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newUser) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['users'] });

    // Snapshot previous value
    const previousUsers = queryClient.getQueryData(['users']);

    // Optimistically update
    queryClient.setQueryData(['users'], old =>
      old.map(user => user.id === newUser.id ? newUser : user)
    );

    return { previousUsers };
  },
  onError: (err, newUser, context) => {
    // Rollback on error
    queryClient.setQueryData(['users'], context.previousUsers);
  },
  onSettled: () => {
    // Refetch after error or success
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

### Related Concepts

- [Asynchronous JavaScript](#asynchronous-javascript)
- See [examples/intermediate/pattern-3.md](../examples/intermediate/pattern-3.md)

## Error Handling Philosophy

### What It Is

A systematic approach to handling API errors including network failures, validation errors, authentication failures, and server errors.

### Why It Matters

Proper error handling:
- Improves user experience
- Aids debugging
- Prevents app crashes
- Provides actionable feedback
- Logs issues for monitoring

### How It Works

**Error Types:**
1. Network errors (no response)
2. HTTP errors (4xx, 5xx status codes)
3. Validation errors (422)
4. Authentication errors (401, 403)
5. Timeout errors

### Examples

**Global Error Handler:**
```typescript
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error status
      switch (error.response.status) {
        case 400:
          console.error('Bad request:', error.response.data);
          break;
        case 401:
          console.error('Unauthorized');
          // Redirect to login
          break;
        case 403:
          console.error('Forbidden');
          break;
        case 404:
          console.error('Not found');
          break;
        case 422:
          console.error('Validation error:', error.response.data);
          break;
        case 500:
          console.error('Server error');
          break;
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server');
    } else {
      // Something else happened
      console.error('Request setup error:', error.message);
    }

    throw error;
  }
);
```

### Related Concepts

- See [docs/troubleshooting.md](troubleshooting.md)
- See [examples/intermediate/pattern-2.md](../examples/intermediate/pattern-2.md)

## TypeScript and Type Safety

### What It Is

TypeScript provides compile-time type checking for API requests and responses, preventing runtime errors and improving developer experience.

### Why It Matters

Type safety:
- Catches errors at compile time
- Provides autocomplete
- Documents API structure
- Prevents data mismatches
- Improves refactoring

### Examples

**Typed API Client:**
```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

const getUsers = async (): Promise<User[]> => {
  const response = await apiClient.get<User[]>('/users');
  return response.data;
};

const getUser = async (id: number): Promise<User> => {
  const response = await apiClient.get<User>(`/users/${id}`);
  return response.data;
};
```

**Generic API Response:**
```typescript
interface ApiResponse<T> {
  data: T;
  message: string;
  success: boolean;
}

const fetchUsers = async (): Promise<User[]> => {
  const response = await apiClient.get<ApiResponse<User[]>>('/users');
  return response.data.data;
};
```

### Related Concepts

- [API Contracts and OpenAPI](#api-contracts-and-openapi)
- See [docs/best-practices.md](best-practices.md)

## Environment Configuration

### What It Is

Managing different API URLs and configurations for development, staging, and production environments.

### Why It Matters

Environment configuration:
- Separates local and production APIs
- Enables testing without affecting production
- Manages feature flags
- Configures different services per environment

### Examples

**React Environment Variables:**
```bash
# .env.development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000

# .env.production
REACT_APP_API_URL=https://api.myapp.com
REACT_APP_API_TIMEOUT=30000
```

**Using Environment Variables:**
```typescript
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT || '10000'),
});
```

### Related Concepts

- [Axios Library Architecture](#axios-library-architecture)
- See [docs/best-practices.md](best-practices.md)

## Asynchronous JavaScript

### What It Is

JavaScript patterns for handling asynchronous operations like API calls using Promises and async/await.

### Why It Matters

Async programming is essential for:
- Non-blocking API calls
- Handling multiple requests
- Sequential vs parallel execution
- Error handling in async code

### Examples

**Promise vs Async/Await:**
```typescript
// Promise
function getUsersPromise() {
  return apiClient.get('/users')
    .then(response => response.data)
    .catch(error => console.error(error));
}

// Async/Await (preferred)
async function getUsersAsync() {
  try {
    const response = await apiClient.get('/users');
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
}
```

**Parallel vs Sequential:**
```typescript
// Sequential (slower)
const users = await getUsers();
const posts = await getPosts();

// Parallel (faster)
const [users, posts] = await Promise.all([
  getUsers(),
  getPosts()
]);
```

### Related Concepts

- [Request/Response Lifecycle](#requestresponse-lifecycle)
- [State Management for APIs](#state-management-for-apis)

---

These core concepts form the foundation for building robust API integrations. For practical applications, see the [examples](../examples/) directory and [best practices](best-practices.md) guide.
