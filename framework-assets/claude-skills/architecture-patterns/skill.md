---
name: architecture-patterns
description: Comprehensive guide to software architecture patterns, principles, and best practices for frontend and backend development
tags: [architecture, patterns, solid, dry, kiss, ddd, clean-architecture, microservices, design-patterns]
version: 1.0.0
---

# Architecture Patterns Skill

This skill provides comprehensive guidance on software architecture patterns, design principles, and best practices for building scalable, maintainable systems.

## Fundamental Principles

### SOLID Principles

#### S - Single Responsibility Principle (SRP)
**A class should have only one reason to change.**

**✅ Good Example (Backend - Python):**
```python
# Each class has single responsibility
class UserRepository:
    """Only responsible for data access"""
    def get_user(self, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()

class UserValidator:
    """Only responsible for validation"""
    def validate_email(self, email: str) -> bool:
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

class UserService:
    """Only responsible for business logic"""
    def __init__(self, repository: UserRepository, validator: UserValidator):
        self.repository = repository
        self.validator = validator

    def create_user(self, email: str, name: str) -> User:
        if not self.validator.validate_email(email):
            raise ValueError("Invalid email")
        return self.repository.create_user(email, name)
```

**❌ Bad Example (Backend - Python):**
```python
# God class - too many responsibilities
class UserManager:
    """Does everything - violates SRP"""
    def get_user(self, user_id: int):
        # Database access
        return db.query(User).filter(User.id == user_id).first()

    def validate_email(self, email: str):
        # Validation logic
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

    def send_email(self, user: User, subject: str, body: str):
        # Email sending
        smtp.send(user.email, subject, body)

    def log_activity(self, user: User, action: str):
        # Logging
        logger.info(f"User {user.id} performed {action}")
```

**✅ Good Example (Frontend - React):**
```typescript
// Separate concerns in React components
// UserList - only displays list
const UserList: React.FC<{ users: User[] }> = ({ users }) => (
  <ul>
    {users.map(user => <UserCard key={user.id} user={user} />)}
  </ul>
);

// UserCard - only displays single user
const UserCard: React.FC<{ user: User }> = ({ user }) => (
  <div className="user-card">
    <h3>{user.name}</h3>
    <p>{user.email}</p>
  </div>
);

// UserContainer - only handles data fetching
const UserContainer: React.FC = () => {
  const { users, loading } = useUsers();

  if (loading) return <Spinner />;
  return <UserList users={users} />;
};
```

**❌ Bad Example (Frontend - React):**
```typescript
// Component does everything - violates SRP
const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');

  // Data fetching
  useEffect(() => {
    fetch('/api/users').then(r => r.json()).then(setUsers);
  }, []);

  // Filtering logic
  const filtered = users.filter(u => u.name.includes(filter));

  // Sorting logic
  const sorted = filtered.sort((a, b) => a[sortBy] > b[sortBy] ? 1 : -1);

  // Rendering logic with inline styles and business logic
  return (
    <div style={{ padding: '20px' }}>
      <input onChange={e => setFilter(e.target.value)} />
      <select onChange={e => setSortBy(e.target.value)}>
        <option value="name">Name</option>
        <option value="email">Email</option>
      </select>
      {sorted.map(user => (
        <div key={user.id} style={{ border: '1px solid gray' }}>
          {user.name} - {user.email}
          <button onClick={() => deleteUser(user.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
};
```

#### O - Open/Closed Principle (OCP)
**Open for extension, closed for modification.**

**✅ Good Example (Backend - Python):**
```python
from abc import ABC, abstractmethod

# Abstract base - closed for modification
class NotificationSender(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> None:
        pass

# Extensions - open for extension
class EmailNotificationSender(NotificationSender):
    def send(self, message: str, recipient: str) -> None:
        smtp.send(recipient, "Notification", message)

class SMSNotificationSender(NotificationSender):
    def send(self, message: str, recipient: str) -> None:
        sms_api.send(recipient, message)

class SlackNotificationSender(NotificationSender):
    def send(self, message: str, recipient: str) -> None:
        slack_api.send_message(recipient, message)

# Usage - no modification needed to add new notification type
class NotificationService:
    def __init__(self, senders: list[NotificationSender]):
        self.senders = senders

    def notify(self, message: str, recipient: str):
        for sender in self.senders:
            sender.send(message, recipient)
```

