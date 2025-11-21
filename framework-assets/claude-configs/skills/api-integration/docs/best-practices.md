# Best Practices - API Integration

Industry-standard best practices for building production-ready API integrations between React and FastAPI applications.

## Table of Contents

- [API Client Architecture](#api-client-architecture)
- [Error Handling Strategies](#error-handling-strategies)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)
- [Code Organization](#code-organization)
- [Testing Strategies](#testing-strategies)
- [Type Safety and Validation](#type-safety-and-validation)
- [Logging and Monitoring](#logging-and-monitoring)
- [Documentation Standards](#documentation-standards)
- [Deployment Checklist](#deployment-checklist)

## API Client Architecture

### Principle

Create a centralized, reusable API client with consistent configuration, interceptors, and error handling rather than making ad-hoc axios calls throughout your application.

### Why It Matters

Centralized API architecture provides:
- Single source of truth for API configuration
- Consistent authentication across all requests
- Global error handling
- Easier testing and mocking
- Simplified maintenance
- Better type safety

### How to Apply

**Create Layered API Architecture:**

```
src/api/
├── client.ts          # Base axios instance
├── interceptors.ts    # Request/response interceptors
├── types.ts           # Shared TypeScript types
├── services/          # Domain-specific services
│   ├── userService.ts
│   ├── authService.ts
│   └── postService.ts
└── hooks/             # React Query hooks
    ├── useUsers.ts
    ├── useAuth.ts
    └── usePosts.ts
```

**Good Example:**

```typescript
// src/api/client.ts
import axios from 'axios';
import { setupInterceptors } from './interceptors';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

setupInterceptors(apiClient);

// src/api/services/userService.ts
import { apiClient } from '../client';
import type { User, CreateUserDto } from '../types';

export class UserService {
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  }

  async getById(id: number): Promise<User> {
    const response = await apiClient.get<User>(`/users/${id}`);
    return response.data;
  }

  async create(data: CreateUserDto): Promise<User> {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  }

  async update(id: number, data: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(`/users/${id}`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/users/${id}`);
  }
}

export const userService = new UserService();

// src/components/UserList.tsx
import { userService } from '../api/services/userService';

function UserList() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    userService.getAll().then(setUsers);
  }, []);

  return (/* render users */);
}
```

**Bad Example:**

```typescript
// ANTI-PATTERN: Ad-hoc axios calls scattered throughout components
import axios from 'axios';

function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Configuration duplicated, no type safety, no error handling
    axios.get('http://localhost:8000/users')
      .then(response => setUsers(response.data));
  }, []);

  const handleDelete = (id) => {
    // Another ad-hoc call with different configuration
    axios.delete(`http://localhost:8000/users/${id}`)
      .then(() => {
        // Inline logic, hard to test
        setUsers(users.filter(u => u.id !== id));
      });
  };

  return (/* render */);
}
```

### Exceptions

For simple proof-of-concepts or single-page demos, a lightweight approach may be acceptable. However, always plan to refactor to proper architecture before production.

### Related Practices

- [Code Organization](#code-organization)
- [Type Safety and Validation](#type-safety-and-validation)
- See [docs/patterns.md](patterns.md) for architectural patterns

## Error Handling Strategies

### Principle

Implement comprehensive error handling at multiple levels: global interceptors, service layer, and UI components. Always provide meaningful feedback to users and log errors for debugging.

### Why It Matters

Robust error handling:
- Prevents app crashes
- Improves user experience
- Aids debugging
- Provides actionable feedback
- Enables monitoring and alerting

### How to Apply

**Multi-Layer Error Handling:**

```typescript
// Layer 1: Global Interceptor
// src/api/interceptors.ts
export const setupInterceptors = (client: AxiosInstance) => {
  client.interceptors.response.use(
    response => response,
    error => {
      // Log all errors
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
      });

      // Handle specific global cases
      if (error.response?.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      }

      // Transform error for consistency
      const apiError = new ApiError(
        error.response?.data?.message || 'An error occurred',
        error.response?.status,
        error.response?.data
      );

      return Promise.reject(apiError);
    }
  );
};

