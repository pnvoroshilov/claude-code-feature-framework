# Deployment Patterns

Common deployment patterns and strategies for different scenarios. Learn when to use each pattern and how to implement them effectively.

## Table of Contents

- [Blue-Green Deployment](#blue-green-deployment)
- [Canary Release](#canary-release)
- [Rolling Update](#rolling-update)
- [Feature Flag Deployment](#feature-flag-deployment)
- [AB Testing Infrastructure](#ab-testing-infrastructure)
- [Multi-Region Deployment](#multi-region-deployment)
- [Microservices Deployment](#microservices-deployment)
- [Serverless Deployment](#serverless-deployment)
- [Hybrid Cloud](#hybrid-cloud)
- [Edge Computing Deployment](#edge-computing-deployment)

---

## Blue-Green Deployment

### Pattern Overview

**Concept**: Maintain two identical production environments. Deploy to inactive environment, test, then switch traffic.

**Benefits**:
- Instant rollback (switch back to previous environment)
- Zero downtime
- Complete testing before switching
- Clean separation of versions

**Drawbacks**:
- Requires 2x infrastructure (expensive)
- Database migrations tricky (both environments need compatibility)
- Stateful applications need special handling

### When to Use

✅ **Use Blue-Green When**:
- You need instant rollback capability
- You can afford duplicate infrastructure
- You want zero-downtime deployments
- You need to test in production environment before going live

❌ **Avoid Blue-Green When**:
- Cost is a major concern (2x infrastructure)
- You have complex stateful systems
- Database schema changes frequently
- Deployment frequency is very high (overhead of maintaining two environments)

### Implementation: AWS with ALB

```bash
#!/bin/bash
# blue-green-aws.sh

set -e

ENVIRONMENT=$1  # "blue" or "green"
VERSION=$2

if [ "$ENVIRONMENT" != "blue" ] && [ "$ENVIRONMENT" != "green" ]; then
    echo "Usage: $0 <blue|green> <version>"
    exit 1
fi

# Get current live environment
CURRENT_TARGET=$(aws elbv2 describe-rules \
    --rule-arns $PRODUCTION_RULE_ARN \
    --query 'Rules[0].Actions[0].TargetGroupArn' \
    --output text)

if [[ "$CURRENT_TARGET" == *"blue"* ]]; then
    LIVE="blue"
    INACTIVE="green"
else
    LIVE="green"
    INACTIVE="blue"
fi

echo "Current live: $LIVE"
echo "Deploying to: $INACTIVE"

# 1. Deploy to inactive environment
echo "Step 1: Deploying version $VERSION to $INACTIVE environment..."
aws ecs update-service \
    --cluster production \
    --service myapp-$INACTIVE \
    --force-new-deployment \
    --task-definition myapp:$VERSION

# Wait for deployment to stabilize
echo "Waiting for deployment to stabilize..."
aws ecs wait services-stable \
    --cluster production \
    --services myapp-$INACTIVE

# 2. Health check on inactive environment
echo "Step 2: Running health checks on $INACTIVE..."
INACTIVE_LB=$(aws elbv2 describe-target-groups \
    --names myapp-$INACTIVE \
    --query 'TargetGroups[0].LoadBalancerArns[0]' \
    --output text)

INACTIVE_DNS=$(aws elbv2 describe-load-balancers \
    --load-balancer-arns $INACTIVE_LB \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

for i in {1..5}; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$INACTIVE_DNS/health)
    if [ "$RESPONSE" == "200" ]; then
        echo "✅ Health check $i/5 passed"
    else
        echo "✗ Health check failed with status $RESPONSE"
        exit 1
    fi
    sleep 5
done

# 3. Run smoke tests
echo "Step 3: Running smoke tests..."
./smoke-tests.sh http://$INACTIVE_DNS || {
    echo "✗ Smoke tests failed"
    exit 1
}

# 4. Switch traffic to inactive environment
echo "Step 4: Switching traffic to $INACTIVE environment..."
INACTIVE_TARGET_ARN=$(aws elbv2 describe-target-groups \
    --names myapp-$INACTIVE \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

aws elbv2 modify-rule \
    --rule-arn $PRODUCTION_RULE_ARN \
    --actions Type=forward,TargetGroupArn=$INACTIVE_TARGET_ARN

echo "✅ Traffic switched to $INACTIVE"

# 5. Monitor for issues
echo "Step 5: Monitoring for 5 minutes..."
sleep 300

# 6. Check metrics
ERROR_RATE=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/ApplicationELB \
    --metric-name HTTPCode_Target_5XX_Count \
    --dimensions Name=TargetGroup,Value=$INACTIVE_TARGET_ARN \
    --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text)

if [ "$ERROR_RATE" != "None" ] && [ "$ERROR_RATE" -gt 10 ]; then
    echo "✗ High error rate detected: $ERROR_RATE errors"
    echo "Rolling back..."

    # Rollback: switch traffic back
    LIVE_TARGET_ARN=$(aws elbv2 describe-target-groups \
        --names myapp-$LIVE \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text)

    aws elbv2 modify-rule \
        --rule-arn $PRODUCTION_RULE_ARN \
        --actions Type=forward,TargetGroupArn=$LIVE_TARGET_ARN

    echo "✅ Rolled back to $LIVE"
    exit 1
fi

echo "✅ Deployment successful!"
echo "New live environment: $INACTIVE"
echo "Old environment ($LIVE) is now inactive and can be used for next deployment"
```

### Database Considerations

**Problem**: Both environments might need to read/write to same database

**Solution: Expand-Contract Pattern**:

```sql
-- Phase 1: Expansion (compatible with both blue and green)
-- Add new column, keep old column
ALTER TABLE users ADD COLUMN email_v2 VARCHAR(255);

-- Both environments can work:
-- Blue (old): uses 'email' column
-- Green (new): uses 'email_v2' column, falls back to 'email'

-- Phase 2: Backfill data
UPDATE users SET email_v2 = email WHERE email_v2 IS NULL;

-- Phase 3: After green is stable, contract (remove old column)
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN email_v2 TO email;
```

---

## Canary Release

### Pattern Overview

**Concept**: Gradually roll out changes to a small percentage of users, monitor, and increase if stable.

**Benefits**:
- Early detection of issues with minimal user impact
- Gradual confidence building
- Controlled risk
- Real production testing

**Drawbacks**:
- Complex routing logic
- Requires sophisticated monitoring
- Takes longer than instant deployment
- Some users get different experiences

### Canary Stages

```
Stage 1: 5% canary   →  95% stable, 5% canary   (1 hour)
Stage 2: 10% canary  →  90% stable, 10% canary  (1 hour)
Stage 3: 25% canary  →  75% stable, 25% canary  (2 hours)
Stage 4: 50% canary  →  50% stable, 50% canary  (2 hours)
Stage 5: 100% new    →  All traffic to new version
```

### Implementation: Kubernetes with Istio

**1. Setup Service Mesh**:
```yaml
# myapp-deployment-stable.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-stable
  labels:
    app: myapp
    version: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      version: stable
  template:
    metadata:
      labels:
        app: myapp
        version: stable
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0
        ports:
        - containerPort: 8080

---
# myapp-deployment-canary.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-canary
  labels:
    app: myapp
    version: canary
spec:
  replicas: 1  # 10% of traffic (1 out of 10 pods)
  selector:
    matchLabels:
      app: myapp
      version: canary
  template:
    metadata:
      labels:
        app: myapp
        version: canary
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0
        ports:
        - containerPort: 8080
```

**2. Istio Traffic Routing**:
```yaml
# virtualservice.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp.example.com
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: myapp
        subset: canary
      weight: 100
  - route:
    - destination:
        host: myapp
        subset: stable
      weight: 90  # 90% to stable
    - destination:
        host: myapp
        subset: canary
      weight: 10  # 10% to canary

---
# destinationrule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
```

**3. Automated Canary Progression**:
```python
# canary-controller.py
import time
import requests
from kubernetes import client, config

config.load_kube_config()
api = client.CustomObjectsApi()

def get_error_rate(version):
    """Query Prometheus for error rate"""
    query = f'rate(http_requests_total{{version="{version}",status=~"5.."}}[5m])'
    response = requests.get(
        'http://prometheus:9090/api/v1/query',
        params={'query': query}
    )
    result = response.json()['data']['result']
    return float(result[0]['value'][1]) if result else 0.0

def update_traffic_split(stable_weight, canary_weight):
    """Update Istio VirtualService traffic split"""
    vs = api.get_namespaced_custom_object(
        group="networking.istio.io",
        version="v1beta1",
        namespace="default",
        plural="virtualservices",
        name="myapp"
    )

    vs['spec']['http'][1]['route'][0]['weight'] = stable_weight
    vs['spec']['http'][1]['route'][1]['weight'] = canary_weight

    api.patch_namespaced_custom_object(
        group="networking.istio.io",
        version="v1beta1",
        namespace="default",
        plural="virtualservices",
        name="myapp",
        body=vs
    )

    print(f"Traffic updated: {stable_weight}% stable, {canary_weight}% canary")

def canary_deployment():
    """Progressive canary deployment with automatic rollback"""
    stages = [
        (95, 5, 3600),   # 5% for 1 hour
        (90, 10, 3600),  # 10% for 1 hour
        (75, 25, 7200),  # 25% for 2 hours
        (50, 50, 7200),  # 50% for 2 hours
        (0, 100, 0)      # 100% (complete)
    ]

    for stable_weight, canary_weight, duration in stages:
        print(f"\n🚀 Stage: {canary_weight}% canary traffic")

        # Update traffic split
        update_traffic_split(stable_weight, canary_weight)

        if duration > 0:
            # Monitor for the duration
            print(f"Monitoring for {duration/3600:.1f} hours...")
            intervals = duration // 300  # Check every 5 minutes

            for i in range(intervals):
                time.sleep(300)

                # Check metrics
                canary_errors = get_error_rate('canary')
                stable_errors = get_error_rate('stable')

                print(f"Check {i+1}/{intervals}: "
                      f"Stable errors: {stable_errors:.4f}, "
                      f"Canary errors: {canary_errors:.4f}")

                # Rollback if canary error rate is significantly higher
                if canary_errors > stable_errors * 2 and canary_errors > 0.01:
                    print(f"⚠️  Canary error rate too high! Rolling back...")
                    update_traffic_split(100, 0)
                    return False

        print(f"✅ Stage complete")

    print("\n🎉 Canary deployment successful!")
    return True

if __name__ == '__main__':
    success = canary_deployment()
    exit(0 if success else 1)
```

---

## Rolling Update

### Pattern Overview

**Concept**: Gradually replace instances of old version with new version, one (or few) at a time.

**Benefits**:
- Zero downtime
- No duplicate infrastructure needed
- Automatic rollback on failure
- Built into Kubernetes

**Drawbacks**:
- Deployment takes longer
- Multiple versions running simultaneously
- Requires careful compatibility planning

### Implementation: Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max 2 extra pods during update
      maxUnavailable: 0  # Always maintain full capacity
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v2.0
        ports:
        - containerPort: 8080
        readinessProbe:  # Critical for rolling updates
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          successThreshold: 2  # Must pass 2 checks before ready
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
```

**Rolling Update Process**:
```
Initial: [v1.0] [v1.0] [v1.0] [v1.0] [v1.0]

Step 1: Create new pod
        [v1.0] [v1.0] [v1.0] [v1.0] [v1.0] [v2.0] ← Creating

Step 2: New pod ready, terminate one old
        [v1.0] [v1.0] [v1.0] [v1.0] [v2.0] ← Removed v1.0

Step 3: Create another new pod
        [v1.0] [v1.0] [v1.0] [v1.0] [v2.0] [v2.0] ← Creating

Step 4: New pod ready, terminate another old
        [v1.0] [v1.0] [v1.0] [v2.0] [v2.0] ← Removed v1.0

... Continue until all pods replaced ...

Final:  [v2.0] [v2.0] [v2.0] [v2.0] [v2.0]
```

**Automated Rolling Update with Validation**:
```bash
#!/bin/bash
# rolling-update.sh

set -e

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

# 1. Update deployment image
echo "Updating deployment to version $VERSION..."
kubectl set image deployment/myapp myapp=myapp:$VERSION

# 2. Watch rollout progress
echo "Watching rollout progress..."
kubectl rollout status deployment/myapp --timeout=10m || {
    echo "⚠️  Rollout failed or timed out"
    echo "Rolling back..."
    kubectl rollout undo deployment/myapp
    kubectl rollout status deployment/myapp
    exit 1
}

# 3. Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=myapp --timeout=5m

# 4. Run smoke tests
echo "Running smoke tests..."
./smoke-tests.sh || {
    echo "⚠️  Smoke tests failed"
    echo "Rolling back..."
    kubectl rollout undo deployment/myapp
    kubectl rollout status deployment/myapp
    exit 1
}

# 5. Monitor metrics for 5 minutes
echo "Monitoring metrics..."
sleep 300

ERROR_RATE=$(kubectl exec -it deployment/myapp -- curl -s localhost:8080/metrics | \
    grep http_errors_total | awk '{print $2}')

if [ "$ERROR_RATE" -gt 100 ]; then
    echo "⚠️  High error rate: $ERROR_RATE"
    echo "Rolling back..."
    kubectl rollout undo deployment/myapp
    kubectl rollout status deployment/myapp
    exit 1
fi

echo "✅ Rolling update successful!"
kubectl rollout history deployment/myapp
```

---

## Feature Flag Deployment

### Pattern Overview

**Concept**: Deploy code with features disabled by flags, enable features gradually via configuration.

**Benefits**:
- Decouple deployment from release
- Test in production with feature disabled
- Gradual rollout of features
- Easy rollback (just disable flag)
- A/B testing capability

**Drawbacks**:
- Code complexity (if/else branches)
- Technical debt (old flags must be removed)
- Configuration management overhead

### Implementation

**1. Feature Flag Service**:
```javascript
// feature-flags.js
const redis = require('redis');
const client = redis.createClient();

class FeatureFlags {
  async isEnabled(flagName, userId = null) {
    // Check if feature is globally enabled
    const globalFlag = await client.get(`feature:${flagName}`);

    if (globalFlag === 'false') {
      return false;  // Disabled for everyone
    }

    if (globalFlag === 'true') {
      return true;  // Enabled for everyone
    }

    // Percentage rollout
    if (globalFlag && globalFlag.startsWith('percentage:')) {
      const percentage = parseInt(globalFlag.split(':')[1]);
      if (userId) {
        // Consistent hash for user
        const hash = hashCode(userId);
        return (hash % 100) < percentage;
      }
      return (Math.random() * 100) < percentage;
    }

    // User/group allowlist
    if (userId) {
      const userEnabled = await client.sismember(
        `feature:${flagName}:users`,
        userId
      );
      return userEnabled === 1;
    }

    return false;  // Default: disabled
  }

  async setFlag(flagName, value) {
    await client.set(`feature:${flagName}`, value);
  }

  async enableForPercentage(flagName, percentage) {
    await client.set(`feature:${flagName}`, `percentage:${percentage}`);
  }

  async enableForUser(flagName, userId) {
    await client.sadd(`feature:${flagName}:users`, userId);
  }
}

function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

module.exports = new FeatureFlags();
```

**2. Application Usage**:
```javascript
// app.js
const featureFlags = require('./feature-flags');

app.get('/api/dashboard', async (req, res) => {
  const userId = req.user.id;

  // Check feature flag
  const newDashboardEnabled = await featureFlags.isEnabled(
    'new-dashboard',
    userId
  );

  if (newDashboardEnabled) {
    // New implementation
    return res.json(await getNewDashboard(userId));
  } else {
    // Old implementation (fallback)
    return res.json(await getOldDashboard(userId));
  }
});
```

**3. Feature Flag Management CLI**:
```bash
#!/bin/bash
# feature-flag.sh

REDIS_CLI="redis-cli"
FLAG_NAME=$1
COMMAND=$2
VALUE=$3

case $COMMAND in
  "enable")
    $REDIS_CLI SET "feature:$FLAG_NAME" "true"
    echo "✅ Feature '$FLAG_NAME' enabled globally"
    ;;

  "disable")
    $REDIS_CLI SET "feature:$FLAG_NAME" "false"
    echo "✅ Feature '$FLAG_NAME' disabled globally"
    ;;

  "percentage")
    $REDIS_CLI SET "feature:$FLAG_NAME" "percentage:$VALUE"
    echo "✅ Feature '$FLAG_NAME' enabled for $VALUE% of users"
    ;;

  "enable-user")
    $REDIS_CLI SADD "feature:$FLAG_NAME:users" "$VALUE"
    echo "✅ Feature '$FLAG_NAME' enabled for user $VALUE"
    ;;

  "status")
    STATUS=$($REDIS_CLI GET "feature:$FLAG_NAME")
    echo "Feature '$FLAG_NAME': $STATUS"
    ;;

  *)
    echo "Usage: $0 <flag-name> <enable|disable|percentage|enable-user|status> [value]"
    exit 1
    ;;
esac
```

**4. Gradual Rollout Strategy**:
```bash
#!/bin/bash
# gradual-rollout.sh

FEATURE=$1

echo "Starting gradual rollout of feature: $FEATURE"

# Stage 1: Enable for internal users only
echo "Stage 1: Internal users only"
./feature-flag.sh $FEATURE enable-user "internal-user-1"
./feature-flag.sh $FEATURE enable-user "internal-user-2"
sleep 3600  # Wait 1 hour

# Stage 2: 5% of users
echo "Stage 2: 5% of users"
./feature-flag.sh $FEATURE percentage 5
sleep 7200  # Wait 2 hours

# Stage 3: 10% of users
echo "Stage 3: 10% of users"
./feature-flag.sh $FEATURE percentage 10
sleep 7200

# Stage 4: 25% of users
echo "Stage 4: 25% of users"
./feature-flag.sh $FEATURE percentage 25
sleep 14400  # Wait 4 hours

# Stage 5: 50% of users
echo "Stage 5: 50% of users"
./feature-flag.sh $FEATURE percentage 50
sleep 14400

# Stage 6: 100% of users
echo "Stage 6: 100% of users (full rollout)"
./feature-flag.sh $FEATURE enable

echo "✅ Feature '$FEATURE' fully rolled out"
```

---

## A/B Testing Infrastructure

### Pattern Overview

**Concept**: Deploy multiple versions simultaneously, split traffic for experimentation and data-driven decisions.

**Benefits**:
- Data-driven feature decisions
- Optimize user experience
- Test multiple variants
- Measure business impact

**Use Cases**:
- UI/UX changes
- Algorithm variations
- Pricing strategies
- Marketing campaigns

### Implementation: Nginx-based A/B Testing

```nginx
# nginx.conf
http {
    # Define upstream groups
    upstream variant_a {
        server 10.0.1.10:8080;  # Version A
    }

    upstream variant_b {
        server 10.0.1.20:8080;  # Version B
    }

    # Split clients based on user ID
    map $cookie_user_id $ab_variant {
        default "variant_a";
        ~*^[0-4] "variant_a";  # 50% → A (user_id ending 0-4)
        ~*^[5-9] "variant_b";  # 50% → B (user_id ending 5-9)
    }

    server {
        listen 80;
        server_name example.com;

        # Set variant cookie if not present
        add_header Set-Cookie "ab_variant=$ab_variant; Path=/; Max-Age=86400";

        location / {
            # Route based on variant
            proxy_pass http://$ab_variant;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-AB-Variant $ab_variant;  # Pass variant to backend
        }
    }
}
```

**Backend Tracking**:
```javascript
// analytics.js
const Analytics = {
  track(event, properties, userId) {
    const variant = properties.ab_variant || 'unknown';

    // Send to analytics service (Mixpanel, Segment, etc.)
    fetch('https://analytics.example.com/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event: event,
        properties: {
          ...properties,
          variant: variant,
          timestamp: new Date().toISOString()
        },
        userId: userId
      })
    });

    // Also send to metrics
    metrics.increment(`ab_test.${event}.${variant}`);
  }
};

// Usage in application
app.post('/api/checkout', async (req, res) => {
  const userId = req.user.id;
  const variant = req.headers['x-ab-variant'];

  // Track conversion
  Analytics.track('checkout_completed', {
    ab_variant: variant,
    order_value: req.body.total,
    items_count: req.body.items.length
  }, userId);

  // Process checkout
  const result = await processCheckout(req.body);
  res.json(result);
});
```

**A/B Test Analysis**:
```python
# analyze-ab-test.py
import psycopg2
from scipy import stats

def analyze_ab_test(metric_name, variant_a_values, variant_b_values):
    """Perform statistical analysis of A/B test"""

    # Calculate means
    mean_a = sum(variant_a_values) / len(variant_a_values)
    mean_b = sum(variant_b_values) / len(variant_b_values)

    # Perform t-test
    t_statistic, p_value = stats.ttest_ind(variant_a_values, variant_b_values)

    # Calculate confidence interval
    diff = mean_b - mean_a
    relative_diff = (diff / mean_a) * 100

    print(f"\n📊 A/B Test Results: {metric_name}")
    print(f"{'='*50}")
    print(f"Variant A: {mean_a:.2f} (n={len(variant_a_values)})")
    print(f"Variant B: {mean_b:.2f} (n={len(variant_b_values)})")
    print(f"Difference: {diff:.2f} ({relative_diff:+.1f}%)")
    print(f"P-value: {p_value:.4f}")

    if p_value < 0.05:
        winner = "B" if mean_b > mean_a else "A"
        print(f"✅ Result: Statistically significant! Variant {winner} wins.")
    else:
        print(f"⚠️  Result: Not statistically significant. Need more data or no real difference.")

    return {
        'mean_a': mean_a,
        'mean_b': mean_b,
        'difference': diff,
        'relative_difference': relative_diff,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

# Fetch data from database
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor()

# Get conversion rates
cursor.execute("""
    SELECT variant, COUNT(DISTINCT user_id) as users, COUNT(*) as conversions
    FROM events
    WHERE event = 'checkout_completed'
    AND timestamp > NOW() - INTERVAL '7 days'
    GROUP BY variant
""")

results = cursor.fetchall()

# Calculate conversion rate for each variant
for variant, users, conversions in results:
    conversion_rate = (conversions / users) * 100
    print(f"Variant {variant}: {conversion_rate:.2f}% conversion rate")
```

---

## Multi-Region Deployment

### Pattern Overview

**Concept**: Deploy application across multiple geographic regions for low latency and high availability.

**Benefits**:
- Low latency for global users
- High availability (region failure isolation)
- Compliance with data residency laws
- Disaster recovery

**Challenges**:
- Data synchronization
- Increased complexity
- Higher costs
- Deployment coordination

### Active-Active Multi-Region

**Architecture**:
```
                    Global DNS (Route53)
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
    Region A (US-East)              Region B (EU-West)
    ├─ Load Balancer               ├─ Load Balancer
    ├─ App Instances (3x)          ├─ App Instances (3x)
    ├─ Cache (Redis)               ├─ Cache (Redis)
    └─ Database (Primary)          └─ Database (Replica)
              ↓                              ↓
         Cross-Region Database Replication
```

**Terraform Multi-Region Setup**:
```hcl
# main.tf
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}

module "us_east_deployment" {
  source = "./modules/region-deployment"
  providers = {
    aws = aws.us_east
  }

  region = "us-east-1"
  environment = "production"
  app_version = var.app_version
}

module "eu_west_deployment" {
  source = "./modules/region-deployment"
  providers = {
    aws = aws.eu_west
  }

  region = "eu-west-1"
  environment = "production"
  app_version = var.app_version
}

# Global DNS with latency-based routing
resource "aws_route53_record" "global" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "us-east-1"
  latency_routing_policy {
    region = "us-east-1"
  }

  alias {
    name                   = module.us_east_deployment.lb_dns_name
    zone_id                = module.us_east_deployment.lb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "global_eu" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "api.example.com"
  type    = "A"

  set_identifier = "eu-west-1"
  latency_routing_policy {
    region = "eu-west-1"
  }

  alias {
    name                   = module.eu_west_deployment.lb_dns_name
    zone_id                = module.eu_west_deployment.lb_zone_id
    evaluate_target_health = true
  }
}
```

**Multi-Region Deployment Script**:
```bash
#!/bin/bash
# deploy-multi-region.sh

set -e

VERSION=$1
REGIONS=("us-east-1" "eu-west-1" "ap-southeast-1")

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "🌍 Multi-region deployment: version $VERSION"

# Deploy to all regions in parallel
for region in "${REGIONS[@]}"; do
    echo "Deploying to $region..."

    (
        # Set region
        export AWS_REGION=$region

        # Update ECS service
        aws ecs update-service \
            --cluster production \
            --service myapp \
            --force-new-deployment \
            --task-definition myapp:$VERSION \
            --region $region

        # Wait for deployment
        aws ecs wait services-stable \
            --cluster production \
            --services myapp \
            --region $region

        echo "✅ Deployment to $region complete"
    ) &
done

# Wait for all deployments to complete
wait

echo "✅ All regions deployed successfully!"

# Verify health in all regions
echo "Verifying health..."
for region in "${REGIONS[@]}"; do
    LB_DNS=$(aws elbv2 describe-load-balancers \
        --region $region \
        --query 'LoadBalancers[0].DNSName' \
        --output text)

    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$LB_DNS/health)

    if [ "$RESPONSE" == "200" ]; then
        echo "✅ $region: Healthy"
    else
        echo "✗ $region: Unhealthy (status $RESPONSE)"
        exit 1
    fi