**❌ Bad Example (Backend - Python):**
```python
# Must modify this class to add new notification type
class NotificationService:
    def send_notification(self, type: str, message: str, recipient: str):
        if type == "email":
            smtp.send(recipient, "Notification", message)
        elif type == "sms":
            sms_api.send(recipient, message)
        elif type == "slack":  # Had to modify class to add this
            slack_api.send_message(recipient, message)
        # Need to keep modifying this class for each new type
```

**✅ Good Example (Frontend - React):**
```typescript
// Base component closed for modification
interface AlertProps {
  message: string;
  variant: 'success' | 'error' | 'warning' | 'info';
}

const Alert: React.FC<AlertProps> = ({ message, variant }) => {
  const variantStyles = useAlertStyles(variant);
  return <div className={variantStyles}>{message}</div>;
};

// Extension without modifying base
const SuccessAlert: React.FC<{ message: string }> = ({ message }) => (
  <Alert variant="success" message={message} />
);

const ErrorAlert: React.FC<{ message: string }> = ({ message }) => (
  <Alert variant="error" message={message} />
);

// Can add new variants without modifying Alert component
const InfoAlert: React.FC<{ message: string }> = ({ message }) => (
  <Alert variant="info" message={message} />
);
```

#### L - Liskov Substitution Principle (LSP)
**Derived classes must be substitutable for their base classes.**

**✅ Good Example (Backend - Python):**
```python
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side * self.side

# Both can be used interchangeably
def calculate_total_area(shapes: list[Shape]) -> float:
    return sum(shape.area() for shape in shapes)

# Works with any Shape
shapes = [Rectangle(5, 10), Square(5), Rectangle(3, 7)]
total = calculate_total_area(shapes)  # Works correctly
```

**❌ Bad Example (Backend - Python):**
```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def set_width(self, width: float):
        self.width = width

    def set_height(self, height: float):
        self.height = height

    def area(self) -> float:
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width: float):
        self.width = width
        self.height = width  # Violates LSP - changes both dimensions

    def set_height(self, height: float):
        self.width = height  # Violates LSP - changes both dimensions
        self.height = height

# Breaks when using Square as Rectangle
def test_rectangle(rect: Rectangle):
    rect.set_width(5)
    rect.set_height(10)
    assert rect.area() == 50  # Fails for Square!

rect = Rectangle(0, 0)
test_rectangle(rect)  # Passes

square = Square(0, 0)
test_rectangle(square)  # Fails - area is 100, not 50!
```

#### I - Interface Segregation Principle (ISP)
**Many client-specific interfaces are better than one general-purpose interface.**

**✅ Good Example (Backend - Python):**
```python
# Segregated interfaces
class Readable(ABC):
    @abstractmethod
    def read(self) -> bytes:
        pass

class Writable(ABC):
    @abstractmethod
    def write(self, data: bytes) -> None:
        pass

class Closeable(ABC):
    @abstractmethod
    def close(self) -> None:
        pass

# Implement only what you need
class ReadOnlyFile(Readable, Closeable):
    def read(self) -> bytes:
        return self.file.read()

    def close(self) -> None:
        self.file.close()

class ReadWriteFile(Readable, Writable, Closeable):
    def read(self) -> bytes:
        return self.file.read()

    def write(self, data: bytes) -> None:
        self.file.write(data)

    def close(self) -> None:
        self.file.close()
```

**❌ Bad Example (Backend - Python):**
```python
# Fat interface - forces implementation of unused methods
class File(ABC):
    @abstractmethod
    def read(self) -> bytes:
        pass

    @abstractmethod
    def write(self, data: bytes) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

# Forced to implement write even though it's read-only
class ReadOnlyFile(File):
    def read(self) -> bytes:
        return self.file.read()

    def write(self, data: bytes) -> None:
        raise NotImplementedError("Cannot write to read-only file")

    def close(self) -> None:
        self.file.close()
```

#### D - Dependency Inversion Principle (DIP)
**Depend on abstractions, not concretions.**

**✅ Good Example (Backend - Python):**
```python
# Abstraction
class IDatabase(ABC):
    @abstractmethod
    def save(self, data: dict) -> None:
        pass

    @abstractmethod
    def find(self, id: int) -> dict:
        pass

# High-level module depends on abstraction
class UserService:
    def __init__(self, database: IDatabase):
        self.database = database  # Depends on interface

    def create_user(self, user_data: dict):
        self.database.save(user_data)

# Low-level modules implement abstraction
class PostgresDatabase(IDatabase):
    def save(self, data: dict) -> None:
        # Postgres-specific implementation
        pass

    def find(self, id: int) -> dict:
        # Postgres-specific implementation
        pass

class MongoDatabase(IDatabase):
    def save(self, data: dict) -> None:
        # MongoDB-specific implementation
        pass

    def find(self, id: int) -> dict:
        # MongoDB-specific implementation
        pass

# Easy to swap implementations
service1 = UserService(PostgresDatabase())
service2 = UserService(MongoDatabase())
```

