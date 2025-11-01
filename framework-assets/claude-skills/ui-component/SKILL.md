---
name: ui-component
description: Expert-level React component creation with TypeScript, modern styling solutions, comprehensive accessibility standards, and production-ready patterns
version: 1.0.0
tags: [react, ui, components, typescript, frontend]
---

# UI Component Development Skill

## Overview
Expert-level React component creation with TypeScript, modern styling solutions, comprehensive accessibility standards, and production-ready patterns. This skill covers the complete lifecycle of UI component development from initial design to deployment.

## Core Competencies

### 1. React Component Architecture
- Functional components with hooks
- Component composition patterns
- Props interface design
- State management strategies
- Performance optimization techniques
- Ref forwarding and imperative handles
- Component lifecycle optimization
- Error boundaries and fallbacks

### 2. TypeScript Integration
- Strict type definitions
- Generic component patterns
- Discriminated unions for variants
- Type-safe props and refs
- Utility types for component APIs
- Type inference optimization
- JSDoc with TypeScript
- Advanced type patterns

### 3. Styling Solutions
- CSS Modules with TypeScript
- Styled Components (CSS-in-JS)
- Tailwind CSS integration
- SCSS/SASS patterns
- CSS Variables (Custom Properties)
- Responsive design patterns
- Theme system implementation
- Animation and transitions

### 4. Accessibility (a11y)
- ARIA attributes and roles
- Keyboard navigation
- Screen reader support
- Focus management
- Semantic HTML
- WCAG 2.1 Level AA compliance
- Color contrast requirements
- Touch target sizing

### 5. Component Patterns
- Compound components
- Render props
- Higher-order components (HOCs)
- Custom hooks
- Controlled vs uncontrolled
- Polymorphic components
- Headless UI patterns
- Design system integration

### 6. Testing & Quality
- Jest + React Testing Library
- Component testing strategies
- Accessibility testing
- Visual regression testing
- Storybook integration
- E2E testing patterns
- Performance testing
- Type coverage

## When to Use This Skill

### Ideal Scenarios
✅ Creating new React components from scratch
✅ Building reusable component libraries
✅ Implementing design system components
✅ Adding TypeScript to existing components
✅ Improving component accessibility
✅ Optimizing component performance
✅ Refactoring class components to hooks
✅ Creating complex interactive UI elements

### Not Suitable For
❌ Backend API development
❌ Database schema design
❌ Server-side rendering setup
❌ Build configuration (use DevOps skills)
❌ State management architecture (use separate skill)
❌ Routing configuration (use separate skill)

## Quick Start

### Basic Component Creation
```typescript
import React from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  children,
  onClick
}) => {
  return (
    <button
      className={`${styles.button} ${styles[variant]} ${styles[size]}`}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
};
```

## Component Development Workflow

### Phase 1: Planning & Design
1. **Requirements Analysis**
   - Identify component purpose and use cases
   - Define component API (props interface)
   - Determine variants and states
   - Consider accessibility requirements
   - Review design specifications

2. **API Design**
   - Define TypeScript interfaces
   - Plan prop naming conventions
   - Design callback signatures
   - Document expected behavior
   - Consider default values

3. **Architecture Decisions**
   - Choose styling approach
   - Determine state management
   - Plan component composition
   - Select testing strategy
   - Consider performance implications

### Phase 2: Implementation
1. **Setup Component Structure**
   - Create component directory
   - Setup TypeScript interfaces
   - Initialize styling files
   - Create test files
   - Add Storybook stories

2. **Implement Core Functionality**
   - Build base component structure
   - Implement props handling
   - Add state management
   - Handle events and callbacks
   - Implement variants

3. **Add Styling**
   - Implement base styles
   - Add variant styles
   - Create responsive breakpoints
   - Add animations/transitions
   - Implement theme support

4. **Accessibility Implementation**
   - Add ARIA attributes
   - Implement keyboard navigation
   - Ensure focus management
   - Add screen reader support
   - Test with accessibility tools

### Phase 3: Testing & Quality
1. **Write Tests**
   - Unit tests for logic
   - Integration tests for interactions
   - Accessibility tests
   - Visual regression tests
   - Performance benchmarks

2. **Code Review Checklist**
   - TypeScript strict mode compliance
   - Props validation complete
   - Accessibility requirements met
   - Performance optimized
   - Documentation complete
   - Tests passing with good coverage

3. **Documentation**
   - JSDoc comments
   - README with examples
   - Storybook stories
   - API documentation
   - Usage guidelines

### Phase 4: Integration & Deployment
1. **Integration Testing**
   - Test in consuming applications
   - Verify bundle size impact
   - Check for style conflicts
   - Validate SSR compatibility
   - Test across browsers

2. **Optimization**
   - Code splitting opportunities
   - Lazy loading implementation
   - Memoization where appropriate
   - Bundle size optimization
   - Performance profiling

## Best Practices

