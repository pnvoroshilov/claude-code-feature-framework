# Python (pytest) Unit Testing Examples

Comprehensive examples for unit testing in Python using pytest framework.

## Basic Test Class with Fixtures

```python
# tests/test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    @pytest.fixture
    def calc(self):
        """Provide a fresh Calculator instance for each test."""
        return Calculator()

    def test_add_positive_numbers(self, calc):
        # Arrange
        a, b = 2, 3

        # Act
        result = calc.add(a, b)

        # Assert
        assert result == 5

    def test_add_negative_numbers(self, calc):
        assert calc.add(-2, -3) == -5

    def test_subtract_larger_from_smaller(self, calc):
        assert calc.subtract(5, 10) == -5

    def test_multiply_by_zero(self, calc):
        assert calc.multiply(42, 0) == 0

    def test_divide_evenly(self, calc):
        assert calc.divide(10, 2) == 5

    def test_divide_by_zero_raises_error(self, calc):
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)

    def test_divide_returns_float(self, calc):
        result = calc.divide(5, 2)
        assert result == 2.5
        assert isinstance(result, float)
```

## Parametrized Tests

```python
# tests/test_validator.py
import pytest
from validator import EmailValidator

class TestEmailValidator:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@example.com",
        "user+tag@example.co.uk",
        "test_user@test-domain.com"
    ])
    def test_valid_email_formats(self, email):
        validator = EmailValidator()
        assert validator.is_valid(email) is True

    @pytest.mark.parametrize("email", [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
        "user@example",
        ""
    ])
    def test_invalid_email_formats(self, email):
        validator = EmailValidator()
        assert validator.is_valid(email) is False

    @pytest.mark.parametrize("input_val,expected", [
        ("test@EXAMPLE.COM", "test@example.com"),
        ("  user@test.com  ", "user@test.com"),
        ("Test@Example.Com", "test@example.com")
    ])
    def test_normalize_email(self, input_val, expected):
        validator = EmailValidator()
        assert validator.normalize(input_val) == expected
```

## Mocking External Dependencies

```python
# tests/test_user_service.py
import pytest
from unittest.mock import Mock, patch, call
from user_service import UserService
from exceptions import UserAlreadyExistsError

class TestUserService:
    @pytest.fixture
    def mock_db(self):
        """Mock database connection."""
        return Mock()

    @pytest.fixture
    def mock_email_service(self):
        """Mock email service."""
        return Mock()

    @pytest.fixture
    def user_service(self, mock_db, mock_email_service):
        """UserService with mocked dependencies."""
        return UserService(
            database=mock_db,
            email_service=mock_email_service
        )

    def test_create_user_saves_to_database(self, user_service, mock_db):
        # Arrange
        email = "test@example.com"
        mock_db.user_exists.return_value = False
        mock_db.save_user.return_value = {"id": 123, "email": email}

        # Act
        user = user_service.create_user(email)

        # Assert
        mock_db.save_user.assert_called_once()
        assert user["email"] == email

    def test_create_user_sends_welcome_email(
        self, user_service, mock_db, mock_email_service
    ):
        # Arrange
        email = "test@example.com"
        mock_db.user_exists.return_value = False
        mock_db.save_user.return_value = {"id": 123, "email": email}

        # Act
        user_service.create_user(email)

        # Assert
        mock_email_service.send_welcome.assert_called_once_with(
            email=email,
            user_id=123
        )

    def test_create_user_raises_error_if_exists(self, user_service, mock_db):
        # Arrange
        email = "existing@example.com"
        mock_db.user_exists.return_value = True

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            user_service.create_user(email)

        # Verify database save was never called
        mock_db.save_user.assert_not_called()

    @patch('user_service.datetime')
    def test_user_creation_timestamp(self, mock_datetime, user_service, mock_db):
        # Arrange
        fixed_time = "2024-01-15T10:30:00"
        mock_datetime.now.return_value.isoformat.return_value = fixed_time
        mock_db.user_exists.return_value = False

        # Act
        user_service.create_user("test@example.com")

        # Assert
        save_call = mock_db.save_user.call_args
        assert save_call[0][0]["created_at"] == fixed_time
```

## Testing Async Code

```python
# tests/test_async_service.py
import pytest
from async_service import AsyncDataService

@pytest.mark.asyncio
class TestAsyncDataService:
    async def test_fetch_data_returns_dict(self):
        service = AsyncDataService()
        result = await service.fetch_data(user_id=123)
        assert isinstance(result, dict)
        assert "user_id" in result

    async def test_fetch_data_handles_timeout(self):
        service = AsyncDataService(timeout=0.001)
        with pytest.raises(TimeoutError):
            await service.fetch_data(user_id=999)

    @pytest.fixture
    async def service_with_data(self):
        """Async fixture providing service with pre-loaded data."""
        service = AsyncDataService()
        await service.load_cache()
        yield service
        await service.cleanup()

    async def test_cached_data_retrieval(self, service_with_data):
        result = await service_with_data.get_cached(key="test")
        assert result is not None
```

## Testing with Temporary Files

```python
# tests/test_file_processor.py
import pytest
from pathlib import Path
from file_processor import FileProcessor

class TestFileProcessor:
    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create temporary test file."""
        file_path = tmp_path / "test_data.txt"
        file_path.write_text("Line 1\nLine 2\nLine 3")
        return file_path

    def test_count_lines(self, temp_file):
        processor = FileProcessor()
        count = processor.count_lines(temp_file)
        assert count == 3

    def test_process_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        processor = FileProcessor()
        result = processor.process(empty_file)
        assert result == []

    def test_handles_nonexistent_file(self):
        processor = FileProcessor()
        with pytest.raises(FileNotFoundError):
            processor.process(Path("nonexistent.txt"))
```

