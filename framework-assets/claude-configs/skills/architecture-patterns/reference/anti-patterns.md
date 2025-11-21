# Anti-Patterns Reference

**Common mistakes to avoid in software architecture and design.**

## Overview

Anti-patterns are common responses to recurring problems that are usually ineffective and risk being counterproductive.

common_anti_patterns[8]{anti_pattern,description,symptoms,solution}:
God Object,Single class knows/does too much,1000+ line classes multiple responsibilities,Apply SRP split into focused classes
Spaghetti Code,Unstructured tangled control flow,Deep nesting unclear logic,Extract methods use early returns
Magic Numbers,Hard-coded values without explanation,Unclear intent difficult changes,Use named constants
Premature Optimization,Optimizing before identifying bottlenecks,Complex code wasted effort,Profile first optimize later
Circular Dependencies,Modules depending on each other,Import errors brittle design,Introduce abstraction layer
Tight Coupling,Components highly dependent on implementation details,Changes cascade cannot swap,Depend on abstractions interfaces
Copy-Paste Programming,Duplicating code instead of abstracting,Scattered logic maintenance nightmare,Apply DRY extract common logic
Big Ball of Mud,No clear architecture structure,Everything depends on everything,Introduce layers enforce boundaries

---

## 1. God Object / God Class

**Problem:** A single class that has too many responsibilities and knows too much about the system.

**Symptoms:**
- Class has 500+ lines of code
- Class name contains "Manager", "Handler", "Util", or "Helper"
- Class has 10+ methods
- Class has many unrelated responsibilities
- Difficult to test
- Changes for unrelated features modify same class

### Bad Example

```python
# DON'T - God class with too many responsibilities
class UserManager:
    def __init__(self, db_session, smtp_config, cache, logger):
        self.db = db_session
        self.smtp = smtp_config
        self.cache = cache
        self.logger = logger

    # Database responsibility
    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def save_user(self, user: User):
        self.db.add(user)
        self.db.commit()

    # Validation responsibility
    def validate_email(self, email: str):
        return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

    def validate_password(self, password: str):
        return len(password) >= 8

    # Business logic responsibility
    def create_user(self, email, name, password):
        if not self.validate_email(email):
            raise ValueError("Invalid email")
        user = User(email=email, name=name)
        self.save_user(user)
        self.send_welcome_email(user)
        self.log_user_creation(user)
        return user

    # Email responsibility
    def send_welcome_email(self, user: User):
        smtp.send(user.email, "Welcome", f"Hello {user.name}")

    def send_password_reset(self, user: User, token: str):
        smtp.send(user.email, "Reset", f"Token: {token}")

    # Logging responsibility
    def log_user_creation(self, user: User):
        self.logger.info(f"User created: {user.id}")

    def log_user_login(self, user: User):
        self.logger.info(f"User login: {user.id}")

    # Caching responsibility
    def cache_user(self, user: User):
        self.cache.set(f"user_{user.id}", user)

    def get_cached_user(self, user_id: int):
        return self.cache.get(f"user_{user_id}")

    # Authentication responsibility
    def authenticate(self, email: str, password: str):
        user = self.find_by_email(email)
        return check_password(password, user.password_hash)

    # ... and many more methods
```

### Good Solution

```python
# DO - Separate responsibilities into focused classes

class UserRepository:
    """Only handles data access"""
    def __init__(self, db_session):
        self.db = db_session

    def get(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        return user


class UserValidator:
    """Only handles validation"""
    @staticmethod
    def validate_email(email: str) -> bool:
        return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        return len(password) >= 8


class EmailService:
    """Only handles email sending"""
    def __init__(self, smtp_config):
        self.smtp = smtp_config

    def send_welcome_email(self, user: User):
        smtp.send(user.email, "Welcome", f"Hello {user.name}")


class UserService:
    """Only handles business logic"""
    def __init__(self, repository, validator, email_service):
        self.repository = repository
        self.validator = validator
        self.email_service = email_service

    def create_user(self, email, name, password) -> User:
        if not self.validator.validate_email(email):
            raise ValueError("Invalid email")
        user = User(email=email, name=name)
        saved_user = self.repository.save(user)
        self.email_service.send_welcome_email(saved_user)
        return saved_user
```

---

## 2. Spaghetti Code

**Problem:** Unstructured, tangled control flow that's hard to follow.

