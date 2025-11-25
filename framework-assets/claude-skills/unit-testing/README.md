# Unit Testing Skill

Comprehensive unit testing best practices and examples for creating, maintaining, and running unit tests across multiple programming languages.

## What This Skill Provides

This skill helps Claude Code assist with:

- Writing effective unit tests following FIRST principles
- Implementing AAA (Arrange-Act-Assert) pattern
- Setting up test frameworks (pytest, Jest, Vitest)
- Mocking external dependencies appropriately
- Achieving meaningful code coverage
- Running and debugging tests
- Avoiding common testing anti-patterns

## Quick Start

**Read the main skill file**: [SKILL.md](SKILL.md)

The main skill file contains:
- Core testing principles (FIRST, AAA)
- Test structure and organization
- What to test (and what not to test)
- Mocking and stubbing best practices
- Test quality criteria
- Running tests and CI/CD integration
- TDD (Test-Driven Development) workflow

## Examples

**Comprehensive code examples**: [examples/](examples/)

Language-specific examples are organized by framework:

- [Python (pytest)](examples/python-pytest.md) - 483 lines
- [JavaScript (Jest)](examples/javascript-jest.md) - 687 lines
- [TypeScript (Vitest)](examples/typescript-vitest.md) - 730 lines
- [Index and Overview](examples/language-examples.md) - 186 lines

## When Claude Should Use This Skill

Claude should activate this skill when you:

trigger_scenarios[12]{user_mention,claude_action}:
"write tests for...",Create unit tests following best practices
"test this function",Implement tests with AAA pattern
"add test coverage",Write missing tests for uncovered code
"mock this dependency",Create appropriate mocks/stubs
"pytest setup",Configure pytest with fixtures
"jest configuration",Set up Jest testing environment
"test this edge case",Write tests for boundary conditions
"TDD",Guide through test-driven development
"failing test",Debug test failures and fix issues
"test structure",Organize test files and directories
"coverage report",Generate and analyze coverage
"CI testing",Set up automated testing in CI/CD

## Key Concepts

### FIRST Principles

Every unit test should be:
- **Fast** - Runs in milliseconds
- **Independent** - No dependencies on other tests
- **Repeatable** - Same result every time
- **Self-validating** - Clear pass/fail
- **Timely** - Written with or before code

### AAA Pattern

Every test follows three phases:
1. **Arrange** - Set up test data and dependencies
2. **Act** - Execute the behavior being tested
3. **Assert** - Verify expected outcomes

### Test Coverage Goals

coverage_targets[4]{category,target}:
Critical business logic,90-100%
Public APIs,80-90%
Error handling paths,70-80%
Overall codebase,80%+

## File Structure

```
unit-testing/
├── README.md              # This file - overview and quick start
├── SKILL.md              # Main skill file (500 lines)
└── examples/             # Code examples directory
    ├── language-examples.md    # Index and cross-language patterns
    ├── python-pytest.md        # Python/pytest examples
    ├── javascript-jest.md      # JavaScript/Jest examples
    └── typescript-vitest.md    # TypeScript/Vitest examples
```

## Quick Reference Commands

### Python (pytest)

```bash
pytest                          # Run all tests
pytest tests/test_user.py       # Run specific file
pytest -k "user"               # Run tests matching pattern
pytest -v                      # Verbose output
pytest --cov=src              # Generate coverage
pytest -n 4                    # Parallel execution (4 workers)
```

### JavaScript (Jest)

```bash
npm test                       # Run all tests
jest user.test.js             # Run specific file
jest -t "creates user"        # Run tests matching name
jest --watch                  # Watch mode
jest --coverage               # Generate coverage
jest --maxWorkers=4           # Parallel execution
```

### TypeScript (Vitest)

```bash
vitest                        # Run all tests
vitest user.test.ts          # Run specific file
vitest -t "creates"          # Run tests matching name
vitest --watch               # Watch mode
vitest --coverage            # Generate coverage
vitest --threads             # Parallel execution
```

## Testing Frameworks Comparison

frameworks[3]{language,primary,features}:
Python,pytest,"Fixtures, parametrization, markers, powerful assertions"
JavaScript,Jest,"Snapshot testing, timers, extensive mocking, built-in coverage"
TypeScript,Vitest,"Type-safe, fast, Vite integration, Jest-compatible API"

## Common Anti-Patterns to Avoid

anti_patterns_summary[6]{pattern,why_bad}:
Testing private methods,Couples tests to implementation details
Over-mocking,Tests don't catch real integration bugs
Test interdependence,Tests fail when run in different order
No assertions,Test runs but doesn't verify anything
Testing framework code,Framework is already tested
Ignoring test failures,Reduces confidence in test suite

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Martin Fowler - Testing](https://martinfowler.com/testing/)

## Version

- **Version**: 1.0.0
- **Last Updated**: 2025-01-25
- **Maintained by**: Claude Code Skills

---

**Note**: This skill focuses on unit testing specifically. For integration testing, end-to-end testing, or performance testing, refer to other specialized skills in the `.claude/skills/` directory.
