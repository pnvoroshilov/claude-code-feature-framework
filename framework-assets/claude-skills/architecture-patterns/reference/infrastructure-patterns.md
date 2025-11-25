# Infrastructure Patterns Reference

**Patterns for scalable, reliable, and maintainable system infrastructure.**

## Overview

Infrastructure patterns help you make decisions about:
- When to use microservices vs monolith
- How to design for high availability
- When containerization makes sense
- How to handle distributed systems challenges

---

## Monolith vs Microservices

### Decision Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│              MONOLITH vs MICROSERVICES DECISION                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Team Size < 10 developers? ──── YES ──► Start with Monolith        │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Clear domain boundaries? ──── NO ───► Stay with Monolith           │
│         │                              (boundaries will emerge)      │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Different scaling needs? ──── NO ───► Modular Monolith             │
│         │                              (best of both)               │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  DevOps maturity high? ─────── NO ───► Modular Monolith             │
│         │                              (ops overhead too high)       │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Consider Microservices (but start with 2-3, not 20)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Monolith

**Good Fit:**

| Scenario | Why Monolith |
|----------|--------------|
| New project / MVP | Faster development, easier changes |
| Small team (< 10) | No need for team isolation |
| Unclear domain boundaries | Refactor later when patterns emerge |
| Simple deployment needs | One artifact to deploy |
| Tight budget | Less infrastructure cost |

**Monolith Benefits:**
- Simpler development and debugging
- Easier data consistency (single DB)
- Lower operational complexity
- Better performance (no network calls)
- Easier refactoring

**Example: Well-Structured Monolith**

```
my-app/
├── src/
│   ├── modules/           # Domain modules (future microservices)
│   │   ├── users/
│   │   │   ├── api/       # HTTP handlers
│   │   │   ├── service/   # Business logic
│   │   │   ├── repository/# Data access
│   │   │   └── models/    # Domain models
│   │   ├── orders/
│   │   ├── payments/
│   │   └── inventory/
│   ├── shared/            # Shared utilities
│   └── infrastructure/    # DB, cache, etc.
├── tests/
└── main.py
```

### When to Use Microservices

**Good Fit:**

| Scenario | Why Microservices |
|----------|-------------------|
| Large organization (50+ devs) | Team autonomy needed |
| Different tech requirements | Polyglot persistence/languages |
| Parts need independent scaling | Scale only what's needed |
| Different deployment frequencies | Deploy users service daily, billing monthly |
| Regulatory requirements | Isolate PCI-compliant payment service |

**Microservices Challenges:**

| Challenge | Mitigation |
|-----------|------------|
| Network latency | Async communication, caching |
| Data consistency | Event sourcing, saga pattern |
| Debugging complexity | Distributed tracing (Jaeger) |
| Operational overhead | Kubernetes, service mesh |
| Testing difficulty | Contract testing, integration tests |

### Modular Monolith (Recommended Start)

**Best of both worlds:**

```python
# Modular monolith structure
# Each module has clear boundaries but shares deployment

# users/service.py
class UserService:
    """Module with explicit interface"""

    def __init__(self, user_repo: IUserRepository):
        self.repo = user_repo

    def get_user(self, user_id: int) -> User:
        return self.repo.find_by_id(user_id)

    def create_user(self, data: CreateUserDTO) -> User:
        # Business logic here
        return self.repo.save(User.create(data))

# orders/service.py
class OrderService:
    """Another module - communicates via defined interfaces"""

    def __init__(self, order_repo: IOrderRepository, user_service: UserService):
        self.repo = order_repo
        self.user_service = user_service  # Explicit dependency

    def create_order(self, user_id: int, items: list) -> Order:
        user = self.user_service.get_user(user_id)  # Internal call
        if not user:
            raise UserNotFoundError(user_id)
        return self.repo.save(Order.create(user, items))
```

**Migration Path:**

```
Phase 1: Monolith
├── All code in one deployment

Phase 2: Modular Monolith
├── Clear module boundaries
├── Interfaces between modules
├── Separate databases per module (optional)

Phase 3: Extract First Service (if needed)
├── Extract highest-value module
├── Keep others in monolith
├── API gateway for routing

Phase 4: Gradual Extraction
├── Extract as business needs dictate
├── Not everything needs to be a service
```