## Advanced Fixtures

```python
# conftest.py - Shared fixtures across test files
import pytest
from database import Database
from config import TestConfig

@pytest.fixture(scope="session")
def test_config():
    """Session-scoped configuration - created once for all tests."""
    return TestConfig()

@pytest.fixture(scope="module")
def database_connection(test_config):
    """Module-scoped - created once per test module."""
    db = Database(test_config.db_url)
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def clean_database(database_connection):
    """Function-scoped - runs before each test."""
    database_connection.clear_all_tables()
    yield database_connection
    database_connection.rollback()

@pytest.fixture
def sample_users(clean_database):
    """Fixture that depends on other fixtures."""
    users = [
        {"email": "user1@test.com", "name": "User 1"},
        {"email": "user2@test.com", "name": "User 2"}
    ]
    for user in users:
        clean_database.insert("users", user)
    return users
```

## Testing with Markers

```python
# tests/test_performance.py
import pytest

@pytest.mark.slow
def test_large_data_processing():
    """Test that takes 5+ seconds."""
    processor = DataProcessor()
    result = processor.process_million_records()
    assert len(result) == 1_000_000

@pytest.mark.integration
def test_database_connection():
    """Requires real database connection."""
    db = Database.connect()
    assert db.ping() is True

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_new_syntax_feature():
    match result:
        case "success":
            assert True

@pytest.mark.xfail(reason="Known bug - fix in progress")
def test_known_issue():
    assert buggy_function() == expected_value

# Run tests selectively:
# pytest -m "not slow"  # Skip slow tests
# pytest -m integration  # Run only integration tests
# pytest -m "slow or integration"  # Run slow OR integration
```

## Custom Test Data Builders

```python
# tests/builders.py
class UserBuilder:
    """Builder pattern for creating test users."""

    def __init__(self):
        self._email = "test@example.com"
        self._role = "user"
        self._name = "Test User"
        self._verified = False

    def with_email(self, email):
        self._email = email
        return self

    def with_role(self, role):
        self._role = role
        return self

    def with_name(self, name):
        self._name = name
        return self

    def verified(self):
        self._verified = True
        return self

    def build(self):
        return User(
            email=self._email,
            role=self._role,
            name=self._name,
            verified=self._verified
        )

# Usage in tests
def test_admin_users_can_delete():
    admin = UserBuilder().with_role("admin").verified().build()
    assert admin.can_delete_users() is True

def test_unverified_users_cannot_post():
    user = UserBuilder().build()  # Not verified by default
    assert user.can_post_content() is False
```

## Testing Exceptions

```python
# tests/test_validation.py
import pytest
from validator import ValidationError, Validator

def test_raises_specific_exception():
    validator = Validator()
    with pytest.raises(ValidationError):
        validator.validate(None)

def test_exception_message_contains_text():
    validator = Validator()
    with pytest.raises(ValidationError, match="email is required"):
        validator.validate_email("")

def test_exception_attributes():
    validator = Validator()
    with pytest.raises(ValidationError) as exc_info:
        validator.validate_age(-5)

    assert exc_info.value.field == "age"
    assert exc_info.value.code == "INVALID_VALUE"

def test_multiple_exceptions_in_one_test():
    validator = Validator()

    # Test first exception
    with pytest.raises(ValueError):
        validator.parse_int("not a number")

    # Test second exception
    with pytest.raises(ValueError):
        validator.parse_int("")
```

## Property-Based Testing with Hypothesis

```python
# tests/test_property_based.py
from hypothesis import given, strategies as st
import pytest

@given(st.integers(), st.integers())
def test_addition_is_commutative(a, b):
    """Property: a + b should equal b + a."""
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_reverse_reverse_is_identity(lst):
    """Property: reversing a list twice returns original."""
    assert list(reversed(list(reversed(lst)))) == lst

@given(st.text())
def test_string_concatenation(s):
    """Property: concatenating empty string doesn't change string."""
    assert s + "" == s
    assert "" + s == s

@given(st.integers(min_value=0, max_value=100))
def test_discount_never_negative(price):
    """Property: discount result is never negative."""
    result = calculate_discount(price, percent=50)
    assert result >= 0
```

## Monkeypatching

```python
# tests/test_monkeypatch.py
import os

def test_environment_variable(monkeypatch):
    """Temporarily set environment variable for test."""
    monkeypatch.setenv("API_KEY", "test-key-123")
    assert os.getenv("API_KEY") == "test-key-123"
    # Environment reverts after test

def test_attribute_modification(monkeypatch):
    """Temporarily modify object attribute."""
    import mymodule
    monkeypatch.setattr(mymodule, "GLOBAL_SETTING", "test-value")
    assert mymodule.GLOBAL_SETTING == "test-value"

def test_dictionary_modification(monkeypatch):
    """Temporarily modify dictionary."""
    test_dict = {"key": "original"}
    monkeypatch.setitem(test_dict, "key", "modified")
    assert test_dict["key"] == "modified"

def test_function_replacement(monkeypatch):
    """Replace function with mock."""
    def mock_function():
        return "mocked"

    import mymodule
    monkeypatch.setattr(mymodule, "real_function", mock_function)
    assert mymodule.real_function() == "mocked"
```

## Best Practices Demonstrated

All Python examples above demonstrate:

1. **Clear AAA pattern** (Arrange, Act, Assert)
2. **Descriptive test names** explaining what's being tested
3. **Proper use of fixtures** for setup and teardown
4. **Isolated tests** with no dependencies between them
5. **Appropriate mocking** of external dependencies only
6. **Testing both success and failure paths**
7. **Using parametrization** for similar test cases
8. **Type hints** where appropriate
9. **Clear comments** explaining complex test logic
10. **One concept per test** for maintainability
