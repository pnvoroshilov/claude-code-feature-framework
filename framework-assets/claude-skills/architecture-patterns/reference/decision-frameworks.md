# Decision Frameworks

**Practical decision trees for common architectural and optimization choices.**

## Overview

This document provides quick decision frameworks for:
- When to apply specific patterns
- How to choose between alternatives
- What questions to ask before implementing

---

## Performance Optimization Decisions

### Should I Optimize This?

```
┌─────────────────────────────────────────────────────────────────────┐
│                  OPTIMIZATION DECISION TREE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Is there a measurable performance problem? ─── NO ──► Don't optimize
│         │                                              (premature)  │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Have you profiled to find the bottleneck? ─── NO ──► Profile first │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Is this code called frequently? ─────────── NO ──► Low priority    │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Will optimization give > 10% improvement? ─ NO ──► Not worth it    │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Optimize! (But measure the improvement)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Response Time Optimization

| Response Time | User Perception | Action Required |
|--------------|-----------------|-----------------|
| < 100ms | Instant | None |
| 100-300ms | Slight delay | Acceptable for most |
| 300-1000ms | Noticeable | Optimize if possible |
| 1-3 seconds | Slow | Add loading indicator + optimize |
| 3-10 seconds | Frustrating | Background job + notification |
| > 10 seconds | Unacceptable | Must redesign |

---

## Caching Decision Framework

### Do I Need Caching?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CACHING DECISION TREE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Is data read more than written? (Read:Write > 3:1) ─ NO ──► Skip   │
│         │                                                  cache    │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Is data expensive to compute/fetch? ─────────────── NO ──► Skip    │
│         │                                                  cache    │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Can you tolerate slightly stale data? ───────────── NO ──► Skip    │
│         │                                                  cache    │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Add caching! Choose type below...                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Cache Type Selection

| Scenario | Cache Type | TTL Suggestion |
|----------|-----------|----------------|
| Single server, hot data | In-memory (LRU) | Seconds-minutes |
| Multiple servers, shared state | Redis/Memcached | Minutes-hours |
| Static assets | CDN | Hours-days |
| Database query results | Application cache | Based on data freshness |
| Session data | Redis | Session duration |
| Computed aggregations | Pre-computed cache | Until source changes |

### Cache Invalidation Strategy

| Data Characteristic | Strategy | Example |
|--------------------|----------|---------|
| Changes predictably | Time-based (TTL) | Weather data (15 min TTL) |
| Changes on user action | Event-based | User profile (invalidate on update) |
| Must always be fresh | Write-through | Account balance |
| Can be slightly stale | TTL + background refresh | Product catalog |

---

## Pagination Decision Framework

### Which Pagination to Use?

```
┌─────────────────────────────────────────────────────────────────────┐
│                 PAGINATION SELECTION TREE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Need to jump to specific page number? ──── YES ──► Offset/Limit    │
│         │                                          (accept slowness │
│        NO                                           on large pages) │
│         │                                                           │
│         ▼                                                           │
│  Data changes frequently during browsing? ─ YES ──► Cursor-based   │
│         │                                          (avoid gaps/     │
│        NO                                           duplicates)     │
│         │                                                           │
│         ▼                                                           │
│  Dataset > 100k rows? ─────────────────────── YES ──► Keyset       │
│         │                                           (O(1) vs O(n)) │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Use Offset/Limit (simple, good enough)                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pagination Comparison

| Aspect | Offset/Limit | Cursor-based | Keyset |
|--------|--------------|--------------|--------|
| **Complexity** | Simple | Medium | Medium |
| **Performance at page 1000** | Slow (O(n)) | Fast (O(1)) | Fast (O(1)) |
| **Random page access** | Yes | No | No |
| **Handles inserts well** | No (gaps) | Yes | Yes |
| **URL bookmarkable** | Yes | No | Partial |
| **Best for** | Admin panels | Infinite scroll | Large datasets |

---

## Scaling Decision Framework

### When to Scale?

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SCALING DECISION TREE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Is resource utilization > 70%? ─────────── NO ──► Don't scale yet  │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Have you optimized the code first? ─────── NO ──► Optimize first   │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Can a bigger server solve it? ──────────── YES ─► Scale vertically │
│         │                                          (simpler)        │
│        NO (or near limit)                                           │
│         │                                                           │
│         ▼                                                           │
│  Scale horizontally (add more servers)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Vertical vs Horizontal Scaling

| Consideration | Vertical (Bigger Server) | Horizontal (More Servers) |
|---------------|-------------------------|---------------------------|
| **Complexity** | Low | High |
| **Cost at scale** | Expensive | More economical |
| **Downtime risk** | Single point of failure | Fault tolerant |
| **Limits** | Hardware ceiling | Virtually unlimited |
| **Best for** | Database, quick fix | Stateless services |

