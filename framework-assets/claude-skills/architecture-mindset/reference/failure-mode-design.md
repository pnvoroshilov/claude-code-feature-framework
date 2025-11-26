# Failure Mode Design - Designing for the Unhappy Path

## The Core Principle

**The "Happy Path" is a lie. Design for the "Unhappy Path."**

Every system will fail. The question is not "if" but "when" and "how gracefully."

## Murphy's Law Assumptions

When designing any system, assume:

| Assumption | Design Implication |
|------------|-------------------|
| The network is flaky | Timeouts, retries, circuit breakers |
| The database is throttled | Connection pooling, read replicas, caching |
| The disk is full | Monitoring, log rotation, cleanup policies |
| The user is malicious | Input validation, rate limiting, auth |
| The third-party is down | Fallbacks, caching, graceful degradation |
| The deployment will fail | Blue-green, rollback procedures |
| The secret will leak | Rotation procedures, least privilege |
| The data will be corrupted | Validation, backups, reconciliation |

## Failure Categories and Mitigations

### 1. Network Failures

#### Latency Spikes

**Question**: What happens when latency spikes to 2 seconds?

**Mitigations**:
```
┌─────────────────────────────────────────────────────┐
│                    Client Request                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Timeout Configuration (e.g., 500ms connect, 2s read)│
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Circuit Breaker (open after 5 failures in 30s)     │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Fallback Response (cached data, default value)     │
└─────────────────────────────────────────────────────┘
```

**Implementation Checklist**:
- [ ] Set explicit timeouts on all HTTP clients
- [ ] Implement circuit breaker pattern
- [ ] Define fallback behavior
- [ ] Add latency metrics and alerts

#### Connection Failures

**Question**: What if the connection is refused or times out?

**Retry Strategy with Exponential Backoff and Jitter**:
```python
# Good: Exponential backoff with jitter
delay = min(base_delay * (2 ** attempt) + random_jitter, max_delay)

# Example: base=100ms, max=30s
# Attempt 1: 100-200ms
# Attempt 2: 200-400ms
# Attempt 3: 400-800ms
# Attempt 4: 800-1600ms
# ... up to 30s max
```

**Anti-Pattern: Immediate Retry**
```python
# Bad: Thundering herd problem
while not success:
    try_again()  # All clients retry simultaneously
```

### 2. Data Failures

#### Message Loss

**Question**: What if the message broker drops the packet?

**Outbox Pattern**:
```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Service A     │     │    Database      │     │  Message Broker  │
│                  │     │                  │     │                  │
│  1. Begin TX     │────▶│                  │     │                  │
│  2. Write Data   │────▶│  Data Table      │     │                  │
│  3. Write Event  │────▶│  Outbox Table    │     │                  │
│  4. Commit TX    │────▶│                  │     │                  │
│                  │     │                  │     │                  │
│  (async)         │     │                  │     │                  │
│  5. Poll Outbox  │◀────│  Outbox Table    │     │                  │
│  6. Publish      │─────│──────────────────│────▶│  Topic/Queue     │
│  7. Mark Sent    │────▶│  Outbox Table    │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**Key Properties**:
- Data and event in same transaction (atomicity)
- At-least-once delivery guaranteed
- Consumer must be idempotent

#### Data Corruption

**Question**: What if invalid state persists in the database?

**Defense in Depth**:
```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Input Validation (API boundary)            │
│   - Schema validation (JSON Schema, Pydantic)       │
│   - Business rule validation                        │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│ Layer 2: Domain Validation (service layer)          │
│   - Invariant checks                                │
│   - State transition validation                     │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│ Layer 3: Database Constraints (persistence layer)   │
│   - NOT NULL, CHECK, FOREIGN KEY                    │
│   - Unique indexes                                  │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│ Layer 4: Reconciliation Jobs (background)           │
│   - Periodic consistency checks                     │
│   - Data quality monitoring                         │
└─────────────────────────────────────────────────────┘
```

### 3. Service Failures

#### Cascading Failures

**Question**: What if one service failure brings down the whole system?

**Bulkhead Pattern**:
```
┌──────────────────────────────────────────────────────────────┐
│                        API Gateway                            │
├──────────────────┬──────────────────┬──────────────────┬─────┤
│   Thread Pool A  │   Thread Pool B  │   Thread Pool C  │ ... │
│   (Users API)    │   (Orders API)   │   (Search API)   │     │
│   Max: 50        │   Max: 100       │   Max: 25        │     │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴─────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐
    │ Users   │        │ Orders  │        │ Search  │
    │ Service │        │ Service │        │ Service │
    └─────────┘        └─────────┘        └─────────┘
