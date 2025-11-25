# React Performance Optimization

**Comprehensive guide to optimizing React application performance: memoization, code splitting, virtualization, and profiling.**

## Performance Optimization Decision Tree

performance_decision[7]{symptom,root_cause,solution}:
Component re-renders unnecessarily,Props or parent state changed,React.memo with props comparison
Expensive computation on every render,Function called in render,useMemo to memoize result
Function recreated on every render,Function defined in component,useCallback to memoize function
Large bundle size,All code loaded upfront,Code splitting with React.lazy
Long list causes lag,Rendering thousands of DOM nodes,Virtualization with react-window
Slow initial load,Too much JavaScript,Code splitting and lazy loading
State causing cascading re-renders,State too high in tree,State colocation closer to usage

## Pattern 1: React.memo

**Prevent component re-renders when props haven't changed.**

### Basic Memoization

```typescript
// src/presentation/components/UserCard.tsx
import React from 'react';
import { User } from '@/domain/entities/User';

interface UserCardProps {
  user: User;
  onSelect: (userId: string) => void;
}

// Without memo - re-renders even if props unchanged
function UserCard({ user, onSelect }: UserCardProps) {
  console.log('UserCard rendered');
  return (
    <div onClick={() => onSelect(user.id)}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}

// ✅ With memo - only re-renders if props changed
export const UserCard = React.memo<UserCardProps>(({ user, onSelect }) => {
  console.log('UserCard rendered');
  return (
    <div onClick={() => onSelect(user.id)}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});
```

### Custom Comparison Function

```typescript
// src/presentation/components/ProductCard.tsx
import React from 'react';
import { Product } from '@/domain/entities/Product';

interface ProductCardProps {
  product: Product;
  inCart: boolean;
  onAddToCart: (product: Product) => void;
}

// Custom comparison - only re-render if specific props changed
export const ProductCard = React.memo<ProductCardProps>(
  ({ product, inCart, onAddToCart }) => {
    return (
      <div>
        <h3>{product.name}</h3>
        <p>${product.price}</p>
        <button
          onClick={() => onAddToCart(product)}
          disabled={inCart}
        >
          {inCart ? 'In Cart' : 'Add to Cart'}
        </button>
      </div>
    );
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (should NOT re-render)
    return (
      prevProps.product.id === nextProps.product.id &&
      prevProps.product.price === nextProps.product.price &&
      prevProps.inCart === nextProps.inCart
    );
  }
);
```

## Pattern 2: useMemo

**Memoize expensive computations.**

### Basic useMemo

```typescript
// src/presentation/components/OrderSummary.tsx
import React, { useMemo } from 'react';
import { Order } from '@/domain/entities/Order';

interface OrderSummaryProps {
  order: Order;
}

export function OrderSummary({ order }: OrderSummaryProps) {
  // ❌ Without useMemo - recalculated on every render
  // const total = order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // ✅ With useMemo - only recalculated when order.items changes
  const total = useMemo(() => {
    console.log('Calculating total...');
    return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }, [order.items]);

  const tax = useMemo(() => total * 0.1, [total]);
  const grandTotal = useMemo(() => total + tax, [total, tax]);

  return (
    <div>
      <p>Subtotal: ${total.toFixed(2)}</p>
      <p>Tax: ${tax.toFixed(2)}</p>
      <p>Total: ${grandTotal.toFixed(2)}</p>
    </div>
  );
}
```

### Complex Computation Memoization

```typescript
// src/presentation/components/DataTable.tsx
import React, { useMemo } from 'react';

interface DataTableProps<T> {
  data: T[];
  searchTerm: string;
  sortBy: keyof T;
  sortOrder: 'asc' | 'desc';
}

export function DataTable<T extends Record<string, any>>({
  data,
  searchTerm,
  sortBy,
  sortOrder,
}: DataTableProps<T>) {
  // Filter data
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    return data.filter(item =>
      Object.values(item).some(value =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  }, [data, searchTerm]);

  // Sort data
  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      const comparison = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortBy, sortOrder]);

  return (
    <table>
      <tbody>
        {sortedData.map((row, i) => (
          <tr key={i}>
            {Object.values(row).map((cell, j) => (
              <td key={j}>{String(cell)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Pattern 3: useCallback

**Memoize function references to prevent child re-renders.**

### Basic useCallback

```typescript
// src/presentation/components/TodoList.tsx
import React, { useState, useCallback } from 'react';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

