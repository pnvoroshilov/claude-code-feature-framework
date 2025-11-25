---
name: unit-testing
description: Comprehensive unit testing best practices for creating, maintaining, and running unit tests. Use when writing test code, setting up test frameworks, implementing TDD, improving test coverage, or debugging test failures across Python, JavaScript, TypeScript and other languages.
version: 1.0.0
tags: [testing, unit-tests, tdd, quality, pytest, jest, coverage]
---

# Unit Testing Best Practices

Expert guidance for creating, maintaining, and running effective unit tests across multiple programming languages and frameworks.

## Core Principles

unit_test_principles[5]{principle,acronym,description}:
Fast,F,Tests run in milliseconds - no network/disk/DB dependencies
Independent,I,Tests can run in any order without affecting each other
Repeatable,R,Same result every time regardless of environment
Self-validating,S,Pass/fail is clear - no manual inspection needed
Timely,T,Written just before or with production code (TDD)

## AAA Pattern (Arrange-Act-Assert)

Every unit test should follow this structure:

```python
def test_user_creation_sets_default_role():
    # Arrange - Set up test data and dependencies
    user_service = UserService()
    email = "test@example.com"

    # Act - Execute the behavior being tested
    user = user_service.create_user(email)

    # Assert - Verify the expected outcome
    assert user.role == "member"
    assert user.email == email
```

aaa_sections[3]{section,purpose,guidelines}:
Arrange,Setup test data and mocks,Keep minimal - only what's needed for this test
Act,Execute the method under test,Should be a single method call or operation
Assert,Verify expected outcomes,Use specific assertions - avoid assertTrue for everything

## Test Naming Conventions

test_naming_patterns[4]{pattern,example,use_case}:
test_<method>_<scenario>_<expected>,test_divide_by_zero_raises_error,Python/standard pattern
should_<expected>_when_<scenario>,should_return_empty_list_when_no_results,BDD-style readable tests
<scenario>_should_<expected>,invalid_email_should_raise_validation_error,Alternative BDD style
test_<behavior>,test_user_cannot_delete_own_account,Behavior-focused naming

**Naming Best Practices**:
- Use descriptive names that explain the test's purpose
- Include the scenario being tested and expected outcome
- Avoid generic names like `test_1` or `test_user`
- Keep names under 80 characters when possible

## Test Structure and Organization

### File Organization

test_file_patterns[3]{language,pattern,example}:
Python,test_<module>.py mirrors src/<module>.py,src/user.py → tests/test_user.py
JavaScript,<module>.test.js or <module>.spec.js,user.js → user.test.js or user.spec.js
TypeScript,<module>.test.ts in __tests__ or colocated,user.ts → user.test.ts or __tests__/user.test.ts

### Directory Structure

```
project/
├── src/
│   ├── user.py
│   ├── payment.py
│   └── utils/
│       └── validator.py
└── tests/
    ├── test_user.py
    ├── test_payment.py
    └── utils/
        └── test_validator.py
```

### Setup and Teardown

setup_teardown_patterns[4]{pattern,use_case,example_framework}:
setUp/tearDown,Per-test setup and cleanup,unittest (Python)
setUpClass/tearDownClass,Per-test-class setup,unittest (Python)
@pytest.fixture,Reusable test dependencies,pytest (Python)
beforeEach/afterEach,Per-test setup and cleanup,Jest (JavaScript)

**Python pytest Example**:
```python
import pytest

@pytest.fixture
def user_service():
    """Fixture providing a fresh UserService instance."""
    service = UserService(database=MockDatabase())
    yield service
    service.cleanup()  # Teardown after test

def test_create_user(user_service):
    user = user_service.create_user("test@example.com")
    assert user.email == "test@example.com"
```

**JavaScript Jest Example**:
```javascript
describe('UserService', () => {
    let userService;

    beforeEach(() => {
        userService = new UserService({ db: new MockDatabase() });
    });

    afterEach(() => {
        userService.cleanup();
    });

    test('creates user with email', () => {
        const user = userService.createUser('test@example.com');
        expect(user.email).toBe('test@example.com');
    });
});
```

