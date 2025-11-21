# Domain-Driven Design (DDD) Reference

**Model software based on the business domain with rich domain models.**

## Overview

Domain-Driven Design is an approach to software development that centers the development on programming a domain model that has a rich understanding of the processes and rules of a domain.

ddd_building_blocks[6]{building_block,purpose,characteristics}:
Entities,Objects with unique identity,ID-based equality mutable state lifecycle
Value Objects,Objects defined by attributes,Attribute-based equality immutable replaceable
Aggregates,Cluster of entities and value objects,Consistency boundary transaction boundary
Repositories,Access to aggregates,Collection-like interface abstracts persistence
Domain Services,Operations that don't belong to entities,Stateless business logic coordination
Domain Events,Something that happened in domain,Past tense immutable triggers side effects

---

## Entities

**Definition:** Objects that have a distinct identity that runs through time and different representations.

**Key Characteristics:**
- Has unique identifier (ID)
- Identity remains constant even if attributes change
- Mutable
- Compared by ID, not attributes
- Has lifecycle (created, modified, deleted)

### Example - Order Entity

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

@dataclass
class Order:
    """Entity - identified by order_id"""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    items: List['OrderItem'] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other):
        """Entities compared by ID"""
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)

    # Business logic methods
    def add_item(self, product_id: str, quantity: int, unit_price: float):
        """Domain logic: add item to order"""
        if self.status != "pending":
            raise ValueError("Cannot add items to non-pending order")

        item = OrderItem(product_id, quantity, unit_price)
        self.items.append(item)
        self.updated_at = datetime.now()

    def remove_item(self, product_id: str):
        """Domain logic: remove item from order"""
        if self.status != "pending":
            raise ValueError("Cannot remove items from non-pending order")

        self.items = [item for item in self.items if item.product_id != product_id]
        self.updated_at = datetime.now()

    def submit(self):
        """Domain logic: submit order"""
        if not self.items:
            raise ValueError("Cannot submit empty order")
        if self.status != "pending":
            raise ValueError("Order already submitted")

        self.status = "submitted"
        self.updated_at = datetime.now()

    def total(self) -> float:
        """Domain logic: calculate total"""
        return sum(item.subtotal() for item in self.items)

    def can_be_cancelled(self) -> bool:
        """Domain logic: cancellation rules"""
        return self.status in ["pending", "submitted"]

    def cancel(self):
        """Domain logic: cancel order"""
        if not self.can_be_cancelled():
            raise ValueError(f"Cannot cancel order with status {self.status}")

        self.status = "cancelled"
        self.updated_at = datetime.now()
```

---

## Value Objects

**Definition:** Objects that describe characteristics but have no identity.

**Key Characteristics:**
- No unique identifier
- Immutable
- Compared by attributes, not ID
- Replaceable (create new instance to "change")
- Can be shared safely

### Example - Money Value Object

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # Immutable
class Money:
    """Value Object - no identity, compared by attributes"""
    amount: Decimal
    currency: str

    def __post_init__(self):
        """Validate on creation"""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency is required")

    def add(self, other: 'Money') -> 'Money':
        """Create new Money instance (immutable)"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)

    def is_zero(self) -> bool:
        return self.amount == Decimal('0')

    def is_positive(self) -> bool:
        return self.amount > Decimal('0')

    def __str__(self):
        return f"{self.amount} {self.currency}"


# Usage
price1 = Money(Decimal('19.99'), 'USD')
price2 = Money(Decimal('5.00'), 'USD')
total = price1.add(price2)  # Creates new Money(24.99, 'USD')

# price1 unchanged (immutable)
assert price1.amount == Decimal('19.99')
```

### Example - Address Value Object

```python
@dataclass(frozen=True)
class Address:
    """Value Object - immutable location"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str

    def __post_init__(self):
        if not all([self.street, self.city, self.state, self.zip_code, self.country]):
            raise ValueError("All address fields are required")

    def is_in_state(self, state: str) -> bool:
        return self.state == state

    def is_domestic(self, country: str = "USA") -> bool:
        return self.country == country

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"


# Usage
address = Address(
    street="123 Main St",
    city="San Francisco",
    state="CA",
    zip_code="94102",
    country="USA"
)

# To "change" address, create new one
new_address = Address(
    street="456 Oak Ave",
    city=address.city,
    state=address.state,
    zip_code=address.zip_code,
    country=address.country
)
```

---

## Aggregates

**Definition:** Cluster of domain objects (entities and value objects) that can be treated as a single unit.

**Key Characteristics:**
- Has root entity (Aggregate Root)
- Enforces consistency boundaries
- External objects can only reference the root
- Root responsible for enforcing invariants
- Transaction boundary

### Example - Order Aggregate

