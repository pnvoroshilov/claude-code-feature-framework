# Domain-Driven Design (DDD) in Python

**Comprehensive guide to implementing Domain-Driven Design patterns in Python using dataclasses, Pydantic, and clean modeling techniques.**

## Core DDD Concepts

ddd_concepts[7]{concept,definition,python_pattern}:
Entity,Object with unique identity that can change over time,dataclass with id field and mutable state
Value Object,Immutable object defined by its attributes,dataclass(frozen=True) with value equality
Aggregate,Cluster of entities and VOs treated as single unit,Entity as root with consistency boundary
Repository,Collection-like interface for aggregates,ABC with find and save methods
Domain Event,Something that happened in the domain,dataclass event with timestamp
Domain Service,Stateless operation not belonging to entity,Function or class with domain logic
Bounded Context,Explicit boundary with specific domain model,Python package or module

## Pattern 1: Entities

**Objects with identity - equality by ID, not by attributes.**

### Entity Characteristics

entity_characteristics[5]{characteristic,description,implementation}:
Identity,Has unique identifier,id: int or id: UUID field
Mutability,State can change over time,Regular dataclass (not frozen)
Behavior,Contains business logic,Methods that enforce business rules
Equality,Two entities equal if same ID,__eq__ based on id comparison
Lifecycle,Created persisted modified deleted,Track changes through events

### Entity Implementation

```python
# domain/entities/order.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Self
from decimal import Decimal
from domain.value_objects.money import Money
from domain.value_objects.order_item import OrderItem
from domain.events.order_events import OrderPlaced, OrderCancelled
from domain.exceptions import DomainException

@dataclass
class Order:
    """Order entity - has identity and mutable state."""
    id: int
    customer_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: str = "PENDING"
    created_at: datetime = field(default_factory=datetime.now)
    total: Money = field(init=False)

    def __post_init__(self):
        """Calculate total on initialization."""
        self._calculate_total()

    def add_item(self, item: OrderItem) -> Self:
        """Business rule: can only add items to pending orders."""
        if self.status != "PENDING":
            raise DomainException(f"Cannot add items to {self.status} order")
        self.items.append(item)
        self._calculate_total()
        return self

    def remove_item(self, item_id: str) -> Self:
        """Business rule: can only remove items from pending orders."""
        if self.status != "PENDING":
            raise DomainException(f"Cannot remove items from {self.status} order")
        self.items = [i for i in self.items if i.id != item_id]
        self._calculate_total()
        return self

    def place(self) -> OrderPlaced:
        """Business rule: order must have items and be pending."""
        if self.status != "PENDING":
            raise DomainException(f"Cannot place {self.status} order")
        if not self.items:
            raise DomainException("Cannot place empty order")
        if self.total.amount <= 0:
            raise DomainException("Order total must be positive")

        self.status = "PLACED"
        return OrderPlaced(order_id=self.id, total=self.total, placed_at=datetime.now())

    def cancel(self) -> OrderCancelled:
        """Business rule: can only cancel pending or placed orders."""
        if self.status in ["SHIPPED", "DELIVERED", "CANCELLED"]:
            raise DomainException(f"Cannot cancel {self.status} order")

        old_status = self.status
        self.status = "CANCELLED"
        return OrderCancelled(order_id=self.id, previous_status=old_status, cancelled_at=datetime.now())

    def ship(self) -> Self:
        """Business rule: can only ship placed orders."""
        if self.status != "PLACED":
            raise DomainException(f"Cannot ship {self.status} order")
        self.status = "SHIPPED"
        return self

    def _calculate_total(self) -> None:
        """Private: calculate order total."""
        total = sum(item.subtotal.amount for item in self.items)
        self.total = Money(amount=Decimal(str(total)), currency="USD")

    def __eq__(self, other) -> bool:
        """Entities equal by ID, not by attributes."""
        if not isinstance(other, Order):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID for use in sets/dicts."""
        return hash(self.id)
```

### Entity Best Practices

entity_best_practices[8]{practice,description,example}:
Encapsulate state,Don't expose mutable collections directly,Return copy or use property
Business rules in methods,Validate state changes in entity methods,activate() deactivate() place() cancel()
Raise domain exceptions,Use domain-specific exceptions,DomainException not ValueError
Return self for chaining,Enable fluent interface,return self from mutation methods
Use value objects,Compose with VOs not primitives,Money Email not Decimal str
Emit domain events,Signal important state changes,Return OrderPlaced event from place()
Keep focused,Single Responsibility Principle,Order handles order logic not shipping logic
Private helpers,Use underscore prefix for internal methods,_calculate_total() _validate()