**Symptoms:**
- Deep nesting (5+ levels)
- No clear structure
- Hard to understand logic flow
- Difficult to test
- Many interdependent conditions

### Bad Example

```python
# DON'T - Deeply nested spaghetti code
def process_order(order_id):
    order = get_order(order_id)
    if order:
        if order.status == "pending":
            if check_inventory(order):
                if process_payment(order):
                    update_inventory(order)
                    if send_confirmation(order):
                        if update_shipping(order):
                            update_order_status(order, "completed")
                            return {"success": True}
                        else:
                            update_order_status(order, "shipping_error")
                            return {"success": False, "error": "shipping"}
                    else:
                        update_order_status(order, "email_error")
                        rollback_payment(order)
                        return {"success": False, "error": "email"}
                else:
                    update_order_status(order, "payment_failed")
                    return {"success": False, "error": "payment"}
            else:
                update_order_status(order, "out_of_stock")
                return {"success": False, "error": "stock"}
        else:
            return {"success": False, "error": "invalid_status"}
    else:
        return {"success": False, "error": "not_found"}
```

### Good Solution

```python
# DO - Flat structure with early returns
def process_order(order_id: str) -> OrderResult:
    # Validate order exists
    order = get_order(order_id)
    if not order:
        return OrderResult.error("not_found", "Order not found")

    # Validate status
    if order.status != "pending":
        return OrderResult.error("invalid_status", f"Order status is {order.status}")

    # Check inventory
    if not check_inventory(order):
        update_order_status(order, "out_of_stock")
        return OrderResult.error("out_of_stock", "Items not available")

    # Process payment
    payment_result = process_payment(order)
    if not payment_result.success:
        update_order_status(order, "payment_failed")
        return OrderResult.error("payment_failed", payment_result.error)

    # Update inventory
    update_inventory(order)

    # Send confirmation
    if not send_confirmation(order):
        update_order_status(order, "email_error")
        rollback_payment(order)
        return OrderResult.error("email_error", "Failed to send confirmation")

    # Update shipping
    if not update_shipping(order):
        update_order_status(order, "shipping_error")
        return OrderResult.error("shipping_error", "Failed to update shipping")

    # Complete order
    update_order_status(order, "completed")
    return OrderResult.success(order)
```

---

## 3. Magic Numbers and Strings

**Problem:** Hard-coded values without explanation of their meaning.

**Symptoms:**
- Unexplained numbers in code
- Hard-coded strings
- Unclear intent
- Difficult to change values
- No single source of truth

### Bad Example

```python
# DON'T - Magic numbers and strings
def calculate_price(quantity: int, customer_type: str) -> float:
    base_price = quantity * 19.99

    if customer_type == "gold":
        return base_price * 0.8
    elif customer_type == "silver":
        return base_price * 0.9
    elif customer_type == "bronze":
        return base_price * 0.95
    else:
        return base_price

def get_shipping_cost(weight: float) -> float:
    if weight < 1:
        return 4.99
    elif weight < 5:
        return 9.99
    elif weight < 10:
        return 14.99
    else:
        return 19.99
```

### Good Solution

```python
# DO - Named constants
# Configuration constants
UNIT_PRICE = 19.99

# Customer tier discounts
CUSTOMER_TIERS = {
    "gold": 0.20,    # 20% discount
    "silver": 0.10,  # 10% discount
    "bronze": 0.05,  # 5% discount
}

# Shipping tiers (weight in kg, cost in USD)
SHIPPING_TIERS = [
    (1.0, 4.99),
    (5.0, 9.99),
    (10.0, 14.99),
    (float('inf'), 19.99),
]

def calculate_price(quantity: int, customer_tier: str) -> float:
    base_price = quantity * UNIT_PRICE
    discount = CUSTOMER_TIERS.get(customer_tier, 0.0)
    return base_price * (1 - discount)

def get_shipping_cost(weight: float) -> float:
    for max_weight, cost in SHIPPING_TIERS:
        if weight < max_weight:
            return cost
    return SHIPPING_TIERS[-1][1]  # Fallback to highest tier
```

---

## 4. Premature Optimization

**Problem:** Optimizing code before identifying actual performance bottlenecks.

**Symptoms:**
- Complex code for unproven performance gains
- Over-engineered solutions
- Micro-optimizations everywhere
- Sacrificing readability for speed
- No profiling data to justify optimization

