# Deployment Best Practices

Industry-standard practices for reliable, secure, and efficient deployments. Follow these guidelines to build production-ready deployment processes.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Zero-Downtime Deployment](#zero-downtime-deployment)
- [Database Migration Strategies](#database-migration-strategies)
- [Secret Management](#secret-management)
- [Container Optimization](#container-optimization)
- [Monitoring and Observability](#monitoring-and-observability)
- [Security Hardening](#security-hardening)
- [Backup and Recovery](#backup-and-recovery)
- [Cost Optimization](#cost-optimization)
- [Team Collaboration](#team-collaboration)

---

## Pre-Deployment Checklist

### Comprehensive Deployment Validation

Copy and complete this checklist before every production deployment:

```
Code Quality:
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code reviewed and approved
- [ ] Linting and formatting checks passed
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Performance tests passed
- [ ] Documentation updated

Configuration:
- [ ] Environment variables configured
- [ ] Secrets stored securely (not in code)
- [ ] Feature flags configured correctly
- [ ] Third-party service credentials validated
- [ ] Database connection strings verified
- [ ] API endpoints configured for environment

Infrastructure:
- [ ] Target environment accessible
- [ ] Required resources available (CPU, memory, disk)
- [ ] Network connectivity verified
- [ ] Load balancer configured
- [ ] SSL certificates valid and not expiring soon
- [ ] DNS records correct

Database:
- [ ] Migrations tested in staging
- [ ] Backup completed before deployment
- [ ] Migration rollback plan prepared
- [ ] Database performance acceptable
- [ ] Indexes optimized

Monitoring & Observability:
- [ ] Application monitoring enabled
- [ ] Error tracking configured
- [ ] Log aggregation working
- [ ] Alerts configured for critical issues
- [ ] Status page prepared

Deployment Process:
- [ ] Deployment plan documented
- [ ] Rollback procedure defined and tested
- [ ] Communication plan (who to notify, when)
- [ ] Maintenance window scheduled (if needed)
- [ ] Team members available for support

Post-Deployment:
- [ ] Health check endpoints responding
- [ ] Key user flows tested
- [ ] Metrics show normal behavior
- [ ] No increase in errors
- [ ] Performance within acceptable range
```

### Automated Pre-Deployment Validation

```bash
#!/bin/bash
# pre-deploy-check.sh

set -e

echo "Running pre-deployment checks..."

# 1. Code quality checks
echo "✓ Running tests..."
npm test || { echo "✗ Tests failed"; exit 1; }

echo "✓ Running linter..."
npm run lint || { echo "✗ Linting failed"; exit 1; }

# 2. Security scan
echo "✓ Scanning for vulnerabilities..."
npm audit --audit-level=high || { echo "✗ Security vulnerabilities found"; exit 1; }

# 3. Build verification
echo "✓ Building application..."
npm run build || { echo "✗ Build failed"; exit 1; }

# 4. Environment validation
echo "✓ Validating environment..."
required_vars=("DATABASE_URL" "API_KEY" "SECRET_KEY")
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "✗ Missing required environment variable: $var"
    exit 1
  fi
done

# 5. Database connectivity
echo "✓ Testing database connection..."
psql $DATABASE_URL -c "SELECT 1" > /dev/null || { echo "✗ Database connection failed"; exit 1; }

# 6. External service checks
echo "✓ Checking external services..."
curl -f https://api.external-service.com/health > /dev/null || { echo "✗ External service unavailable"; exit 1; }

echo "✅ All pre-deployment checks passed!"
echo "Ready to deploy to production."
```

---

## Zero-Downtime Deployment

### Why Zero-Downtime Matters

**Business Impact**:
- No revenue loss during deployment
- Better user experience
- Deploy more frequently with confidence
- Competitive advantage

### Strategy 1: Blue-Green Deployment

**Concept**: Maintain two identical environments (Blue and Green). Deploy to inactive, switch traffic when ready.

```
Current State:
  Users → Blue (v1.0 - Live)
          Green (idle)

Deploy v2.0:
  Users → Blue (v1.0 - Live)
          Green (v2.0 - Deploy here, test)

Switch Traffic:
  Users → Green (v2.0 - Now live)
          Blue (v1.0 - Keep for rollback)

After Verification:
  Users → Green (v2.0 - Live)
          Blue (idle - Ready for next deployment)
```

**Implementation with AWS ALB**:

```bash
#!/bin/bash
# blue-green-deploy.sh

# 1. Deploy new version to green environment
echo "Deploying v2.0 to green environment..."
docker-compose -f docker-compose.green.yml up -d

# 2. Wait for green to be healthy
echo "Waiting for green environment to be ready..."
until $(curl --output /dev/null --silent --head --fail http://green.internal/health); do
    sleep 5
done

# 3. Run smoke tests on green
echo "Running smoke tests..."
./smoke-tests.sh http://green.internal || { echo "Smoke tests failed"; exit 1; }

# 4. Switch traffic from blue to green (ALB)
echo "Switching traffic to green..."
aws elbv2 modify-rule \
  --rule-arn $RULE_ARN \
  --actions Type=forward,TargetGroupArn=$GREEN_TARGET_GROUP_ARN

# 5. Monitor for issues
echo "Monitoring green environment..."
sleep 60

# 6. Check for errors
ERROR_COUNT=$(curl -s http://green.internal/metrics | grep error_count | awk '{print $2}')
if [ "$ERROR_COUNT" -gt 10 ]; then
  echo "Error rate too high, rolling back..."
  aws elbv2 modify-rule \
    --rule-arn $RULE_ARN \
    --actions Type=forward,TargetGroupArn=$BLUE_TARGET_GROUP_ARN
  exit 1
fi

echo "✅ Deployment successful! Green is now live."
echo "Blue environment kept for rollback if needed."
```

### Strategy 2: Rolling Deployment

**Concept**: Gradually replace old instances with new ones, maintaining service availability.

```
Step 1: [Old] [Old] [Old] [Old] [Old]  ← Start with 5 old instances
        Deploy new to 20%

Step 2: [New] [Old] [Old] [Old] [Old]  ← 1 new, 4 old
        Monitor, if healthy continue

Step 3: [New] [New] [Old] [Old] [Old]  ← 2 new, 3 old
        Monitor, if healthy continue

Step 4: [New] [New] [New] [Old] [Old]  ← 3 new, 2 old
        Monitor, if healthy continue

Step 5: [New] [New] [New] [New] [Old]  ← 4 new, 1 old
        Monitor, if healthy continue

Step 6: [New] [New] [New] [New] [New]  ← Complete!
```

**Kubernetes Rolling Update**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max 1 extra pod during update
      maxUnavailable: 0  # Always maintain full capacity
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
```

**Deploy and Monitor**:

```bash
# Deploy new version
kubectl set image deployment/myapp myapp=myapp:v2.0

# Watch rollout progress
kubectl rollout status deployment/myapp

# If issues occur, rollback
kubectl rollout undo deployment/myapp
```

### Strategy 3: Canary Deployment

**Concept**: Route small percentage of traffic to new version, gradually increase if stable.

```
Phase 1: 95% → Old (v1.0)    Test with 5% of users
          5% → New (v2.0)

Phase 2: 90% → Old (v1.0)    If metrics good, increase to 10%
         10% → New (v2.0)

Phase 3: 75% → Old (v1.0)    Continue increasing
         25% → New (v2.0)

Phase 4: 50% → Old (v1.0)    Split traffic
         50% → New (v2.0)

Phase 5:  0% → Old (v1.0)    Complete migration
        100% → New (v2.0)
```

**Nginx Canary Configuration**:

```nginx
# Split traffic: 95% to old, 5% to new
upstream old_version {
    server 10.0.1.10:8080 weight=95;
}

upstream new_version {
    server 10.0.1.20:8080 weight=5;
}

server {
    listen 80;
    server_name example.com;

    location / {
        # Random distribution
        split_clients "${remote_addr}${http_user_agent}" $backend {
            95%     old_version;
            *       new_version;
        }

        proxy_pass http://$backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Gradual Rollout Script**:

```bash
#!/bin/bash
# canary-deploy.sh

deploy_canary() {
  local percentage=$1

  echo "Deploying to $percentage% of traffic..."

  # Update traffic split
  kubectl patch service myapp-service -p "{
    \"spec\": {
      \"selector\": {
        \"version\": \"canary\"
      }
    }
  }"

  # Scale canary deployment
  CANARY_REPLICAS=$((10 * $percentage / 100))
  kubectl scale deployment myapp-canary --replicas=$CANARY_REPLICAS

  # Wait and monitor
  sleep 300  # 5 minutes

  # Check error rate
  ERROR_RATE=$(curl -s http://prometheus/api/v1/query?query=error_rate | jq '.data.result[0].value[1]')

  if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
    echo "Error rate too high ($ERROR_RATE), rolling back..."
    kubectl scale deployment myapp-canary --replicas=0
    exit 1
  fi

  echo "✅ $percentage% rollout successful"
}

# Gradual rollout
deploy_canary 5
deploy_canary 10
deploy_canary 25
deploy_canary 50
deploy_canary 100

echo "✅ Canary deployment complete!"
```

---

## Database Migration Strategies

### Principle: Never Break Compatibility

**Bad: Breaking Change**:
```sql
-- This breaks running v1.0 application
ALTER TABLE users DROP COLUMN old_field;
```

**Good: Backward Compatible**:
```sql
-- Step 1: Add new field (v1.1 deployment)
ALTER TABLE users ADD COLUMN new_field VARCHAR(255);

-- Step 2: Migrate data in background
UPDATE users SET new_field = old_field WHERE new_field IS NULL;

-- Step 3: Deploy v1.2 that uses new_field only

-- Step 4: Remove old_field in v1.3
ALTER TABLE users DROP COLUMN old_field;
```

### Migration Best Practices

**1. Separate Migration from Deployment**:

```bash
# Bad: Migrations run during app startup (blocks deployment)
npm start  # Runs migrations, then starts app

# Good: Run migrations first, then deploy
./run-migrations.sh  # Completes migrations
kubectl rollout restart deployment/myapp  # Deploy new code
```

**2. Test Migrations in Staging**:

```bash
#!/bin/bash
# test-migrations.sh

# 1. Create copy of production database
pg_dump production_db > production_backup.sql
createdb staging_db
psql staging_db < production_backup.sql

# 2. Run migrations on copy
export DATABASE_URL=postgresql://localhost/staging_db
alembic upgrade head

# 3. Verify data integrity
./verify-data.sh

# 4. Test application against migrated database
npm test

echo "✅ Migrations tested successfully"
```

**3. Always Create Rollback Migrations**:

```python
# migrations/002_add_email_field.py

def upgrade():
    # Forward migration
    op.add_column('users', sa.Column('email', sa.String(255)))

def downgrade():
    # Rollback migration
    op.drop_column('users', 'email')
```

**4. Use Locking Carefully**:

```sql
-- Bad: Long-running migration with table lock
ALTER TABLE large_table ADD COLUMN new_field TEXT;
-- Blocks reads/writes for minutes!

-- Good: Non-blocking index creation
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
-- Allows concurrent reads/writes
```

### Multi-Phase Migration Pattern

**Phase 1: Add New Schema (Compatible with Old Code)**:
```sql
-- Add new column, nullable
ALTER TABLE orders ADD COLUMN status_v2 VARCHAR(50);
```

**Phase 2: Dual-Write (Application Writes to Both)**:
```python
# Application code v1.1
def create_order(order_data):
    order = Order(
        status=order_data['status'],      # Old field
        status_v2=order_data['status']    # New field (dual write)
    )
    db.session.add(order)
    db.session.commit()
```

**Phase 3: Backfill Data**:
```sql
-- Run in background, batched
UPDATE orders
SET status_v2 = status
WHERE status_v2 IS NULL
LIMIT 1000;
-- Repeat until all rows migrated
```

**Phase 4: Switch to New Field (Application Reads from New)**:
```python
# Application code v1.2
def get_order_status(order):
    return order.status_v2  # Read from new field
```

**Phase 5: Remove Old Field**:
```sql
-- After v1.2 fully deployed
ALTER TABLE orders DROP COLUMN status;
ALTER TABLE orders RENAME COLUMN status_v2 TO status;
```

---

## Secret Management

### Principle: Secrets Never in Code

**Bad Examples**:
```javascript
// ❌ Hardcoded in source
const API_KEY = "sk_live_abc123xyz";

// ❌ Committed to git
const config = {
  dbPassword: "MyP@ssw0rd"
};

// ❌ In Dockerfile
ENV DATABASE_PASSWORD=secret123
```

**Good Examples**:
```javascript
// ✅ Environment variables
const API_KEY = process.env.API_KEY;

// ✅ Secret manager
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();
const apiKey = await secretsManager.getSecretValue({
  SecretId: 'myapp/api-key'
}).promise();
```

### Secret Storage Solutions

**1. Environment Variables (Development)**:
```bash
# .env (never commit to git!)
DATABASE_URL=postgresql://localhost:5432/dev
API_KEY=sk_test_123
SECRET_KEY=dev-secret-key

# Add to .gitignore
echo ".env" >> .gitignore
```

**2. AWS Secrets Manager (Production)**:
```bash
# Store secret
aws secretsmanager create-secret \
  --name myapp/prod/database-url \
  --description "Production database connection string" \
  --secret-string "postgresql://prod.db.com:5432/myapp"

# Retrieve in application
aws secretsmanager get-secret-value \
  --secret-id myapp/prod/database-url \
  --query SecretString \
  --output text
```

**Application Integration**:
```javascript
// secrets.js
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({
  region: process.env.AWS_REGION
});

async function getSecret(secretName) {
  try {
    const data = await secretsManager.getSecretValue({
      SecretId: secretName
    }).promise();
    return JSON.parse(data.SecretString);
  } catch (error) {
    console.error(`Error retrieving secret ${secretName}:`, error);
    throw error;
  }
}

// Usage
const dbCredentials = await getSecret('myapp/prod/database');
const dbUrl = `postgresql://${dbCredentials.username}:${dbCredentials.password}@${dbCredentials.host}:${dbCredentials.port}/${dbCredentials.database}`;
```

**3. HashiCorp Vault**:
```bash
# Store secret
vault kv put secret/myapp/database \
  username=dbuser \
  password=dbpass \
  host=db.example.com

# Retrieve secret
vault kv get -format=json secret/myapp/database | jq -r .data.data
```

**4. Kubernetes Secrets**:
```yaml
# Create secret
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
stringData:
  database-url: postgresql://user:pass@host:5432/db
  api-key: sk_live_abc123

---
# Use in deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: database-url
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: api-key
```

### Secret Rotation

**Automated Secret Rotation**:
```python
# rotate-secrets.py
import boto3
import random
import string

def generate_password(length=32):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def rotate_database_password():
    # 1. Generate new password
    new_password = generate_password()

    # 2. Update database user password
    db = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = db.cursor()
    cursor.execute(f"ALTER USER myapp WITH PASSWORD '{new_password}'")
    db.commit()

    # 3. Update secret in AWS Secrets Manager
    secretsmanager = boto3.client('secretsmanager')
    secretsmanager.update_secret(
        SecretId='myapp/prod/database-password',
        SecretString=new_password
    )

    # 4. Restart application to pick up new secret
    ecs = boto3.client('ecs')
    ecs.update_service(
        cluster='production',
        service='myapp',
        forceNewDeployment=True
    )

    print(f"✅ Database password rotated successfully")

# Run monthly via cron or Lambda
if __name__ == '__main__':
    rotate_database_password()
```

---

## Container Optimization

### Principle: Smaller is Better

**Why Optimize Containers**:
- Faster builds and deployments
- Reduced storage costs
- Smaller attack surface
- Faster startup times
- Lower network transfer costs

### Multi-Stage Builds

**Bad: Everything in One Stage**:
```dockerfile
FROM node:18
WORKDIR /app

# Install everything
COPY package*.json ./
RUN npm install  # Installs dev dependencies too

# Build
COPY . .
RUN npm run build

# Runtime includes unnecessary build tools
CMD ["node", "dist/server.js"]

# Result: 1.2GB image with dev dependencies
```

**Good: Multi-Stage Build**:
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci  # Clean install

# Build application
COPY . .
RUN npm run build
RUN npm prune --production  # Remove dev dependencies

# Stage 2: Runtime
FROM node:18-alpine
WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Security: Non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 8080
CMD ["node", "dist/server.js"]

# Result: 150MB image with only production dependencies
```

### Layer Optimization

**Bad: Poor Layer Caching**:
```dockerfile
FROM node:18-alpine
WORKDIR /app

# Everything in one layer
COPY . .
RUN npm install && npm run build

# Cache invalidated on any file change
```

**Good: Optimized Layer Caching**:
```dockerfile
FROM node:18-alpine
WORKDIR /app

# Layer 1: Dependencies (cached unless package.json changes)
COPY package*.json ./
RUN npm ci --only=production

# Layer 2: Source code (cached unless source changes)
COPY src ./src

# Layer 3: Build (cached unless source or deps change)
RUN npm run build

CMD ["node", "dist/server.js"]
```

### .dockerignore

```
# .dockerignore - Exclude unnecessary files

# Dependencies (install from package.json)
node_modules/
npm-debug.log

# Development files
.git/
.gitignore
.env
.env.*
*.md
README.md

# Test files
test/
coverage/
.nyc_output/
jest.config.js

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Build artifacts (rebuild in container)
dist/
build/
*.log

# OS files
.DS_Store
Thumbs.db
```

### Security Best Practices

**1. Use Specific Base Image Versions**:
```dockerfile
# Bad: Latest tag (unpredictable)
FROM node:latest

# Good: Specific version
FROM node:18.17.0-alpine
```

**2. Run as Non-Root User**:
```dockerfile
# Create user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser
```

**3. Scan for Vulnerabilities**:
```bash
# Scan with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image myapp:latest

# Scan with Snyk
snyk container test myapp:latest

# Fail build on critical vulnerabilities
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

---

## Monitoring and Observability

### Three Pillars of Observability

**1. Metrics**: Numerical measurements over time
**2. Logs**: Event records with context
**3. Traces**: Request flows through distributed systems

### Essential Metrics to Monitor

```yaml
Application Metrics:
  - Request rate (requests per second)
  - Error rate (percentage of failed requests)
  - Response time (p50, p95, p99 percentiles)
  - Active connections/users

System Metrics:
  - CPU utilization (percentage)
  - Memory usage (percentage and absolute)
  - Disk I/O (read/write operations)
  - Network traffic (in/out bandwidth)

Database Metrics:
  - Query performance (slow queries)
  - Connection pool usage
  - Lock contention
  - Replication lag

Business Metrics:
  - User signups/registrations
  - Transaction volume
  - Revenue (if applicable)
  - Feature usage
```

### Implementing Prometheus Monitoring

**1. Instrument Application**:
```javascript
// metrics.js
const promClient = require('prom-client');

// Create metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// Middleware to track metrics
function metricsMiddleware(req, res, next) {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;

    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);

    httpRequestTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .inc();
  });

  next();
}

// Expose metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.end(await promClient.register.metrics());
});
```

**2. Prometheus Configuration**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['myapp:8080']
    metrics_path: '/metrics'

# Alert rules
rule_files:
  - 'alerts.yml'
```

**3. Alert Rules**:
```yaml
# alerts.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} (>5%) for 5 minutes"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time (p95 > 1s)"
          description: "95th percentile response time is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="myapp"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "myapp has been down for more than 1 minute"
```

### Structured Logging

**Bad: Unstructured Logs**:
```javascript
console.log("User logged in: " + username);
console.log("Failed to connect to database");
```

**Good: Structured JSON Logs**:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' })
  ]
});

// Structured logging
logger.info('User logged in', {
  userId: user.id,
  username: user.username,
  ipAddress: req.ip,
  timestamp: new Date().toISOString()
});

logger.error('Database connection failed', {
  error: error.message,
  stack: error.stack,
  connectionString: dbConfig.host,  // Don't log passwords!
  attemptNumber: retryCount
});
```

---

## Security Hardening

### Security Checklist

```
Infrastructure Security:
- [ ] All traffic uses HTTPS/TLS
- [ ] Firewall configured (only necessary ports open)
- [ ] SSH access restricted to specific IPs
- [ ] Root login disabled
- [ ] Fail2ban configured for brute force protection
- [ ] Security groups/network ACLs properly configured

Application Security:
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (output encoding)
- [ ] CSRF protection enabled
- [ ] Rate limiting implemented

Authentication & Authorization:
- [ ] Strong password requirements
- [ ] Multi-factor authentication available
- [ ] Session management secure (httpOnly, secure cookies)
- [ ] JWT tokens properly validated
- [ ] Principle of least privilege applied
- [ ] Regular access audits performed

Data Protection:
- [ ] Sensitive data encrypted at rest
- [ ] All communication encrypted in transit
- [ ] Database credentials rotated regularly
- [ ] API keys stored in secret manager
- [ ] Backups encrypted
- [ ] PII data properly handled

Dependency Security:
- [ ] Dependencies regularly updated
- [ ] Security advisories monitored
- [ ] Vulnerability scanning automated
- [ ] Supply chain security considered
- [ ] License compliance verified

Monitoring & Incident Response:
- [ ] Security logs aggregated and monitored
- [ ] Intrusion detection system configured
- [ ] Incident response plan documented
- [ ] Security team contacts defined
- [ ] Regular security drills conducted
```

### Implementing Security Headers

```nginx
# nginx security headers
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Remove server header
    server_tokens off;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Backup and Recovery

### Backup Strategy: 3-2-1 Rule

- **3** copies of data
- **2** different storage types
- **1** copy offsite

**Example Implementation**:
```
Primary: Production database (AWS RDS)
Copy 1: Automated daily snapshot (same region, S3)
Copy 2: Cross-region replication (different AWS region)
```

### Automated Backup Script

```bash
#!/bin/bash
# automated-backup.sh

set -e

# Configuration
DB_HOST="localhost"
DB_NAME="myapp"
DB_USER="postgres"
BACKUP_DIR="/backups"
S3_BUCKET="s3://myapp-backups"
RETENTION_DAYS=30

# Create backup
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"

echo "Creating backup: $BACKUP_FILE"
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(stat -f%z "$BACKUP_FILE")
    echo "✅ Backup created successfully ($SIZE bytes)"
else
    echo "✗ Backup failed"
    exit 1
fi

# Upload to S3
echo "Uploading to S3..."
aws s3 cp $BACKUP_FILE $S3_BUCKET/daily/

# Cleanup old local backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Verify S3 backup
if aws s3 ls $S3_BUCKET/daily/backup_$DATE.sql.gz > /dev/null 2>&1; then
    echo "✅ Backup uploaded to S3 successfully"
else
    echo "✗ S3 upload failed"
    exit 1
fi

echo "✅ Backup completed successfully"
```

### Backup Testing

**Regularly test your backups**:

```bash
#!/bin/bash
# test-restore.sh

set -e

# Get latest backup
LATEST_BACKUP=$(aws s3 ls s3://myapp-backups/daily/ | sort | tail -n 1 | awk '{print $4}')

echo "Testing restore of backup: $LATEST_BACKUP"

# Download backup
aws s3 cp s3://myapp-backups/daily/$LATEST_BACKUP /tmp/test_backup.sql.gz

# Create test database
createdb test_restore

# Restore backup
gunzip -c /tmp/test_backup.sql.gz | psql test_restore

# Verify data integrity
RECORD_COUNT=$(psql test_restore -t -c "SELECT COUNT(*) FROM users")
echo "Restored $RECORD_COUNT user records"

# Cleanup
dropdb test_restore
rm /tmp/test_backup.sql.gz

echo "✅ Backup restore test successful"
```

---

## Cost Optimization

### Right-Sizing Resources

**Monitor and Adjust**:
```bash
# Check actual resource usage
kubectl top pods -n production

# Output:
# NAME                     CPU    MEMORY
# myapp-6d8f9c4b5d-abc12   50m    128Mi   ← Using 50% of 100m, 50% of 256Mi

# Current resource limits
resources:
  requests:
    cpu: 100m      # Requesting 100 millicores
    memory: 256Mi  # Requesting 256 MB
  limits:
    cpu: 200m      # Max 200 millicores
    memory: 512Mi  # Max 512 MB

# Optimized (right-sized)
resources:
  requests:
    cpu: 75m       # Adjusted down
    memory: 192Mi  # Adjusted down
  limits:
    cpu: 150m
    memory: 384Mi
```

### Auto-Scaling

**Horizontal Pod Autoscaler**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2      # Always at least 2 for availability
  maxReplicas: 10     # Cap at 10 to control costs
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale up at 70% CPU
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 50  # Scale down max 50% at a time
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
      - type: Percent
        value: 100  # Can double replicas
        periodSeconds: 15
```

### Cost-Saving Strategies

**1. Use Spot/Preemptible Instances for Non-Critical Workloads**:
```hcl
# Terraform: AWS Spot Instances
resource "aws_autoscaling_group" "workers" {
  name = "worker-asg"

  mixed_instances_policy {
    instances_distribution {
      on_demand_percentage_above_base_capacity = 20  # 20% on-demand
      spot_allocation_strategy = "lowest-price"
      spot_instance_pools = 4
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.worker.id
        version = "$Latest"
      }

      override {
        instance_type = "t3.medium"
      }
      override {
        instance_type = "t3a.medium"  # AMD variant (cheaper)
      }
    }
  }

  min_size = 2
  max_size = 10
}
```

**2. Storage Lifecycle Policies**:
```hcl
# Archive old data to cheaper storage
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id = "archive-old-logs"
    status = "Enabled"

    transition {
      days = 30
      storage_class = "STANDARD_IA"  # Infrequent Access (cheaper)
    }

    transition {
      days = 90
      storage_class = "GLACIER"  # Long-term archive (cheapest)
    }

    expiration {
      days = 365  # Delete after 1 year
    }
  }
}
```

---

## Team Collaboration

### Deployment Roles and Responsibilities

**Developer**:
- Create deployment configurations
- Test in staging environment
- Document deployment requirements
- Participate in deployment reviews

**DevOps Engineer**:
- Maintain infrastructure
- Implement CI/CD pipelines
- Monitor deployment health
- Optimize deployment processes

**SRE (Site Reliability Engineer)**:
- Define SLOs and SLIs
- Implement monitoring and alerting
- Conduct incident response
- Perform capacity planning

**QA Engineer**:
- Verify deployments in staging
- Run smoke tests after production deployment
- Report and track deployment issues

### Communication Best Practices

**1. Deployment Announcements**:
```markdown
# Slack/Teams message template

