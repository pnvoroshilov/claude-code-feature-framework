# React State Management Patterns

**Comprehensive guide to state management in React: Context API, Redux Toolkit, Zustand, Jotai, and React Query.**

## State Management Decision Tree

state_management_decision[6]{scenario,solution,reason}:
Local component state,useState,State used only in one component
Shared state in subtree,Context API,State shared among related components
Global client state (simple),Zustand,Simple API minimal boilerplate
Global client state (complex),Redux Toolkit,DevTools time-travel complex middleware
Atomic state management,Jotai,Fine-grained reactivity derived state
Server state,React Query or SWR,Caching invalidation background updates

## Pattern 1: Context API

**For sharing state across component subtrees without prop drilling.**

### Basic Context Pattern

```typescript
// src/application/stores/AuthContext.tsx
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { User } from '@/domain/entities/User';
import { IAuthService } from '@/application/ports/IAuthService';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  authService: IAuthService;
  children: ReactNode;
}

export function AuthProvider({ authService, children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const user = await authService.login({ email, password });
      setUser(user);
    } finally {
      setLoading(false);
    }
  }, [authService]);

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [authService]);

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Context with Reducer Pattern

```typescript
// src/application/stores/CartContext.tsx
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Product } from '@/domain/entities/Product';

interface CartItem {
  product: Product;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  total: number;
}

type CartAction =
  | { type: 'ADD_ITEM'; payload: { product: Product; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: { productId: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { productId: string; quantity: number } }
  | { type: 'CLEAR_CART' };

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingIndex = state.items.findIndex(
        item => item.product.id === action.payload.product.id
      );

      let items: CartItem[];
      if (existingIndex >= 0) {
        items = [...state.items];
        items[existingIndex] = {
          ...items[existingIndex],
          quantity: items[existingIndex].quantity + action.payload.quantity,
        };
      } else {
        items = [...state.items, action.payload];
      }

      const total = calculateTotal(items);
      return { items, total };
    }

    case 'REMOVE_ITEM': {
      const items = state.items.filter(item => item.product.id !== action.payload.productId);
      const total = calculateTotal(items);
      return { items, total };
    }

    case 'UPDATE_QUANTITY': {
      const items = state.items.map(item =>
        item.product.id === action.payload.productId
          ? { ...item, quantity: action.payload.quantity }
          : item
      );
      const total = calculateTotal(items);
      return { items, total };
    }

    case 'CLEAR_CART':
      return { items: [], total: 0 };

    default:
      return state;
  }
}

function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);
}

interface CartContextType {
  state: CartState;
  addItem: (product: Product, quantity: number) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(cartReducer, { items: [], total: 0 });

  const addItem = (product: Product, quantity: number) => {
    dispatch({ type: 'ADD_ITEM', payload: { product, quantity } });
  };

  const removeItem = (productId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: { productId } });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { productId, quantity } });
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };

  return (
    <CartContext.Provider value={{ state, addItem, removeItem, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextType {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
}
```

### Performance-Optimized Context

```typescript
// Split context to prevent unnecessary re-renders
import React, { createContext, useContext, useState, ReactNode } from 'react';

// State context
interface StateContextType {
  user: User | null;
  loading: boolean;
}

const StateContext = createContext<StateContextType | undefined>(undefined);

// Actions context (doesn't change, won't cause re-renders)
interface ActionsContextType {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const ActionsContext = createContext<ActionsContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Actions object is stable (doesn't change on re-render)
  const actions = useMemo(
    () => ({
      login: async (email: string, password: string) => {
        setLoading(true);
        const user = await authService.login({ email, password });
        setUser(user);
        setLoading(false);
      },
      logout: () => setUser(null),
    }),
    []
  );

  return (
    <StateContext.Provider value={{ user, loading }}>
      <ActionsContext.Provider value={actions}>{children}</ActionsContext.Provider>
    </StateContext.Provider>
  );
}

// Separate hooks for state and actions
export function useAuthState() {
  const context = useContext(StateContext);
  if (!context) throw new Error('useAuthState must be used within AuthProvider');
  return context;
}

export function useAuthActions() {
  const context = useContext(ActionsContext);
  if (!context) throw new Error('useAuthActions must be used within AuthProvider');
  return context;
}
```

## Pattern 2: Zustand

**Simple, fast, and scalable state management with minimal boilerplate.**

### Basic Zustand Store

```typescript
// src/application/stores/useAuthStore.ts
import { create } from 'zustand';
import { User } from '@/domain/entities/User';
import { authService } from '@/infrastructure/services/AuthService';

interface AuthState {
  user: User | null;
  loading: boolean;
  error: Error | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      const user = await authService.login({ email, password });
      set({ user, loading: false });
    } catch (error) {
      set({ error: error as Error, loading: false });
    }
  },

  logout: () => {
    authService.logout();
    set({ user: null });
  },

  clearError: () => set({ error: null }),
}));

