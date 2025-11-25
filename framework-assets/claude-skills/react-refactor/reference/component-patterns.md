# React Component Patterns

**Comprehensive guide to modern React component patterns: HOC, Render Props, Compound Components, Hooks, and migration strategies.**

## Pattern Evolution Timeline

pattern_evolution[5]{pattern,era,status,modern_replacement}:
Higher-Order Components (HOC),2015-2018,Legacy,Custom Hooks
Render Props,2017-2019,Legacy,Custom Hooks
Compound Components,2016-Present,Active,Compound + Context + Hooks
Container/Presentational,2015-Present,Active,Custom Hooks + Pure Components
Custom Hooks,2019-Present,Modern Standard,N/A - this is the current best practice

## Pattern 1: Custom Hooks (Modern Standard)

**The modern way to share stateful logic across components.**

### Basic Custom Hook

```typescript
// src/application/hooks/useToggle.ts
import { useState, useCallback } from 'react';

export interface UseToggleResult {
  isOn: boolean;
  toggle: () => void;
  setOn: () => void;
  setOff: () => void;
}

export function useToggle(initialValue = false): UseToggleResult {
  const [isOn, setIsOn] = useState(initialValue);

  const toggle = useCallback(() => setIsOn(prev => !prev), []);
  const setOn = useCallback(() => setIsOn(true), []);
  const setOff = useCallback(() => setIsOn(false), []);

  return { isOn, toggle, setOn, setOff };
}

// Usage in component
function Modal() {
  const { isOn: isOpen, toggle, setOff } = useToggle(false);

  return (
    <>
      <button onClick={toggle}>Open Modal</button>
      {isOpen && (
        <div className="modal">
          <button onClick={setOff}>Close</button>
        </div>
      )}
    </>
  );
}
```

### Complex Custom Hook with Dependencies

```typescript
// src/application/hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchInput() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  useEffect(() => {
    if (debouncedSearch) {
      // API call here
      searchAPI(debouncedSearch);
    }
  }, [debouncedSearch]);

  return <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />;
}
```

### Hook with Cleanup

```typescript
// src/application/hooks/useEventListener.ts
import { useEffect, useRef } from 'react';

export function useEventListener<K extends keyof WindowEventMap>(
  eventName: K,
  handler: (event: WindowEventMap[K]) => void,
  element: HTMLElement | Window = window
) {
  const savedHandler = useRef(handler);

  useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);

  useEffect(() => {
    const isSupported = element && element.addEventListener;
    if (!isSupported) return;

    const eventListener = (event: Event) => savedHandler.current(event as WindowEventMap[K]);

    element.addEventListener(eventName, eventListener);

    return () => {
      element.removeEventListener(eventName, eventListener);
    };
  }, [eventName, element]);
}

// Usage
function App() {
  useEventListener('resize', () => {
    console.log('Window resized!');
  });

  return <div>App</div>;
}
```

## Pattern 2: Compound Components

**Components that work together to share implicit state.**

### Basic Compound Component

```typescript
// src/presentation/components/Tabs/Tabs.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

function useTabs() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tabs compound components must be used within Tabs');
  }
  return context;
}

interface TabsProps {
  defaultTab?: string;
  children: ReactNode;
}

export function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || '');

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

interface TabListProps {
  children: ReactNode;
}

function TabList({ children }: TabListProps) {
  return <div className="tab-list">{children}</div>;
}

interface TabProps {
  id: string;
  children: ReactNode;
}

function Tab({ id, children }: TabProps) {
  const { activeTab, setActiveTab } = useTabs();

  return (
    <button
      className={`tab ${activeTab === id ? 'active' : ''}`}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
}

interface TabPanelsProps {
  children: ReactNode;
}

function TabPanels({ children }: TabPanelsProps) {
  return <div className="tab-panels">{children}</div>;
}

interface TabPanelProps {
  id: string;
  children: ReactNode;
}

function TabPanel({ id, children }: TabPanelProps) {
  const { activeTab } = useTabs();

  if (activeTab !== id) return null;

  return <div className="tab-panel">{children}</div>;
}

// Attach compound components
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panels = TabPanels;
Tabs.Panel = TabPanel;

// Usage
function MyComponent() {
  return (
    <Tabs defaultTab="profile">
      <Tabs.List>
        <Tabs.Tab id="profile">Profile</Tabs.Tab>
        <Tabs.Tab id="settings">Settings</Tabs.Tab>
      </Tabs.List>

      <Tabs.Panels>
        <Tabs.Panel id="profile">
          <h2>Profile Content</h2>
        </Tabs.Panel>
        <Tabs.Panel id="settings">
          <h2>Settings Content</h2>
        </Tabs.Panel>
      </Tabs.Panels>
    </Tabs>
  );
}
```

