# Scalability & Performance Patterns

Practical guidance on when and how to apply scalability patterns, caching strategies, pagination, and high-load optimization.

## Table of Contents

- [Decision Framework](#decision-framework)
- [Caching Strategies](#caching-strategies)
- [Pagination Patterns](#pagination-patterns)
- [High Load Patterns](#high-load-patterns)
- [High Availability Patterns](#high-availability-patterns)
- [Data Volume Patterns](#data-volume-patterns)
- [When to Use What](#when-to-use-what)

---

## Decision Framework

### Performance Problem Identification

**Step 1: Measure Before Optimizing**

```python
# Profile your application first
import cProfile
import time

# Simple timing decorator
def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__}: {duration:.4f}s")
        return result
    return wrapper

# Identify bottlenecks
@measure_time
def slow_operation():
    # Your code here
    pass
```

**Step 2: Identify the Type of Problem**

| Symptom | Likely Cause | Solution Category |
|---------|--------------|-------------------|
| Slow response time | CPU/algorithm | Caching, Algorithm optimization |
| High latency | Network/DB | Caching, Connection pooling |
| Memory issues | Large data | Pagination, Streaming |
| Timeouts | Long operations | Async, Background jobs |
| Crashes under load | Resource limits | Scaling, Rate limiting |

### When NOT to Optimize

**Premature Optimization Checklist:**

- [ ] Have you measured the actual bottleneck?
- [ ] Is the slow code actually called frequently?
- [ ] Will optimization provide noticeable improvement (>10%)?
- [ ] Is the current performance actually a problem?

**If any answer is NO - don't optimize yet!**

---

## Caching Strategies

### When to Use Caching

**Good Candidates for Caching:**

| Data Type | Cache Strategy | TTL Suggestion |
|-----------|---------------|----------------|
| Static config | Long-term cache | Hours/Days |
| User profiles | Medium cache | 5-15 minutes |
| API responses | Short cache | 30s-5min |
| Computed results | Result cache | Based on input staleness |
| Session data | Session cache | Session duration |

**Bad Candidates for Caching:**

- Frequently changing data (real-time prices)
- User-specific sensitive data
- Data requiring immediate consistency
- Large datasets that would blow cache memory

### Cache Layers

```
┌─────────────────────────────────────────────────┐
│                   Request                        │
└─────────────────────┬───────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │   L1: In-Memory Cache  │  Fastest, smallest
          │   (Application memory) │  TTL: seconds
          └───────────┬───────────┘
                      │ Miss
          ┌───────────▼───────────┐
          │   L2: Distributed Cache│  Fast, shared
          │   (Redis, Memcached)   │  TTL: minutes
          └───────────┬───────────┘
                      │ Miss
          ┌───────────▼───────────┐
          │   L3: CDN Cache        │  Edge, static
          │   (CloudFlare, AWS CF) │  TTL: hours
          └───────────┬───────────┘
                      │ Miss
          ┌───────────▼───────────┐
          │   Origin (Database)    │  Source of truth
          └───────────────────────┘
```

### In-Memory Caching (L1)

**When:** Single server, small dataset, hot data

```python
from functools import lru_cache
from cachetools import TTLCache
import time

# Simple LRU cache - good for pure functions
@lru_cache(maxsize=1000)
def expensive_computation(param):
    # Result cached forever (until eviction)
    return compute(param)

# TTL cache - good for data that expires
cache = TTLCache(maxsize=1000, ttl=300)  # 5 min TTL

def get_user_profile(user_id):
    if user_id in cache:
        return cache[user_id]

    profile = db.fetch_user(user_id)
    cache[user_id] = profile
    return profile

# Manual invalidation
def update_user_profile(user_id, data):
    db.update_user(user_id, data)
    if user_id in cache:
        del cache[user_id]  # Invalidate cache
```

### Distributed Caching (L2)

**When:** Multiple servers, shared state, larger dataset

```python
import redis
import json
from typing import Optional, Any

class RedisCache:
    def __init__(self, host='localhost', port=6379, default_ttl=300):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value with TTL"""
        self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(value)
        )

    def delete(self, key: str) -> None:
        """Invalidate cache entry"""
        self.client.delete(key)

    def delete_pattern(self, pattern: str) -> None:
        """Invalidate all keys matching pattern"""
        for key in self.client.scan_iter(pattern):
            self.client.delete(key)

# Cache-aside pattern
cache = RedisCache()

def get_product(product_id: str) -> dict:
    cache_key = f"product:{product_id}"

    # Try cache first
    product = cache.get(cache_key)
    if product:
        return product

    # Cache miss - fetch from DB
    product = db.fetch_product(product_id)
    if product:
        cache.set(cache_key, product, ttl=600)  # 10 min

    return product

def update_product(product_id: str, data: dict) -> None:
    db.update_product(product_id, data)
    cache.delete(f"product:{product_id}")  # Invalidate
```

### Cache Invalidation Strategies

**Strategy 1: Time-based (TTL)**

```python
# Simple but may serve stale data
cache.set(key, value, ttl=300)  # Expires in 5 min
```

**Strategy 2: Event-based**

```python
# Update triggers invalidation
def update_user(user_id, data):
    db.update_user(user_id, data)
    cache.delete(f"user:{user_id}")
    cache.delete(f"user_profile:{user_id}")
    # Publish event for other services
    event_bus.publish("user_updated", {"user_id": user_id})
```

**Strategy 3: Write-through**

```python
# Write to cache and DB simultaneously
def create_order(order_data):
    order = db.create_order(order_data)
    cache.set(f"order:{order.id}", order, ttl=3600)
    return order
```

**Strategy 4: Cache warming**

```python
# Pre-populate cache on startup
def warm_cache():
    popular_products = db.get_popular_products(limit=1000)
    for product in popular_products:
        cache.set(f"product:{product.id}", product)
```

### Caching Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Cache everything | Memory bloat | Cache hot data only |
| No TTL | Stale data forever | Always set TTL |
| Cache stampede | DB hammered on expiry | Staggered TTL, locks |
| Cache avalanche | Mass expiry crashes DB | Random TTL offset |
| Ignoring cold start | Slow after restart | Cache warming |

**Cache Stampede Prevention:**

```python
import threading

locks = {}

def get_with_lock(key: str, fetch_func):
    """Prevent multiple threads fetching same key"""
    value = cache.get(key)
    if value:
        return value

    # Get or create lock for this key
    if key not in locks:
        locks[key] = threading.Lock()

    with locks[key]:
        # Double-check after acquiring lock
        value = cache.get(key)
        if value:
            return value

        # Only one thread fetches
        value = fetch_func()
        cache.set(key, value)
        return value
```

---

## Pagination Patterns

### When to Use Which Pagination

| Pattern | Best For | Limitations |
|---------|----------|-------------|
| **Offset/Limit** | Simple lists, admin panels | Slow on large offsets |
| **Cursor-based** | Infinite scroll, real-time feeds | No random page access |
| **Keyset** | Large datasets, consistent ordering | Requires sortable unique key |

### Offset/Limit Pagination

**When:** Small datasets (<100k rows), need page numbers

```python
# Simple but has performance issues with large offsets
from fastapi import Query

@app.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * page_size

    # This becomes slow for large offsets!
    users = db.query(User).offset(offset).limit(page_size).all()
    total = db.query(User).count()

    return {
        "data": users,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    }
```

**Problem with Large Offsets:**

```sql
-- OFFSET 1000000 means DB must scan 1M rows first!
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 1000000;
```

### Cursor-Based Pagination

**When:** Large datasets, infinite scroll, real-time data

```python
import base64
from typing import Optional
from dataclasses import dataclass

@dataclass
class CursorPage:
    items: list
    next_cursor: Optional[str]
    has_more: bool

def encode_cursor(user_id: int, created_at: str) -> str:
    """Encode cursor from last item"""
    data = f"{user_id}:{created_at}"
    return base64.b64encode(data.encode()).decode()

def decode_cursor(cursor: str) -> tuple:
    """Decode cursor to get position"""
    data = base64.b64decode(cursor.encode()).decode()
    user_id, created_at = data.split(":")
    return int(user_id), created_at

@app.get("/feed")
async def get_feed(
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    query = db.query(Post).order_by(Post.created_at.desc(), Post.id.desc())

    if cursor:
        last_id, last_created = decode_cursor(cursor)
        # Keyset pagination - very efficient!
        query = query.filter(
            (Post.created_at < last_created) |
            ((Post.created_at == last_created) & (Post.id < last_id))
        )

    # Fetch one extra to check if there's more
    items = query.limit(limit + 1).all()
    has_more = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        next_cursor = encode_cursor(last_item.id, str(last_item.created_at))

    return CursorPage(items=items, next_cursor=next_cursor, has_more=has_more)
```

### Keyset Pagination

**When:** Sorted by non-unique field, need consistency

```python
@app.get("/products")
async def get_products(
    last_price: Optional[float] = None,
    last_id: Optional[int] = None,
    limit: int = 20
):
    query = db.query(Product).order_by(Product.price.desc(), Product.id.desc())

    if last_price is not None and last_id is not None:
        # WHERE (price < last_price) OR (price = last_price AND id < last_id)
        query = query.filter(
            (Product.price < last_price) |
            ((Product.price == last_price) & (Product.id < last_id))
        )

    products = query.limit(limit + 1).all()

    return {
        "data": products[:limit],
        "has_more": len(products) > limit,
        "next_params": {
            "last_price": products[-1].price,
            "last_id": products[-1].id
        } if len(products) > limit else None
    }
```

### Pagination Decision Matrix

```
Start
  │
  ▼
Need random page access? ─── Yes ──► Use Offset/Limit
  │                                  (accept performance hit)
  No
  │
  ▼
Data changes frequently? ─── Yes ──► Use Cursor-based
  │                                  (avoid duplicates/gaps)
  No
  │
  ▼
Dataset > 100k rows? ─────── Yes ──► Use Keyset
  │                                  (consistent performance)
  No
  │
  ▼
Use simple Offset/Limit (it's fine for small datasets)
```

---

## High Load Patterns

### Rate Limiting

**When:** Protect API from abuse, ensure fair usage

```python
import time
from collections import defaultdict

class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.tokens = defaultdict(lambda: self.rate)
        self.last_update = defaultdict(time.time)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        time_passed = now - self.last_update[client_id]

        # Refill tokens
        self.tokens[client_id] = min(
            self.rate,
            self.tokens[client_id] + time_passed * (self.rate / 60)
        )
        self.last_update[client_id] = now

        if self.tokens[client_id] >= 1:
            self.tokens[client_id] -= 1
            return True
        return False

# Middleware usage
limiter = RateLimiter(requests_per_minute=100)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    client_ip = request.client.host

    if not limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests"},
            headers={"Retry-After": "60"}
        )

    return await call_next(request)
```

### Connection Pooling

**When:** High DB connection overhead, many concurrent requests

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Without pooling: New connection per request (SLOW)
# With pooling: Reuse existing connections (FAST)

engine = create_engine(
    "postgresql://user:pass@localhost/db",
    poolclass=QueuePool,
    pool_size=20,           # Maintain 20 connections
    max_overflow=10,        # Allow 10 more under load
    pool_pre_ping=True,     # Verify connection health
    pool_recycle=3600,      # Recycle after 1 hour
)

# Redis connection pooling
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=50
)

redis_client = redis.Redis(connection_pool=pool)
```

### Load Balancing

**When:** Single server can't handle load

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │  (nginx, HAProxy)│
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
    │ Server 1 │        │ Server 2 │        │ Server 3 │
    └─────────┘        └─────────┘        └─────────┘
```

**Load Balancing Strategies:**

| Strategy | Best For | Consideration |
|----------|----------|---------------|
| Round Robin | Identical servers | Simple, even distribution |
| Least Connections | Varying request times | Better for long requests |
| IP Hash | Session affinity | Sticky sessions |
| Weighted | Different server capacities | Manual configuration |

### Async Processing

**When:** Long operations blocking responses

```python
from celery import Celery
from fastapi import BackgroundTasks

# Option 1: Background tasks (simple)
@app.post("/orders")
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    # Fast response
    db_order = db.create_order(order)

    # Process async
    background_tasks.add_task(send_confirmation_email, order.email)
    background_tasks.add_task(update_inventory, order.items)

    return {"order_id": db_order.id, "status": "processing"}

# Option 2: Celery (distributed, robust)
celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def process_large_report(report_id: str):
    """Long-running task processed by worker"""
    data = fetch_report_data(report_id)
    result = generate_report(data)
    save_report(report_id, result)
    notify_user(report_id)

@app.post("/reports")
async def create_report(report_request: ReportRequest):
    report = db.create_report(report_request)

    # Queue for background processing
    process_large_report.delay(report.id)

    return {
        "report_id": report.id,
        "status": "queued",
        "check_status_url": f"/reports/{report.id}/status"
    }
```

---

## High Availability Patterns

### Circuit Breaker

**When:** Dependent service might fail, need graceful degradation

```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None

    def call(self, func: Callable, fallback: Callable = None) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                if fallback:
                    return fallback()
                raise CircuitBreakerOpen("Circuit is open")

        try:
            result = func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            if fallback:
                return fallback()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time > self.recovery_timeout
        )

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.successes = 0

# Usage
payment_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

def process_payment(amount):
    def call_payment_api():
        return payment_service.charge(amount)

    def fallback():
        # Queue for later processing
        queue.add("pending_payment", amount)
        return {"status": "queued", "message": "Payment queued for processing"}

    return payment_breaker.call(call_payment_api, fallback)
```

### Retry with Exponential Backoff

**When:** Transient failures, network issues

```python
import time
import random
from functools import wraps

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for retry with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # Calculate delay
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    print(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s")
                    time.sleep(delay)

            raise last_exception
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, base_delay=1.0)
def call_external_api(endpoint):
    response = requests.get(endpoint, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Health Checks

**When:** Load balancer needs to know server health

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/ready")
async def readiness_check():
    """Check if service is ready to accept traffic"""
    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "external_api": check_external_api()
    }

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }

@app.get("/health/live")
async def liveness_check():
    """Check if service is alive (for k8s)"""
    return {"status": "alive"}

def check_database() -> bool:
    try:
        db.execute("SELECT 1")
        return True
    except:
        return False

def check_cache() -> bool:
    try:
        cache.ping()
        return True
    except:
        return False
```

---

## Data Volume Patterns

### Streaming Large Data

**When:** Data too large to load in memory

```python
from typing import Generator, Iterator
import csv

def stream_large_file(filepath: str) -> Generator[dict, None, None]:
    """Stream CSV file row by row"""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row  # Don't load entire file

def process_large_dataset():
    """Process without loading everything"""
    for row in stream_large_file("large_data.csv"):
        process_row(row)

# FastAPI streaming response
from fastapi.responses import StreamingResponse

@app.get("/export/users")
async def export_users():
    def generate():
        yield "id,name,email\n"

        # Stream from database in batches
        offset = 0
        batch_size = 1000

        while True:
            users = db.query(User).offset(offset).limit(batch_size).all()
            if not users:
                break

            for user in users:
                yield f"{user.id},{user.name},{user.email}\n"

            offset += batch_size

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )
```

### Batch Processing

**When:** Process large amounts of data efficiently

```python
from typing import List, TypeVar, Callable, Iterator

T = TypeVar('T')

def batch_iterator(items: Iterator[T], batch_size: int) -> Iterator[List[T]]:
    """Split iterator into batches"""
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

def bulk_insert(records: List[dict], batch_size: int = 1000):
    """Insert records in batches"""
    for batch in batch_iterator(iter(records), batch_size):
        db.bulk_insert(batch)
        db.commit()

# Example: Process 1M records
def process_large_update():
    query = db.query(User).filter(User.needs_update == True)

    # Process in batches to avoid memory issues
    batch_size = 500
    offset = 0

    while True:
        users = query.offset(offset).limit(batch_size).all()
        if not users:
            break

        for user in users:
            user.status = calculate_new_status(user)

        db.commit()
        offset += batch_size
        print(f"Processed {offset} users")
```

### Data Archiving

**When:** Table growing too large, old data rarely accessed

```python
from datetime import datetime, timedelta

def archive_old_orders():
    """Move old orders to archive table"""
    cutoff_date = datetime.now() - timedelta(days=365)

    # Move in batches
    while True:
        old_orders = db.query(Order).filter(
            Order.created_at < cutoff_date
        ).limit(1000).all()

        if not old_orders:
            break

        # Insert into archive
        for order in old_orders:
            archive_order = ArchivedOrder(
                original_id=order.id,
                data=order.to_dict(),
                archived_at=datetime.now()
            )
            db.add(archive_order)

        # Delete from main table
        order_ids = [o.id for o in old_orders]
        db.query(Order).filter(Order.id.in_(order_ids)).delete()

        db.commit()
        print(f"Archived {len(old_orders)} orders")
```

---

## When to Use What

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROBLEM IDENTIFICATION                            │
├──────────────────────┬──────────────────────────────────────────────┤
│ Response time > 500ms │ → Check: Query optimization, Caching         │
│ Memory growing        │ → Check: Streaming, Pagination, Memory leaks │
│ DB connections maxed  │ → Check: Connection pooling, Query batching  │
│ Timeouts             │ → Check: Async processing, Timeouts config   │
│ Errors under load    │ → Check: Rate limiting, Circuit breaker      │
│ Single point failure │ → Check: Replication, Load balancing         │
└──────────────────────┴──────────────────────────────────────────────┘
```

### Solution Selection Guide

| Scenario | Solution | When to Apply |
|----------|----------|---------------|
| **Same data requested often** | Caching (Redis) | Read:Write > 10:1 |
| **Large list endpoints** | Pagination | > 100 items returned |
| **Slow external API** | Circuit Breaker | External dependency |
| **DB connection overhead** | Connection Pool | > 10 concurrent users |
| **Long-running operations** | Async/Queue | Operation > 1 second |
| **Traffic spikes** | Rate Limiting | Public API |
| **Data grows unbounded** | Archiving | > 10M rows |
| **Single server limit** | Horizontal Scaling | CPU/Memory at 80%+ |
| **Network failures** | Retry + Backoff | Distributed system |
| **Need 99.9% uptime** | Health checks + LB | Production critical |

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Cache everything | Memory bloat, complexity | Cache hot paths only |
| Infinite retry | Resource exhaustion | Max retries + backoff |
| Sync external calls | Blocking, timeouts | Async + timeout |
| No connection limits | Connection exhaustion | Pool with limits |
| Fetch all, filter in app | Memory, network waste | DB-level filtering |
| Global locks | Bottleneck | Fine-grained locks |

---

## Summary

### Quick Reference

**Caching:**
- Use Redis for shared cache across servers
- Always set TTL, never cache forever
- Invalidate on write, not on read
- Warm cache for predictable hot data

**Pagination:**
- Offset/limit for small datasets with page numbers
- Cursor for infinite scroll / real-time feeds
- Keyset for large datasets with consistent ordering

**High Load:**
- Rate limit public endpoints
- Use connection pooling always
- Async for operations > 1 second
- Background jobs for non-critical work

**High Availability:**
- Circuit breaker for external dependencies
- Retry with exponential backoff
- Health checks for load balancer
- Graceful degradation with fallbacks

### Next Steps

- Profile your application to identify actual bottlenecks
- Apply solutions incrementally, measure impact
- Review [Advanced Topics](advanced-topics.md) for migration strategies
- See [Performance Refactoring](advanced-topics.md#performance-refactoring) for code-level optimization