**❌ Bad Example (Backend - Python):**
```python
# High-level module depends on low-level module
class PostgresDatabase:
    def save_to_postgres(self, data: dict):
        # Postgres-specific implementation
        pass

class UserService:
    def __init__(self):
        self.database = PostgresDatabase()  # Tight coupling!

    def create_user(self, user_data: dict):
        self.database.save_to_postgres(user_data)  # Cannot swap database
```

**✅ Good Example (Frontend - React):**
```typescript
// Abstraction - API interface
interface IUserAPI {
  fetchUsers(): Promise<User[]>;
  createUser(user: CreateUserDTO): Promise<User>;
}

// Component depends on abstraction
const UserList: React.FC<{ api: IUserAPI }> = ({ api }) => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    api.fetchUsers().then(setUsers);
  }, [api]);

  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
};

// Implementations
class RestUserAPI implements IUserAPI {
  async fetchUsers(): Promise<User[]> {
    return fetch('/api/users').then(r => r.json());
  }

  async createUser(user: CreateUserDTO): Promise<User> {
    return fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(user)
    }).then(r => r.json());
  }
}

class MockUserAPI implements IUserAPI {
  async fetchUsers(): Promise<User[]> {
    return Promise.resolve([{ id: 1, name: 'Test User' }]);
  }

  async createUser(user: CreateUserDTO): Promise<User> {
    return Promise.resolve({ id: 2, ...user });
  }
}

// Easy to swap implementations
<UserList api={new RestUserAPI()} />
<UserList api={new MockUserAPI()} />  // For testing
```

### DRY (Don't Repeat Yourself)
**Every piece of knowledge should have a single, unambiguous representation.**

**✅ Good Example (Backend - Python):**
```python
# Single source of truth for validation
class UserValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

    @staticmethod
    def validate_password(password: str) -> bool:
        return len(password) >= 8 and any(c.isdigit() for c in password)

# Reuse validation logic
class UserService:
    def create_user(self, email: str, password: str):
        if not UserValidator.validate_email(email):
            raise ValueError("Invalid email")
        if not UserValidator.validate_password(password):
            raise ValueError("Invalid password")
        # Create user

class UserUpdateService:
    def update_email(self, user_id: int, new_email: str):
        if not UserValidator.validate_email(new_email):
            raise ValueError("Invalid email")
        # Update email
```

**❌ Bad Example (Backend - Python):**
```python
# Duplicated validation logic
class UserService:
    def create_user(self, email: str, password: str):
        # Validation duplicated
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email")
        if len(password) < 8 or not any(c.isdigit() for c in password):
            raise ValueError("Invalid password")
        # Create user

class UserUpdateService:
    def update_email(self, user_id: int, new_email: str):
        # Same validation duplicated again
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', new_email):
            raise ValueError("Invalid email")
        # Update email
```

### KISS (Keep It Simple, Stupid)
**Simplicity should be a key goal in design.**

**✅ Good Example (Backend - Python):**
```python
# Simple and clear
def calculate_discount(price: float, discount_percent: float) -> float:
    return price * (1 - discount_percent / 100)

# Simple conditional
def get_shipping_cost(weight: float) -> float:
    if weight < 1:
        return 5.0
    elif weight < 5:
        return 10.0
    else:
        return 15.0
```

**❌ Bad Example (Backend - Python):**
```python
# Over-engineered solution
class DiscountCalculationStrategy(ABC):
    @abstractmethod
    def calculate(self, price: float) -> float:
        pass

class PercentageDiscountStrategy(DiscountCalculationStrategy):
    def __init__(self, percent: float):
        self.percent = percent

    def calculate(self, price: float) -> float:
        return price * (1 - self.percent / 100)

class DiscountCalculator:
    def __init__(self, strategy: DiscountCalculationStrategy):
        self.strategy = strategy

    def calculate_final_price(self, price: float) -> float:
        return self.strategy.calculate(price)

# Too complex for simple task
calculator = DiscountCalculator(PercentageDiscountStrategy(10))
final_price = calculator.calculate_final_price(100)
```

