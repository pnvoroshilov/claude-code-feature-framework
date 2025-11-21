# Advanced Deployment Topics

Expert-level deployment techniques, patterns, and strategies for complex scenarios. Master advanced concepts for enterprise-scale deployments.

## Table of Contents

- [Advanced Kubernetes Operators](#advanced-kubernetes-operators)
- [Service Mesh Implementation](#service-mesh-implementation)
- [GitOps Workflows](#gitops-workflows)
- [Multi-Tenancy Architectures](#multi-tenancy-architectures)
- [Chaos Engineering](#chaos-engineering)
- [Advanced Monitoring and Tracing](#advanced-monitoring-and-tracing)
- [Infrastructure Automation at Scale](#infrastructure-automation-at-scale)
- [Compliance and Audit Automation](#compliance-and-audit-automation)
- [Custom CI/CD Pipeline Development](#custom-cicd-pipeline-development)
- [Performance Optimization](#performance-optimization)

---

## Advanced Kubernetes Operators

### What is a Kubernetes Operator?

An operator extends Kubernetes API to manage complex applications with custom resources and controllers. It encodes operational knowledge into software.

**Use Cases**:
- Database management (backup, scaling, failover)
- Stateful application orchestration
- Complex deployment workflows
- Self-healing applications

### Building a Custom Operator

**Custom Resource Definition (CRD)**:
```yaml
# myapp-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: myapps.example.com
spec:
  group: example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
                  minimum: 1
                  maximum: 10
                version:
                  type: string
                database:
                  type: object
                  properties:
                    type:
                      type: string
                      enum: [postgres, mysql]
                    size:
                      type: string
  scope: Namespaced
  names:
    plural: myapps
    singular: myapp
    kind: MyApp
    shortNames:
      - ma
```

**Operator Controller (Go)**:
```go
// controller.go
package main

import (
    "context"
    "fmt"
    "time"

    corev1 "k8s.io/api/core/v1"
    "k8s.io/apimachinery/pkg/api/errors"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "sigs.k8s.io/controller-runtime/pkg/controller"
    "sigs.k8s.io/controller-runtime/pkg/handler"
    "sigs.k8s.io/controller-runtime/pkg/reconcile"
)

type MyAppReconciler struct {
    client.Client
    Scheme *runtime.Scheme
}

func (r *MyAppReconciler) Reconcile(ctx context.Context, req reconcile.Request) (reconcile.Result, error) {
    // Fetch MyApp instance
    myapp := &examplev1.MyApp{}
    err := r.Get(ctx, req.NamespacedName, myapp)
    if err != nil {
        if errors.IsNotFound(err) {
            return reconcile.Result{}, nil
        }
        return reconcile.Result{}, err
    }

    // Ensure deployment exists
    deployment := r.createDeployment(myapp)
    err = r.Get(ctx, client.ObjectKeyFromObject(deployment), deployment)
    if err != nil && errors.IsNotFound(err) {
        err = r.Create(ctx, deployment)
        if err != nil {
            return reconcile.Result{}, err
        }
    }

    // Ensure service exists
    service := r.createService(myapp)
    err = r.Get(ctx, client.ObjectKeyFromObject(service), service)
    if err != nil && errors.IsNotFound(err) {
        err = r.Create(ctx, service)
        if err != nil {
            return reconcile.Result{}, err
        }
    }

    // Ensure database exists if specified
    if myapp.Spec.Database != nil {
        database := r.createDatabase(myapp)
        err = r.Get(ctx, client.ObjectKeyFromObject(database), database)
        if err != nil && errors.IsNotFound(err) {
            err = r.Create(ctx, database)
            if err != nil {
                return reconcile.Result{}, err
            }
        }
    }

    // Update status
    myapp.Status.Ready = true
    err = r.Status().Update(ctx, myapp)
    if err != nil {
        return reconcile.Result{}, err
    }

    return reconcile.Result{RequeueAfter: 30 * time.Second}, nil
}
```

---

## Service Mesh Implementation

### Istio Service Mesh

**Complete Setup**:
```bash
# Install Istio
istioctl install --set profile=production

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled

# Verify installation
kubectl get pods -n istio-system
```

**Advanced Traffic Management**:
```yaml
# Canary deployment with Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp.example.com
  http:
  # Route based on headers (for testing)
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: myapp
        subset: canary
      weight: 100
  # Weighted traffic split
  - route:
    - destination:
        host: myapp
        subset: stable
      weight: 90
    - destination:
        host: myapp
        subset: canary
      weight: 10
    timeout: 10s
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure,refused-stream

---
# Circuit breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
  subsets:
  - name: stable
    labels:
      version: stable
  - name: canary
    labels:
      version: canary
```

**Mutual TLS (mTLS)**:
```yaml
# Enforce mTLS for all services
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: myapp-authz
  namespace: default
spec:
  selector:
    matchLabels:
      app: myapp
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

---

## GitOps Workflows

### ArgoCD Setup

**Installation**:
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**Application Definition**:
```yaml
# myapp-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myapp-k8s
    targetRevision: main
    path: k8s/production
    helm:
      valueFiles:
      - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # Delete resources not in git
      selfHeal: true   # Sync if cluster state drifts
      allowEmpty: false
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

**Multi-Environment GitOps**:
```
repo-structure:
k8s/
├── base/                  # Common resources
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/              # Dev-specific overrides
│   │   ├── kustomization.yaml
│   │   └── patches.yaml
│   ├── staging/          # Staging-specific
│   │   ├── kustomization.yaml
│   │   └── patches.yaml
│   └── production/       # Production-specific
│       ├── kustomization.yaml
│       └── patches.yaml
```

---

## Multi-Tenancy Architectures

### Namespace-based Multi-Tenancy

**Tenant Isolation**:
```yaml
# tenant-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-acme
  labels:
    tenant: acme

---
# Resource Quotas
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-acme-quota
  namespace: tenant-acme
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    persistentvolumeclaims: "10"
    pods: "50"

---
# Network Policy (isolation)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: tenant-isolation
  namespace: tenant-acme
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tenant: acme
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          tenant: acme
  - to:  # Allow DNS
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

---

## Chaos Engineering

### Chaos Mesh Setup

**Installation**:
```bash
# Install Chaos Mesh
curl -sSL https://mirrors.chaos-mesh.org/latest/install.sh | bash

# Verify
kubectl get pods -n chaos-testing
```

**Chaos Experiments**:
```yaml
# Network delay injection
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - production
    labelSelectors:
      app: myapp
  delay:
    latency: "100ms"
    correlation: "25"
    jitter: "10ms"
  duration: "30s"

---
# Pod failure injection
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-failure
spec:
  action: pod-failure
  mode: fixed
  value: "2"  # Kill 2 pods
  selector:
    namespaces:
      - production
    labelSelectors:
      app: myapp
  duration: "60s"
  scheduler:
    cron: "@every 1h"  # Run every hour
```

---

## Advanced Monitoring and Tracing

### Distributed Tracing with Jaeger

**Setup**:
```bash
# Install Jaeger Operator
kubectl create namespace observability
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.42.0/jaeger-operator.yaml -n observability

# Create Jaeger instance
kubectl apply -f - <<EOF
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
  namespace: observability
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch:9200
EOF
```

**Application Instrumentation**:
```javascript
// tracing.js
const { JaegerTracer } = require('jaeger-client');
const { initTracer } = require('jaeger-client');

const config = {
  serviceName: 'myapp',
  sampler: {
    type: 'const',
    param: 1  // Sample all traces
  },
  reporter: {
    agentHost: process.env.JAEGER_AGENT_HOST || 'localhost',
    agentPort: 6832
  }
};

const tracer = initTracer(config);

// Express middleware
function tracingMiddleware(req, res, next) {
  const span = tracer.startSpan(`${req.method} ${req.path}`);

  span.setTag('http.method', req.method);
  span.setTag('http.url', req.url);
  span.setTag('http.status_code', res.statusCode);

  req.span = span;

  res.on('finish', () => {
    span.setTag('http.status_code', res.statusCode);
    span.finish();
  });

  next();
}

// Trace database queries
async function getUserFromDB(userId, parentSpan) {
  const span = tracer.startSpan('db.query.getUser', {
    childOf: parentSpan
  });

  span.setTag('db.type', 'postgresql');
  span.setTag('db.statement', 'SELECT * FROM users WHERE id = $1');

  try {
    const result = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
    span.setTag('db.rows', result.rows.length);
    return result.rows[0];
  } catch (error) {
    span.setTag('error', true);
    span.log({ event: 'error', message: error.message });
    throw error;
  } finally {
    span.finish();
  }
}
```

---

## Infrastructure Automation at Scale

### Terraform Workspaces and Modules

**Scalable Terraform Structure**:
```
terraform/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks-cluster/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── rds/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── production/
│       ├── main.tf
│       ├── terraform.tfvars
│       └── backend.tf
```

**Multi-Region Terraform**:
```hcl
# environments/production/main.tf
module "us_east_infrastructure" {
  source = "../../modules/complete-infrastructure"

  region = "us-east-1"
  environment = "production"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  vpc_cidr = "10.0.0.0/16"
  eks_cluster_version = "1.27"
  rds_instance_type = "db.r6g.xlarge"
  rds_multi_az = true
}

module "eu_west_infrastructure" {
  source = "../../modules/complete-infrastructure"

  region = "eu-west-1"
  environment = "production"
  availability_zones = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]

  vpc_cidr = "10.1.0.0/16"
  eks_cluster_version = "1.27"
  rds_instance_type = "db.r6g.xlarge"
  rds_multi_az = true
}

# Cross-region replication
resource "aws_db_instance_automated_backups_replication" "cross_region" {
  source_db_instance_arn = module.us_east_infrastructure.rds_arn
  retention_period       = 7
}
```

---

## Compliance and Audit Automation

### Policy-as-Code with OPA

**Open Policy Agent (OPA) Setup**:
```yaml
# opa-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opa
  namespace: opa
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opa
  template:
    metadata:
      labels:
        app: opa
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        args:
        - "run"
        - "--server"
        - "--addr=0.0.0.0:8181"
        ports:
        - containerPort: 8181
```

**Security Policies**:
```rego
# policies/security.rego

# Deny containers running as root
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  container.securityContext.runAsNonRoot != true
  msg := sprintf("Container %v must run as non-root user", [container.name])
}

# Require resource limits
deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  not container.resources.limits
  msg := sprintf("Container %v must have resource limits", [container.name])
}

# Enforce image from approved registries
deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  not startswith(container.image, "mycompany.registry.io/")
  msg := sprintf("Container %v uses unapproved registry", [container.name])
}
```

---

## Custom CI/CD Pipeline Development

### Jenkins Shared Library

```groovy
// vars/deployApplication.groovy
def call(Map config) {
    pipeline {
        agent any

        environment {
            DOCKER_REGISTRY = credentials('docker-registry')
            KUBECONFIG = credentials('kubeconfig-production')
        }

        stages {
            stage('Build') {
                steps {
                    script {
                        docker.build("${config.imageName}:${env.BUILD_NUMBER}")
                    }
                }
            }

            stage('Test') {
                steps {
                    sh 'npm test'
                    sh 'npm run test:integration'
                }
            }

            stage('Security Scan') {
                steps {
                    sh "trivy image ${config.imageName}:${env.BUILD_NUMBER}"
                }
            }

            stage('Push Image') {
                steps {
                    script {
                        docker.withRegistry('https://registry.example.com', 'docker-registry') {
                            docker.image("${config.imageName}:${env.BUILD_NUMBER}").push()
                            docker.image("${config.imageName}:${env.BUILD_NUMBER}").push('latest')
                        }
                    }
                }
            }

            stage('Deploy') {
                steps {
                    sh """
                        kubectl set image deployment/${config.deploymentName} \
                            ${config.containerName}=${config.imageName}:${env.BUILD_NUMBER}
                        kubectl rollout status deployment/${config.deploymentName}
                    """
                }
            }

            stage('Verify') {
                steps {
                    script {
                        def healthy = sh(
                            script: "kubectl get deployment ${config.deploymentName} -o jsonpath='{.status.conditions[?(@.type==\"Available\")].status}'",
                            returnStdout: true
                        ).trim()

                        if (healthy != 'True') {
                            error("Deployment not healthy")
                        }
                    }
                }
            }
        }

        post {
            failure {
                sh "kubectl rollout undo deployment/${config.deploymentName}"
            }
        }
    }
}
```

---

## Performance Optimization

### Database Query Optimization

**Query Analysis**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries > 100ms

-- Analyze slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_orders_user_created ON orders(user_id, created_at DESC);
```

### Application-Level Caching

**Multi-Layer Cache Strategy**:
```javascript
// cache.js
const NodeCache = require('node-cache');
const Redis = require('redis');

class MultiLayerCache {
  constructor() {
    this.l1Cache = new NodeCache({ stdTTL: 60, checkperiod: 120 });
    this.l2Cache = Redis.createClient({ url: process.env.REDIS_URL });
  }

  async get(key) {
    // Check L1 (in-memory)
    const l1Value = this.l1Cache.get(key);
    if (l1Value) {
      return l1Value;
    }

    // Check L2 (Redis)
    const l2Value = await this.l2Cache.get(key);
    if (l2Value) {
      const parsed = JSON.parse(l2Value);
      this.l1Cache.set(key, parsed);  // Warm L1
      return parsed;
    }

    return null;
  }

  async set(key, value, ttl = 300) {
    // Set in both layers
    this.l1Cache.set(key, value, Math.min(ttl, 60));
    await this.l2Cache.setEx(key, ttl, JSON.stringify(value));
  }

  async delete(key) {
    this.l1Cache.del(key);
    await this.l2Cache.del(key);
  }
}

module.exports = new MultiLayerCache();
```

---

## Related Documentation

- **[Core Concepts](core-concepts.md)**: Foundational knowledge
- **[Best Practices](best-practices.md)**: Standard practices
- **[Patterns](patterns.md)**: Common deployment patterns
- **[Examples](../examples/advanced/)**: Advanced examples

---

**Next**: See [Advanced Examples](../examples/advanced/) for practical implementations, or review [Troubleshooting](troubleshooting.md) for complex issue resolution.
