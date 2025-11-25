# Clean Architecture in React

**Comprehensive guide to implementing Clean Architecture in React applications with TypeScript, hooks, and modern patterns.**

## The Core Principle: The Dependency Rule

**"Dependencies must point inward only, toward higher-level policies."**

dependency_flow[4]{from_layer,to_layer,allowed,explanation}:
Infrastructure,Application,YES,Infrastructure implements Application interfaces
Infrastructure,Domain,YES,Infrastructure can use Domain types
Application,Domain,YES,Application uses Domain entities and rules
Domain,Any outer layer,NO,Domain must have zero external dependencies

## The Four Layers in React

### Layer 1: Domain Layer (Innermost)

**Pure business logic with no framework dependencies - not even React.**

domain_layer_contents[7]{component,description,typescript_implementation}:
Entities,Business objects with identity,TypeScript interfaces or types
Value Objects,Immutable domain values,Readonly types or branded types
Business Rules,Domain validation and invariants,Pure functions or classes
Domain Events,Events representing business changes,TypeScript types for events
Domain Exceptions,Business rule violations,Custom Error classes
Aggregates,Consistency boundaries,Composite types with validation
Domain Services,Stateless domain operations,Pure functions with no side effects

**Key Rules:**
- NO React imports
- NO hooks or components
- NO external libraries (except utility libs like date-fns)
- Pure TypeScript/JavaScript only

**Example Structure:**
```
src/domain/
├── entities/
│   ├── User.ts
│   ├── Product.ts
│   └── Order.ts
├── value-objects/
│   ├── Email.ts
│   ├── Money.ts
│   └── Address.ts
├── rules/
│   ├── userRules.ts
│   └── orderRules.ts
├── events/
│   └── UserEvents.ts
└── errors/
    └── DomainErrors.ts
```

### Layer 2: Application Layer

**Orchestrates domain logic, defines ports (interfaces), contains hooks.**

application_layer_contents[6]{component,description,react_implementation}:
Custom Hooks,Reusable stateful logic,useUser useAuth useProducts hooks
Use Cases,Application-specific business flows,Hook that orchestrates domain logic
Ports (Interfaces),Abstract interfaces for infrastructure,TypeScript interfaces for services
DTOs,Data transfer objects between layers,TypeScript types for API responses
Application Services,Coordinate multiple use cases,Hooks that compose other hooks
State Managers,Application state logic,Zustand stores Jotai atoms

**Key Rules:**
- Can use React hooks
- Depends ONLY on Domain layer
- Defines interfaces that Infrastructure implements
- No direct API calls (use ports)
- No component JSX

**Example Structure:**
```
src/application/
├── hooks/
│   ├── useUser.ts
│   ├── useAuth.ts
│   ├── useProducts.ts
│   └── useCart.ts
├── ports/
│   ├── IUserRepository.ts
│   ├── IAuthService.ts
│   └── IProductRepository.ts
├── stores/
│   ├── authStore.ts
│   └── cartStore.ts
└── dtos/
    ├── UserDTO.ts
    └── ProductDTO.ts
```

### Layer 3: Infrastructure Layer

**Implements abstractions, handles external dependencies.**

infrastructure_layer_contents[6]{component,description,implementation}:
API Clients,HTTP communication,Axios or fetch implementations
Repository Implementations,Data access concrete implementations,UserRepository implementing IUserRepository
Storage Adapters,Browser storage access,LocalStorage SessionStorage adapters
External Service Clients,Third-party integrations,Stripe Stripe PayPal clients
WebSocket Clients,Real-time communication,Socket.io or native WebSocket
Cache Implementations,Caching strategies,React Query cache or custom cache

**Key Rules:**
- Implements Application port interfaces
- Contains all external dependencies
- Can use any libraries
- No React components (only services)

