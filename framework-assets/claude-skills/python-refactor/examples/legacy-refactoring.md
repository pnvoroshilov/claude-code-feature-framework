# Complete Legacy Refactoring Example

**Step-by-step walkthrough of refactoring a legacy Python monolith to Clean Architecture with DDD patterns.**

## The Legacy System: E-Commerce Order Service

### Starting Point: Spaghetti Code

```python
# legacy/order_service.py - THE PROBLEM
"""
Legacy monolithic order service with multiple issues:
- Business logic mixed with data access
- Direct database queries in service
- No separation of concerns
- Difficult to test
- Tightly coupled to Flask and SQLAlchemy
"""
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
engine = create_engine("postgresql://user:pass@localhost/db")
Session = sessionmaker(bind=engine)

# ORM models mixed with business logic
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_email = Column(String)
    total = Column(Float)
    status = Column(String, default='pending')
    discount_applied = Column(Boolean, default=False)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

# God class with all responsibilities
class OrderService:
    def __init__(self):
        self.session = Session()

    def create_order(self, customer_email, items):
        """Everything mixed together - validation, business logic, persistence, email."""
        # Validation in service
        if not customer_email or '@' not in customer_email:
            raise ValueError("Invalid email")

        if not items:
            raise ValueError("Order must have items")

        # Business logic mixed with ORM
        order = Order(customer_email=customer_email, total=0)
        self.session.add(order)
        self.session.flush()  # Get ID

        total = 0
        for item in items:
            # Direct ORM usage
            order_item = OrderItem(
                order_id=order.id,
                product_name=item['name'],
                quantity=item['quantity'],
                price=item['price']
            )
            self.session.add(order_item)
            total += item['quantity'] * item['price']

        # Business rule embedded in service
        if total > 100:
            total *= 0.9  # 10% discount
            order.discount_applied = True

        order.total = total
        self.session.commit()

        # Side effect - sending email in business logic
        self._send_confirmation(customer_email, order.id, total)

        return {'order_id': order.id, 'total': total}

    def _send_confirmation(self, email, order_id, total):
        """Email sending mixed with business logic."""
        msg = MIMEText(f"Order {order_id} confirmed. Total: ${total}")
        msg['Subject'] = 'Order Confirmation'
        with smtplib.SMTP('localhost') as server:
            server.send_message(msg)

# Flask routes with business logic
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    service = OrderService()
    try:
        result = service.create_order(data['email'], data['items'])
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### Problems Identified

legacy_problems[10]{problem,description,impact}:
God class,OrderService handles everything,Cannot test in isolation
ORM in business logic,SQLAlchemy queries throughout,Cannot swap database
Email in service,SMTP calls embedded,Cannot mock for tests
No domain model,ORM models are domain,Business rules scattered
Validation scattered,Checks in multiple places,Inconsistent validation
Direct dependencies,Hard-coded Session creation,Cannot inject mocks
No interfaces,Concrete implementations only,Tight coupling
Side effects,Email sent during business logic,Hard to predict behavior
Flask coupling,Routes know business logic,Framework lock-in
No testing,Cannot unit test effectively,Regressions likely

## Refactoring Plan

### Migration Strategy

refactoring_phases[6]{phase,scope,deliverable}:
Phase 1,Extract Domain Model,Entities Value Objects in domain/
Phase 2,Define Ports,ABC interfaces in application/ports/
Phase 3,Create Use Cases,Business logic in application/use_cases/
Phase 4,Implement Adapters,Repository and services in infrastructure/
Phase 5,Setup DI,Dependency injection container
Phase 6,Migrate Presentation,Thin FastAPI controllers

## Phase 1: Extract Domain Model

### Step 1.1: Create Value Objects

```python
# domain/value_objects/email.py
from dataclasses import dataclass
import re
from domain.exceptions import InvalidEmailException

@dataclass(frozen=True)
class Email:
    """Email value object - immutable, self-validating."""
    value: str

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailException(f"Invalid email: {self.value}")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

# domain/value_objects/money.py
from dataclasses import dataclass
from decimal import Decimal
from typing import Self
from domain.exceptions import DomainException

@dataclass(frozen=True)
class Money:
    """Money value object with currency."""
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < Decimal("0"):
            raise DomainException("Amount cannot be negative")

    def add(self, other: Self) -> Self:
        self._check_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: Decimal) -> Self:
        return Money(amount=self.amount * factor, currency=self.currency)

    def apply_discount(self, percentage: Decimal) -> Self:
        """Apply percentage discount."""
        discount = self.amount * (percentage / Decimal("100"))
        return Money(amount=self.amount - discount, currency=self.currency)

    def _check_currency(self, other: Self) -> None:
        if self.currency != other.currency:
            raise DomainException("Currency mismatch")

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
```

### Step 1.2: Create Domain Entities

```python
# domain/entities/order.py
from dataclasses import dataclass, field
from typing import List, Self
from decimal import Decimal
from domain.value_objects.money import Money
from domain.value_objects.email import Email
from domain.exceptions import DomainException
from domain.events.order_events import OrderPlaced

