---
name: refactoring
description: Expert code refactoring and cleanup for maintainability, performance, and code quality improvement
version: 1.0.0
tags: [refactoring, code-quality, clean-code, maintainability, performance, technical-debt]
---

# Code Refactoring Skill

Comprehensive code refactoring expertise that transforms legacy code, reduces technical debt, improves maintainability, and enhances performance while preserving functionality. Master the art of systematic code improvement through proven refactoring patterns, techniques, and workflows.

## Core Philosophy

**Refactoring is disciplined code improvement**: Make code better without changing its external behavior. Every refactoring should be:
- **Safe**: Preserves existing functionality
- **Incremental**: Small, testable steps
- **Reversible**: Can undo if needed
- **Testable**: Verified by automated tests
- **Purposeful**: Solves a real problem

## Core Capabilities

This skill provides expert-level refactoring knowledge including:

### Code Improvement Techniques
- **Extract Method/Function**: Break down large functions into smaller, focused units
- **Rename Variables/Functions**: Improve code readability through better naming
- **Simplify Conditionals**: Reduce complexity in if/else chains and boolean logic
- **Remove Duplication**: Apply DRY principle to eliminate code repetition
- **Improve Data Structures**: Choose appropriate collections and structures
- **Optimize Algorithms**: Replace inefficient approaches with better solutions

### Structural Refactoring
- **Modularization**: Break monolithic code into cohesive modules
- **Dependency Management**: Reduce coupling, increase cohesion
- **Interface Extraction**: Define clean contracts between components
- **Class Decomposition**: Split god objects into focused classes
- **Package Reorganization**: Create logical namespace hierarchies
- **Architecture Migration**: Gradual transition to better architectures

### Pattern Application
- **Design Pattern Implementation**: Apply Gang of Four patterns appropriately
- **Anti-Pattern Elimination**: Identify and remove code smells
- **Code Smell Detection**: Recognize problematic patterns early
- **Refactoring Catalog**: Apply proven refactoring recipes
- **Pattern Refactoring**: Convert between different design patterns

### Performance Optimization
- **Algorithm Optimization**: Improve time/space complexity
- **Database Query Optimization**: Reduce N+1 queries, add indexes
- **Caching Strategies**: Memoization, Redis, CDN integration
- **Memory Management**: Reduce allocations, fix leaks
- **Lazy Loading**: Defer expensive operations
- **Parallel Processing**: Introduce concurrency where beneficial

### Technical Debt Reduction
- **Legacy Code Modernization**: Update outdated codebases
- **Dead Code Elimination**: Remove unused code safely
- **Deprecated API Migration**: Update to modern APIs
- **Dependency Updates**: Upgrade libraries safely
- **Configuration Externalization**: Move hardcoded values to config
- **Documentation Improvement**: Add/update code documentation

### Testing & Quality
- **Test Coverage Improvement**: Add tests before refactoring
- **Characterization Tests**: Understand legacy behavior
- **Test Refactoring**: Improve test quality and maintainability
- **Code Quality Metrics**: Measure and improve cyclomatic complexity
- **Static Analysis**: Use linters and analyzers effectively

## Quick Start

### Basic Refactoring Workflow

```markdown
Refactoring Checklist:
- [ ] 1. Ensure comprehensive test coverage exists
- [ ] 2. Identify code smell or improvement opportunity
- [ ] 3. Plan small, incremental refactoring steps
- [ ] 4. Execute one refactoring at a time
- [ ] 5. Run tests after each change
- [ ] 6. Commit after successful refactoring
- [ ] 7. Repeat until code meets quality standards
```

### Simple Example: Extract Method

**Before:**
```python
def process_order(order):
    # Validate order
    if not order.customer_id:
        raise ValueError("Customer ID required")
    if not order.items:
        raise ValueError("Order must have items")
    if order.total < 0:
        raise ValueError("Total must be positive")

    # Calculate discounts
    discount = 0
    if order.total > 1000:
        discount = order.total * 0.1
    elif order.total > 500:
        discount = order.total * 0.05

    # Apply discount
    final_total = order.total - discount

    # Save order
    db.save(order)

    return final_total
```

**After:**
```python
def process_order(order):
    validate_order(order)
    discount = calculate_discount(order.total)
    final_total = order.total - discount
    save_order(order)
    return final_total

def validate_order(order):
    if not order.customer_id:
        raise ValueError("Customer ID required")
    if not order.items:
        raise ValueError("Order must have items")
    if order.total < 0:
        raise ValueError("Total must be positive")

def calculate_discount(total):
    if total > 1000:
        return total * 0.1
    elif total > 500:
        return total * 0.05
    return 0

def save_order(order):
    db.save(order)
```

