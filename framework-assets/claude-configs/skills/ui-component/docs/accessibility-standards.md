# Accessibility Standards for React Components

## Introduction

This guide covers implementing WCAG 2.1 Level AA accessibility standards in React components, including ARIA attributes, keyboard navigation, screen reader support, and testing strategies.

## Core Accessibility Principles (POUR)

### Perceivable
Information and UI components must be presentable to users in ways they can perceive.

### Operable
UI components and navigation must be operable.

### Understandable
Information and the operation of UI must be understandable.

### Robust
Content must be robust enough to be interpreted by a wide variety of user agents, including assistive technologies.

## Semantic HTML

### Use Correct HTML Elements

```typescript
// ✅ Good - semantic HTML
export const Navigation: React.FC = () => (
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/home">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
);

// ❌ Bad - divs for everything
export const Navigation: React.FC = () => (
  <div className="nav">
    <div className="nav-item" onClick={() => navigate('/home')}>Home</div>
    <div className="nav-item" onClick={() => navigate('/about')}>About</div>
  </div>
);
```

### Button vs Link

```typescript
// ✅ Button for actions
<button onClick={handleSubmit}>Submit</button>

// ✅ Link for navigation
<a href="/page">Go to page</a>

// ❌ Bad - div as button
<div onClick={handleClick}>Click me</div>

// ❌ Bad - button for navigation
<button onClick={() => navigate('/page')}>Go to page</button>
```

## ARIA Attributes

### ARIA Roles

```typescript
// Main landmarks
<header role="banner">...</header>
<nav role="navigation" aria-label="Main">...</nav>
<main role="main">...</main>
<aside role="complementary">...</aside>
<footer role="contentinfo">...</footer>

// Interactive elements
<div role="button" tabIndex={0}>Custom Button</div>
<div role="dialog" aria-modal="true">Modal Content</div>
<div role="alert">Important message</div>
<div role="status">Status update</div>

// Form elements
<div role="radiogroup">
  <div role="radio" aria-checked="true">Option 1</div>
  <div role="radio" aria-checked="false">Option 2</div>
</div>
```

### ARIA Labels and Descriptions

```typescript
// aria-label - provides accessible name
<button aria-label="Close dialog">
  <X />
</button>

// aria-labelledby - references element with label
<div role="dialog" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Action</h2>
  <p>Are you sure?</p>
</div>

// aria-describedby - provides additional description
<input
  type="email"
  aria-describedby="email-hint"
/>
<span id="email-hint">We'll never share your email</span>

// aria-label vs aria-labelledby
<button aria-label="Submit form">Submit</button>
<button aria-labelledby="submit-text">
  <span id="submit-text">Submit</span>
</button>
```

### ARIA States and Properties

```typescript
// aria-expanded - for expandable elements
<button
  aria-expanded={isOpen}
  aria-controls="dropdown-menu"
>
  Menu
</button>

// aria-selected - for selectable items
<div role="tab" aria-selected={isSelected}>Tab 1</div>

// aria-checked - for checkboxes and radios
<div role="checkbox" aria-checked={isChecked}>Option</div>

// aria-disabled - for disabled elements
<button aria-disabled="true">Disabled</button>

// aria-hidden - hide from screen readers
<div aria-hidden="true">Decorative content</div>

// aria-live - announce dynamic content
<div aria-live="polite">Status: Loading...</div>
<div aria-live="assertive">Error: Form validation failed</div>

// aria-invalid - for form validation
<input
  type="email"
  aria-invalid={!!error}
  aria-describedby={error ? "email-error" : undefined}
/>
{error && <span id="email-error">{error}</span>}

// aria-required - for required fields
<input
  type="text"
  required
  aria-required="true"
/>
```

## Keyboard Navigation

### Focus Management

```typescript
// Trap focus in modal
export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Save current focus
      previousFocusRef.current = document.activeElement as HTMLElement;

      // Focus first focusable element
      const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      firstFocusable?.focus();
    } else {
      // Restore previous focus
      previousFocusRef.current?.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }

    if (e.key === 'Tab') {
      const focusableElements = modalRef.current?.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (!focusableElements || focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      // Shift + Tab on first element
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
      // Tab on last element
      else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
};
```

### Keyboard Event Handlers

```typescript
// Custom button with keyboard support
export const CustomButton: React.FC<ButtonProps> = ({ onClick, children }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Activate on Enter or Space
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      className={styles.customButton}
    >
      {children}
    </div>
  );
};

// Dropdown with arrow key navigation
export const Dropdown: React.FC<DropdownProps> = ({ options, onSelect }) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < options.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev));
        break;
      case 'Enter':
        e.preventDefault();
        onSelect(options[selectedIndex]);
        setIsOpen(false);
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        break;
    }
  };

  return (
    <div className={styles.dropdown}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        Select option
      </button>
      {isOpen && (
        <ul role="listbox" onKeyDown={handleKeyDown}>
          {options.map((option, index) => (
            <li
              key={option.value}
              role="option"
              aria-selected={index === selectedIndex}
              onClick={() => onSelect(option)}
            >
              {option.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

### Focus Indicators

```css
/* ✅ Good - visible focus indicators */
button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* ❌ Bad - removing focus outline without alternative */
button:focus {
  outline: none;
}

