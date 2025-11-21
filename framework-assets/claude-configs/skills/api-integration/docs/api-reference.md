# API Reference - API Integration

Complete reference for axios API, custom utilities, and React Query hooks.

## Table of Contents

- [Axios Core API](#axios-core-api)
- [Custom API Client Methods](#custom-api-client-methods)
- [React Query Hooks](#react-query-hooks)
- [TypeScript Interfaces](#typescript-interfaces)
- [Environment Variables](#environment-variables)
- [Configuration Options](#configuration-options)
- [Utility Functions](#utility-functions)
- [Helper Methods](#helper-methods)

## Axios Core API

### axios.create()

Creates a new axios instance with custom configuration.

**Signature:**
```typescript
function create(config?: AxiosRequestConfig): AxiosInstance
```

**Parameters:**
- `config` (optional): Configuration object

**Returns:** Configured axios instance

**Example:**
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});
```

### instance.get()

Perform HTTP GET request.

**Signature:**
```typescript
function get<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Parameters:**
- `url`: Request URL
- `config` (optional): Request configuration

**Returns:** Promise resolving to response

**Examples:**

```typescript
// Basic GET
const response = await apiClient.get('/users');

// With query parameters
const response = await apiClient.get('/users', {
  params: { page: 1, limit: 10 }
});

// With TypeScript type
const response = await apiClient.get<User[]>('/users');
const users: User[] = response.data;

// With custom headers
const response = await apiClient.get('/users', {
  headers: { 'X-Custom-Header': 'value' }
});
```

### instance.post()

Perform HTTP POST request.

**Signature:**
```typescript
function post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Parameters:**
- `url`: Request URL
- `data` (optional): Request body
- `config` (optional): Request configuration

**Returns:** Promise resolving to response

**Examples:**

```typescript
// Create user
const response = await apiClient.post('/users', {
  name: 'John',
  email: 'john@example.com'
});

// With TypeScript
const response = await apiClient.post<User>('/users', {
  name: 'John',
  email: 'john@example.com'
});

// File upload
const formData = new FormData();
formData.append('file', fileBlob);

const response = await apiClient.post('/upload', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
```

### instance.put()

Perform HTTP PUT request (full update).

**Signature:**
```typescript
function put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Example:**
```typescript
const response = await apiClient.put('/users/1', {
  name: 'John Updated',
  email: 'john.updated@example.com'
});
```

### instance.patch()

Perform HTTP PATCH request (partial update).

**Signature:**
```typescript
function patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Example:**
```typescript
const response = await apiClient.patch('/users/1', {
  name: 'John Updated' // Only update name
});
```

### instance.delete()

Perform HTTP DELETE request.

**Signature:**
```typescript
function delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Example:**
```typescript
await apiClient.delete('/users/1');
```

### instance.request()

Perform request with full configuration.

**Signature:**
```typescript
function request<T = any>(config: AxiosRequestConfig): Promise<AxiosResponse<T>>
```

**Example:**
```typescript
const response = await apiClient.request({
  method: 'POST',
  url: '/users',
  data: { name: 'John' },
  headers: { 'X-Custom': 'value' }
});
```

### instance.interceptors

Configure request/response interceptors.

**Request Interceptor:**
```typescript
apiClient.interceptors.request.use(
  config => {
    // Modify config before request is sent
    config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  error => {
    // Handle request error
    return Promise.reject(error);
  }
);
```

**Response Interceptor:**
```typescript
apiClient.interceptors.response.use(
  response => {
    // Transform response data
    return response;
  },
  error => {
    // Handle response error
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

## Custom API Client Methods

### UserService

**getAll()**

Fetch all users.

```typescript
async getAll(): Promise<User[]>
```

**Example:**
```typescript
const users = await userService.getAll();
```

**getById()**

Fetch single user by ID.

```typescript
async getById(id: number): Promise<User>
```

**Example:**
```typescript
const user = await userService.getById(1);
```

**create()**

Create new user.

```typescript
async create(data: CreateUserDto): Promise<User>
```

**Example:**
```typescript
const newUser = await userService.create({
  name: 'John',
  email: 'john@example.com'
});
```

**update()**

Update existing user.

```typescript
async update(id: number, data: UpdateUserDto): Promise<User>
```

**Example:**
```typescript
const updated = await userService.update(1, {
  name: 'John Updated'
});
```

**delete()**

Delete user.

```typescript
async delete(id: number): Promise<void>
```

**Example:**
```typescript
await userService.delete(1);
```

**search()**

Search users by query.

```typescript
async search(query: string): Promise<User[]>
```

**Example:**
```typescript
const results = await userService.search('john');
```

### AuthService

**login()**

Authenticate user.

```typescript
async login(email: string, password: string): Promise<{ access_token: string }>
```

**Example:**
```typescript
const { access_token } = await authService.login(
  'user@example.com',
  'password123'
);
```

**logout()**

Logout user.

```typescript
async logout(): Promise<void>
```

**Example:**
```typescript
await authService.logout();
```

**refreshToken()**

Refresh access token.

```typescript
async refreshToken(): Promise<{ access_token: string }>
```

**Example:**
```typescript
const { access_token } = await authService.refreshToken();
```

**getToken()**

Get current access token.

```typescript
getToken(): string | null
```

**Example:**
```typescript
const token = authService.getToken();
```

## React Query Hooks

### useUsers()

Fetch all users with caching.

**Signature:**
```typescript
function useUsers(): UseQueryResult<User[], Error>
```

**Returns:**
- `data`: User array
- `isLoading`: Loading state
- `error`: Error object
- `refetch`: Manual refetch function

**Example:**
```typescript
function UserList() {
  const { data, isLoading, error, refetch } = useUsers();

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

### useUser()

Fetch single user by ID.

**Signature:**
```typescript
function useUser(id: number): UseQueryResult<User, Error>
```

**Example:**
```typescript
function UserProfile({ userId }: { userId: number }) {
  const { data: user, isLoading } = useUser(userId);

  if (isLoading) return <div>Loading...</div>;

  return <div>{user.name}</div>;
}
```

### useCreateUser()

Mutation hook for creating users.

**Signature:**
```typescript
function useCreateUser(): UseMutationResult<User, Error, CreateUserDto>
```

**Returns:**
- `mutate`: Trigger mutation
- `mutateAsync`: Async mutation
- `isLoading`: Loading state
- `error`: Error object
- `data`: Created user

**Example:**
```typescript
function CreateUserForm() {
  const createUser = useCreateUser();

  const handleSubmit = (data: CreateUserDto) => {
    createUser.mutate(data, {
      onSuccess: (user) => {
        console.log('Created:', user);
      },
      onError: (error) => {
        console.error('Failed:', error);
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {createUser.isLoading && <p>Creating...</p>}
      {createUser.error && <p>Error: {createUser.error.message}</p>}
      {/* form fields */}
    </form>
  );
}
```

### useUpdateUser()

Mutation hook for updating users.

**Signature:**
```typescript
function useUpdateUser(): UseMutationResult<User, Error, { id: number; data: UpdateUserDto }>
```

**Example:**
```typescript
function EditUserForm({ user }: { user: User }) {
  const updateUser = useUpdateUser();

  const handleSubmit = (data: UpdateUserDto) => {
    updateUser.mutate({ id: user.id, data });
  };

  return (/* form */);
}
```

### useDeleteUser()

Mutation hook for deleting users.

**Signature:**
```typescript
function useDeleteUser(): UseMutationResult<void, Error, number>
```

**Example:**
```typescript
function UserActions({ userId }: { userId: number }) {
  const deleteUser = useDeleteUser();

  const handleDelete = () => {
    if (confirm('Delete user?')) {
      deleteUser.mutate(userId);
    }
  };

  return <button onClick={handleDelete}>Delete</button>;
}
```

## TypeScript Interfaces

### AxiosRequestConfig

Request configuration options.

```typescript
interface AxiosRequestConfig {
  url?: string;
  method?: Method;
  baseURL?: string;
  headers?: Record<string, string>;
  params?: any;
  data?: any;
  timeout?: number;
  withCredentials?: boolean;
  responseType?: ResponseType;
  onUploadProgress?: (progressEvent: any) => void;
  onDownloadProgress?: (progressEvent: any) => void;
  maxRedirects?: number;
  signal?: AbortSignal;
}
```

### AxiosResponse

Response object structure.

```typescript
interface AxiosResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  config: AxiosRequestConfig;
}
```

### AxiosError

Error object structure.

```typescript
interface AxiosError extends Error {
  config: AxiosRequestConfig;
  code?: string;
  request?: any;
  response?: AxiosResponse;
  isAxiosError: boolean;
}
```

### User

User entity interface.

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  created_at: Date;
  updated_at: Date;
}
```

### CreateUserDto

User creation data transfer object.

```typescript
interface CreateUserDto {
  name: string;
  email: string;
  password: string;
  role?: 'admin' | 'user' | 'guest';
}
```

### UpdateUserDto

User update data transfer object.

```typescript
interface UpdateUserDto {
  name?: string;
  email?: string;
  role?: 'admin' | 'user' | 'guest';
}
```

### ApiError

Custom API error class.

```typescript
class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
```

## Environment Variables

### Frontend (React)

**REACT_APP_API_URL**

Backend API base URL.

- Type: `string`
- Default: `http://localhost:8000`
- Example: `https://api.myapp.com`

**REACT_APP_API_TIMEOUT**

Request timeout in milliseconds.

- Type: `number`
- Default: `10000` (10 seconds)
- Example: `30000`

**REACT_APP_WS_URL**

WebSocket server URL.

- Type: `string`
- Example: `ws://localhost:8000/ws`

### Backend (FastAPI)

**CORS_ORIGINS**

Allowed CORS origins (comma-separated).

- Type: `string`
- Example: `http://localhost:3000,http://localhost:3001`

**JWT_SECRET**

Secret key for JWT token signing.

- Type: `string`
- Required: Yes
- Example: `your-secret-key-here`

**JWT_EXPIRATION**

JWT token expiration time.

- Type: `number` (seconds)
- Default: `3600` (1 hour)

## Configuration Options

### QueryClient Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,   // Don't refetch on window focus
      retry: 1,                       // Retry failed requests once
      staleTime: 5 * 60 * 1000,      // Consider data fresh for 5 minutes
      cacheTime: 10 * 60 * 1000,     // Keep unused data in cache for 10 minutes
    },
    mutations: {
      retry: 0,                       // Don't retry mutations
    },
  },
});
```

### Axios Instance Configuration

```typescript
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  maxRedirects: 5,
});
```

## Utility Functions

### buildQueryString()

Build URL query string from object.

**Signature:**
```typescript
function buildQueryString(params: Record<string, any>): string
```

**Example:**
```typescript
const query = buildQueryString({ page: 1, limit: 10, sort: 'name' });
// Returns: "page=1&limit=10&sort=name"
```

### parseApiError()

Extract error message from API error.

**Signature:**
```typescript
function parseApiError(error: unknown): string
```

**Example:**
```typescript
try {
  await apiClient.get('/users');
} catch (error) {
  const message = parseApiError(error);
  console.error(message);
}
```

### isNetworkError()

Check if error is network-related.

**Signature:**
```typescript
function isNetworkError(error: AxiosError): boolean
```

**Example:**
```typescript
if (isNetworkError(error)) {
  console.log('Network issue detected');
}
```

### delay()

Create promise that resolves after specified time.

**Signature:**
```typescript
function delay(ms: number): Promise<void>
```

**Example:**
```typescript
await delay(1000); // Wait 1 second
```

## Helper Methods

### getAuthHeader()

Get authentication header object.

**Signature:**
```typescript
function getAuthHeader(): { Authorization: string } | {}
```

**Example:**
```typescript
const headers = getAuthHeader();
// Returns: { Authorization: "Bearer eyJhbGc..." }
```

### refreshAccessToken()

Refresh JWT access token.

**Signature:**
```typescript
async function refreshAccessToken(): Promise<string>
```

**Example:**
```typescript
const newToken = await refreshAccessToken();
localStorage.setItem('access_token', newToken);
```

### handleLogout()

Logout user and cleanup.

**Signature:**
```typescript
function handleLogout(): void
```

**Example:**
```typescript
handleLogout();
window.location.href = '/login';
```

---

For usage examples, see [examples/](../examples/). For implementation patterns, see [docs/patterns.md](patterns.md).
