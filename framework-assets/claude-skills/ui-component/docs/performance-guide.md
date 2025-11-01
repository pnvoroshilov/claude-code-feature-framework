# Performance Guide for React Components

## Introduction

This guide covers performance optimization strategies for React components, including memoization, code splitting, virtualization, and profiling techniques.

## Understanding React Rendering

### Rendering Process

1. **Trigger**: State/props change triggers re-render
2. **Render Phase**: React calls component functions
3. **Commit Phase**: React updates DOM
4. **Browser Paint**: Browser paints updated DOM

### When Components Re-render

- Parent component re-renders
- Component's own state changes
- Context value changes
- Props change (even if same value)

## Optimization Techniques

### 1. React.memo

Prevents unnecessary re-renders when props haven't changed.

```typescript
// Without memo - re-renders on every parent render
export const ExpensiveComponent: React.FC<Props> = ({ data }) => {
  // Expensive computation
  const processed = processData(data);
  return <div>{processed}</div>;
};

// With memo - only re-renders when props change
export const ExpensiveComponent = React.memo<Props>(
  ({ data }) => {
    const processed = processData(data);
    return <div>{processed}</div>;
  }
);

// Custom comparison function
export const ExpensiveComponent = React.memo<Props>(
  ({ data }) => {
    return <div>{data.value}</div>;
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (skip render)
    return prevProps.data.id === nextProps.data.id;
  }
);
```

### 2. useMemo

Memoizes expensive computations.

```typescript
export const DataTable: React.FC<Props> = ({ data, filter, sortBy }) => {
  // ❌ Bad - recomputes on every render
  const processedData = data
    .filter(filter)
    .sort(sortBy)
    .map(transform);

  // ✅ Good - only recomputes when dependencies change
  const processedData = useMemo(
    () => data.filter(filter).sort(sortBy).map(transform),
    [data, filter, sortBy]
  );

  return <Table data={processedData} />;
};

// Real-world example
export const SearchResults: React.FC<Props> = ({ items, searchTerm }) => {
  const filteredItems = useMemo(() => {
    if (!searchTerm) return items;

    return items.filter((item) =>
      item.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [items, searchTerm]);

  const sortedItems = useMemo(
    () => [...filteredItems].sort((a, b) => a.name.localeCompare(b.name)),
    [filteredItems]
  );

  return (
    <ul>
      {sortedItems.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
};
```

### 3. useCallback

Memoizes callback functions to prevent child re-renders.

```typescript
export const Parent: React.FC = () => {
  // ❌ Bad - new function on every render
  const handleClick = (id: number) => {
    console.log('Clicked:', id);
  };

  // ✅ Good - same function reference
  const handleClick = useCallback((id: number) => {
    console.log('Clicked:', id);
  }, []);

  return <ChildList items={items} onItemClick={handleClick} />;
};

// With dependencies
export const Form: React.FC = () => {
  const [values, setValues] = useState({});

  const handleChange = useCallback(
    (name: string, value: string) => {
      setValues((prev) => ({ ...prev, [name]: value }));
    },
    [] // No dependencies - setValues is stable
  );

  return <FormFields onChange={handleChange} />;
};
```

### 4. Code Splitting

Split code into smaller chunks loaded on demand.

```typescript
// Route-based splitting
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));

export const App: React.FC = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
};

// Component-based splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));
const VideoPlayer = lazy(() => import('./components/VideoPlayer'));

export const Dashboard: React.FC = () => {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<div>Loading chart...</div>}>
        <HeavyChart data={chartData} />
      </Suspense>
    </div>
  );
};

// Named export splitting
const AdminPanel = lazy(() =>
  import('./components/AdminPanel').then((module) => ({
    default: module.AdminPanel,
  }))
);
```

### 5. Virtual Scrolling

Render only visible items in large lists.

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