**Benefits**: Improved readability, testability, reusability, and single responsibility.

## Documentation

### In-Depth Guides
- **[Core Concepts](docs/core-concepts.md)** - Fundamental refactoring principles, when and why to refactor
- **[Best Practices](docs/best-practices.md)** - Industry-standard refactoring guidelines and workflows
- **[Refactoring Patterns](docs/patterns.md)** - Complete catalog of refactoring techniques with examples
- **[Advanced Topics](docs/advanced-topics.md)** - Large-scale refactoring, architecture migration, legacy code
- **[Scalability Patterns](docs/scalability-patterns.md)** - Caching, pagination, high load, high availability patterns
- **[Troubleshooting](docs/troubleshooting.md)** - Common refactoring problems and solutions
- **[Tool Reference](docs/api-reference.md)** - IDE refactoring tools, static analyzers, automation

## Examples

### Basic Examples
Start with fundamental refactoring techniques:
- **[Extract Method Pattern](examples/basic/extract-method.md)** - Break down long functions into focused methods
- **[Rename for Clarity](examples/basic/rename-for-clarity.md)** - Improve code readability through better naming
- **[Simplify Conditionals](examples/basic/simplify-conditionals.md)** - Reduce complexity in boolean logic

### Intermediate Examples
Apply more advanced refactoring patterns:
- **[Remove Duplication](examples/intermediate/remove-duplication.md)** - DRY principle implementation across codebase
- **[Replace Magic Numbers](examples/intermediate/replace-magic-numbers.md)** - Use named constants for better maintainability
- **[Introduce Parameter Object](examples/intermediate/parameter-object.md)** - Group related parameters into cohesive objects

### Advanced Examples
Master complex refactoring scenarios:
- **[Decompose God Class](examples/advanced/decompose-god-class.md)** - Split large classes into focused components
- **[Strangler Fig Pattern](examples/advanced/strangler-fig-pattern.md)** - Gradually migrate legacy systems
- **[Performance Refactoring](examples/advanced/performance-refactoring.md)** - Optimize algorithms and data structures

## Templates

Ready-to-use refactoring templates:
- **[Basic Cleanup Template](templates/basic-cleanup.md)** - Standard code cleanup checklist and workflow
- **[Performance Optimization Template](templates/performance-optimization.md)** - Systematic performance improvement process
- **[Legacy Modernization Template](templates/legacy-modernization.md)** - Step-by-step legacy code migration

## Resources

Additional reference materials:
- **[Refactoring Checklists](resources/checklists.md)** - Pre-refactoring, during, and post-refactoring checklists
- **[Code Smells Glossary](resources/glossary.md)** - Complete guide to code smells and anti-patterns
- **[External References](resources/references.md)** - Books, articles, tools, and learning resources
- **[Refactoring Workflows](resources/workflows.md)** - Step-by-step processes for different scenarios

## Usage Examples

### Example 1: Simple Function Refactoring

**Scenario**: Long method doing too many things

**Approach**:
1. Identify distinct responsibilities in the method
2. Extract each responsibility into separate function
3. Give functions intention-revealing names
4. Verify tests still pass
5. Remove temporary variables where possible

**Result**: Smaller, focused functions that are easier to test and maintain

### Example 2: Class-Level Refactoring

**Scenario**: God class with 1000+ lines and 50+ methods

**Approach**:
1. Group related methods and fields
2. Extract cohesive groups into new classes
3. Use composition to connect new classes
4. Maintain original interface for backward compatibility
5. Gradually migrate callers to new structure

**Result**: Multiple focused classes with clear responsibilities

### Example 3: Removing Code Duplication

**Scenario**: Same logic repeated in 5 different places

**Approach**:
1. Identify the duplicated code pattern
2. Extract to shared function/method
3. Parameterize variations
4. Replace all duplicates with function calls
5. Add tests for the extracted function

**Result**: Single source of truth, easier maintenance

### Example 4: Simplifying Complex Conditionals

**Scenario**: Nested if/else statements 6 levels deep

**Approach**:
1. Extract boolean expressions to named methods
2. Use guard clauses for early returns
3. Replace nested conditionals with polymorphism
4. Use strategy pattern for complex branching
5. Apply lookup tables for switch statements