done

echo "🎉 Multi-region deployment successful!"
```

---

## Microservices Deployment

### Pattern Overview

**Concept**: Deploy multiple independent services that work together.

**Challenges**:
- Service discovery
- Inter-service communication
- Dependency management
- Coordinated deployments
- Distributed tracing

### Service Mesh with Istio

```yaml
# microservices-deployment.yaml

# Service 1: User Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
        version: v1.0
    spec:
      containers:
      - name: user-service
        image: user-service:v1.0
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - port: 80
    targetPort: 8080

---
# Service 2: Order Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
        version: v1.0
    spec:
      containers:
      - name: order-service
        image: order-service:v1.0
        ports:
        - containerPort: 8080
        env:
        - name: USER_SERVICE_URL
          value: "http://user-service"
---
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
  - port: 80
    targetPort: 8080

---
# Istio VirtualService for Traffic Management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service
spec:
  hosts:
  - user-service
  http:
  - timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
    route:
    - destination:
        host: user-service
        subset: v1
      weight: 100
```

**Coordinated Microservices Deployment**:
```bash
#!/bin/bash
# deploy-microservices.sh

set -e

# Define services in dependency order
SERVICES=(
  "database-service:v2.0"
  "user-service:v2.0"
  "order-service:v2.0"
  "notification-service:v2.0"
  "api-gateway:v2.0"
)