### Component Design Principles
1. **Single Responsibility**: Each component should do one thing well
2. **Composition Over Inheritance**: Build complex UIs from simple components
3. **Props Over State**: Prefer controlled components when possible
4. **Explicit Over Implicit**: Make component behavior obvious
5. **Accessibility First**: Build accessibility in from the start

### TypeScript Best Practices
```typescript
// ✅ Good: Explicit, strict typing
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

// ❌ Bad: Loose typing
interface ButtonProps {
  variant?: string;
  size?: any;
  onClick?: Function;
  children?: any;
}
```

### Accessibility Checklist
- [ ] Semantic HTML elements used
- [ ] ARIA roles and attributes added where needed
- [ ] Keyboard navigation implemented
- [ ] Focus indicators visible
- [ ] Color contrast ratios met (4.5:1 minimum)
- [ ] Screen reader tested
- [ ] Touch targets ≥ 44x44px
- [ ] Error messages announced
- [ ] Loading states communicated

### Performance Guidelines
1. **Memoization**: Use `React.memo` for expensive render logic
2. **Callback Stability**: Use `useCallback` for props callbacks
3. **State Optimization**: Use `useMemo` for derived values
4. **Lazy Loading**: Code-split large components
5. **Bundle Size**: Monitor and optimize component size

## Common Patterns

### 1. Compound Components Pattern
```typescript
// Flexible API for related components
<Select>
  <Select.Trigger>Choose option</Select.Trigger>
  <Select.Options>
    <Select.Option value="1">Option 1</Select.Option>
    <Select.Option value="2">Option 2</Select.Option>
  </Select.Options>
</Select>
```

### 2. Polymorphic Components
```typescript
// Component that can render as different HTML elements
<Button as="a" href="/home">Link Button</Button>
<Button as="button" onClick={handler}>Button</Button>
```

### 3. Render Props
```typescript
// Flexible rendering with render props
<DataProvider>
  {({ data, loading }) => (
    loading ? <Spinner /> : <DataDisplay data={data} />
  )}
</DataProvider>
```

### 4. Custom Hooks
```typescript
// Extract reusable logic
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle] as const;
}
```

## Documentation Standards

### Component Documentation Template
```typescript
/**
 * Button component for user interactions
 *
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click me
 * </Button>
 * ```
 *
 * @see {@link docs/button-guide.md} for detailed usage
 */
export const Button: React.FC<ButtonProps> = ({ ... }) => { ... };
```

### Props Documentation
```typescript
interface ButtonProps {
  /**
   * Visual style variant of the button
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'outline';

  /**
   * Size of the button
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Whether the button is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Click event handler
   */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
```

## Troubleshooting Guide

### Common Issues

#### TypeScript Errors
**Issue**: "Type 'X' is not assignable to type 'Y'"
- Check prop types match interface
- Verify discriminated unions are properly typed
- Ensure ref types are correct

#### Styling Issues
**Issue**: Styles not applying
- Check CSS module imports
- Verify className is applied
- Check CSS specificity conflicts
- Ensure styles are imported in correct order

#### Accessibility Issues
**Issue**: Screen reader not announcing content
- Verify ARIA labels are present
- Check for aria-live regions
- Ensure semantic HTML is used
- Test with actual screen reader

#### Performance Issues
**Issue**: Component re-rendering too often
- Check for inline function creation
- Verify useCallback/useMemo usage
- Look for unnecessary state updates
- Profile with React DevTools

## File Organization

### Recommended Structure
```
components/
├── Button/
│   ├── Button.tsx              # Component implementation
│   ├── Button.types.ts         # TypeScript interfaces
│   ├── Button.module.css       # Component styles
│   ├── Button.test.tsx         # Unit tests
│   ├── Button.stories.tsx      # Storybook stories
│   ├── Button.a11y.test.tsx    # Accessibility tests
│   ├── index.ts                # Public exports
│   └── README.md               # Component documentation
```

## Integration with Tools

### Storybook Integration
```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Primary Button',
  },
};
```

### Jest + React Testing Library
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

## Resources

### Documentation
- [Getting Started Guide](docs/getting-started.md)
- [Component Architecture](docs/component-architecture.md)
- [TypeScript Patterns](docs/typescript-patterns.md)
- [Styling Guide](docs/styling-guide.md)
- [Accessibility Standards](docs/accessibility-standards.md)
- [Testing Strategies](docs/testing-strategies.md)

### Examples
- [Basic Components](examples/basic/)
- [Advanced Patterns](examples/advanced/)
- [Real-World Components](examples/real-world/)

### Templates
- [Component Template](templates/component-template/)
- [Test Template](templates/test-template/)
- [Storybook Template](templates/storybook-template/)

### External Resources
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Testing Library](https://testing-library.com/react)

## Version History

### v1.0.0 (2025-10-31)
- Initial skill package release
- Core component patterns
- TypeScript integration
- Accessibility standards
- Testing strategies
- Comprehensive examples

## Contributing

When extending this skill:
1. Follow existing patterns and conventions
2. Add tests for new patterns
3. Update documentation
4. Add examples for new features
5. Ensure accessibility compliance

## License

This skill is part of the Claude Code Feature Framework.