**Result**: Linear, readable code flow

### Example 5: Performance Optimization

**Scenario**: Application slow due to N+1 queries

**Approach**:
1. Profile to identify bottleneck
2. Analyze database query patterns
3. Add eager loading/batch fetching
4. Implement caching layer
5. Measure performance improvement

**Result**: 10x-100x performance increase

### Example 6: Modernizing Legacy Code

**Scenario**: 10-year-old codebase needs update

**Approach**:
1. Add characterization tests
2. Update dependencies incrementally
3. Apply modern language features
4. Refactor to current patterns
5. Improve documentation

**Result**: Modern, maintainable codebase

## When to Use This Skill

### Perfect for:
- **Code Reviews**: Identify improvements during PR review
- **Technical Debt Sprints**: Dedicated refactoring work
- **Performance Issues**: Optimize slow code paths
- **Before New Features**: Clean up area before adding features
- **Legacy Maintenance**: Improve old codebases
- **Test Addition**: Restructure for testability
- **Onboarding**: Make code clearer for new developers

### Not Ideal for:
- **Tight Deadlines**: Refactoring needs time and tests
- **Unstable Code**: Need tests first
- **Unclear Requirements**: Understand the domain first
- **Broken Features**: Fix bugs before refactoring
- **New Greenfield Projects**: Write clean code from start

## Refactoring Principles

### The Rule of Three
First time: just write it. Second time: notice duplication. Third time: refactor.

### Boy Scout Rule
Leave code cleaner than you found it. Small improvements compound.

### Red-Green-Refactor
TDD cycle: failing test → passing test → refactor. Always refactor after green.

### Two Hats
Wear one hat at a time: either adding features OR refactoring. Never both simultaneously.

### Baby Steps
Small, safe changes. Run tests frequently. Commit working code often.

### Preparatory Refactoring
Make change easy, then make easy change. Refactor before adding features.

## Code Quality Metrics

### What to Measure
- **Cyclomatic Complexity**: Aim for < 10 per function
- **Lines of Code**: Functions < 50 lines, classes < 300 lines
- **Code Coverage**: Aim for 80%+ test coverage
- **Duplication**: < 3% duplicated code
- **Coupling**: Measure dependencies between modules
- **Cohesion**: How focused each module is

### How to Improve
- Break down complex functions
- Extract classes and modules
- Add missing tests
- Remove duplication
- Reduce dependencies
- Improve naming

## Common Refactoring Operations

### Method-Level
- Extract Method
- Inline Method
- Rename Method
- Add Parameter
- Remove Parameter
- Replace Temp with Query

### Class-Level
- Extract Class
- Inline Class
- Extract Interface
- Move Method/Field
- Replace Inheritance with Delegation
- Replace Delegation with Inheritance

### Data-Level
- Rename Variable
- Replace Magic Number with Constant
- Introduce Parameter Object
- Replace Array with Object
- Encapsulate Field

### Conditional-Level
- Decompose Conditional
- Consolidate Conditional Expression
- Replace Nested Conditional with Guard Clauses
- Replace Conditional with Polymorphism

### API-Level
- Separate Query from Modifier
- Parameterize Method
- Replace Parameter with Method Call
- Introduce Gateway
- Replace Error Code with Exception

## Progressive Refactoring Strategy

### Level 1: Quick Wins (1-2 hours)
- Fix obvious naming issues
- Remove commented code
- Format code consistently
- Add missing null checks
- Fix simple duplication

### Level 2: Medium Refactoring (1-2 days)
- Extract methods from long functions
- Simplify complex conditionals
- Introduce constants for magic numbers
- Add missing documentation
- Improve error handling

### Level 3: Deep Refactoring (1-2 weeks)
- Decompose god classes
- Introduce design patterns
- Restructure module boundaries
- Migrate to better architecture
- Comprehensive test coverage

### Level 4: System Refactoring (1-3 months)
- Architecture migration
- Technology stack upgrades
- Database schema evolution
- API versioning and migration
- Performance optimization at scale

## Integration with Development Workflow

### During Feature Development
1. **Before**: Preparatory refactoring to make feature easier
2. **During**: Keep production code clean while adding feature
3. **After**: Cleanup refactoring to improve final implementation

### During Bug Fixes
1. **Understand**: Add characterization tests
2. **Simplify**: Refactor to make bug obvious
3. **Fix**: Correct the issue
4. **Verify**: Ensure tests pass
5. **Cleanup**: Improve surrounding code

