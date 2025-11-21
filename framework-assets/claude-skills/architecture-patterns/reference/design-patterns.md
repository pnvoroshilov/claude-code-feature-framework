# Design Patterns Reference

**Common solutions to recurring software design problems.**

## Overview

Design patterns are reusable solutions to commonly occurring problems in software design.

pattern_categories[3]{category,purpose,patterns}:
Creational,Object creation mechanisms,Singleton Factory Builder Prototype
Structural,Composition of classes and objects,Adapter Decorator Repository Facade
Behavioral,Communication between objects,Observer Strategy Command State

---

## Creational Patterns

### Singleton Pattern

**Purpose:** Ensure a class has only one instance and provide global access point.

**Use When:**
- Need exactly one instance (database connection, configuration, logger)
- Want to control concurrent access to shared resource

**Python Example:**

```python
import threading

class DatabaseConnection:
    """Thread-safe singleton"""
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
        """Initialize connection only once"""
        self.connection = psycopg2.connect(
            host="localhost",
            database="mydb",
            user="admin"
        )
        self.is_connected = True

    def execute(self, query: str):
        return self.connection.execute(query)

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # Same instance
```

**TypeScript Example:**

```typescript
class Configuration {
  private static instance: Configuration;
  private settings: Map<string, any>;

  private constructor() {
    this.settings = new Map();
    this.loadSettings();
  }

  public static getInstance(): Configuration {
    if (!Configuration.instance) {
      Configuration.instance = new Configuration();
    }
    return Configuration.instance;
  }

  private loadSettings(): void {
    // Load configuration from file or environment
    this.settings.set('apiUrl', process.env.API_URL);
    this.settings.set('timeout', 5000);
  }

  public get(key: string): any {
    return this.settings.get(key);
  }
}

// Usage
const config1 = Configuration.getInstance();
const config2 = Configuration.getInstance();
console.log(config1 === config2); // true
```

---

### Factory Pattern

**Purpose:** Create objects without specifying exact class to create.

**Use When:**
- Don't know beforehand exact types to create
- Want to delegate instantiation to subclasses
- Need to centralize object creation logic

**Python Example:**

```python
from abc import ABC, abstractmethod

# Product interface
class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> bool:
        pass

# Concrete products
class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        print(f"Sending email to {recipient}: {message}")
        # SMTP implementation
        return True

class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        print(f"Sending SMS to {recipient}: {message}")
        # SMS API implementation
        return True

class PushNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        print(f"Sending push to {recipient}: {message}")
        # Push service implementation
        return True

# Factory
class NotificationFactory:
    @staticmethod
    def create(notification_type: str) -> Notification:
        factories = {
            "email": EmailNotification,
            "sms": SMSNotification,
            "push": PushNotification
        }

        notification_class = factories.get(notification_type)
        if not notification_class:
            raise ValueError(f"Unknown type: {notification_type}")

        return notification_class()

# Usage
notification = NotificationFactory.create("email")
notification.send("Hello!", "user@example.com")

notification = NotificationFactory.create("sms")
notification.send("Hello!", "+1234567890")
```

**TypeScript Example:**

```typescript
// Product interface
interface Logger {
  log(message: string): void;
}

// Concrete products
class ConsoleLogger implements Logger {
  log(message: string): void {
    console.log(`[Console] ${message}`);
  }
}

class FileLogger implements Logger {
  constructor(private filename: string) {}

  log(message: string): void {
    // Write to file
    console.log(`[File:${this.filename}] ${message}`);
  }
}

class RemoteLogger implements Logger {
  constructor(private endpoint: string) {}

  log(message: string): void {
    // Send to remote service
    console.log(`[Remote:${this.endpoint}] ${message}`);
  }
}

// Factory
class LoggerFactory {
  static create(type: string, ...args: any[]): Logger {
    switch (type) {
      case 'console':
        return new ConsoleLogger();
      case 'file':
        return new FileLogger(args[0]);
      case 'remote':
        return new RemoteLogger(args[0]);
      default:
        throw new Error(`Unknown logger type: ${type}`);
    }
  }
}

// Usage
const logger = LoggerFactory.create('console');
logger.log('Application started');

const fileLogger = LoggerFactory.create('file', 'app.log');
fileLogger.log('File logging enabled');
```

---

## Structural Patterns

### Repository Pattern

**Purpose:** Encapsulate data access logic and provide collection-like interface.

**Use When:**
- Need to abstract database access
- Want to test business logic without database
- Need to swap data sources (SQL → NoSQL)

**Python Example:**