## Pattern 2: Value Objects

**Immutable objects defined by their attributes - equality by value.**

### Value Object Characteristics

value_object_characteristics[5]{characteristic,description,implementation}:
Immutability,Cannot change after creation,dataclass(frozen=True)
Value equality,Equal if all attributes equal,Default __eq__ from frozen dataclass
No identity,No ID field,Only value attributes
Self-validation,Validates in __post_init__,Raise exception if invalid
Replaceability,Replace entire object instead of mutating,Create new instance with dataclasses.replace()

### Value Object Implementation: Email

```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re
from domain.exceptions import InvalidEmailException

@dataclass(frozen=True)  # Immutable!
class Email:
    """Email value object."""
    value: str

    def __post_init__(self):
        """Validate email format on creation."""
        if not self._is_valid(self.value):
            raise InvalidEmailException(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        """Business rule: email format validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def domain(self) -> str:
        """Extract domain from email."""
        return self.value.split('@')[1]

    def __str__(self) -> str:
        return self.value
```

### Value Object Implementation: Money

```python
# domain/value_objects/money.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Self
from domain.exceptions import DomainException

@dataclass(frozen=True)
class Money:
    """Money value object - immutable."""
    amount: Decimal
    currency: str

    def __post_init__(self):
        """Validate money values."""
        if not isinstance(self.amount, Decimal):
            raise DomainException("Amount must be Decimal")
        if self.currency not in ["USD", "EUR", "GBP"]:
            raise DomainException(f"Unsupported currency: {self.currency}")

    def add(self, other: Self) -> Self:
        """Add two money values (same currency)."""
        self._check_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def subtract(self, other: Self) -> Self:
        """Subtract two money values (same currency)."""
        self._check_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def multiply(self, factor: Decimal) -> Self:
        """Multiply money by factor."""
        return Money(amount=self.amount * factor, currency=self.currency)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == Decimal("0")

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > Decimal("0")

    def _check_currency(self, other: Self) -> None:
        """Business rule: can't operate on different currencies."""
        if self.currency != other.currency:
            raise DomainException(
                f"Cannot operate on different currencies: {self.currency} and {other.currency}"
            )

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
```

### Value Object Implementation: Address

```python
# domain/value_objects/address.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Address:
    """Address value object."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str

    def __post_init__(self):
        """Validate address components."""
        if not self.street or not self.city:
            raise ValueError("Street and city are required")
        if len(self.zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

    def full_address(self) -> str:
        """Format full address."""
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"

    def __str__(self) -> str:
        return self.full_address()
```

### Value Object Best Practices

value_object_best_practices[7]{practice,description,example}:
Always frozen,Use dataclass(frozen=True),@dataclass(frozen=True)
Validate in __post_init__,Fail fast on invalid values,Check format and constraints
No setters,Immutable - no way to modify,Use dataclasses.replace() to create new
Business logic methods,Include domain operations,add() subtract() for Money
Primitive obsession fix,Replace primitives with VOs,Email instead of str Money instead of float
Equality by value,Default behavior from frozen dataclass,Two Money(100 USD) are equal
Small and focused,Single concept per VO,Email not EmailAndPhone

## Pattern 3: Aggregates

**Cluster of entities and value objects with consistency boundary.**

### Aggregate Characteristics

aggregate_characteristics[6]{characteristic,description,implementation}:
Root entity,One entity as aggregate root,Order is root OrderItem is child
Consistency boundary,All changes go through root,Can't modify OrderItem directly
Transactional boundary,Saved/loaded as single unit,Repository saves entire aggregate
External references,Outside references only to root,Reference Order.id not OrderItem.id
Invariant enforcement,Root enforces business rules,Order.add_item() validates total
Single responsibility,Focused aggregate scope,Order aggregate not OrderAndShipping

### Aggregate Implementation