### During Code Review
1. **Review**: Identify improvement opportunities
2. **Prioritize**: Critical vs nice-to-have changes
3. **Apply**: Make changes before merge
4. **Document**: Explain refactoring decisions

## Safety Guidelines

### Always Before Refactoring
- ✅ Have comprehensive test coverage
- ✅ Understand what code does
- ✅ Version control with clean working directory
- ✅ One refactoring at a time
- ✅ Tests pass before starting

### Never During Refactoring
- ❌ Mix refactoring with feature changes
- ❌ Refactor without tests
- ❌ Change external behavior
- ❌ Make large, sweeping changes
- ❌ Ignore failing tests

### After Each Refactoring
- ✅ Run full test suite
- ✅ Verify performance unchanged
- ✅ Check for regressions
- ✅ Commit working code
- ✅ Update documentation if needed

## Language-Specific Considerations

### Python
- Use type hints for clarity
- Apply list/dict comprehensions
- Leverage context managers
- Follow PEP 8 style guide
- Use dataclasses for data objects

### JavaScript/TypeScript
- Use arrow functions appropriately
- Apply destructuring
- Leverage async/await
- Use const/let instead of var
- Apply functional programming patterns

### Java
- Use streams for collections
- Apply Optional for null safety
- Leverage interfaces and abstractions
- Follow SOLID principles
- Use modern Java features (records, switch expressions)

### C#
- Use LINQ for queries
- Apply async/await
- Leverage properties
- Use nullable reference types
- Follow .NET conventions

### Go
- Keep interfaces small
- Use composition over inheritance
- Apply defer for cleanup
- Follow effective Go guidelines
- Use goroutines appropriately

## Success Metrics

### Before/After Comparison
- Lines of code reduced by X%
- Cyclomatic complexity reduced by Y%
- Test coverage increased to Z%
- Duplication reduced from A% to B%
- Build time reduced by C seconds

### Long-Term Benefits
- Fewer bugs introduced
- Faster feature development
- Easier onboarding
- Better developer satisfaction
- Lower maintenance costs

## Limitations

This skill provides refactoring guidance but does **not**:
- Replace the need for comprehensive tests
- Guarantee perfect code (trade-offs exist)
- Make architectural decisions for you
- Automatically refactor code (you must apply)
- Fix business logic errors
- Replace domain expertise

## Related Skills

Works best in combination with:
- `testing`: Add tests before refactoring
- `code-review`: Identify refactoring opportunities
- `performance-optimization`: Optimize after refactoring
- `architecture-design`: Plan large refactorings
- `technical-debt-management`: Prioritize refactoring work

## Getting Started

1. **Read** [Core Concepts](docs/core-concepts.md) to understand refactoring fundamentals
2. **Study** [Best Practices](docs/best-practices.md) for safe refactoring workflows
3. **Browse** [Patterns Catalog](docs/patterns.md) for specific refactoring techniques
4. **Try** [Basic Examples](examples/basic/) to practice fundamental techniques
5. **Apply** [Templates](templates/) to your own refactoring work
6. **Reference** [Checklists](resources/checklists.md) during refactoring sessions

## Quick Reference

### Top 10 Most Common Refactorings
1. Extract Method - Break down long functions
2. Rename - Improve naming throughout
3. Extract Variable - Name intermediate results
4. Inline - Remove unnecessary indirection
5. Move - Relocate code to better location
6. Pull Up - Move to superclass
7. Push Down - Move to subclass
8. Extract Class - Split responsibilities
9. Introduce Parameter Object - Group parameters
10. Replace Conditional with Polymorphism - Eliminate type checking

### Top 10 Code Smells to Fix
1. Long Method - Functions > 50 lines
2. Large Class - Classes > 300 lines
3. Duplicate Code - Same logic repeated
4. Long Parameter List - > 3-4 parameters
5. Divergent Change - Class changes for multiple reasons
6. Shotgun Surgery - Change requires many small edits
7. Feature Envy - Method uses another class more than its own
8. Data Clumps - Same group of data appears together
9. Primitive Obsession - Using primitives instead of objects
10. Switch Statements - Type-checking instead of polymorphism

## Version History

- **1.0.0** (2025-01-31): Initial release
  - Complete refactoring pattern catalog
  - Comprehensive examples and templates
  - Best practices and workflows
  - Code smell detection guide
  - Tool reference and automation