@dataclass
class OrderItem:
    """Order item - part of Order aggregate."""
    id: str
    product_name: str
    quantity: int
    unit_price: Money

    def subtotal(self) -> Money:
        return self.unit_price.multiply(Decimal(str(self.quantity)))

@dataclass
class Order:
    """Order aggregate root with business logic."""
    id: int
    customer_email: Email
    items: List[OrderItem] = field(default_factory=list)
    status: str = "PENDING"
    discount_applied: bool = False

    # Business rules as constants
    DISCOUNT_THRESHOLD = Decimal("100")
    DISCOUNT_PERCENTAGE = Decimal("10")

    def add_item(self, item: OrderItem) -> Self:
        """Add item to order."""
        if self.status != "PENDING":
            raise DomainException("Cannot modify non-pending order")
        self.items.append(item)
        return self

    def calculate_total(self) -> Money:
        """Calculate order total with discount logic."""
        if not self.items:
            return Money(amount=Decimal("0"))

        subtotal = Money(amount=Decimal("0"))
        for item in self.items:
            subtotal = subtotal.add(item.subtotal())

        # Business rule: 10% discount for orders over $100
        if subtotal.amount > self.DISCOUNT_THRESHOLD:
            self.discount_applied = True
            return subtotal.apply_discount(self.DISCOUNT_PERCENTAGE)

        return subtotal

    def place(self) -> OrderPlaced:
        """Place order - business rule enforcement."""
        if self.status != "PENDING":
            raise DomainException("Can only place pending orders")
        if not self.items:
            raise DomainException("Cannot place empty order")

        self.status = "PLACED"
        total = self.calculate_total()

        return OrderPlaced(
            order_id=self.id,
            customer_email=self.customer_email.value,
            total=total,
            discount_applied=self.discount_applied
        )

# domain/events/order_events.py
from dataclasses import dataclass
from datetime import datetime
from domain.value_objects.money import Money

@dataclass(frozen=True)
class OrderPlaced:
    """Domain event: Order was placed."""
    order_id: int
    customer_email: str
    total: Money
    discount_applied: bool
    occurred_at: datetime = field(default_factory=datetime.now)
```

## Phase 2: Define Application Ports

```python
# application/ports/repositories.py
from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.order import Order

class OrderRepository(ABC):
    """Port: Order persistence interface."""

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        pass

    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

# application/ports/email_service.py
from abc import ABC, abstractmethod
from domain.events.order_events import OrderPlaced

class EmailService(ABC):
    """Port: Email sending interface."""

    @abstractmethod
    def send_order_confirmation(self, event: OrderPlaced) -> None:
        pass
```

## Phase 3: Create Use Cases

```python
# application/use_cases/create_order.py
from dataclasses import dataclass
from typing import List
from decimal import Decimal
from application.ports.repositories import OrderRepository
from application.ports.email_service import EmailService
from domain.entities.order import Order, OrderItem
from domain.value_objects.email import Email
from domain.value_objects.money import Money

@dataclass
class OrderItemDTO:
    """Input DTO for order item."""
    product_name: str
    quantity: int
    price: float

@dataclass
class CreateOrderCommand:
    """Input for create order use case."""
    customer_email: str
    items: List[OrderItemDTO]

@dataclass
class CreateOrderResult:
    """Output from create order use case."""
    order_id: int
    total: str
    discount_applied: bool

class CreateOrderUseCase:
    """Create order use case - orchestrates domain logic."""

    def __init__(
        self,
        order_repo: OrderRepository,
        email_service: EmailService
    ):
        self._order_repo = order_repo
        self._email_service = email_service

    def execute(self, command: CreateOrderCommand) -> CreateOrderResult:
        """Execute create order logic."""
        # Create domain objects with validation
        email = Email(command.customer_email)

        # Build order aggregate
        order = Order(id=0, customer_email=email)

        for idx, item_dto in enumerate(command.items):
            order_item = OrderItem(
                id=f"item_{idx}",
                product_name=item_dto.product_name,
                quantity=item_dto.quantity,
                unit_price=Money(amount=Decimal(str(item_dto.price)))
            )
            order.add_item(order_item)

        # Domain operation returns event
        event = order.place()

        # Persist
        saved_order = self._order_repo.save(order)

        # Handle event
        self._email_service.send_order_confirmation(event)

        return CreateOrderResult(
            order_id=saved_order.id,
            total=str(event.total),
            discount_applied=event.discount_applied
        )
```

## Phase 4: Implement Infrastructure

```python
# infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class OrderORM(Base):
    """SQLAlchemy ORM model - infrastructure only."""
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_email = Column(String(255), nullable=False)
    total = Column(Numeric(10, 2))
    status = Column(String(50), default='PENDING')
    discount_applied = Column(Boolean, default=False)
    items = relationship("OrderItemORM", back_populates="order")

