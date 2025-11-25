# Unit Testing Language-Specific Examples

Comprehensive code examples for unit testing across different programming languages and frameworks.

## Available Examples

This directory contains detailed, production-ready examples for:

### Python (pytest)
**File**: [python-pytest.md](python-pytest.md)

python_examples[11]{category,description}:
Basic Tests,Test classes with fixtures and AAA pattern
Parametrized Tests,Using @pytest.mark.parametrize for data-driven tests
Mocking,Mock objects unittest.mock for dependencies
Async Testing,Testing async/await code with @pytest.mark.asyncio
Temp Files,Using tmp_path fixture for file operations
Advanced Fixtures,Scope management session module function fixtures
Markers,Test categorization with @pytest.mark custom markers
Builders,Test data builder pattern for complex objects
Exceptions,Testing error conditions with pytest.raises
Property Testing,Property-based testing with Hypothesis library
Monkeypatching,Runtime patching with monkeypatch fixture

### JavaScript (Jest)
**File**: [javascript-jest.md](javascript-jest.md)

javascript_examples[11]{category,description}:
Basic Tests,Describe blocks beforeEach afterEach setup
Parametrized Tests,Using test.each for data-driven tests
Mocking,jest.mock for modules and jest.fn for functions
Async Testing,Testing Promises and async/await code
Snapshot Testing,Component snapshot testing with Jest
Timers,Testing setTimeout setInterval with fake timers
Spies,jest.spyOn for tracking function calls
Custom Matchers,Extending Jest with custom assertions
Error Handling,Testing error boundaries and exception handling
Builders,Test data builder pattern for objects
DOM Testing,Testing DOM manipulation and events

### TypeScript (Vitest)
**File**: [typescript-vitest.md](typescript-vitest.md)

typescript_examples[11]{category,description}:
Type Safety,Fully typed tests with TypeScript
Generics,Testing generic classes and functions
Mocking,Type-safe mocks with vi.mocked
Async Testing,Typed async/await testing patterns
Inheritance,Testing class hierarchies and inheritance
Type Guards,Testing runtime type checking functions
Enums and Unions,Testing TypeScript enums and union types
Interfaces,Interface-based testing for loose coupling
Decorators,Testing TypeScript decorators
Branded Types,Testing nominal types for domain safety
Utility Types,Testing with Pick Omit Partial Required

## Cross-Language Patterns

Common patterns demonstrated across all languages:

### Builder Pattern
Create complex test data objects with fluent interfaces:

```
UserBuilder()
    .withEmail("test@example.com")
    .withRole("admin")
    .asVerified()
    .build()
```

**See**: All three language files contain builder examples

### AAA Pattern
Every test follows Arrange-Act-Assert structure:

```
// Arrange - Setup test data
const user = createUser();

// Act - Execute the behavior
const result = user.login();

// Assert - Verify outcomes
expect(result).toBe(true);
```

**See**: All test examples follow this pattern

### Custom Matchers/Assertions
Extend testing framework with domain-specific assertions:

**Python**: Custom fixtures in conftest.py
**JavaScript**: expect.extend() with custom matchers
**TypeScript**: Type-safe custom matchers with Vitest

**See**:
- python-pytest.md - Custom fixtures section
- javascript-jest.md - Custom matchers section
- typescript-vitest.md - Type-safe assertions

### Mocking External Dependencies
Mock only external boundaries, not internal code:

**Python**: unittest.mock.Mock and @patch decorator
**JavaScript**: jest.mock() and jest.fn()
**TypeScript**: vi.mock() and vi.fn() with types

**See**:
- python-pytest.md - Mocking section
- javascript-jest.md - Mocking modules section
- typescript-vitest.md - Type-safe mocking section

## Example Selection Guide

example_selection[6]{scenario,recommended_file,why}:
Python web API testing,python-pytest.md,Fixtures for DB and async support
React/Vue component testing,javascript-jest.md,Snapshot testing and DOM utilities
Node.js backend services,javascript-jest.md,Async patterns and module mocking
TypeScript libraries,typescript-vitest.md,Full type safety and generics
CLI tools Python,python-pytest.md,Temp file testing and monkeypatching
Enterprise TypeScript apps,typescript-vitest.md,Interface testing and branded types

## Quick Reference: Framework Commands

### Running Tests

framework_commands[3]{framework,run_all,run_specific,watch_mode}:
pytest,pytest,pytest tests/test_user.py,pytest --watch
Jest,npm test,jest user.test.js,jest --watch
Vitest,vitest,vitest user.test.ts,vitest --watch

### Coverage Reports

coverage_commands[3]{framework,generate_coverage,view_html}:
pytest,pytest --cov=src,pytest --cov=src --cov-report=html
Jest,jest --coverage,open coverage/lcov-report/index.html
Vitest,vitest --coverage,open coverage/index.html

### Test Filtering

filter_commands[3]{framework,by_name,by_marker,parallel}:
pytest,pytest -k "user",pytest -m "not slow",pytest -n 4
Jest,jest -t "user",jest --testPathPattern=integration,jest --maxWorkers=4
Vitest,vitest -t "user",vitest --run integration,vitest --threads

## Best Practices Across All Examples

All examples in this directory demonstrate:

best_practices[10]{practice,benefit}:
AAA Pattern,Clear test structure and readability
Descriptive Names,Self-documenting tests
Isolated Tests,No dependencies between tests
Proper Mocking,Mock external dependencies only
Error Testing,Verify both success and failure paths
Parametrization,Reduce duplication for similar cases
Type Safety,TypeScript examples fully typed
Fixture Usage,Reusable test setup code
Single Responsibility,One concept per test
Clean Code,Maintainable and readable tests

## Additional Resources

- [Main Skill Documentation](../SKILL.md) - Core principles and guidelines
- [pytest Documentation](https://docs.pytest.org/) - Python testing
- [Jest Documentation](https://jestjs.io/) - JavaScript testing
- [Vitest Documentation](https://vitest.dev/) - TypeScript testing
- [Testing Library](https://testing-library.com/) - DOM testing utilities

## Contributing Examples

When adding new examples:

1. Follow the established pattern (AAA, descriptive names)
2. Include comments explaining complex logic
3. Demonstrate both success and error cases
4. Keep examples practical and realistic
5. Ensure examples are self-contained
6. Add proper type annotations (TypeScript)
7. Follow language-specific conventions
8. Test that examples actually work

---

**File Organization**: Each language has its own file to keep examples under 500 lines per file and maintain clarity.
