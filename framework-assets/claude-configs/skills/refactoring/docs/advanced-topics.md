# Advanced Refactoring Topics

Expert-level refactoring techniques for complex scenarios, large-scale systems, and challenging legacy codebases.

## Table of Contents

- [Legacy Code Refactoring](#legacy-code-refactoring)
- [Large-Scale Refactoring](#large-scale-refactoring)
- [Architecture Migration](#architecture-migration)
- [Database Refactoring](#database-refactoring)
- [API Evolution](#api-evolution)
- [Performance Refactoring](#performance-refactoring)
- [Concurrent Code Refactoring](#concurrent-code-refactoring)
- [Microservices Refactoring](#microservices-refactoring)

## Legacy Code Refactoring

### Understanding Legacy Code

**Characteristics**:
- No tests (or poor tests)
- Complex dependencies
- Unclear business logic
- Fear of changes
- Multiple authors over years

### The Legacy Code Dilemma

> "To refactor safely, we need tests. To add tests, we need to refactor."

**Solution**: Break the cycle with careful seams and characterization tests.

### Characterization Testing

Document existing behavior before refactoring.

**Example**:
```python
# Legacy code (unclear what it does)
def calculate(x, y, z):
    if x > 10:
        return ((y * 2) + z) * 1.1
    else:
        return y + (z * 0.5)

# Characterization tests
def test_calculate_behavior():
    """Document current behavior, even if seems wrong"""
    assert calculate(15, 10, 5) == 27.5  # (10*2 + 5) * 1.1
    assert calculate(5, 10, 4) == 12.0   # 10 + (4 * 0.5)
    assert calculate(10, 0, 10) == 5.0   # 0 + (10 * 0.5)
    # Note: x=10 uses else branch (not >10)
```

**Steps**:
1. Exercise the code with various inputs
2. Record actual outputs (not expected)
3. Create tests that pass with current behavior
4. Now safe to refactor

### Finding Seams

**Seam**: Place where you can alter behavior without editing code.

#### Object Seam

```java
// Legacy code with database coupling
public class OrderProcessor {
    public void process(Order order) {
        Database db = new Database();  // Hard-coded dependency
        db.save(order);
    }
}

// Create seam through subclassing
public class TestableOrderProcessor extends OrderProcessor {
    private Database testDatabase;

    public void setDatabase(Database db) {
        this.testDatabase = db;
    }
}

// Now can inject mock in tests
```

#### Preprocessing Seam

```c
// Legacy C code
void processData() {
    #ifdef TESTING
        // Test implementation
    #else
        // Production implementation
    #endif
}
```

### Sprout Method/Class

Add new functionality without modifying legacy code.

**Sprout Method**:
```python
# Legacy method (don't touch)
def process_payment(payment):
    # 200 lines of scary legacy code
    pass

# New requirement: log all payments
def log_payment(payment):
    logger.info(f"Processing payment: {payment.id}")

# Modify legacy to call new method
def process_payment(payment):
    log_payment(payment)  # New line
    # 200 lines of scary legacy code
    pass
```

**Sprout Class**:
```java
// Legacy class (complex, no tests)
public class LegacyOrderService {
    public void processOrder(Order order) {
        // 500 lines
    }
}

// New functionality in new class (fully tested)
public class OrderValidator {
    public ValidationResult validate(Order order) {
        // New logic with tests
    }
}

// Use in legacy
public class LegacyOrderService {
    private OrderValidator validator = new OrderValidator();

    public void processOrder(Order order) {
        ValidationResult result = validator.validate(order);
        if (!result.isValid()) return;
        // 500 lines
    }
}
```

### Wrap Method/Class

Wrap legacy code to add new behavior.

**Wrap Method**:
```python
# Legacy method
def add_user(user):
    database.save(user)

# Rename legacy
def add_user_to_database(user):
    database.save(user)

# New wrapper adds behavior
def add_user(user):
    add_user_to_database(user)
    send_welcome_email(user)
    log_user_creation(user)
```

### Strangler Fig Pattern

Gradually replace legacy system.

```
┌─────────────────┐
│  Legacy System  │
│  (Monolith)     │
└────────┬────────┘
         │
    ┌────▼────────────────────────┐
    │  Strangler Facade Layer     │
    │  Routes to old or new       │
    └────┬───────────────┬────────┘
         │               │
    ┌────▼────┐    ┌────▼──────┐
    │ Legacy  │    │ New       │
    │ Code    │    │ Service   │
    └─────────┘    └───────────┘
```

**Implementation**:
```python
class OrderFacade:
    def __init__(self):
        self.legacy_service = LegacyOrderService()
        self.new_service = NewOrderService()
        self.feature_flags = FeatureFlags()

    def create_order(self, order):
        if self.feature_flags.use_new_order_service():
            return self.new_service.create(order)
        else:
            return self.legacy_service.create_order(order)
```

**Migration Process**:
1. Create facade
2. Build new implementation
3. Route subset of traffic to new
4. Gradually increase traffic
5. Remove legacy when 100% migrated

## Large-Scale Refactoring

### Planning Large Refactorings

**Steps**:
1. **Define Goal**: What are we improving?
2. **Measure Baseline**: Current metrics
3. **Break into Phases**: Incremental milestones
4. **Identify Risks**: What could go wrong?
5. **Plan Rollback**: How to undo if needed?
6. **Set Timeline**: Realistic schedule
7. **Communicate**: Keep team informed

### Branch by Abstraction

Refactor without breaking main branch.

**Scenario**: Replace OldCache with NewCache system-wide

**Steps**:
```python
# Step 1: Create abstraction
class CacheInterface:
    def get(self, key): pass
    def set(self, key, value): pass

# Step 2: Make old implementation conform
class OldCacheAdapter(CacheInterface):
    def __init__(self):
        self.old_cache = OldCache()

    def get(self, key):
        return self.old_cache.retrieve(key)

    def set(self, key, value):
        self.old_cache.store(key, value)

# Step 3: Update all clients to use interface
class UserService:
    def __init__(self, cache: CacheInterface):
        self.cache = cache  # Not OldCache directly

# Step 4: Create new implementation
class NewCacheAdapter(CacheInterface):
    def __init__(self):
        self.new_cache = NewCache()

    def get(self, key):
        return self.new_cache.fetch(key)

    def set(self, key, value):
        self.new_cache.put(key, value)

# Step 5: Switch implementations
# Old: cache = OldCacheAdapter()
cache = NewCacheAdapter()

# Step 6: Remove abstraction if no longer needed
```

### Parallel Change (Expand-Migrate-Contract)

**Pattern**: Expand → Migrate → Contract

**Example**: Rename field across large codebase

```typescript
// Step 1: EXPAND - Add new field alongside old
class User {
    email: string;      // Old field
    emailAddress: string;  // New field

    constructor(email: string) {
        this.email = email;
        this.emailAddress = email;  // Keep in sync
    }

    setEmail(email: string) {
        this.email = email;
        this.emailAddress = email;  // Keep in sync
    }
}

// Step 2: MIGRATE - Update clients gradually
// Old code keeps working:
user.email = "test@example.com";

// New code uses new field:
user.emailAddress = "test@example.com";

// Step 3: CONTRACT - Remove old field once all migrated
class User {
    emailAddress: string;  // Only new field remains

    constructor(emailAddress: string) {
        this.emailAddress = emailAddress;
    }
}
```

### Feature Toggles for Refactoring

Use flags to enable gradual rollout.

```python
class FeatureFlags:
    def use_new_payment_service(self, user_id):
        # Gradual rollout
        return hash(user_id) % 100 < self.rollout_percentage

class PaymentService:
    def __init__(self):
        self.flags = FeatureFlags()
        self.old_service = OldPaymentService()
        self.new_service = NewPaymentService()

    def process_payment(self, user_id, amount):
        if self.flags.use_new_payment_service(user_id):
            return self.new_service.process(user_id, amount)
        else:
            return self.old_service.process(user_id, amount)
```

**Rollout**:
- 0%: Development/testing
- 1%: Canary (early detection)
- 10%: Small user base
- 50%: Half traffic
- 100%: Full rollout
- Remove flag and old code

## Architecture Migration

### Monolith to Microservices

**Identify Bounded Contexts**:
```
Monolith:
├── User Management
├── Order Processing
├── Inventory
├── Shipping
└── Billing
```

**Extract Services Gradually**:
```
Phase 1: Extract User Service
Phase 2: Extract Order Service
Phase 3: Extract Inventory Service
...
```

**Example Extraction**:
```python
# Monolith - everything in one app
class MonolithApp:
    def create_order(self, user_id, items):
        user = self.db.get_user(user_id)
        order = Order(user, items)
        self.db.save_order(order)
        self.send_confirmation_email(user, order)
        self.update_inventory(items)
        return order

# Step 1: Extract User Service
class UserService:
    def get_user(self, user_id):
        return http.get(f"{USER_SERVICE_URL}/users/{user_id}")

class MonolithApp:
    def __init__(self):
        self.user_service = UserService()

    def create_order(self, user_id, items):
        user = self.user_service.get_user(user_id)  # Now remote
        order = Order(user, items)
        self.db.save_order(order)
        self.send_confirmation_email(user, order)
        self.update_inventory(items)
        return order

# Step 2: Extract Order Service
# ...continue gradually
```

### Layered to Hexagonal Architecture

**From**:
```
Controller → Service → Repository → Database
```

**To** (Hexagonal/Ports & Adapters):
```
          ┌─────────────────┐
          │  Domain Core    │
          │  (Business      │
          │   Logic)        │
          └───┬─────────┬───┘
              │         │
         Ports│         │Ports
              │         │
    ┌─────────▼──┐  ┌──▼──────────┐
    │  Adapters  │  │  Adapters   │
    │  (HTTP,    │  │  (DB, Email)│
    │   CLI)     │  │             │
    └────────────┘  └─────────────┘
```

**Implementation**:
```python
# Step 1: Define port (interface)
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order): pass

    @abstractmethod
    def find_by_id(self, order_id): pass

# Step 2: Core domain uses port
class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order):
        # Business logic
        self.repository.save(order)

# Step 3: Implement adapters
class PostgresOrderRepository(OrderRepository):
    def save(self, order):
        self.db.execute("INSERT INTO orders...")

    def find_by_id(self, order_id):
        return self.db.query("SELECT * FROM orders...")

class MongoOrderRepository(OrderRepository):
    def save(self, order):
        self.mongo.orders.insert_one(order.to_dict())

    def find_by_id(self, order_id):
        return self.mongo.orders.find_one({"_id": order_id})

# Step 4: Inject adapter
repository = PostgresOrderRepository()  # or MongoOrderRepository()
service = OrderService(repository)
```

## Database Refactoring

### Schema Evolution

**Challenge**: Database changes affect running application

**Solutions**:

#### Expand-Contract Pattern

**Add Column**:
```sql
-- Step 1: EXPAND - Add new column (nullable)
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Dual write - app writes to both columns
UPDATE users SET email_address = email WHERE email_address IS NULL;

-- Step 3: Backfill old data
UPDATE users SET email_address = email WHERE email_address IS NULL;

-- Step 4: MIGRATE - Update app to read from new column

-- Step 5: CONTRACT - Remove old column
ALTER TABLE users DROP COLUMN email;
```

**Split Table**:
```sql
-- Step 1: Create new tables
CREATE TABLE user_profiles (
    user_id INT PRIMARY KEY,
    bio TEXT,
    avatar_url VARCHAR(255)
);

-- Step 2: Copy data
INSERT INTO user_profiles (user_id, bio, avatar_url)
SELECT id, bio, avatar_url FROM users;

-- Step 3: Update app to use both tables

-- Step 4: Drop columns from users table
ALTER TABLE users DROP COLUMN bio, DROP COLUMN avatar_url;
```

### Zero-Downtime Migrations

**Blue-Green Deployment**:
```
1. Deploy new version (green)
2. Route 0% traffic to green
3. Verify green works
4. Route 100% traffic to green
5. Shutdown blue (old version)
```

**Rolling Deployment**:
```
1. Deploy to 10% of servers
2. Monitor for errors
3. Deploy to 50% of servers
4. Monitor for errors
5. Deploy to 100% of servers
```

### Data Migration Strategies

**Live Migration**:
```python
# Background job migrates data gradually
def migrate_user_emails():
    batch_size = 1000
    offset = 0

    while True:
        users = db.query("SELECT * FROM users LIMIT ? OFFSET ?",
                         batch_size, offset)

        if not users:
            break

        for user in users:
            user.email_address = user.email
            db.save(user)

        offset += batch_size
        time.sleep(1)  # Don't overwhelm database
```

## API Evolution

### Versioning Strategies

#### URL Versioning
```
/api/v1/users
/api/v2/users
```

#### Header Versioning
```
GET /api/users
Accept: application/vnd.myapi.v1+json
```

#### Query Parameter Versioning
```
/api/users?version=1
```

### Deprecation Process

```python
# Version 1 - Original API
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

# Version 2 - Improved API
@app.route('/api/v2/users', methods=['GET'])
def get_users_v2():
    return jsonify(enhanced_users)

# Version 1 with deprecation warning
@app.route('/api/users', methods=['GET'])
def get_users():
    response = jsonify(users)
    response.headers['X-API-Warn'] = 'This endpoint is deprecated. Use /api/v2/users'
    response.headers['X-API-Deprecation-Date'] = '2025-06-01'
    response.headers['X-API-Sunset-Date'] = '2025-12-01'
    return response
```

### Backward Compatibility

**Adding Fields** (safe):
```json
// V1
{"id": 1, "name": "John"}

// V2 (backward compatible)
{"id": 1, "name": "John", "email": "john@example.com"}
```

**Removing Fields** (breaking):
```json
// V1
{"id": 1, "name": "John", "deprecated_field": "value"}

// V2 (maintain both temporarily)
{"id": 1, "name": "John"}

// Transition: Keep deprecated_field but mark deprecated
```

## Performance Refactoring

### Profiling First

```python
import cProfile
import pstats

# Profile code
profiler = cProfile.Profile()
profiler.enable()

# Run slow code
process_large_dataset()

profiler.disable()

# Analyze results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

### Common Performance Refactorings

#### N+1 Query Problem

**Before**:
```python
# Fetches users
users = User.query.all()

for user in users:
    # N additional queries!
    print(user.profile.bio)
```

**After**:
```python
# Eager loading - 1 query
users = User.query.options(joinedload(User.profile)).all()

for user in users:
    print(user.profile.bio)  # No additional query
```

#### Caching

**Before**:
```python
def get_user_recommendations(user_id):
    # Expensive calculation every time
    return calculate_recommendations(user_id)
```

**After**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_recommendations(user_id):
    return calculate_recommendations(user_id)
```

#### Lazy Loading

**Before**:
```python
class Report:
    def __init__(self, data_source):
        self.data = data_source.load_all()  # Load everything upfront
```

**After**:
```python
class Report:
    def __init__(self, data_source):
        self.data_source = data_source
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self.data_source.load_all()  # Load when needed
        return self._data
```

## Concurrent Code Refactoring

### Thread Safety

**Before (not thread-safe)**:
```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1  # Race condition!
```

**After (thread-safe)**:
```python
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1
```

### Async Refactoring

**Before (blocking)**:
```python
def process_orders():
    for order in orders:
        validate_order(order)     # Blocks
        charge_payment(order)     # Blocks
        send_confirmation(order)  # Blocks
```

**After (async)**:
```python
async def process_orders():
    tasks = []
    for order in orders:
        task = process_single_order(order)
        tasks.append(task)

    await asyncio.gather(*tasks)  # Process concurrently

async def process_single_order(order):
    await validate_order(order)
    await charge_payment(order)
    await send_confirmation(order)
```

## Microservices Refactoring

### Extracting Microservice

**Steps**:
1. Identify bounded context
2. Create service skeleton
3. Duplicate functionality
4. Dual write (to both monolith and service)
5. Route reads to new service
6. Remove from monolith

**Example**:
```python
# Monolith
class OrderService:
    def create_order(self, user_id, items):
        # Inventory check in monolith
        if not self.inventory.available(items):
            raise OutOfStockError()

        order = Order(user_id, items)
        self.db.save(order)
        return order

# Step 1: Create inventory microservice
class InventoryMicroservice:
    @app.route('/api/inventory/check', methods=['POST'])
    def check_availability(self):
        items = request.json['items']
        available = inventory.check(items)
        return {'available': available}

# Step 2: Call from monolith
class OrderService:
    def create_order(self, user_id, items):
        # Call inventory microservice
        response = requests.post(
            f'{INVENTORY_SERVICE}/api/inventory/check',
            json={'items': items}
        )

        if not response.json()['available']:
            raise OutOfStockError()

        order = Order(user_id, items)
        self.db.save(order)
        return order
```

### Service Communication Patterns

#### Synchronous (REST)
```python
# Order service calls payment service
payment_response = requests.post(
    f'{PAYMENT_SERVICE}/api/payments',
    json={'order_id': order.id, 'amount': order.total}
)
```

#### Asynchronous (Message Queue)
```python
# Order service publishes event
message_queue.publish('order.created', {
    'order_id': order.id,
    'user_id': order.user_id,
    'total': order.total
})

# Payment service subscribes
@message_queue.subscribe('order.created')
def handle_order_created(event):
    process_payment(event['order_id'], event['total'])
```

## Summary

### Key Takeaways

1. **Legacy code** requires characterization tests and seams
2. **Large refactorings** need incremental phases and feature flags
3. **Architecture changes** use patterns like Strangler Fig
4. **Database refactorings** require expand-contract pattern
5. **API evolution** needs versioning and deprecation strategy
6. **Performance refactoring** starts with profiling
7. **Concurrent code** requires careful synchronization
8. **Microservices** extracted gradually with dual-write

### Next Steps

- Practice with [Advanced Examples](../examples/advanced/)
- Use [Templates](../templates/) for migration patterns
- Review [Troubleshooting](troubleshooting.md) for common issues