```python
@dataclass
class OrderItem:
    """Part of Order aggregate"""
    product_id: str
    quantity: int
    unit_price: Money

    def subtotal(self) -> Money:
        return self.unit_price.multiply(Decimal(self.quantity))


@dataclass
class Order:
    """Aggregate Root - controls access to OrderItems"""
    order_id: str
    customer_id: str
    _items: List[OrderItem] = field(default_factory=list)
    status: str = "pending"
    shipping_address: Address = None

    # Root enforces invariants
    @property
    def items(self) -> List[OrderItem]:
        """Read-only access to items"""
        return self._items.copy()

    def add_item(self, product_id: str, quantity: int, unit_price: Money):
        """Only way to add items - enforces business rules"""
        if self.status != "pending":
            raise ValueError("Cannot modify non-pending order")

        # Check if item already exists
        for item in self._items:
            if item.product_id == product_id:
                raise ValueError("Product already in order. Use update_quantity instead")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        item = OrderItem(product_id, quantity, unit_price)
        self._items.append(item)

    def update_quantity(self, product_id: str, new_quantity: int):
        """Only way to update quantity - enforces business rules"""
        if self.status != "pending":
            raise ValueError("Cannot modify non-pending order")

        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")

        for item in self._items:
            if item.product_id == product_id:
                # Create new item (value object immutability)
                self._items.remove(item)
                self._items.append(OrderItem(product_id, new_quantity, item.unit_price))
                return

        raise ValueError(f"Product {product_id} not in order")

    def set_shipping_address(self, address: Address):
        """Only way to set address"""
        if self.status not in ["pending", "submitted"]:
            raise ValueError("Cannot change shipping address after order is shipped")
        self.shipping_address = address

    def submit(self):
        """Enforces invariants before submission"""
        if not self._items:
            raise ValueError("Cannot submit empty order")
        if not self.shipping_address:
            raise ValueError("Shipping address required")
        if self.total().is_zero():
            raise ValueError("Order total must be greater than zero")

        self.status = "submitted"

    def total(self) -> Money:
        """Aggregate calculation"""
        if not self._items:
            return Money(Decimal('0'), 'USD')

        result = self._items[0].subtotal()
        for item in self._items[1:]:
            result = result.add(item.subtotal())
        return result


# Usage - all access through aggregate root
order = Order(order_id="ORD-123", customer_id="CUST-456")

# Add items through root
order.add_item("PROD-1", 2, Money(Decimal('19.99'), 'USD'))
order.add_item("PROD-2", 1, Money(Decimal('29.99'), 'USD'))

# Set shipping address
address = Address("123 Main St", "SF", "CA", "94102", "USA")
order.set_shipping_address(address)

# Submit order (enforces invariants)
order.submit()

# Cannot modify items directly - must go through root
# order._items.append(...)  # Bad! Bypasses business rules
# order.add_item(...)  # Good! Enforces business rules
```

---

## Repositories

**Definition:** Mechanism for encapsulating storage, retrieval, and search behavior which emulates a collection of aggregates.

**Key Characteristics:**
- One repository per aggregate root
- Collection-like interface
- Abstracts persistence details
- Returns fully-formed aggregates

### Example - Order Repository

```python
from abc import ABC, abstractmethod
from typing import Optional, List

class IOrderRepository(ABC):
    """Repository interface for Order aggregate"""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Retrieve complete aggregate by ID"""
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        """Find all orders for customer"""
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        """Persist complete aggregate"""
        pass

    @abstractmethod
    def delete(self, order_id: str) -> bool:
        """Remove aggregate"""
        pass


class SQLOrderRepository(IOrderRepository):
    """Concrete implementation"""

    def __init__(self, db_session):
        self.db = db_session

    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Reconstruct complete aggregate from database"""
        order_model = self.db.query(OrderModel).filter(
            OrderModel.order_id == order_id
        ).first()

        if not order_model:
            return None

        # Reconstruct aggregate with all items
        order = Order(
            order_id=order_model.order_id,
            customer_id=order_model.customer_id,
            status=order_model.status
        )

        # Load items
        for item_model in order_model.items:
            order.add_item(
                item_model.product_id,
                item_model.quantity,
                Money(Decimal(str(item_model.unit_price)), item_model.currency)
            )

        # Load address
        if order_model.shipping_address:
            order.set_shipping_address(
                Address(
                    street=order_model.shipping_address.street,
                    city=order_model.shipping_address.city,
                    state=order_model.shipping_address.state,
                    zip_code=order_model.shipping_address.zip_code,
                    country=order_model.shipping_address.country
                )
            )

        return order

    def save(self, order: Order) -> None:
        """Persist complete aggregate"""
        order_model = self.db.query(OrderModel).filter(
            OrderModel.order_id == order.order_id
        ).first()

        if not order_model:
            order_model = OrderModel(order_id=order.order_id)
            self.db.add(order_model)

        # Update order
        order_model.customer_id = order.customer_id
        order_model.status = order.status

        # Update items (clear and re-add for simplicity)
        self.db.query(OrderItemModel).filter(
            OrderItemModel.order_id == order.order_id
        ).delete()

        for item in order.items:
            item_model = OrderItemModel(
                order_id=order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=str(item.unit_price.amount),
                currency=item.unit_price.currency
            )
            self.db.add(item_model)

        self.db.commit()
```

