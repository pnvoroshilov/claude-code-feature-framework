# Testing Strategies for React Components

## Introduction

This guide covers comprehensive testing approaches for React components, including unit tests, integration tests, accessibility tests, visual regression tests, and E2E tests.

## Testing Philosophy

### Testing Pyramid

```
        /\
       /  \  E2E Tests (Few)
      /    \
     /------\ Integration Tests (Some)
    /        \
   /----------\ Unit Tests (Many)
  /__Component_\
```

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

### Testing Principles

1. **Test behavior, not implementation**
2. **Test from the user's perspective**
3. **Write maintainable tests**
4. **Aim for high confidence, not 100% coverage**
5. **Make tests readable and self-documenting**

## Unit Testing with Jest + React Testing Library

### Basic Component Test

```typescript
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    screen.getByRole('button').click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Testing Component Variants

```typescript
describe('Button variants', () => {
  it.each([
    ['primary', 'primary'],
    ['secondary', 'secondary'],
    ['outline', 'outline'],
  ])('renders %s variant correctly', (variant, expectedClass) => {
    const { container } = render(<Button variant={variant as any}>Test</Button>);
    expect(container.firstChild).toHaveClass(expectedClass);
  });
});

// Or using test.each with objects
describe('Button sizes', () => {
  test.each([
    { size: 'sm', expectedHeight: 32 },
    { size: 'md', expectedHeight: 40 },
    { size: 'lg', expectedHeight: 48 },
  ])('applies correct height for $size size', ({ size, expectedHeight }) => {
    const { container } = render(<Button size={size as any}>Test</Button>);
    const button = container.firstChild as HTMLElement;
    expect(button.style.minHeight).toBe(`${expectedHeight}px`);
  });
});
```

### Testing User Interactions

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from './Input';

describe('Input interactions', () => {
  it('calls onChange when user types', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();

    render(<Input onChange={handleChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'Hello');

    expect(handleChange).toHaveBeenCalledTimes(5); // Once per character
    expect(input).toHaveValue('Hello');
  });

  it('clears input when clear button is clicked', async () => {
    const user = userEvent.setup();

    render(<Input defaultValue="Test" />);

    const input = screen.getByRole('textbox');
    const clearButton = screen.getByRole('button', { name: /clear/i });

    await user.click(clearButton);

    expect(input).toHaveValue('');
  });

  it('shows error message when validation fails', async () => {
    const user = userEvent.setup();
    const validate = (value: string) =>
      value.length < 3 ? 'Minimum 3 characters' : undefined;

    render(<Input validate={validate} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'ab');
    await user.tab(); // Trigger onBlur

    expect(screen.getByText('Minimum 3 characters')).toBeInTheDocument();
  });
});
```

### Testing Async Behavior

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchableSelect } from './SearchableSelect';

describe('SearchableSelect async behavior', () => {
  it('loads and displays search results', async () => {
    const user = userEvent.setup();
    const mockSearch = jest.fn().mockResolvedValue([
      { id: 1, label: 'Result 1' },
      { id: 2, label: 'Result 2' },
    ]);

    render(<SearchableSelect onSearch={mockSearch} />);

    const input = screen.getByRole('combobox');
    await user.type(input, 'test query');

    // Wait for debounced search
    await waitFor(() => {
      expect(mockSearch).toHaveBeenCalledWith('test query');
    });

    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText('Result 1')).toBeInTheDocument();
      expect(screen.getByText('Result 2')).toBeInTheDocument();
    });
  });

  it('shows loading state while searching', async () => {
    const user = userEvent.setup();
    const mockSearch = jest
      .fn()
      .mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 1000)));

    render(<SearchableSelect onSearch={mockSearch} />);

    const input = screen.getByRole('combobox');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('Loading...');
    });
  });

  it('handles search errors gracefully', async () => {
    const user = userEvent.setup();
    const mockSearch = jest.fn().mockRejectedValue(new Error('Search failed'));

    render(<SearchableSelect onSearch={mockSearch} />);

    const input = screen.getByRole('combobox');
    await user.type(input, 'test');

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('Search failed');
    });
  });
});
```

### Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react';
import { useToggle } from './useToggle';

describe('useToggle', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useToggle(false));
    expect(result.current.value).toBe(false);
  });

  it('toggles value when toggle is called', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current.toggle();
    });

    expect(result.current.value).toBe(true);

    act(() => {
      result.current.toggle();
    });

    expect(result.current.value).toBe(false);
  });

  it('sets value to true when setTrue is called', () => {
    const { result } = renderHook(() => useToggle(false));

    act(() => {
      result.current.setTrue();
    });

    expect(result.current.value).toBe(true);
  });
});
```

