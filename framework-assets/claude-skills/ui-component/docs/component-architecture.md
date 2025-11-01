# Component Architecture Guide

## Introduction

This guide covers advanced component architecture patterns, composition strategies, and design principles for building scalable, maintainable React component libraries.

## Architectural Principles

### 1. Component Hierarchy

#### Atomic Design Methodology

**Atoms** - Basic building blocks
```typescript
// Button, Input, Label, Icon
export const Button: React.FC<ButtonProps> = ({ children, ...props }) => (
  <button {...props}>{children}</button>
);
```

**Molecules** - Groups of atoms
```typescript
// FormField (Label + Input + Error)
export const FormField: React.FC<FormFieldProps> = ({
  label,
  error,
  children,
}) => (
  <div className={styles.formField}>
    <Label>{label}</Label>
    {children}
    {error && <ErrorText>{error}</ErrorText>}
  </div>
);
```

**Organisms** - Complex components
```typescript
// LoginForm (Multiple FormFields + Button)
export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit }) => (
  <form onSubmit={onSubmit}>
    <FormField label="Email" error={emailError}>
      <Input type="email" name="email" />
    </FormField>
    <FormField label="Password" error={passwordError}>
      <Input type="password" name="password" />
    </FormField>
    <Button type="submit">Login</Button>
  </form>
);
```

**Templates** - Page layouts
```typescript
// AuthTemplate (Header + Content + Footer)
export const AuthTemplate: React.FC<AuthTemplateProps> = ({ children }) => (
  <div className={styles.authTemplate}>
    <Header />
    <main className={styles.content}>{children}</main>
    <Footer />
  </div>
);
```

**Pages** - Specific instances
```typescript
// LoginPage (AuthTemplate + LoginForm)
export const LoginPage: React.FC = () => (
  <AuthTemplate>
    <LoginForm onSubmit={handleLogin} />
  </AuthTemplate>
);
```

### 2. Component Composition Patterns

#### Compound Components Pattern

Best for: Components with related sub-components that share state.

```typescript
// Select.tsx
interface SelectContextValue {
  value: string;
  onChange: (value: string) => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

const SelectContext = React.createContext<SelectContextValue | undefined>(
  undefined
);

export const Select: React.FC<SelectProps> & {
  Trigger: typeof Trigger;
  Options: typeof Options;
  Option: typeof Option;
} = ({ children, value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const contextValue: SelectContextValue = {
    value,
    onChange,
    isOpen,
    setIsOpen,
  };

  return (
    <SelectContext.Provider value={contextValue}>
      <div className={styles.select}>{children}</div>
    </SelectContext.Provider>
  );
};

const Trigger: React.FC<{ children: ReactNode }> = ({ children }) => {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Trigger must be used within Select');

  return (
    <button
      type="button"
      onClick={() => context.setIsOpen(!context.isOpen)}
      aria-haspopup="listbox"
      aria-expanded={context.isOpen}
    >
      {children}
    </button>
  );
};

const Options: React.FC<{ children: ReactNode }> = ({ children }) => {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Options must be used within Select');

  if (!context.isOpen) return null;

  return (
    <ul role="listbox" className={styles.options}>
      {children}
    </ul>
  );
};

const Option: React.FC<OptionProps> = ({ value, children }) => {
  const context = useContext(SelectContext);
  if (!context) throw new Error('Option must be used within Select');

  const isSelected = context.value === value;

  return (
    <li
      role="option"
      aria-selected={isSelected}
      onClick={() => {
        context.onChange(value);
        context.setIsOpen(false);
      }}
      className={isSelected ? styles.selected : undefined}
    >
      {children}
    </li>
  );
};

Select.Trigger = Trigger;
Select.Options = Options;
Select.Option = Option;

// Usage
<Select value={selected} onChange={setSelected}>
  <Select.Trigger>Choose option</Select.Trigger>
  <Select.Options>
    <Select.Option value="1">Option 1</Select.Option>
    <Select.Option value="2">Option 2</Select.Option>
  </Select.Options>
</Select>
```

#### Render Props Pattern

Best for: Sharing logic while giving consumers rendering control.

```typescript
interface RenderPropsProps<T> {
  data: T[];
  children: (props: {
    data: T[];
    loading: boolean;
    error: Error | null;
  }) => ReactNode;
}

export function DataProvider<T>({ data, children }: RenderPropsProps<T>) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  return <>{children({ data, loading, error })}</>;
}

// Usage
<DataProvider data={users}>
  {({ data, loading, error }) => {
    if (loading) return <Spinner />;
    if (error) return <ErrorMessage error={error} />;
    return <UserList users={data} />;
  }}
</DataProvider>
```

#### Custom Hooks Pattern

