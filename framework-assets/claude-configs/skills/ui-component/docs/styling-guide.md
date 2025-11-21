# Styling Guide for React Components

## Introduction

This guide covers modern CSS approaches for React components, including CSS Modules, CSS-in-JS, Tailwind CSS, and best practices for maintainable, scalable styling solutions.

## Styling Approaches

### 1. CSS Modules

**Best for**: Component-scoped styles, traditional CSS workflow, good performance.

#### Setup

```typescript
// Button.module.css
.button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.primary {
  background-color: #0066cc;
  color: white;
}

.secondary {
  background-color: #6c757d;
  color: white;
}
```

```typescript
// Button.tsx
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  children,
}) => {
  return (
    <button className={`${styles.button} ${styles[variant]}`}>
      {children}
    </button>
  );
};
```

#### Dynamic Class Names

```typescript
import classNames from 'classnames';
import styles from './Button.module.css';

export const Button: React.FC<ButtonProps> = ({
  variant,
  size,
  disabled,
  fullWidth,
  className,
}) => {
  return (
    <button
      className={classNames(
        styles.button,
        styles[variant],
        styles[size],
        {
          [styles.disabled]: disabled,
          [styles.fullWidth]: fullWidth,
        },
        className
      )}
    >
      {children}
    </button>
  );
};
```

#### CSS Module TypeScript Types

```typescript
// Button.module.css.d.ts (auto-generated or manual)
declare const styles: {
  readonly button: string;
  readonly primary: string;
  readonly secondary: string;
  readonly sm: string;
  readonly md: string;
  readonly lg: string;
  readonly disabled: string;
  readonly fullWidth: string;
};

export default styles;
```

### 2. CSS-in-JS (Styled Components)

**Best for**: Dynamic styling, theme-aware components, type-safe styles.

#### Basic Styled Component

```typescript
import styled from 'styled-components';

interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}

const StyledButton = styled.button<ButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: ${({ size }) => {
    switch (size) {
      case 'sm':
        return '6px 12px';
      case 'lg':
        return '14px 28px';
      default:
        return '10px 20px';
    }
  }};
  font-size: ${({ size }) => {
    switch (size) {
      case 'sm':
        return '14px';
      case 'lg':
        return '18px';
      default:
        return '16px';
    }
  }};
  background-color: ${({ variant, theme }) => {
    switch (variant) {
      case 'secondary':
        return theme.colors.secondary;
      default:
        return theme.colors.primary;
    }
  }};
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: ${({ fullWidth }) => (fullWidth ? '100%' : 'auto')};
  transition: all 0.2s ease-in-out;

  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

export const Button: React.FC<ButtonProps & { children: React.ReactNode }> = ({
  children,
  ...props
}) => {
  return <StyledButton {...props}>{children}</StyledButton>;
};
```

#### Theme System

```typescript
// theme.ts
export const lightTheme = {
  colors: {
    primary: '#0066cc',
    secondary: '#6c757d',
    success: '#28a745',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8',
    text: '#212529',
    background: '#ffffff',
    border: '#dee2e6',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      md: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
  },
  radii: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '1rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
  },
};

export const darkTheme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    text: '#f8f9fa',
    background: '#212529',
    border: '#495057',
  },
};

export type Theme = typeof lightTheme;
```

```typescript
// App.tsx
import { ThemeProvider } from 'styled-components';
import { lightTheme, darkTheme } from './theme';

export const App: React.FC = () => {
  const [isDark, setIsDark] = useState(false);

  return (
    <ThemeProvider theme={isDark ? darkTheme : lightTheme}>
      <Button variant="primary">Themed Button</Button>
    </ThemeProvider>
  );
};
```

#### Styled Components with Refs

```typescript
const StyledInput = styled.input`
  padding: 10px;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radii.md};
  font-size: ${({ theme }) => theme.typography.fontSize.md};
`;

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>((props, ref) => {
  return <StyledInput ref={ref} {...props} />;
});
```

### 3. Tailwind CSS

**Best for**: Rapid development, utility-first approach, consistent design system.