### Bad Example

```python
# DON'T - Premature optimization
class UserCache:
    """Over-optimized cache before measuring if caching is even needed"""
    def __init__(self, max_size=10000):
        self.cache = {}
        self.lru_queue = deque(maxlen=max_size)
        self.access_counts = defaultdict(int)
        self.last_access_time = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def get(self, user_id: int) -> Optional[User]:
        if user_id in self.cache:
            self.cache_hits += 1
            self.access_counts[user_id] += 1
            self.last_access_time[user_id] = time.time()
            self.lru_queue.remove(user_id)
            self.lru_queue.append(user_id)
            return self.cache[user_id]
        else:
            self.cache_misses += 1
            return None

    # ... complex eviction logic, statistics, etc.
```

### Good Solution

```python
# DO - Start simple, optimize if needed
class UserCache:
    """Simple cache - will optimize if profiling shows it's needed"""
    def __init__(self):
        self.cache: dict[int, User] = {}

    def get(self, user_id: int) -> Optional[User]:
        return self.cache.get(user_id)

    def set(self, user_id: int, user: User):
        self.cache[user_id] = user

    def clear(self):
        self.cache.clear()

# If profiling shows caching is bottleneck, THEN optimize:
# - Add LRU eviction if memory is issue
# - Add TTL if staleness is issue
# - Add metrics if monitoring is needed
```

---

## 5. Circular Dependencies

**Problem:** Two or more modules depend on each other, creating import cycles.

**Symptoms:**
- Import errors
- Difficult to understand module structure
- Hard to test in isolation
- Brittle design

### Bad Example

```python
# DON'T - Circular dependency

# user_service.py
from order_service import OrderService

class UserService:
    def __init__(self):
        self.order_service = OrderService()

    def get_user_with_orders(self, user_id: int):
        user = self.get_user(user_id)
        orders = self.order_service.get_user_orders(user_id)
        return {"user": user, "orders": orders}


# order_service.py
from user_service import UserService  # Circular import!

class OrderService:
    def __init__(self):
        self.user_service = UserService()

    def create_order(self, user_id: int, items: list):
        user = self.user_service.get_user(user_id)  # Uses UserService
        # Create order...
```

### Good Solution

```python
# DO - Break circular dependency with abstraction

# domain/user.py
@dataclass
class User:
    id: int
    email: str
    name: str

# domain/order.py
@dataclass
class Order:
    id: str
    user_id: int
    items: list

# repositories/user_repository.py
class IUserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[User]:
        pass

# repositories/order_repository.py
class IOrderRepository(ABC):
    @abstractmethod
    def get_user_orders(self, user_id: int) -> list[Order]:
        pass

# services/user_service.py
class UserService:
    def __init__(self, user_repo: IUserRepository, order_repo: IOrderRepository):
        self.user_repo = user_repo
        self.order_repo = order_repo

    def get_user_with_orders(self, user_id: int):
        user = self.user_repo.get_user(user_id)
        orders = self.order_repo.get_user_orders(user_id)
        return {"user": user, "orders": orders}

# services/order_service.py
class OrderService:
    def __init__(self, user_repo: IUserRepository, order_repo: IOrderRepository):
        self.user_repo = user_repo
        self.order_repo = order_repo

    def create_order(self, user_id: int, items: list):
        user = self.user_repo.get_user(user_id)
        # Create order...
```

---

## Anti-Pattern Detection Checklist

detection_checklist[10]{anti_pattern,detection_question,threshold}:
God Object,Does class have more than 5 responsibilities?,Yes = Problem
God Object,Is class longer than 300 lines?,Yes = Warning
Spaghetti Code,Is nesting deeper than 3 levels?,Yes = Warning
Magic Numbers,Are there unexplained numbers in code?,Yes = Problem
Tight Coupling,Does change in one class require changes in many others?,Yes = Problem
Circular Dependencies,Do modules import each other?,Yes = Problem
Copy-Paste Code,Is same logic repeated in 3+ places?,Yes = Problem
Premature Optimization,Is code complex without profiling data?,Yes = Warning
Poor Naming,Are variable names less than 3 chars or unclear?,Yes = Warning
No Abstraction,Is concrete implementation used everywhere?,Yes = Problem

---

**File Size**: 320/500 lines max ✅