Best for: Extracting reusable stateful logic.

```typescript
// useToggle.ts
export function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => {
    setValue((v) => !v);
  }, []);

  const setTrue = useCallback(() => {
    setValue(true);
  }, []);

  const setFalse = useCallback(() => {
    setValue(false);
  }, []);

  return {
    value,
    toggle,
    setTrue,
    setFalse,
    setValue,
  };
}

// useDisclosure.ts
export function useDisclosure(initialOpen = false) {
  const { value: isOpen, setTrue: onOpen, setFalse: onClose } = useToggle(
    initialOpen
  );

  return { isOpen, onOpen, onClose };
}

// Usage in component
const { isOpen, onOpen, onClose } = useDisclosure();

return (
  <>
    <Button onClick={onOpen}>Open Modal</Button>
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalContent />
    </Modal>
  </>
);
```

#### Polymorphic Components Pattern

Best for: Components that can render as different HTML elements.

```typescript
// Polymorphic component type definition
type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

type PolymorphicComponentProp<
  C extends React.ElementType,
  Props = {}
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

// Box component implementation
type BoxProps<C extends React.ElementType> = PolymorphicComponentProp<
  C,
  {
    className?: string;
    padding?: 'sm' | 'md' | 'lg';
  }
>;

export const Box = <C extends React.ElementType = 'div'>({
  as,
  children,
  className,
  padding,
  ...rest
}: BoxProps<C>) => {
  const Component = as || 'div';

  const classes = [
    styles.box,
    padding && styles[`padding-${padding}`],
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <Component className={classes} {...rest}>
      {children}
    </Component>
  );
};

// Usage - renders as different elements with full type safety
<Box>Default div</Box>
<Box as="section">Section element</Box>
<Box as="button" onClick={handleClick}>Button element</Box>
<Box as={Link} to="/home">Link component</Box>
```

### 3. State Management Architecture

#### Local State Strategy

```typescript
// Simple component state
export const Counter: React.FC = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <Button onClick={() => setCount((c) => c + 1)}>Increment</Button>
    </div>
  );
};
```

#### Lifted State Strategy

```typescript
// State lifted to parent component
export const TodoApp: React.FC = () => {
  const [todos, setTodos] = useState<Todo[]>([]);

  const addTodo = (text: string) => {
    setTodos([...todos, { id: Date.now(), text, completed: false }]);
  };

  const toggleTodo = (id: number) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <TodoList todos={todos} onToggle={toggleTodo} />
    </div>
  );
};
```

#### Context-Based State

```typescript
// Theme context example
interface ThemeContextValue {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === 'light' ? 'dark' : 'light'));
  }, []);

  const value = useMemo(
    () => ({ theme, toggleTheme }),
    [theme, toggleTheme]
  );

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Usage
const ThemedButton: React.FC = () => {
  const { theme } = useTheme();
  return <Button className={styles[theme]}>Themed Button</Button>;
};
```

#### Reducer-Based State

```typescript
// Complex state management with useReducer
type TodoState = {
  todos: Todo[];
  filter: 'all' | 'active' | 'completed';
};

type TodoAction =
  | { type: 'ADD_TODO'; text: string }
  | { type: 'TOGGLE_TODO'; id: number }
  | { type: 'DELETE_TODO'; id: number }
  | { type: 'SET_FILTER'; filter: TodoState['filter'] };

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: Date.now(), text: action.text, completed: false },
        ],
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };
    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter((todo) => todo.id !== action.id),
      };
    case 'SET_FILTER':
      return { ...state, filter: action.filter };
    default:
      return state;
  }
}

export const TodoApp: React.FC = () => {
  const [state, dispatch] = useReducer(todoReducer, {
    todos: [],
    filter: 'all',
  });

  const filteredTodos = useMemo(() => {
    switch (state.filter) {
      case 'active':
        return state.todos.filter((t) => !t.completed);
      case 'completed':
        return state.todos.filter((t) => t.completed);
      default:
        return state.todos;
    }
  }, [state.todos, state.filter]);

  return (
    <div>
      <TodoInput onAdd={(text) => dispatch({ type: 'ADD_TODO', text })} />
      <TodoFilters
        filter={state.filter}
        onFilterChange={(filter) => dispatch({ type: 'SET_FILTER', filter })}
      />
      <TodoList
        todos={filteredTodos}
        onToggle={(id) => dispatch({ type: 'TOGGLE_TODO', id })}
        onDelete={(id) => dispatch({ type: 'DELETE_TODO', id })}
      />
    </div>
  );
};
```

### 4. Component Communication Patterns

#### Props Drilling (Avoid when deep)