// Layer 2: Service Layer
// src/api/services/userService.ts
export class UserService {
  async getById(id: number): Promise<User> {
    try {
      const response = await apiClient.get<User>(`/users/${id}`);
      return response.data;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        throw new Error(`User with ID ${id} not found`);
      }
      throw error; // Re-throw for component to handle
    }
  }
}

// Layer 3: Component Layer
// src/components/UserProfile.tsx
function UserProfile({ userId }: { userId: number }) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        setError(null);
        const userData = await userService.getById(userId);
        setUser(userData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [userId]);

  if (loading) return <Skeleton />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  if (!user) return null;

  return <div>{user.name}</div>;
}
```

**Good Example - Error Boundaries:**

```typescript
// src/components/ErrorBoundary.tsx
import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Send to error tracking service
    // trackError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div>
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <UserProfile userId={1} />
    </ErrorBoundary>
  );
}
```

**Bad Example:**

```typescript
// ANTI-PATTERN: Silent failures, no user feedback
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    apiClient.get('/users')
      .then(response => setUsers(response.data))
      .catch(error => {
        // Silent failure - user sees nothing
        console.log(error);
      });
  }, []);

  // No loading state, no error state
  return <div>{users.map(u => <div>{u.name}</div>)}</div>;
}
```

### Exceptions

For internal admin tools or developer-only interfaces, less polished error messages may be acceptable. However, always log errors for debugging.

### Related Practices

- [Logging and Monitoring](#logging-and-monitoring)
- See [docs/troubleshooting.md](troubleshooting.md)
- See [examples/intermediate/pattern-2.md](../examples/intermediate/pattern-2.md)

## Security Best Practices

### Principle

Protect sensitive data, validate inputs, use HTTPS, secure authentication tokens, and follow OWASP guidelines for web security.

### Why It Matters

Security is critical for:
- Protecting user data
- Preventing unauthorized access
- Complying with regulations (GDPR, HIPAA)
- Maintaining user trust
- Preventing financial losses

### How to Apply

**Good Example - Secure Authentication:**

```typescript
// HTTPS Only
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL, // https://api.myapp.com
  timeout: 10000,
});

// Secure token storage (httpOnly cookies preferred)
// src/api/services/authService.ts
export class AuthService {
  async login(email: string, password: string): Promise<void> {
    // Don't log credentials
    const response = await apiClient.post('/auth/login', { email, password });

    // Store in httpOnly cookie (set by server) OR
    // Store in memory/sessionStorage (safer than localStorage)
    sessionStorage.setItem('access_token', response.data.access_token);

    // Never store in localStorage if XSS risk exists
  }

  async logout(): Promise<void> {
    sessionStorage.removeItem('access_token');
    await apiClient.post('/auth/logout');
  }

  getToken(): string | null {
    return sessionStorage.getItem('access_token');
  }
}

export const authService = new AuthService();