**✅ Good Example (Frontend - React):**
```typescript
// Simple component
const Button: React.FC<{ text: string; onClick: () => void }> = ({ text, onClick }) => (
  <button onClick={onClick}>{text}</button>
);

// Usage
<Button text="Submit" onClick={handleSubmit} />
```

**❌ Bad Example (Frontend - React):**
```typescript
// Over-complicated component
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  rounded?: boolean;
  elevation?: number;
}

const Button: React.FC<ButtonProps> = ({
  text,
  onClick,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  rounded = false,
  elevation = 0
}) => {
  // Complex logic for simple button
  const classes = useMemo(() => {
    return classNames(
      'button',
      `button--${variant}`,
      `button--${size}`,
      { 'button--disabled': disabled },
      { 'button--loading': loading },
      { 'button--full-width': fullWidth },
      { 'button--rounded': rounded },
      `button--elevation-${elevation}`
    );
  }, [variant, size, disabled, loading, fullWidth, rounded, elevation]);

  return (
    <button className={classes} onClick={onClick} disabled={disabled || loading}>
      {loading && <Spinner />}
      {icon && iconPosition === 'left' && icon}
      {text}
      {icon && iconPosition === 'right' && icon}
    </button>
  );
};
```

## Architectural Patterns

### Clean Architecture
**Organize code by layers with dependency rule: dependencies point inward.**

**Layers (Outside → Inside):**
1. **Frameworks & Drivers** (UI, DB, External APIs)
2. **Interface Adapters** (Controllers, Presenters, Gateways)
3. **Application Business Rules** (Use Cases)
4. **Enterprise Business Rules** (Entities)

**✅ Good Example (Backend - Python):**
```python
# Layer 4: Entities (Core business rules)
@dataclass
class User:
    id: int
    email: str
    name: str

    def is_active(self) -> bool:
        return self.status == "active"

# Layer 3: Use Cases (Application business rules)
class CreateUserUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def execute(self, email: str, name: str) -> User:
        # Business logic
        if self.user_repository.exists_by_email(email):
            raise ValueError("Email already exists")

        user = User(id=0, email=email, name=name)
        return self.user_repository.save(user)

# Layer 2: Interface Adapters
class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass

# Layer 1: Frameworks & Drivers
class SQLAlchemyUserRepository(IUserRepository):
    def save(self, user: User) -> User:
        db_user = UserModel(**asdict(user))
        db.session.add(db_user)
        db.session.commit()
        return user

    def exists_by_email(self, email: str) -> bool:
        return db.session.query(UserModel).filter_by(email=email).first() is not None

# API Controller (Layer 1)
@router.post("/users")
def create_user(request: CreateUserRequest):
    repository = SQLAlchemyUserRepository()
    use_case = CreateUserUseCase(repository)
    user = use_case.execute(request.email, request.name)
    return UserResponse.from_entity(user)
```

### Domain-Driven Design (DDD)
**Model software based on the business domain.**

**✅ Good Example (Backend - Python):**
```python
# Value Object
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

# Entity
class Order:
    def __init__(self, id: str, customer_id: str):
        self.id = id
        self.customer_id = customer_id
        self.items: list[OrderItem] = []
        self.status = OrderStatus.PENDING

    def add_item(self, product_id: str, quantity: int, price: Money):
        if self.status != OrderStatus.PENDING:
            raise ValueError("Cannot add items to non-pending order")

        item = OrderItem(product_id, quantity, price)
        self.items.append(item)

    def total(self) -> Money:
        return sum((item.subtotal() for item in self.items), Money(Decimal(0), "USD"))

    def submit(self):
        if not self.items:
            raise ValueError("Cannot submit empty order")
        self.status = OrderStatus.SUBMITTED

# Aggregate Root
class OrderAggregate:
    def __init__(self, order: Order):
        self.order = order
        self._domain_events: list[DomainEvent] = []

    def submit(self):
        self.order.submit()
        self._domain_events.append(OrderSubmittedEvent(self.order.id))

    def get_domain_events(self) -> list[DomainEvent]:
        return self._domain_events

# Repository
class IOrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order:
        pass

# Domain Service
class OrderService:
    def __init__(self, repository: IOrderRepository):
        self.repository = repository

    def submit_order(self, order_id: str):
        order = self.repository.find_by_id(order_id)
        aggregate = OrderAggregate(order)
        aggregate.submit()
        self.repository.save(order)

        # Publish domain events
        for event in aggregate.get_domain_events():
            event_bus.publish(event)
```

