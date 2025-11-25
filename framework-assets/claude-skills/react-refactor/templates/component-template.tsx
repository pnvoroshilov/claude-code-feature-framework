/**
 * React Component Template - Clean Architecture Pattern
 *
 * This template demonstrates:
 * - Proper component structure with TypeScript
 * - Separation of concerns (presentational vs container)
 * - Performance optimization with memo
 * - Accessibility best practices
 * - Testing-friendly design
 *
 * Usage:
 * 1. Copy this template
 * 2. Rename ComponentName to your component name
 * 3. Update props interface
 * 4. Implement component logic
 * 5. Add tests
 */

import {
  memo,
  forwardRef,
  useCallback,
  useMemo,
  type ReactNode,
  type HTMLAttributes,
  type ForwardedRef,
} from 'react';
import styles from './ComponentName.module.css';

// ============================================================================
// Types & Interfaces
// ============================================================================

/**
 * Variant options for the component
 * Add your variants here based on design requirements
 */
type ComponentVariant = 'primary' | 'secondary' | 'outline';

/**
 * Size options following design system
 */
type ComponentSize = 'sm' | 'md' | 'lg';

/**
 * Component props interface
 * Extends HTML attributes for native element support
 */
interface ComponentNameProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  /** Content to render inside the component */
  children: ReactNode;

  /** Visual variant of the component */
  variant?: ComponentVariant;

  /** Size of the component */
  size?: ComponentSize;

  /** Whether the component is disabled */
  disabled?: boolean;

  /** Whether the component is in loading state */
  loading?: boolean;

  /** Callback when component is clicked */
  onClick?: () => void;

  /** Optional icon to display */
  icon?: ReactNode;

  /** Position of the icon */
  iconPosition?: 'left' | 'right';

  /** Additional CSS class name */
  className?: string;

  /** Test ID for testing */
  testId?: string;
}

// ============================================================================
// Default Values
// ============================================================================

const defaultProps: Partial<ComponentNameProps> = {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  iconPosition: 'left',
};

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generates CSS classes based on props
 * Pure function for testability
 */
function getClassNames(
  variant: ComponentVariant,
  size: ComponentSize,
  disabled: boolean,
  loading: boolean,
  className?: string
): string {
  const classes = [
    styles.root,
    styles[`variant-${variant}`],
    styles[`size-${size}`],
  ];

  if (disabled) classes.push(styles.disabled);
  if (loading) classes.push(styles.loading);
  if (className) classes.push(className);

  return classes.filter(Boolean).join(' ');
}

// ============================================================================
// Sub-components
// ============================================================================

/**
 * Loading spinner sub-component
 * Extracted for reusability and separation of concerns
 */
function LoadingSpinner() {
  return (
    <span className={styles.spinner} aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" className={styles.spinnerIcon}>
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
          className={styles.spinnerCircle}
        />
        <path
          d="M12 2a10 10 0 0 1 10 10"
          stroke="currentColor"
          strokeWidth="4"
          className={styles.spinnerPath}
        />
      </svg>
    </span>
  );
}

/**
 * Icon wrapper sub-component
 * Handles icon rendering with proper positioning
 */
interface IconWrapperProps {
  icon: ReactNode;
  position: 'left' | 'right';
}

function IconWrapper({ icon, position }: IconWrapperProps) {
  return (
    <span
      className={`${styles.icon} ${styles[`icon-${position}`]}`}
      aria-hidden="true"
    >
      {icon}
    </span>
  );
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * ComponentName - A reusable, accessible React component
 *
 * @example
 * // Basic usage
 * <ComponentName>Hello World</ComponentName>
 *
 * @example
 * // With variants and icon
 * <ComponentName variant="secondary" icon={<Icon />}>
 *   Click me
 * </ComponentName>
 *
 * @example
 * // With forwarded ref
 * const ref = useRef<HTMLDivElement>(null);
 * <ComponentName ref={ref}>Content</ComponentName>
 */
export const ComponentName = memo(
  forwardRef<HTMLDivElement, ComponentNameProps>(function ComponentName(
    props: ComponentNameProps,
    ref: ForwardedRef<HTMLDivElement>
  ) {
    // Merge with defaults
    const {
      children,
      variant = defaultProps.variant!,
      size = defaultProps.size!,
      disabled = defaultProps.disabled!,
      loading = defaultProps.loading!,
      onClick,
      icon,
      iconPosition = defaultProps.iconPosition!,
      className,
      testId,
      ...restProps
    } = props;

    // Memoized class names
    const classNames = useMemo(
      () => getClassNames(variant, size, disabled, loading, className),
      [variant, size, disabled, loading, className]
    );

    // Memoized click handler
    const handleClick = useCallback(() => {
      if (!disabled && !loading && onClick) {
        onClick();
      }
    }, [disabled, loading, onClick]);

    // Memoized keyboard handler for accessibility
    const handleKeyDown = useCallback(
      (event: React.KeyboardEvent<HTMLDivElement>) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          handleClick();
        }
      },
      [handleClick]
    );

    // Computed values
    const isInteractive = !!onClick;
    const ariaDisabled = disabled || loading;

    return (
      <div
        ref={ref}
        className={classNames}
        onClick={handleClick}
        onKeyDown={isInteractive ? handleKeyDown : undefined}
        role={isInteractive ? 'button' : undefined}
        tabIndex={isInteractive && !ariaDisabled ? 0 : undefined}
        aria-disabled={ariaDisabled || undefined}
        aria-busy={loading || undefined}
        data-testid={testId}
        {...restProps}
      >
        {/* Loading state */}
        {loading && <LoadingSpinner />}

        {/* Left icon */}
        {icon && iconPosition === 'left' && !loading && (
          <IconWrapper icon={icon} position="left" />
        )}

        {/* Main content */}
        <span className={styles.content}>{children}</span>

        {/* Right icon */}
        {icon && iconPosition === 'right' && !loading && (
          <IconWrapper icon={icon} position="right" />
        )}
      </div>
    );
  })
);

// ============================================================================
// Display Name (for React DevTools)
// ============================================================================

ComponentName.displayName = 'ComponentName';

// ============================================================================
// Compound Components (Optional)
// ============================================================================

/**
 * Header sub-component for compound pattern
 * Use when component needs multiple composable parts
 */
interface ComponentNameHeaderProps {
  children: ReactNode;
  className?: string;
}

export const ComponentNameHeader = memo<ComponentNameHeaderProps>(
  function ComponentNameHeader({ children, className }) {
    return (
      <div className={`${styles.header} ${className || ''}`}>{children}</div>
    );
  }
);

/**
 * Body sub-component for compound pattern
 */
interface ComponentNameBodyProps {
  children: ReactNode;
  className?: string;
}

export const ComponentNameBody = memo<ComponentNameBodyProps>(
  function ComponentNameBody({ children, className }) {
    return (
      <div className={`${styles.body} ${className || ''}`}>{children}</div>
    );
  }
);

/**
 * Footer sub-component for compound pattern
 */
interface ComponentNameFooterProps {
  children: ReactNode;
  className?: string;
}

export const ComponentNameFooter = memo<ComponentNameFooterProps>(
  function ComponentNameFooter({ children, className }) {
    return (
      <div className={`${styles.footer} ${className || ''}`}>{children}</div>
    );
  }
);

// ============================================================================
// Exports
// ============================================================================

export type { ComponentNameProps, ComponentVariant, ComponentSize };