🚀 **Production Deployment - myapp v2.1.0**

📅 **When**: Today at 2:00 PM EST
⏱️ **Duration**: ~15 minutes
👤 **Deployer**: @jane.doe
📝 **Changes**:
  - New user dashboard
  - Performance improvements
  - Bug fixes

🔗 **Details**: https://github.com/myorg/myapp/releases/v2.1.0
📊 **Monitoring**: https://grafana.example.com/d/myapp

⚠️ **Expected Impact**: None (zero-downtime deployment)
🔄 **Rollback Plan**: Automated rollback on error rate > 1%

Will provide status updates here.
```

**2. Post-Deployment Report**:
```markdown
✅ **Deployment Complete - myapp v2.1.0**

⏰ **Deployed at**: 2:05 PM EST
⏱️ **Duration**: 12 minutes

📊 **Status**:
  - Deployment: ✅ Successful
  - Health checks: ✅ Passing
  - Error rate: ✅ Normal (0.1%)
  - Response time: ✅ Normal (p95: 180ms)
  - Database: ✅ No issues

🧪 **Smoke Tests**: All passed

📈 **Next Steps**:
  - Monitor for 1 hour
  - Review metrics tomorrow
  - Close deployment ticket

👍 No issues detected. Deployment successful!
```

### Documentation Standards

**1. Deployment Runbook**:
```markdown
# Deployment Runbook - myapp