### Microservices Architecture
**Decompose application into small, independent services.**

**✅ Good Example (Backend - Python):**
```python
# User Service
@app.post("/users")
async def create_user(user: CreateUserDTO):
    user_id = await user_service.create(user)

    # Publish event for other services
    await event_bus.publish(UserCreatedEvent(user_id, user.email))

    return {"user_id": user_id}

# Order Service (separate microservice)
@app.post("/orders")
async def create_order(order: CreateOrderDTO):
    # Call User Service to validate user exists
    user = await user_service_client.get_user(order.user_id)
    if not user:
        raise HTTPException(404, "User not found")

    order_id = await order_service.create(order)
    return {"order_id": order_id}

# Event Handler in Order Service
@event_bus.subscribe("user.created")
async def on_user_created(event: UserCreatedEvent):
    # Create welcome order or discount for new user
    await order_service.create_welcome_offer(event.user_id)

# API Gateway (entry point)
class APIGateway:
    def __init__(self):
        self.user_service = UserServiceClient("http://user-service:8001")
        self.order_service = OrderServiceClient("http://order-service:8002")

    async def get_user_orders(self, user_id: str):
        # Aggregate data from multiple services
        user = await self.user_service.get_user(user_id)
        orders = await self.order_service.get_user_orders(user_id)

        return {
            "user": user,
            "orders": orders
        }
```

### Design Patterns

#### Singleton Pattern
**Ensure a class has only one instance.**

**✅ Good Example (Backend - Python):**
```python
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="mydb"
        )

    def execute(self, query: str):
        return self.connection.execute(query)

# Always returns same instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # True
```

#### Factory Pattern
**Create objects without specifying exact class.**

**✅ Good Example (Backend - Python):**
```python
class NotificationFactory:
    @staticmethod
    def create(notification_type: str) -> INotification:
        if notification_type == "email":
            return EmailNotification()
        elif notification_type == "sms":
            return SMSNotification()
        elif notification_type == "push":
            return PushNotification()
        else:
            raise ValueError(f"Unknown notification type: {notification_type}")

# Usage
notification = NotificationFactory.create("email")
notification.send("Hello!")
```

#### Repository Pattern
**Encapsulate data access logic.**

**✅ Good Example (Backend - Python):**
```python
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def find_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.query("SELECT * FROM users WHERE id = ?", user_id)
        return User.from_row(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        row = self.db.query("SELECT * FROM users WHERE email = ?", email)
        return User.from_row(row) if row else None

    def save(self, user: User) -> User:
        if user.id:
            self.db.execute("UPDATE users SET name = ?, email = ? WHERE id = ?",
                           user.name, user.email, user.id)
        else:
            user.id = self.db.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                                     user.name, user.email)
        return user
```

#### Observer Pattern
**Define one-to-many dependency between objects.**

**✅ Good Example (Frontend - React with Context):**
```typescript
// Subject
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);

// Provider (Subject)
const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Observers
const Header: React.FC = () => {
  const { theme } = useContext(ThemeContext)!;
  return <header className={`header header--${theme}`}>Header</header>;
};

const Sidebar: React.FC = () => {
  const { theme } = useContext(ThemeContext)!;
  return <aside className={`sidebar sidebar--${theme}`}>Sidebar</aside>;
};

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useContext(ThemeContext)!;
  return <button onClick={toggleTheme}>Switch to {theme === 'light' ? 'dark' : 'light'}</button>;
};
```

## Anti-Patterns to Avoid

### God Object / God Class
**❌ Anti-Pattern:** Single class that knows/does too much.

```python
# DON'T - God class
class Application:
    def __init__(self):
        self.db = Database()
        self.cache = Cache()
        self.logger = Logger()

    def handle_user_request(self, request):
        # Validation
        if not self.validate_request(request):
            return "Invalid"

        # Database access
        user = self.db.query("SELECT * FROM users WHERE id = ?", request.user_id)

        # Business logic
        if user.status == "active":
            # Caching
            self.cache.set(f"user_{user.id}", user)

            # Logging
            self.logger.info(f"User {user.id} accessed")

            # Email sending
            self.send_email(user.email, "Welcome")

        return user
```

**✅ Solution:** Split into focused classes following SRP.

### Spaghetti Code
**❌ Anti-Pattern:** Unstructured, tangled control flow.