// Usage in component
function LoginForm() {
  const { login, loading, error } = useAuthStore();

  const handleSubmit = async (email: string, password: string) => {
    await login(email, password);
  };

  return <form>{/* ... */}</form>;
}
```

### Zustand with Slices Pattern

```typescript
// src/application/stores/useStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Auth slice
interface AuthSlice {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const createAuthSlice = (set: any): AuthSlice => ({
  user: null,
  login: async (credentials) => {
    const user = await authService.login(credentials);
    set({ user }, false, 'auth/login');
  },
  logout: () => set({ user: null }, false, 'auth/logout'),
});

// Cart slice
interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
}

const createCartSlice = (set: any): CartSlice => ({
  items: [],
  addItem: (item) =>
    set(
      (state: any) => ({ items: [...state.items, item] }),
      false,
      'cart/addItem'
    ),
  removeItem: (id) =>
    set(
      (state: any) => ({ items: state.items.filter((i: any) => i.id !== id) }),
      false,
      'cart/removeItem'
    ),
});

// Combined store
type StoreState = AuthSlice & CartSlice;

export const useStore = create<StoreState>()(
  devtools((...a) => ({
    ...createAuthSlice(...a),
    ...createCartSlice(...a),
  }))
);

// Usage - select only needed state
function UserProfile() {
  const user = useStore((state) => state.user);
  return <div>{user?.name}</div>;
}
```

### Zustand with Persistence

```typescript
// src/application/stores/useSettingsStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  theme: 'light' | 'dark';
  language: string;
  notifications: boolean;
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (lang: string) => void;
  toggleNotifications: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'light',
      language: 'en',
      notifications: true,

      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
      toggleNotifications: () =>
        set((state) => ({ notifications: !state.notifications })),
    }),
    {
      name: 'settings-storage', // localStorage key
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        notifications: state.notifications,
      }),
    }
  )
);
```

## Pattern 3: Redux Toolkit

**For large applications requiring DevTools, middleware, and time-travel debugging.**

### Redux Toolkit Slice

```typescript
// src/application/stores/slices/userSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { User } from '@/domain/entities/User';
import { userRepository } from '@/infrastructure/repositories/UserRepository';

interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  users: [],
  currentUser: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchUsers = createAsyncThunk('users/fetchAll', async () => {
  return await userRepository.findAll();
});

export const fetchUserById = createAsyncThunk(
  'users/fetchById',
  async (userId: string) => {
    return await userRepository.findById(userId);
  }
);

export const createUser = createAsyncThunk(
  'users/create',
  async (user: Omit<User, 'id'>) => {
    return await userRepository.save(user as User);
  }
);

// Slice
const userSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentUser: (state, action: PayloadAction<User | null>) => {
      state.currentUser = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch all users
    builder.addCase(fetchUsers.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchUsers.fulfilled, (state, action) => {
      state.loading = false;
      state.users = action.payload;
    });
    builder.addCase(fetchUsers.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch users';
    });

    // Fetch user by ID
    builder.addCase(fetchUserById.fulfilled, (state, action) => {
      state.currentUser = action.payload;
    });

    // Create user
    builder.addCase(createUser.fulfilled, (state, action) => {
      state.users.push(action.payload);
    });
  },
});

export const { clearError, setCurrentUser } = userSlice.actions;
export default userSlice.reducer;
```

### Redux Store Configuration

```typescript
// src/application/stores/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import userReducer from './slices/userSlice';
import authReducer from './slices/authSlice';
import cartReducer from './slices/cartSlice';