### Advanced Compound Component with Controlled State

```typescript
// src/presentation/components/Accordion/Accordion.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AccordionContextType {
  openItems: Set<string>;
  toggle: (id: string) => void;
  allowMultiple: boolean;
}

const AccordionContext = createContext<AccordionContextType | undefined>(undefined);

function useAccordion() {
  const context = useContext(AccordionContext);
  if (!context) {
    throw new Error('Accordion compound components must be used within Accordion');
  }
  return context;
}

interface AccordionProps {
  allowMultiple?: boolean;
  defaultOpenItems?: string[];
  children: ReactNode;
}

export function Accordion({ allowMultiple = false, defaultOpenItems = [], children }: AccordionProps) {
  const [openItems, setOpenItems] = useState(new Set(defaultOpenItems));

  const toggle = (id: string) => {
    setOpenItems(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (!allowMultiple) {
          next.clear();
        }
        next.add(id);
      }
      return next;
    });
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggle, allowMultiple }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

interface AccordionItemProps {
  id: string;
  children: ReactNode;
}

function AccordionItem({ id, children }: AccordionItemProps) {
  return <div className="accordion-item">{children}</div>;
}

interface AccordionTriggerProps {
  id: string;
  children: ReactNode;
}

function AccordionTrigger({ id, children }: AccordionTriggerProps) {
  const { openItems, toggle } = useAccordion();
  const isOpen = openItems.has(id);

  return (
    <button
      className={`accordion-trigger ${isOpen ? 'open' : ''}`}
      onClick={() => toggle(id)}
      aria-expanded={isOpen}
    >
      {children}
    </button>
  );
}

interface AccordionContentProps {
  id: string;
  children: ReactNode;
}

function AccordionContent({ id, children }: AccordionContentProps) {
  const { openItems } = useAccordion();
  const isOpen = openItems.has(id);

  if (!isOpen) return null;

  return <div className="accordion-content">{children}</div>;
}

Accordion.Item = AccordionItem;
Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;
```

## Pattern 3: Container/Presentational Separation

**Separate data fetching and logic (Container) from rendering (Presentational).**

### Presentational Component (Pure)

```typescript
// src/presentation/components/UserList/UserListView.tsx
import React from 'react';
import { User } from '@/domain/entities/User';

interface UserListViewProps {
  users: User[];
  loading: boolean;
  error: Error | null;
  onUserClick: (userId: string) => void;
}

export function UserListView({ users, loading, error, onUserClick }: UserListViewProps) {
  if (loading) {
    return <div>Loading users...</div>;
  }

  if (error) {
    return <div className="error">Error: {error.message}</div>;
  }

  if (users.length === 0) {
    return <div>No users found</div>;
  }

  return (
    <ul className="user-list">
      {users.map(user => (
        <li key={user.id} onClick={() => onUserClick(user.id)}>
          <h3>{user.name}</h3>
          <p>{user.email}</p>
        </li>
      ))}
    </ul>
  );
}
```

### Container Component (Logic)