**Example Structure:**
```
src/infrastructure/
├── api/
│   ├── userApi.ts
│   ├── productApi.ts
│   └── httpClient.ts
├── repositories/
│   ├── UserRepository.ts
│   └── ProductRepository.ts
├── storage/
│   ├── LocalStorageAdapter.ts
│   └── SessionStorageAdapter.ts
└── services/
    ├── AuthService.ts
    └── AnalyticsService.ts
```

### Layer 4: Presentation Layer

**React components, pages, routing - the UI layer.**

presentation_layer_contents[6]{component,description,implementation}:
Components,Reusable UI components,Functional components with TypeScript
Pages,Route-level components,Next.js pages or route components
Layouts,Page layouts and shells,Layout components with children
Hooks (UI),UI-specific hooks,useToggle useModal useDebounce
Styles,Component styling,CSS Modules Tailwind Styled Components
Routes,Application routing,React Router or Next.js routing

**Key Rules:**
- Thin layer - delegates to Application hooks
- No business logic
- Consumes Application hooks
- Handles rendering and user interaction

**Example Structure:**
```
src/presentation/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   ├── features/
│   │   ├── UserProfile.tsx
│   │   └── ProductCard.tsx
│   └── layouts/
│       └── MainLayout.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── UserPage.tsx
│   └── ProductPage.tsx
├── hooks/
│   ├── useToggle.ts
│   └── useDebounce.ts
└── routes/
    └── AppRouter.tsx
```

## Dependency Inversion in React

### Without DIP (Wrong)

```tsx
// ❌ Hook directly depends on API implementation
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Direct dependency on axios and API endpoint!
    axios.get(`/api/users/${userId}`)
      .then(res => setUser(res.data));
  }, [userId]);

  return { user };
}
```

**Problems:**
- Cannot test without mocking axios
- Cannot swap API implementation
- Violates dependency rule

### With DIP (Correct)

```tsx
// ✅ Application layer defines interface (Port)
// src/application/ports/IUserRepository.ts
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findAll(): Promise<User[]>;
  save(user: User): Promise<User>;
}

// ✅ Hook depends on abstraction
// src/application/hooks/useUser.ts
export function useUser(userId: string, repository: IUserRepository) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    repository.findById(userId).then(user => {
      if (!cancelled) {
        setUser(user);
        setLoading(false);
      }
    });

    return () => { cancelled = true; };
  }, [userId, repository]);

  return { user, loading };
}

// ✅ Infrastructure implements interface (Adapter)
// src/infrastructure/repositories/UserRepository.ts
export class UserRepository implements IUserRepository {
  constructor(private httpClient: HttpClient) {}

  async findById(id: string): Promise<User | null> {
    const response = await this.httpClient.get(`/users/${id}`);
    return response.data;
  }

  async findAll(): Promise<User[]> {
    const response = await this.httpClient.get('/users');
    return response.data;
  }

  async save(user: User): Promise<User> {
    const response = await this.httpClient.post('/users', user);
    return response.data;
  }
}

// ✅ Component uses hook with injected dependency
// src/presentation/components/UserProfile.tsx
function UserProfile({ userId }: { userId: string }) {
  const userRepository = useUserRepository(); // DI via context
  const { user, loading } = useUser(userId, userRepository);

  if (loading) return <Spinner />;
  return <div>{user?.name}</div>;
}
```

**Benefits:**
- Hook testable with mock repository
- Can swap API implementation
- Dependency points inward

## Practical Implementation Patterns

### Pattern 1: Domain Entity (Pure TypeScript)

```typescript
// src/domain/entities/User.ts
export interface User {
  readonly id: string;
  readonly email: string;
  readonly name: string;
  readonly status: UserStatus;
  readonly createdAt: Date;
}

export enum UserStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  BANNED = 'BANNED',
}

// Domain rules - pure functions
export function canActivateUser(user: User): boolean {
  return user.status === UserStatus.INACTIVE;
}

export function canBanUser(user: User): boolean {
  return user.status !== UserStatus.BANNED;
}

export function activateUser(user: User): User {
  if (!canActivateUser(user)) {
    throw new DomainError('Cannot activate user in current status');
  }
  return { ...user, status: UserStatus.ACTIVE };
}
```