// Request interceptor - add auth header
apiClient.interceptors.request.use(config => {
  const token = authService.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Input sanitization
import DOMPurify from 'dompurify';

function CommentForm() {
  const handleSubmit = async (text: string) => {
    // Sanitize user input before sending
    const sanitized = DOMPurify.sanitize(text);
    await apiClient.post('/comments', { text: sanitized });
  };
}
```

**FastAPI Security:**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# HTTPS redirect in production
if os.getenv("ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.myapp.com", "www.myapp.com"]
)

# CORS with specific origins (not *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Input validation with Pydantic
from pydantic import BaseModel, EmailStr, validator

class CreateUserRequest(BaseModel):
    email: EmailStr  # Validates email format
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

**Bad Example:**

```typescript
// ANTI-PATTERN: Security vulnerabilities
const apiClient = axios.create({
  baseURL: 'http://api.myapp.com', // HTTP not HTTPS
});

// Storing sensitive data in localStorage (XSS vulnerable)
localStorage.setItem('password', password);
localStorage.setItem('api_key', apiKey);

// No input sanitization
const handleSubmit = (userInput) => {
  // Directly using user input (XSS risk)
  document.getElementById('output').innerHTML = userInput;
  apiClient.post('/comments', { text: userInput });
};

// Hardcoded credentials
const token = 'hardcoded-secret-token-123';

// CORS wildcard with credentials (not allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # ERROR
)
```

### Security Checklist

- [ ] Use HTTPS in production
- [ ] Never store passwords/secrets in code
- [ ] Use httpOnly cookies for tokens (when possible)
- [ ] Sanitize all user inputs
- [ ] Validate data on both client and server
- [ ] Implement CSRF protection
- [ ] Set security headers
- [ ] Use specific CORS origins (not *)
- [ ] Implement rate limiting
- [ ] Log security events
- [ ] Regular security audits
- [ ] Keep dependencies updated

### Related Practices

- [Type Safety and Validation](#type-safety-and-validation)
- See [docs/core-concepts.md](core-concepts.md#authentication-and-authorization)

## Performance Optimization

### Principle

Optimize API calls through caching, request deduplication, lazy loading, pagination, and efficient data fetching strategies.

### Why It Matters

Performance optimization:
- Reduces server load
- Improves user experience
- Decreases bandwidth usage
- Lowers infrastructure costs
- Improves SEO and metrics

### How to Apply

**Good Example - React Query Caching:**

```typescript
// src/index.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// src/hooks/useUsers.ts
import { useQuery } from '@tanstack/react-query';

export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => userService.getAll(),
    staleTime: 5 * 60 * 1000, // Cached for 5 minutes
  });
};

// Components automatically share cached data
function UserList() {
  const { data } = useUsers(); // Uses cache if fresh
  return (/* render */);
}

function UserCount() {
  const { data } = useUsers(); // Reuses same cached data
  return <div>Total: {data?.length}</div>;
}
```

**Pagination:**

```typescript
// Cursor-based pagination (preferred for large datasets)
interface PaginatedResponse<T> {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
}

export const useUsersPaginated = () => {
  return useInfiniteQuery({
    queryKey: ['users', 'paginated'],
    queryFn: ({ pageParam = null }) =>
      userService.getPaginated(pageParam),
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.next_cursor : undefined,
  });
};