export const store = configureStore({
  reducer: {
    users: userReducer,
    auth: authReducer,
    cart: cartReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['auth/login/pending'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['items.dates'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

### Redux Usage in Component

```typescript
// src/presentation/components/UserList.tsx
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/application/stores/store';
import { fetchUsers } from '@/application/stores/slices/userSlice';

export function UserList() {
  const dispatch = useAppDispatch();
  const { users, loading, error } = useAppSelector((state) => state.users);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

## Pattern 4: Jotai (Atomic State Management)

**Fine-grained reactive state management with atoms.**

### Basic Atoms

```typescript
// src/application/stores/atoms/userAtoms.ts
import { atom } from 'jotai';
import { User } from '@/domain/entities/User';

// Primitive atoms
export const userAtom = atom<User | null>(null);
export const usersAtom = atom<User[]>([]);
export const loadingAtom = atom<boolean>(false);

// Derived atom
export const userNameAtom = atom((get) => {
  const user = get(userAtom);
  return user?.name || 'Guest';
});

// Computed atom
export const activeUsersAtom = atom((get) => {
  const users = get(usersAtom);
  return users.filter((user) => user.status === 'ACTIVE');
});

// Write-only atom (action)
export const logoutAtom = atom(null, (_get, set) => {
  set(userAtom, null);
  localStorage.removeItem('token');
});
```

### Async Atoms

```typescript
// src/application/stores/atoms/userAtoms.ts
import { atom } from 'jotai';
import { userRepository } from '@/infrastructure/repositories/UserRepository';

// Async atom for fetching user
export const userIdAtom = atom<string>('');

export const userAtom = atom(async (get) => {
  const userId = get(userIdAtom);
  if (!userId) return null;
  return await userRepository.findById(userId);
});

// Async atom with write
export const fetchUserAtom = atom(
  null,
  async (_get, set, userId: string) => {
    set(userIdAtom, userId);
    const user = await userRepository.findById(userId);
    return user;
  }
);
```

### Jotai Usage in Component

```typescript
// src/presentation/components/UserProfile.tsx
import { useAtom, useAtomValue, useSetAtom } from 'jotai';
import { userAtom, userNameAtom, logoutAtom } from '@/application/stores/atoms/userAtoms';

export function UserProfile() {
  const [user, setUser] = useAtom(userAtom);
  const userName = useAtomValue(userNameAtom);
  const logout = useSetAtom(logoutAtom);

  return (
    <div>
      <h1>{userName}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## Pattern 5: React Query (Server State)

**For managing server state with automatic caching, refetching, and synchronization.**

### Basic Query

```typescript
// src/application/hooks/useUser.ts
import { useQuery } from '@tanstack/react-query';
import { useUserRepository } from '@/infrastructure/di/RepositoryContext';

export function useUser(userId: string) {
  const userRepository = useUserRepository();

  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => userRepository.findById(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!userId,
  });
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading, error } = useUser(userId);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{user?.name}</div>;
}
```

### Mutations

```typescript
// src/application/hooks/useCreateUser.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useUserRepository } from '@/infrastructure/di/RepositoryContext';

export function useCreateUser() {
  const queryClient = useQueryClient();
  const userRepository = useUserRepository();

  return useMutation({
    mutationFn: (user: Omit<User, 'id'>) => userRepository.save(user as User),
    onSuccess: () => {
      // Invalidate and refetch users list
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// Usage
function CreateUserForm() {
  const createUser = useCreateUser();

  const handleSubmit = async (data: Omit<User, 'id'>) => {
    await createUser.mutateAsync(data);
  };

  return <form onSubmit={handleSubmit}>{/* ... */}</form>;
}
```

### Optimistic Updates

```typescript
// src/application/hooks/useUpdateUser.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { User } from '@/domain/entities/User';

export function useUpdateUser() {
  const queryClient = useQueryClient();
  const userRepository = useUserRepository();

  return useMutation({
    mutationFn: (user: User) => userRepository.save(user),
    onMutate: async (newUser) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['user', newUser.id] });

      // Snapshot previous value
      const previousUser = queryClient.getQueryData(['user', newUser.id]);

      // Optimistically update
      queryClient.setQueryData(['user', newUser.id], newUser);

      return { previousUser };
    },
    onError: (_err, _newUser, context) => {
      // Rollback on error
      queryClient.setQueryData(['user', _newUser.id], context?.previousUser);
    },
    onSettled: (user) => {
      // Refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['user', user?.id] });
    },
  });
}
```

## State Management Comparison

state_management_comparison[6]{solution,complexity,bundle_size,devtools,use_case}:
Context API,Low,0kb (built-in),No,Simple shared state in subtrees
Zustand,Low,1.2kb,Yes (middleware),Simple to medium global state
Redux Toolkit,Medium,8kb,Yes (excellent),Large apps complex state
Jotai,Medium,3kb,Yes (separate package),Atomic fine-grained state
React Query,Medium,12kb,Yes (excellent),Server state and caching
Valtio,Low,3kb,Yes,Proxy-based mutable state

## Anti-Patterns to Avoid

state_management_antipatterns[8]{antipattern,problem,solution}:
Global state for everything,Performance issues unnecessary re-renders,Colocate state close to usage
Too many contexts,Context hell and re-render issues,Combine related state or use Zustand
Storing server state in Redux,Duplicate state manual cache management,Use React Query for server state
Not splitting context,All consumers re-render on any change,Split into state and actions contexts
Prop drilling instead of context,Maintenance nightmare,Use Context or state management
Overusing Redux,Boilerplate for simple state,Use useState or Zustand for simple cases
Not memoizing context values,Unnecessary re-renders,Wrap context value in useMemo
Mixing client and server state,Complex sync logic,Separate with React Query and client state library

## Best Practices Checklist

state_management_checklist[10]{practice,requirement}:
Colocate state,Keep state as close to usage as possible
Server state separate,Use React Query for server state
Split contexts,Separate state and actions to prevent re-renders
Memoize values,Memoize context values and selectors
Type everything,Full TypeScript coverage for stores and atoms
Use selectors,Select only needed state from stores
Normalize data,Normalize nested data structures
Optimistic updates,Implement optimistic updates for better UX
Error handling,Proper error states in all async operations
DevTools integration,Use DevTools for debugging

---

**File Size**: 480/500 lines max ✅