### Resource-Specific Scaling

| Resource Bottleneck | First Action | Scale Action |
|---------------------|--------------|--------------|
| **CPU** | Profile & optimize | More servers + LB |
| **Memory** | Reduce data in memory | More RAM or servers |
| **Disk I/O** | Add SSD, indexes | Sharding, read replicas |
| **Network** | Compression, caching | CDN, regional distribution |
| **Database** | Query optimization | Read replicas, sharding |

---

## Microservices Decision Framework

### Should This Be a Separate Service?

```
┌─────────────────────────────────────────────────────────────────────┐
│              MICROSERVICE EXTRACTION DECISION                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Does it have different scaling requirements? ─ NO ──► Keep together│
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Is there a clear bounded context? ──────────── NO ──► Keep together│
│         │                                             (find boundary│
│        YES                                              first)      │
│         │                                                           │
│         ▼                                                           │
│  Does a separate team own it? ───────────────── NO ──► Consider     │
│         │                                             modular      │
│        YES                                            monolith     │
│         │                                                           │
│         ▼                                                           │
│  Can you handle the operational complexity? ─── NO ──► Not ready    │
│         │                                                           │
│        YES                                                          │
│         │                                                           │
│         ▼                                                           │
│  Extract as microservice                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Service Boundary Indicators

| Good Boundary Signal | Bad Boundary Signal |
|---------------------|---------------------|
| Clear domain concept (Orders, Users) | Technical layer (Database, Cache) |
| Different data ownership | Shared database tables |
| Independent deployment need | Frequent cross-service changes |
| Different team responsible | Same developers work on both |
| Different scaling requirements | Always scale together |

---

## Database Decision Framework

### Choosing a Database

```
┌─────────────────────────────────────────────────────────────────────┐
│                 DATABASE SELECTION GUIDE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Need ACID transactions? ──────────────── YES ──► PostgreSQL/MySQL  │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Document-oriented data? ──────────────── YES ──► MongoDB          │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Time-series data? ────────────────────── YES ──► TimescaleDB/     │
│         │                                         InfluxDB          │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Full-text search priority? ───────────── YES ──► Elasticsearch    │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Key-value + caching? ─────────────────── YES ──► Redis            │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Massive write throughput? ────────────── YES ──► Cassandra/ScyllaDB│
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Just start with PostgreSQL (it handles 90% of use cases)           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Database Selection Matrix

| Use Case | Best Choice | Why |
|----------|-------------|-----|
| General purpose | PostgreSQL | ACID, JSON, full-text, reliable |
| Simple web app | SQLite/PostgreSQL | Zero config / production-ready |
| Document storage | MongoDB | Flexible schema, embedded docs |
| Caching layer | Redis | Speed, TTL, data structures |
| Full-text search | Elasticsearch | Inverted index, relevance |
| Analytics/OLAP | ClickHouse/BigQuery | Columnar, aggregations |
| Time-series | TimescaleDB | Time-based partitioning |
| Graph relationships | Neo4j | Traversals, relationships |
| Session storage | Redis | Fast, TTL built-in |

---

## API Design Decisions

### REST vs GraphQL vs gRPC

```
┌─────────────────────────────────────────────────────────────────────┐
│                    API STYLE SELECTION                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Internal service-to-service? ─────────── YES ──► gRPC             │
│         │                                         (performance,     │
│        NO                                          type safety)     │
│         │                                                           │
│         ▼                                                           │
│  Mobile app with varying data needs? ──── YES ──► GraphQL          │
│         │                                         (flexible         │
│        NO                                          queries)         │
│         │                                                           │
│         ▼                                                           │
│  Public API for third parties? ────────── YES ──► REST             │
│         │                                         (widely           │
│        NO                                          understood)      │
│         │                                                           │
│         ▼                                                           │
│  Simple CRUD operations? ──────────────── YES ──► REST             │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Complex nested data relationships? ───── YES ──► GraphQL          │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Default to REST (simple, cacheable, well-tooled)                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### API Comparison

| Aspect | REST | GraphQL | gRPC |
|--------|------|---------|------|
| **Learning curve** | Low | Medium | Medium |
| **Caching** | Easy (HTTP) | Complex | Custom |
| **Over-fetching** | Common | No | No |
| **Tooling** | Excellent | Good | Good |
| **Browser support** | Native | Via HTTP | Requires proxy |
| **Real-time** | SSE/WebSocket | Subscriptions | Streaming |
| **Best for** | Public APIs | Mobile apps | Microservices |

---

## Async Processing Decisions

### When to Use Background Jobs

```
┌─────────────────────────────────────────────────────────────────────┐
│               ASYNC PROCESSING DECISION                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Does user need to wait for result? ───── YES ──► Synchronous       │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Operation takes > 1 second? ──────────── YES ──► Background job    │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Operation can fail independently? ─────── YES ──► Background job   │
│         │                                          with retry       │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Need to rate-limit the operation? ─────── YES ──► Queue + worker   │
│         │                                                           │
│        NO                                                           │
│         │                                                           │
│         ▼                                                           │
│  Synchronous is fine                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Background Job Selection

