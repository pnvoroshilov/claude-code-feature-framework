---
name: architecture-patterns
description: |
  Provides comprehensive guidance on software architecture patterns, design principles, and best practices.
  Use when users mention: SOLID principles, DRY, KISS, clean architecture, domain-driven design, DDD,
  microservices, design patterns, architectural patterns, code structure, software design, refactoring,
  anti-patterns, code quality, separation of concerns, dependency injection, layered architecture.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Architecture Patterns Skill

**Expert guidance on software architecture patterns, design principles, and best practices for building scalable, maintainable systems.**

## Overview

This skill provides comprehensive knowledge of:

skill_capabilities[7]{capability,description,use_case}:
SOLID Principles,Five fundamental OOP design principles,Writing maintainable object-oriented code
DRY & KISS,Don't Repeat Yourself and Keep It Simple Stupid principles,Reducing complexity and duplication
Clean Architecture,Layered architecture with dependency inversion,Organizing code by business rules
Domain-Driven Design,Modeling software based on business domain,Complex business logic implementation
Design Patterns,Common solutions to recurring problems,Factory Singleton Repository Observer patterns
Anti-Patterns,Common mistakes to avoid,Code review and refactoring guidance
Best Practices,Language-specific architectural guidance,Frontend and backend development

## When to Use This Skill

**Trigger Scenarios:**

trigger_scenarios[10]{scenario,skill_application}:
User asks about SOLID,Explain principles with code examples
User mentions refactoring,Identify anti-patterns and suggest improvements
User designs new feature,Recommend appropriate architecture pattern
User asks about code structure,Suggest Clean Architecture or DDD approach
User mentions duplicate code,Apply DRY principle with examples
User over-engineers solution,Recommend KISS principle simplification
User asks about design patterns,Provide pattern examples and use cases
User needs database abstraction,Suggest Repository pattern implementation
User builds microservices,Guide microservices architecture patterns
User reviews code quality,Identify violations and suggest fixes

## Quick Reference

### Fundamental Principles (SOLID)

solid_principles[5]{principle,acronym,rule,benefit}:
Single Responsibility,S,A class should have only one reason to change,Better maintainability and testability
Open/Closed,O,Open for extension closed for modification,Add features without breaking existing code
Liskov Substitution,L,Derived classes must be substitutable for base classes,Proper inheritance hierarchies
Interface Segregation,I,Many specific interfaces better than one general interface,Clients don't depend on unused methods
Dependency Inversion,D,Depend on abstractions not concretions,Loose coupling and easier testing

### Other Core Principles

