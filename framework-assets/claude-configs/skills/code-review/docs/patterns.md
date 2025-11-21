# Code Patterns and Anti-Patterns

## Table of Contents

- [Design Patterns](#design-patterns)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Error Handling Patterns](#error-handling-patterns)
- [Testing Patterns](#testing-patterns)
- [Security Patterns](#security-patterns)
- [Performance Patterns](#performance-patterns)
- [Database Patterns](#database-patterns)
- [API Design Patterns](#api-design-patterns)
- [Frontend Patterns](#frontend-patterns)
- [Concurrency Patterns](#concurrency-patterns)

## Design Patterns

### 1. Repository Pattern

**When to Use**: Separate data access logic from business logic

**Good Implementation**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    """Abstract repository defining data access interface."""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> None:
        pass


class SQLAlchemyUserRepository(UserRepository):
    """Concrete implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def find_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def save(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def delete(self, user_id: int) -> None:
        user = self.find_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()


class UserService:
    """Business logic layer using repository."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, email: str, password: str) -> User:
        existing = self.repository.find_by_email(email)
        if existing:
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        user = User(email=email, password_hash=hash_password(password))
        return self.repository.save(user)
```

**Benefits**:
- Business logic independent of data access
- Easy to switch databases
- Simplified testing (mock repository)
- Clear separation of concerns

**Anti-Pattern**: Direct database access in business logic
```python
# Bad: Business logic tightly coupled to database
class UserService:
    def register_user(self, email, password):
        existing = db.session.query(User).filter_by(email=email).first()
        if existing:
            raise UserAlreadyExistsError()
        # ...
```

### 2. Factory Pattern

**When to Use**: Complex object creation, multiple variants, creation logic needs encapsulation

**Good Implementation**:
```python
from enum import Enum
from abc import ABC, abstractmethod

class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(ABC):
    """Base notification interface."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        pass


class EmailNotification(Notification):
    def __init__(self, smtp_config: SMTPConfig):
        self.smtp = smtp_config

    def send(self, recipient: str, message: str) -> bool:
        # Email sending implementation
        return True


class SMSNotification(Notification):
    def __init__(self, sms_config: SMSConfig):
        self.sms_client = sms_config

    def send(self, recipient: str, message: str) -> bool:
        # SMS sending implementation
        return True


class NotificationFactory:
    """Factory for creating notification instances."""

    def __init__(
        self,
        email_config: SMTPConfig,
        sms_config: SMSConfig,
        push_config: PushConfig
    ):
        self.email_config = email_config
        self.sms_config = sms_config
        self.push_config = push_config

    def create(self, notification_type: NotificationType) -> Notification:
        if notification_type == NotificationType.EMAIL:
            return EmailNotification(self.email_config)
        elif notification_type == NotificationType.SMS:
            return SMSNotification(self.sms_config)
        elif notification_type == NotificationType.PUSH:
            return PushNotification(self.push_config)
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")


# Usage
factory = NotificationFactory(email_cfg, sms_cfg, push_cfg)
notification = factory.create(NotificationType.EMAIL)
notification.send("user@example.com", "Hello!")
```

**Benefits**:
- Centralized object creation
- Easy to add new types
- Configuration encapsulated
- Testable (mock factory)

### 3. Strategy Pattern

**When to Use**: Multiple algorithms/behaviors, runtime selection, avoid conditionals

**Good Implementation**:
```python
from abc import ABC, abstractmethod
from decimal import Decimal

class DiscountStrategy(ABC):
    """Strategy interface for discount calculations."""

    @abstractmethod
    def calculate_discount(self, order_total: Decimal) -> Decimal:
        pass


class NoDiscount(DiscountStrategy):
    def calculate_discount(self, order_total: Decimal) -> Decimal:
        return Decimal('0')


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: Decimal):
        self.percentage = percentage

    def calculate_discount(self, order_total: Decimal) -> Decimal:
        return order_total * (self.percentage / 100)


class TieredDiscount(DiscountStrategy):
    """Discount based on order amount tiers."""

    TIERS = [
        (Decimal('1000'), Decimal('15')),  # 15% off orders over $1000
        (Decimal('500'), Decimal('10')),   # 10% off orders over $500
        (Decimal('100'), Decimal('5')),    # 5% off orders over $100
    ]

    def calculate_discount(self, order_total: Decimal) -> Decimal:
        for threshold, percentage in self.TIERS:
            if order_total >= threshold:
                return order_total * (percentage / 100)
        return Decimal('0')


class Order:
    def __init__(self, items: List[OrderItem], discount_strategy: DiscountStrategy):
        self.items = items
        self.discount_strategy = discount_strategy

    def calculate_total(self) -> Decimal:
        subtotal = sum(item.price * item.quantity for item in self.items)
        discount = self.discount_strategy.calculate_discount(subtotal)
        return subtotal - discount


# Usage: Easy to switch strategies
loyalty_customer = Order(items, PercentageDiscount(Decimal('20')))
regular_customer = Order(items, TieredDiscount())
```

**Benefits**:
- Eliminates complex conditionals
- Easy to add new strategies
- Runtime strategy selection
- Testable in isolation

**Anti-Pattern**: Massive if-else chains
```python
# Bad: Hard to maintain, test, extend
def calculate_discount(order_total, customer_type, loyalty_years):
    if customer_type == "premium":
        if loyalty_years > 10:
            return order_total * 0.25
        elif loyalty_years > 5:
            return order_total * 0.20
        else:
            return order_total * 0.15
    elif customer_type == "regular":
        if order_total > 1000:
            return order_total * 0.15
        elif order_total > 500:
            return order_total * 0.10
        # ... many more conditions
```

### 4. Dependency Injection

**When to Use**: Always for testability and flexibility

**Good Implementation**:
```python
class UserService:
    """Dependencies injected via constructor."""

    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
        password_hasher: PasswordHasher,
        logger: Logger
    ):
        self.user_repository = user_repository
        self.email_service = email_service
        self.password_hasher = password_hasher
        self.logger = logger

    def register_user(self, email: str, password: str) -> User:
        self.logger.info(f"Registering user: {email}")

        password_hash = self.password_hasher.hash(password)
        user = User(email=email, password_hash=password_hash)

        saved_user = self.user_repository.save(user)
        self.email_service.send_welcome_email(user)

        return saved_user


# Easy to test with mocks
def test_register_user():
    mock_repo = Mock(UserRepository)
    mock_email = Mock(EmailService)
    mock_hasher = Mock(PasswordHasher)
    mock_logger = Mock(Logger)

    service = UserService(mock_repo, mock_email, mock_hasher, mock_logger)
    user = service.register_user("test@example.com", "password")

    mock_repo.save.assert_called_once()
    mock_email.send_welcome_email.assert_called_once()
```

**Anti-Pattern**: Hard-coded dependencies
```python
# Bad: Hard to test, tightly coupled
class UserService:
    def __init__(self):
        self.user_repository = SQLAlchemyUserRepository()  # Hard-coded
        self.email_service = SendGridEmailService()  # Hard-coded
        self.logger = FileLogger("/var/log/app.log")  # Hard-coded

    def register_user(self, email, password):
        # Cannot easily test without real database, email service, file system
        pass
```

## Anti-Patterns to Avoid

### 1. God Object / God Class

**Problem**: Class knows or does too much, violates SRP

**Bad Example**:
```python
class UserManager:
    """God class - handles everything user-related."""

    def __init__(self):
        self.db = Database()
        self.email = EmailClient()
        self.cache = Redis()
        self.logger = Logger()

    def register_user(self, data):
        # Validation
        if not self._valid_email(data['email']):
            raise ValidationError()

        # Password hashing
        hashed = self._hash_password(data['password'])

        # Database insertion
        user_id = self.db.insert('users', ...)

        # Cache update
        self.cache.set(f'user:{user_id}', ...)

        # Email sending
        self.email.send_welcome(data['email'])

        # Logging
        self.logger.info(f"User registered: {user_id}")

        # Analytics
        self._track_registration(user_id)

        return user_id

    # 50 more methods handling all user operations...
```

**Solution**: Split into focused classes
```python
class UserValidator:
    def validate(self, data: dict) -> None:
        """Focused on validation only."""
        pass

class UserRepository:
    def save(self, user: User) -> User:
        """Focused on persistence only."""
        pass

class UserRegistrationService:
    """Orchestrates registration workflow."""

    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        email_service: EmailService
    ):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service

    def register(self, data: dict) -> User:
        self.validator.validate(data)
        user = User.from_dict(data)
        saved_user = self.repository.save(user)
        self.email_service.send_welcome(saved_user)
        return saved_user
```

### 2. Spaghetti Code

**Problem**: Complex, tangled control flow; hard to follow

**Bad Example**:
```python
def process_order(order_id):
    order = get_order(order_id)
    if order:
        if order.status == 'pending':
            items = get_items(order_id)
            if items:
                total = 0
                for item in items:
                    if item.available:
                        total += item.price
                    else:
                        if item.backorder:
                            if item.eta < 7:
                                total += item.price
                            else:
                                notify_customer(order_id, item.id)
                        else:
                            remove_item(order_id, item.id)
                if total > 0:
                    if charge_customer(order.customer_id, total):
                        ship_order(order_id)
                        send_confirmation(order.customer_id)
                    else:
                        # ... more nesting
```

**Solution**: Extract functions, reduce nesting
```python
def process_order(order_id: str) -> None:
    order = get_order(order_id)
    validate_order_state(order)

    items = get_available_items(order)
    handle_unavailable_items(order, items)

    total = calculate_total(items)
    if total > 0:
        process_payment_and_ship(order, total)


def validate_order_state(order: Order) -> None:
    if not order:
        raise OrderNotFoundError()
    if order.status != OrderStatus.PENDING:
        raise InvalidOrderStateError()


def get_available_items(order: Order) -> List[OrderItem]:
    return [item for item in order.items if item.is_available()]


def handle_unavailable_items(order: Order, available_items: List[OrderItem]) -> None:
    unavailable = set(order.items) - set(available_items)
    for item in unavailable:
        handle_unavailable_item(order, item)


def process_payment_and_ship(order: Order, total: Decimal) -> None:
    payment_result = charge_customer(order.customer_id, total)
    if payment_result.success:
        ship_order(order.id)
        send_confirmation(order.customer_id)
    else:
        handle_payment_failure(order, payment_result)
```

### 3. Magic Numbers and Strings

**Problem**: Unclear meaning, hard to maintain

**Bad Example**:
```python
def validate_password(password):
    if len(password) < 8:  # Magic number
        return False
    if password == "password123":  # Magic string
        return False
    return True

def calculate_shipping(weight):
    if weight < 5:  # What is 5?
        return 9.99  # What is 9.99?
    elif weight < 20:  # What is 20?
        return 19.99
    return 29.99
```

**Solution**: Named constants
```python
# Configuration constants
MIN_PASSWORD_LENGTH = 8
COMMON_PASSWORDS = ["password123", "12345678", "qwerty"]

# Shipping tiers
LIGHTWEIGHT_THRESHOLD = 5  # kg
LIGHTWEIGHT_COST = Decimal('9.99')  # USD

MEDIUM_WEIGHT_THRESHOLD = 20  # kg
MEDIUM_WEIGHT_COST = Decimal('19.99')

HEAVY_WEIGHT_COST = Decimal('29.99')


def validate_password(password: str) -> bool:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if password in COMMON_PASSWORDS:
        return False
    return True


def calculate_shipping(weight: float) -> Decimal:
    if weight < LIGHTWEIGHT_THRESHOLD:
        return LIGHTWEIGHT_COST
    elif weight < MEDIUM_WEIGHT_THRESHOLD:
        return MEDIUM_WEIGHT_COST
    return HEAVY_WEIGHT_COST
```

### 4. Primitive Obsession

**Problem**: Using primitives instead of domain objects

**Bad Example**:
```python
def send_email(
    to: str,
    from_addr: str,
    subject: str,
    body: str,
    cc: List[str],
    bcc: List[str],
    attachments: List[str]
) -> bool:
    # Long parameter list of primitives
    # No validation
    # Easy to mix up parameters
    pass

# Usage: Error-prone
send_email(
    "Subject Line",  # Oops, swapped parameters
    "user@example.com",
    "sender@example.com",
    "Body text",
    [],
    [],
    []
)
```

**Solution**: Value objects and domain models
```python
@dataclass
class EmailAddress:
    """Value object ensuring valid email."""
    address: str

    def __post_init__(self):
        if not self._is_valid_email(self.address):
            raise ValueError(f"Invalid email: {self.address}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return '@' in email and '.' in email.split('@')[1]


@dataclass
class Email:
    """Rich domain model for email."""
    to: EmailAddress
    from_addr: EmailAddress
    subject: str
    body: str
    cc: List[EmailAddress] = field(default_factory=list)
    bcc: List[EmailAddress] = field(default_factory=list)
    attachments: List[Path] = field(default_factory=list)

    def __post_init__(self):
        if not self.subject:
            raise ValueError("Subject is required")
        if not self.body:
            raise ValueError("Body is required")


def send_email(email: Email) -> bool:
    # Type-safe, validated, clear intent
    pass

# Usage: Type-safe and clear
email = Email(
    to=EmailAddress("user@example.com"),
    from_addr=EmailAddress("sender@example.com"),
    subject="Subject Line",
    body="Body text"
)
send_email(email)
```

### 5. Copy-Paste Programming

**Problem**: Duplicated code everywhere

**Bad Example**:
```python
def validate_username(username):
    if not username:
        raise ValidationError("Username is required")
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    if len(username) > 20:
        raise ValidationError("Username cannot exceed 20 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")

def validate_display_name(display_name):
    if not display_name:
        raise ValidationError("Display name is required")
    if len(display_name) < 3:
        raise ValidationError("Display name must be at least 3 characters")
    if len(display_name) > 20:
        raise ValidationError("Display name cannot exceed 20 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', display_name):
        raise ValidationError("Display name can only contain letters, numbers, and underscores")

# More duplicated validation...
```

**Solution**: Extract reusable validation
```python
def validate_string_field(
    field_name: str,
    value: str,
    min_length: int,
    max_length: int,
    pattern: Optional[str] = None
) -> None:
    """Reusable string validation."""
    if not value:
        raise ValidationError(f"{field_name} is required")

    if len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters"
        )

    if len(value) > max_length:
        raise ValidationError(
            f"{field_name} cannot exceed {max_length} characters"
        )

    if pattern and not re.match(pattern, value):
        raise ValidationError(
            f"{field_name} contains invalid characters"
        )


# Configuration-driven validation
USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'

def validate_username(username: str) -> None:
    validate_string_field("Username", username, 3, 20, USERNAME_PATTERN)

def validate_display_name(display_name: str) -> None:
    validate_string_field("Display name", display_name, 3, 20, USERNAME_PATTERN)
```

## Error Handling Patterns

### 1. Exception Hierarchy

**Pattern**: Create specific exception types for different failure modes

**Good Implementation**:
```python
class ApplicationError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(ApplicationError):
    """Input validation failures."""
    pass

class AuthenticationError(ApplicationError):
    """Authentication failures."""
    pass

class AuthorizationError(ApplicationError):
    """Authorization failures."""
    pass

class ResourceNotFoundError(ApplicationError):
    """Requested resource doesn't exist."""
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

class ExternalServiceError(ApplicationError):
    """External service unavailable or error."""
    pass

# Usage: Catch specifically what you can handle
try:
    user = user_service.get_user(user_id)
except ResourceNotFoundError as e:
    return jsonify({"error": "User not found"}), 404
except AuthorizationError:
    return jsonify({"error": "Forbidden"}), 403
except ApplicationError as e:
    logger.error(f"Application error: {e}")
    return jsonify({"error": "Internal error"}), 500
```

### 2. Result Pattern

**Pattern**: Return success/failure without exceptions for expected failures

**Good Implementation**:
```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Success(Generic[T]):
    value: T

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False

@dataclass
class Failure(Generic[E]):
    error: E

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True

Result = Union[Success[T], Failure[E]]


def divide(a: float, b: float) -> Result[float, str]:
    """Returns Result instead of raising exception."""
    if b == 0:
        return Failure("Cannot divide by zero")
    return Success(a / b)


# Usage: Explicit error handling
result = divide(10, 0)
if result.is_success():
    print(f"Result: {result.value}")
else:
    print(f"Error: {result.error}")
```

### 3. Circuit Breaker

**Pattern**: Prevent cascading failures when external service is down

**Good Implementation**:
```python
from enum import Enum
from datetime import datetime, timedelta
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = Lock()

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. Try again after {self.timeout}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
        )

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN


# Usage
payment_circuit = CircuitBreaker(failure_threshold=5, timeout=60)

def charge_customer(customer_id, amount):
    return payment_circuit.call(
        payment_gateway.charge,
        customer_id,
        amount
    )
```

## Testing Patterns

### 1. Test Fixtures

**Pattern**: Reusable test data setup

**Good Implementation**:
```python
import pytest
from datetime import datetime, timedelta

@pytest.fixture
def sample_user():
    """Fixture providing a sample user for tests."""
    return User(
        id=1,
        email="test@example.com",
        username="testuser",
        created_at=datetime.now()
    )

@pytest.fixture
def sample_order(sample_user):
    """Fixture using another fixture."""
    return Order(
        id=100,
        user=sample_user,
        items=[
            OrderItem(product_id=1, quantity=2, price=Decimal('10.00')),
            OrderItem(product_id=2, quantity=1, price=Decimal('25.00'))
        ],
        created_at=datetime.now()
    )

@pytest.fixture
def db_session():
    """Fixture for database session with cleanup."""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()

# Usage
def test_order_total(sample_order):
    assert sample_order.total == Decimal('45.00')

def test_save_order(db_session, sample_order):
    db_session.add(sample_order)
    db_session.commit()
    assert sample_order.id is not None
```

### 2. Parameterized Tests

**Pattern**: Test multiple cases without duplication

**Good Implementation**:
```python
import pytest

@pytest.mark.parametrize("password,expected", [
    ("short", False),           # Too short
    ("12345678", False),        # No uppercase
    ("PASSWORD", False),        # No lowercase
    ("Password", False),        # No number
    ("Password1", True),        # Valid
    ("P@ssw0rd!", True),        # Valid with special chars
])
def test_password_validation(password, expected):
    assert validate_password(password) == expected


@pytest.mark.parametrize("weight,expected_cost", [
    (0.5, Decimal('9.99')),    # Lightweight
    (4.9, Decimal('9.99')),
    (5.0, Decimal('19.99')),   # Medium
    (19.9, Decimal('19.99')),
    (20.0, Decimal('29.99')),  # Heavy
    (100.0, Decimal('29.99')),
])
def test_shipping_cost_calculation(weight, expected_cost):
    assert calculate_shipping_cost(weight) == expected_cost
```

### 3. Test Doubles (Mocks, Stubs, Spies)

**Pattern**: Isolate unit under test

**Good Implementation**:
```python
from unittest.mock import Mock, patch

class TestUserRegistration:
    def test_sends_welcome_email(self):
        """Test using mock to verify behavior."""
        mock_email_service = Mock(spec=EmailService)
        mock_repository = Mock(spec=UserRepository)

        service = UserRegistrationService(
            email_service=mock_email_service,
            repository=mock_repository
        )

        user = service.register("test@example.com", "password")

        # Verify email service was called
        mock_email_service.send_welcome_email.assert_called_once_with(user)

    def test_handles_email_service_failure(self):
        """Test error handling with mock."""
        mock_email_service = Mock(spec=EmailService)
        mock_email_service.send_welcome_email.side_effect = EmailServiceError()

        service = UserRegistrationService(
            email_service=mock_email_service,
            repository=Mock()
        )

        # Should not raise - email failure shouldn't prevent registration
        user = service.register("test@example.com", "password")
        assert user is not None

    @patch('payment_gateway.charge')
    def test_payment_processing(self, mock_charge):
        """Test using patch decorator."""
        mock_charge.return_value = PaymentResult(
            success=True,
            transaction_id="txn_123"
        )

        result = process_payment(order_id="ORD-123", amount=Decimal('100.00'))

        assert result.success
        mock_charge.assert_called_once()
```

## Security Patterns

### 1. Input Sanitization

**Pattern**: Clean and validate all input

**Good Implementation**:
```python
import bleach
from html import escape

def sanitize_user_input(text: str, allow_html: bool = False) -> str:
    """Sanitize user input to prevent XSS."""
    if not allow_html:
        # Escape all HTML
        return escape(text)

    # Allow safe HTML tags only
    allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'li', 'ol']
    allowed_attributes = {}

    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier (table/column name)."""
    # Allow only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")
    return identifier
```

### 2. Secure Configuration

**Pattern**: Externalize secrets, validate configuration

**Good Implementation**:
```python
import os
from pydantic import BaseSettings, validator, SecretStr

class Settings(BaseSettings):
    """Application settings with validation."""

    # Database
    database_url: SecretStr
    database_pool_size: int = 10

    # API Keys (never hard-coded)
    stripe_api_key: SecretStr
    sendgrid_api_key: SecretStr

    # Security
    secret_key: SecretStr
    jwt_expiration_hours: int = 24

    # Environment
    environment: str = "production"
    debug: bool = False

    @validator('environment')
    def validate_environment(cls, v):
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @validator('debug')
    def validate_debug_in_production(cls, v, values):
        if values.get('environment') == 'production' and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v

    class Config:
        env_file = '.env'
        case_sensitive = False


# Usage
settings = Settings()  # Loads from environment variables or .env file
```

---

Understanding these patterns helps identify well-structured code and anti-patterns that need refactoring during code review.
