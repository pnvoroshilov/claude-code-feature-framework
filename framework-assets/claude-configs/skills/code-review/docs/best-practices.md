# Code Review Best Practices

## Table of Contents

- [Universal Best Practices](#universal-best-practices)
- [Language-Specific Best Practices](#language-specific-best-practices)
- [Security Review Best Practices](#security-review-best-practices)
- [Performance Review Best Practices](#performance-review-best-practices)
- [Testing Best Practices](#testing-best-practices)
- [Documentation Best Practices](#documentation-best-practices)
- [API Design Best Practices](#api-design-best-practices)
- [Database Best Practices](#database-best-practices)
- [Frontend Best Practices](#frontend-best-practices)
- [Error Handling Best Practices](#error-handling-best-practices)

## Universal Best Practices

### 1. Code Readability

**Best Practice**: Write code for humans first, computers second

**Guidelines**:
- Use descriptive, meaningful names
- Keep functions small and focused (<50 lines)
- Limit nesting depth (max 3-4 levels)
- Add comments for complex logic only
- Use consistent formatting
- Follow language idioms

**Good Example**:
```python
def calculate_order_total_with_discounts(
    items: List[OrderItem],
    customer: Customer,
    promotional_code: Optional[str] = None
) -> Decimal:
    """Calculate order total including all applicable discounts.

    Args:
        items: List of items in the order
        customer: Customer placing the order
        promotional_code: Optional promotional code for additional discount

    Returns:
        Final total after all discounts applied
    """
    subtotal = sum(item.price * item.quantity for item in items)
    customer_discount = calculate_customer_loyalty_discount(customer, subtotal)
    promo_discount = apply_promotional_code(promotional_code, subtotal)

    return subtotal - customer_discount - promo_discount
```

**Bad Example**:
```python
def calc(i, c, p=None):  # Unclear names
    t = 0
    for x in i:  # Single letter variables
        t += x[0] * x[1]  # Magic numbers
    d1 = c.d * t if c.d else 0  # Unclear logic
    d2 = p.d if p else 0
    return t - d1 - d2
```

### 2. Single Responsibility Principle (SRP)

**Best Practice**: Each function/class should have one, and only one, reason to change

**Guidelines**:
- Functions do one thing well
- Classes represent one cohesive concept
- Separate concerns (business logic, data access, presentation)
- Extract mixed responsibilities

**Good Example**:
```python
class UserRegistration:
    """Handles user registration business logic only."""

    def register_user(self, email: str, password: str) -> User:
        self._validate_email(email)
        self._validate_password(password)
        hashed_password = self._hash_password(password)
        return User(email=email, password_hash=hashed_password)

class UserRepository:
    """Handles user data persistence only."""

    def save(self, user: User) -> int:
        return self.db.insert('users', user.to_dict())

class EmailService:
    """Handles email sending only."""

    def send_welcome_email(self, user: User) -> None:
        self.email_client.send(
            to=user.email,
            subject="Welcome!",
            body=self._render_welcome_template(user)
        )
```

**Bad Example**:
```python
class UserManager:
    """God class doing everything - violates SRP."""

    def register_user(self, email, password):
        # Validation
        if '@' not in email:
            raise ValueError("Invalid email")

        # Password hashing
        hashed = hashlib.sha256(password.encode()).hexdigest()

        # Database insertion
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users...")

        # Email sending
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail('noreply@...', email, "Welcome!")

        # Logging
        logger.info(f"User {email} registered")

        return user_id
```

### 3. DRY (Don't Repeat Yourself)

**Best Practice**: Avoid code duplication; extract common logic

**Guidelines**:
- Extract duplicate code to functions
- Use inheritance/composition for common behavior
- Create utility modules for shared functionality
- Use configuration for repeated values
- Wait for 3rd occurrence before extracting (rule of three)

**Good Example**:
```python
def validate_field_length(field_name: str, value: str, min_length: int, max_length: int) -> None:
    """Reusable validation function."""
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters")
    if len(value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters")

def validate_username(username: str) -> None:
    validate_field_length("Username", username, 3, 20)

def validate_password(password: str) -> None:
    validate_field_length("Password", password, 8, 128)
```

**Bad Example**:
```python
def validate_username(username: str) -> None:
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters")
    if len(username) > 20:
        raise ValidationError("Username cannot exceed 20 characters")

def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    if len(password) > 128:
        raise ValidationError("Password cannot exceed 128 characters")
```

### 4. Error Handling

**Best Practice**: Handle errors explicitly and provide meaningful messages

**Guidelines**:
- Use specific exception types
- Provide context in error messages
- Don't swallow exceptions silently
- Clean up resources in finally blocks
- Log errors appropriately
- Fail fast for invalid states

**Good Example**:
```python
def process_payment(order_id: str, amount: Decimal) -> PaymentResult:
    """Process payment with comprehensive error handling."""
    try:
        order = Order.get_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")

        if order.status != OrderStatus.PENDING:
            raise InvalidOrderStateError(
                f"Cannot process payment for order {order_id} with status {order.status}"
            )

        payment_gateway = PaymentGateway()
        result = payment_gateway.charge(amount, order.customer.payment_method)

        order.mark_paid(result.transaction_id)
        return result

    except PaymentGatewayError as e:
        logger.error(f"Payment gateway error for order {order_id}: {e}")
        raise PaymentProcessingError(f"Failed to process payment: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error processing payment for order {order_id}: {e}")
        raise
```

**Bad Example**:
```python
def process_payment(order_id, amount):
    try:
        order = Order.get(order_id)
        payment_gateway.charge(amount)
        order.paid = True
    except:  # Catching all exceptions
        pass  # Silently swallowing errors
```

### 5. Code Comments

**Best Practice**: Comment "why", not "what"; let code explain "what"

**Guidelines**:
- Explain complex algorithms
- Document non-obvious decisions
- Clarify business rules
- Warn about gotchas
- Don't comment obvious code
- Keep comments up to date

**Good Comments**:
```python
def calculate_shipping_cost(weight: float, distance: float) -> Decimal:
    # Use cubic pricing model as per partnership agreement with ShipCo
    # Effective date: 2024-01-01 (Contract #12345)
    base_rate = Decimal('5.99')

    # Weight factor: $0.50 per kg
    weight_cost = Decimal(str(weight)) * Decimal('0.50')

    # Distance factor: $0.10 per km, capped at 500km
    # Cap prevents excessive charges for remote areas while maintaining profitability
    distance_cost = Decimal(str(min(distance, 500))) * Decimal('0.10')

    return base_rate + weight_cost + distance_cost
```

**Bad Comments**:
```python
def calculate_shipping_cost(weight, distance):
    # Set base rate to 5.99
    base_rate = 5.99

    # Multiply weight by 0.50
    weight_cost = weight * 0.50

    # Calculate distance cost
    distance_cost = min(distance, 500) * 0.10

    # Return total
    return base_rate + weight_cost + distance_cost
```

## Language-Specific Best Practices

### Python Best Practices

**1. Use Type Hints**
```python
# Good
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old"

# Bad
def greet(name, age):
    return f"Hello {name}, you are {age} years old"
```

**2. Use List Comprehensions Appropriately**
```python
# Good: Simple transformation
squares = [x**2 for x in range(10)]

# Good: With filter
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Bad: Too complex (use regular loop)
result = [f(g(h(x))) for x in items if complex_condition(x) and another_check(x)]
```

**3. Use Context Managers**
```python
# Good: Automatic resource cleanup
with open('file.txt', 'r') as f:
    content = f.read()

# Bad: Manual cleanup (error-prone)
f = open('file.txt', 'r')
content = f.read()
f.close()
```

**4. Use f-strings for Formatting**
```python
# Good: Readable and efficient
message = f"User {username} has {count} items"

# Bad: Old style
message = "User %s has %d items" % (username, count)
message = "User {} has {} items".format(username, count)
```

**5. Follow PEP 8**
- 4 spaces for indentation
- Max line length: 79 characters
- Two blank lines between top-level definitions
- Snake_case for functions and variables
- PascalCase for classes

### JavaScript/TypeScript Best Practices

**1. Use const/let, Never var**
```javascript
// Good
const MAX_USERS = 100;
let userCount = 0;

// Bad
var MAX_USERS = 100;
var userCount = 0;
```

**2. Use Arrow Functions Appropriately**
```javascript
// Good: Simple transformations
const doubled = numbers.map(n => n * 2);

// Good: Preserves 'this' context
class Counter {
    count = 0;
    increment = () => {
        this.count++;  // 'this' refers to Counter instance
    }
}

// Bad: Not needed for object methods
const obj = {
    name: 'test',
    getName: () => this.name  // 'this' is not bound correctly
};
```

**3. Use Async/Await Over Promises**
```javascript
// Good: Readable async code
async function fetchUserData(userId) {
    try {
        const user = await api.getUser(userId);
        const orders = await api.getOrders(user.id);
        return { user, orders };
    } catch (error) {
        logger.error('Failed to fetch user data', error);
        throw error;
    }
}

// Bad: Promise chain (less readable)
function fetchUserData(userId) {
    return api.getUser(userId)
        .then(user => api.getOrders(user.id)
            .then(orders => ({ user, orders })))
        .catch(error => {
            logger.error('Failed to fetch user data', error);
            throw error;
        });
}
```

**4. Use Destructuring**
```javascript
// Good: Clean and readable
const { name, email, age } = user;
const [first, second, ...rest] = items;

// Bad: Repetitive
const name = user.name;
const email = user.email;
const age = user.age;
```

**5. Use Optional Chaining**
```javascript
// Good: Safe property access
const streetName = user?.address?.street?.name;

// Bad: Manual null checks
const streetName = user && user.address && user.address.street
    ? user.address.street.name
    : undefined;
```

### TypeScript Specific

**1. Enable Strict Mode**
```json
// tsconfig.json
{
    "compilerOptions": {
        "strict": true,
        "noImplicitAny": true,
        "strictNullChecks": true,
        "strictFunctionTypes": true
    }
}
```

**2. Use Interfaces for Object Shapes**
```typescript
// Good
interface User {
    id: string;
    name: string;
    email: string;
    createdAt: Date;
}

function updateUser(user: User): Promise<void> {
    // Type-safe implementation
}

// Bad: Using 'any'
function updateUser(user: any): Promise<void> {
    // No type safety
}
```

## Security Review Best Practices

### 1. Input Validation

**Best Practice**: Validate all input at boundaries

**Guidelines**:
- Whitelist validation (allow known good)
- Validate type, length, format, range
- Sanitize before use
- Use validation libraries
- Validate on both client and server

**Good Example**:
```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserRegistration(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=20, regex=r'^[a-zA-Z0-9_]+$')
    password: constr(min_length=8, max_length=128)
    age: int

    @validator('age')
    def validate_age(cls, v):
        if v < 13 or v > 120:
            raise ValueError('Age must be between 13 and 120')
        return v
```

**Bad Example**:
```python
def register_user(email, username, password, age):
    # No validation - accepts anything
    user = User(email=email, username=username, password=password, age=age)
    db.save(user)
```

### 2. SQL Injection Prevention

**Best Practice**: Always use parameterized queries

**Good Example**:
```python
# Good: Parameterized query
cursor.execute(
    "SELECT * FROM users WHERE email = %s AND active = %s",
    (email, True)
)

# Good: ORM (automatically parameterizes)
user = User.query.filter_by(email=email, active=True).first()
```

**Bad Example**:
```python
# Bad: String concatenation - SQL injection vulnerability
query = f"SELECT * FROM users WHERE email = '{email}' AND active = TRUE"
cursor.execute(query)
```

### 3. Authentication & Authorization

**Best Practice**: Verify identity and permissions on every request

**Guidelines**:
- Use established auth libraries (OAuth, JWT)
- Store password hashes, never plaintext
- Use strong hashing (bcrypt, argon2)
- Implement rate limiting
- Use multi-factor authentication
- Check authorization on every protected resource

**Good Example**:
```python
from passlib.hash import argon2

def register_user(username: str, password: str) -> User:
    # Hash password with strong algorithm
    password_hash = argon2.hash(password)
    user = User(username=username, password_hash=password_hash)
    return user

def verify_password(user: User, password: str) -> bool:
    return argon2.verify(password, user.password_hash)

@app.route('/admin/users')
@require_auth
@require_role('admin')  # Authorization check
def list_users():
    # Only admins can access
    return User.query.all()
```

**Bad Example**:
```python
def register_user(username, password):
    # Bad: Storing plaintext password
    user = User(username=username, password=password)
    return user

def verify_password(user, password):
    # Bad: Direct comparison of plaintext
    return user.password == password

@app.route('/admin/users')
@require_auth  # Only checks authentication, not authorization
def list_users():
    # Anyone authenticated can access admin endpoint
    return User.query.all()
```

### 4. XSS Prevention

**Best Practice**: Escape output, validate input, use Content Security Policy

**Good Example**:
```javascript
// Good: Use framework's built-in escaping
function UserProfile({ user }) {
    return (
        <div>
            {/* React automatically escapes */}
            <h1>{user.name}</h1>
            <p>{user.bio}</p>
        </div>
    );
}

// Good: Explicit escaping when needed
import DOMPurify from 'dompurify';

function RichContent({ html }) {
    const clean = DOMPurify.sanitize(html);
    return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

**Bad Example**:
```javascript
// Bad: Direct HTML insertion - XSS vulnerability
function UserProfile({ user }) {
    return (
        <div>
            {/* Dangerous: user.name could contain <script> tags */}
            <div dangerouslySetInnerHTML={{ __html: user.name }} />
        </div>
    );
}
```

### 5. CSRF Protection

**Best Practice**: Use CSRF tokens for state-changing operations

**Good Example**:
```python
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
@csrf.protect()  # Validates CSRF token
def transfer_money():
    amount = request.form['amount']
    recipient = request.form['recipient']
    # Process transfer
```

**Bad Example**:
```python
@app.route('/transfer', methods=['POST'])
def transfer_money():
    # No CSRF protection - vulnerable to cross-site requests
    amount = request.form['amount']
    recipient = request.form['recipient']
    # Process transfer
```

## Performance Review Best Practices

### 1. Database Query Optimization

**Best Practice**: Minimize queries, use indexes, avoid N+1 problems

**Good Example**:
```python
# Good: Single query with join (eager loading)
users = (
    db.session.query(User)
    .options(joinedload(User.profile))
    .options(joinedload(User.orders))
    .filter(User.active == True)
    .all()
)

for user in users:
    print(f"{user.name}: {len(user.orders)} orders")  # No additional queries

# Good: Add appropriate indexes
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, index=True)  # Frequently filtered
```

**Bad Example**:
```python
# Bad: N+1 query problem
users = User.query.filter_by(active=True).all()

for user in users:
    # Each iteration makes a separate query
    print(f"{user.name}: {len(user.orders)} orders")

# Bad: No indexes on frequently queried columns
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)  # No index despite frequent lookups
    created_at = Column(DateTime)  # No index despite frequent filtering
```

### 2. Caching Strategy

**Best Practice**: Cache expensive computations and frequently accessed data

**Good Example**:
```python
from functools import lru_cache
from redis import Redis

# Good: Cache expensive computation
@lru_cache(maxsize=1000)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Good: Cache database queries
class UserService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def get_user(self, user_id: int) -> User:
        cache_key = f"user:{user_id}"

        # Check cache first
        cached = self.redis.get(cache_key)
        if cached:
            return User.from_json(cached)

        # Cache miss - query database
        user = User.query.get(user_id)
        if user:
            self.redis.setex(cache_key, 3600, user.to_json())

        return user
```

**Bad Example**:
```python
# Bad: Recalculating expensive operation every time
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Bad: No caching of database queries
class UserService:
    def get_user(self, user_id: int) -> User:
        # Always hits database
        return User.query.get(user_id)
```

### 3. Algorithm Complexity

**Best Practice**: Choose appropriate algorithms for the scale

**Good Example**:
```python
# Good: O(n log n) - Efficient for large datasets
def find_duplicates(items: List[int]) -> Set[int]:
    sorted_items = sorted(items)  # O(n log n)
    duplicates = set()

    for i in range(len(sorted_items) - 1):
        if sorted_items[i] == sorted_items[i + 1]:
            duplicates.add(sorted_items[i])

    return duplicates

# Good: O(n) - Even better using hash set
def find_duplicates_optimal(items: List[int]) -> Set[int]:
    seen = set()
    duplicates = set()

    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates
```

**Bad Example**:
```python
# Bad: O(n²) - Inefficient for large datasets
def find_duplicates(items: List[int]) -> Set[int]:
    duplicates = set()

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.add(items[i])

    return duplicates
```

## Testing Best Practices

### 1. Test Coverage

**Best Practice**: Aim for 80%+ coverage, 100% for critical paths

**Guidelines**:
- Test critical business logic thoroughly
- Test error handling paths
- Test edge cases and boundaries
- Don't test framework code
- Focus on behavior, not implementation

**Good Example**:
```python
import pytest
from decimal import Decimal

class TestOrderCalculation:
    """Comprehensive test coverage for order calculations."""

    def test_basic_order_total(self):
        """Test simple order total calculation."""
        items = [
            OrderItem(price=Decimal('10.00'), quantity=2),
            OrderItem(price=Decimal('5.50'), quantity=3)
        ]
        total = calculate_order_total(items)
        assert total == Decimal('36.50')

    def test_empty_order(self):
        """Test edge case: empty order."""
        total = calculate_order_total([])
        assert total == Decimal('0.00')

    def test_order_with_discounts(self):
        """Test order with customer discount applied."""
        items = [OrderItem(price=Decimal('100.00'), quantity=1)]
        customer = Customer(loyalty_discount=Decimal('0.10'))
        total = calculate_order_total(items, customer)
        assert total == Decimal('90.00')

    def test_negative_quantity_raises_error(self):
        """Test validation: negative quantities not allowed."""
        items = [OrderItem(price=Decimal('10.00'), quantity=-1)]
        with pytest.raises(ValidationError, match="Quantity must be positive"):
            calculate_order_total(items)

    def test_large_order(self):
        """Test performance: large number of items."""
        items = [OrderItem(price=Decimal('1.00'), quantity=1)] * 10000
        total = calculate_order_total(items)
        assert total == Decimal('10000.00')
```

### 2. Test Independence

**Best Practice**: Each test should run independently, in any order

**Good Example**:
```python
import pytest

@pytest.fixture
def clean_database():
    """Set up fresh database for each test."""
    db.create_all()
    yield
    db.drop_all()

class TestUserRegistration:
    def test_register_new_user(self, clean_database):
        """Each test gets clean database."""
        user = register_user('test@example.com', 'password123')
        assert user.id is not None

    def test_duplicate_email_rejected(self, clean_database):
        """Independent test with own database state."""
        register_user('test@example.com', 'password123')
        with pytest.raises(ValidationError):
            register_user('test@example.com', 'different_password')
```

**Bad Example**:
```python
class TestUserRegistration:
    # Bad: Tests depend on execution order

    def test_1_register_new_user(self):
        self.user = register_user('test@example.com', 'password123')
        assert self.user.id is not None

    def test_2_duplicate_email_rejected(self):
        # Depends on test_1 running first
        with pytest.raises(ValidationError):
            register_user('test@example.com', 'different_password')
```

### 3. Test Naming

**Best Practice**: Use descriptive names that explain what is tested

**Good Example**:
```python
def test_user_cannot_purchase_product_when_out_of_stock():
    """Clear name explains scenario and expected outcome."""
    pass

def test_order_total_includes_tax_for_taxable_items():
    """Name describes specific business rule being tested."""
    pass

def test_admin_can_delete_any_user_account():
    """Name specifies authorization scenario."""
    pass
```

**Bad Example**:
```python
def test_1():  # Unclear what this tests
    pass

def test_user():  # Too vague
    pass

def test_works():  # No information about what works
    pass
```

## Documentation Best Practices

### 1. Function/Method Documentation

**Best Practice**: Document public APIs with clear docstrings

**Good Example**:
```python
def calculate_shipping_cost(
    origin: Address,
    destination: Address,
    weight: float,
    service_level: ShippingService
) -> Decimal:
    """Calculate shipping cost based on distance and weight.

    Uses the carrier's cubic pricing model with distance-based
    multipliers. Costs are calculated in USD.

    Args:
        origin: Shipping origin address
        destination: Delivery destination address
        weight: Package weight in kilograms
        service_level: Shipping service (STANDARD, EXPRESS, OVERNIGHT)

    Returns:
        Shipping cost in USD

    Raises:
        InvalidAddressError: If origin or destination is incomplete
        InvalidWeightError: If weight is negative or exceeds 50kg

    Example:
        >>> origin = Address(city="New York", state="NY", zip="10001")
        >>> dest = Address(city="Los Angeles", state="CA", zip="90001")
        >>> cost = calculate_shipping_cost(origin, dest, 2.5, ShippingService.STANDARD)
        >>> print(cost)
        Decimal('15.99')

    Note:
        Prices updated quarterly based on carrier contract.
        See internal wiki for pricing history and negotiation docs.
    """
    # Implementation
```

### 2. Code Comments

**Best Practice**: Comment "why" and complex logic, not "what"

**Good Comments**:
```python
def process_refund(order_id: str, amount: Decimal) -> RefundResult:
    # Stripe requires amounts in cents (integer)
    amount_cents = int(amount * 100)

    # Refunds must be processed within 180 days of charge per Stripe policy
    if order.days_since_purchase() > 180:
        raise RefundWindowExpiredError()

    # Use idempotency key to prevent duplicate refunds if request is retried
    idempotency_key = f"refund-{order_id}-{int(time.time())}"

    return stripe_client.refund(charge_id, amount_cents, idempotency_key)
```

**Bad Comments**:
```python
def process_refund(order_id, amount):
    # Convert to cents
    amount_cents = int(amount * 100)

    # Check if greater than 180
    if order.days_since_purchase() > 180:
        # Raise error
        raise RefundWindowExpiredError()

    # Create key
    idempotency_key = f"refund-{order_id}-{int(time.time())}"

    # Call stripe
    return stripe_client.refund(charge_id, amount_cents, idempotency_key)
```

### 3. README and Setup Documentation

**Best Practice**: Include comprehensive setup and usage instructions

**Good README Structure**:
```markdown
# Project Name

Brief description of what the project does.

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+

## Installation

\`\`\`bash
# Clone repository
git clone https://github.com/org/project.git
cd project

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb project_db
alembic upgrade head

# Configure environment
cp .env.example .env
# Edit .env with your settings
\`\`\`

## Running

\`\`\`bash
# Development server
python run.py

# Production (using gunicorn)
gunicorn app:app -w 4 -b 0.0.0.0:8000
\`\`\`

## Testing

\`\`\`bash
# Run all tests
pytest

# With coverage
pytest --cov=app tests/
\`\`\`

## Architecture

Brief overview of system architecture and key components.

## Contributing

See CONTRIBUTING.md for development workflow and standards.

## License

MIT License - see LICENSE file.
```

---

These best practices form the foundation for high-quality, maintainable code. Apply them consistently during code reviews to improve overall code quality.
