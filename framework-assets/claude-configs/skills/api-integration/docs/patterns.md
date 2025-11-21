# Patterns - API Integration

Common architectural patterns and anti-patterns for building robust API integrations.

## Table of Contents

- [Service Layer Pattern](#service-layer-pattern)
- [Repository Pattern](#repository-pattern)
- [Factory Pattern for API Clients](#factory-pattern-for-api-clients)
- [Singleton vs Multiple Instances](#singleton-vs-multiple-instances)
- [Adapter Pattern](#adapter-pattern)
- [Facade Pattern](#facade-pattern)
- [Observer Pattern for Real-time](#observer-pattern-for-real-time)
- [Strategy Pattern for Auth](#strategy-pattern-for-auth)
- [Command Pattern for API Actions](#command-pattern-for-api-actions)
- [Interceptor Chain Pattern](#interceptor-chain-pattern)

## Service Layer Pattern

### When to Use

Use the service layer pattern when you need to encapsulate business logic and API calls in reusable, testable modules separate from UI components.

### Implementation

```typescript
// src/api/services/userService.ts
import { apiClient } from '../client';
import type { User, CreateUserDto, UpdateUserDto } from '../../types/user';

export class UserService {
  private readonly basePath = '/users';

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

  async search(query: string): Promise<User[]> {
    const response = await apiClient.get<User[]>(this.basePath, {
      params: { q: query }
    });
    return response.data;
  }
}

export const userService = new UserService();
```

### Benefits

- Centralized API logic
- Easy to test
- Reusable across components
- Type-safe
- Clear separation of concerns

### Anti-Pattern

```typescript
// DON'T: API calls scattered in components
function UserList() {
  useEffect(() => {
    axios.get('http://localhost:8000/users').then(setUsers);
  }, []);
}
```

## Repository Pattern

### When to Use

Use repository pattern when you need to abstract data access logic and potentially support multiple data sources (API, localStorage, IndexedDB).

### Implementation

```typescript
// src/repositories/userRepository.ts
import { apiClient } from '../api/client';
import type { User } from '../types/user';

export interface IUserRepository {
  getAll(): Promise<User[]>;
  getById(id: number): Promise<User>;
  save(user: User): Promise<User>;
  delete(id: number): Promise<void>;
}

export class ApiUserRepository implements IUserRepository {
  async getAll(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  }

  async getById(id: number): Promise<User> {
    const response = await apiClient.get<User>(`/users/${id}`);
    return response.data;
  }

  async save(user: User): Promise<User> {
    if (user.id) {
      const response = await apiClient.put<User>(`/users/${user.id}`, user);
      return response.data;
    } else {
      const response = await apiClient.post<User>('/users', user);
      return response.data;
    }
  }

  async delete(id: number): Promise<void> {
    await apiClient.delete(`/users/${id}`);
  }
}

// LocalStorage implementation for offline support
export class LocalStorageUserRepository implements IUserRepository {
  private readonly key = 'users';

  async getAll(): Promise<User[]> {
    const data = localStorage.getItem(this.key);
    return data ? JSON.parse(data) : [];
  }

  async getById(id: number): Promise<User> {
    const users = await this.getAll();
    const user = users.find(u => u.id === id);
    if (!user) throw new Error('User not found');
    return user;
  }

  async save(user: User): Promise<User> {
    const users = await this.getAll();
    if (user.id) {
      const index = users.findIndex(u => u.id === user.id);
      users[index] = user;
    } else {
      user.id = Date.now();
      users.push(user);
    }
    localStorage.setItem(this.key, JSON.stringify(users));
    return user;
  }

  async delete(id: number): Promise<void> {
    const users = await this.getAll();
    const filtered = users.filter(u => u.id !== id);
    localStorage.setItem(this.key, JSON.stringify(filtered));
  }
}

// Usage - easily switch between implementations
const userRepository: IUserRepository =
  navigator.onLine
    ? new ApiUserRepository()
    : new LocalStorageUserRepository();
```

### Benefits

- Data source abstraction
- Offline support
- Easy to mock for testing
- Flexible data sources

## Factory Pattern for API Clients

### When to Use

Use factory pattern when you need to create multiple API client instances with different configurations.

### Implementation

```typescript
// src/api/clientFactory.ts
import axios, { AxiosInstance } from 'axios';

export interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  withCredentials?: boolean;
  headers?: Record<string, string>;
}

export class ApiClientFactory {
  static create(config: ApiClientConfig): AxiosInstance {
    const client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 10000,
      withCredentials: config.withCredentials || false,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers,
      },
    });

    // Add common interceptors
    this.setupInterceptors(client);

    return client;
  }

  static createAuth(token: string): AxiosInstance {
    return this.create({
      baseURL: process.env.REACT_APP_API_URL!,
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  static createPublic(): AxiosInstance {
    return this.create({
      baseURL: process.env.REACT_APP_API_URL!,
    });
  }

  private static setupInterceptors(client: AxiosInstance): void {
    client.interceptors.request.use(config => {
      console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    });

    client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }
}

// Usage
const publicClient = ApiClientFactory.createPublic();
const authClient = ApiClientFactory.createAuth(userToken);
```

### Benefits

- Flexible client creation
- Consistent configuration
- Easy to extend
- Testable

## Singleton vs Multiple Instances

### Singleton Pattern (Recommended for Most Cases)

```typescript
// src/api/client.ts
import axios from 'axios';

// Single instance shared across application
export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// All services use same instance
import { apiClient } from './client';
export const userService = {
  getAll: () => apiClient.get('/users'),
};
```

### Multiple Instances (For Different APIs)

```typescript
// src/api/clients.ts
import axios from 'axios';

// Main API
export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// Analytics API
export const analyticsClient = axios.create({
  baseURL: process.env.REACT_APP_ANALYTICS_URL,
  timeout: 5000,
});

// Payment API
export const paymentClient = axios.create({
  baseURL: process.env.REACT_APP_PAYMENT_URL,
  timeout: 30000,
});
```

### When to Use Each

**Singleton:**
- Single backend API
- Consistent configuration
- Shared interceptors

**Multiple Instances:**
- Different backends (microservices)
- Different timeouts/configs
- Separate auth requirements

## Adapter Pattern

### When to Use

Use adapter pattern to create a consistent interface over different API implementations or external SDKs.

### Implementation

```typescript
// src/adapters/apiAdapter.ts
export interface IApiAdapter {
  get<T>(url: string, params?: any): Promise<T>;
  post<T>(url: string, data?: any): Promise<T>;
  put<T>(url: string, data?: any): Promise<T>;
  delete(url: string): Promise<void>;
}

// Axios adapter
export class AxiosAdapter implements IApiAdapter {
  constructor(private client: AxiosInstance) {}

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  async delete(url: string): Promise<void> {
    await this.client.delete(url);
  }
}

// Fetch adapter (alternative implementation)
export class FetchAdapter implements IApiAdapter {
  constructor(private baseURL: string) {}

  async get<T>(url: string, params?: any): Promise<T> {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}${url}?${query}`);
    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Request failed');
    return response.json();
  }

  async delete(url: string): Promise<void> {
    const response = await fetch(`${this.baseURL}${url}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Request failed');
  }
}

// Usage - easily swap implementations
const api: IApiAdapter = new AxiosAdapter(apiClient);
// const api: IApiAdapter = new FetchAdapter('http://localhost:8000');

const users = await api.get<User[]>('/users');
```

### Benefits

- Implementation independence
- Easy to swap HTTP libraries
- Testable with mocks
- Consistent interface

## Facade Pattern

### When to Use

Use facade pattern to simplify complex API interactions or combine multiple API calls.

### Implementation

```typescript
// src/api/facades/dashboardFacade.ts
import { userService } from '../services/userService';
import { postService } from '../services/postService';
import { analyticsService } from '../services/analyticsService';

export interface DashboardData {
  users: User[];
  recentPosts: Post[];
  analytics: Analytics;
  summary: DashboardSummary;
}

export class DashboardFacade {
  async loadDashboard(): Promise<DashboardData> {
    // Load multiple resources in parallel
    const [users, posts, analytics] = await Promise.all([
      userService.getAll(),
      postService.getRecent(10),
      analyticsService.get(),
    ]);

    // Combine and transform data
    const summary: DashboardSummary = {
      totalUsers: users.length,
      activeUsers: users.filter(u => u.isActive).length,
      totalPosts: analytics.totalPosts,
      postsToday: posts.filter(p => this.isToday(p.created_at)).length,
    };

    return {
      users,
      recentPosts: posts,
      analytics,
      summary,
    };
  }

  private isToday(date: string): boolean {
    const today = new Date().toDateString();
    return new Date(date).toDateString() === today;
  }
}

export const dashboardFacade = new DashboardFacade();

// Usage in component
function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    dashboardFacade.loadDashboard().then(setData);
  }, []);

  return (/* render dashboard with data */);
}
```

### Benefits

- Simplifies complex operations
- Combines related API calls
- Reduces component complexity
- Reusable business logic

## Observer Pattern for Real-time

### When to Use

Use observer pattern for WebSocket connections or real-time event handling.

### Implementation

```typescript
// src/api/websocket/websocketClient.ts
export type WebSocketEventHandler = (data: any) => void;

export class WebSocketClient {
  private socket: WebSocket | null = null;
  private listeners: Map<string, WebSocketEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(private url: string) {}

  connect(): void {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.notify(message.type, message.data);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(event: string, handler: WebSocketEventHandler): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(handler);
  }

  off(event: string, handler: WebSocketEventHandler): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  send(type: string, data: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, data }));
    }
  }

  private notify(event: string, data: any): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  private reconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms...`);
      setTimeout(() => this.connect(), delay);
    }
  }
}

// Usage
const ws = new WebSocketClient('ws://localhost:8000/ws');

ws.on('user:created', (user) => {
  console.log('New user:', user);
});

ws.on('post:updated', (post) => {
  console.log('Post updated:', post);
});

ws.connect();
```

### Benefits

- Decoupled event handling
- Multiple subscribers
- Easy to add/remove listeners
- Automatic reconnection

## Strategy Pattern for Auth

### When to Use

Use strategy pattern when you need to support multiple authentication methods.

### Implementation

```typescript
// src/auth/strategies/authStrategy.ts
export interface IAuthStrategy {
  login(credentials: any): Promise<{ token: string }>;
  logout(): Promise<void>;
  refreshToken(): Promise<{ token: string }>;
  getToken(): string | null;
}

// JWT Strategy
export class JwtAuthStrategy implements IAuthStrategy {
  async login(credentials: { email: string; password: string }): Promise<{ token: string }> {
    const response = await apiClient.post('/auth/login', credentials);
    localStorage.setItem('access_token', response.data.access_token);
    return { token: response.data.access_token };
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
    await apiClient.post('/auth/logout');
  }

  async refreshToken(): Promise<{ token: string }> {
    const refresh = localStorage.getItem('refresh_token');
    const response = await apiClient.post('/auth/refresh', { refresh });
    localStorage.setItem('access_token', response.data.access_token);
    return { token: response.data.access_token };
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

// OAuth Strategy
export class OAuthStrategy implements IAuthStrategy {
  async login(credentials: { provider: string }): Promise<{ token: string }> {
    // Redirect to OAuth provider
    window.location.href = `/auth/oauth/${credentials.provider}`;
    return { token: '' }; // Token returned via callback
  }

  async logout(): Promise<void> {
    localStorage.removeItem('oauth_token');
  }

  async refreshToken(): Promise<{ token: string }> {
    // OAuth refresh logic
    return { token: '' };
  }

  getToken(): string | null {
    return localStorage.getItem('oauth_token');
  }
}

// Auth Context using strategy
export class AuthManager {
  constructor(private strategy: IAuthStrategy) {}

  setStrategy(strategy: IAuthStrategy): void {
    this.strategy = strategy;
  }

  async login(credentials: any): Promise<{ token: string }> {
    return this.strategy.login(credentials);
  }

  async logout(): Promise<void> {
    return this.strategy.logout();
  }

  getToken(): string | null {
    return this.strategy.getToken();
  }
}

// Usage
const authManager = new AuthManager(new JwtAuthStrategy());

// Switch to OAuth if needed
authManager.setStrategy(new OAuthStrategy());
```

### Benefits

- Multiple auth methods
- Easy to extend
- Testable
- Clear separation

## Command Pattern for API Actions

### When to Use

Use command pattern for undo/redo functionality or complex API operations.

### Implementation

```typescript
// src/commands/apiCommand.ts
export interface ICommand {
  execute(): Promise<void>;
  undo(): Promise<void>;
}

export class CreateUserCommand implements ICommand {
  private createdUser?: User;

  constructor(private userData: CreateUserDto) {}

  async execute(): Promise<void> {
    this.createdUser = await userService.create(this.userData);
  }

  async undo(): Promise<void> {
    if (this.createdUser) {
      await userService.delete(this.createdUser.id);
    }
  }
}

export class UpdateUserCommand implements ICommand {
  private previousData?: User;

  constructor(
    private userId: number,
    private newData: UpdateUserDto
  ) {}

  async execute(): Promise<void> {
    this.previousData = await userService.getById(this.userId);
    await userService.update(this.userId, this.newData);
  }

  async undo(): Promise<void> {
    if (this.previousData) {
      await userService.update(this.userId, this.previousData);
    }
  }
}

export class CommandManager {
  private history: ICommand[] = [];
  private currentIndex = -1;

  async execute(command: ICommand): Promise<void> {
    await command.execute();
    this.history = this.history.slice(0, this.currentIndex + 1);
    this.history.push(command);
    this.currentIndex++;
  }

  async undo(): Promise<void> {
    if (this.canUndo()) {
      const command = this.history[this.currentIndex];
      await command.undo();
      this.currentIndex--;
    }
  }

  async redo(): Promise<void> {
    if (this.canRedo()) {
      this.currentIndex++;
      const command = this.history[this.currentIndex];
      await command.execute();
    }
  }

  canUndo(): boolean {
    return this.currentIndex >= 0;
  }

  canRedo(): boolean {
    return this.currentIndex < this.history.length - 1;
  }
}

// Usage
const commandManager = new CommandManager();

const createCommand = new CreateUserCommand({ name: 'John', email: 'john@example.com' });
await commandManager.execute(createCommand);

// Undo creation
await commandManager.undo();

// Redo creation
await commandManager.redo();
```

### Benefits

- Undo/redo support
- Command history
- Complex operations
- Testable

## Interceptor Chain Pattern

### When to Use

Use interceptor chain when you need multiple transformations or checks on requests/responses.

### Implementation

```typescript
// src/api/interceptors/interceptorChain.ts
export interface RequestInterceptor {
  onRequest(config: AxiosRequestConfig): AxiosRequestConfig | Promise<AxiosRequestConfig>;
}

export interface ResponseInterceptor {
  onResponse(response: AxiosResponse): AxiosResponse | Promise<AxiosResponse>;
  onError(error: any): any;
}

// Auth interceptor
export class AuthInterceptor implements RequestInterceptor {
  onRequest(config: AxiosRequestConfig): AxiosRequestConfig {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
}

// Logging interceptor
export class LoggingInterceptor implements RequestInterceptor, ResponseInterceptor {
  onRequest(config: AxiosRequestConfig): AxiosRequestConfig {
    console.log(`→ ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  }

  onResponse(response: AxiosResponse): AxiosResponse {
    console.log(`← ${response.status} ${response.config.url}`);
    return response;
  }

  onError(error: any): any {
    console.error(`✗ ${error.config?.url}:`, error.message);
    throw error;
  }
}

// Retry interceptor
export class RetryInterceptor implements ResponseInterceptor {
  private maxRetries = 3;

  onResponse(response: AxiosResponse): AxiosResponse {
    return response;
  }

  async onError(error: any): Promise<any> {
    const config = error.config;

    if (!config || !config.retryCount) {
      config.retryCount = 0;
    }

    if (config.retryCount < this.maxRetries) {
      config.retryCount++;
      const delay = Math.pow(2, config.retryCount) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      return apiClient.request(config);
    }

    throw error;
  }
}

// Setup chain
export function setupInterceptorChain(client: AxiosInstance): void {
  const requestInterceptors: RequestInterceptor[] = [
    new AuthInterceptor(),
    new LoggingInterceptor(),
  ];

  const responseInterceptors: ResponseInterceptor[] = [
    new LoggingInterceptor(),
    new RetryInterceptor(),
  ];

  requestInterceptors.forEach(interceptor => {
    client.interceptors.request.use(
      config => interceptor.onRequest(config)
    );
  });

  responseInterceptors.forEach(interceptor => {
    client.interceptors.response.use(
      response => interceptor.onResponse(response),
      error => interceptor.onError(error)
    );
  });
}
```

### Benefits

- Modular interceptors
- Easy to add/remove
- Clear responsibilities
- Testable

---

These patterns provide proven solutions for common API integration challenges. For practical implementations, see the [examples](../examples/) directory.
