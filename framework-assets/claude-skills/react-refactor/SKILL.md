---
name: react-refactor
description: Expert React code refactoring using Clean Architecture component patterns and modern hooks for transforming legacy class components monoliths and prop-drilling nightmares into maintainable composable designs with proper state management TypeScript and testing
version: 1.0.0
tags: [react, refactoring, clean-architecture, hooks, typescript, state-management, component-patterns, performance, testing, nextjs]
---

# React Refactoring Expert

**Comprehensive React refactoring methodology using Clean Architecture, modern component patterns, hooks, and TypeScript for transforming legacy class components and monolithic React applications into maintainable, performant architectures.**

## Overview

This skill provides systematic refactoring techniques for:

skill_capabilities[10]{capability,description,use_case}:
Legacy Component Analysis,Identify component smells and refactoring opportunities,Initial assessment of React codebase
Clean Architecture Implementation,Apply layered architecture to React applications,Organizing monoliths into maintainable structures
Component Pattern Migration,HOC Render Props to Hooks conversion,Modernizing legacy patterns
State Management Refactoring,Context Redux Zustand Jotai implementation,Eliminating prop drilling and global state issues
Performance Optimization,React.memo useMemo useCallback virtualization,Fixing performance bottlenecks
TypeScript Integration,Type-safe component patterns and hooks,Adding type safety to JavaScript codebases
Class to Functional Migration,Convert class components to hooks,Modernizing legacy React code
Testing Strategy,RTL Jest testing patterns for components,Test-driven refactoring approach
Design System Integration,Component library and design token patterns,Creating consistent UI systems
Next.js Clean Architecture,SSR SSG with clean architecture layers,Scalable Next.js applications

## When to Use This Skill

**Trigger Scenarios:**

trigger_scenarios[15]{scenario,skill_application}:
User mentions legacy React code,Assess component architecture and plan refactoring strategy
User has class components,Convert to functional components with hooks
User asks about Clean Architecture in React,Implement layered React architecture with dependency injection
User needs component patterns,Apply HOC Render Props Compound Components Hooks patterns
User has prop drilling issues,Refactor to Context API or state management library
User mentions performance issues,Optimize with memo useMemo useCallback virtualization
User needs state management,Implement Context Redux Zustand or Jotai
User asks about TypeScript in React,Add type-safe patterns and generic components
User has tangled component logic,Extract custom hooks and separate concerns
User needs testing strategy,Implement RTL and Jest patterns
User mentions Next.js,Structure Next.js with clean architecture
User has God components,Break down using SRP and component composition
User needs design system,Create component library with design tokens
User wants incremental refactoring,Apply Strangler Fig with feature flags
User has mixed presentation and logic,Separate into Container Presentation patterns

## Quick Reference

### Core Architectural Principles

architectural_principles[4]{principle,rule,react_implementation}:
The Dependency Rule,Dependencies point inward only - outer layers depend on inner,"Domain → Application → Infrastructure → Presentation, use dependency injection"
Component Layer Independence,Presentation components have minimal dependencies,Pure React components with no business logic
Application Layer Abstraction,Use Cases define interfaces (Ports),Define interfaces in hooks implement in services
Infrastructure Volatility,Infrastructure is replaceable,API clients and storage adapters are implementation details

### Clean Architecture Layers in React

clean_architecture_layers[4]{layer,contents,dependencies,react_modules}:
Domain Layer,Entities Business Rules Types,Zero external dependencies,src/domain/entities src/domain/types src/domain/rules
Application Layer,Custom Hooks Use Cases Ports,Depends only on Domain,src/application/hooks src/application/ports
Infrastructure Layer,API clients Storage Repository implementations,Implements Application ports,src/infrastructure/api src/infrastructure/storage
Presentation Layer,Components Pages Routes,Calls Application hooks,src/presentation/components src/presentation/pages

### Component Pattern Evolution

component_patterns[5]{pattern,use_case,modern_alternative,when_to_use}:
Higher-Order Components,Cross-cutting concerns like auth logging,Custom Hooks,Legacy code only - prefer hooks
Render Props,Sharing stateful logic between components,Custom Hooks,Legacy code only - prefer hooks
Compound Components,Related components working together,Compound with Context and Hooks,Design systems tabs accordions
Container/Presentational,Separate logic from presentation,Custom Hooks + Pure Components,Large components with complex logic
Custom Hooks,Reusable stateful logic,N/A - this is the modern pattern,All new code

### State Management Patterns

state_management[5]{solution,use_case,complexity,when_to_use}:
useState + useContext,Local and shared state across subtree,Low,Small apps limited shared state
React Query + useState,Server state + local UI state,Medium,Apps with lots of API calls
Zustand,Global client state with simple API,Medium,Medium apps needing global state
Jotai,Atomic state management,Medium,Complex state with many dependencies
Redux Toolkit,Large-scale global state with middleware,High,Large apps complex state logic DevTools