---

## Containerization & Docker

### When to Use Docker

**Good Use Cases:**

| Scenario | Benefit |
|----------|---------|
| Consistent environments | Dev = Staging = Prod |
| Complex dependencies | Package everything together |
| Multiple language services | Isolated runtimes |
| CI/CD pipelines | Reproducible builds |
| Microservices | Easy deployment unit |
| Local development | Same env as production |

**Skip Docker When:**

| Scenario | Why |
|----------|-----|
| Simple static site | Nginx alone is fine |
| Tiny VPS with limited RAM | Overhead not worth it |
| Legacy system migration | Too much rewrite |
| Team has no Docker experience | Learning curve |

### Docker Best Practices

**Dockerfile Optimization:**

```dockerfile
# Bad: Large image, slow builds
FROM python:3.11
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

# Good: Multi-stage, cached layers, small image
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

**Docker Compose for Development:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    volumes:
      - .:/app  # Hot reload in development

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

  cache:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### Kubernetes Decision

**When Kubernetes Makes Sense:**

| Scenario | K8s Value |
|----------|-----------|
| 10+ microservices | Orchestration needed |
| Auto-scaling requirements | Built-in HPA |
| Multi-cloud deployment | Portable abstractions |
| Zero-downtime deployments | Rolling updates |
| Large team / enterprise | Standard platform |

**When Kubernetes is Overkill:**

| Scenario | Better Alternative |
|----------|-------------------|
| 1-3 services | Docker Compose + VM |
| Small team (< 5 devs) | Managed PaaS (Heroku, Render) |
| Tight budget | Single server + systemd |
| Simple scaling needs | Cloud auto-scaling groups |

**Simpler Alternatives:**

```
Complexity Scale (low to high):
─────────────────────────────────────────────────►

Single Server  →  Docker Compose  →  Managed K8s  →  Self-hosted K8s
(systemd)         (Swarm)            (EKS, GKE)      (kubeadm)

Choose the simplest that meets your needs!
```

---

## High Availability Patterns

### Replication Strategies

**Database Replication:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRIMARY (Write)                               │
│                         │                                        │
│         ┌───────────────┼───────────────┐                        │
│         │               │               │                        │
│    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐                    │
│    │ Replica │    │ Replica │    │ Replica │   (Read)           │
│    │   1     │    │   2     │    │   3     │                    │
│    └─────────┘    └─────────┘    └─────────┘                    │
└─────────────────────────────────────────────────────────────────┘

Read queries → Any replica (load balanced)
Write queries → Primary only
```

**When to Use:**

| Pattern | Use When |
|---------|----------|
| Single Primary | Read-heavy workloads (blogs, catalogs) |
| Multi-Primary | Write-heavy, geo-distributed |
| Read Replicas | Scale reads without affecting writes |

### Failover Strategies

**Automatic Failover:**

```python
# Application-level failover
class DatabasePool:
    def __init__(self, primary_url: str, replica_urls: list[str]):
        self.primary = create_connection(primary_url)
        self.replicas = [create_connection(url) for url in replica_urls]
        self.replica_index = 0

    def get_read_connection(self):
        """Round-robin read replicas"""
        replica = self.replicas[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(self.replicas)
        return replica

    def get_write_connection(self):
        """Always use primary for writes"""
        if not self.primary.is_healthy():
            self.promote_replica()
        return self.primary

    def promote_replica(self):
        """Promote replica to primary on failure"""
        for replica in self.replicas:
            if replica.is_healthy():
                self.primary = replica
                self.replicas.remove(replica)
                logger.warning(f"Promoted {replica} to primary")
                return
        raise NoHealthyDatabaseError()
```

### Geographic Distribution

**When to Use Multi-Region:**

| Scenario | Multi-Region Benefit |
|----------|---------------------|
| Global users | Lower latency |
| Compliance requirements | Data residency |
| Disaster recovery | Survive region outages |
| 99.99%+ uptime SLA | Redundancy required |

**Trade-offs:**

| Benefit | Cost |
|---------|------|
| Lower latency | Higher complexity |
| Better availability | Data sync challenges |
| Disaster recovery | 2-3x infrastructure cost |
| Compliance | Operational overhead |