### Testing Context

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider, useTheme } from './ThemeContext';

// Test component that uses context
const ThemeConsumer: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="current-theme">{theme}</span>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  );
};

describe('ThemeContext', () => {
  it('provides theme value to consumers', () => {
    render(
      <ThemeProvider initialTheme="light">
        <ThemeConsumer />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-theme')).toHaveTextContent('light');
  });

  it('toggles theme when toggleTheme is called', async () => {
    const user = userEvent.setup();

    render(
      <ThemeProvider initialTheme="light">
        <ThemeConsumer />
      </ThemeProvider>
    );

    await user.click(screen.getByRole('button', { name: /toggle/i }));

    expect(screen.getByTestId('current-theme')).toHaveTextContent('dark');
  });

  it('throws error when useTheme is used outside provider', () => {
    // Suppress console.error for this test
    const spy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      render(<ThemeConsumer />);
    }).toThrow('useTheme must be used within ThemeProvider');

    spy.mockRestore();
  });
});
```

## Integration Testing

### Testing Component Composition

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Form, FormField, Button } from './components';

describe('Form integration', () => {
  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const handleSubmit = jest.fn();

    render(
      <Form onSubmit={handleSubmit}>
        <FormField label="Email" name="email" type="email" />
        <FormField label="Password" name="password" type="password" />
        <Button type="submit">Submit</Button>
      </Form>
    );

    // Fill in form
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');

    // Submit
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
  });

  it('displays validation errors for invalid data', async () => {
    const user = userEvent.setup();

    render(
      <Form>
        <FormField
          label="Email"
          name="email"
          type="email"
          required
          validate={(value) => (!value ? 'Email is required' : undefined)}
        />
        <Button type="submit">Submit</Button>
      </Form>
    );

    // Submit without filling in field
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });
});
```

### Testing with External Dependencies

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserProfile } from './UserProfile';