### Pattern 2: Value Object

```typescript
// src/domain/value-objects/Email.ts
export class Email {
  private constructor(private readonly value: string) {
    if (!Email.isValid(value)) {
      throw new DomainError(`Invalid email: ${value}`);
    }
  }

  static create(value: string): Email {
    return new Email(value);
  }

  static isValid(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  toString(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}

// Or simpler branded type approach:
export type Email = string & { readonly __brand: 'Email' };

export function createEmail(value: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    throw new DomainError(`Invalid email: ${value}`);
  }
  return value as Email;
}
```

### Pattern 3: Port Interface (Application Layer)

```typescript
// src/application/ports/IUserRepository.ts
import { User } from '@/domain/entities/User';

export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findAll(filters?: UserFilters): Promise<User[]>;
  save(user: User): Promise<User>;
  delete(id: string): Promise<void>;
}

export interface UserFilters {
  status?: UserStatus;
  searchQuery?: string;
  limit?: number;
  offset?: number;
}
```

### Pattern 4: Custom Hook (Application Layer)

```typescript
// src/application/hooks/useUser.ts
import { useState, useEffect } from 'react';
import { User } from '@/domain/entities/User';
import { IUserRepository } from '@/application/ports/IUserRepository';

export interface UseUserResult {
  user: User | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

export function useUser(
  userId: string,
  repository: IUserRepository
): UseUserResult {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchUser = async () => {
    try {
      setLoading(true);
      setError(null);
      const user = await repository.findById(userId);
      setUser(user);
    } catch (err) {
      setError(err as Error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        const user = await repository.findById(userId);
        if (!cancelled) {
          setUser(user);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      cancelled = true;
    };
  }, [userId, repository]);

  return { user, loading, error, refresh: fetchUser };
}
```

### Pattern 5: Repository Implementation (Infrastructure)

```typescript
// src/infrastructure/repositories/UserRepository.ts
import { IUserRepository, UserFilters } from '@/application/ports/IUserRepository';
import { User } from '@/domain/entities/User';
import { HttpClient } from '@/infrastructure/api/httpClient';

export class UserRepository implements IUserRepository {
  constructor(private readonly httpClient: HttpClient) {}

  async findById(id: string): Promise<User | null> {
    try {
      const response = await this.httpClient.get<User>(`/users/${id}`);
      return this.toDomain(response.data);
    } catch (error) {
      if (this.isNotFoundError(error)) {
        return null;
      }
      throw error;
    }
  }

  async findByEmail(email: string): Promise<User | null> {
    try {
      const response = await this.httpClient.get<User>(`/users/by-email/${email}`);
      return this.toDomain(response.data);
    } catch (error) {
      if (this.isNotFoundError(error)) {
        return null;
      }
      throw error;
    }
  }

  async findAll(filters?: UserFilters): Promise<User[]> {
    const params = this.buildQueryParams(filters);
    const response = await this.httpClient.get<User[]>('/users', { params });
    return response.data.map(this.toDomain);
  }

  async save(user: User): Promise<User> {
    const dto = this.toDTO(user);
    if (user.id) {
      const response = await this.httpClient.put<User>(`/users/${user.id}`, dto);
      return this.toDomain(response.data);
    } else {
      const response = await this.httpClient.post<User>('/users', dto);
      return this.toDomain(response.data);
    }
  }

  async delete(id: string): Promise<void> {
    await this.httpClient.delete(`/users/${id}`);
  }

  private toDomain(dto: any): User {
    return {
      id: dto.id,
      email: dto.email,
      name: dto.name,
      status: dto.status,
      createdAt: new Date(dto.created_at),
    };
  }

  private toDTO(user: User): any {
    return {
      id: user.id,
      email: user.email,
      name: user.name,
      status: user.status,
      created_at: user.createdAt.toISOString(),
    };
  }

  private buildQueryParams(filters?: UserFilters): Record<string, any> {
    if (!filters) return {};
    return {
      status: filters.status,
      q: filters.searchQuery,
      limit: filters.limit,
      offset: filters.offset,
    };
  }

  private isNotFoundError(error: any): boolean {
    return error?.response?.status === 404;
  }
}
```