---

## Service Communication Patterns

### Synchronous (REST/gRPC)

**When to Use:**

```python
# Synchronous - When you need immediate response

# REST - Simple, HTTP-based
@app.post("/orders")
async def create_order(order: OrderCreate):
    # Call user service synchronously
    user = await http_client.get(f"{USER_SERVICE}/users/{order.user_id}")
    if not user:
        raise HTTPException(404, "User not found")

    # Process order
    return create_order_in_db(order, user)

# gRPC - When performance matters
async def create_order(order: OrderCreate):
    user = await user_service_stub.GetUser(GetUserRequest(user_id=order.user_id))
    return create_order_in_db(order, user)
```

**Good for:**
- User-facing APIs needing immediate response
- Simple request-response patterns
- When caller needs result to proceed

### Asynchronous (Message Queue)

**When to Use:**

```python
# Asynchronous - When you don't need immediate response

# Publish event
async def create_order(order: OrderCreate):
    db_order = await save_order(order)

    # Don't wait for these
    await message_queue.publish("order.created", {
        "order_id": db_order.id,
        "user_id": order.user_id,
        "items": order.items
    })

    return db_order  # Return immediately

# Subscribe in other services
@message_queue.subscribe("order.created")
async def handle_order_created(event):
    # Inventory service
    await reserve_inventory(event["items"])

@message_queue.subscribe("order.created")
async def send_confirmation(event):
    # Notification service
    await send_email(event["user_id"], "Order confirmed!")
```

**Good for:**
- Fire-and-forget operations
- Long-running processes
- Decoupling services
- Handling traffic spikes (queue absorbs burst)

### Event-Driven Architecture

**Event Sourcing Pattern:**

```python
# Instead of storing current state, store events
class OrderEventStore:
    def save_event(self, event: OrderEvent):
        """Append-only event log"""
        self.db.insert({
            "aggregate_id": event.order_id,
            "event_type": event.type,
            "data": event.data,
            "timestamp": datetime.utcnow()
        })

    def get_order_state(self, order_id: str) -> Order:
        """Rebuild state from events"""
        events = self.db.find({"aggregate_id": order_id}).sort("timestamp")
        order = Order()
        for event in events:
            order.apply(event)
        return order

# Events
class OrderCreated(OrderEvent): pass
class ItemAdded(OrderEvent): pass
class PaymentReceived(OrderEvent): pass
class OrderShipped(OrderEvent): pass

# Benefits:
# - Complete audit trail
# - Can replay to any point in time
# - Debug production issues
# - Build new read models from events
```

### Communication Pattern Selection

| Pattern | Latency | Coupling | Reliability | Use Case |
|---------|---------|----------|-------------|----------|
| REST/HTTP | Low | High | Medium | User-facing APIs |
| gRPC | Very Low | High | Medium | Service-to-service |
| Message Queue | High | Low | High | Background tasks |
| Event Streaming | Medium | Very Low | Very High | Real-time analytics |

---

## API Gateway Pattern

### When to Use API Gateway

**Benefits:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Clients                                   │
│     Mobile App    Web App    Third-party    Internal Tools      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │   API   │  Single entry point
                    │ Gateway │  ─────────────────
                    └────┬────┘  • Authentication
                         │       • Rate limiting
         ┌───────────────┼───────────────┐     • Request routing
         │               │               │     • Response caching
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐  • Load balancing
    │ Users   │    │ Orders  │    │ Products│  • Protocol translation
    │ Service │    │ Service │    │ Service │  • API versioning
    └─────────┘    └─────────┘    └─────────┘
```

**Implementation Example:**

```python
# Simple API Gateway with FastAPI
from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI()

# Service registry
SERVICES = {
    "users": "http://users-service:8001",
    "orders": "http://orders-service:8002",
    "products": "http://products-service:8003",
}

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("100/minute")
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(404, "Service not found")

    # Forward request to appropriate service
    service_url = f"{SERVICES[service]}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=service_url,
            headers=dict(request.headers),
            content=await request.body(),
            params=request.query_params
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
```

---

## Database Patterns

### Database Per Service

**When to Use:**

```
┌──────────────────────────────────────────────────────────────────┐
│                     Shared Database (Anti-pattern for microservices)
│                                                                   │
│   Users Service ──┐                                               │
│   Orders Service ──┼──► Single Database ◄── Tight coupling!      │
│   Products Service ─┘                                             │
└──────────────────────────────────────────────────────────────────┘

                              vs