## Prerequisites
- [ ] All tests passing on main branch
- [ ] Staging deployment successful
- [ ] Database migrations tested
- [ ] Feature flags configured

## Deployment Steps

### 1. Pre-Deployment
```bash
# Check current production version
kubectl get deployment myapp -o jsonpath='{.spec.template.spec.containers[0].image}'

# Verify staging
curl https://staging.example.com/health
```

### 2. Database Migration
```bash
# Connect to production database
kubectl run -it --rm psql --image=postgres:15 --restart=Never -- \
  psql postgresql://prod.db.example.com:5432/myapp

# Run migrations
./run-migrations.sh production
```

### 3. Deploy Application
```bash
# Deploy new version
kubectl set image deployment/myapp myapp=myapp:v2.1.0

# Watch rollout
kubectl rollout status deployment/myapp
```

### 4. Verification
```bash
# Health check
curl https://api.example.com/health

# Smoke tests
./smoke-tests.sh production
```

### 5. Rollback (if needed)
```bash
# Rollback to previous version
kubectl rollout undo deployment/myapp

# Verify rollback
kubectl rollout status deployment/myapp
```

## Contacts
- **On-Call Engineer**: Check PagerDuty
- **Database Admin**: @db-team
- **Security Team**: @security-team
```

---

## Related Documentation

- **[Core Concepts](core-concepts.md)**: Understand fundamental concepts
- **[Patterns](patterns.md)**: Common deployment patterns
- **[Troubleshooting](troubleshooting.md)**: Fix deployment issues
- **[Examples](../examples/)**: See best practices in action

---

**Next**: Explore [Common Deployment Patterns](patterns.md) or see [Practical Examples](../examples/basic/).
