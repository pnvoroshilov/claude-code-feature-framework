---
name: test-runner
description: Comprehensive automated test execution with intelligent coverage analysis, failure diagnostics, and quality reporting across multiple frameworks and languages
version: 1.0.0
tags: [testing, qa, automation, coverage, test-execution]
---

# Test Runner - Automated Test Execution & Quality Assurance

## Overview

The Test Runner skill provides comprehensive automated test execution capabilities with intelligent coverage analysis, failure diagnostics, and quality reporting. This skill enables systematic testing across multiple frameworks, languages, and environments while providing actionable insights for maintaining high code quality.

Whether you're running unit tests, integration tests, end-to-end tests, or performance tests, this skill automates the entire testing workflow from test discovery to detailed failure analysis and coverage reporting.

## Key Capabilities

This skill provides 20+ comprehensive testing capabilities:

### Test Execution
- ✅ **Multi-Framework Support**: Jest, pytest, JUnit, Mocha, Jasmine, RSpec, PHPUnit, Go test
- ✅ **Parallel Test Execution**: Run tests concurrently for faster feedback
- ✅ **Selective Test Running**: Run specific tests, suites, or patterns
- ✅ **Watch Mode**: Automatic test re-running on code changes
- ✅ **Test Isolation**: Ensure tests don't interfere with each other

### Coverage Analysis
- ✅ **Line Coverage**: Measure which lines of code are executed
- ✅ **Branch Coverage**: Verify all conditional paths are tested
- ✅ **Function Coverage**: Track function execution during tests
- ✅ **Statement Coverage**: Count executed statements
- ✅ **Coverage Thresholds**: Enforce minimum coverage requirements

### Failure Diagnostics
- ✅ **Detailed Error Reports**: Comprehensive failure information
- ✅ **Stack Trace Analysis**: Identify failure root causes
- ✅ **Diff Visualization**: Compare expected vs actual values
- ✅ **Flaky Test Detection**: Identify unreliable tests
- ✅ **Failure Categorization**: Group similar failures

### Quality Reporting
- ✅ **Test Result Summaries**: Overview of test execution
- ✅ **Coverage Reports**: Visual coverage analysis
- ✅ **Trend Analysis**: Track quality metrics over time
- ✅ **Performance Metrics**: Test execution time tracking
- ✅ **Quality Gates**: Pass/fail criteria enforcement

### Integration Features
- ✅ **CI/CD Integration**: Works with GitHub Actions, GitLab CI, Jenkins
- ✅ **IDE Integration**: VSCode, IntelliJ, PyCharm integration
- ✅ **Report Formats**: JSON, XML, HTML, console output
- ✅ **Notification Systems**: Slack, email, webhook alerts

## Quick Start

### Basic Test Execution

```bash
# Run all tests with coverage
npm test -- --coverage

# Run specific test file
pytest tests/test_user_service.py -v

# Run tests with pattern matching
npm test -- --testNamePattern="user authentication"

# Run tests in watch mode
npm test -- --watch
```

### Coverage Analysis

```bash
# Generate coverage report
npm test -- --coverage --coverageReporters=html text

# Check coverage thresholds
pytest --cov=src --cov-fail-under=80

# Generate detailed coverage report
jest --coverage --collectCoverageFrom='src/**/*.{js,jsx,ts,tsx}'
```

### Failure Diagnostics

```bash
# Run with verbose output
pytest -vv --tb=long

# Show only failed tests
npm test -- --onlyFailures

# Debug specific test
node --inspect-brk node_modules/.bin/jest --runInBand test-file.test.js
```

## Core Documentation

### Essential Guides

**Core Concepts**: [docs/core-concepts.md](docs/core-concepts.md)
- Test types and hierarchy
- Test lifecycle and execution
- Coverage metrics explained
- Quality metrics and gates
- Test isolation principles

**Best Practices**: [docs/best-practices.md](docs/best-practices.md)
- Test organization patterns
- Naming conventions
- Test structure (AAA pattern)
- Mock and stub strategies
- Performance optimization

**Patterns**: [docs/patterns.md](docs/patterns.md)
- Test organization patterns
- Setup and teardown patterns
- Data-driven testing
- Snapshot testing
- Property-based testing

**Advanced Topics**: [docs/advanced-topics.md](docs/advanced-topics.md)
- Parallel test execution
- Test sharding strategies
- Performance testing
- Load and stress testing
- Contract testing

**Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- Common test failures
- Flaky test debugging
- Performance issues
- Coverage problems
- Framework-specific issues