function UserListInfinite() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useUsersPaginated();

  return (
    <div>
      {data?.pages.map(page =>
        page.items.map(user => <div key={user.id}>{user.name}</div>)
      )}
      {hasNextPage && (
        <button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
          {isFetchingNextPage ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

**Request Debouncing:**

```typescript
// Search with debounce
import { useDebounce } from 'use-debounce';

function UserSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch] = useDebounce(searchTerm, 500); // 500ms delay

  const { data } = useQuery({
    queryKey: ['users', 'search', debouncedSearch],
    queryFn: () => userService.search(debouncedSearch),
    enabled: debouncedSearch.length > 2, // Only search if 3+ chars
  });

  return (
    <input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search users..."
    />
  );
}
```

**Parallel Requests:**

```typescript
// Load multiple resources in parallel
async function loadDashboard() {
  const [users, posts, analytics] = await Promise.all([
    userService.getAll(),
    postService.getAll(),
    analyticsService.get(),
  ]);

  return { users, posts, analytics };
}

// React Query parallel queries
function Dashboard() {
  const users = useQuery({ queryKey: ['users'], queryFn: userService.getAll });
  const posts = useQuery({ queryKey: ['posts'], queryFn: postService.getAll });
  const analytics = useQuery({ queryKey: ['analytics'], queryFn: analyticsService.get });

  if (users.isLoading || posts.isLoading || analytics.isLoading) {
    return <Skeleton />;
  }

  return (/* render dashboard */);
}
```

**Request Cancellation:**

```typescript
// Cancel requests when component unmounts
function UserSearch() {
  useEffect(() => {
    const controller = new AbortController();

    apiClient.get('/users', { signal: controller.signal })
      .then(setUsers)
      .catch(error => {
        if (error.name !== 'AbortError') {
          console.error(error);
        }
      });

    return () => controller.abort(); // Cleanup
  }, []);
}
```

**Bad Example:**

```typescript
// ANTI-PATTERN: No caching, unnecessary requests
function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Fetches every time component renders
    apiClient.get('/users').then(response => setUsers(response.data));
  }); // Missing dependency array - runs on every render!

  return (/* render */);
}

// Multiple components fetch same data
function UserCount() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // Duplicate request for same data
    apiClient.get('/users').then(response => setUsers(response.data));
  }, []);

  return <div>{users.length}</div>;
}
```

### Performance Checklist

- [ ] Implement caching (React Query/SWR)
- [ ] Use pagination for large datasets
- [ ] Debounce search inputs
- [ ] Cancel requests on unmount
- [ ] Load data in parallel when possible
- [ ] Lazy load components and routes
- [ ] Minimize payload size
- [ ] Enable compression (gzip)
- [ ] Use CDN for static assets
- [ ] Monitor API performance

### Related Practices

- [Code Organization](#code-organization)
- See [docs/advanced-topics.md](advanced-topics.md)

## Code Organization

### Principle

Structure API-related code in a logical, maintainable way with clear separation of concerns between API clients, services, types, and UI components.

### Why It Matters

Good organization:
- Improves maintainability
- Makes code easier to find
- Facilitates testing
- Enables code reuse
- Helps onboarding

### How to Apply

**Recommended Structure:**

```
src/
├── api/
│   ├── client.ts                 # Axios instance
│   ├── interceptors.ts           # Request/response interceptors
│   ├── types.ts                  # Shared API types
│   ├── errors.ts                 # Custom error classes
│   ├── services/
│   │   ├── userService.ts        # User API calls
│   │   ├── authService.ts        # Auth API calls
│   │   ├── postService.ts        # Post API calls
│   │   └── index.ts              # Export all services
│   └── hooks/                    # React Query hooks
│       ├── useUsers.ts
│       ├── useAuth.ts
│       ├── usePosts.ts
│       └── index.ts
├── components/
│   ├── UserList.tsx              # UI components
│   ├── UserProfile.tsx
│   └── ...
├── types/
│   ├── user.ts                   # Domain types
│   ├── post.ts
│   └── index.ts
└── utils/
    ├── validators.ts
    └── formatters.ts
```

**Good Example:**

```typescript
// src/api/services/userService.ts
import { apiClient } from '../client';
import type { User, CreateUserDto, UpdateUserDto } from '../../types/user';

class UserService {
  private basePath = '/users';

  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>(this.basePath);
    return response.data;
  }

  async getById(id: number): Promise<User> {
    const response = await apiClient.get<User>(`${this.basePath}/${id}`);
    return response.data;
  }

  async create(data: CreateUserDto): Promise<User> {
    const response = await apiClient.post<User>(this.basePath, data);
    return response.data;
  }

  async update(id: number, data: UpdateUserDto): Promise<User> {
    const response = await apiClient.put<User>(`${this.basePath}/${id}`, data);
    return response.data;
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.basePath}/${id}`);
  }
}

export const userService = new UserService();

// src/api/services/index.ts
export { userService } from './userService';
export { authService } from './authService';
export { postService } from './postService';

// src/api/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services';

export const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: userService.getAll,
  });
};