/* ✅ Better - custom focus style */
button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.5);
}
```

## Screen Reader Support

### Live Regions

```typescript
// Status messages
export const StatusMessage: React.FC<{ message: string; type: 'info' | 'error' }> = ({
  message,
  type,
}) => {
  return (
    <div
      role={type === 'error' ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      aria-atomic="true"
    >
      {message}
    </div>
  );
};

// Loading indicator
export const LoadingSpinner: React.FC = () => {
  return (
    <div role="status" aria-live="polite" aria-busy="true">
      <span className="visually-hidden">Loading...</span>
      <div className={styles.spinner} aria-hidden="true" />
    </div>
  );
};
```

### Visually Hidden Content

```typescript
// Visually hidden but accessible to screen readers
const visuallyHidden: React.CSSProperties = {
  position: 'absolute',
  width: '1px',
  height: '1px',
  padding: 0,
  margin: '-1px',
  overflow: 'hidden',
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap',
  border: 0,
};

export const IconButton: React.FC<IconButtonProps> = ({ icon, label, onClick }) => {
  return (
    <button onClick={onClick} aria-label={label}>
      {icon}
      <span style={visuallyHidden}>{label}</span>
    </button>
  );
};

// Or with CSS
// .visually-hidden { /* same styles */ }
<button aria-label={label}>
  {icon}
  <span className="visually-hidden">{label}</span>
</button>
```

### Skip Links

```typescript
export const SkipLink: React.FC = () => {
  return (
    <a href="#main-content" className={styles.skipLink}>
      Skip to main content
    </a>
  );
};

// CSS
/*
.skipLink {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}

.skipLink:focus {
  top: 0;
}
*/
```

## Form Accessibility

### Accessible Form Fields

```typescript
export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  error,
  hint,
  required,
  type = 'text',
  ...inputProps
}) => {
  const id = inputProps.id || `field-${name}`;
  const hintId = `${id}-hint`;
  const errorId = `${id}-error`;

  return (
    <div className={styles.formField}>
      <label htmlFor={id}>
        {label}
        {required && <span aria-label="required"> *</span>}
      </label>

      {hint && (
        <p id={hintId} className={styles.hint}>
          {hint}
        </p>
      )}

      <input
        {...inputProps}
        id={id}
        name={name}
        type={type}
        required={required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={
          [hint && hintId, error && errorId].filter(Boolean).join(' ') || undefined
        }
      />

      {error && (
        <p id={errorId} className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
};
```

### Form Validation

```typescript
export const LoginForm: React.FC = () => {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Validation logic
    const newErrors = validate(formData);
    setErrors(newErrors);

    // Announce errors to screen readers
    if (Object.keys(newErrors).length > 0) {
      // Focus first error field
      const firstErrorField = document.getElementById(
        `field-${Object.keys(newErrors)[0]}`
      );
      firstErrorField?.focus();
    }
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* Error summary for screen readers */}
      {Object.keys(errors).length > 0 && (
        <div role="alert" aria-live="assertive" className={styles.errorSummary}>
          <h2>Please correct the following errors:</h2>
          <ul>
            {Object.entries(errors).map(([field, message]) => (
              <li key={field}>
                <a href={`#field-${field}`}>{message}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <FormField
        label="Email"
        name="email"
        type="email"
        required
        error={touched.email ? errors.email : undefined}
        onBlur={() => setTouched({ ...touched, email: true })}
      />

      <FormField
        label="Password"
        name="password"
        type="password"
        required
        error={touched.password ? errors.password : undefined}
        onBlur={() => setTouched({ ...touched, password: true })}
      />

      <button type="submit">Login</button>
    </form>
  );
};
```

## Color and Contrast

### WCAG Color Contrast Requirements

- **Normal text**: 4.5:1 minimum contrast ratio
- **Large text** (18pt or 14pt bold): 3:1 minimum
- **UI components**: 3:1 minimum

```typescript
// ✅ Good - sufficient contrast
const goodColors = {
  background: '#ffffff',
  text: '#212529', // Contrast ratio: 16.1:1
  primary: '#0066cc', // Contrast ratio: 4.5:1 on white
};

// ❌ Bad - insufficient contrast
const badColors = {
  background: '#ffffff',
  text: '#cccccc', // Contrast ratio: 1.6:1 ❌
  primary: '#66ccff', // Contrast ratio: 2.3:1 ❌
};
```

### Don't Rely on Color Alone

```typescript
// ❌ Bad - color only
<button style={{ color: 'red' }}>Delete</button>

// ✅ Good - color + icon + text
<button className={styles.deleteButton}>
  <TrashIcon aria-hidden="true" />
  Delete
</button>

// ✅ Good - multiple indicators for form validation
<input
  className={error ? styles.inputError : styles.input}
  aria-invalid={!!error}
/>
{error && (
  <span className={styles.error}>
    <ErrorIcon aria-hidden="true" />
    {error}
  </span>
)}
```

## Touch and Click Targets

### Minimum Target Size

WCAG 2.1 Level AAA: 44x44 pixels minimum

```css
/* Ensure sufficient touch target size */
button,
a,
input[type="checkbox"],
input[type="radio"] {
  min-width: 44px;
  min-height: 44px;
}

/* If visual size is smaller, increase click area with padding */
.icon-button {
  width: 24px;
  height: 24px;
  padding: 10px; /* Creates 44x44px touch target */
}
```

## Motion and Animation

### Respect User Preferences

```css
/* Disable animations for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

```typescript
// React hook for reduced motion
export function usePrefersReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

// Usage
export const AnimatedComponent: React.FC = () => {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <motion.div
      animate={{ opacity: 1, y: 0 }}
      initial={{ opacity: 0, y: 20 }}
      transition={{
        duration: prefersReducedMotion ? 0 : 0.3,
      }}
    >
      Content
    </motion.div>
  );
};
```

## Accessibility Testing

### Automated Testing

```typescript
// Jest + jest-axe
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### Screen Reader Testing

```typescript
// React Testing Library - screen reader queries
import { render, screen } from '@testing-library/react';

describe('Modal accessibility', () => {
  it('is properly labeled for screen readers', () => {
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <h2 id="modal-title">Confirm Action</h2>
        <p>Are you sure?</p>
      </Modal>
    );

    // Check dialog role
    const dialog = screen.getByRole('dialog', { name: 'Confirm Action' });
    expect(dialog).toBeInTheDocument();

    // Check modal attribute
    expect(dialog).toHaveAttribute('aria-modal', 'true');
  });

  it('announces dynamic content to screen readers', () => {
    const { rerender } = render(<StatusMessage message="Loading..." />);

    const status = screen.getByRole('status');
    expect(status).toHaveTextContent('Loading...');

    rerender(<StatusMessage message="Success!" />);
    expect(status).toHaveTextContent('Success!');
  });
});
```

### Keyboard Testing

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('Dropdown keyboard navigation', () => {
  it('opens dropdown with Enter key', async () => {
    const user = userEvent.setup();
    render(<Dropdown options={options} />);

    const trigger = screen.getByRole('button');
    await user.keyboard('{Enter}');

    expect(screen.getByRole('listbox')).toBeVisible();
  });

  it('navigates options with arrow keys', async () => {
    const user = userEvent.setup();
    render(<Dropdown options={options} />);

    await user.keyboard('{Enter}'); // Open
    await user.keyboard('{ArrowDown}'); // Move to second option

    const options = screen.getAllByRole('option');
    expect(options[1]).toHaveAttribute('aria-selected', 'true');
  });

  it('closes with Escape key', async () => {
    const user = userEvent.setup();
    render(<Dropdown options={options} />);

    await user.keyboard('{Enter}'); // Open
    await user.keyboard('{Escape}'); // Close

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });
});
```

## Accessibility Checklist

### Component-Level Checklist

- [ ] Semantic HTML elements used
- [ ] ARIA attributes added where needed
- [ ] Keyboard navigation implemented
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Touch targets ≥ 44x44px
- [ ] Screen reader tested
- [ ] Error messages are announced
- [ ] Loading states communicated
- [ ] Motion respects user preferences
- [ ] No keyboard traps
- [ ] Skip links provided (for page-level components)
- [ ] Headings are hierarchical
- [ ] Images have alt text
- [ ] Forms have proper labels and error handling

### Testing Checklist

- [ ] Automated accessibility tests pass (jest-axe)
- [ ] Manual keyboard navigation tested
- [ ] Screen reader tested (NVDA, JAWS, or VoiceOver)
- [ ] Color contrast verified
- [ ] Touch target sizes verified
- [ ] Tested with zoom (200%)
- [ ] Tested in high contrast mode

## Resources

### Tools
- [axe DevTools](https://www.deque.com/axe/devtools/) - Browser extension
- [WAVE](https://wave.webaim.org/) - Web accessibility evaluation tool
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Built into Chrome DevTools
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)

### Guidelines
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

---

**Next Steps:**
- [Testing Strategies](./testing-strategies.md) - Comprehensive testing guide
- [Component Architecture](./component-architecture.md) - Accessible architecture patterns