**API Reference**: [docs/api-reference.md](docs/api-reference.md)
- Test framework commands
- Coverage tool APIs
- Configuration options
- Reporter APIs
- Plugin interfaces

## Examples

### Basic Examples

**[Example 1: Simple Unit Test Suite](examples/basic/example-1.md)**
- Setting up a basic test suite
- Writing simple unit tests
- Running tests with coverage
- Understanding test output

**[Example 2: Integration Test Setup](examples/basic/example-2.md)**
- Creating integration tests
- Database test fixtures
- API endpoint testing
- Test data management

**[Example 3: Mock and Stub Usage](examples/basic/example-3.md)**
- Creating test doubles
- Mocking external dependencies
- Stubbing API responses
- Verifying interactions

### Intermediate Examples

**[Pattern 1: Test Organization Architecture](examples/intermediate/pattern-1.md)**
- Organizing large test suites
- Shared test utilities
- Test helper functions
- Configuration management

**[Pattern 2: Advanced Coverage Strategies](examples/intermediate/pattern-2.md)**
- Achieving high coverage
- Coverage gap analysis
- Ignoring specific code
- Branch coverage optimization

**[Pattern 3: Continuous Testing Pipeline](examples/intermediate/pattern-3.md)**
- CI/CD test integration
- Parallel test execution
- Test result caching
- Failure notifications

### Advanced Examples

**[Advanced Pattern 1: Performance Test Suite](examples/advanced/advanced-pattern-1.md)**
- Load testing infrastructure
- Performance benchmarking
- Stress testing strategies
- Performance regression detection

**[Advanced Pattern 2: Multi-Environment Testing](examples/advanced/advanced-pattern-2.md)**
- Cross-browser testing
- Multi-platform execution
- Environment-specific configs
- Test matrix strategies

**[Advanced Pattern 3: Custom Test Reporters](examples/advanced/advanced-pattern-3.md)**
- Building custom reporters
- Integration with monitoring
- Real-time test dashboards
- Advanced analytics

## Templates

**[Template 1: Basic Test Suite Structure](templates/template-1.md)**
- Standard test file organization
- Common test patterns
- Setup and teardown boilerplate
- Configuration templates

**[Template 2: CI/CD Test Pipeline](templates/template-2.md)**
- GitHub Actions workflow
- GitLab CI configuration
- Jenkins pipeline setup
- Test result artifacts

**[Template 3: Comprehensive Test Strategy](templates/template-3.md)**
- Full testing stack setup
- Multi-level testing approach
- Coverage requirements
- Quality gates configuration

## Resources

**[Quality Checklists](resources/checklists.md)**
- Pre-commit test checklist
- Code review testing checklist
- Release testing checklist
- Coverage validation checklist

**[Complete Glossary](resources/glossary.md)**
- Testing terminology
- Framework-specific terms
- Coverage metrics definitions
- Quality metrics explained

**[External References](resources/references.md)**
- Official documentation
- Testing best practices
- Framework comparisons
- Tool recommendations

**[Step-by-Step Workflows](resources/workflows.md)**
- Test-driven development workflow
- Test debugging workflow
- Coverage improvement workflow
- CI/CD integration workflow

## Framework-Specific Guides

### JavaScript/TypeScript
```bash
# Jest
npm test -- --coverage --verbose

# Mocha + Chai
mocha tests/**/*.test.js --reporter spec

# Jasmine
jasmine --config=jasmine.json
```

### Python
```bash
# pytest
pytest --cov=src --cov-report=html

# unittest
python -m unittest discover -s tests

# nose2
nose2 --with-coverage
```

### Java
```bash
# JUnit
mvn test

# Gradle
./gradlew test

# TestNG
mvn test -DsuiteXmlFile=testng.xml
```

### Other Languages
```bash
# Go
go test ./... -cover -v

# Ruby (RSpec)
rspec --format documentation

# PHP (PHPUnit)
phpunit --coverage-html coverage/
```

## Test Execution Strategies

### Run All Tests
```bash
# Complete test suite execution
npm test
pytest
mvn test
go test ./...
```

### Selective Testing
```bash
# Single test file
jest src/components/Button.test.js

# Test pattern
pytest -k "user_authentication"

# Specific test class
mvn test -Dtest=UserServiceTest
```

### Parallel Execution
```bash
# Jest parallel
jest --maxWorkers=4

# pytest parallel
pytest -n 4

# Go parallel
go test -p 4 ./...
```

### Watch Mode
```bash
# Jest watch
jest --watch

# pytest watch
ptw -- --testmon

# Mocha watch
mocha --watch
```

