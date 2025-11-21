# TypeScript Patterns for React Components

## Introduction

This guide covers advanced TypeScript patterns specifically for React component development, including strict typing, generic components, utility types, and type-safe patterns.

## Core Type Patterns

### 1. Props Interface Design

#### Basic Props Interface

```typescript
// Basic interface with required and optional props
interface ButtonProps {
  // Required props - no ?
  children: React.ReactNode;
  onClick: () => void;

  // Optional props - with ?
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  className?: string;
}

// With default values in implementation
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  disabled = false,
  className = '',
  children,
  onClick,
}) => {
  // Implementation
};
```

#### Extending HTML Element Props

```typescript
// Extend native button props
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

// Now button receives all native button attributes
const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  ...nativeProps // onClick, disabled, type, etc.
}) => {
  return (
    <button {...nativeProps} className={getClassName(variant, size)}>
      {children}
    </button>
  );
};

// Usage with full type safety
<Button
  variant="primary"
  onClick={handleClick}
  disabled={isLoading}
  aria-label="Submit form"
  type="submit"
/>
```

#### Discriminated Union Types

```typescript
// Button with different behaviors based on type
type ButtonProps =
  | {
      variant: 'link';
      href: string;
      target?: '_blank' | '_self';
      onClick?: never; // Cannot have onClick when variant is link
    }
  | {
      variant: 'button';
      onClick: () => void;
      href?: never; // Cannot have href when variant is button
      target?: never;
    };

const Button: React.FC<ButtonProps> = (props) => {
  if (props.variant === 'link') {
    // TypeScript knows props has href and target
    return (
      <a href={props.href} target={props.target}>
        {props.children}
      </a>
    );
  }

  // TypeScript knows props has onClick
  return <button onClick={props.onClick}>{props.children}</button>;
};

// Type-safe usage
<Button variant="link" href="/home" />           // ✅ Valid
<Button variant="button" onClick={handleClick} /> // ✅ Valid
<Button variant="link" onClick={handleClick} />   // ❌ Type error
<Button variant="button" href="/home" />          // ❌ Type error
```

### 2. Generic Components

#### Generic List Component

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T) => string | number;
  emptyMessage?: string;
}

// Generic component that works with any type
export function List<T>({
  items,
  renderItem,
  keyExtractor,
  emptyMessage = 'No items',
}: ListProps<T>) {
  if (items.length === 0) {
    return <div className={styles.empty}>{emptyMessage}</div>;
  }

  return (
    <ul className={styles.list}>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  );
}

// Usage with type inference
interface User {
  id: number;
  name: string;
  email: string;
}

<List<User>
  items={users}
  keyExtractor={(user) => user.id}
  renderItem={(user) => (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )}
/>
```

#### Generic Form Field

```typescript
interface FormFieldProps<T> {
  value: T;
  onChange: (value: T) => void;
  validate?: (value: T) => string | undefined;
  label: string;
  name: string;
}

export function FormField<T extends string | number>({
  value,
  onChange,
  validate,
  label,
  name,
}: FormFieldProps<T>) {
  const [error, setError] = useState<string>();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value as T;
    onChange(newValue);

    if (validate) {
      const validationError = validate(newValue);
      setError(validationError);
    }
  };

  return (
    <div className={styles.formField}>
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        value={value}
        onChange={handleChange}
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : undefined}
      />
      {error && (
        <span id={`${name}-error`} className={styles.error}>
          {error}
        </span>
      )}
    </div>
  );
}
```

#### Generic Data Table

```typescript
interface Column<T> {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], item: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string | number;
  onRowClick?: (item: T) => void;
}