## What to Test

test_coverage_targets[8]{category,description,priority}:
Public API,All public methods and functions,High
Business Logic,Calculations and decision logic,High
Edge Cases,Boundary values and limits,High
Error Handling,Exception paths and validation,High
State Changes,Object state transitions,Medium
Integration Points,Module boundaries and contracts,Medium
Configuration,Different config combinations,Medium
Happy Path,Main success scenarios,Medium

### Testing Edge Cases

edge_case_categories[6]{category,examples}:
Boundary Values,"0, -1, MAX_INT, empty string, null"
Empty Collections,"[], {}, empty string, None/null"
Invalid Input,"negative when positive expected, wrong type"
Concurrent Access,"race conditions, deadlocks (if applicable)"
Large Data Sets,"performance with 1000+ items"
Special Characters,"unicode, emojis, escape sequences"

**Example - Boundary Testing**:
```python
def test_calculate_discount_boundary_values():
    # Test boundaries of discount calculation
    assert calculate_discount(0) == 0      # Minimum
    assert calculate_discount(100) == 10   # Maximum
    assert calculate_discount(50) == 5     # Middle
    assert calculate_discount(-1) == 0     # Below minimum
    assert calculate_discount(101) == 10   # Above maximum
```

## What NOT to Test

avoid_testing[6]{category,reason,alternative}:
Private Methods,Implementation details may change,Test through public API
Framework Code,Already tested by framework authors,Test your usage of it
Simple Getters/Setters,No logic to test,Test complex properties only
Third-Party Libraries,Maintained by library authors,Mock and test integration
Generated Code,Auto-generated from schemas/tools,Test the generator not output
Trivial Code,No branching or logic,Focus on complex code

**Anti-Pattern Example**:
```python
# DON'T TEST THIS - too simple
def test_get_name():
    user = User(name="Alice")
    assert user.name == "Alice"  # Just testing Python works

# DO TEST THIS - has logic
def test_get_display_name_uses_username_when_no_full_name():
    user = User(username="alice123", full_name=None)
    assert user.display_name == "alice123"
```

## Mocking and Stubbing

mock_types[4]{type,purpose,when_to_use}:
Mock,Verify behavior (calls and arguments),Testing interactions and side effects
Stub,Provide predetermined responses,Testing with external dependencies
Spy,Wrap real object to track calls,Testing partial behavior
Fake,Lightweight implementation for testing,In-memory DB or simplified service

### Mocking Best Practices

mocking_guidelines[6]{guideline,explanation}:
Mock at boundaries,Mock external services not internal classes
Don't over-mock,Too many mocks make tests brittle
Use dependency injection,Pass dependencies to make mocking easy
Mock interfaces not implementations,Test against abstractions
Verify important interactions only,Don't verify every method call
Reset mocks between tests,Ensure test independence

**Python Mock Example**:
```python
from unittest.mock import Mock, patch

def test_send_welcome_email_on_user_creation():
    # Arrange
    mock_email_service = Mock()
    user_service = UserService(email_service=mock_email_service)

    # Act
    user = user_service.create_user("alice@example.com")

    # Assert
    mock_email_service.send_welcome.assert_called_once_with(
        email="alice@example.com",
        user_id=user.id
    )

@patch('payment.stripe_api.charge')
def test_process_payment_calls_stripe(mock_stripe):
    # Arrange
    mock_stripe.return_value = {"status": "success"}
    payment_service = PaymentService()

    # Act
    result = payment_service.process(amount=100, card="tok_visa")

    # Assert
    assert result.status == "success"
    mock_stripe.assert_called_once_with(amount=100, card="tok_visa")
```

