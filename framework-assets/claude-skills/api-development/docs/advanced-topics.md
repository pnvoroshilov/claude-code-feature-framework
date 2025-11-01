# Advanced Topics - API Development

Advanced concepts and techniques for expert-level API development, including distributed systems, performance optimization, and production-grade patterns.

## Table of Contents

- [1. GraphQL N+1 Problem](#1-graphql-n1-problem)
- [2. API Rate Limiting Algorithms](#2-api-rate-limiting-algorithms)
- [3. WebSocket Real-Time APIs](#3-websocket-real-time-apis)
- [4. Server-Sent Events (SSE)](#4-server-sent-events-sse)
- [5. API Caching Strategies](#5-api-caching-strategies)
- [6. Distributed Tracing](#6-distributed-tracing)
- [7. API Throttling and Backpressure](#7-api-throttling-and-backpressure)
- [8. Multi-Tenancy Patterns](#8-multi-tenancy-patterns)
- [9. Event Sourcing](#9-event-sourcing)
- [10. CQRS Pattern](#10-cqrs-pattern)

---

## 1. GraphQL N+1 Problem

### What It Is
The N+1 problem occurs when GraphQL resolvers execute N+1 database queries for related data.

### Solution: DataLoader

```python
from strawberry.dataloader import DataLoader
from typing import List

async def load_users(keys: List[int]) -> List[User]:
    """Batch load users - one query instead of N"""
    users = await db.fetch(
        "SELECT * FROM users WHERE id = ANY($1)",
        keys
    )
    user_map = {user.id: user for user in users}
    return [user_map.get(key) for key in keys]

@strawberry.type
class Post:
    id: int
    title: str
    author_id: int

    @strawberry.field
    async def author(self, info) -> User:
        """Efficiently load author using DataLoader"""
        loader = info.context["user_loader"]
        return await loader.load(self.author_id)

# Context with DataLoader
async def get_context():
    return {
        "user_loader": DataLoader(load_fn=load_users)
    }
```

### Advanced Caching

```python
class CachedDataLoader(DataLoader):
    """DataLoader with Redis caching"""

    async def load_fn(self, keys: List[int]) -> List[Any]:
        # Check cache first
        cached = await redis.mget([f"user:{k}" for k in keys])

        # Find cache misses
        missing_keys = [
            keys[i] for i, val in enumerate(cached) if val is None
        ]

        if missing_keys:
            # Fetch from database
            users = await db.fetch_users_by_ids(missing_keys)

            # Cache results
            for user in users:
                await redis.setex(
                    f"user:{user.id}",
                    3600,
                    json.dumps(user.dict())
                )

        # Return all results
        return [
            json.loads(cached[i]) if cached[i]
            else users_map[keys[i]]
            for i in range(len(keys))
        ]
```

---

## 2. API Rate Limiting Algorithms

### Token Bucket Algorithm

```python
import time
from typing import Dict

class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens"""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill

        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

# Usage
buckets: Dict[str, TokenBucket] = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting"""
    client_id = request.headers.get("X-API-Key")

    if client_id not in buckets:
        buckets[client_id] = TokenBucket(capacity=100, refill_rate=10)

    if not buckets[client_id].consume():
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limit_exceeded"}
        )

    return await call_next(request)
```

### Sliding Window Log

```python
from collections import deque
from datetime import datetime, timedelta

class SlidingWindowLog:
    """Sliding window rate limiter"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: deque = deque()

    def allow_request(self) -> bool:
        """Check if request is allowed"""
        now = datetime.now()

        # Remove old requests
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False
```

---

## 3. WebSocket Real-Time APIs

### FastAPI WebSocket Implementation

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        dead_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process message
            if message["type"] == "chat":
                await manager.broadcast({
                    "type": "chat",
                    "user": message["user"],
                    "text": message["text"],
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### WebSocket Authentication

```python
@app.websocket("/ws")
async def authenticated_websocket(websocket: WebSocket):
    """Authenticate WebSocket connection"""
    # Get token from query params
    token = websocket.query_params.get("token")

    try:
        user = verify_token(token)
    except Exception:
        await websocket.close(code=403)
        return

    await manager.connect(websocket, user)

    try:
        while True:
            data = await websocket.receive_text()
            # Process authenticated user's messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## 4. Server-Sent Events (SSE)

### Implementation

```python
from fastapi.responses import StreamingResponse
from asyncio import sleep

async def event_stream(user_id: int):
    """Generate server-sent events"""
    while True:
        # Fetch updates for user
        updates = await get_user_updates(user_id)

        if updates:
            for update in updates:
                yield f"data: {json.dumps(update)}\n\n"

        await sleep(1)  # Poll every second

@app.get("/stream")
async def stream_updates(user: User = Depends(get_current_user)):
    """SSE endpoint"""
    return StreamingResponse(
        event_stream(user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
```

---

## 5. API Caching Strategies

### Multi-Level Caching

```python
from functools import lru_cache
import redis
import hashlib

redis_client = redis.Redis(host='localhost', port=6379)

class CacheService:
    """Multi-level cache: Memory -> Redis -> Database"""

    @lru_cache(maxsize=1000)
    def get_from_memory(self, key: str):
        """L1: Memory cache"""
        return None  # Handled by lru_cache

    async def get(self, key: str):
        """Get with fallback through cache levels"""
        # L1: Check memory cache
        try:
            result = self.get_from_memory(key)
            if result:
                return result
        except KeyError:
            pass

        # L2: Check Redis
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)

        # L3: Fetch from database
        result = await fetch_from_database(key)

        # Populate caches
        redis_client.setex(key, 3600, json.dumps(result))
        self.get_from_memory(key)  # Cache in memory

        return result

cache = CacheService()

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Endpoint with multi-level caching"""
    return await cache.get(f"product:{product_id}")
```

### Cache Invalidation

```python
@app.put("/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    """Update product and invalidate cache"""
    # Update database
    updated = await db.update_product(product_id, product)

    # Invalidate caches
    cache_key = f"product:{product_id}"
    redis_client.delete(cache_key)
    cache.get_from_memory.cache_clear()

    # Broadcast invalidation to other servers
    await pubsub.publish("cache:invalidate", cache_key)

    return updated
```

---

## 6. Distributed Tracing

### OpenTelemetry Integration

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Manual instrumentation
@app.get("/complex-operation")
async def complex_operation():
    """Traced operation with custom spans"""
    with tracer.start_as_current_span("complex-operation"):
        # Step 1
        with tracer.start_as_current_span("fetch-user-data"):
            user_data = await fetch_user_data()

        # Step 2
        with tracer.start_as_current_span("process-data"):
            processed = process_data(user_data)

        # Step 3
        with tracer.start_as_current_span("save-results"):
            await save_results(processed)

        return {"status": "completed"}
```

---

## 7. API Throttling and Backpressure

### Adaptive Throttling

```python
import asyncio
from collections import deque

class AdaptiveThrottler:
    """Throttle based on system load"""

    def __init__(self):
        self.response_times = deque(maxlen=100)
        self.semaphore = asyncio.Semaphore(100)

    async def __call__(self, func):
        """Execute with adaptive throttling"""
        # Calculate current load
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )

        # Adjust concurrency based on load
        if avg_response_time > 1.0:  # Slow responses
            # Reduce concurrency
            new_limit = max(10, int(self.semaphore._value * 0.8))
            self.semaphore = asyncio.Semaphore(new_limit)

        async with self.semaphore:
            start = time.time()
            result = await func()
            duration = time.time() - start
            self.response_times.append(duration)
            return result

throttler = AdaptiveThrottler()

@app.get("/expensive-operation")
async def expensive_operation():
    """Throttled endpoint"""
    return await throttler(fetch_expensive_data)
```

---

## 8. Multi-Tenancy Patterns

### Row-Level Security

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session

class TenantModel(Base):
    """Base model with tenant isolation"""
    __abstract__ = True

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

class Product(TenantModel):
    """Product with automatic tenant isolation"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)

# Middleware to inject tenant
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    """Extract and validate tenant"""
    tenant_id = request.headers.get("X-Tenant-ID")

    if not tenant_id:
        return JSONResponse(status_code=400, content={"error": "Missing tenant ID"})

    request.state.tenant_id = int(tenant_id)
    return await call_next(request)

# Scoped queries
def get_tenant_db(tenant_id: int = Depends(get_tenant_id)):
    """Database session scoped to tenant"""
    db = SessionLocal()
    # Set tenant filter
    db.execute(f"SET app.current_tenant = {tenant_id}")
    try:
        yield db
    finally:
        db.close()

@app.get("/products")
async def list_products(db: Session = Depends(get_tenant_db)):
    """Automatically filtered by tenant"""
    return db.query(Product).all()
```

---

## 9. Event Sourcing

### Implementation

```python
from datetime import datetime
from typing import List, Dict, Any

class Event:
    """Base event class"""
    def __init__(self, aggregate_id: str, data: Dict[str, Any]):
        self.aggregate_id = aggregate_id
        self.event_type = self.__class__.__name__
        self.data = data
        self.timestamp = datetime.now()

class OrderCreated(Event):
    pass

class OrderItemAdded(Event):
    pass

class OrderShipped(Event):
    pass

class EventStore:
    """Store and replay events"""

    def __init__(self):
        self.events: List[Event] = []

    def append(self, event: Event):
        """Append event to store"""
        self.events.append(event)
        # Persist to database
        save_event_to_db(event)

    def get_events(self, aggregate_id: str) -> List[Event]:
        """Get all events for aggregate"""
        return [e for e in self.events if e.aggregate_id == aggregate_id]

class Order:
    """Aggregate rebuilt from events"""

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.items = []
        self.status = "pending"

    def apply(self, event: Event):
        """Apply event to rebuild state"""
        if isinstance(event, OrderCreated):
            self.status = "created"
        elif isinstance(event, OrderItemAdded):
            self.items.append(event.data["item"])
        elif isinstance(event, OrderShipped):
            self.status = "shipped"

    @classmethod
    def from_events(cls, events: List[Event]):
        """Rebuild aggregate from events"""
        order = cls(events[0].aggregate_id)
        for event in events:
            order.apply(event)
        return order

# Usage
event_store = EventStore()

@app.post("/orders")
async def create_order(order_data: OrderCreate):
    """Create order using event sourcing"""
    order_id = generate_id()

    # Create events
    event_store.append(OrderCreated(order_id, order_data.dict()))

    for item in order_data.items:
        event_store.append(OrderItemAdded(order_id, {"item": item}))

    return {"order_id": order_id}

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Rebuild order from events"""
    events = event_store.get_events(order_id)
    order = Order.from_events(events)
    return order
```

---

## 10. CQRS Pattern

### Command Query Responsibility Segregation

```python
# Write model (Commands)
class CreateOrderCommand:
    def __init__(self, user_id: int, items: List[dict]):
        self.user_id = user_id
        self.items = items

class CommandHandler:
    """Handle write operations"""

    async def handle_create_order(self, command: CreateOrderCommand):
        """Process order creation"""
        order = Order(
            user_id=command.user_id,
            items=command.items
        )

        # Save to write database
        await write_db.save(order)

        # Publish event
        await event_bus.publish(OrderCreatedEvent(order))

        return order

# Read model (Queries)
class OrderSummary:
    """Optimized read model"""
    id: int
    user_name: str
    total: float
    item_count: int
    status: str

class QueryHandler:
    """Handle read operations"""

    async def get_order_summary(self, order_id: int) -> OrderSummary:
        """Query optimized read model"""
        return await read_db.query(OrderSummary).get(order_id)

# Event handler to sync read model
@event_bus.subscribe(OrderCreatedEvent)
async def update_read_model(event: OrderCreatedEvent):
    """Update read model when order created"""
    summary = OrderSummary(
        id=event.order_id,
        user_name=event.user_name,
        total=event.total,
        item_count=len(event.items),
        status="created"
    )
    await read_db.save(summary)

# API endpoints
@app.post("/orders")
async def create_order(command: CreateOrderCommand):
    """Command endpoint"""
    return await command_handler.handle_create_order(command)

@app.get("/orders/{order_id}/summary")
async def get_order_summary(order_id: int):
    """Query endpoint - uses optimized read model"""
    return await query_handler.get_order_summary(order_id)
```

---

## Summary

These advanced topics enable:

- **GraphQL DataLoader**: Solve N+1 query problems
- **Rate Limiting**: Token bucket, sliding window algorithms
- **Real-Time**: WebSockets and Server-Sent Events
- **Caching**: Multi-level caching strategies
- **Tracing**: Distributed request tracking
- **Throttling**: Adaptive backpressure handling
- **Multi-Tenancy**: Row-level security patterns
- **Event Sourcing**: Audit trail and time travel
- **CQRS**: Separate read and write models

Apply these patterns to build production-grade, scalable APIs.