#### Basic Component

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  children: React.ReactNode;
  className?: string;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  children,
  className = '',
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'bg-transparent border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-7 py-3.5 text-lg',
  };

  const widthClass = fullWidth ? 'w-full' : '';

  const classes = classNames(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    widthClass,
    className
  );

  return <button className={classes}>{children}</button>;
};
```

#### Custom Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f2ff',
          100: '#b3d9ff',
          200: '#80bfff',
          300: '#4da6ff',
          400: '#1a8cff',
          500: '#0066cc',
          600: '#0052a3',
          700: '#003d7a',
          800: '#002952',
          900: '#001429',
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

### 4. SCSS/SASS

**Best for**: Complex styling logic, variables, mixins, nested styles.

#### Component Styles

```scss
// Button.module.scss
@use './variables' as *;
@use './mixins' as *;

.button {
  @include button-base;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md $spacing-lg;
  border: none;
  border-radius: $border-radius-md;
  font-family: $font-family-base;
  font-size: $font-size-md;
  font-weight: $font-weight-medium;
  cursor: pointer;
  transition: all $transition-base;

  &:focus-visible {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }

  // Variants
  &.primary {
    @include button-variant($color-primary, $color-white);
  }

  &.secondary {
    @include button-variant($color-secondary, $color-white);
  }

  &.outline {
    background-color: transparent;
    color: $color-primary;
    border: 2px solid $color-primary;

    &:hover:not(:disabled) {
      background-color: $color-primary;
      color: $color-white;
    }
  }

  // Sizes
  &.sm {
    padding: $spacing-sm $spacing-md;
    font-size: $font-size-sm;
  }

  &.lg {
    padding: $spacing-lg $spacing-xl;
    font-size: $font-size-lg;
  }

  // States
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.fullWidth {
    width: 100%;
  }

  // Loading state
  &[data-loading='true'] {
    position: relative;
    color: transparent;

    &::after {
      @include spinner;
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
  }
}
```

#### Variables and Mixins

```scss
// _variables.scss
// Colors
$color-primary: #0066cc;
$color-secondary: #6c757d;
$color-success: #28a745;
$color-danger: #dc3545;
$color-white: #ffffff;
$color-black: #000000;

// Spacing
$spacing-xs: 0.25rem;
$spacing-sm: 0.5rem;
$spacing-md: 1rem;
$spacing-lg: 1.5rem;
$spacing-xl: 2rem;

// Typography
$font-family-base: 'Inter', system-ui, sans-serif;
$font-size-xs: 0.75rem;
$font-size-sm: 0.875rem;
$font-size-md: 1rem;
$font-size-lg: 1.125rem;
$font-weight-normal: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;

// Border radius
$border-radius-sm: 0.25rem;
$border-radius-md: 0.5rem;
$border-radius-lg: 1rem;

// Transitions
$transition-base: all 0.2s ease-in-out;

// Breakpoints
$breakpoint-sm: 640px;
$breakpoint-md: 768px;
$breakpoint-lg: 1024px;
$breakpoint-xl: 1280px;
```

```scss
// _mixins.scss
@use './variables' as *;

// Button base styles
@mixin button-base {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  text-decoration: none;
  outline: none;
}

// Button variant
@mixin button-variant($bg-color, $text-color) {
  background-color: $bg-color;
  color: $text-color;

  &:hover:not(:disabled) {
    background-color: darken($bg-color, 10%);
  }

  &:active:not(:disabled) {
    background-color: darken($bg-color, 15%);
  }
}

// Responsive breakpoint
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (min-width: $breakpoint-sm) {
      @content;
    }
  } @else if $breakpoint == 'md' {
    @media (min-width: $breakpoint-md) {
      @content;
    }
  } @else if $breakpoint == 'lg' {
    @media (min-width: $breakpoint-lg) {
      @content;
    }
  } @else if $breakpoint == 'xl' {
    @media (min-width: $breakpoint-xl) {
      @content;
    }
  }
}

// Spinner animation
@mixin spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// Truncate text
@mixin truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// Visually hidden (for screen readers)
@mixin visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

## CSS Architecture Patterns

### 1. BEM Methodology