echo "🚀 Deploying microservices..."

for service_version in "${SERVICES[@]}"; do
    SERVICE=$(echo $service_version | cut -d: -f1)
    VERSION=$(echo $service_version | cut -d: -f2)

    echo "\nDeploying $SERVICE:$VERSION..."

    # Deploy service
    kubectl set image deployment/$SERVICE $SERVICE=${SERVICE}:${VERSION}

    # Wait for rollout
    kubectl rollout status deployment/$SERVICE --timeout=5m || {
        echo "✗ Deployment failed for $SERVICE"
        echo "Rolling back..."
        kubectl rollout undo deployment/$SERVICE
        exit 1
    }

    # Health check
    echo "Health check for $SERVICE..."
    sleep 10
    kubectl exec -it deployment/$SERVICE -- curl -f http://localhost:8080/health || {
        echo "✗ Health check failed for $SERVICE"
        exit 1
    }

    echo "✅ $SERVICE deployed successfully"
done

echo "\n🎉 All microservices deployed successfully!"
```

---

## Serverless Deployment

### Pattern Overview

**Concept**: Deploy functions that run on-demand without managing servers.

**Benefits**:
- No server management
- Automatic scaling
- Pay per execution
- Built-in high availability

**Use Cases**:
- Event-driven processing
- APIs with variable traffic
- Background jobs
- Webhooks

### AWS Lambda Deployment

```yaml
# serverless.yml (Serverless Framework)
service: myapp-functions

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  environment:
    DATABASE_URL: ${ssm:/myapp/database-url}
    API_KEY: ${ssm:/myapp/api-key~true}  # SecureString