### Performance Optimization Patterns

performance_patterns[6]{pattern,problem,solution,implementation}:
React.memo,Component re-renders unnecessarily,Memoize component by props,React.memo(Component propsComparison)
useMemo,Expensive computation on every render,Memoize computed value,useMemo(() => expensive() [deps])
useCallback,Function recreation on every render,Memoize function reference,useCallback(() => handler() [deps])
Code Splitting,Large bundle size,Dynamic imports and lazy loading,React.lazy(() => import('./Component'))
Virtualization,Long lists causing performance issues,Render only visible items,react-window or react-virtual
State Colocation,State causing unnecessary re-renders,Move state close to usage,useState in specific component not root

## Documentation Structure

**Complete refactoring methodology split across multiple files:**

documentation_files[7]{file,content,line_count}:
reference/clean-architecture.md,Clean Architecture layers for React applications,~470 lines
reference/component-patterns.md,HOC Render Props Compound Components Hooks patterns,~460 lines
reference/state-management.md,Context Redux Zustand Jotai implementation patterns,~480 lines
reference/performance.md,React.memo useMemo useCallback virtualization patterns,~450 lines
reference/testing-patterns.md,RTL Jest component testing strategies,~440 lines
examples/legacy-migration.md,Class to functional component migration examples,~490 lines
examples/nextjs-clean-arch.md,Next.js application with Clean Architecture,~480 lines

## Usage Workflow

**Systematic approach to refactoring React codebases:**

refactoring_workflow[8]{step,action,reference_file}:
1. Assess Current State,Analyze component architecture identify smells,reference/clean-architecture.md
2. Plan Strategy,Choose refactoring approach (Strangler Fig vs full rewrite),examples/legacy-migration.md
3. Extract Domain Logic,Move business rules to domain layer,reference/clean-architecture.md
4. Modernize Patterns,Convert HOC/Render Props to Hooks,reference/component-patterns.md
5. Refactor State Management,Implement Context/Zustand/Redux properly,reference/state-management.md
6. Optimize Performance,Apply memo useMemo useCallback,reference/performance.md
7. Add TypeScript,Incrementally add type safety,reference/component-patterns.md
8. Establish Testing,Create RTL test suite,reference/testing-patterns.md

## Refactoring Process - Step by Step

### Phase 1: Diagnosis and Planning

diagnosis_steps[6]{step,action,deliverable}:
1. Map Component Tree,Identify component hierarchy and data flow,Component tree diagram
2. Identify Business Logic,Find business rules scattered in components,Business logic inventory
3. Analyze State Flow,Map state and prop drilling patterns,State flow diagram
4. Assess Technical Debt,Identify code smells anti-patterns issues,Technical debt backlog
5. Define Target Architecture,Design Clean Architecture structure,Architecture diagram
6. Plan Migration Strategy,Choose Strangler Fig or Big Bang approach,Migration roadmap

### Phase 2: Domain Layer Extraction

domain_extraction[5]{step,action,reference}:
1. Extract Types,Create TypeScript types for domain entities,reference/clean-architecture.md
2. Extract Business Rules,Move validation and business logic to domain,reference/clean-architecture.md
3. Define Value Objects,Create immutable domain value types,reference/clean-architecture.md
4. Create Domain Events,Model state changes as events,reference/clean-architecture.md
5. Establish Boundaries,Define bounded contexts and modules,reference/clean-architecture.md

### Phase 3: Application Layer Design

application_layer_steps[4]{step,action,reference}:
1. Create Custom Hooks,Extract stateful logic to custom hooks,reference/component-patterns.md
2. Define Port Interfaces,Create TypeScript interfaces for services,reference/clean-architecture.md
3. Implement Use Cases,Move use case logic to application hooks,examples/nextjs-clean-arch.md
4. Handle State Management,Setup Context Zustand or Redux,reference/state-management.md

### Phase 4: Infrastructure Implementation

infrastructure_steps[5]{step,action,reference}:
1. Implement API Clients,Create service implementations,reference/clean-architecture.md
2. Setup Storage Adapters,Implement localStorage sessionStorage adapters,reference/clean-architecture.md
3. Configure HTTP Client,Setup axios or fetch with interceptors,examples/nextjs-clean-arch.md
4. Create Repository Implementations,Build data access layer,reference/clean-architecture.md
5. Setup Dependency Injection,Configure DI container or context,reference/clean-architecture.md

### Phase 5: Presentation Layer