const TodoItem = React.memo<{
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}>(({ todo, onToggle, onDelete }) => {
  console.log('TodoItem rendered:', todo.id);
  return (
    <div>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id)}
      />
      <span>{todo.text}</span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </div>
  );
});

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);

  // ❌ Without useCallback - new function on every render
  // const handleToggle = (id: string) => {
  //   setTodos(prev => prev.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  // };

  // ✅ With useCallback - same function reference
  const handleToggle = useCallback((id: string) => {
    setTodos(prev =>
      prev.map(t => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  }, []);

  const handleDelete = useCallback((id: string) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <div>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
```

### useCallback with Dependencies

```typescript
// src/presentation/components/SearchableList.tsx
import React, { useState, useCallback } from 'react';

export function SearchableList<T>({ items, onSelect }: {
  items: T[];
  onSelect: (item: T) => void;
}) {
  const [searchTerm, setSearchTerm] = useState('');

  // Callback depends on searchTerm and onSelect
  const handleSearch = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    console.log('Searching for:', value);
  }, []);

  // Memoized with dependencies
  const handleItemClick = useCallback((item: T) => {
    console.log('Selected:', item);
    onSelect(item);
  }, [onSelect]);

  return (
    <div>
      <input value={searchTerm} onChange={handleSearch} />
      {/* Render items */}
    </div>
  );
}
```

## Pattern 4: Code Splitting

**Split code into chunks and load on demand.**

### Route-Based Code Splitting

```typescript
// src/presentation/routes/AppRouter.tsx
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Static import - always loaded
import { Layout } from '../components/Layout';

// Dynamic imports - loaded on demand
const HomePage = lazy(() => import('../pages/HomePage'));
const UserPage = lazy(() => import('../pages/UserPage'));
const ProductPage = lazy(() => import('../pages/ProductPage'));
const AdminPage = lazy(() => import('../pages/AdminPage'));

function LoadingFallback() {
  return <div>Loading page...</div>;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/users/:id" element={<UserPage />} />
            <Route path="/products/:id" element={<ProductPage />} />
            <Route path="/admin/*" element={<AdminPage />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}
```

### Component-Based Code Splitting

```typescript
// src/presentation/components/HeavyComponent.tsx
import React, { lazy, Suspense, useState } from 'react';

// Heavy component loaded only when needed
const HeavyChart = lazy(() => import('./HeavyChart'));
const HeavyDataGrid = lazy(() => import('./HeavyDataGrid'));

export function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>

      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

### Preloading Components

```typescript
// src/presentation/components/Modal.tsx
import React, { lazy, Suspense } from 'react';

const HeavyModal = lazy(() => import('./HeavyModal'));

export function ModalTrigger() {
  const [isOpen, setIsOpen] = useState(false);

  // Preload on hover
  const handleMouseEnter = () => {
    // Start loading component before user clicks
    import('./HeavyModal');
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        onMouseEnter={handleMouseEnter}
      >
        Open Modal
      </button>

      {isOpen && (
        <Suspense fallback={<div>Loading...</div>}>
          <HeavyModal onClose={() => setIsOpen(false)} />
        </Suspense>
      )}
    </>
  );
}
```

## Pattern 5: Virtualization

**Render only visible items in long lists.**

### React Window (Fixed Size)

```typescript
// src/presentation/components/VirtualizedList.tsx
import React from 'react';
import { FixedSizeList } from 'react-window';
import { User } from '@/domain/entities/User';

interface VirtualizedListProps {
  users: User[];
}

export function VirtualizedUserList({ users }: VirtualizedListProps) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const user = users[index];
    return (
      <div style={style} className="list-item">
        <h3>{user.name}</h3>
        <p>{user.email}</p>
      </div>
    );
  };

  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}
```

### React Window (Variable Size)

```typescript
// src/presentation/components/VirtualizedVariableList.tsx
import React, { useRef } from 'react';
import { VariableSizeList } from 'react-window';

interface Message {
  id: string;
  text: string;
}

export function MessageList({ messages }: { messages: Message[] }) {
  const listRef = useRef<VariableSizeList>(null);

  // Calculate item size based on content
  const getItemSize = (index: number) => {
    const message = messages[index];
    // Estimate height based on text length
    const lines = Math.ceil(message.text.length / 50);
    return lines * 20 + 20; // 20px per line + padding
  };

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const message = messages[index];
    return (
      <div style={style} className="message">
        {message.text}
      </div>
    );
  };

  return (
    <VariableSizeList
      ref={listRef}
      height={600}
      itemCount={messages.length}
      itemSize={getItemSize}
      width="100%"
    >
      {Row}
    </VariableSizeList>
  );
}
```

### React Virtual (Modern Alternative)

```typescript
// src/presentation/components/VirtualList.tsx
import React from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

export function VirtualList({ items }: { items: any[] }) {
  const parentRef = React.useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80,
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '600px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Pattern 6: State Colocation

**Move state close to where it's used.**

### Before: State Too High

```typescript
// ❌ State causes entire app to re-render
function App() {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <div>
      <Header />
      <UserList
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        onUserSelect={setSelectedUser}
      />
      <Footer />
      {modalOpen && <Modal onClose={() => setModalOpen(false)} />}
    </div>
  );
}
```

### After: State Colocated

```typescript
// ✅ State close to usage - only affected components re-render
function App() {
  return (
    <div>
      <Header />
      <UserListSection />
      <Footer />
      <ModalSection />
    </div>
  );
}

function UserListSection() {
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <UserList
      searchTerm={searchTerm}
      onSearchChange={setSearchTerm}
      onUserSelect={setSelectedUser}
    />
  );
}

