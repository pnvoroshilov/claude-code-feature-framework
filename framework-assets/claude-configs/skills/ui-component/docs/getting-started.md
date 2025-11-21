# Getting Started with UI Component Development

## Introduction

This guide will walk you through creating your first React component using the UI Component Development skill. You'll learn the fundamentals of component creation, TypeScript integration, styling, and accessibility.

## Prerequisites

### Required Knowledge
- JavaScript ES6+ fundamentals
- React basics (components, props, state)
- HTML and CSS
- Basic command line usage

### Required Tools
- Node.js (v16 or higher)
- npm or yarn package manager
- Code editor (VS Code recommended)
- TypeScript support in editor

### Project Setup
```bash
# Create a new React + TypeScript project
npx create-react-app my-component-library --template typescript

# Or with Vite (recommended for faster development)
npm create vite@latest my-component-library -- --template react-ts

# Navigate to project
cd my-component-library

# Install dependencies
npm install

# Install additional development dependencies
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

## Your First Component

### Step 1: Create Component Directory

```bash
# Create directory structure
mkdir -p src/components/Button
touch src/components/Button/{Button.tsx,Button.module.css,Button.test.tsx,index.ts}
```

### Step 2: Define TypeScript Interface

Create `Button.types.ts`:

```typescript
// src/components/Button/Button.types.ts
import { ReactNode, MouseEvent } from 'react';

/**
 * Button component props
 */
export interface ButtonProps {
  /**
   * Button content
   */
  children: ReactNode;

  /**
   * Visual style variant
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';

  /**
   * Button size
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Disabled state
   * @default false
   */
  disabled?: boolean;

  /**
   * Full width button
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Click handler
   */
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void;

  /**
   * Button type attribute
   * @default 'button'
   */
  type?: 'button' | 'submit' | 'reset';

  /**
   * Additional CSS class names
   */
  className?: string;

  /**
   * ARIA label for accessibility
   */
  'aria-label'?: string;
}
```

### Step 3: Implement Component

Create `Button.tsx`:

```typescript
// src/components/Button/Button.tsx
import React from 'react';
import { ButtonProps } from './Button.types';
import styles from './Button.module.css';

/**
 * Button component for user interactions
 *
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 */
export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  fullWidth = false,
  onClick,
  type = 'button',
  className = '',
  'aria-label': ariaLabel,
}) => {
  const buttonClasses = [
    styles.button,
    styles[variant],
    styles[size],
    fullWidth && styles.fullWidth,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel}
    >
      {children}
    </button>
  );
};

Button.displayName = 'Button';
```

### Step 4: Add Styles

Create `Button.module.css`:

```css
/* src/components/Button/Button.module.css */

/* Base button styles */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  outline: none;
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
}

.button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* Size variants */
.sm {
  padding: 6px 12px;
  font-size: 14px;
  line-height: 1.4;
  min-height: 32px;
}

.md {
  padding: 10px 20px;
  font-size: 16px;
  line-height: 1.5;
  min-height: 40px;
}

.lg {
  padding: 14px 28px;
  font-size: 18px;
  line-height: 1.5;
  min-height: 48px;
}

/* Style variants */
.primary {
  background-color: #0066cc;
  color: white;
}

.primary:hover:not(:disabled) {
  background-color: #0052a3;
}

.primary:active:not(:disabled) {
  background-color: #003d7a;
}

.secondary {
  background-color: #6c757d;
  color: white;
}

.secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.secondary:active:not(:disabled) {
  background-color: #484e53;
}

.outline {
  background-color: transparent;
  color: #0066cc;
  border: 2px solid #0066cc;
}

.outline:hover:not(:disabled) {
  background-color: #0066cc;
  color: white;
}

.ghost {
  background-color: transparent;
  color: #0066cc;
}

.ghost:hover:not(:disabled) {
  background-color: rgba(0, 102, 204, 0.1);
}

/* Disabled state */
.button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Full width */
.fullWidth {
  width: 100%;
}