presentation_steps[4]{step,action,reference}:
1. Create Presentational Components,Pure components with no business logic,reference/component-patterns.md
2. Implement Container Patterns,Connect components to application hooks,reference/component-patterns.md
3. Add Type Safety,TypeScript props and generics,reference/component-patterns.md
4. Optimize Performance,Apply memo and virtualization,reference/performance.md

### Phase 6: Testing Strategy

testing_strategy[3]{test_type,coverage_target,focus}:
Unit Tests,70% of test suite,Custom hooks and business logic with mocked dependencies
Integration Tests,20% of test suite,Components with hooks and API integration
E2E Tests,10% of test suite,Critical user flows with Playwright or Cypress

## Key Refactoring Patterns

### Pattern 1: Class to Functional Component Migration

**Problem**: Legacy class components with lifecycle methods
**Solution**: Convert to functional components with hooks

```tsx
// ❌ BEFORE: Class component
class UserProfile extends React.Component {
  state = { user: null, loading: true };

  componentDidMount() {
    this.fetchUser();
  }

  fetchUser = async () => {
    const user = await api.getUser(this.props.userId);
    this.setState({ user, loading: false });
  };

  render() {
    if (this.state.loading) return <Spinner />;
    return <div>{this.state.user.name}</div>;
  }
}

// ✅ AFTER: Functional component with hooks
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await api.getUser(userId);
      setUser(user);
      setLoading(false);
    };
    fetchUser();
  }, [userId]);

  if (loading) return <Spinner />;
  return <div>{user?.name}</div>;
}
```

**Reference**: `examples/legacy-migration.md`

### Pattern 2: Extract Custom Hook

**Problem**: Complex stateful logic mixed with UI
**Solution**: Extract to reusable custom hook

```tsx
// ✅ Custom hook extraction
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchUser = async () => {
      try {
        setLoading(true);
        const user = await api.getUser(userId);
        if (!cancelled) {
          setUser(user);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchUser();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { user, loading, error };
}

// Component becomes simple
function UserProfile({ userId }: { userId: string }) {
  const { user, loading, error } = useUser(userId);

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{user?.name}</div>;
}
```

**Reference**: `reference/component-patterns.md`

### Pattern 3: State Management with Context

**Problem**: Prop drilling through multiple levels
**Solution**: Context API with custom hook

```tsx
// ✅ Context pattern
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await api.login(credentials);
    setUser(user);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

**Reference**: `reference/state-management.md`

### Pattern 4: Performance Optimization

**Problem**: Unnecessary re-renders causing performance issues
**Solution**: React.memo, useMemo, useCallback

```tsx
// ✅ Optimized component
interface ListItemProps {
  item: Item;
  onSelect: (id: string) => void;
}

const ListItem = React.memo<ListItemProps>(({ item, onSelect }) => {
  const handleClick = useCallback(() => {
    onSelect(item.id);
  }, [item.id, onSelect]);

  return (
    <div onClick={handleClick}>
      {item.name}
    </div>
  );
});