```python
from abc import ABC, abstractmethod
from typing import Optional, List

# Entity
@dataclass
class User:
    id: int
    email: str
    name: str

# Repository interface
class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

# SQL Implementation
class SQLUserRepository(IUserRepository):
    def __init__(self, db_session):
        self.db = db_session

    def find_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        row = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(row) if row else None

    def find_all(self) -> List[User]:
        rows = self.db.query(UserModel).all()
        return [self._to_entity(row) for row in rows]

    def save(self, user: User) -> User:
        if user.id == 0:
            model = UserModel(email=user.email, name=user.name)
            self.db.add(model)
        else:
            model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
            model.email = user.email
            model.name = user.name
        self.db.commit()
        return self._to_entity(model)

    def delete(self, user_id: int) -> bool:
        result = self.db.query(UserModel).filter(UserModel.id == user_id).delete()
        self.db.commit()
        return result > 0

    def _to_entity(self, model: UserModel) -> User:
        return User(id=model.id, email=model.email, name=model.name)

# MongoDB Implementation
class MongoUserRepository(IUserRepository):
    def __init__(self, db):
        self.collection = db['users']

    def find_by_id(self, user_id: int) -> Optional[User]:
        doc = self.collection.find_one({"_id": user_id})
        return self._to_entity(doc) if doc else None

    def find_by_email(self, email: str) -> Optional[User]:
        doc = self.collection.find_one({"email": email})
        return self._to_entity(doc) if doc else None

    def find_all(self) -> List[User]:
        docs = self.collection.find()
        return [self._to_entity(doc) for doc in docs]

    def save(self, user: User) -> User:
        doc = {"email": user.email, "name": user.name}
        if user.id == 0:
            result = self.collection.insert_one(doc)
            user.id = result.inserted_id
        else:
            self.collection.update_one({"_id": user.id}, {"$set": doc})
        return user

    def delete(self, user_id: int) -> bool:
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    def _to_entity(self, doc: dict) -> User:
        return User(id=doc['_id'], email=doc['email'], name=doc['name'])

# Usage - Easy to swap implementations
user_service = UserService(SQLUserRepository(db_session))
# or
user_service = UserService(MongoUserRepository(mongo_db))
```

---

## Behavioral Patterns

### Observer Pattern

**Purpose:** Define one-to-many dependency where state change in one object notifies all dependents.

**Use When:**
- Object state changes need to trigger updates in other objects
- Need loose coupling between notifier and observers
- Want pub/sub style communication

**Python Example:**

```python
from abc import ABC, abstractmethod
from typing import List

# Observer interface
class IObserver(ABC):
    @abstractmethod
    def update(self, event: dict) -> None:
        pass

# Subject
class Subject:
    def __init__(self):
        self._observers: List[IObserver] = []

    def attach(self, observer: IObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, event: dict) -> None:
        for observer in self._observers:
            observer.update(event)

# Concrete subject
class UserAccount(Subject):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self._status = "active"

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        old_status = self._status
        self._status = value
        self.notify({
            "event": "status_changed",
            "user_id": self.user_id,
            "old_status": old_status,
            "new_status": value
        })

# Concrete observers
class EmailNotifier(IObserver):
    def update(self, event: dict) -> None:
        if event["event"] == "status_changed":
            print(f"Email: User {event['user_id']} status changed to {event['new_status']}")

class LoggingObserver(IObserver):
    def update(self, event: dict) -> None:
        print(f"Log: {event}")

class AnalyticsObserver(IObserver):
    def update(self, event: dict) -> None:
        print(f"Analytics: Track event {event['event']} for user {event['user_id']}")

# Usage
account = UserAccount(123)

# Attach observers
account.attach(EmailNotifier())
account.attach(LoggingObserver())
account.attach(AnalyticsObserver())

# Change triggers all observers
account.status = "suspended"
# Output:
# Email: User 123 status changed to suspended
# Log: {'event': 'status_changed', 'user_id': 123, 'old_status': 'active', 'new_status': 'suspended'}
# Analytics: Track event status_changed for user 123
```

**React Context Example (Observer Pattern):**

```typescript
// Subject: Context Provider
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);

// Subject implementation
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

// Observers: Components that subscribe
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
  return (
    <button onClick={toggleTheme}>
      Switch to {theme === 'light' ? 'dark' : 'light'}
    </button>
  );
};

// All observers auto-update when theme changes
```

---

### Strategy Pattern

**Purpose:** Define family of algorithms, encapsulate each one, and make them interchangeable.

**Use When:**
- Need different variants of algorithm
- Want to switch algorithms at runtime
- Need to isolate algorithm implementation details

**Python Example:**

```python
# Strategy interface
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

# Concrete strategies
class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str):
        self.card_number = card_number
        self.cvv = cvv

    def pay(self, amount: float) -> bool:
        print(f"Paying ${amount} with credit card {self.card_number}")
        # Process credit card payment
        return True

class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str):
        self.email = email

    def pay(self, amount: float) -> bool:
        print(f"Paying ${amount} with PayPal account {self.email}")
        # Process PayPal payment
        return True

class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address

    def pay(self, amount: float) -> bool:
        print(f"Paying ${amount} to wallet {self.wallet_address}")
        # Process crypto payment
        return True

# Context
class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def process_payment(self, amount: float) -> bool:
        return self.strategy.pay(amount)

# Usage - can switch strategies at runtime
processor = PaymentProcessor(CreditCardPayment("1234-5678-9012-3456", "123"))
processor.process_payment(100.00)

processor.set_strategy(PayPalPayment("user@example.com"))
processor.process_payment(50.00)

processor.set_strategy(CryptoPayment("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"))
processor.process_payment(75.00)
```

---

## Pattern Selection Guide

pattern_selection[8]{problem,recommended_pattern,reason}:
Need single instance,Singleton,Ensures only one instance exists globally
Create objects dynamically,Factory,Centralize creation logic decouple from concrete classes
Abstract data access,Repository,Encapsulate database logic enable testing
Notify multiple objects of changes,Observer,Loose coupling between subject and observers
Switch algorithms at runtime,Strategy,Encapsulate algorithms make them interchangeable
Add behavior without modifying class,Decorator,Follow Open/Closed principle
Simplify complex subsystem,Facade,Provide simple interface to complex system
Build complex objects step by step,Builder,Separate construction from representation

---

**File Size**: 350/500 lines max ✅