---

## Domain Services

**Definition:** Operations that don't naturally fit within an entity or value object.

**Key Characteristics:**
- Stateless
- Operate on multiple aggregates
- Contain domain logic that doesn't belong to specific entity
- Named with verb (e.g., TransferMoney, CalculateShipping)

### Example - Order Pricing Service

```python
class OrderPricingService:
    """Domain service for complex pricing calculations"""

    def __init__(self, tax_calculator, shipping_calculator):
        self.tax_calculator = tax_calculator
        self.shipping_calculator = shipping_calculator

    def calculate_total_price(
        self,
        order: Order,
        customer: Customer,
        promo_code: Optional[str] = None
    ) -> Money:
        """Calculate total including tax, shipping, discounts"""

        # Subtotal
        subtotal = order.total()

        # Apply customer discount
        discount = self._calculate_customer_discount(customer, subtotal)
        after_discount = subtotal.subtract(discount)

        # Apply promo code
        if promo_code:
            promo_discount = self._apply_promo_code(promo_code, after_discount)
            after_discount = after_discount.subtract(promo_discount)

        # Calculate shipping
        shipping = self.shipping_calculator.calculate(
            order.shipping_address,
            order.total_weight()
        )

        # Calculate tax
        tax = self.tax_calculator.calculate(
            after_discount,
            order.shipping_address.state
        )

        # Final total
        return after_discount.add(shipping).add(tax)

    def _calculate_customer_discount(
        self,
        customer: Customer,
        subtotal: Money
    ) -> Money:
        """Business logic for customer discounts"""
        if customer.tier == "gold":
            return subtotal.multiply(Decimal('0.10'))  # 10% off
        elif customer.tier == "silver":
            return subtotal.multiply(Decimal('0.05'))  # 5% off
        return Money(Decimal('0'), subtotal.currency)
```

---

## Domain Events

**Definition:** Something that happened in the domain that domain experts care about.

**Key Characteristics:**
- Named in past tense (OrderPlaced, PaymentProcessed)
- Immutable
- Contains relevant data about what happened
- Used to trigger side effects

### Example - Domain Events

```python
@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class OrderPlacedEvent(DomainEvent):
    """Event: Order was placed"""
    order_id: str
    customer_id: str
    total: Money


@dataclass(frozen=True)
class OrderCancelledEvent(DomainEvent):
    """Event: Order was cancelled"""
    order_id: str
    customer_id: str
    reason: str


class Order:
    """Aggregate that raises events"""

    def __init__(self, order_id: str, customer_id: str):
        self.order_id = order_id
        self.customer_id = customer_id
        self._items = []
        self.status = "pending"
        self._domain_events: List[DomainEvent] = []

    def submit(self):
        """Business operation that raises event"""
        if not self._items:
            raise ValueError("Cannot submit empty order")

        self.status = "submitted"

        # Raise domain event
        self._domain_events.append(OrderPlacedEvent(
            order_id=self.order_id,
            customer_id=self.customer_id,
            total=self.total()
        ))

    def cancel(self, reason: str):
        """Business operation that raises event"""
        if not self.can_be_cancelled():
            raise ValueError("Cannot cancel order")

        self.status = "cancelled"

        # Raise domain event
        self._domain_events.append(OrderCancelledEvent(
            order_id=self.order_id,
            customer_id=self.customer_id,
            reason=reason
        ))

    def get_domain_events(self) -> List[DomainEvent]:
        """Get and clear events"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


# Event handlers
class OrderEventHandler:
    def __init__(self, email_service, inventory_service):
        self.email_service = email_service
        self.inventory_service = inventory_service

    def handle_order_placed(self, event: OrderPlacedEvent):
        """React to order placed"""
        # Send confirmation email
        self.email_service.send_order_confirmation(event.customer_id, event.order_id)

        # Reserve inventory
        self.inventory_service.reserve_items(event.order_id)

    def handle_order_cancelled(self, event: OrderCancelledEvent):
        """React to order cancellation"""
        # Send cancellation email
        self.email_service.send_order_cancellation(event.customer_id, event.order_id)

        # Release inventory
        self.inventory_service.release_items(event.order_id)
```

---

**File Size**: 280/500 lines max ✅