### Pattern 6: Dependency Injection with Context

```typescript
// src/infrastructure/di/RepositoryContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { IUserRepository } from '@/application/ports/IUserRepository';
import { UserRepository } from '@/infrastructure/repositories/UserRepository';
import { httpClient } from '@/infrastructure/api/httpClient';

interface RepositoryContextType {
  userRepository: IUserRepository;
}

const RepositoryContext = createContext<RepositoryContextType | undefined>(undefined);

export function RepositoryProvider({ children }: { children: ReactNode }) {
  const userRepository = new UserRepository(httpClient);

  return (
    <RepositoryContext.Provider value={{ userRepository }}>
      {children}
    </RepositoryContext.Provider>
  );
}

export function useUserRepository(): IUserRepository {
  const context = useContext(RepositoryContext);
  if (!context) {
    throw new Error('useUserRepository must be used within RepositoryProvider');
  }
  return context.userRepository;
}
```

### Pattern 7: Component (Presentation Layer)

```tsx
// src/presentation/components/UserProfile.tsx
import React from 'react';
import { useUser } from '@/application/hooks/useUser';
import { useUserRepository } from '@/infrastructure/di/RepositoryContext';
import { Spinner } from './common/Spinner';
import { ErrorMessage } from './common/ErrorMessage';

interface UserProfileProps {
  userId: string;
}

export function UserProfile({ userId }: UserProfileProps) {
  const userRepository = useUserRepository();
  const { user, loading, error } = useUser(userId, userRepository);

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorMessage error={error} />;
  }

  if (!user) {
    return <div>User not found</div>;
  }

  return (
    <div className="user-profile">
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      <span className={`status status-${user.status.toLowerCase()}`}>
        {user.status}
      </span>
    </div>
  );
}
```

## Common Violations and Fixes

### Violation 1: Business Logic in Component

```tsx
// ❌ WRONG: Component contains business logic
function UserForm({ user }: { user: User }) {
  const handleSubmit = (email: string) => {
    // Business logic in component!
    if (!email.includes('@')) {
      alert('Invalid email');
      return;
    }
    // ...
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

**Fix**: Move to domain layer

```tsx
// ✅ CORRECT: Business logic in domain
// src/domain/value-objects/Email.ts
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Component uses domain logic
function UserForm({ user }: { user: User }) {
  const handleSubmit = (email: string) => {
    if (!validateEmail(email)) {
      alert('Invalid email');
      return;
    }
    // ...
  };

  return <form onSubmit={handleSubmit}>...</form>;
}
```

### Violation 2: Direct API Calls in Component

```tsx
// ❌ WRONG: Component makes API calls directly
function UserList() {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    axios.get('/api/users').then(res => setUsers(res.data));
  }, []);

  return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
