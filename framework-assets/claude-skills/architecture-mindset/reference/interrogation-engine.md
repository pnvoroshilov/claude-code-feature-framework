# The Interrogation Engine - Complete Question Framework

Before proposing ANY solution, run these probes to understand the true requirements. Never skip this step.

## A. Business Interrogation

### Scale & Growth Questions

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| What is the expected RPS now? | Current load baseline | Initial infrastructure sizing |
| What is the expected RPS in 12 months? | Growth trajectory | Scalability architecture |
| What's the peak vs average load ratio? | Burst capacity needs | Auto-scaling configuration |
| Is growth linear or exponential? | Scaling strategy | Horizontal vs vertical approach |

### Budget & Cost Questions

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| What's the infrastructure budget? | TCO constraints | Managed vs self-hosted |
| What's the engineering salary budget? | Build vs buy decisions | Custom vs off-the-shelf |
| Is OpEx or CapEx preferred? | Financial model | Cloud vs on-premise |
| What's the cost of downtime per hour? | HA/DR investment justification | Redundancy level |

### Business Criticality Questions

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| What's the acceptable downtime per year? | SLA definition | HA architecture requirements |
| What's the data loss tolerance (RPO)? | Backup strategy | Replication and backup frequency |
| What's the recovery time tolerance (RTO)? | DR strategy | Failover automation level |
| Who are the stakeholders? | Decision authority | Approval and review process |

## B. Technical Interrogation

### Data Characteristics

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| Read-heavy or write-heavy? | Optimization focus | Caching vs write scaling |
| What's the data volume (GB/TB/PB)? | Storage architecture | Tiered storage, archival |
| What's the data growth rate? | Capacity planning | Scaling timeline |
| What are the access patterns? | Query optimization | Indexing, partitioning |
| Hot vs cold data ratio? | Storage tiering | Cost optimization |

### Consistency Requirements

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| Strong or eventual consistency? | CAP trade-off | Database selection |
| What operations require ACID? | Transaction boundaries | Service and DB boundaries |
| Acceptable staleness window? | Caching strategy | TTL configuration |
| Cross-service consistency needs? | Distributed transaction | Saga vs 2PC |

### Integration & API

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| What are the integration points? | Interface design | API style (REST/GraphQL/gRPC) |
| Sync or async communication? | Coupling level | Message broker needs |
| What's the API versioning strategy? | Breaking change handling | Backward compatibility |
| Rate limiting requirements? | Protection strategy | Gateway configuration |

### Security & Compliance

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| What regulations apply (GDPR, HIPAA, PCI)? | Compliance requirements | Data handling, audit logs |
| Data residency requirements? | Geographic constraints | Multi-region architecture |
| Encryption requirements (at-rest, in-transit)? | Security baseline | Key management |
| Authentication/Authorization model? | Access control | Identity provider selection |

## C. Failure Simulation (The What-If Gauntlet)

### Infrastructure Failures

| Scenario | Question to Ask | Mitigation Pattern |
|----------|-----------------|-------------------|
| Primary region offline | How do we failover? | Multi-region active-passive |
| Database failure | How do we recover? | Replica promotion, PITR |
| Network partition | How do services communicate? | Circuit breaker, local cache |
| Storage full | How do we prevent data loss? | Monitoring, auto-cleanup |

### Application Failures

| Scenario | Question to Ask | Mitigation Pattern |
|----------|-----------------|-------------------|
| Memory leak | How do we detect and recover? | Health checks, auto-restart |
| Deadlock | How do we break it? | Timeout, deadlock detection |
| Infinite loop | How do we stop it? | Resource limits, watchdog |
| Crash loop | How do we prevent cascading? | Backoff, circuit breaker |

### Data Failures

| Scenario | Question to Ask | Mitigation Pattern |
|----------|-----------------|-------------------|
| Data corruption | How do we detect? | Checksums, validation |
| Accidental deletion | How do we recover? | Soft deletes, backups |
| Schema migration failure | How do we rollback? | Reversible migrations |
| Replication lag | How do we handle stale reads? | Read-your-writes, sticky sessions |

### Integration Failures

| Scenario | Question to Ask | Mitigation Pattern |
|----------|-----------------|-------------------|
| Third-party API down | How do we degrade gracefully? | Fallback, cache |
| Message broker failure | How do we prevent data loss? | Outbox pattern, retry |
| Certificate expiration | How do we prevent outage? | Monitoring, auto-renewal |
| Rate limit exceeded | How do we throttle? | Backpressure, queue |

### Security Incidents

| Scenario | Question to Ask | Mitigation Pattern |
|----------|-----------------|-------------------|
| Credential leak | How do we rotate? | Secret management, rotation |
| DDoS attack | How do we protect? | WAF, rate limiting, CDN |
| SQL injection | How do we prevent? | Parameterized queries, WAF |
| Privilege escalation | How do we detect? | Audit logs, anomaly detection |

## D. Team & Organization Assessment

### Team Capability

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| Team size and composition? | Conway's Law | Architecture boundaries |
| DevOps expertise level? | Operational capability | Managed vs self-hosted |
| On-call rotation available? | Support capability | Monitoring and alerting |
| Training budget? | Skill acquisition | Technology selection |

### Organization Structure

| Question | Purpose | Design Impact |
|----------|---------|---------------|
| Single team or multiple? | Service boundaries | Monolith vs microservices |
| Cross-team dependencies? | Coordination overhead | API contracts |
| Release coordination? | Deployment complexity | Independent vs coordinated |
| Shared services team? | Platform availability | Build vs consume |

## Using the Interrogation Engine

### Step 1: Triage
Identify which category of questions is most relevant:
- New system → Full interrogation
- Feature addition → Technical + Failure simulation
- Performance issue → Technical + Scale questions
- Migration → All categories

### Step 2: Prioritize
Not all questions are equally important. Focus on:
1. Questions where the answer most impacts the design
2. Questions where assumptions are risky
3. Questions that reveal hidden requirements

### Step 3: Document
Record answers in a decision log:
```
## Requirements Discovery - [Date]

### Business Context
- RPS: Current 100, Expected 10K in 12 months
- Budget: $500/mo infrastructure, 2 FTE engineering
- Downtime cost: $1K/hour

### Technical Constraints
- Data: Read-heavy (10:1), 50GB current, 10% monthly growth
- Consistency: Strong for orders, eventual for analytics
- Integration: 3 third-party APIs, all REST

### Key Risks Identified
1. Single region → Add multi-AZ
2. No rate limiting → Add API gateway
3. Manual failover → Automate with health checks
```

### Step 4: Validate
Before finalizing design:
- [ ] All critical questions answered
- [ ] Assumptions documented
- [ ] Risks identified with mitigations
- [ ] Stakeholder sign-off obtained