export function DataTable<T>({
  data,
  columns,
  keyExtractor,
  onRowClick,
}: DataTableProps<T>) {
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={String(column.key)}>{column.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr
            key={keyExtractor(item)}
            onClick={() => onRowClick?.(item)}
            className={onRowClick ? styles.clickable : undefined}
          >
            {columns.map((column) => (
              <td key={String(column.key)}>
                {column.render
                  ? column.render(item[column.key], item)
                  : String(item[column.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Usage
interface Product {
  id: number;
  name: string;
  price: number;
  inStock: boolean;
}

<DataTable<Product>
  data={products}
  keyExtractor={(p) => p.id}
  columns={[
    { key: 'name', header: 'Product Name' },
    {
      key: 'price',
      header: 'Price',
      render: (price) => `$${price.toFixed(2)}`,
    },
    {
      key: 'inStock',
      header: 'Status',
      render: (inStock) => (inStock ? '✓' : '✗'),
    },
  ]}
  onRowClick={(product) => console.log(product)}
/>
```

### 3. Polymorphic Component Types

#### As Prop Pattern

```typescript
type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsToOmit<C extends React.ElementType, P> = keyof (AsProp<C> & P);

// Polymorphic component props that merge with element props
type PolymorphicComponentProp<
  C extends React.ElementType,
  Props = {}
> = React.PropsWithChildren<Props & AsProp<C>> &
  Omit<React.ComponentPropsWithoutRef<C>, PropsToOmit<C, Props>>;

// Polymorphic ref type
type PolymorphicRef<C extends React.ElementType> =
  React.ComponentPropsWithRef<C>['ref'];

type PolymorphicComponentPropWithRef<
  C extends React.ElementType,
  Props = {}
> = PolymorphicComponentProp<C, Props> & { ref?: PolymorphicRef<C> };

// Implementation
type TextProps<C extends React.ElementType> = PolymorphicComponentPropWithRef<
  C,
  {
    color?: 'primary' | 'secondary' | 'error';
    size?: 'sm' | 'md' | 'lg';
  }
>;

type TextComponent = <C extends React.ElementType = 'span'>(
  props: TextProps<C>
) => React.ReactElement | null;

export const Text: TextComponent = React.forwardRef(
  <C extends React.ElementType = 'span'>(
    { as, color, size, children, ...rest }: TextProps<C>,
    ref?: PolymorphicRef<C>
  ) => {
    const Component = as || 'span';

    return (
      <Component
        ref={ref}
        className={getClassName(color, size)}
        {...rest}
      >
        {children}
      </Component>
    );
  }
);

// Usage with full type safety
<Text>Default span</Text>
<Text as="p">Paragraph</Text>
<Text as="h1" color="primary">Heading</Text>
<Text as="a" href="/home" target="_blank">Link</Text>
<Text as={Link} to="/home">React Router Link</Text>
```

### 4. Advanced Hook Patterns

#### Typed Custom Hooks

```typescript
// useLocalStorage hook with full type safety
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue];
}

// Usage
const [user, setUser] = useLocalStorage<User>('user', { name: '', email: '' });
```

#### Typed useReducer

```typescript
// State type
type TodoState = {
  todos: Todo[];
  filter: 'all' | 'active' | 'completed';
  loading: boolean;
};

// Action types with discriminated unions
type TodoAction =
  | { type: 'ADD_TODO'; payload: { text: string } }
  | { type: 'TOGGLE_TODO'; payload: { id: number } }
  | { type: 'DELETE_TODO'; payload: { id: number } }
  | { type: 'SET_FILTER'; payload: { filter: TodoState['filter'] } }
  | { type: 'SET_LOADING'; payload: { loading: boolean } };

// Reducer with type safety
function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case 'ADD_TODO':
      return {
        ...state,
        todos: [
          ...state.todos,
          {
            id: Date.now(),
            text: action.payload.text,
            completed: false,
          },
        ],
      };
    case 'TOGGLE_TODO':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.payload.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      };
    case 'DELETE_TODO':
      return {
        ...state,
        todos: state.todos.filter((todo) => todo.id !== action.payload.id),
      };
    case 'SET_FILTER':
      return {
        ...state,
        filter: action.payload.filter,
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload.loading,
      };
    default:
      // TypeScript ensures all cases are handled
      const _exhaustiveCheck: never = action;
      return state;
  }
}

// Action creators for type safety
const todoActions = {
  addTodo: (text: string): TodoAction => ({
    type: 'ADD_TODO',
    payload: { text },
  }),
  toggleTodo: (id: number): TodoAction => ({
    type: 'TOGGLE_TODO',
    payload: { id },
  }),
  deleteTodo: (id: number): TodoAction => ({
    type: 'DELETE_TODO',
    payload: { id },
  }),
  setFilter: (filter: TodoState['filter']): TodoAction => ({
    type: 'SET_FILTER',
    payload: { filter },
  }),
  setLoading: (loading: boolean): TodoAction => ({
    type: 'SET_LOADING',
    payload: { loading },
  }),
};

// Usage in component
const [state, dispatch] = useReducer(todoReducer, {
  todos: [],
  filter: 'all',
  loading: false,
});

// Type-safe dispatch
dispatch(todoActions.addTodo('Buy groceries'));
dispatch(todoActions.toggleTodo(1));
```

### 5. Utility Types for Components

#### Common Utility Types

```typescript
// Extract prop types from component
type ButtonProps = React.ComponentProps<typeof Button>;

// Extract element ref type
type ButtonRef = React.ElementRef<typeof Button>;

// Make all props optional
type PartialButtonProps = Partial<ButtonProps>;

// Make all props required
type RequiredButtonProps = Required<ButtonProps>;

// Pick specific props
type ButtonVariantProps = Pick<ButtonProps, 'variant' | 'size'>;

// Omit specific props
type ButtonWithoutCallbacks = Omit<ButtonProps, 'onClick' | 'onFocus'>;

// Readonly props (for immutable data)
type ReadonlyButtonProps = Readonly<ButtonProps>;
```

#### Custom Utility Types

```typescript
// Make specific props required
type RequireProps<T, K extends keyof T> = T & Required<Pick<T, K>>;

interface FormProps {
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
}

// Make value and onChange required
type ControlledFormProps = RequireProps<FormProps, 'value' | 'onChange'>;

// Make specific props optional
type OptionalProps<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Exclude null and undefined
type NonNullableProps<T> = {
  [K in keyof T]: NonNullable<T[K]>;
};

// Deep partial (all nested props optional)
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};
```

### 6. Event Handler Types

#### Typed Event Handlers

```typescript
interface FormProps {
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onFocus: (event: React.FocusEvent<HTMLInputElement>) => void;
  onKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

// Generic event handler type
type EventHandler<T extends HTMLElement, E extends React.SyntheticEvent> = (
  event: E & { currentTarget: T }
) => void;

// Usage
const handleClick: EventHandler<HTMLButtonElement, React.MouseEvent> = (
  event
) => {
  // event.currentTarget is typed as HTMLButtonElement
  console.log(event.currentTarget.name);
};
```

#### Custom Event Types

```typescript
// Custom event with data
interface SelectChangeEvent {
  value: string;
  name: string;
  originalEvent: React.ChangeEvent<HTMLSelectElement>;
}

interface SelectProps {
  name: string;
  value: string;
  onChange: (event: SelectChangeEvent) => void;
}

export const Select: React.FC<SelectProps> = ({ name, value, onChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange({
      value: e.target.value,
      name,
      originalEvent: e,
    });
  };

  return <select name={name} value={value} onChange={handleChange} />;
};
```

### 7. Ref Types

#### Forwarding Refs

```typescript
interface InputProps {
  label: string;
  error?: string;
}

// Component with forwarded ref
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, ...props }, ref) => {
    return (
      <div className={styles.inputWrapper}>
        <label>{label}</label>
        <input ref={ref} aria-invalid={!!error} {...props} />
        {error && <span className={styles.error}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Usage
const inputRef = useRef<HTMLInputElement>(null);
<Input ref={inputRef} label="Email" />
```

#### useImperativeHandle Type

```typescript
// Expose custom ref handle
interface ModalRef {
  open: () => void;
  close: () => void;
  toggle: () => void;
}

interface ModalProps {
  children: React.ReactNode;
}

export const Modal = React.forwardRef<ModalRef, ModalProps>(
  ({ children }, ref) => {
    const [isOpen, setIsOpen] = useState(false);

    useImperativeHandle(ref, () => ({
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
      toggle: () => setIsOpen((prev) => !prev),
    }));

    if (!isOpen) return null;

    return <div className={styles.modal}>{children}</div>;
  }
);

// Usage
const modalRef = useRef<ModalRef>(null);

<Modal ref={modalRef}>
  <p>Modal content</p>
</Modal>

<Button onClick={() => modalRef.current?.open()}>Open Modal</Button>
```

### 8. Context Types

#### Typed Context

```typescript
// Define context value type
interface AuthContextValue {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Create context with undefined default (requires provider)
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const user = await authService.login(email, password);
      setUser(user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Typed hook
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Usage
const { user, login, logout, isAuthenticated } = useAuth();
```

## Best Practices

### TypeScript Configuration for React

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Type Safety Checklist

- [ ] All props interfaces are explicitly typed
- [ ] No `any` types used (use `unknown` if needed)
- [ ] Event handlers have correct event types
- [ ] Refs are properly typed
- [ ] Generic components have type constraints
- [ ] Context has type-safe hooks
- [ ] Discriminated unions for complex props
- [ ] Utility types used appropriately

## Common Patterns Summary

1. **Props**: Use discriminated unions for mutually exclusive props
2. **Generics**: Make components reusable with type parameters
3. **Polymorphic**: Allow components to render as different elements
4. **Refs**: Forward refs with proper typing
5. **Hooks**: Type custom hooks for reusable logic
6. **Context**: Create type-safe context providers and hooks
7. **Events**: Use specific event types, not generic ones
8. **Utilities**: Leverage TypeScript utility types

---

**Next Steps:**
- [Styling Guide](./styling-guide.md) - CSS and styling patterns
- [Accessibility Standards](./accessibility-standards.md) - A11y implementation
- [Testing Strategies](./testing-strategies.md) - Testing TypeScript components