function ItemList({ items }: { items: Item[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Memoize callback to prevent ListItem re-renders
  const handleSelect = useCallback((id: string) => {
    setSelectedId(id);
  }, []);

  // Memoize filtered items
  const activeItems = useMemo(
    () => items.filter(item => item.active),
    [items]
  );

  return (
    <div>
      {activeItems.map(item => (
        <ListItem key={item.id} item={item} onSelect={handleSelect} />
      ))}
    </div>
  );
}
```

**Reference**: `reference/performance.md`

## Common Refactoring Scenarios

### Scenario 1: Refactor God Component

**Before**: 800-line component handling everything

**Approach**:
1. Identify responsibilities (data fetching, validation, rendering)
2. Extract custom hooks for each responsibility
3. Create smaller presentational components
4. Use composition instead of props

**Reference**: `examples/legacy-migration.md` (God Component Refactoring section)

### Scenario 2: Eliminate Prop Drilling

**Before**: Props passed through 5+ component levels

**Approach**:
1. Identify truly global state
2. Create Context for shared state
3. Extract custom hook for context access
4. Colocate state when possible

**Reference**: `reference/state-management.md` (Context Patterns section)

### Scenario 3: Migrate HOC to Hooks

**Before**: withAuth, withLoading HOCs wrapping components

**Approach**:
1. Create custom hooks (useAuth, useLoading)
2. Replace HOC usage with hooks in components
3. Remove HOC implementations
4. Add TypeScript types

**Reference**: `reference/component-patterns.md` (HOC to Hooks Migration)

### Scenario 4: Add TypeScript Incrementally

**Before**: Large JavaScript React codebase

**Approach**:
1. Setup TypeScript configuration
2. Rename .jsx to .tsx gradually
3. Add types starting from leaf components
4. Use type inference where possible
5. Create shared type definitions

**Reference**: `reference/component-patterns.md` (TypeScript Integration)

## Testing Strategy for Refactored Code

### Unit Tests (Hooks + Components)

unit_test_focus[5]{what_to_test,approach,tools}:
Custom Hooks,Test hook logic with renderHook,React Testing Library hooks
Pure Components,Test rendering with different props,RTL render and queries
Business Logic,Test domain rules in isolation,Jest with no React
Utility Functions,Test pure functions,Jest unit tests
Type Safety,Test TypeScript types,tsd or expect-type

### Integration Tests (Components + Hooks)

integration_test_focus[4]{what_to_test,approach,tools}:
Component Integration,Test components with real hooks,RTL with MSW for API mocking
State Management,Test context providers and stores,RTL with provider wrappers
API Integration,Test components with API calls,MSW (Mock Service Worker)
Routing,Test navigation and route changes,React Router with RTL

### E2E Tests (Full Stack)

e2e_test_focus[3]{what_to_test,approach,tools}:
Critical User Journeys,Test complete workflows,Playwright or Cypress
Form Submissions,Test full form flows with validation,Playwright with real backend
Authentication Flows,Test login logout protected routes,Playwright with test users

## Quality Checklist

**Before completing refactoring work, verify:**

refactoring_quality[12]{check,requirement,reference}:
Domain Independence,Domain layer has zero React dependencies,reference/clean-architecture.md
Dependency Rule,Dependencies point inward only,reference/clean-architecture.md
Hook Extraction,Complex logic extracted to custom hooks,reference/component-patterns.md
No Prop Drilling,Deep prop passing eliminated,reference/state-management.md
Type Safety,All components and hooks have TypeScript types,reference/component-patterns.md
Performance Optimized,memo useMemo useCallback applied correctly,reference/performance.md
Pure Components,Presentational components are pure,reference/component-patterns.md
Test Coverage,70% coverage with RTL,reference/testing-patterns.md
No God Components,Single Responsibility applied,examples/legacy-migration.md
Accessibility,ARIA labels and semantic HTML,reference/testing-patterns.md
Error Boundaries,Error handling at appropriate levels,reference/clean-architecture.md
Code Splitting,Routes and heavy components lazy loaded,reference/performance.md

## Integration with Other Skills

**This skill complements:**

skill_integrations[6]{skill,integration_point,workflow}:
architecture-patterns,Apply SOLID and Clean Architecture to React,Use architecture-patterns for principles react-refactor for implementation
code-review,Review refactored React code against principles,Check component patterns and architecture boundaries
testing,Implement test pyramid for React components,Unit tests for hooks integration for components
api-development,Structure API clients in infrastructure layer,Use react-refactor for frontend architecture
typescript,Add comprehensive type safety,Combine TypeScript skill with React patterns
design-systems,Create component library with tokens,Use react-refactor for component architecture

## Success Criteria

**Effective React refactoring achieves:**

success_criteria[10]{criterion,indicator}:
Clear Layer Separation,Domain Application Infrastructure Presentation are distinct
Dependency Direction,All dependencies point inward toward domain
Testability,Can unit test hooks without rendering components
Framework Independence,Business logic independent of React
Type Safety,TypeScript with no any types in core code
Component Reusability,Presentational components highly reusable
Hook Composition,Custom hooks composable and focused
Performance,No unnecessary re-renders or computations
State Management,Clear state ownership and flow
No Regressions,Existing functionality preserved through refactoring

## Quick Start Guide

### Starting a React Refactoring Project

quick_start[6]{step,action,reference_file}:
1. Read Clean Architecture,Understand layers for React,reference/clean-architecture.md
2. Read Component Patterns,Learn modern React patterns,reference/component-patterns.md
3. Study Migration Example,See class to functional conversion,examples/legacy-migration.md
4. Review State Management,Choose appropriate state solution,reference/state-management.md
5. Read Performance Guide,Learn optimization techniques,reference/performance.md
6. Setup Testing,Establish RTL test patterns,reference/testing-patterns.md

## Additional Resources

**For detailed implementation guidance, see:**

- `reference/clean-architecture.md` - Complete Clean Architecture for React
- `reference/component-patterns.md` - HOC Render Props Compound Hooks patterns
- `reference/state-management.md` - Context Redux Zustand Jotai implementations
- `reference/performance.md` - Optimization with memo useMemo useCallback
- `reference/testing-patterns.md` - RTL and Jest testing strategies
- `examples/legacy-migration.md` - Complete class to functional migration
- `examples/nextjs-clean-arch.md` - Next.js with Clean Architecture
- `templates/component-template.tsx` - React component template
- `templates/hook-template.tsx` - Custom hook template
- `templates/context-template.tsx` - Context provider template

---

**File Size**: 467/500 lines max ✅
**Next Steps**: Review reference and example files for detailed implementations