```typescript
// src/presentation/components/UserList/UserListContainer.tsx
import React, { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUsers } from '@/application/hooks/useUsers';
import { useUserRepository } from '@/infrastructure/di/RepositoryContext';
import { UserListView } from './UserListView';

export function UserListContainer() {
  const navigate = useNavigate();
  const userRepository = useUserRepository();
  const { users, loading, error } = useUsers(userRepository);

  const handleUserClick = useCallback((userId: string) => {
    navigate(`/users/${userId}`);
  }, [navigate]);

  return (
    <UserListView
      users={users}
      loading={loading}
      error={error}
      onUserClick={handleUserClick}
    />
  );
}
```

## Pattern 4: Render Props (Legacy - Migrate to Hooks)

**How to migrate Render Props to Custom Hooks.**

### Before: Render Props

```typescript
// ❌ OLD: Render Props pattern
interface MouseTrackerProps {
  render: (position: { x: number; y: number }) => React.ReactElement;
}

class MouseTracker extends React.Component<MouseTrackerProps> {
  state = { x: 0, y: 0 };

  handleMouseMove = (event: MouseEvent) => {
    this.setState({ x: event.clientX, y: event.clientY });
  };

  componentDidMount() {
    window.addEventListener('mousemove', this.handleMouseMove);
  }

  componentWillUnmount() {
    window.removeEventListener('mousemove', this.handleMouseMove);
  }

  render() {
    return this.props.render(this.state);
  }
}

// Usage
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        <div>Mouse position: {x}, {y}</div>
      )}
    />
  );
}
```

### After: Custom Hook

```typescript
// ✅ NEW: Custom Hook
function useMousePosition() {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setPosition({ x: event.clientX, y: event.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return position;
}

// Usage
function App() {
  const { x, y } = useMousePosition();
  return <div>Mouse position: {x}, {y}</div>;
}
```

## Pattern 5: Higher-Order Components (Legacy - Migrate to Hooks)

**How to migrate HOCs to Custom Hooks.**

### Before: HOC Pattern

```typescript
// ❌ OLD: HOC pattern
function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      authService.getCurrentUser().then(user => {
        setUser(user);
        setLoading(false);
      });
    }, []);

    if (loading) return <div>Loading...</div>;
    if (!user) return <div>Please login</div>;

    return <Component {...props} user={user} />;
  };
}

// Usage
const ProtectedPage = withAuth(({ user }: { user: User }) => {
  return <div>Welcome, {user.name}</div>;
});
```

### After: Custom Hook

```typescript
// ✅ NEW: Custom Hook
function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authService.getCurrentUser().then(user => {
      setUser(user);
      setLoading(false);
    });
  }, []);

  return { user, loading, isAuthenticated: !!user };
}

// Usage
function ProtectedPage() {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please login</div>;

  return <div>Welcome, {user!.name}</div>;
}
```

### Migration Strategy: Multiple HOCs

```typescript
// ❌ OLD: Multiple HOCs
const EnhancedComponent = withRouter(
  withAuth(
    withLoading(
      withErrorBoundary(MyComponent)
    )
  )
);

// ✅ NEW: Multiple Hooks
function MyComponent() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { data, loading: dataLoading } = useData();
  const errorBoundary = useErrorBoundary();

  const loading = authLoading || dataLoading;

  // Component logic...
}
```

## TypeScript Patterns

### Generic Components

```typescript
// Generic List component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
  emptyMessage?: string;
}

export function List<T>({ items, renderItem, keyExtractor, emptyMessage }: ListProps<T>) {
  if (items.length === 0) {
    return <div>{emptyMessage || 'No items'}</div>;
  }

  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// Usage
function UserList({ users }: { users: User[] }) {
  return (
    <List
      items={users}
      renderItem={user => <div>{user.name}</div>}
      keyExtractor={user => user.id}
    />
  );
}
```

### Type-Safe Context