/* Loading state (for future enhancement) */
.button[data-loading="true"] {
  position: relative;
  color: transparent;
  pointer-events: none;
}
```

### Step 5: Create Export File

Create `index.ts`:

```typescript
// src/components/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button.types';
```

### Step 6: Write Tests

Create `Button.test.tsx`:

```typescript
// src/components/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(
      <Button onClick={handleClick} disabled>
        Click me
      </Button>
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();

    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    let button = screen.getByRole('button');
    expect(button.className).toContain('primary');

    rerender(<Button variant="secondary">Secondary</Button>);
    button = screen.getByRole('button');
    expect(button.className).toContain('secondary');
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<Button size="sm">Small</Button>);
    let button = screen.getByRole('button');
    expect(button.className).toContain('sm');

    rerender(<Button size="lg">Large</Button>);
    button = screen.getByRole('button');
    expect(button.className).toContain('lg');
  });

  it('applies fullWidth class when prop is true', () => {
    render(<Button fullWidth>Full Width</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('fullWidth');
  });

  it('uses custom className', () => {
    render(<Button className="custom-class">Custom</Button>);
    const button = screen.getByRole('button');
    expect(button.className).toContain('custom-class');
  });

  it('sets type attribute correctly', () => {
    const { rerender } = render(<Button type="submit">Submit</Button>);
    let button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'submit');

    rerender(<Button type="reset">Reset</Button>);
    button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'reset');
  });

  it('applies aria-label when provided', () => {
    render(<Button aria-label="Close dialog">×</Button>);
    expect(screen.getByRole('button', { name: 'Close dialog' })).toBeInTheDocument();
  });
});
```

### Step 7: Use Your Component

```typescript
// src/App.tsx
import React from 'react';
import { Button } from './components/Button';

function App() {
  const handleClick = () => {
    console.log('Button clicked!');
  };

  return (
    <div className="App">
      <h1>Button Examples</h1>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <Button variant="primary" onClick={handleClick}>
          Primary Button
        </Button>

        <Button variant="secondary" onClick={handleClick}>
          Secondary Button
        </Button>

        <Button variant="outline" onClick={handleClick}>
          Outline Button
        </Button>

        <Button variant="ghost" onClick={handleClick}>
          Ghost Button
        </Button>

        <Button variant="primary" disabled>
          Disabled Button
        </Button>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h2>Sizes</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </div>
      </div>

      <div style={{ marginTop: '2rem', maxWidth: '400px' }}>
        <h2>Full Width</h2>
        <Button fullWidth variant="primary">
          Full Width Button
        </Button>
      </div>
    </div>
  );
}

export default App;
```

## Running and Testing

### Start Development Server

```bash
npm run dev
# or
npm start
```

Visit `http://localhost:3000` (or the port shown in terminal) to see your component.

### Run Tests

```bash
# Run tests once
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## Next Steps

### Enhance Your Component

1. **Add Loading State**
   ```typescript
   interface ButtonProps {
     // ... existing props
     loading?: boolean;
   }
   ```

2. **Add Icon Support**
   ```typescript
   interface ButtonProps {
     // ... existing props
     leftIcon?: ReactNode;
     rightIcon?: ReactNode;
   }
   ```

3. **Add More Variants**
   ```typescript
   variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
   ```

### Learn Advanced Patterns

- [Component Architecture Guide](./component-architecture.md)
- [TypeScript Patterns](./typescript-patterns.md)
- [Accessibility Standards](./accessibility-standards.md)
- [Testing Strategies](./testing-strategies.md)

### Explore Examples

- [Basic Components](../examples/basic/)
- [Advanced Patterns](../examples/advanced/)
- [Real-World Components](../examples/real-world/)

## Troubleshooting

### Common Issues

**CSS Modules not working**
- Ensure file is named `*.module.css`
- Check TypeScript configuration for CSS module support
- Verify import statement is correct

**TypeScript errors**
- Run `npm install --save-dev @types/react @types/react-dom`
- Check `tsconfig.json` includes correct compiler options
- Ensure all props are properly typed

**Tests failing**
- Verify `@testing-library/react` is installed
- Check test setup files are configured
- Ensure test matchers are imported from `@testing-library/jest-dom`

## Best Practices Checklist

- [ ] Component has clear, single responsibility
- [ ] Props interface is well-typed
- [ ] Component is accessible (ARIA, keyboard support)
- [ ] Styles are modular and maintainable
- [ ] Tests cover main functionality
- [ ] Documentation is clear
- [ ] Component is performant (no unnecessary re-renders)
- [ ] Error states are handled
- [ ] Loading states are implemented where needed
- [ ] Component works across browsers

## Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [CSS Modules Guide](https://github.com/css-modules/css-modules)

---

**Next**: Continue to [Component Architecture](./component-architecture.md) to learn advanced patterns and best practices.