```

**If Search Service is slow/down**:
- Only Thread Pool C is exhausted
- Users and Orders continue working
- Blast radius is contained

#### Circuit Breaker States

```
         ┌───────────────────────────────────────┐
         │                                       │
         ▼                                       │
    ┌─────────┐  failures > threshold  ┌─────────┐
    │ CLOSED  │ ─────────────────────▶ │  OPEN   │
    │(normal) │                        │(failing)│
    └─────────┘                        └────┬────┘
         ▲                                  │
         │                                  │ timeout
         │    success                       ▼
         │  ┌─────────────────────────┐ ┌─────────┐
         └──│      HALF-OPEN          │◀┤         │
            │(testing if recovered)   │ │         │
            └─────────────────────────┘ └─────────┘
                      │
                      │ failure
                      ▼
                 (back to OPEN)
```

### 4. Resource Exhaustion

#### Memory Exhaustion

**Question**: What if the service runs out of memory?

**Mitigations**:
- Set memory limits (container/JVM)
- Implement pagination for large datasets
- Use streaming for file processing
- Add memory alerts at 70%, 85%, 95%

#### Connection Pool Exhaustion

**Question**: What if all database connections are in use?

**Configuration Best Practices**:
```yaml
# Connection pool settings
pool:
  min_size: 5              # Minimum connections
  max_size: 20             # Maximum connections
  max_overflow: 10         # Temporary overflow
  timeout: 30              # Wait timeout for connection
  recycle: 3600            # Recycle connections hourly
  pre_ping: true           # Validate connection before use
```

**Monitoring**:
- Track active/idle connections
- Alert when pool utilization > 80%
- Log connection acquisition time

### 5. Deployment Failures

#### Failed Deployment

**Question**: What if the new version crashes in production?

**Blue-Green Deployment**:
```
                    Load Balancer
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
    ┌─────────┐                     ┌─────────┐
    │  BLUE   │ ◄── Production      │  GREEN  │ ◄── Staging
    │  v1.0   │     Traffic (100%)  │  v1.1   │     Traffic (0%)
    └─────────┘                     └─────────┘

    After testing GREEN:
         │
         ▼
    ┌─────────┐                     ┌─────────┐
    │  BLUE   │     Traffic (0%)    │  GREEN  │ ◄── Production
    │  v1.0   │ ◄── Rollback ready  │  v1.1   │     Traffic (100%)
    └─────────┘                     └─────────┘
```

**Rollback Checklist**:
- [ ] Database migrations are backward compatible
- [ ] API changes are backward compatible
- [ ] Feature flags for new functionality
- [ ] Automated rollback triggers defined
- [ ] Rollback tested in staging

## Failure Mode Analysis Template

For each component, document:

```markdown
## Component: [Name]

### Failure Modes

| Failure | Probability | Impact | Detection | Mitigation |
|---------|-------------|--------|-----------|------------|
| Network timeout | Medium | High | Latency metrics | Circuit breaker |
| OOM | Low | Critical | Memory alerts | Limits + restart |
| Data corruption | Very Low | Critical | Validation | Backups |

### Dependencies

| Dependency | Failure Behavior | Fallback |
|------------|------------------|----------|
| Database | Read from replica | Cached data |
| Redis | Continue without cache | Degraded performance |
| Auth Service | 503 to user | Maintenance page |

### Recovery Procedures

1. **Automatic Recovery**
   - Health check failure → Restart container
   - Circuit breaker open → Fallback response

2. **Manual Recovery**
   - Database corruption → PITR restore
   - Secret leak → Rotation runbook
```

## Key Metrics to Monitor

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Error rate | > 1% | Investigate logs |
| P99 latency | > 2s | Check dependencies |
| CPU usage | > 80% sustained | Scale or optimize |
| Memory usage | > 85% | Investigate leaks |
| Connection pool | > 80% utilized | Increase pool or optimize |
| Circuit breaker | Opens | Check downstream service |
| Queue depth | Growing | Scale consumers |

## The Golden Rule

**If you haven't tested the failure path, it doesn't work.**

- Chaos engineering in production (carefully)
- Game days for disaster recovery
- Regular failover testing
- Load testing to breaking point