```typescript
// Problematic - props drilling through multiple levels
<GrandParent data={data}>
  <Parent data={data}>
    <Child data={data} />
  </Parent>
</GrandParent>
```

#### Context for Deep Hierarchies

```typescript
// Solution - use context for deeply nested data
const DataContext = createContext<Data | undefined>(undefined);

<DataContext.Provider value={data}>
  <GrandParent>
    <Parent>
      <Child />
    </Parent>
  </GrandParent>
</DataContext.Provider>

// Child accesses data directly
const Child: React.FC = () => {
  const data = useContext(DataContext);
  return <div>{data?.value}</div>;
};
```

#### Event Bubbling Pattern

```typescript
// Parent handles events from children
export const Form: React.FC = () => {
  const handleFormEvent = (event: React.FormEvent) => {
    // Handle all form events in one place
    const target = event.target as HTMLElement;
    console.log('Event from:', target.name);
  };

  return (
    <form onChange={handleFormEvent} onSubmit={handleFormEvent}>
      <Input name="email" />
      <Input name="password" />
      <Button type="submit">Submit</Button>
    </form>
  );
};
```

### 5. Performance Architecture

#### Memoization Strategy

```typescript
// Memo expensive calculations
const ExpensiveComponent: React.FC<Props> = ({ data, filter }) => {
  const processedData = useMemo(() => {
    return data.filter(filter).map(transform);
  }, [data, filter]);

  return <DataDisplay data={processedData} />;
};

// Memo callback functions
const Parent: React.FC = () => {
  const handleClick = useCallback((id: number) => {
    console.log('Clicked:', id);
  }, []);

  return <Child onClick={handleClick} />;
};

// Memo entire component
export const Child = React.memo<ChildProps>(
  ({ onClick }) => {
    return <button onClick={() => onClick(1)}>Click</button>;
  },
  (prevProps, nextProps) => {
    // Custom comparison function
    return prevProps.onClick === nextProps.onClick;
  }
);
```

#### Code Splitting Strategy

```typescript
// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));
const AdminPanel = lazy(() => import('./AdminPanel'));

export const Dashboard: React.FC = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <HeavyChart data={chartData} />
    </Suspense>
  );
};

// Route-based code splitting
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard')),
  },
  {
    path: '/admin',
    component: lazy(() => import('./pages/Admin')),
  },
];
```

#### Virtual Scrolling for Large Lists

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

export const VirtualList: React.FC<{ items: Item[] }> = ({ items }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
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
```

## Design System Integration

### Component Token System

```typescript
// tokens.ts
export const tokens = {
  colors: {
    primary: {
      50: '#e6f2ff',
      100: '#b3d9ff',
      500: '#0066cc',
      900: '#003d7a',
    },
    neutral: {
      50: '#f8f9fa',
      500: '#6c757d',
      900: '#212529',
    },
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  typography: {
    fontFamily: {
      sans: 'Inter, system-ui, sans-serif',
      mono: 'Monaco, monospace',
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
    },
  },
  radii: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '1rem',
    full: '9999px',
  },
};

// Use in components
const Button = styled.button<{ variant: 'primary' | 'secondary' }>`
  background-color: ${({ variant }) =>
    variant === 'primary' ? tokens.colors.primary[500] : tokens.colors.neutral[500]};
  padding: ${tokens.spacing.md} ${tokens.spacing.lg};
  border-radius: ${tokens.radii.md};
  font-family: ${tokens.typography.fontFamily.sans};
`;
```

## Best Practices

### Component Architecture Checklist

- [ ] Components follow single responsibility principle
- [ ] Clear separation of concerns (UI vs logic)
- [ ] Proper composition over inheritance
- [ ] State is managed at appropriate level
- [ ] Performance optimizations applied where needed
- [ ] Components are properly typed
- [ ] Accessibility is built-in
- [ ] Error boundaries implemented for error handling
- [ ] Components are testable
- [ ] Documentation is comprehensive

### When to Extract a Component

Extract when:
- Code is reused in multiple places
- Component has clear, single purpose
- Reducing parent component complexity
- Creating a design system element
- Enabling independent testing
- Improving code organization

Don't extract when:
- Used only once with no reuse potential
- Extraction increases complexity
- Component is tightly coupled to parent
- Premature optimization

## Summary

Effective component architecture requires:
1. Understanding composition patterns
2. Choosing appropriate state management
3. Optimizing performance strategically
4. Building with accessibility in mind
5. Creating maintainable, testable code

---

**Next Steps:**
- [TypeScript Patterns](./typescript-patterns.md) - Advanced typing strategies
- [Styling Guide](./styling-guide.md) - CSS architecture and patterns
- [Testing Strategies](./testing-strategies.md) - Comprehensive testing approaches