```python
# DON'T - Spaghetti code
def process_order(order_id):
    order = get_order(order_id)
    if order:
        if order.status == "pending":
            if check_inventory(order):
                if process_payment(order):
                    update_inventory(order)
                    if send_confirmation(order):
                        update_order_status(order, "completed")
                    else:
                        update_order_status(order, "error")
                        rollback_payment(order)
                else:
                    update_order_status(order, "payment_failed")
            else:
                update_order_status(order, "out_of_stock")
        else:
            return "Order not pending"
    else:
        return "Order not found"
```

**✅ Solution:** Extract methods, use early returns, separate concerns.

```python
# DO - Clean structure
def process_order(order_id: str) -> OrderResult:
    order = get_order(order_id)
    if not order:
        return OrderResult.not_found()

    if order.status != "pending":
        return OrderResult.invalid_status()

    if not check_inventory(order):
        return OrderResult.out_of_stock()

    payment_result = process_payment(order)
    if not payment_result.success:
        return OrderResult.payment_failed(payment_result.error)

    update_inventory(order)
    send_confirmation_email(order)
    complete_order(order)

    return OrderResult.success()
```

### Magic Numbers / Magic Strings
**❌ Anti-Pattern:** Hard-coded values without explanation.

```python
# DON'T
def calculate_price(quantity):
    if quantity > 100:
        return quantity * 9.99 * 0.9
    elif quantity > 50:
        return quantity * 9.99 * 0.95
    else:
        return quantity * 9.99
```

**✅ Solution:** Use named constants.

```python
# DO
UNIT_PRICE = 9.99
BULK_TIER_1 = 50
BULK_TIER_2 = 100
BULK_DISCOUNT_1 = 0.05
BULK_DISCOUNT_2 = 0.10

def calculate_price(quantity: int) -> float:
    price = quantity * UNIT_PRICE

    if quantity > BULK_TIER_2:
        return price * (1 - BULK_DISCOUNT_2)
    elif quantity > BULK_TIER_1:
        return price * (1 - BULK_DISCOUNT_1)
    else:
        return price
```

### Premature Optimization
**❌ Anti-Pattern:** Optimizing before identifying bottlenecks.

```python
# DON'T - Over-optimized before needed
class UserCache:
    def __init__(self):
        self.cache = {}
        self.lru_queue = deque()
        self.access_counts = defaultdict(int)
        self.last_access_time = {}

    def get(self, user_id):
        # Complex caching logic that's not needed yet
        pass
```

**✅ Solution:** Write clear code first, optimize when needed.

```python
# DO - Simple first
class UserCache:
    def __init__(self):
        self.cache: dict[int, User] = {}

    def get(self, user_id: int) -> Optional[User]:
        return self.cache.get(user_id)

    def set(self, user_id: int, user: User):
        self.cache[user_id] = user
```

### Circular Dependencies
**❌ Anti-Pattern:** Modules depending on each other.

```python
# DON'T - module_a.py
from module_b import ClassB

class ClassA:
    def method(self):
        b = ClassB()
        b.do_something()

# DON'T - module_b.py
from module_a import ClassA

class ClassB:
    def method(self):
        a = ClassA()
        a.do_something()
```

**✅ Solution:** Introduce abstraction or move shared code.

```python
# DO - module_a.py
from interface import IProcessor

class ClassA:
    def __init__(self, processor: IProcessor):
        self.processor = processor

    def method(self):
        self.processor.process()

# DO - module_b.py
from interface import IProcessor

class ClassB(IProcessor):
    def process(self):
        # Implementation
        pass
```

## Best Practices Summary

### Backend Architecture
- ✅ Use layered architecture (Controller → Service → Repository → Database)
- ✅ Implement dependency injection
- ✅ Use DTOs for API requests/responses
- ✅ Separate business logic from infrastructure
- ✅ Use transaction boundaries correctly
- ✅ Implement proper error handling and logging

### Frontend Architecture
- ✅ Component composition over inheritance
- ✅ Container/Presentational component pattern
- ✅ Custom hooks for reusable logic
- ✅ Context API for cross-cutting concerns
- ✅ Proper state management (local vs global)
- ✅ Code splitting and lazy loading

### General Guidelines
- ✅ Write self-documenting code
- ✅ Follow consistent naming conventions
- ✅ Keep functions/methods small and focused
- ✅ Write tests for business logic
- ✅ Use version control effectively
- ✅ Document architectural decisions (ADRs)
- ✅ Regular refactoring to prevent technical debt