```scss
// Block
.card {
  background: white;
  border-radius: 8px;
  padding: 1rem;

  // Element
  &__header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }

  &__title {
    font-size: 1.25rem;
    font-weight: 600;
  }

  &__body {
    color: #666;
  }

  &__footer {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  // Modifier
  &--featured {
    border: 2px solid #0066cc;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  &--compact {
    padding: 0.5rem;

    .card__header {
      margin-bottom: 0.5rem;
    }
  }
}
```

### 2. CSS Custom Properties (CSS Variables)

```css
:root {
  /* Colors */
  --color-primary: #0066cc;
  --color-secondary: #6c757d;
  --color-text: #212529;
  --color-background: #ffffff;
  --color-border: #dee2e6;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-family-base: 'Inter', system-ui, sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-md: 1rem;
  --font-size-lg: 1.125rem;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-base: all 0.2s ease-in-out;
}

/* Dark theme */
[data-theme='dark'] {
  --color-text: #f8f9fa;
  --color-background: #212529;
  --color-border: #495057;
}

/* Component using variables */
.button {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-family: var(--font-family-base);
  transition: var(--transition-base);
}
```

### 3. Responsive Design Patterns

```scss
.container {
  width: 100%;
  padding: 0 1rem;

  // Mobile first approach
  @media (min-width: 640px) {
    max-width: 640px;
    margin: 0 auto;
  }

  @media (min-width: 768px) {
    max-width: 768px;
  }

  @media (min-width: 1024px) {
    max-width: 1024px;
  }

  @media (min-width: 1280px) {
    max-width: 1280px;
  }
}

.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr; // Mobile: 1 column

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr); // Tablet: 2 columns
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr); // Desktop: 3 columns
  }
}
```

## Animation and Transitions

### CSS Transitions

```scss
.button {
  transition: background-color 0.2s ease-in-out,
              transform 0.2s ease-in-out,
              box-shadow 0.2s ease-in-out;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  &:active {
    transform: translateY(0);
  }
}
```

### CSS Animations

```scss
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.modal {
  animation: fadeIn 0.3s ease-out;
}

.spinner {
  animation: spin 1s linear infinite;
}

.loading {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

## Performance Best Practices

### 1. CSS Performance

```scss
// ✅ Good - efficient selectors
.button { }
.button--primary { }
.card__header { }

// ❌ Bad - inefficient selectors
div > ul > li > a { }
#header .nav ul li a { }
* { }

// ✅ Good - use transforms for animations
.animated {
  transform: translateX(100px);
  transition: transform 0.3s;
}

// ❌ Bad - animating layout properties
.animated {
  left: 100px;
  transition: left 0.3s;
}
```

### 2. Critical CSS

```html
<!-- Inline critical CSS -->
<style>
  .above-fold { /* Styles for content visible without scrolling */ }
</style>

<!-- Load non-critical CSS async -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

### 3. CSS-in-JS Performance

```typescript
// ✅ Good - static styles outside component
const StaticButton = styled.button`
  padding: 10px 20px;
  border-radius: 4px;
`;

// ❌ Bad - dynamic styles with inline functions
const DynamicButton = styled.button`
  padding: ${() => computePadding()}px;
  color: ${() => getColor()};
`;

// ✅ Better - use props for dynamic values
const DynamicButton = styled.button<{ $padding: number; $color: string }>`
  padding: ${({ $padding }) => $padding}px;
  color: ${({ $color }) => $color};
`;
```

## Styling Checklist

- [ ] Styles are scoped to component (CSS Modules or CSS-in-JS)
- [ ] No global style pollution
- [ ] Responsive design implemented (mobile-first)
- [ ] Accessible focus states defined
- [ ] Hover and active states implemented
- [ ] Loading and disabled states styled
- [ ] Animations are smooth (60fps)
- [ ] Color contrast meets WCAG standards
- [ ] Touch targets are ≥ 44x44px
- [ ] Print styles considered (if needed)

---

**Next Steps:**
- [Accessibility Standards](./accessibility-standards.md) - Implement a11y
- [Testing Strategies](./testing-strategies.md) - Test styled components
- [Performance Guide](./performance-guide.md) - Optimize rendering