## Coverage Analysis Workflow

### Generate Coverage Report
```bash
# Detailed HTML report
jest --coverage --coverageReporters=html lcov text

# Console summary
pytest --cov=src --cov-report=term-missing

# XML for CI/CD
mvn test jacoco:report
```

### Coverage Thresholds
```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

```python
# pytest.ini
[pytest]
addopts = --cov=src --cov-fail-under=80
```

### Coverage Analysis
1. **Review coverage report** - Identify uncovered code
2. **Prioritize gaps** - Focus on critical paths
3. **Write targeted tests** - Cover missing branches
4. **Verify improvement** - Re-run coverage analysis

## Failure Diagnostics Process

### Analyze Test Failures
```bash
# Verbose output with full error details
pytest -vv --tb=long

# Show only failures
jest --onlyFailures

# Debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

### Common Failure Patterns
- **Assertion failures**: Expected vs actual mismatches
- **Timeout errors**: Async operations taking too long
- **Setup failures**: Test environment issues
- **Flaky tests**: Intermittent failures

### Debugging Workflow
1. **Reproduce failure** - Run test in isolation
2. **Analyze stack trace** - Identify failure point
3. **Add debug output** - Log intermediate values
4. **Step through code** - Use debugger
5. **Fix root cause** - Update code or test
6. **Verify fix** - Re-run test suite

## Quality Gates

### Enforce Quality Standards
```yaml
# .github/workflows/test.yml
- name: Run tests with quality gates
  run: |
    npm test -- --coverage
    if [ $? -ne 0 ]; then
      echo "Tests failed"
      exit 1
    fi

    # Check coverage thresholds
    npx jest --coverage --coverageThreshold='{"global": {"lines": 80}}'
```

### Quality Metrics
- **Pass Rate**: Percentage of passing tests
- **Coverage**: Code coverage percentage
- **Performance**: Test execution time
- **Reliability**: Flaky test rate

## Integration with Development Workflow

### Pre-Commit Testing
```bash
# .husky/pre-commit
#!/bin/sh
npm test -- --bail --findRelatedTests
```

### Continuous Integration
```yaml
# GitHub Actions
- name: Test
  run: npm test -- --ci --coverage --maxWorkers=2

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/lcov.info
```

### IDE Integration
- **VSCode**: Jest extension, pytest extension
- **IntelliJ**: Built-in test runner
- **PyCharm**: Integrated pytest support

## Success Metrics

### Test Suite Health
- ✅ **High Coverage**: >80% line coverage, >75% branch coverage
- ✅ **Fast Execution**: Tests complete in <5 minutes
- ✅ **Reliable**: <1% flaky test rate
- ✅ **Maintainable**: Clear test organization and naming

### Quality Indicators
- 📊 **Trend Analysis**: Coverage increasing over time
- 📊 **Failure Rate**: Decreasing failure rate
- 📊 **Performance**: Stable or improving execution time
- 📊 **Test Count**: Growing test suite

## Common Use Cases

### 1. Pre-Commit Validation
Run affected tests before committing code

### 2. Pull Request Checks
Automated testing on every PR with coverage reporting

### 3. Release Validation
Comprehensive test execution before production deployment

### 4. Regression Testing
Verify existing functionality after changes

### 5. Performance Monitoring
Track application performance over time

## Getting Started Checklist

Copy this checklist to get started with test-runner:

```
Test Runner Setup:
- [ ] Install test framework for your language
- [ ] Configure test runner settings
- [ ] Set up coverage collection
- [ ] Create basic test structure
- [ ] Run first test suite
- [ ] Review coverage report
- [ ] Set up CI/CD integration
- [ ] Configure quality gates
- [ ] Add pre-commit hooks
- [ ] Document testing strategy
```

## Next Steps

1. **Review Core Concepts** - Understand testing fundamentals
2. **Explore Examples** - See working test implementations
3. **Use Templates** - Quick-start with proven patterns
4. **Check Resources** - Access checklists and workflows
5. **Practice** - Implement tests in your projects

## Support and Resources

- **Official Documentation**: Framework-specific test guides
- **Community Forums**: Stack Overflow, Reddit, Discord
- **Video Tutorials**: YouTube testing channels
- **Books**: "Test Driven Development" by Kent Beck
- **Courses**: Testing JavaScript, pytest Complete Guide

---

**Ready to ensure code quality?** Start with [Basic Example 1](examples/basic/example-1.md) to see a simple test suite in action, or jump to [Core Concepts](docs/core-concepts.md) for deeper understanding of testing principles.