```typescript
// Type-safe context pattern
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### Discriminated Union Props

```typescript
// Discriminated union for button variants
type ButtonProps =
  | {
      variant: 'primary';
      onClick: () => void;
      children: ReactNode;
    }
  | {
      variant: 'link';
      href: string;
      children: ReactNode;
    };

export function Button(props: ButtonProps) {
  if (props.variant === 'primary') {
    return (
      <button className="btn-primary" onClick={props.onClick}>
        {props.children}
      </button>
    );
  }

  return (
    <a className="btn-link" href={props.href}>
      {props.children}
    </a>
  );
}
```

## Advanced Hook Patterns

### useReducer for Complex State

```typescript
// Complex state management with useReducer
interface State {
  data: User[];
  loading: boolean;
  error: Error | null;
  filters: {
    search: string;
    status: string;
  };
}

type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: User[] }
  | { type: 'FETCH_ERROR'; payload: Error }
  | { type: 'SET_SEARCH'; payload: string }
  | { type: 'SET_STATUS'; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, data: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'SET_SEARCH':
      return { ...state, filters: { ...state.filters, search: action.payload } };
    case 'SET_STATUS':
      return { ...state, filters: { ...state.filters, status: action.payload } };
    default:
      return state;
  }
}

function useUsers() {
  const [state, dispatch] = useReducer(reducer, {
    data: [],
    loading: false,
    error: null,
    filters: { search: '', status: 'all' },
  });

  const fetchUsers = useCallback(async () => {
    dispatch({ type: 'FETCH_START' });
    try {
      const users = await api.getUsers(state.filters);
      dispatch({ type: 'FETCH_SUCCESS', payload: users });
    } catch (error) {
      dispatch({ type: 'FETCH_ERROR', payload: error as Error });
    }
  }, [state.filters]);

  return { ...state, fetchUsers, dispatch };
}
```

### Custom Hook with Dependency Injection

```typescript
// Hook with injected dependencies
interface UseUserOptions {
  repository: IUserRepository;
  cache?: ICache;
}

export function useUser(userId: string, options: UseUserOptions) {
  const { repository, cache } = options;
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      // Try cache first
      if (cache) {
        const cached = await cache.get(`user:${userId}`);
        if (cached && !cancelled) {
          setUser(cached);
          setLoading(false);
          return;
        }
      }

      // Fetch from repository
      const user = await repository.findById(userId);
      if (!cancelled) {
        setUser(user);
        setLoading(false);

        // Update cache
        if (cache && user) {
          await cache.set(`user:${userId}`, user);
        }
      }
    };

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId, repository, cache]);

  return { user, loading };
}
```

## Pattern Decision Guide

pattern_decision_guide[6]{scenario,recommended_pattern,reasoning}:
Sharing stateful logic,Custom Hooks,Most flexible and composable
Related components working together,Compound Components,Clear API and shared implicit state
Separating logic from UI,Container/Presentational + Hooks,Testability and reusability
Complex form state,useReducer + Custom Hook,Predictable state updates
Cross-cutting concerns (auth logging),Custom Hooks,Replace HOCs with hooks
Type-safe prop variations,Discriminated Unions,Type safety and IDE autocomplete

## Best Practices Checklist

component_pattern_checklist[12]{practice,requirement}:
Use custom hooks,Extract reusable logic to custom hooks
Avoid HOCs,Replace HOCs with custom hooks
Avoid render props,Replace render props with custom hooks
Use compound components,For related components like Tabs Accordions
Type everything,Full TypeScript coverage for components and hooks
Pure presentational components,No side effects in presentational components
Colocate state,Keep state close to where it's used
Memoize callbacks,Use useCallback for callbacks passed to children
Extract complex state,Use useReducer for complex state logic
Dependency injection,Inject dependencies via props or context
Generic when reusable,Use TypeScript generics for reusable components
Test hooks separately,Test custom hooks with renderHook

---

**File Size**: 460/500 lines max ✅
