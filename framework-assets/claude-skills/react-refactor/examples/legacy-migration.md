# Legacy React Migration Examples

**Comprehensive examples for migrating legacy React patterns to modern architecture with Clean Architecture principles, hooks, and TypeScript.**

## Overview

This document provides step-by-step migration examples for common legacy patterns:

migration_scenarios[8]{scenario,complexity,estimated_effort}:
Class Component to Functional,Medium,1-2 hours per component
HOC to Custom Hook,Medium,30-60 minutes per HOC
Render Props to Hooks,Medium,30-60 minutes per pattern
God Component Refactoring,High,4-8 hours per component
Redux Class Connect to Hooks,Medium,1-2 hours per container
Legacy Lifecycle to useEffect,Low,15-30 minutes per component
Prop Drilling to Context,Medium,2-4 hours for subtree
Mixed Concerns Separation,High,4-8 hours per feature

---

## Example 1: Class Component to Functional with Hooks

### Before: Legacy Class Component

```tsx
// ❌ LEGACY: Class component with lifecycle methods
import React, { Component } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: 'admin' | 'user' | 'guest';
}

interface UserProfileProps {
  userId: string;
  onUserLoad?: (user: User) => void;
}

interface UserProfileState {
  user: User | null;
  loading: boolean;
  error: string | null;
  isEditing: boolean;
  editedName: string;
}

class UserProfile extends Component<UserProfileProps, UserProfileState> {
  private mounted: boolean = false;

  constructor(props: UserProfileProps) {
    super(props);
    this.state = {
      user: null,
      loading: true,
      error: null,
      isEditing: false,
      editedName: '',
    };
  }

  componentDidMount() {
    this.mounted = true;
    this.fetchUser();
  }

  componentDidUpdate(prevProps: UserProfileProps) {
    if (prevProps.userId !== this.props.userId) {
      this.fetchUser();
    }
  }

  componentWillUnmount() {
    this.mounted = false;
  }

  fetchUser = async () => {
    this.setState({ loading: true, error: null });

    try {
      const response = await fetch(`/api/users/${this.props.userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      const user = await response.json();

      if (this.mounted) {
        this.setState({ user, loading: false, editedName: user.name });
        this.props.onUserLoad?.(user);
      }
    } catch (error) {
      if (this.mounted) {
        this.setState({
          error: error instanceof Error ? error.message : 'Unknown error',
          loading: false,
        });
      }
    }
  };

  handleEditToggle = () => {
    this.setState((state) => ({
      isEditing: !state.isEditing,
      editedName: state.user?.name || '',
    }));
  };

  handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ editedName: e.target.value });
  };

  handleSave = async () => {
    if (!this.state.user) return;

    try {
      const response = await fetch(`/api/users/${this.state.user.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.state.editedName }),
      });

      if (!response.ok) throw new Error('Failed to update');

      const updatedUser = await response.json();
      this.setState({
        user: updatedUser,
        isEditing: false,
      });
    } catch (error) {
      this.setState({
        error: error instanceof Error ? error.message : 'Update failed',
      });
    }
  };

  render() {
    const { user, loading, error, isEditing, editedName } = this.state;

    if (loading) {
      return <div className="spinner">Loading...</div>;
    }

    if (error) {
      return (
        <div className="error">
          <p>{error}</p>
          <button onClick={this.fetchUser}>Retry</button>
        </div>
      );
    }

    if (!user) {
      return <div>User not found</div>;
    }

    return (
      <div className="user-profile">
        <img src={user.avatar} alt={user.name} />
        {isEditing ? (
          <input
            value={editedName}
            onChange={this.handleNameChange}
            autoFocus
          />
        ) : (
          <h2>{user.name}</h2>
        )}
        <p>{user.email}</p>
        <span className="role-badge">{user.role}</span>
        <div className="actions">
          <button onClick={this.handleEditToggle}>
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
          {isEditing && <button onClick={this.handleSave}>Save</button>}
        </div>
      </div>
    );
  }
}

export default UserProfile;
```

### After: Modern Functional Component

```tsx
// ✅ MODERN: Functional component with Clean Architecture

// === Domain Layer ===
// src/domain/entities/User.ts
export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: 'admin' | 'user' | 'guest';
}

export interface UpdateUserDTO {
  name?: string;
  email?: string;
}

// === Application Layer ===
// src/application/ports/UserRepository.ts
export interface UserRepository {
  getById(id: string): Promise<User>;
  update(id: string, data: UpdateUserDTO): Promise<User>;
}

// src/application/hooks/useUser.ts
import { useState, useEffect, useCallback } from 'react';
import { User, UpdateUserDTO } from '@/domain/entities/User';
import { UserRepository } from '@/application/ports/UserRepository';

interface UseUserOptions {
  onLoad?: (user: User) => void;
}

interface UseUserResult {
  user: User | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  updateUser: (data: UpdateUserDTO) => Promise<void>;
}

export function useUser(
  userId: string,
  repository: UserRepository,
  options: UseUserOptions = {}
): UseUserResult {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchUser = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const fetchedUser = await repository.getById(userId);
      setUser(fetchedUser);
      options.onLoad?.(fetchedUser);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [userId, repository, options.onLoad]);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        const fetchedUser = await repository.getById(userId);
        if (!cancelled) {
          setUser(fetchedUser);
          options.onLoad?.(fetchedUser);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
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

  const updateUser = useCallback(
    async (data: UpdateUserDTO) => {
      if (!user) return;

      try {
        const updatedUser = await repository.update(user.id, data);
        setUser(updatedUser);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Update failed'));
        throw err;
      }
    },
    [user, repository]
  );

  return { user, loading, error, refetch: fetchUser, updateUser };
}

// src/application/hooks/useEditableField.ts
import { useState, useCallback } from 'react';

interface UseEditableFieldResult {
  isEditing: boolean;
  editedValue: string;
  startEditing: () => void;
  cancelEditing: () => void;
  setEditedValue: (value: string) => void;
  saveEdit: () => Promise<void>;
}

export function useEditableField(
  initialValue: string,
  onSave: (value: string) => Promise<void>
): UseEditableFieldResult {
  const [isEditing, setIsEditing] = useState(false);
  const [editedValue, setEditedValue] = useState(initialValue);

  const startEditing = useCallback(() => {
    setEditedValue(initialValue);
    setIsEditing(true);
  }, [initialValue]);

  const cancelEditing = useCallback(() => {
    setEditedValue(initialValue);
    setIsEditing(false);
  }, [initialValue]);

  const saveEdit = useCallback(async () => {
    await onSave(editedValue);
    setIsEditing(false);
  }, [editedValue, onSave]);

  return {
    isEditing,
    editedValue,
    startEditing,
    cancelEditing,
    setEditedValue,
    saveEdit,
  };
}

// === Infrastructure Layer ===
// src/infrastructure/api/UserApiRepository.ts
import { User, UpdateUserDTO } from '@/domain/entities/User';
import { UserRepository } from '@/application/ports/UserRepository';

export class UserApiRepository implements UserRepository {
  constructor(private baseUrl: string = '/api') {}

  async getById(id: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/${id}`);
    if (!response.ok) {
      throw new Error('Failed to fetch user');
    }
    return response.json();
  }

  async update(id: string, data: UpdateUserDTO): Promise<User> {
    const response = await fetch(`${this.baseUrl}/users/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error('Failed to update user');
    }
    return response.json();
  }
}

// === Presentation Layer ===
// src/presentation/components/UserProfile/UserProfile.tsx
import { memo, useCallback, useMemo } from 'react';
import { User } from '@/domain/entities/User';
import { UserRepository } from '@/application/ports/UserRepository';
import { useUser } from '@/application/hooks/useUser';
import { useEditableField } from '@/application/hooks/useEditableField';
import { Spinner } from '@/presentation/components/common/Spinner';
import { ErrorMessage } from '@/presentation/components/common/ErrorMessage';
import { Avatar } from './Avatar';
import { RoleBadge } from './RoleBadge';
import { EditableText } from './EditableText';
import styles from './UserProfile.module.css';

interface UserProfileProps {
  userId: string;
  repository: UserRepository;
  onUserLoad?: (user: User) => void;
}

export const UserProfile = memo<UserProfileProps>(function UserProfile({
  userId,
  repository,
  onUserLoad,
}) {
  const options = useMemo(() => ({ onLoad: onUserLoad }), [onUserLoad]);
  const { user, loading, error, refetch, updateUser } = useUser(
    userId,
    repository,
    options
  );

  const handleSaveName = useCallback(
    async (name: string) => {
      await updateUser({ name });
    },
    [updateUser]
  );

  const nameEditor = useEditableField(user?.name || '', handleSaveName);

  if (loading) {
    return <Spinner />;
  }

  if (error) {
    return <ErrorMessage message={error.message} onRetry={refetch} />;
  }

  if (!user) {
    return <div>User not found</div>;
  }

  return (
    <div className={styles.profile}>
      <Avatar src={user.avatar} alt={user.name} />
      <EditableText
        value={user.name}
        isEditing={nameEditor.isEditing}
        editedValue={nameEditor.editedValue}
        onEdit={nameEditor.startEditing}
        onCancel={nameEditor.cancelEditing}
        onSave={nameEditor.saveEdit}
        onChange={nameEditor.setEditedValue}
      />
      <p className={styles.email}>{user.email}</p>
      <RoleBadge role={user.role} />
    </div>
  );
});
```

### Migration Key Points

migration_checklist[8]{item,action}:
Lifecycle Methods,Replace with useEffect hooks
Instance Variables,Use useRef or useState
this.state,Use useState hook
this.setState,Use setState from useState
this.props,Destructure from function params
Instance Methods,Use useCallback for handlers
componentDidMount,useEffect with empty deps
componentWillUnmount,useEffect cleanup function

---

## Example 2: HOC to Custom Hook Migration

### Before: Higher-Order Component Pattern

```tsx
// ❌ LEGACY: HOC for authentication
import React, { ComponentType, useEffect, useState } from 'react';

interface WithAuthProps {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

interface User {
  id: string;
  name: string;
  role: string;
}

interface Credentials {
  email: string;
  password: string;
}

function withAuth<P extends WithAuthProps>(
  WrappedComponent: ComponentType<P>
): ComponentType<Omit<P, keyof WithAuthProps>> {
  return function WithAuthComponent(props: Omit<P, keyof WithAuthProps>) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const checkAuth = async () => {
        try {
          const response = await fetch('/api/auth/me');
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          }
        } catch (error) {
          console.error('Auth check failed:', error);
        } finally {
          setLoading(false);
        }
      };

      checkAuth();
    }, []);

    const login = async (credentials: Credentials) => {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const userData = await response.json();
      setUser(userData);
    };

    const logout = async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      setUser(null);
    };

    if (loading) {
      return <div>Loading...</div>;
    }

    return (
      <WrappedComponent
        {...(props as P)}
        user={user}
        isAuthenticated={!!user}
        login={login}
        logout={logout}
      />
    );
  };
}

// Usage
const Dashboard = withAuth(function Dashboard({ user, logout }) {
  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
});
```

### After: Custom Hook Pattern

```tsx
// ✅ MODERN: Custom hook with Context

// === Domain Layer ===
// src/domain/entities/Auth.ts
export interface User {
  id: string;
  name: string;
  role: string;
}

export interface Credentials {
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// === Application Layer ===
// src/application/ports/AuthService.ts
export interface AuthService {
  getCurrentUser(): Promise<User | null>;
  login(credentials: Credentials): Promise<User>;
  logout(): Promise<void>;
}

// src/application/hooks/useAuth.ts
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
  useMemo,
} from 'react';
import { User, Credentials, AuthState } from '@/domain/entities/Auth';
import { AuthService } from '@/application/ports/AuthService';

interface AuthContextValue extends AuthState {
  login: (credentials: Credentials) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
  authService: AuthService;
}

export function AuthProvider({ children, authService }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const checkAuth = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        if (!cancelled) {
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    checkAuth();

    return () => {
      cancelled = true;
    };
  }, [authService]);

  const login = useCallback(
    async (credentials: Credentials) => {
      const loggedInUser = await authService.login(credentials);
      setUser(loggedInUser);
    },
    [authService]
  );

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, [authService]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Convenience hooks for specific needs
export function useCurrentUser(): User | null {
  const { user } = useAuth();
  return user;
}

export function useIsAuthenticated(): boolean {
  const { isAuthenticated } = useAuth();
  return isAuthenticated;
}

// === Infrastructure Layer ===
// src/infrastructure/api/AuthApiService.ts
import { AuthService } from '@/application/ports/AuthService';
import { User, Credentials } from '@/domain/entities/Auth';

export class AuthApiService implements AuthService {
  constructor(private baseUrl: string = '/api/auth') {}

  async getCurrentUser(): Promise<User | null> {
    const response = await fetch(`${this.baseUrl}/me`);
    if (!response.ok) {
      return null;
    }
    return response.json();
  }

  async login(credentials: Credentials): Promise<User> {
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  }

  async logout(): Promise<void> {
    await fetch(`${this.baseUrl}/logout`, { method: 'POST' });
  }
}

// === Presentation Layer ===
// src/presentation/components/Dashboard/Dashboard.tsx
import { useAuth } from '@/application/hooks/useAuth';
import { Spinner } from '@/presentation/components/common/Spinner';

export function Dashboard() {
  const { user, isLoading, logout } = useAuth();

  if (isLoading) {
    return <Spinner />;
  }

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

// App setup
// src/App.tsx
import { AuthProvider } from '@/application/hooks/useAuth';
import { AuthApiService } from '@/infrastructure/api/AuthApiService';
import { Dashboard } from '@/presentation/components/Dashboard';

const authService = new AuthApiService();

function App() {
  return (
    <AuthProvider authService={authService}>
      <Dashboard />
    </AuthProvider>
  );
}
```

---

## Example 3: God Component Refactoring

### Before: 800-line God Component

```tsx
// ❌ LEGACY: God component handling everything
function OrderManagement() {
  // 50+ lines of state
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [filters, setFilters] = useState({});
  const [sorting, setSorting] = useState({});
  const [pagination, setPagination] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newOrderData, setNewOrderData] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  // ... 40 more state variables

  // 200+ lines of handlers and business logic
  useEffect(() => {
    // Complex data fetching with filters, sorting, pagination
  }, [filters, sorting, pagination]);

  const handleFilterChange = () => {
    /* ... */
  };
  const handleSortChange = () => {
    /* ... */
  };
  const handlePageChange = () => {
    /* ... */
  };
  const handleOrderSelect = () => {
    /* ... */
  };
  const handleOrderCreate = () => {
    /* ... */
  };
  const handleOrderUpdate = () => {
    /* ... */
  };
  const handleOrderDelete = () => {
    /* ... */
  };
  const validateOrder = () => {
    /* ... */
  };
  const calculateTotals = () => {
    /* ... */
  };
  // ... 30 more handlers

  // 500+ lines of JSX
  return (
    <div className="order-management">
      {/* Header with stats */}
      <header>{/* 50 lines */}</header>

      {/* Filters section */}
      <div className="filters">{/* 100 lines */}</div>

      {/* Orders table */}
      <table>{/* 200 lines */}</table>

      {/* Order details panel */}
      {selectedOrder && <div className="details">{/* 150 lines */}</div>}

      {/* Create order modal */}
      {isCreating && <div className="modal">{/* 100 lines */}</div>}
    </div>
  );
}
```

### After: Decomposed Architecture

```tsx
// ✅ MODERN: Clean Architecture decomposition

// === Domain Layer ===
// src/domain/entities/Order.ts
export interface Order {
  id: string;
  customerId: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  createdAt: Date;
}

export interface OrderItem {
  productId: string;
  quantity: number;
  price: number;
}

export type OrderStatus = 'pending' | 'confirmed' | 'shipped' | 'delivered';

// src/domain/rules/OrderRules.ts
export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function canCancelOrder(order: Order): boolean {
  return order.status === 'pending' || order.status === 'confirmed';
}

// === Application Layer ===
// src/application/hooks/useOrders.ts
import { useState, useEffect, useCallback } from 'react';
import { Order } from '@/domain/entities/Order';
import { OrderRepository, OrderFilters } from '@/application/ports/OrderRepository';

interface UseOrdersResult {
  orders: Order[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useOrders(
  repository: OrderRepository,
  filters: OrderFilters
): UseOrdersResult {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const data = await repository.getAll(filters);
      setOrders(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch'));
    } finally {
      setLoading(false);
    }
  }, [repository, filters]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return { orders, loading, error, refetch: fetchOrders };
}

// src/application/hooks/useOrderFilters.ts
import { useState, useCallback, useMemo } from 'react';
import { OrderFilters as Filters } from '@/application/ports/OrderRepository';

export function useOrderFilters() {
  const [status, setStatus] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<[Date, Date] | null>(null);
  const [search, setSearch] = useState('');

  const filters = useMemo<Filters>(
    () => ({
      status: status || undefined,
      dateFrom: dateRange?.[0],
      dateTo: dateRange?.[1],
      search: search || undefined,
    }),
    [status, dateRange, search]
  );

  const clearFilters = useCallback(() => {
    setStatus(null);
    setDateRange(null);
    setSearch('');
  }, []);

  return {
    filters,
    status,
    setStatus,
    dateRange,
    setDateRange,
    search,
    setSearch,
    clearFilters,
  };
}

// src/application/hooks/usePagination.ts
import { useState, useCallback, useMemo } from 'react';

interface PaginationState {
  page: number;
  pageSize: number;
  totalItems: number;
}

export function usePagination(initialPageSize = 20) {
  const [pagination, setPagination] = useState<PaginationState>({
    page: 1,
    pageSize: initialPageSize,
    totalItems: 0,
  });

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }));
  }, []);

  const setTotalItems = useCallback((totalItems: number) => {
    setPagination((prev) => ({ ...prev, totalItems }));
  }, []);

  const totalPages = useMemo(
    () => Math.ceil(pagination.totalItems / pagination.pageSize),
    [pagination.totalItems, pagination.pageSize]
  );

  return {
    ...pagination,
    totalPages,
    setPage,
    setTotalItems,
  };
}

// src/application/hooks/useOrderSelection.ts
import { useState, useCallback } from 'react';
import { Order } from '@/domain/entities/Order';

export function useOrderSelection() {
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  const selectOrder = useCallback((order: Order) => {
    setSelectedOrder(order);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedOrder(null);
  }, []);

  return {
    selectedOrder,
    selectOrder,
    clearSelection,
    hasSelection: !!selectedOrder,
  };
}

// === Presentation Layer ===
// src/presentation/components/OrderManagement/OrderManagement.tsx
import { memo } from 'react';
import { OrderRepository } from '@/application/ports/OrderRepository';
import { useOrders } from '@/application/hooks/useOrders';
import { useOrderFilters } from '@/application/hooks/useOrderFilters';
import { usePagination } from '@/application/hooks/usePagination';
import { useOrderSelection } from '@/application/hooks/useOrderSelection';
import { OrderHeader } from './OrderHeader';
import { OrderFilters } from './OrderFilters';
import { OrderTable } from './OrderTable';
import { OrderDetails } from './OrderDetails';
import { Spinner } from '@/presentation/components/common/Spinner';
import { ErrorMessage } from '@/presentation/components/common/ErrorMessage';
import styles from './OrderManagement.module.css';

interface OrderManagementProps {
  repository: OrderRepository;
}

export const OrderManagement = memo<OrderManagementProps>(
  function OrderManagement({ repository }) {
    const { filters, ...filterControls } = useOrderFilters();
    const pagination = usePagination();
    const selection = useOrderSelection();
    const { orders, loading, error, refetch } = useOrders(repository, filters);

    if (loading) return <Spinner />;
    if (error) return <ErrorMessage message={error.message} onRetry={refetch} />;

    return (
      <div className={styles.container}>
        <OrderHeader orderCount={orders.length} />

        <OrderFilters {...filterControls} />

        <OrderTable
          orders={orders}
          selectedId={selection.selectedOrder?.id}
          onSelect={selection.selectOrder}
        />

        {selection.hasSelection && (
          <OrderDetails
            order={selection.selectedOrder!}
            onClose={selection.clearSelection}
          />
        )}
      </div>
    );
  }
);

// Smaller focused components
// src/presentation/components/OrderManagement/OrderHeader.tsx
interface OrderHeaderProps {
  orderCount: number;
}

export function OrderHeader({ orderCount }: OrderHeaderProps) {
  return (
    <header>
      <h1>Order Management</h1>
      <span>{orderCount} orders</span>
    </header>
  );
}

// src/presentation/components/OrderManagement/OrderFilters.tsx
interface OrderFiltersProps {
  status: string | null;
  setStatus: (status: string | null) => void;
  search: string;
  setSearch: (search: string) => void;
  clearFilters: () => void;
}

export function OrderFilters({
  status,
  setStatus,
  search,
  setSearch,
  clearFilters,
}: OrderFiltersProps) {
  return (
    <div className="filters">
      <select
        value={status || ''}
        onChange={(e) => setStatus(e.target.value || null)}
      >
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="confirmed">Confirmed</option>
        <option value="shipped">Shipped</option>
      </select>

      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search orders..."
      />

      <button onClick={clearFilters}>Clear</button>
    </div>
  );
}
```

---

## Example 4: Redux Class Connect to Hooks

### Before: mapStateToProps / mapDispatchToProps

```tsx
// ❌ LEGACY: Redux connect pattern
import { connect } from 'react-redux';
import { Dispatch } from 'redux';
import { fetchProducts, addToCart } from './actions';

interface Product {
  id: string;
  name: string;
  price: number;
}

interface StateProps {
  products: Product[];
  loading: boolean;
  cartCount: number;
}

interface DispatchProps {
  fetchProducts: () => void;
  addToCart: (productId: string) => void;
}

interface OwnProps {
  categoryId: string;
}

type Props = StateProps & DispatchProps & OwnProps;

class ProductList extends React.Component<Props> {
  componentDidMount() {
    this.props.fetchProducts();
  }

  render() {
    const { products, loading, cartCount, addToCart } = this.props;

    if (loading) return <div>Loading...</div>;

    return (
      <div>
        <p>Cart: {cartCount} items</p>
        {products.map((product) => (
          <div key={product.id}>
            <span>{product.name}</span>
            <button onClick={() => addToCart(product.id)}>Add to Cart</button>
          </div>
        ))}
      </div>
    );
  }
}

const mapStateToProps = (state: RootState, ownProps: OwnProps): StateProps => ({
  products: state.products.items.filter(
    (p) => p.categoryId === ownProps.categoryId
  ),
  loading: state.products.loading,
  cartCount: state.cart.items.length,
});

const mapDispatchToProps = (dispatch: Dispatch): DispatchProps => ({
  fetchProducts: () => dispatch(fetchProducts()),
  addToCart: (id) => dispatch(addToCart(id)),
});

export default connect(mapStateToProps, mapDispatchToProps)(ProductList);
```

### After: Redux Toolkit with Hooks

```tsx
// ✅ MODERN: Redux Toolkit with hooks

// === Store Setup ===
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import productsReducer from './slices/productsSlice';
import cartReducer from './slices/cartSlice';

export const store = configureStore({
  reducer: {
    products: productsReducer,
    cart: cartReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// === Slice Definition ===
// src/store/slices/productsSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface Product {
  id: string;
  name: string;
  price: number;
  categoryId: string;
}

interface ProductsState {
  items: Product[];
  loading: boolean;
  error: string | null;
}

const initialState: ProductsState = {
  items: [],
  loading: false,
  error: null,
};

export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async () => {
    const response = await fetch('/api/products');
    return response.json();
  }
);

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.items = action.payload;
        state.loading = false;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch';
      });
  },
});

export default productsSlice.reducer;

// === Custom Hook for Products ===
// src/application/hooks/useProducts.ts
import { useEffect, useMemo } from 'react';
import { useAppDispatch, useAppSelector } from '@/store';
import { fetchProducts } from '@/store/slices/productsSlice';

export function useProducts(categoryId?: string) {
  const dispatch = useAppDispatch();
  const { items, loading, error } = useAppSelector((state) => state.products);

  useEffect(() => {
    dispatch(fetchProducts());
  }, [dispatch]);

  const filteredProducts = useMemo(
    () =>
      categoryId ? items.filter((p) => p.categoryId === categoryId) : items,
    [items, categoryId]
  );

  return {
    products: filteredProducts,
    loading,
    error,
  };
}

// === Custom Hook for Cart ===
// src/application/hooks/useCart.ts
import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '@/store';
import { addItem, removeItem, clearCart } from '@/store/slices/cartSlice';

export function useCart() {
  const dispatch = useAppDispatch();
  const { items, total } = useAppSelector((state) => state.cart);

  const addToCart = useCallback(
    (productId: string) => {
      dispatch(addItem(productId));
    },
    [dispatch]
  );

  const removeFromCart = useCallback(
    (productId: string) => {
      dispatch(removeItem(productId));
    },
    [dispatch]
  );

  const clear = useCallback(() => {
    dispatch(clearCart());
  }, [dispatch]);

  return {
    items,
    total,
    count: items.length,
    addToCart,
    removeFromCart,
    clearCart: clear,
  };
}

// === Presentation Layer ===
// src/presentation/components/ProductList/ProductList.tsx
import { memo } from 'react';
import { useProducts } from '@/application/hooks/useProducts';
import { useCart } from '@/application/hooks/useCart';
import { ProductCard } from './ProductCard';
import { CartSummary } from './CartSummary';
import { Spinner } from '@/presentation/components/common/Spinner';
import styles from './ProductList.module.css';

interface ProductListProps {
  categoryId: string;
}

export const ProductList = memo<ProductListProps>(function ProductList({
  categoryId,
}) {
  const { products, loading, error } = useProducts(categoryId);
  const { count, addToCart } = useCart();

  if (loading) return <Spinner />;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className={styles.container}>
      <CartSummary count={count} />

      <div className={styles.grid}>
        {products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={() => addToCart(product.id)}
          />
        ))}
      </div>
    </div>
  );
});
```

---

## Migration Strategy Patterns

### Pattern 1: Strangler Fig Migration

strangler_fig_steps[6]{step,action,risk}:
1. Create Parallel Structure,Set up new architecture alongside legacy,Low
2. Wrap Legacy Components,Create adapters for legacy code,Low
3. Migrate Incrementally,Move one feature at a time,Medium
4. Feature Flags,Toggle between old and new,Low
5. Monitor and Compare,Validate new implementation,Low
6. Remove Legacy Code,Delete old code when stable,Medium

```tsx
// Feature flag wrapper for incremental migration
function FeatureWrapper({ featureId, children, legacyComponent }) {
  const { isEnabled } = useFeatureFlags();

  if (isEnabled(featureId)) {
    return children;
  }

  return legacyComponent;
}

// Usage
<FeatureWrapper
  featureId="new-user-profile"
  legacyComponent={<LegacyUserProfile userId={id} />}
>
  <ModernUserProfile userId={id} repository={userRepo} />
</FeatureWrapper>
```

### Pattern 2: Bottom-Up Migration

bottom_up_steps[5]{step,focus,dependencies}:
1. Extract Types,Define TypeScript interfaces,None
2. Extract Utils,Move pure functions to domain,Types only
3. Extract Hooks,Create custom hooks from logic,Types and utils
4. Create Components,Build presentational components,Hooks
5. Compose Features,Assemble from new parts,All above

---

## Quality Checklist for Migration

migration_quality[10]{check,validation}:
No Regressions,All existing tests pass
Type Safety,No implicit any types
Performance,No new unnecessary renders
Accessibility,ARIA and keyboard support maintained
Test Coverage,New code has unit tests
Error Handling,Errors handled gracefully
Loading States,Loading indicators present
Bundle Size,No significant increase
Code Splitting,Large components lazy loaded
Documentation,Key decisions documented

---

**File Size**: ~490 lines
**Next**: See `nextjs-clean-arch.md` for Next.js specific patterns