core_principles[2]{principle,description,application}:
DRY (Don't Repeat Yourself),Every piece of knowledge should have single representation,Extract shared logic into reusable functions
KISS (Keep It Simple Stupid),Simplicity should be key goal in design,Avoid over-engineering and premature optimization

### Architectural Patterns

architectural_patterns[4]{pattern,description,when_to_use}:
Clean Architecture,Organize code by layers with dependency rule,Large applications with complex business logic
Domain-Driven Design (DDD),Model software based on business domain,Complex domains requiring rich domain models
Microservices Architecture,Decompose app into independent services,Scalable systems with team autonomy
Layered Architecture,Separate concerns into presentation business data layers,Traditional enterprise applications

### Common Design Patterns

design_patterns[4]{pattern,type,purpose,example_use_case}:
Singleton,Creational,Ensure class has only one instance,Database connections configuration managers
Factory,Creational,Create objects without specifying exact class,Notification systems plugin architectures
Repository,Structural,Encapsulate data access logic,Database abstraction layer
Observer,Behavioral,Define one-to-many dependency between objects,Event systems state management (React Context)

### Anti-Patterns to Avoid

anti_patterns[6]{anti_pattern,description,impact}:
God Object/God Class,Single class that knows/does too much,Difficult to maintain test and extend
Spaghetti Code,Unstructured tangled control flow,Hard to understand and debug
Magic Numbers/Strings,Hard-coded values without explanation,Unclear intent difficult to change
Premature Optimization,Optimizing before identifying bottlenecks,Wasted effort and complex code
Circular Dependencies,Modules depending on each other,Brittle design difficult refactoring
Tight Coupling,Components highly dependent on each other,Changes cascade hard to test

## Documentation Structure

**Complete documentation is split across multiple files:**

documentation_files[8]{file,content,line_count}:
reference/solid-principles.md,Detailed SOLID principles with examples,~480 lines
reference/other-principles.md,DRY KISS and related principles,~200 lines
reference/clean-architecture.md,Clean Architecture pattern and implementation,~250 lines
reference/domain-driven-design.md,DDD concepts entities aggregates value objects,~280 lines
reference/design-patterns.md,Common design patterns with examples,~350 lines
reference/anti-patterns.md,Anti-patterns and solutions,~320 lines
examples/backend-python.md,Python/FastAPI backend examples,~450 lines
examples/frontend-react.md,React/TypeScript frontend examples,~450 lines

## Usage Workflow

**How to apply this skill effectively:**

usage_steps[8]{step,action,details}:
1. Identify need,Determine which principle or pattern applies,User mentions refactoring design or architecture
2. Read reference,Access appropriate reference documentation,Navigate to specific reference/*.md file
3. Review examples,Study code examples for target language,Check examples/backend-python.md or examples/frontend-react.md
4. Apply pattern,Implement pattern following examples,Use exact syntax and structure from examples
5. Verify quality,Check against anti-patterns list,Ensure no violations in reference/anti-patterns.md
6. Document decision,Record architectural decision rationale,Create ADR if significant architectural choice
7. Review compliance,Validate implementation follows principle,Cross-reference with principles documentation
8. Refactor iteratively,Improve code incrementally,Apply boy scout rule (leave code better than found)

## Language-Specific Guidance

### Backend (Python/FastAPI)

**Recommended patterns:**

backend_patterns[6]{pattern,description,implementation_file}:
Layered Architecture,Controller → Service → Repository → Database,examples/backend-python.md
Dependency Injection,Constructor injection with abstract interfaces,reference/solid-principles.md (DIP)
Repository Pattern,Encapsulate database access logic,reference/design-patterns.md
Service Layer,Business logic separate from controllers,examples/backend-python.md
DTO Pattern,Data Transfer Objects for API boundaries,examples/backend-python.md
Factory Pattern,Create service instances dynamically,reference/design-patterns.md

### Frontend (React/TypeScript)

**Recommended patterns:**

frontend_patterns[6]{pattern,description,implementation_file}:
Component Composition,Compose small focused components,examples/frontend-react.md
Container/Presentational,Separate data fetching from presentation,examples/frontend-react.md
Custom Hooks,Extract reusable stateful logic,examples/frontend-react.md
Context API,Cross-cutting concerns (theme auth),reference/design-patterns.md (Observer)
Dependency Injection,Props injection for API clients,reference/solid-principles.md (DIP)
Single Responsibility,One component one purpose,reference/solid-principles.md (SRP)

## Best Practices Summary

### Backend Architecture Best Practices

backend_best_practices[8]{practice,description}:
Use layered architecture,Controller → Service → Repository → Database separation
Implement dependency injection,Constructor injection with interfaces
Use DTOs for boundaries,Separate API models from domain models
Separate business from infrastructure,Business logic independent of frameworks
Use transaction boundaries correctly,Atomic operations at service layer
Implement proper error handling,Structured exceptions with error codes
Use abstract interfaces,Define contracts with ABC or Protocol
Write integration tests,Test service layer with real database

### Frontend Architecture Best Practices

frontend_best_practices[8]{practice,description}:
Component composition over inheritance,Build complex UIs from simple components
Container/Presentational pattern,Separate concerns data vs presentation
Custom hooks for reusable logic,Extract stateful logic into hooks
Context API for cross-cutting concerns,Theme authentication global state
Proper state management,Choose local vs global state appropriately
Code splitting and lazy loading,Optimize bundle size and load time
Type safety with TypeScript,Leverage interfaces and type checking
Test components in isolation,Unit test presentational components

### General Architecture Guidelines

general_guidelines[8]{guideline,description}:
Write self-documenting code,Clear names that explain intent
Follow consistent naming conventions,Stick to language/framework standards
Keep functions/methods small,Single responsibility under 20 lines
Write tests for business logic,High coverage for critical paths
Use version control effectively,Atomic commits descriptive messages
Document architectural decisions,Create ADRs for significant choices
Regular refactoring,Prevent technical debt accumulation
Code reviews with checklist,Use SOLID principles as review criteria

## Example Scenarios

### Scenario 1: User Asks About SOLID Principles

**Response Pattern:**

1. Read `/reference/solid-principles.md` for detailed explanations
2. Identify which principle(s) apply to user's context
3. Provide relevant code examples (good and bad)
4. Explain benefits and trade-offs
5. Suggest implementation approach

### Scenario 2: User Needs to Refactor God Class

**Response Pattern:**

1. Read `/reference/anti-patterns.md` to identify God Class anti-pattern
2. Read `/reference/solid-principles.md` for SRP guidance
3. Analyze existing code structure
4. Propose split based on responsibilities
5. Show before/after examples from documentation
6. Recommend testing strategy

### Scenario 3: User Designs New Backend API

**Response Pattern:**

1. Read `/reference/clean-architecture.md` for layered approach
2. Read `/examples/backend-python.md` for implementation patterns
3. Suggest Controller → Service → Repository structure
4. Recommend DTOs for API boundaries
5. Apply dependency injection for testability
6. Reference Repository and Factory patterns as needed

### Scenario 4: User Builds React Feature

**Response Pattern:**

1. Read `/examples/frontend-react.md` for component patterns
2. Suggest Component Composition approach
3. Recommend Container/Presentational separation
4. Apply Single Responsibility Principle
5. Extract reusable logic to custom hooks
6. Use Context API for shared state if needed

## Integration with Other Skills

**This skill complements:**

skill_integrations[5]{skill,integration_point,benefit}:
code-review,Use principles as review criteria,Identify violations suggest improvements
refactoring,Apply patterns during refactoring,Systematic improvement approach
testing,Design testable code with DI,Better test coverage and isolation
api-design,Apply layered architecture,Clean API boundaries with DTOs
documentation,Document architectural decisions,Clear rationale for future maintainers

## Quality Checklist

**Before completing architecture work, verify:**

quality_checks[12]{check,requirement,reference}:
Single Responsibility,Each class/component has one reason to change,reference/solid-principles.md
Open/Closed,Can extend without modifying existing code,reference/solid-principles.md
Liskov Substitution,Subtypes are substitutable for base types,reference/solid-principles.md
Interface Segregation,Clients don't depend on unused interfaces,reference/solid-principles.md
Dependency Inversion,Depend on abstractions not concretions,reference/solid-principles.md
No Duplication,Logic not repeated across codebase,reference/other-principles.md
Appropriate Complexity,Solution not over-engineered,reference/other-principles.md
No God Classes,No classes with too many responsibilities,reference/anti-patterns.md
Clear Dependencies,No circular dependencies,reference/anti-patterns.md
Named Constants,No magic numbers or strings,reference/anti-patterns.md
Layered Structure,Clear separation of concerns,reference/clean-architecture.md
Documented Decisions,Significant choices recorded in ADRs,N/A

## Key Principles for Code Quality

### Maintainability

**Code should be easy to understand and modify:**

- Use clear, descriptive names
- Keep functions small and focused
- Minimize dependencies
- Write self-documenting code
- Add comments only for "why" not "what"

### Testability

**Code should be easy to test:**

- Use dependency injection
- Separate business logic from infrastructure
- Avoid static/global state
- Design with interfaces
- Keep side effects isolated

### Scalability

**Code should support growth:**

- Loose coupling between components
- Open for extension
- Modular design
- Clear boundaries
- Proper abstraction levels

### Readability

**Code should be easy to read:**

- Consistent formatting
- Logical organization
- Clear control flow
- Minimal nesting
- Meaningful names

## Additional Resources

**For detailed information, see:**

- `/reference/solid-principles.md` - Complete SOLID principles guide
- `/reference/other-principles.md` - DRY, KISS, and related principles
- `/reference/clean-architecture.md` - Clean Architecture implementation
- `/reference/domain-driven-design.md` - DDD concepts and patterns
- `/reference/design-patterns.md` - Common design patterns
- `/reference/anti-patterns.md` - Anti-patterns to avoid
- `/examples/backend-python.md` - Python/FastAPI examples
- `/examples/frontend-react.md` - React/TypeScript examples

---

**File Size**: 316/500 lines max ✅
**Next Steps**: Review reference and example files for detailed implementations
