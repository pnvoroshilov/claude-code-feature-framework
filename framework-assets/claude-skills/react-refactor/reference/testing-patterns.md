# React Testing Patterns

**Comprehensive guide to testing React components and hooks with React Testing Library, Jest, and MSW.**

## Testing Philosophy

testing_principles[5]{principle,explanation,example}:
Test behavior not implementation,Test what users see and do,Query by text not by class names
Avoid testing implementation details,Don't test state or props directly,Test rendered output and interactions
Write tests users would perform,Simulate real user interactions,Click buttons type in inputs
Use accessibility queries,Query by role label text,screen.getByRole('button')
Mock external dependencies,Mock API calls and services,Use MSW for API mocking

## Pattern 1: Component Testing

### Basic Component Test

```typescript
// src/presentation/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button');
    await userEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Testing Component with Props

```typescript
// src/presentation/components/UserCard.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserCard } from './UserCard';
import { User } from '@/domain/entities/User';

describe('UserCard', () => {
  const mockUser: User = {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    status: 'ACTIVE',
    createdAt: new Date(),
  };

  it('displays user information', () => {
    render(<UserCard user={mockUser} onSelect={jest.fn()} />);

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onSelect with user id when clicked', async () => {
    const handleSelect = jest.fn();
    render(<UserCard user={mockUser} onSelect={handleSelect} />);

    await userEvent.click(screen.getByText('John Doe'));

    expect(handleSelect).toHaveBeenCalledWith('1');
  });
});
```

### Testing Forms

```typescript
// src/presentation/components/LoginForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('submits form with email and password', async () => {
    const handleSubmit = jest.fn();
    render(<LoginForm onSubmit={handleSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows validation error for invalid email', async () => {
    render(<LoginForm onSubmit={jest.fn()} />);

    const emailInput = screen.getByLabelText(/email/i);
    await userEvent.type(emailInput, 'invalid-email');
    await userEvent.tab(); // Blur input

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

## Pattern 2: Hook Testing

### Testing Custom Hooks

```typescript
// src/application/hooks/useToggle.test.ts
import { renderHook, act } from '@testing-library/react';
import { useToggle } from './useToggle';

describe('useToggle', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useToggle());
    expect(result.current.isOn).toBe(false);
  });

  it('initializes with provided value', () => {
    const { result } = renderHook(() => useToggle(true));
    expect(result.current.isOn).toBe(true);
  });

  it('toggles value', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isOn).toBe(true);

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isOn).toBe(false);
  });

  it('sets value to true', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current.setOn();
    });

    expect(result.current.isOn).toBe(true);
  });

  it('sets value to false', () => {
    const { result } = renderHook(() => useToggle(true));

    act(() => {
      result.current.setOff();
    });

    expect(result.current.isOn).toBe(false);
  });
});
```

### Testing Async Hooks

```typescript
// src/application/hooks/useUser.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useUser } from './useUser';
import { IUserRepository } from '@/application/ports/IUserRepository';
import { User } from '@/domain/entities/User';

describe('useUser', () => {
  const mockUser: User = {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    status: 'ACTIVE',
    createdAt: new Date(),
  };

  it('fetches user on mount', async () => {
    const mockRepository: IUserRepository = {
      findById: jest.fn().mockResolvedValue(mockUser),
      findByEmail: jest.fn(),
      findAll: jest.fn(),
      save: jest.fn(),
      delete: jest.fn(),
    };

    const { result } = renderHook(() => useUser('1', mockRepository));

    expect(result.current.loading).toBe(true);
    expect(result.current.user).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.error).toBeNull();
    expect(mockRepository.findById).toHaveBeenCalledWith('1');
  });

  it('handles error', async () => {
    const error = new Error('Failed to fetch');
    const mockRepository: IUserRepository = {
      findById: jest.fn().mockRejectedValue(error),
      findByEmail: jest.fn(),
      findAll: jest.fn(),
      save: jest.fn(),
      delete: jest.fn(),
    };

    const { result } = renderHook(() => useUser('1', mockRepository));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.error).toEqual(error);
  });
});
```

## Pattern 3: Testing with Context

### Creating Test Wrapper

```typescript
// src/test/utils/test-utils.tsx
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/application/stores/AuthContext';
import { mockAuthService } from '../mocks/authService';

interface AllProvidersProps {
  children: React.ReactNode;
}

function AllProviders({ children }: AllProvidersProps) {
  return (
    <BrowserRouter>
      <AuthProvider authService={mockAuthService}>
        {children}
      </AuthProvider>
    </BrowserRouter>
  );
}

function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllProviders, ...options });
}

export * from '@testing-library/react';
export { customRender as render };
```

### Using Custom Render

```typescript
// src/presentation/components/ProtectedRoute.test.tsx
import { screen } from '@testing-library/react';
import { render } from '@/test/utils/test-utils';
import { ProtectedRoute } from './ProtectedRoute';

describe('ProtectedRoute', () => {
  it('renders children when authenticated', () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
```

## Pattern 4: API Mocking with MSW

### Setting up MSW

```typescript
// src/test/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);

// src/test/mocks/handlers.ts
import { rest } from 'msw';
import { User } from '@/domain/entities/User';

export const handlers = [
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    return res(
      ctx.json<User>({
        id: id as string,
        name: 'John Doe',
        email: 'john@example.com',
        status: 'ACTIVE',
        createdAt: new Date().toISOString(),
      })
    );
  }),

  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json<User[]>([
        {
          id: '1',
          name: 'John Doe',
          email: 'john@example.com',
          status: 'ACTIVE',
          createdAt: new Date().toISOString(),
        },
      ])
    );
  }),

  rest.post('/api/users', async (req, res, ctx) => {
    const user = await req.json<Omit<User, 'id'>>();
    return res(
      ctx.json<User>({
        ...user,
        id: '123',
      })
    );
  }),
];

// src/test/setup.ts
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Testing with MSW

```typescript
// src/presentation/components/UserList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { UserList } from './UserList';
import { server } from '@/test/mocks/server';
import { rest } from 'msw';

describe('UserList', () => {
  it('fetches and displays users', async () => {
    render(<UserList />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('handles error', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
```

## Pattern 5: Testing React Query

### Testing with React Query

```typescript
// src/test/utils/query-test-utils.tsx
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
      },
    },
  });
}

interface QueryWrapperProps {
  children: React.ReactNode;
}

function QueryWrapper({ children }: QueryWrapperProps) {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

function renderWithQuery(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: QueryWrapper, ...options });
}

export { renderWithQuery };
```

### Testing Query Component

```typescript
// src/presentation/components/UserProfile.test.tsx
import { screen, waitFor } from '@testing-library/react';
import { renderWithQuery } from '@/test/utils/query-test-utils';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('fetches and displays user', async () => {
    renderWithQuery(<UserProfile userId="1" />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });
});
```

## Testing Best Practices

testing_best_practices[10]{practice,explanation,example}:
Use accessibility queries,Query by role label text,screen.getByRole('button')
Avoid test IDs,Use semantic queries,screen.getByText not data-testid
Test user behavior,Test what users do,Click type not state changes
Mock external dependencies,Mock APIs and services,Use MSW for HTTP mocking
Use userEvent,Simulates real user interactions,userEvent.click not fireEvent
Wait for async operations,Use waitFor findBy,await screen.findByText
Don't test implementation,Test behavior not internals,Don't check state directly
Isolate tests,Each test independent,Reset mocks between tests
Descriptive test names,Name describes behavior,it('calls onSubmit when form is valid')
Arrange Act Assert,Clear test structure,Setup → Execute → Verify

## Testing Anti-Patterns

testing_antipatterns[8]{antipattern,problem,solution}:
Using data-testid everywhere,Not testing accessibility,Use semantic queries (role label text)
Testing implementation details,Brittle tests,Test behavior and output
Not waiting for async,Intermittent failures,Use waitFor and findBy queries
Using fireEvent,Doesn't simulate real interactions,Use userEvent from @testing-library/user-event
Mocking too much,Not testing real behavior,Only mock external dependencies
Not testing error states,Incomplete coverage,Test loading error and success states
Large snapshots,Hard to review and maintain,Test specific elements not whole tree
Testing library internals,Coupled to implementation,Test public API and behavior

## Testing Checklist

testing_checklist[12]{check,requirement}:
Query accessibility,Use getByRole getByLabelText getByText,
Test user interactions,Click type submit forms
Mock API calls,Use MSW for HTTP mocking
Test error states,Loading error success states covered
Test edge cases,Empty states no data error conditions
Async operations handled,Use waitFor and findBy
Custom hooks tested,Use renderHook from RTL
Integration tests,Test components with context and routing
Avoid test IDs,Use semantic queries
User event library,Use userEvent not fireEvent
Descriptive test names,Clear behavior descriptions
Independent tests,Each test can run in isolation

---

**File Size**: 440/500 lines max ✅