export const useUser = (id: number) => {
  return useQuery({
    queryKey: ['users', id],
    queryFn: () => userService.getById(id),
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
};

// Usage in component
import { useUsers, useCreateUser } from '../api/hooks';

function UserList() {
  const { data, isLoading } = useUsers();
  const createUser = useCreateUser();

  // ...
}
```

**Bad Example:**

```typescript
// ANTI-PATTERN: Everything in one file
// src/api.ts (1000+ lines)
export const getUsers = async () => { /* ... */ };
export const getUser = async (id) => { /* ... */ };
export const createUser = async (data) => { /* ... */ };
export const getPosts = async () => { /* ... */ };
// ... 50 more functions

// ANTI-PATTERN: API calls in components
function UserList() {
  useEffect(() => {
    axios.get('http://localhost:8000/users')
      .then(response => setUsers(response.data));
  }, []);
}
```

### Naming Conventions

- Services: `userService`, `authService` (camelCase)
- Hooks: `useUsers`, `useCreateUser` (camelCase, starts with "use")
- Types: `User`, `CreateUserDto` (PascalCase)
- Files: `userService.ts`, `useUsers.ts` (camelCase)

### Related Practices

- [API Client Architecture](#api-client-architecture)
- [Testing Strategies](#testing-strategies)

## Testing Strategies

### Principle

Test API integrations at multiple levels: unit tests for services, integration tests for API calls, and end-to-end tests for user workflows.

### Why It Matters

Testing ensures:
- Code works as expected
- Regressions are caught early
- Refactoring is safe
- Documentation through examples
- Confidence in deployments

### How to Apply

**Good Example - Service Unit Tests:**

```typescript
// src/api/services/__tests__/userService.test.ts
import { userService } from '../userService';
import { apiClient } from '../../client';
import type { User } from '../../../types/user';

jest.mock('../../client');

describe('UserService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all users', async () => {
      const mockUsers: User[] = [
        { id: 1, name: 'John', email: 'john@example.com' },
        { id: 2, name: 'Jane', email: 'jane@example.com' },
      ];

      (apiClient.get as jest.Mock).mockResolvedValue({ data: mockUsers });

      const users = await userService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/users');
      expect(users).toEqual(mockUsers);
    });

    it('should handle errors', async () => {
      const error = new Error('Network error');
      (apiClient.get as jest.Mock).mockRejectedValue(error);

      await expect(userService.getAll()).rejects.toThrow('Network error');
    });
  });

  describe('create', () => {
    it('should create a new user', async () => {
      const newUser = { name: 'Bob', email: 'bob@example.com' };
      const createdUser = { id: 3, ...newUser };

      (apiClient.post as jest.Mock).mockResolvedValue({ data: createdUser });

      const result = await userService.create(newUser);

      expect(apiClient.post).toHaveBeenCalledWith('/users', newUser);
      expect(result).toEqual(createdUser);
    });
  });
});
```

**API Mocking with MSW:**

```typescript
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('http://localhost:8000/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'John', email: 'john@example.com' },
        { id: 2, name: 'Jane', email: 'jane@example.com' },
      ])
    );
  }),

  rest.post('http://localhost:8000/users', async (req, res, ctx) => {
    const body = await req.json();
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...body })
    );
  }),

  rest.delete('http://localhost:8000/users/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  }),
];

// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// src/setupTests.ts
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**React Query Hook Tests:**

```typescript
// src/api/hooks/__tests__/useUsers.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUsers } from '../useUsers';
import { userService } from '../../services/userService';

jest.mock('../../services/userService');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useUsers', () => {
  it('should fetch users successfully', async () => {
    const mockUsers = [{ id: 1, name: 'John', email: 'john@example.com' }];
    (userService.getAll as jest.Mock).mockResolvedValue(mockUsers);

    const { result } = renderHook(() => useUsers(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockUsers);
  });
});
```

**Integration Tests:**

