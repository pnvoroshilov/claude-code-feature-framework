# Frontend React Architecture Examples

**Complete examples of architecture patterns in React/TypeScript applications.**

## Project Structure

Recommended directory structure for React applications:

```
src/
├── domain/              # Domain models (if complex business logic)
│   └── models/
│       └── User.ts
├── features/            # Feature-based organization
│   └── users/
│       ├── components/  # Feature-specific components
│       │   ├── UserList.tsx
│       │   ├── UserCard.tsx
│       │   └── UserForm.tsx
│       ├── hooks/       # Feature-specific hooks
│       │   ├── useUsers.ts
│       │   ├── useUserForm.ts
│       │   └── useUserFiltering.ts
│       ├── api/         # Feature-specific API calls
│       │   └── userApi.ts
│       └── types/       # Feature-specific types
│           └── index.ts
├── shared/              # Shared/common code
│   ├── components/      # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Card.tsx
│   ├── hooks/           # Reusable hooks
│   │   └── useDebounce.ts
│   ├── api/             # API client
│   │   └── apiClient.ts
│   └── utils/           # Utilities
│       └── validation.ts
├── context/             # Global state (Context API)
│   ├── AuthContext.tsx
│   └── ThemeContext.tsx
└── App.tsx
```

---

## Component Patterns

### Container/Presentational Pattern

**Container Component** (Smart): Handles data and logic
**Presentational Component** (Dumb): Handles UI rendering

```typescript
// users/components/UserCard.tsx - Presentational (Dumb)
interface UserCardProps {
  user: User;
  onClick: () => void;
}

export const UserCard: React.FC<UserCardProps> = ({ user, onClick }) => (
  <div className="user-card" onClick={onClick}>
    <Avatar src={user.avatar} alt={user.name} />
    <h3>{user.name}</h3>
    <p>{user.email}</p>
    <StatusBadge status={user.status} />
  </div>
);


// users/components/UserList.tsx - Presentational (Dumb)
interface UserListProps {
  users: User[];
  onUserClick: (userId: number) => void;
  loading?: boolean;
  error?: string | null;
}

export const UserList: React.FC<UserListProps> = ({
  users,
  onUserClick,
  loading = false,
  error = null
}) => {
  if (loading) return <Spinner />;
  if (error) return <ErrorMessage message={error} />;
  if (users.length === 0) return <EmptyState message="No users found" />;

  return (
    <ul className="user-list">
      {users.map(user => (
        <UserCard
          key={user.id}
          user={user}
          onClick={() => onUserClick(user.id)}
        />
      ))}
    </ul>
  );
};


// users/components/UserListContainer.tsx - Container (Smart)
export const UserListContainer: React.FC = () => {
  const navigate = useNavigate();
  const { users, loading, error } = useUsers();
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'email'>('name');

  const filteredUsers = useUserFiltering(users, filter);
  const sortedUsers = useUserSorting(filteredUsers, sortBy);

  const handleUserClick = (userId: number) => {
    navigate(`/users/${userId}`);
  };

  return (
    <div className="user-management">
      <UserFilter filter={filter} onFilterChange={setFilter} />
      <UserSort sortBy={sortBy} onSortChange={setSortBy} />
      <UserList
        users={sortedUsers}
        onUserClick={handleUserClick}
        loading={loading}
        error={error}
      />
    </div>
  );
};
```

---

## Custom Hooks Pattern

Extract reusable logic into custom hooks following Single Responsibility Principle.

### Data Fetching Hook

```typescript
// users/hooks/useUsers.ts
interface UseUsersResult {
  users: User[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useUsers(): UseUsersResult {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await userApi.getUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, loading, error, refetch: fetchUsers };
}


// users/hooks/useUser.ts
export function useUser(userId: number) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      try {
        setLoading(true);
        setError(null);
        const data = await userApi.getUser(userId);
        if (!cancelled) {
          setUser(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch user');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { user, loading, error };
}
```

### Business Logic Hooks