export const VirtualList: React.FC<{ items: Item[] }> = ({ items }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5, // Render 5 extra items above/below viewport
  });

  return (
    <div
      ref={parentRef}
      style={{
        height: '600px',
        overflow: 'auto',
      }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
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
            <ListItem item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};

// With dynamic heights
export const DynamicVirtualList: React.FC<Props> = ({ items }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: (index) => {
      // Estimate size based on content
      return items[index].longDescription ? 100 : 50;
    },
    measureElement:
      typeof window !== 'undefined' &&
      navigator.userAgent.indexOf('Firefox') === -1
        ? (element) => element?.getBoundingClientRect().height
        : undefined,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            data-index={virtualItem.index}
            ref={virtualizer.measureElement}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <ListItem item={items[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 6. Debouncing and Throttling

Limit frequency of expensive operations.

```typescript
import { debounce } from 'lodash';

// Debounce - wait until user stops typing
export const SearchInput: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // ❌ Bad - API call on every keystroke
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    searchAPI(value); // Called immediately
  };

  // ✅ Good - debounced API call
  const debouncedSearch = useMemo(
    () =>
      debounce((value: string) => {
        searchAPI(value);
      }, 300),
    []
  );

  useEffect(() => {
    return () => {
      debouncedSearch.cancel();
    };
  }, [debouncedSearch]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    debouncedSearch(value); // Called after 300ms of inactivity
  };

  return <input value={searchTerm} onChange={handleChange} />;
};

// Throttle - limit frequency of calls
export const ScrollTracker: React.FC = () => {
  const throttledScroll = useMemo(
    () =>
      throttle(() => {
        console.log('Scroll position:', window.scrollY);
      }, 100), // Max once per 100ms
    []
  );

  useEffect(() => {
    window.addEventListener('scroll', throttledScroll);
    return () => {
      window.removeEventListener('scroll', throttledScroll);
      throttledScroll.cancel();
    };
  }, [throttledScroll]);

  return <div>Tracking scroll...</div>;
};
```

### 7. Windowing for Large Data

Use react-window for efficient list rendering.

```typescript
import { FixedSizeList } from 'react-window';

export const LargeList: React.FC<{ items: Item[] }> = ({ items }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};

// Variable size list
import { VariableSizeList } from 'react-window';

export const VariableList: React.FC<{ items: Item[] }> = ({ items }) => {
  const getItemSize = (index: number) => {
    return items[index].longDescription ? 100 : 50;
  };

  const Row = ({ index, style }: RowProps) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <VariableSizeList
      height={600}
      itemCount={items.length}
      itemSize={getItemSize}
      width="100%"
    >
      {Row}
    </VariableSizeList>
  );
};
```

### 8. Optimize Images

```typescript
// Use next/image or similar optimized image component
import Image from 'next/image';

export const OptimizedImage: React.FC<Props> = ({ src, alt }) => {
  return (
    <Image
      src={src}
      alt={alt}
      width={800}
      height={600}
      loading="lazy" // Lazy load images
      placeholder="blur" // Show placeholder while loading
      quality={85} // Optimize quality vs size
    />
  );
};

// Native lazy loading
export const LazyImage: React.FC<Props> = ({ src, alt }) => {
  return <img src={src} alt={alt} loading="lazy" />;
};

// Responsive images
export const ResponsiveImage: React.FC<Props> = ({ src, alt }) => {
  return (
    <img
      src={src}
      alt={alt}
      srcSet={`
        ${src}?w=400 400w,
        ${src}?w=800 800w,
        ${src}?w=1200 1200w
      `}
      sizes="(max-width: 640px) 400px, (max-width: 1024px) 800px, 1200px"
      loading="lazy"
    />
  );
};
```

## State Management Optimization

### 1. State Colocation

Keep state close to where it's used.

```typescript
// ❌ Bad - unnecessary global state
export const App: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div>
      <Header />
      <Content />
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
};

// ✅ Good - colocate state with component that uses it
export const ModalContainer: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsModalOpen(true)}>Open Modal</button>
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
};
```

### 2. Split Context

Avoid unnecessary re-renders from context changes.

```typescript
// ❌ Bad - single context causes unnecessary re-renders
const AppContext = createContext({
  user: null,
  theme: 'light',
  setUser: () => {},
  setTheme: () => {},
});

// Component using only theme re-renders when user changes
const ThemedButton = () => {
  const { theme } = useContext(AppContext);
  return <button className={theme}>Button</button>;
};

// ✅ Good - separate contexts
const UserContext = createContext(null);
const ThemeContext = createContext('light');

// Component only re-renders when theme changes
const ThemedButton = () => {
  const theme = useContext(ThemeContext);
  return <button className={theme}>Button</button>;
};
```

### 3. Use Reducers for Complex State

```typescript
// ✅ Better state management with useReducer
type State = {
  data: Item[];
  loading: boolean;
  error: Error | null;
  filter: string;
  sortBy: string;
};

type Action =
  | { type: 'SET_DATA'; payload: Item[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: Error }
  | { type: 'SET_FILTER'; payload: string }
  | { type: 'SET_SORT'; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_DATA':
      return { ...state, data: action.payload, loading: false };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_FILTER':
      return { ...state, filter: action.payload };
    case 'SET_SORT':
      return { ...state, sortBy: action.payload };
    default:
      return state;
  }
}

export const DataView: React.FC = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  // Single dispatch for related updates
  const loadData = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const data = await fetchData();
      dispatch({ type: 'SET_DATA', payload: data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error });
    }
  };

  return <div>{/* UI */}</div>;
};
```

## Performance Monitoring

### 1. React DevTools Profiler

```typescript
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

export const App: React.FC = () => {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
};
```

### 2. Performance API

```typescript
export function measureRenderTime(componentName: string) {
  return {
    start: () => {
      performance.mark(`${componentName}-start`);
    },
    end: () => {
      performance.mark(`${componentName}-end`);
      performance.measure(
        componentName,
        `${componentName}-start`,
        `${componentName}-end`
      );

      const measure = performance.getEntriesByName(componentName)[0];
      console.log(`${componentName} render time: ${measure.duration}ms`);

      // Clean up
      performance.clearMarks(`${componentName}-start`);
      performance.clearMarks(`${componentName}-end`);
      performance.clearMeasures(componentName);
    },
  };
}

// Usage
export const HeavyComponent: React.FC = () => {
  useEffect(() => {
    const perf = measureRenderTime('HeavyComponent');
    perf.start();

    return () => {
      perf.end();
    };
  });

  return <div>{/* Heavy rendering */}</div>;
};
```

### 3. Web Vitals

```typescript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  console.log(metric);
  // Send to analytics service
}

getCLS(sendToAnalytics); // Cumulative Layout Shift
getFID(sendToAnalytics); // First Input Delay
getFCP(sendToAnalytics); // First Contentful Paint
getLCP(sendToAnalytics); // Largest Contentful Paint
getTTFB(sendToAnalytics); // Time to First Byte
```

## Performance Checklist

### Component Level
- [ ] Use React.memo for expensive components
- [ ] Use useMemo for expensive computations
- [ ] Use useCallback for callbacks passed to children
- [ ] Colocate state close to where it's used
- [ ] Avoid inline object/array creation in JSX
- [ ] Use proper keys in lists
- [ ] Lazy load heavy components
- [ ] Implement virtualization for long lists

### Application Level
- [ ] Code-split by route
- [ ] Lazy load non-critical components
- [ ] Optimize images (size, format, lazy loading)
- [ ] Minimize bundle size
- [ ] Use CDN for static assets
- [ ] Enable compression (gzip/brotli)
- [ ] Cache API responses
- [ ] Debounce/throttle expensive operations

### Monitoring
- [ ] Profile with React DevTools
- [ ] Monitor Web Vitals
- [ ] Set up performance budgets
- [ ] Track bundle size over time
- [ ] Monitor real user metrics (RUM)

## Anti-Patterns to Avoid

### 1. Premature Optimization

```typescript
// ❌ Bad - unnecessary memo for simple component
const SimpleText = React.memo<{ text: string }>(({ text }) => <p>{text}</p>);

// ✅ Good - memo only for expensive components
const ExpensiveChart = React.memo<Props>(({ data }) => {
  // Complex chart rendering
});
```

### 2. Over-Memoization

```typescript
// ❌ Bad - memoizing everything
const Component = () => {
  const value1 = useMemo(() => prop1 + prop2, [prop1, prop2]);
  const value2 = useMemo(() => prop3 * 2, [prop3]);
  const value3 = useMemo(() => `${prop4}`, [prop4]);

  // Memoization overhead > computation cost
};

// ✅ Good - only memoize expensive operations
const Component = () => {
  const value1 = prop1 + prop2; // Simple, no memo needed
  const expensiveValue = useMemo(
    () => complexCalculation(data),
    [data]
  );
};
```

### 3. Unstable Dependencies

```typescript
// ❌ Bad - new object on every render
const Component = () => {
  const config = { option: 'value' };

  const memoizedValue = useMemo(
    () => processData(config), // config changes every render
    [config]
  );
};

// ✅ Good - stable dependencies
const Component = () => {
  const config = useMemo(() => ({ option: 'value' }), []);

  const memoizedValue = useMemo(
    () => processData(config),
    [config]
  );
};
```

## Summary

Performance optimization requires:
1. Understanding when and why components re-render
2. Applying optimizations strategically
3. Measuring impact before and after changes
4. Avoiding premature optimization
5. Monitoring performance in production

---

**Next Steps:**
- [Testing Strategies](./testing-strategies.md) - Test performance optimizations
- [Component Architecture](./component-architecture.md) - Build performant architectures