**JavaScript Jest Mock Example**:
```javascript
// Mock module
jest.mock('./emailService');
import { EmailService } from './emailService';

test('sends welcome email on user creation', () => {
    // Arrange
    const mockSend = jest.fn().mockResolvedValue({ sent: true });
    EmailService.mockImplementation(() => ({
        sendWelcome: mockSend
    }));

    const userService = new UserService();

    // Act
    const user = userService.createUser('alice@example.com');

    // Assert
    expect(mockSend).toHaveBeenCalledWith({
        email: 'alice@example.com',
        userId: user.id
    });
});
```

## Test Quality Criteria

quality_criteria[8]{criterion,target,explanation}:
Coverage,80%+ meaningful coverage,Focus on critical paths not 100%
Speed,< 100ms per test,Fast feedback loop for TDD
Readability,Self-documenting tests,Others understand without comments
Maintainability,Low coupling to implementation,Refactor code without breaking tests
Reliability,Zero flaky tests,Always same result - no randomness
Isolation,No shared state between tests,Tests run in any order
Assertions,1-3 assertions per test,Single responsibility per test
Documentation,Test names explain purpose,Test serves as usage example

### Code Coverage

**Coverage Goals**:
- Critical business logic: 90-100%
- Public APIs: 80-90%
- Error handling paths: 70-80%
- Overall codebase: 80%+

**Coverage is NOT a goal itself**:
```python
# BAD: 100% coverage but meaningless test
def test_user_exists():
    user = User("alice")
    assert user is not None  # Pointless assertion

# GOOD: Tests actual behavior
def test_user_validates_email_format():
    with pytest.raises(ValueError, match="Invalid email"):
        User("not-an-email")
```

### Avoiding Flaky Tests

flaky_test_causes[7]{cause,solution}:
Time Dependencies,Use fixed timestamps or mock time
Random Data,Use fixed seed or controlled test data
External Services,Mock external APIs and services
Race Conditions,Avoid threading in tests or use proper synchronization
Global State,Reset global state in setUp/tearDown
Test Order Dependencies,Ensure tests don't depend on execution order
Environment Variables,Set and reset env vars in test fixtures

**Example - Fixing Time-Dependent Tests**:
```python
# FLAKY - depends on current time
def test_is_expired():
    token = Token(expires_at="2024-01-01")
    assert token.is_expired()  # Fails after 2024!

# FIXED - mock time
@freeze_time("2024-06-01")
def test_is_expired():
    token = Token(expires_at="2024-01-01")
    assert token.is_expired()  # Always reliable
```

## Running Tests

### pytest Commands (Python)

pytest_commands[10]{command,description}:
pytest,Run all tests in current directory
pytest tests/,Run all tests in tests directory
pytest tests/test_user.py,Run specific test file
pytest tests/test_user.py::test_create,Run specific test function
pytest -k "user and create",Run tests matching expression
pytest -v,Verbose output with test names
pytest -x,Stop on first failure
pytest --lf,Run last failed tests only
pytest -n 4,Run tests in parallel (4 workers)
pytest --cov=src --cov-report=html,Generate coverage report

### Jest Commands (JavaScript/TypeScript)

jest_commands[10]{command,description}:
npm test,Run all tests
jest,Run all tests with Jest
jest user.test.js,Run specific test file
jest -t "creates user",Run tests matching name pattern
jest --watch,Watch mode - rerun on file changes
jest --coverage,Generate coverage report
jest --verbose,Detailed test output
jest --silent,Suppress console output
jest --maxWorkers=4,Run tests in parallel
jest --updateSnapshot,Update snapshot tests

### Test Selection and Filtering

**Python pytest markers**:
```python
import pytest

@pytest.mark.slow
def test_large_data_processing():
    # Takes 5+ seconds
    pass

@pytest.mark.integration
def test_database_connection():
    # Requires database
    pass

# Run only fast tests
# pytest -m "not slow"

# Run only integration tests
# pytest -m integration
```