```typescript
// users/hooks/useUserFiltering.ts
export function useUserFiltering(users: User[], filter: string): User[] {
  return useMemo(() => {
    if (!filter) return users;

    const lowerFilter = filter.toLowerCase();
    return users.filter(user =>
      user.name.toLowerCase().includes(lowerFilter) ||
      user.email.toLowerCase().includes(lowerFilter)
    );
  }, [users, filter]);
}


// users/hooks/useUserSorting.ts
export function useUserSorting(
  users: User[],
  sortBy: 'name' | 'email' | 'createdAt'
): User[] {
  return useMemo(() => {
    return [...users].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    });
  }, [users, sortBy]);
}


// users/hooks/useUserForm.ts
interface UserFormData {
  name: string;
  email: string;
}

interface UseUserFormResult {
  formData: UserFormData;
  errors: Partial<Record<keyof UserFormData, string>>;
  isValid: boolean;
  isSubmitting: boolean;
  handleChange: (field: keyof UserFormData, value: string) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
}

export function useUserForm(
  initialData: UserFormData,
  onSubmit: (data: UserFormData) => Promise<void>
): UseUserFormResult {
  const [formData, setFormData] = useState<UserFormData>(initialData);
  const [errors, setErrors] = useState<Partial<Record<keyof UserFormData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateField = (field: keyof UserFormData, value: string): string | null => {
    if (field === 'email') {
      if (!value) return 'Email is required';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Invalid email format';
    }
    if (field === 'name') {
      if (!value) return 'Name is required';
      if (value.length < 2) return 'Name must be at least 2 characters';
    }
    return null;
  };

  const handleChange = (field: keyof UserFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Validate on change
    const error = validateField(field, value);
    setErrors(prev => ({
      ...prev,
      [field]: error || undefined
    }));
  };

  const validateAll = (): boolean => {
    const newErrors: Partial<Record<keyof UserFormData, string>> = {};
    let valid = true;

    (Object.keys(formData) as Array<keyof UserFormData>).forEach(field => {
      const error = validateField(field, formData[field]);
      if (error) {
        newErrors[field] = error;
        valid = false;
      }
    });

    setErrors(newErrors);
    return valid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateAll()) return;

    try {
      setIsSubmitting(true);
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = Object.keys(errors).length === 0;

  return {
    formData,
    errors,
    isValid,
    isSubmitting,
    handleChange,
    handleSubmit
  };
}
```

---

## Dependency Injection Pattern

Pass dependencies (API clients) as props for testability.

```typescript
// users/api/userApi.ts
export interface IUserAPI {
  getUsers(): Promise<User[]>;
  getUser(id: number): Promise<User>;
  createUser(data: CreateUserDTO): Promise<User>;
  updateUser(id: number, data: UpdateUserDTO): Promise<User>;
  deleteUser(id: number): Promise<void>;
}

export class UserAPI implements IUserAPI {
  constructor(private apiClient: APIClient) {}

  async getUsers(): Promise<User[]> {
    return this.apiClient.get<User[]>('/users');
  }

  async getUser(id: number): Promise<User> {
    return this.apiClient.get<User>(`/users/${id}`);
  }

  async createUser(data: CreateUserDTO): Promise<User> {
    return this.apiClient.post<User>('/users', data);
  }

  async updateUser(id: number, data: UpdateUserDTO): Promise<User> {
    return this.apiClient.put<User>(`/users/${id}`, data);
  }

  async deleteUser(id: number): Promise<void> {
    return this.apiClient.delete(`/users/${id}`);
  }
}

// Mock for testing
export class MockUserAPI implements IUserAPI {
  private users: User[] = [
    { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'active' }
  ];

  async getUsers(): Promise<User[]> {
    return Promise.resolve([...this.users]);
  }

  async getUser(id: number): Promise<User> {
    const user = this.users.find(u => u.id === id);
    if (!user) throw new Error('User not found');
    return Promise.resolve(user);
  }

  async createUser(data: CreateUserDTO): Promise<User> {
    const newUser: User = {
      id: this.users.length + 1,
      ...data,
      status: 'active'
    };
    this.users.push(newUser);
    return Promise.resolve(newUser);
  }

  async updateUser(id: number, data: UpdateUserDTO): Promise<User> {
    const index = this.users.findIndex(u => u.id === id);
    if (index === -1) throw new Error('User not found');

    this.users[index] = { ...this.users[index], ...data };
    return Promise.resolve(this.users[index]);
  }

  async deleteUser(id: number): Promise<void> {
    const index = this.users.findIndex(u => u.id === id);
    if (index === -1) throw new Error('User not found');
    this.users.splice(index, 1);
  }
}


// Inject API dependency
interface UserListProps {
  userApi: IUserAPI;  // Dependency injection
}

export const UserList: React.FC<UserListProps> = ({ userApi }) => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    userApi.getUsers().then(setUsers);
  }, [userApi]);

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
};

// Production usage
<UserList userApi={new UserAPI(apiClient)} />

// Testing usage
<UserList userApi={new MockUserAPI()} />
```