| Task Type | Solution | Example |
|-----------|----------|---------|
| Simple, same process | FastAPI BackgroundTasks | Send email |
| Distributed, persistent | Celery + Redis/RabbitMQ | Process payment |
| Scheduled tasks | Celery Beat / cron | Daily reports |
| High throughput | Kafka + workers | Event processing |
| One-off tasks | Database queue | Migration jobs |

---

## Reliability Decisions

### Retry Strategy Selection

| Failure Type | Retry Strategy | Example |
|--------------|----------------|---------|
| Transient (network blip) | Immediate retry (1-3x) | DNS timeout |
| Rate limiting | Exponential backoff | API 429 response |
| Downstream overload | Backoff + jitter | Service busy |
| Permanent failure | No retry | 404, 401 |
| Unknown | Limited retry + alert | 500 errors |

### Circuit Breaker Thresholds

| Service Criticality | Failure Threshold | Recovery Time |
|--------------------|-------------------|---------------|
| Critical (payments) | 2-3 failures | 30 seconds |
| Important (search) | 5 failures | 60 seconds |
| Non-critical (analytics) | 10 failures | 5 minutes |

---

## Quick Reference Cards

### "When to Cache" Checklist

- [ ] Read:Write ratio > 3:1
- [ ] Data fetch takes > 50ms
- [ ] Data doesn't change every request
- [ ] Stale data is acceptable (even briefly)
- [ ] Have plan for invalidation

### "When to Scale Horizontally" Checklist

- [ ] Vertical scaling limit reached (or too expensive)
- [ ] Application is stateless (or state externalized)
- [ ] Load balancer in place
- [ ] Health checks implemented
- [ ] Deployment automation ready

### "When to Use Microservices" Checklist

- [ ] Team size > 10 developers
- [ ] Clear domain boundaries identified
- [ ] Different scaling needs per component
- [ ] Kubernetes/container expertise available
- [ ] Distributed tracing implemented
- [ ] Service mesh or API gateway ready

### "When to Add a Queue" Checklist

- [ ] Operation doesn't need immediate response
- [ ] Need to handle traffic spikes
- [ ] Want to retry failed operations
- [ ] Need to rate-limit downstream calls
- [ ] Different processing speeds (producer/consumer)

---

## Anti-Pattern Warnings

### Common Decision Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| **Resume-Driven Development** | Using tech for CV, not need | Choose boring tech that works |
| **Premature Microservices** | Complexity before scale | Start monolith, extract later |
| **Cache Everything** | Memory bloat, stale data | Cache hot paths only |
| **NoSQL Because Cool** | Lost ACID when needed | PostgreSQL handles 90% of cases |
| **Kubernetes for 2 Services** | Massive overhead | Docker Compose is fine |
| **GraphQL for Simple CRUD** | Over-engineering | REST is simpler |
| **Retry Forever** | Resource exhaustion | Max retries + circuit breaker |

### Decision Smell Indicators

| Smell | What It Indicates |
|-------|-------------------|
| "We might need this later" | YAGNI violation |
| "Industry best practice" | Cargo cult |
| "Netflix uses it" | Scale envy |
| "It's more elegant" | Over-engineering |
| "Everyone's using it" | Hype-driven |

**Good decision indicators:**
- "This solves our measured problem"
- "This is the simplest solution that works"
- "We have the expertise to operate this"
- "The trade-offs are acceptable for our case"

---

## Summary: Default Choices

When in doubt, start with these sensible defaults:

| Category | Default Choice | Upgrade When |
|----------|---------------|--------------|
| Architecture | Modular Monolith | Need independent scaling |
| Database | PostgreSQL | Specific data model needs |
| Cache | Redis | Need specialized caching |
| API Style | REST | Complex nested queries |
| Pagination | Offset/Limit | > 100k rows |
| Deployment | Docker Compose | > 5 services |
| Queue | Redis Queue | Need persistence/reliability |
| Search | PostgreSQL FTS | Need advanced relevance |

**Remember: Complexity is a cost. Only pay it when you get clear value in return.**