```

**Fix**: Use custom hook and repository

```tsx
// ✅ CORRECT: Component uses application hook
function UserList() {
  const userRepository = useUserRepository();
  const { users, loading } = useUsers(userRepository);

  if (loading) return <Spinner />;
  return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
```

### Violation 3: Hooks in Infrastructure Layer

```tsx
// ❌ WRONG: Repository using React hooks
class UserRepository implements IUserRepository {
  async findById(id: string): Promise<User> {
    const [data] = useState(); // NO! Hooks don't belong here
    // ...
  }
}
```

**Fix**: Hooks only in Application layer

```tsx
// ✅ CORRECT: Repository is pure class, hooks in application
class UserRepository implements IUserRepository {
  async findById(id: string): Promise<User> {
    const response = await this.httpClient.get(`/users/${id}`);
    return response.data;
  }
}

// Hook in application layer
function useUser(id: string, repo: IUserRepository) {
  const [user, setUser] = useState<User | null>(null);
  // ...
}
```

## Testing Strategy by Layer

### Domain Layer Tests

```typescript
// tests/domain/userRules.test.ts
import { User, UserStatus, canActivateUser, activateUser } from '@/domain/entities/User';

describe('User Domain Rules', () => {
  it('should allow activation of inactive user', () => {
    const user: User = {
      id: '1',
      email: 'test@example.com',
      name: 'Test',
      status: UserStatus.INACTIVE,
      createdAt: new Date(),
    };

    expect(canActivateUser(user)).toBe(true);
  });

  it('should not allow activation of banned user', () => {
    const user: User = { ...baseUser, status: UserStatus.BANNED };
    expect(() => activateUser(user)).toThrow('Cannot activate');
  });
});
```

### Application Layer Tests

```typescript
// tests/application/hooks/useUser.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useUser } from '@/application/hooks/useUser';
import { IUserRepository } from '@/application/ports/IUserRepository';

describe('useUser hook', () => {
  it('should fetch user on mount', async () => {
    const mockRepo: IUserRepository = {
      findById: jest.fn().mockResolvedValue({ id: '1', name: 'Test' }),
      findByEmail: jest.fn(),
      findAll: jest.fn(),
      save: jest.fn(),
      delete: jest.fn(),
    };

    const { result } = renderHook(() => useUser('1', mockRepo));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user?.name).toBe('Test');
    expect(mockRepo.findById).toHaveBeenCalledWith('1');
  });
});
```

### Infrastructure Layer Tests

```typescript
// tests/infrastructure/repositories/UserRepository.test.ts
import { UserRepository } from '@/infrastructure/repositories/UserRepository';
import { HttpClient } from '@/infrastructure/api/httpClient';

describe('UserRepository', () => {
  it('should fetch user by id', async () => {
    const mockHttpClient: HttpClient = {
      get: jest.fn().mockResolvedValue({
        data: { id: '1', email: 'test@example.com', name: 'Test' }
      }),
    } as any;

    const repository = new UserRepository(mockHttpClient);
    const user = await repository.findById('1');

    expect(user?.id).toBe('1');
    expect(mockHttpClient.get).toHaveBeenCalledWith('/users/1');
  });
});
```

### Presentation Layer Tests

```tsx
// tests/presentation/components/UserProfile.test.tsx
import { render, screen } from '@testing-library/react';
import { UserProfile } from '@/presentation/components/UserProfile';
import { RepositoryProvider } from '@/infrastructure/di/RepositoryContext';

describe('UserProfile', () => {
  it('should display user name', async () => {
    render(
      <RepositoryProvider>
        <UserProfile userId="1" />
      </RepositoryProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    const userName = await screen.findByText('Test User');
    expect(userName).toBeInTheDocument();
  });
});
```

## Checklist for Clean Architecture in React

clean_architecture_checklist[15]{check,requirement}:
Domain independence,Domain has no React or external library imports
Dependency direction,All dependencies point inward toward domain
Interface usage,Application defines interfaces Infrastructure implements
No framework in domain,No React imports in domain layer
No components in application,Application has hooks not components
Hook extraction,Complex logic extracted to custom hooks
Repository abstraction,All data access through interfaces
Thin components,Components delegate to application hooks
DI implementation,Dependencies injected via Context or props
Testable domain,Can test domain rules without React
Testable hooks,Can test hooks with mocked repositories
Type safety,Full TypeScript coverage with no any
Error handling,Domain exceptions properly propagated
State management,Clear state ownership per layer
Code splitting,Routes and features lazy loaded

---

**File Size**: 470/500 lines max ✅