┌──────────────────────────────────────────────────────────────────┐
│                     Database Per Service (Recommended)            │
│                                                                   │
│   Users Service ──────► Users DB (PostgreSQL)                    │
│   Orders Service ─────► Orders DB (PostgreSQL)                   │
│   Products Service ───► Products DB (MongoDB)  ← Different DB!   │
│   Analytics Service ──► Analytics DB (ClickHouse)                │
└──────────────────────────────────────────────────────────────────┘
```

**Trade-offs:**

| Benefit | Challenge |
|---------|-----------|
| Independent scaling | Cross-service queries hard |
| Technology freedom | Data consistency |
| Team autonomy | Duplication of data |
| Failure isolation | Distributed transactions |

### CQRS (Command Query Responsibility Segregation)

**When to Use:**

```python
# CQRS: Separate read and write models

# Write Model (Commands)
class OrderCommandService:
    """Handles state changes"""

    def create_order(self, command: CreateOrderCommand) -> str:
        order = Order.create(command)
        self.write_db.save(order)

        # Publish event for read model update
        self.events.publish(OrderCreated(order))
        return order.id

    def update_status(self, command: UpdateStatusCommand):
        order = self.write_db.get(command.order_id)
        order.update_status(command.status)
        self.write_db.save(order)
        self.events.publish(OrderStatusChanged(order))

# Read Model (Queries)
class OrderQueryService:
    """Optimized for reading"""

    def get_order_summary(self, order_id: str) -> OrderSummaryDTO:
        # Read from denormalized, optimized read store
        return self.read_db.get_order_summary(order_id)

    def search_orders(self, filters: OrderFilters) -> list[OrderListDTO]:
        # Complex queries on read-optimized store
        return self.read_db.search(filters)

# Event handler updates read model
@events.subscribe(OrderCreated)
def update_read_model(event: OrderCreated):
    # Denormalize data for fast reads
    summary = OrderSummaryDTO(
        id=event.order.id,
        customer_name=event.order.customer.name,  # Denormalized
        total=event.order.total,
        item_count=len(event.order.items),
        status=event.order.status
    )
    read_db.save_summary(summary)
```

**Good for:**
- Read-heavy applications (100:1 read/write)
- Complex querying requirements
- Different scaling needs for reads vs writes
- Event sourcing compatibility

---

## Summary: Decision Cheat Sheet

### Architecture Selection

| Situation | Recommendation |
|-----------|----------------|
| Starting new project | Modular Monolith |
| Team < 10 developers | Monolith |
| Clear bounded contexts + large team | Consider microservices |
| Need to scale part independently | Extract that part as service |
| Different tech requirements | Microservices for that part |

### Infrastructure Selection

| Situation | Recommendation |
|-----------|----------------|
| Development environment | Docker Compose |
| Single service, simple scaling | VM + systemd or PaaS |
| 3-5 services | Docker Compose or Docker Swarm |
| 10+ services, large team | Kubernetes (managed) |
| Need auto-scaling | Cloud provider services or K8s HPA |

### Database Selection

| Situation | Recommendation |
|-----------|----------------|
| ACID transactions needed | PostgreSQL |
| Flexible schema, documents | MongoDB |
| High write throughput | Cassandra |
| Time-series data | TimescaleDB, InfluxDB |
| Search functionality | Elasticsearch |
| Caching | Redis |
| Analytics, OLAP | ClickHouse, BigQuery |

### Communication Selection

| Situation | Recommendation |
|-----------|----------------|
| Need immediate response | REST or gRPC |
| Fire and forget | Message queue (RabbitMQ, SQS) |
| Event streaming | Kafka |
| Real-time updates | WebSockets, SSE |
| Service-to-service (internal) | gRPC |
| Public API | REST with OpenAPI |

---

**Key Principle:** Start simple, add complexity only when needed. Every architectural decision has trade-offs - choose based on your actual constraints, not theoretical best practices.