```typescript
// src/components/__tests__/UserList.integration.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { UserList } from '../UserList';
import { server } from '../../mocks/server';
import { rest } from 'msw';

const renderWithClient = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('UserList Integration', () => {
  it('should display users fetched from API', async () => {
    renderWithClient(<UserList />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
      expect(screen.getByText('Jane')).toBeInTheDocument();
    });
  });

  it('should handle API errors', async () => {
    server.use(
      rest.get('http://localhost:8000/users', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    renderWithClient(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('should create new user', async () => {
    renderWithClient(<UserList />);

    await waitFor(() => screen.getByText('John'));

    const nameInput = screen.getByPlaceholderText('Name');
    const emailInput = screen.getByPlaceholderText('Email');
    const submitButton = screen.getByRole('button', { name: /create/i });

    await userEvent.type(nameInput, 'Bob');
    await userEvent.type(emailInput, 'bob@example.com');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });
});
```

### Testing Checklist

- [ ] Unit tests for all service methods
- [ ] Mock API responses with MSW
- [ ] Test error scenarios
- [ ] Test loading states
- [ ] Test optimistic updates
- [ ] Integration tests for user flows
- [ ] E2E tests for critical paths
- [ ] Test request/response interceptors
- [ ] Test authentication flows
- [ ] Test form validation

### Related Practices