functions:
  api:
    handler: src/api.handler
    events:
      - httpApi:
          path: /api/{proxy+}
          method: ANY
    memorySize: 512
    timeout: 30
    reservedConcurrency: 100  # Limit concurrent executions

  processOrder:
    handler: src/processOrder.handler
    events:
      - sqs:
          arn: arn:aws:sqs:us-east-1:123456789012:orders-queue
          batchSize: 10
    memorySize: 1024
    timeout: 300

  scheduledJob:
    handler: src/scheduledJob.handler
    events:
      - schedule: rate(1 hour)
    memorySize: 256
    timeout: 60

resources:
  Resources:
    OrdersQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: orders-queue
        VisibilityTimeout: 300
```

**Deployment Script**:
```bash
#!/bin/bash
# deploy-serverless.sh

set -e

STAGE=$1  # dev, staging, prod

if [ -z "$STAGE" ]; then
    echo "Usage: $0 <stage>"
    exit 1
fi

echo "Deploying serverless functions to $STAGE..."

# Install dependencies
npm ci

# Run tests
npm test

# Deploy with Serverless Framework
serverless deploy --stage $STAGE --verbose

# Get deployment info
API_ENDPOINT=$(serverless info --stage $STAGE | grep "endpoint:" | awk '{print $2}')