class OrderItemORM(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    item_id = Column(String(50))
    product_name = Column(String(255))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    order = relationship("OrderORM", back_populates="items")

# infrastructure/repositories/order_repository.py
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from application.ports.repositories import OrderRepository
from domain.entities.order import Order, OrderItem
from domain.value_objects.email import Email
from domain.value_objects.money import Money
from infrastructure.database.models import OrderORM, OrderItemORM

class SQLAlchemyOrderRepository(OrderRepository):
    """SQLAlchemy implementation of OrderRepository."""

    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, order_id: int) -> Optional[Order]:
        orm_order = self._session.query(OrderORM).filter_by(id=order_id).first()
        return self._to_domain(orm_order) if orm_order else None

    def save(self, order: Order) -> Order:
        orm_order = self._to_orm(order)
        self._session.add(orm_order)
        self._session.commit()
        self._session.refresh(orm_order)
        return self._to_domain(orm_order)

    def _to_domain(self, orm: OrderORM) -> Order:
        items = [
            OrderItem(
                id=item.item_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=Money(amount=Decimal(str(item.unit_price)))
            )
            for item in orm.items
        ]
        return Order(
            id=orm.id,
            customer_email=Email(orm.customer_email),
            items=items,
            status=orm.status,
            discount_applied=orm.discount_applied
        )

    def _to_orm(self, order: Order) -> OrderORM:
        orm_order = OrderORM(
            customer_email=order.customer_email.value,
            total=float(order.calculate_total().amount),
            status=order.status,
            discount_applied=order.discount_applied
        )
        orm_order.items = [
            OrderItemORM(
                item_id=item.id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=float(item.unit_price.amount)
            )
            for item in order.items
        ]
        return orm_order

# infrastructure/adapters/email_adapter.py
from application.ports.email_service import EmailService
from domain.events.order_events import OrderPlaced
import smtplib
from email.mime.text import MIMEText

class SMTPEmailService(EmailService):
    """SMTP implementation of EmailService."""

    def __init__(self, smtp_host: str, smtp_port: int):
        self._host = smtp_host
        self._port = smtp_port

    def send_order_confirmation(self, event: OrderPlaced) -> None:
        msg = MIMEText(
            f"Order {event.order_id} confirmed!\n"
            f"Total: {event.total}\n"
            f"Discount applied: {event.discount_applied}"
        )
        msg['Subject'] = 'Order Confirmation'
        msg['To'] = event.customer_email

        with smtplib.SMTP(self._host, self._port) as server:
            server.send_message(msg)
```

## Phase 5: Testing the Refactored Code

```python
# tests/domain/test_order.py
import pytest
from decimal import Decimal
from domain.entities.order import Order, OrderItem
from domain.value_objects.email import Email
from domain.value_objects.money import Money
from domain.exceptions import DomainException

def test_order_calculates_total():
    order = Order(id=1, customer_email=Email("test@example.com"))
    order.add_item(OrderItem(id="1", product_name="Widget", quantity=2, unit_price=Money(Decimal("25"))))
    assert order.calculate_total().amount == Decimal("50")

def test_order_applies_discount_over_threshold():
    order = Order(id=1, customer_email=Email("test@example.com"))
    order.add_item(OrderItem(id="1", product_name="Widget", quantity=5, unit_price=Money(Decimal("50"))))
    # Total before discount: $250, after 10% discount: $225
    assert order.calculate_total().amount == Decimal("225")
    assert order.discount_applied

def test_cannot_place_empty_order():
    order = Order(id=1, customer_email=Email("test@example.com"))
    with pytest.raises(DomainException, match="empty order"):
        order.place()

# tests/application/test_create_order.py
from unittest.mock import Mock
from application.use_cases.create_order import CreateOrderUseCase, CreateOrderCommand, OrderItemDTO

def test_create_order_success():
    mock_repo = Mock()
    mock_repo.save.return_value = Order(id=1, customer_email=Email("test@example.com"))
    mock_email = Mock()

    use_case = CreateOrderUseCase(mock_repo, mock_email)
    command = CreateOrderCommand(
        customer_email="test@example.com",
        items=[OrderItemDTO(product_name="Widget", quantity=2, price=25.0)]
    )

    result = use_case.execute(command)

    assert result.order_id == 1
    mock_repo.save.assert_called_once()
    mock_email.send_order_confirmation.assert_called_once()
```

## Before vs After Comparison

comparison[8]{aspect,before,after}:
Business Logic,Mixed in service and ORM,Encapsulated in domain entities
Data Access,Direct SQLAlchemy in service,Repository pattern with ABC
Email Sending,Embedded in service,Adapter behind interface
Validation,Scattered throughout,Value Objects self-validate
Testing,Difficult needs database,Easy with mocked dependencies
Framework,Tightly coupled to Flask,Framework-agnostic
Dependencies,Hard-coded instantiation,Dependency injection
Extensibility,Requires modifying service,Extend via new implementations

---

**File Size**: 470/500 lines max ✅