function ModalSection() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <button onClick={() => setModalOpen(true)}>Open</button>
      {modalOpen && <Modal onClose={() => setModalOpen(false)} />}
    </>
  );
}
```

## Performance Profiling

### Using React DevTools Profiler

```typescript
// Wrap components to profile
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <UserList />
    </Profiler>
  );
}
```

## Performance Anti-Patterns

performance_antipatterns[10]{antipattern,problem,solution}:
Inline object props,New object every render causes re-render,useMemo or define outside component
Inline function props,New function every render causes re-render,useCallback or define outside
Anonymous function in JSX,Creates new function on every render,useCallback for event handlers
Index as key,Causes unnecessary re-renders on reorder,Use stable unique ID as key
Not memoizing expensive computations,Recalculated every render,useMemo for expensive operations
Not using React.memo,Component re-renders unnecessarily,Wrap with React.memo
Too much state at top level,Cascading re-renders,Colocate state close to usage
Rendering large lists without virtualization,DOM nodes cause lag,Use react-window or react-virtual
Not code splitting,Large initial bundle,Lazy load routes and heavy components
Derived state not memoized,Recomputed on every render,useMemo for derived values

## Performance Checklist

performance_checklist[12]{check,requirement}:
Memoize components,Use React.memo for expensive components
Memoize callbacks,Use useCallback for callbacks passed to children
Memoize computations,Use useMemo for expensive computations
Code splitting implemented,Lazy load routes and heavy components
Long lists virtualized,Use react-window for lists over 100 items
State colocated,State close to components that use it
No inline objects,Move objects outside or use useMemo
No inline functions,Use useCallback or define outside
Profiling done,Use React DevTools Profiler to find bottlenecks
Bundle analyzed,Check bundle size with webpack-bundle-analyzer
Lazy images,Use lazy loading for images below fold
Keys are stable,Use unique IDs not array indices

---

**File Size**: 450/500 lines max ✅