---

## Context API (Observer Pattern)

Use Context API for cross-cutting concerns like theme and authentication.

```typescript
// context/ThemeContext.tsx
type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Load from localStorage
    return (localStorage.getItem('theme') as Theme) || 'light';
  });

  const toggleTheme = useCallback(() => {
    setTheme(prev => {
      const newTheme = prev === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      return newTheme;
    });
  }, []);

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}


// context/AuthContext.tsx
interface User {
  id: number;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    async function checkAuth() {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = await authApi.verifyToken(token);
          setUser(userData);
        }
      } catch (error) {
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    localStorage.setItem('token', response.token);
    setUser(response.user);
  };

  const logout = async () => {
    await authApi.logout();
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated: user !== null
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}


// Usage in components
const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header className={`header header--${theme}`}>
      <button onClick={toggleTheme}>
        {theme === 'light' ? '🌙' : '☀️'}
      </button>

      {isAuthenticated ? (
        <>
          <span>Welcome, {user!.name}</span>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </header>
  );
};
```

---

## Component Composition

Build complex UIs from simple, reusable components.

```typescript
// shared/components/Card.tsx
interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick }) => (
  <div className={`card ${className}`} onClick={onClick}>
    {children}
  </div>
);


// shared/components/CardHeader.tsx
export const CardHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="card-header">{children}</div>
);


// shared/components/CardBody.tsx
export const CardBody: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="card-body">{children}</div>
);


// shared/components/CardFooter.tsx
export const CardFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="card-footer">{children}</div>
);


// Usage - compose components
const UserDetailCard: React.FC<{ user: User }> = ({ user }) => (
  <Card>
    <CardHeader>
      <h2>{user.name}</h2>
      <StatusBadge status={user.status} />
    </CardHeader>

    <CardBody>
      <p>Email: {user.email}</p>
      <p>Joined: {formatDate(user.createdAt)}</p>
    </CardBody>

    <CardFooter>
      <Button variant="primary" onClick={() => handleEdit(user.id)}>
        Edit
      </Button>
      <Button variant="danger" onClick={() => handleDelete(user.id)}>
        Delete
      </Button>
    </CardFooter>
  </Card>
);
```

---

## Testing Strategy

### Component Testing with React Testing Library

```typescript
// users/components/UserCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser: User = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    status: 'active',
    avatar: 'https://example.com/avatar.jpg'
  };

  it('renders user information', () => {
    render(<UserCard user={mockUser} onClick={() => {}} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<UserCard user={mockUser} onClick={handleClick} />);

    fireEvent.click(screen.getByRole('article'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});


// users/hooks/useUsers.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useUsers } from './useUsers';
import { MockUserAPI } from '../api/userApi';

describe('useUsers', () => {
  it('fetches users on mount', async () => {
    const mockApi = new MockUserAPI();
    const { result } = renderHook(() => useUsers(mockApi));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.users).toHaveLength(2);
    expect(result.current.error).toBeNull();
  });
});
```

---

## Best Practices Summary

react_best_practices[10]{practice,description,benefit}:
Component Composition,Build complex UIs from simple components,Reusability maintainability
Container/Presentational,Separate data logic from UI,Easier testing clear responsibilities
Custom Hooks,Extract reusable stateful logic,DRY principle code reuse
Dependency Injection,Pass dependencies as props,Testability flexibility
Context for Global State,Use Context for cross-cutting concerns,Avoid prop drilling
TypeScript,Use strong typing throughout,Type safety fewer bugs
Single Responsibility,One component one purpose,Easier to understand and test
Immutability,Don't mutate state directly,Predictable behavior easier debugging
Error Boundaries,Catch errors in component tree,Graceful error handling
Code Splitting,Lazy load components,Faster initial load

---

**File Size**: 450/500 lines max ✅