```python
# domain/entities/order.py (Aggregate Root)
from dataclasses import dataclass, field
from typing import List
from domain.value_objects.order_item import OrderItem
from domain.value_objects.money import Money

@dataclass
class Order:
    """Order aggregate root."""
    id: int
    customer_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: str = "PENDING"

    def add_item(self, product_id: int, quantity: int, price: Money) -> None:
        """Add item - root enforces invariants."""
        if self.status != "PENDING":
            raise DomainException("Can't modify non-pending order")

        # Check if item already exists
        existing = self._find_item(product_id)
        if existing:
            existing.increase_quantity(quantity)
        else:
            item = OrderItem(
                id=self._next_item_id(),
                product_id=product_id,
                quantity=quantity,
                unit_price=price
            )
            self.items.append(item)

        # Invariant: order total must not exceed limit
        if self.calculate_total().amount > 10000:
            raise DomainException("Order total exceeds limit")

    def remove_item(self, product_id: int) -> None:
        """Remove item through root."""
        if self.status != "PENDING":
            raise DomainException("Can't modify non-pending order")
        self.items = [i for i in self.items if i.product_id != product_id]

    def calculate_total(self) -> Money:
        """Aggregate calculation."""
        total = sum(item.subtotal().amount for item in self.items)
        return Money(amount=total, currency="USD")

    def _find_item(self, product_id: int) -> OrderItem | None:
        """Private: find item in aggregate."""
        return next((i for i in self.items if i.product_id == product_id), None)

    def _next_item_id(self) -> str:
        """Private: generate next item ID."""
        return f"item_{len(self.items) + 1}"

# domain/value_objects/order_item.py (Not aggregate root)
@dataclass
class OrderItem:
    """Order item - part of Order aggregate, not standalone."""
    id: str
    product_id: int
    quantity: int
    unit_price: Money

    def subtotal(self) -> Money:
        """Calculate item subtotal."""
        return self.unit_price.multiply(Decimal(str(self.quantity)))

    def increase_quantity(self, amount: int) -> None:
        """Modify quantity - only called from Order root."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.quantity += amount
```

### Aggregate Rules

aggregate_rules[7]{rule,explanation,example}:
Small aggregates,Keep aggregates focused and small,Order with OrderItems not Order with Customer with Address
Root is entry point,All changes through root,order.add_item() not order.items.append()
One repository per aggregate,Repo saves entire aggregate,OrderRepository not OrderItemRepository
Reference by ID,Aggregates reference each other by ID,Order stores customer_id not Customer object
Eventual consistency,Between aggregates not within,Order and Inventory are separate aggregates
Transactional boundary,One aggregate per transaction,Don't modify Order and Shipping in same transaction
Clear boundaries,Each aggregate is conceptually separate,Order manages items not shipping logistics

## Pattern 4: Domain Events

**Events representing something that happened in the domain.**

### Domain Event Implementation

```python
# domain/events/order_events.py
from dataclasses import dataclass
from datetime import datetime
from domain.value_objects.money import Money

@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events."""
    occurred_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class OrderPlaced(DomainEvent):
    """Event: Order was placed."""
    order_id: int
    customer_id: int
    total: Money

@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """Event: Order was cancelled."""
    order_id: int
    reason: str

@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """Event: Order was shipped."""
    order_id: int
    tracking_number: str
    carrier: str
```

### Using Domain Events

```python
# domain/entities/order.py
@dataclass
class Order:
    id: int
    status: str
    _events: List[DomainEvent] = field(default_factory=list, init=False)

    def place(self) -> None:
        """Place order and emit event."""
        if self.status != "PENDING":
            raise DomainException("Can't place non-pending order")

        self.status = "PLACED"

        # Emit domain event
        event = OrderPlaced(
            order_id=self.id,
            customer_id=self.customer_id,
            total=self.calculate_total(),
            occurred_at=datetime.now()
        )
        self._events.append(event)

    def collect_events(self) -> List[DomainEvent]:
        """Collect and clear events."""
        events = self._events.copy()
        self._events.clear()
        return events
```

### Event Handler Pattern

```python
# application/event_handlers/order_event_handlers.py
from domain.events.order_events import OrderPlaced
from application.ports.email_service import EmailService

class OrderPlacedHandler:
    """Handle OrderPlaced event."""

    def __init__(self, email_service: EmailService):
        self._email_service = email_service

    def handle(self, event: OrderPlaced) -> None:
        """Send confirmation email when order placed."""
        self._email_service.send_order_confirmation(
            customer_id=event.customer_id,
            order_id=event.order_id,
            total=event.total
        )
```

## Pattern 5: Domain Services

**Stateless operations that don't naturally fit in entities or value objects.**

### When to Use Domain Services

domain_service_use_cases[5]{scenario,reason,example}:
Operation spans multiple aggregates,Logic doesn't belong to single entity,TransferFunds(from_account to_account)
Pure calculation,Stateless computation,PricingService.calculate_discount()
External domain knowledge,Domain logic from external source,CurrencyConversionService
Complex validation,Validation across multiple entities,OrderValidationService
Coordination,Orchestrate multiple domain objects,InventoryAllocationService

### Domain Service Implementation