echo "✅ Deployment complete!"
echo "API Endpoint: $API_ENDPOINT"

# Smoke test
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_ENDPOINT/health)
if [ "$RESPONSE" == "200" ]; then
    echo "✅ Smoke test passed"
else
    echo "✗ Smoke test failed (status $RESPONSE)"
    exit 1
fi
```

---

## Hybrid Cloud

### Pattern Overview

**Concept**: Deploy across on-premises and cloud infrastructure.

**Reasons**:
- Gradual cloud migration
- Data residency requirements
- Cost optimization
- Leverage existing infrastructure

**Challenges**:
- Network connectivity
- Security across boundaries
- Unified monitoring
- Consistent deployment process

### Implementation with Kubernetes Federation

```yaml
# hybrid-deployment.yaml

# Deploy to on-prem cluster
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  annotations:
    federation.kubernetes.io/clusters: "on-prem,aws-cloud"
spec:
  replicas: 5
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myregistry.onprem.com/myapp:v1.0
        env:
        - name: DATABASE_URL
          value: "postgresql://on-prem-db:5432/myapp"

---
# Replica placement preferences
apiVersion: scheduling.federation.k8s.io/v1alpha1
kind: ReplicaSchedulingPreference
metadata:
  name: myapp
  namespace: production
spec:
  targetKind: Deployment
  totalReplicas: 5
  clusters:
    on-prem:
      minReplicas: 2  # At least 2 on-prem
      maxReplicas: 3
      weight: 60      # Prefer on-prem (60%)
    aws-cloud:
      minReplicas: 2  # At least 2 in cloud
      maxReplicas: 3
      weight: 40      # Cloud as backup (40%)