- [Code Organization](#code-organization)
- See [resources/checklists.md](../resources/checklists.md)

## Type Safety and Validation

### Principle

Use TypeScript for compile-time type safety and runtime validation to prevent type-related bugs and ensure data integrity.

### Why It Matters

Type safety:
- Catches errors at compile time
- Provides IDE autocomplete
- Documents API structure
- Prevents runtime errors
- Improves refactoring

### How to Apply

**Good Example:**

```typescript
// src/types/user.ts
export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  created_at: string;
  updated_at: string;
}

export interface CreateUserDto {
  name: string;
  email: string;
  password: string;
  role?: 'admin' | 'user' | 'guest';
}

export interface UpdateUserDto {
  name?: string;
  email?: string;
  role?: 'admin' | 'user' | 'guest';
}

// src/api/services/userService.ts
import type { User, CreateUserDto, UpdateUserDto } from '../../types/user';

class UserService {
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  }

  async create(data: CreateUserDto): Promise<User> {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  }

  async update(id: number, data: UpdateUserDto): Promise<User> {
    const response = await apiClient.put<User>(`/users/${id}`, data);
    return response.data;
  }
}
```

**Runtime Validation with Zod:**

```typescript
// src/schemas/user.ts
import { z } from 'zod';

export const userSchema = z.object({
  id: z.number(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(['admin', 'user', 'guest']),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(['admin', 'user', 'guest']).optional(),
});

export type User = z.infer<typeof userSchema>;
export type CreateUserDto = z.infer<typeof createUserSchema>;

// Validate API responses
async function getUsers(): Promise<User[]> {
  const response = await apiClient.get('/users');

  // Runtime validation
  const users = z.array(userSchema).parse(response.data);

  return users;
}
```

**FastAPI Type Generation:**

```python
# backend/app/models/user.py
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: Literal['admin', 'user', 'guest'] = 'user'
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Literal['admin', 'user', 'guest'] = 'user'

# Generate TypeScript types from OpenAPI schema
# npm install -g openapi-typescript
# openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

### Related Practices

- [API Client Architecture](#api-client-architecture)
- See [docs/core-concepts.md](core-concepts.md#typescript-and-type-safety)

## Logging and Monitoring

### Principle

Implement comprehensive logging and monitoring to track API performance, errors, and usage patterns.

### Why It Matters

Logging and monitoring:
- Aids debugging
- Tracks performance
- Detects anomalies
- Provides usage analytics
- Enables proactive fixes

### How to Apply

**Good Example:**

```typescript
// src/api/interceptors.ts
import * as Sentry from '@sentry/react';

export const setupInterceptors = (client: AxiosInstance) => {
  // Request logging
  client.interceptors.request.use(config => {
    config.metadata = { startTime: Date.now() };

    if (process.env.NODE_ENV === 'development') {
      console.log(`→ ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    return config;
  });

  // Response logging and monitoring
  client.interceptors.response.use(
    response => {
      const duration = Date.now() - response.config.metadata.startTime;

      if (process.env.NODE_ENV === 'development') {
        console.log(
          `← ${response.status} ${response.config.url} (${duration}ms)`,
          response.data
        );
      }

      // Track performance
      if (duration > 2000) {
        Sentry.captureMessage(`Slow API call: ${response.config.url}`, {
          level: 'warning',
          extra: { duration, url: response.config.url },
        });
      }

      return response;
    },
    error => {
      const duration = Date.now() - error.config.metadata.startTime;

      console.error(
        `✗ ${error.config?.url} (${duration}ms):`,
        error.response?.status,
        error.response?.data || error.message
      );

      // Track errors
      Sentry.captureException(error, {
        extra: {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          data: error.response?.data,
        },
      });

      return Promise.reject(error);
    }
  );
};
```

### Related Practices

- [Error Handling Strategies](#error-handling-strategies)
- See [docs/advanced-topics.md](advanced-topics.md)

## Documentation Standards

### Principle

Document APIs, services, and integration patterns to improve team collaboration and reduce onboarding time.

### Why It Matters

Good documentation:
- Speeds up onboarding
- Reduces questions
- Prevents mistakes
- Serves as contract
- Enables self-service

### How to Apply

**Good Example:**

```typescript
/**
 * User Service
 *
 * Handles all user-related API operations including CRUD operations,
 * search, and authentication.
 *
 * @example
 * ```typescript
 * const users = await userService.getAll();
 * const user = await userService.create({ name: 'John', email: 'john@example.com' });
 * ```
 */
class UserService {
  /**
   * Fetch all users
   *
   * @returns Promise resolving to array of users
   * @throws {ApiError} If request fails
   *
   * @example
   * ```typescript
   * const users = await userService.getAll();
   * console.log(users.length);
   * ```
   */
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  }

  /**
   * Create a new user
   *
   * @param data - User creation data
   * @returns Promise resolving to created user with ID
   * @throws {ValidationError} If data is invalid
   * @throws {ApiError} If request fails
   *
   * @example
   * ```typescript
   * const newUser = await userService.create({
   *   name: 'John Doe',
   *   email: 'john@example.com',
   *   password: 'secure123'
   * });
   * console.log(newUser.id);
   * ```
   */
  async create(data: CreateUserDto): Promise<User> {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  }
}
```

### Related Practices

- [Code Organization](#code-organization)
- See [SKILL.md](../SKILL.md)

## Deployment Checklist

### Principle

Follow a comprehensive checklist before deploying API integrations to production.

### How to Apply

**Pre-Deployment Checklist:**

- [ ] **Environment Configuration**
  - [ ] Production API URL configured
  - [ ] Secrets stored securely (not in code)
  - [ ] CORS origins configured for production
  - [ ] HTTPS enforced

- [ ] **Security**
  - [ ] Authentication implemented
  - [ ] Authorization checked on all routes
  - [ ] Input validation on all forms
  - [ ] XSS protection enabled
  - [ ] CSRF protection enabled
  - [ ] Security headers set
  - [ ] Rate limiting configured

- [ ] **Performance**
  - [ ] Caching implemented
  - [ ] Pagination on large lists
  - [ ] Request debouncing on search
  - [ ] Image optimization
  - [ ] Compression enabled

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] E2E tests passing
  - [ ] Manual testing completed
  - [ ] Error scenarios tested

- [ ] **Monitoring**
  - [ ] Error tracking configured (Sentry)
  - [ ] Logging implemented
  - [ ] Performance monitoring enabled
  - [ ] Uptime monitoring configured

- [ ] **Documentation**
  - [ ] API documentation updated
  - [ ] README updated
  - [ ] Deployment guide written
  - [ ] Runbook created

### Related Practices

- [Security Best Practices](#security-best-practices)
- [Logging and Monitoring](#logging-and-monitoring)
- See [resources/checklists.md](../resources/checklists.md)

---

Following these best practices ensures robust, secure, and maintainable API integrations. For implementation examples, see the [examples](../examples/) directory.