```python
# domain/services/pricing_service.py
from decimal import Decimal
from domain.value_objects.money import Money
from domain.entities.order import Order
from domain.entities.customer import Customer

class PricingService:
    """Domain service for pricing calculations."""

    @staticmethod
    def calculate_discount(order: Order, customer: Customer) -> Money:
        """Calculate discount based on customer tier and order total."""
        total = order.calculate_total()

        # Domain logic: discount rules
        if customer.tier == "GOLD" and total.amount > Decimal("1000"):
            discount_rate = Decimal("0.15")  # 15% for gold customers over $1000
        elif customer.tier == "SILVER" and total.amount > Decimal("500"):
            discount_rate = Decimal("0.10")  # 10% for silver customers over $500
        elif customer.tier == "BRONZE":
            discount_rate = Decimal("0.05")  # 5% for bronze customers
        else:
            discount_rate = Decimal("0")  # No discount

        discount_amount = total.amount * discount_rate
        return Money(amount=discount_amount, currency=total.currency)

    @staticmethod
    def apply_discount(order: Order, customer: Customer) -> Money:
        """Apply discount to order total."""
        total = order.calculate_total()
        discount = PricingService.calculate_discount(order, customer)
        return total.subtract(discount)
```

## Pydantic in Domain Layer - Decision Guide

### When to Use Pydantic

pydantic_usage[3]{location,use_pydantic,reason}:
Presentation Layer (API schemas),YES,Validation serialization for HTTP boundaries
Application Layer (DTOs),MAYBE,If validation and serialization needed
Domain Layer (Entities/VOs),CAREFUL,Avoid dependency on external library

### Dataclass vs Pydantic in Domain

```python
# ✅ PREFERRED: Pure dataclass in domain
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email")

# ⚠️ ACCEPTABLE: Pydantic in domain (document decision in ADR)
from pydantic import BaseModel, EmailStr

class Email(BaseModel):
    value: EmailStr

    class Config:
        frozen = True

# ✅ BEST: Pydantic in Presentation, dataclass in Domain
# Presentation layer (API schema)
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str

# Domain layer (pure dataclass)
@dataclass(frozen=True)
class Email:
    value: str
```

## Common Domain Modeling Mistakes

### Mistake 1: Anemic Domain Model

```python
# ❌ WRONG: Entity is just data container
@dataclass
class Order:
    id: int
    total: Money
    status: str

# Business logic in service
class OrderService:
    def place_order(self, order: Order):
        order.status = "PLACED"  # Business logic outside entity
```

**Fix**: Move logic to entity

```python
# ✅ CORRECT: Rich domain model
@dataclass
class Order:
    id: int
    total: Money
    status: str

    def place(self) -> None:
        """Business logic in entity."""
        if self.status != "PENDING":
            raise DomainException("Can't place non-pending order")
        self.status = "PLACED"
```

### Mistake 2: Primitive Obsession

```python
# ❌ WRONG: Using primitives instead of value objects
@dataclass
class User:
    id: int
    email: str  # Just a string
    balance: float  # Just a float
```

**Fix**: Use value objects

```python
# ✅ CORRECT: Value objects instead of primitives
@dataclass
class User:
    id: int
    email: Email  # Value object
    balance: Money  # Value object
```

### Mistake 3: Large Aggregates

```python
# ❌ WRONG: Aggregate too large
@dataclass
class Order:
    id: int
    customer: Customer  # Entire customer object
    items: List[OrderItem]
    shipment: Shipment  # Entire shipment object
    invoices: List[Invoice]  # All invoices
```

**Fix**: Keep aggregates small, reference by ID

```python
# ✅ CORRECT: Small aggregate with ID references
@dataclass
class Order:
    id: int
    customer_id: int  # Reference by ID
    items: List[OrderItem]
    # Shipment is separate aggregate
    # Invoice is separate aggregate
```

## Domain Layer Checklist

domain_layer_checklist[12]{check,requirement}:
No external dependencies,Domain imports only standard library and internal domain modules
Entities have behavior,Business logic in entity methods not services
Value objects immutable,All VOs use frozen=True
Entities have identity,Entity equality based on ID
VOs have value equality,VO equality based on attributes
Business rules enforced,Invariants checked in entity methods
Domain exceptions,Custom exceptions for business rule violations
Rich models not anemic,Avoid data classes with no behavior
Small aggregates,Each aggregate focused on single consistency boundary
Value objects used,Replace primitives with VOs where appropriate
Domain events emitted,Important state changes captured as events
Clear bounded context,Domain model has explicit boundaries

---

**File Size**: 472/500 lines max ✅