**JavaScript Jest patterns**:
```javascript
describe('UserService', () => {
    describe('creation', () => {
        test('creates user with email', () => { /* ... */ });
        test('validates email format', () => { /* ... */ });
    });

    describe('deletion', () => {
        test('soft deletes user', () => { /* ... */ });
    });
});

// Run only creation tests
// jest -t "creation"
```

## CI/CD Integration

ci_cd_patterns[5]{platform,config_file,example_command}:
GitHub Actions,.github/workflows/test.yml,pytest --cov=src --cov-report=xml
GitLab CI,.gitlab-ci.yml,pytest --junitxml=report.xml
CircleCI,.circleci/config.yml,jest --ci --coverage
Jenkins,Jenkinsfile,sh 'pytest --html=report.html'
Travis CI,.travis.yml,pytest tests/

**GitHub Actions Example**:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Language-Specific Examples

language_frameworks[5]{language,primary_framework,alternative,test_runner}:
Python,pytest,unittest,pytest or python -m pytest
JavaScript,Jest,Mocha + Chai,npm test or jest
TypeScript,Vitest,Jest,vitest or npm test
Java,JUnit 5,TestNG,mvn test
Go,testing package,testify,go test

**See [examples/language-examples.md](examples/language-examples.md) for comprehensive code examples including:**
- Python (pytest) - fixtures, parametrization, mocking, async tests
- JavaScript (Jest) - test suites, mocking, async, snapshot testing
- TypeScript (Vitest) - type-safe tests, generics, mocking
- Cross-language patterns - builders, custom matchers

## Test-Driven Development (TDD)

tdd_cycle[3]{step,description,duration}:
Red,Write failing test for new feature,2-3 minutes
Green,Write minimal code to make test pass,3-5 minutes
Refactor,Improve code while keeping tests green,2-5 minutes

**TDD Example**:
```python
# Step 1: RED - Write failing test
def test_user_full_name_combines_first_and_last():
    user = User(first_name="Alice", last_name="Smith")
    assert user.full_name == "Alice Smith"
# Test fails - full_name property doesn't exist

# Step 2: GREEN - Make it pass
class User:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
# Test passes!

# Step 3: REFACTOR - Improve (example)
class User:
    def __init__(self, first_name, last_name):
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
# Test still passes, code is better
```

## Common Testing Anti-Patterns

anti_patterns[8]{pattern,problem,solution}:
Testing Implementation Details,Tests break with refactoring,Test behavior not internal structure
Over-Mocking,Tests don't catch real bugs,Mock external dependencies only
Test Interdependence,Tests fail in different order,Each test fully independent
Ignoring Test Failures,Builds pass with failing tests,Fix or delete broken tests
No Assertions,Test runs but verifies nothing,Every test needs assertions
Generic Assertions,assert x is not None for everything,Use specific meaningful assertions
Testing Too Much,One test verifies 10 behaviors,One concept per test
Copy-Paste Tests,Duplicate test code everywhere,Use fixtures and parametrization

## Best Practices Summary

testing_best_practices[12]{practice,explanation}:
Start with simple cases,Test happy path before edge cases
One assertion per concept,Group related assertions but keep focused
Test behavior not implementation,Refactoring shouldn't break tests
Use descriptive test names,Test name should explain what's being tested
Keep tests DRY,Use fixtures and helper functions
Make tests readable,Optimize for clarity not brevity
Test error cases,Verify exceptions and error messages
Use test doubles wisely,Mock external dependencies not internal code
Run tests frequently,Fast feedback loop is essential
Maintain test code quality,Tests are code - review and refactor them
Commit tests with code,Never commit code without tests
Delete obsolete tests,Remove tests for deleted features

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/) - Python testing framework
- [Jest Documentation](https://jestjs.io/) - JavaScript testing framework
- [Vitest Documentation](https://vitest.dev/) - Fast Vite-native testing framework
- [Testing Best Practices](https://testingjavascript.com/) - JavaScript testing guide
- [Python Testing with pytest Book](https://pragprog.com/titles/bopytest/) - Comprehensive pytest guide