// Setup MSW server for API mocking
const server = setupServer(
  rest.get('/api/user', (req, res, ctx) => {
    return res(
      ctx.json({
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('UserProfile integration', () => {
  it('loads and displays user data', async () => {
    render(<UserProfile userId={1} />);

    // Initial loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });
  });

  it('handles API errors', async () => {
    // Override handler for this test
    server.use(
      rest.get('/api/user', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(<UserProfile userId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/error loading user/i)).toBeInTheDocument();
    });
  });
});
```

## Accessibility Testing

### Automated Accessibility Tests

```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Button } from './Button';

expect.extend(toHaveNoViolations);

describe('Button accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('is accessible with icon only when aria-label is provided', async () => {
    const { container } = render(
      <Button aria-label="Close">
        <CloseIcon />
      </Button>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Testing Keyboard Navigation

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from './Modal';

describe('Modal keyboard accessibility', () => {
  it('traps focus within modal', async () => {
    const user = userEvent.setup();

    render(
      <Modal isOpen={true} onClose={jest.fn()}>
        <button>First</button>
        <button>Second</button>
        <button>Third</button>
      </Modal>
    );

    const buttons = screen.getAllByRole('button');
    const firstButton = buttons[0];
    const lastButton = buttons[buttons.length - 1];

    // Focus should start at first element
    expect(firstButton).toHaveFocus();

    // Tab to last element
    await user.tab();
    await user.tab();
    expect(lastButton).toHaveFocus();

    // Tab from last should cycle to first
    await user.tab();
    expect(firstButton).toHaveFocus();

    // Shift+Tab from first should cycle to last
    await user.tab({ shift: true });
    expect(lastButton).toHaveFocus();
  });

  it('closes modal when Escape is pressed', async () => {
    const user = userEvent.setup();
    const handleClose = jest.fn();

    render(
      <Modal isOpen={true} onClose={handleClose}>
        <button>Close</button>
      </Modal>
    );

    await user.keyboard('{Escape}');

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
```

### Testing ARIA Attributes

```typescript
describe('Dropdown ARIA attributes', () => {
  it('has correct ARIA attributes', async () => {
    const user = userEvent.setup();

    render(<Dropdown options={options} />);

    const trigger = screen.getByRole('button');

    // Closed state
    expect(trigger).toHaveAttribute('aria-expanded', 'false');
    expect(trigger).toHaveAttribute('aria-haspopup', 'listbox');

    // Open dropdown
    await user.click(trigger);

    // Open state
    expect(trigger).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('listbox')).toBeInTheDocument();

    // Options have correct ARIA
    const options = screen.getAllByRole('option');
    expect(options[0]).toHaveAttribute('aria-selected', 'true');
  });
});
```

## Visual Regression Testing

### Storybook + Chromatic

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline'],
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Primary Button',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button',
  },
};

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
    </div>
  ),
};

export const States: Story = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <Button>Normal</Button>
      <Button disabled>Disabled</Button>
      <Button data-loading="true">Loading</Button>
    </div>
  ),
};
```

### Percy for Visual Testing

```typescript
// Button.percy.test.tsx
import { render } from '@testing-library/react';
import percySnapshot from '@percy/puppeteer';
import { Button } from './Button';

describe('Button visual tests', () => {
  it('renders all variants correctly', async () => {
    const { container } = render(
      <div style={{ padding: '20px' }}>
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
      </div>
    );

    await percySnapshot(page, 'Button - All Variants');
  });

  it('renders all states correctly', async () => {
    const { container } = render(
      <div style={{ padding: '20px' }}>
        <Button>Normal</Button>
        <Button disabled>Disabled</Button>
        <Button className="hover">Hover</Button>
        <Button className="active">Active</Button>
      </div>
    );

    await percySnapshot(page, 'Button - All States');
  });
});
```

## Performance Testing

### Testing Render Performance

```typescript
import { render } from '@testing-library/react';
import { LargeList } from './LargeList';

describe('LargeList performance', () => {
  it('renders 1000 items efficiently', () => {
    const items = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      label: `Item ${i}`,
    }));

    const startTime = performance.now();
    render(<LargeList items={items} />);
    const endTime = performance.now();

    const renderTime = endTime - startTime;

    // Assert render time is reasonable
    expect(renderTime).toBeLessThan(1000); // Less than 1 second
  });

  it('does not re-render unnecessarily', () => {
    const renderSpy = jest.fn();

    const MemoizedItem = React.memo(({ item }: { item: Item }) => {
      renderSpy();
      return <div>{item.label}</div>;
    });

    const { rerender } = render(
      <MemoizedItem item={{ id: 1, label: 'Item 1' }} />
    );

    renderSpy.mockClear();

    // Rerender with same props
    rerender(<MemoizedItem item={{ id: 1, label: 'Item 1' }} />);

    // Should not re-render
    expect(renderSpy).not.toHaveBeenCalled();
  });
});
```

## E2E Testing with Playwright

```typescript
// button.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Button component', () => {
  test('renders and can be clicked', async ({ page }) => {
    await page.goto('/button-demo');

    const button = page.getByRole('button', { name: 'Click me' });
    await expect(button).toBeVisible();

    await button.click();

    await expect(page.getByText('Button clicked!')).toBeVisible();
  });

  test('is keyboard accessible', async ({ page }) => {
    await page.goto('/button-demo');

    await page.keyboard.press('Tab');

    const button = page.getByRole('button', { name: 'Click me' });
    await expect(button).toBeFocused();

    await page.keyboard.press('Enter');

    await expect(page.getByText('Button clicked!')).toBeVisible();
  });

  test('has correct visual appearance', async ({ page }) => {
    await page.goto('/button-demo');

    const button = page.getByRole('button', { name: 'Primary' });

    // Screenshot test
    await expect(button).toHaveScreenshot('primary-button.png');
  });
});
```

## Test Organization

### File Structure

```
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.module.css
│   ├── Button.types.ts
│   ├── Button.test.tsx          # Unit tests
│   ├── Button.a11y.test.tsx     # Accessibility tests
│   ├── Button.integration.test.tsx # Integration tests
│   ├── Button.stories.tsx       # Storybook stories
│   └── index.ts
```

### Test Naming Conventions

```typescript
// ✅ Good - descriptive test names
describe('Button', () => {
  it('renders with children', () => {});
  it('calls onClick when clicked', () => {});
  it('is disabled when disabled prop is true', () => {});
});

// ❌ Bad - vague test names
describe('Button', () => {
  it('works', () => {});
  it('test 1', () => {});
  it('button test', () => {});
});
```

## Testing Best Practices

### DO's

✅ Test user-visible behavior
✅ Use semantic queries (getByRole, getByLabelText)
✅ Wait for async updates with waitFor
✅ Test accessibility
✅ Mock external dependencies
✅ Keep tests isolated and independent
✅ Use descriptive test names
✅ Test error states

### DON'Ts

❌ Test implementation details
❌ Use testId as primary query method
❌ Rely on setTimeout for async tests
❌ Skip accessibility tests
❌ Test external libraries
❌ Create interdependent tests
❌ Only test happy paths

## Coverage Goals

```json
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --coverage
      - run: npm run test:a11y
      - uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

---

**Next Steps:**
- [Performance Guide](./performance-guide.md) - Optimize component performance
- [Component Architecture](./component-architecture.md) - Testable architecture patterns