```

---

## Edge Computing Deployment

### Pattern Overview

**Concept**: Deploy applications at the edge, close to end users or IoT devices.

**Benefits**:
- Ultra-low latency
- Reduced bandwidth costs
- Offline capability
- Data locality

**Use Cases**:
- CDN and content delivery
- IoT edge processing
- Mobile edge computing
- Gaming and streaming

### Cloudflare Workers Deployment

```javascript
// worker.js - Edge function
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)

  // Edge caching
  const cache = caches.default
  const cachedResponse = await cache.match(request)
  if (cachedResponse) {
    return cachedResponse
  }

  // Route to origin based on location
  const country = request.headers.get('cf-ipcountry')
  const origin = getOriginForCountry(country)

  // Fetch from origin
  const response = await fetch(`${origin}${url.pathname}`, {
    headers: request.headers
  })

  // Cache response
  const responseToCache = response.clone()
  event.waitUntil(cache.put(request, responseToCache))

  return response
}

function getOriginForCountry(country) {
  const regions = {
    'US': 'https://us.api.example.com',
    'EU': 'https://eu.api.example.com',
    'ASIA': 'https://asia.api.example.com'
  }
  return regions[country] || regions['US']
}
```

**Deploy to Edge**:
```bash
# wrangler.toml
name = "myapp-edge"
type = "javascript"
account_id = "your-account-id"
workers_dev = true
route = "api.example.com/*"
zone_id = "your-zone-id"

# Deploy
wrangler publish
```

---

## Related Documentation

- **[Core Concepts](core-concepts.md)**: Fundamental deployment concepts
- **[Best Practices](best-practices.md)**: Apply patterns correctly
- **[Advanced Topics](advanced-topics.md)**: Complex deployment scenarios
- **[Examples](../examples/)**: See patterns in action

---

**Next**: Explore [Advanced Topics](advanced-topics.md) for deep dives into complex scenarios, or see [Examples](../examples/intermediate/) for practical pattern implementations.
