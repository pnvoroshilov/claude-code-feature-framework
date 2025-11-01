# Deployment Troubleshooting Guide

Common deployment issues, their causes, and step-by-step solutions. Use this guide to diagnose and fix deployment problems quickly.

## Table of Contents

- [Deployment Failures](#deployment-failures)
- [Container Startup Issues](#container-startup-issues)
- [Networking Problems](#networking-problems)
- [Database Migration Failures](#database-migration-failures)
- [SSL/TLS Certificate Issues](#ssltls-certificate-issues)
- [Resource Exhaustion](#resource-exhaustion)
- [CI/CD Pipeline Debugging](#cicd-pipeline-debugging)
- [Cloud Provider Issues](#cloud-provider-issues)
- [Monitoring Gaps](#monitoring-gaps)
- [Performance Degradation](#performance-degradation)

---

## Deployment Failures

### Issue: Deployment Stuck in Pending State

**Symptoms**:
```bash
$ kubectl get pods
NAME                    READY   STATUS    RESTARTS   AGE
myapp-6d8f9c4b5d-abc12  0/1     Pending   0          5m
```

**Common Causes**:
1. Insufficient cluster resources
2. Node selector mismatch
3. Pod security policy violation
4. Volume mount failures

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod myapp-6d8f9c4b5d-abc12

# Check node resources
kubectl top nodes

# Check available resources
kubectl describe nodes
```

**Solutions**:

**Solution 1: Insufficient Resources**
```bash
# Check current resource requests
kubectl get pod myapp-6d8f9c4b5d-abc12 -o jsonpath='{.spec.containers[*].resources}'

# Reduce resource requests
kubectl edit deployment myapp
# Update resources.requests to lower values
```

**Solution 2: Node Selector Issues**
```yaml
# Remove or update node selector
spec:
  template:
    spec:
      # nodeSelector:
      #   disktype: ssd  # Remove if no matching nodes
      containers:
      - name: myapp
        image: myapp:v1.0
```

**Solution 3: Add More Nodes**
```bash
# AWS EKS
eksctl scale nodegroup --cluster=my-cluster --nodes=5 --name=my-nodegroup

# GKE
gcloud container clusters resize my-cluster --num-nodes=5

# Kubernetes cluster autoscaler
kubectl apply -f cluster-autoscaler.yaml
```

### Issue: Rollout Stuck in Progress

**Symptoms**:
```bash
$ kubectl rollout status deployment/myapp
Waiting for deployment "myapp" rollout to finish: 2 out of 3 new replicas have been updated...
```

**Diagnosis**:
```bash
# Check deployment status
kubectl describe deployment myapp

# Check replica set
kubectl get rs

# Check pod logs
kubectl logs deployment/myapp --tail=50
```

**Common Causes**:
- Failing readiness probes
- Image pull errors
- Application startup failures

**Solution: Fix Readiness Probe**
```yaml
spec:
  containers:
  - name: myapp
    readinessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30  # Increase if app starts slowly
      periodSeconds: 10
      timeoutSeconds: 5
      successThreshold: 1
      failureThreshold: 3
```

**Emergency Rollback**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/myapp

# Rollback to specific revision
kubectl rollout history deployment/myapp
kubectl rollout undo deployment/myapp --to-revision=2
```

---

## Container Startup Issues

### Issue: CrashLoopBackOff

**Symptoms**:
```bash
$ kubectl get pods
NAME                    READY   STATUS             RESTARTS   AGE
myapp-6d8f9c4b5d-abc12  0/1     CrashLoopBackOff   5          5m
```

**Diagnosis**:
```bash
# Check logs
kubectl logs myapp-6d8f9c4b5d-abc12

# Check previous container logs
kubectl logs myapp-6d8f9c4b5d-abc12 --previous

# Describe pod
kubectl describe pod myapp-6d8f9c4b5d-abc12
```

**Common Causes**:

**Cause 1: Missing Environment Variables**
```bash
# Check environment
kubectl exec -it myapp-6d8f9c4b5d-abc12 -- env

# Fix: Add missing variables
kubectl set env deployment/myapp DATABASE_URL=postgresql://...
```

**Cause 2: Application Error on Startup**
```javascript
// Check application logs
// Common issues:
// - Database connection failure
// - Missing configuration
// - Port already in use

// Fix database connection
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL environment variable required');
  process.exit(1);  // Clear error message
}
```

**Cause 3: Insufficient Permissions**
```dockerfile
# Fix: Run as non-root with proper permissions
FROM node:18-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy files and set ownership
COPY --chown=nodejs:nodejs . .

# Switch to non-root user
USER nodejs

CMD ["node", "server.js"]
```

### Issue: ImagePullBackOff

**Symptoms**:
```bash
$ kubectl get pods
NAME                    READY   STATUS            RESTARTS   AGE
myapp-6d8f9c4b5d-abc12  0/1     ImagePullBackOff  0          2m
```

**Diagnosis**:
```bash
# Check events
kubectl describe pod myapp-6d8f9c4b5d-abc12 | grep -A 10 Events

# Output:
# Failed to pull image "myregistry.com/myapp:v1.0": rpc error: code = Unknown desc = Error response from daemon: pull access denied
```

**Solutions**:

**Solution 1: Add Registry Credentials**
```bash
# Create docker-registry secret
kubectl create secret docker-registry regcred \
  --docker-server=myregistry.com \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=myemail@example.com

# Use in deployment
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
      containers:
      - name: myapp
        image: myregistry.com/myapp:v1.0
```

**Solution 2: Fix Image Tag**
```bash
# Check available tags
docker images | grep myapp

# Update deployment with correct tag
kubectl set image deployment/myapp myapp=myregistry.com/myapp:v1.0.1
```

---

## Networking Problems

### Issue: Service Not Accessible

**Symptoms**:
- Cannot access service from outside cluster
- Internal services cannot communicate

**Diagnosis**:
```bash
# Check service
kubectl get svc myapp
kubectl describe svc myapp

# Check endpoints
kubectl get endpoints myapp

# Test from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://myapp
```

**Common Causes**:

**Cause 1: Service Selector Mismatch**
```yaml
# Service selector must match pod labels
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # Must match pod labels exactly
  ports:
  - port: 80
    targetPort: 8080
```

**Cause 2: Firewall/Security Group Rules**
```bash
# AWS Security Group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# GCP Firewall Rule
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --source-ranges 0.0.0.0/0
```

**Cause 3: Ingress Configuration**
```yaml
# Verify ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
```

### Issue: DNS Resolution Failures

**Symptoms**:
```bash
# Services cannot resolve each other
Error: getaddrinfo ENOTFOUND database-service
```

**Diagnosis**:
```bash
# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup myapp

# Check CoreDNS
kubectl get pods -n kube-system | grep coredns
kubectl logs -n kube-system -l k8s-app=kube-dns
```

**Solution: Fix CoreDNS**
```bash
# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system

# Check DNS configuration
kubectl get configmap coredns -n kube-system -o yaml
```

---

## Database Migration Failures

### Issue: Migration Timeout

**Symptoms**:
```
Migration failed: Connection timeout
Error: Lock wait timeout exceeded
```

**Diagnosis**:
```sql
-- Check running migrations
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;

-- Check locks
SELECT * FROM information_schema.innodb_locks;
SELECT * FROM pg_locks;

-- Check long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '5 minutes';
```

**Solutions**:

**Solution 1: Kill Blocking Queries**
```sql
-- PostgreSQL
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <blocking_pid>;

-- MySQL
KILL <process_id>;
```

**Solution 2: Run Migrations with Higher Timeout**
```bash
# Increase lock wait timeout
export MIGRATION_LOCK_TIMEOUT=600  # 10 minutes

# Run migrations
alembic upgrade head
```

**Solution 3: Break Large Migration into Smaller Steps**
```sql
-- Instead of:
ALTER TABLE large_table ADD COLUMN new_field TEXT;

-- Do:
-- Step 1: Add column (nullable)
ALTER TABLE large_table ADD COLUMN new_field TEXT;

-- Step 2: Backfill in batches
UPDATE large_table SET new_field = default_value
WHERE id >= :start_id AND id < :end_id;

-- Step 3: Add constraint (after all data filled)
ALTER TABLE large_table ALTER COLUMN new_field SET NOT NULL;
```

### Issue: Data Corruption During Migration

**Prevention**:
```bash
# Always backup before migration
pg_dump -U postgres myapp > backup_$(date +%Y%m%d_%H%M%S).sql

# Test migration on copy first
createdb myapp_test
psql myapp_test < backup.sql
alembic upgrade head  # Test on copy first
```

**Recovery**:
```bash
# Restore from backup
dropdb myapp
createdb myapp
psql myapp < backup_20240131_120000.sql

# Re-run migrations carefully
alembic upgrade head
```

---

## SSL/TLS Certificate Issues

### Issue: Certificate Expired

**Symptoms**:
```
ERR_CERT_DATE_INVALID
SSL certificate expired
```

**Diagnosis**:
```bash
# Check certificate expiry
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -dates

# Output:
# notBefore=Jan 15 00:00:00 2024 GMT
# notAfter=Apr 15 23:59:59 2024 GMT  ← Expired
```

**Solution: Renew Certificate**
```bash
# Let's Encrypt renewal
certbot renew

# Or force renewal
certbot renew --force-renewal

# Reload web server
systemctl reload nginx
```

**Automate Renewal**:
```bash
# Add to crontab
0 0 * * * certbot renew --quiet && systemctl reload nginx

# Or use systemd timer
cat > /etc/systemd/system/certbot-renewal.timer <<EOF
[Unit]
Description=Certbot Renewal Timer

[Timer]
OnCalendar=daily
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
EOF

systemctl enable --now certbot-renewal.timer
```

### Issue: Certificate Chain Incomplete

**Symptoms**:
```
NET::ERR_CERT_AUTHORITY_INVALID
Unable to verify the first certificate
```

**Diagnosis**:
```bash
# Check certificate chain
openssl s_client -connect example.com:443 -showcerts

# Verify chain
curl -v https://example.com
```

**Solution: Use Full Chain**
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name example.com;

    # Use fullchain, not just cert
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;  # ← Full chain
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

---

## Resource Exhaustion

### Issue: Out of Memory (OOM) Kills

**Symptoms**:
```bash
$ kubectl get pods
NAME                    READY   STATUS      RESTARTS   AGE
myapp-6d8f9c4b5d-abc12  0/1     OOMKilled   3          5m
```

**Diagnosis**:
```bash
# Check memory usage
kubectl top pod myapp-6d8f9c4b5d-abc12

# Check events
kubectl describe pod myapp-6d8f9c4b5d-abc12 | grep -i oom

# Check limits
kubectl get pod myapp-6d8f9c4b5d-abc12 -o jsonpath='{.spec.containers[*].resources}'
```

**Solutions**:

**Solution 1: Increase Memory Limits**
```yaml
spec:
  containers:
  - name: myapp
    resources:
      requests:
        memory: "256Mi"
      limits:
        memory: "512Mi"  # Increase this
```

**Solution 2: Fix Memory Leaks**
```javascript
// Identify memory leaks
const v8 = require('v8');

setInterval(() => {
  const heapStats = v8.getHeapStatistics();
  console.log('Heap used:', heapStats.used_heap_size / 1024 / 1024, 'MB');
  console.log('Heap total:', heapStats.total_heap_size / 1024 / 1024, 'MB');
}, 60000);

// Common memory leak: Event listeners
// Bad:
setInterval(() => {
  eventEmitter.on('data', processData);  // Leak: listener never removed
}, 1000);

// Good:
const listener = processData;
eventEmitter.on('data', listener);
// Remove when done:
eventEmitter.removeListener('data', listener);
```

### Issue: Disk Space Full

**Symptoms**:
```
No space left on device
ENOSPC: no space left on device
```

**Diagnosis**:
```bash
# Check disk usage
df -h

# Find large directories
du -sh /* | sort -hr | head -10

# Docker disk usage
docker system df

# Find large log files
find /var/log -type f -size +100M
```

**Solutions**:

**Solution 1: Clean Up Docker**
```bash
# Remove unused containers, images, volumes
docker system prune -a --volumes

# Remove old images
docker images | grep '<none>' | awk '{print $3}' | xargs docker rmi
```

**Solution 2: Rotate Logs**
```bash
# Configure log rotation
cat > /etc/logrotate.d/myapp <<EOF
/var/log/myapp/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 myapp myapp
    sharedscripts
    postrotate
        systemctl reload myapp
    endscript
}
EOF
```

**Solution 3: Increase Volume Size**
```bash
# AWS EBS volume resize
aws ec2 modify-volume --volume-id vol-xxxxx --size 100

# Resize filesystem
sudo resize2fs /dev/xvdf
```

---

## CI/CD Pipeline Debugging

### Issue: Pipeline Fails Intermittently

**Symptoms**:
- Tests pass locally but fail in CI
- Random failures

**Common Causes**:

**Cause 1: Race Conditions**
```javascript
// Bad: Race condition
test('creates user', async () => {
  createUser({ name: 'John' });
  const user = await getUser('John');  // Might not exist yet
  expect(user.name).toBe('John');
});

// Good: Await async operations
test('creates user', async () => {
  await createUser({ name: 'John' });
  const user = await getUser('John');
  expect(user.name).toBe('John');
});
```

**Cause 2: External Service Dependencies**
```javascript
// Bad: Depends on external API
test('fetches user data', async () => {
  const data = await fetch('https://api.example.com/user/1');
  expect(data).toBeDefined();
});

// Good: Mock external dependencies
jest.mock('node-fetch');
test('fetches user data', async () => {
  fetch.mockResolvedValue({ json: async () => ({ id: 1, name: 'John' }) });
  const data = await getUserData(1);
  expect(data.name).toBe('John');
});
```

**Cause 3: Test Pollution**
```javascript
// Bad: Tests affect each other
let sharedState = {};

test('test 1', () => {
  sharedState.value = 10;
  expect(sharedState.value).toBe(10);
});

test('test 2', () => {
  // Depends on test 1's state!
  expect(sharedState.value).toBe(10);  // Fails if run in different order
});

// Good: Clean state for each test
beforeEach(() => {
  sharedState = {};
});
```

---

## Cloud Provider Issues

### AWS Specific

**Issue: ECS Task Fails to Start**
```bash
# Check task logs
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks arn:aws:ecs:us-east-1:123456789012:task/my-cluster/abc123

# Common issues:
# - IAM role missing permissions
# - Security group blocks traffic
# - Task definition errors
```

**Solution: Fix IAM Permissions**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### GCP Specific

**Issue: GKE Nodes Not Joining Cluster**
```bash
# Check node pool status
gcloud container node-pools describe default-pool --cluster=my-cluster

# Check node logs
gcloud compute instances get-serial-port-output NODE_NAME
```

---

## Monitoring Gaps

### Issue: Missing Metrics

**Solution: Add Instrumentation**
```javascript
// Add custom metrics
const prometheus = require('prom-client');

const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_ms',
  help: 'Duration of HTTP requests in ms',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 5, 15, 50, 100, 500]
});

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    httpRequestDuration
      .labels(req.method, req.route?.path, res.statusCode)
      .observe(duration);
  });
  next();
});
```

---

## Performance Degradation

### Issue: Slow Response Times

**Diagnosis**:
```bash
# Check application metrics
curl http://localhost:8080/metrics

# Profile application
node --inspect server.js
# Open chrome://inspect

# Database query analysis
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

**Solutions**:
- Add database indexes
- Implement caching
- Optimize queries
- Add CDN for static assets
- Enable connection pooling

---

## Related Documentation

- **[Core Concepts](core-concepts.md)**: Understanding fundamentals helps prevent issues
- **[Best Practices](best-practices.md)**: Follow practices to avoid common problems
- **[Examples](../examples/)**: See working implementations

---

**Quick Tip**: When troubleshooting, always check logs first, then metrics, then configuration. Most issues are configuration or resource-related.
