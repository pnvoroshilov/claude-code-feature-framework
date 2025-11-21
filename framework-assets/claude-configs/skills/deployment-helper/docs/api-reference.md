# API and Tools Reference

Complete reference guide for deployment tools, commands, and configuration options. Quick lookup for syntax and parameters.

## Table of Contents

- [Docker Commands](#docker-commands)
- [Kubernetes kubectl](#kubernetes-kubectl)
- [Cloud CLI Tools](#cloud-cli-tools)
- [Terraform](#terraform)
- [CI/CD Configuration](#cicd-configuration)
- [Monitoring Tools](#monitoring-tools)
- [Infrastructure Automation](#infrastructure-automation)
- [Configuration Management](#configuration-management)
- [Security Tools](#security-tools)
- [Helm Charts](#helm-charts)

---

## Docker Commands

### Image Management

**Build Image**
```bash
docker build [OPTIONS] PATH

Options:
  -t, --tag NAME:TAG      # Name and tag image
  -f, --file FILE         # Path to Dockerfile
  --build-arg KEY=VALUE   # Set build-time variables
  --target STAGE          # Multi-stage build target
  --no-cache              # Build without cache

Examples:
docker build -t myapp:v1.0 .
docker build -t myapp:v1.0 -f Dockerfile.prod .
docker build --target production -t myapp:prod .
```

**Push/Pull Images**
```bash
# Push to registry
docker push [OPTIONS] NAME[:TAG]

# Pull from registry
docker pull [OPTIONS] NAME[:TAG]

# Tag image
docker tag SOURCE_IMAGE[:TAG] TARGET_IMAGE[:TAG]

Examples:
docker tag myapp:v1.0 myregistry.com/myapp:v1.0
docker push myregistry.com/myapp:v1.0
docker pull myregistry.com/myapp:v1.0
```

**List and Remove Images**
```bash
# List images
docker images [OPTIONS] [REPOSITORY[:TAG]]

Options:
  -a, --all              # Show all images
  -f, --filter FILTER    # Filter output
  -q, --quiet            # Only show IDs

# Remove images
docker rmi [OPTIONS] IMAGE [IMAGE...]

Options:
  -f, --force            # Force removal
  --no-prune             # Don't delete untagged parents

Examples:
docker images myapp
docker rmi myapp:v1.0
docker rmi $(docker images -f "dangling=true" -q)  # Remove untagged images
```

### Container Management

**Run Container**
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]

Options:
  -d, --detach                    # Run in background
  -p, --publish HOST:CONTAINER    # Publish ports
  -e, --env KEY=VALUE             # Set environment variables
  -v, --volume HOST:CONTAINER     # Mount volume
  --name NAME                     # Container name
  --rm                            # Remove on exit
  --network NETWORK               # Connect to network
  --restart POLICY                # Restart policy

Examples:
docker run -d -p 8080:80 --name web nginx
docker run -d -e DATABASE_URL=postgresql://... myapp:v1.0
docker run -d -v /host/data:/container/data myapp:v1.0
docker run -d --restart=unless-stopped myapp:v1.0
```

**Container Operations**
```bash
# Start/Stop/Restart
docker start CONTAINER
docker stop CONTAINER
docker restart CONTAINER

# View logs
docker logs [OPTIONS] CONTAINER

Options:
  -f, --follow           # Follow log output
  --tail N               # Show last N lines
  --since TIME           # Show logs since timestamp

# Execute command in container
docker exec [OPTIONS] CONTAINER COMMAND [ARG...]

Options:
  -i, --interactive      # Keep STDIN open
  -t, --tty              # Allocate pseudo-TTY

Examples:
docker logs -f --tail=100 myapp
docker exec -it myapp bash
docker exec myapp ls /app
```

### Docker Compose

**docker-compose.yml Syntax**
```yaml
version: '3.8'

services:
  web:
    image: nginx:latest
    # Or build from Dockerfile
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_ENV: production
    ports:
      - "8080:80"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    env_file:
      - .env
    volumes:
      - ./app:/usr/share/nginx/html
      - app-data:/var/lib/data
    depends_on:
      - database
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  database:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - app-network
    secrets:
      - db_password

volumes:
  app-data:
  db-data:

networks:
  app-network:
    driver: bridge

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

**Docker Compose Commands**
```bash
# Start services
docker-compose up [OPTIONS] [SERVICE...]

Options:
  -d, --detach           # Detached mode
  --build                # Build images before starting
  --force-recreate       # Recreate containers
  --scale SERVICE=NUM    # Scale service to NUM instances

# Stop and remove
docker-compose down [OPTIONS]

Options:
  -v, --volumes          # Remove volumes
  --rmi TYPE             # Remove images (all|local)

# Other commands
docker-compose ps                  # List containers
docker-compose logs -f SERVICE     # View logs
docker-compose exec SERVICE CMD    # Execute command
docker-compose build               # Build images
docker-compose pull                # Pull images

Examples:
docker-compose up -d
docker-compose up -d --build
docker-compose logs -f web
docker-compose exec web bash
docker-compose down -v
```

---

## Kubernetes kubectl

### Resource Management

**Apply/Create Resources**
```bash
# Apply configuration
kubectl apply -f FILE

Options:
  -f, --filename FILE     # File or directory
  -R, --recursive         # Process directory recursively
  --dry-run=client        # Preview without creating
  -o, --output FORMAT     # Output format (json|yaml|wide)

# Create resource
kubectl create RESOURCE [OPTIONS]

Examples:
kubectl apply -f deployment.yaml
kubectl apply -f k8s/ -R
kubectl create deployment myapp --image=myapp:v1.0 --replicas=3
kubectl apply -f deployment.yaml --dry-run=client -o yaml
```

**Get Resources**
```bash
kubectl get RESOURCE [NAME] [OPTIONS]

Options:
  -o, --output FORMAT     # Output format
  -l, --selector LABEL    # Label selector
  -A, --all-namespaces    # All namespaces
  -w, --watch             # Watch for changes

Examples:
kubectl get pods
kubectl get pods -o wide
kubectl get pods -l app=myapp
kubectl get pods -A
kubectl get pods -w
kubectl get pods myapp-pod -o yaml
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
```

**Describe Resources**
```bash
kubectl describe RESOURCE NAME

Examples:
kubectl describe pod myapp-pod
kubectl describe deployment myapp
kubectl describe node node-1
```

**Delete Resources**
```bash
kubectl delete RESOURCE NAME [OPTIONS]

Options:
  -f, --filename FILE     # Delete from file
  -l, --selector LABEL    # Delete by label
  --grace-period SECONDS  # Grace period
  --force                 # Force deletion

Examples:
kubectl delete pod myapp-pod
kubectl delete -f deployment.yaml
kubectl delete pods -l app=myapp
kubectl delete pod myapp-pod --force --grace-period=0
```

### Deployment Management

**Rolling Updates**
```bash
# Set new image
kubectl set image deployment/DEPLOYMENT CONTAINER=IMAGE

# Rollout status
kubectl rollout status deployment/DEPLOYMENT

# Rollout history
kubectl rollout history deployment/DEPLOYMENT

# Rollback
kubectl rollout undo deployment/DEPLOYMENT [--to-revision=N]

# Restart deployment
kubectl rollout restart deployment/DEPLOYMENT

Examples:
kubectl set image deployment/myapp myapp=myapp:v2.0
kubectl rollout status deployment/myapp
kubectl rollout history deployment/myapp
kubectl rollout undo deployment/myapp
kubectl rollout undo deployment/myapp --to-revision=2
kubectl rollout restart deployment/myapp
```

**Scaling**
```bash
# Scale replicas
kubectl scale deployment/DEPLOYMENT --replicas=N

# Autoscale
kubectl autoscale deployment/DEPLOYMENT --min=MIN --max=MAX --cpu-percent=PERCENT

Examples:
kubectl scale deployment/myapp --replicas=5
kubectl autoscale deployment/myapp --min=2 --max=10 --cpu-percent=80
```

### Debugging

**Logs**
```bash
kubectl logs POD [CONTAINER] [OPTIONS]

Options:
  -f, --follow            # Follow logs
  --tail=N                # Last N lines
  --since=TIME            # Since time (5m, 1h)
  -p, --previous          # Previous container
  --timestamps            # Show timestamps

Examples:
kubectl logs myapp-pod
kubectl logs myapp-pod -f
kubectl logs myapp-pod --tail=100
kubectl logs myapp-pod --since=1h
kubectl logs myapp-pod -p  # Previous crashed container
```

**Execute Commands**
```bash
kubectl exec POD [OPTIONS] -- COMMAND [ARGS...]

Options:
  -i, --stdin             # Pass stdin
  -t, --tty               # Allocate TTY
  -c, --container NAME    # Container name

Examples:
kubectl exec myapp-pod -- ls /app
kubectl exec -it myapp-pod -- bash
kubectl exec myapp-pod -c sidecar -- ps aux
```

**Port Forwarding**
```bash
kubectl port-forward POD|SERVICE LOCAL_PORT:REMOTE_PORT

Examples:
kubectl port-forward pod/myapp-pod 8080:80
kubectl port-forward service/myapp 8080:80
```

---

## Cloud CLI Tools

### AWS CLI

**EC2 Operations**
```bash
# List instances
aws ec2 describe-instances [--filters KEY=VALUE]

# Start/Stop instances
aws ec2 start-instances --instance-ids INSTANCE_ID
aws ec2 stop-instances --instance-ids INSTANCE_ID

# Create instance
aws ec2 run-instances \
  --image-id AMI_ID \
  --instance-type TYPE \
  --key-name KEY_NAME \
  --security-group-ids SG_ID \
  --subnet-id SUBNET_ID

Examples:
aws ec2 describe-instances --filters "Name=tag:Name,Values=web-server"
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

**ECS Operations**
```bash
# Update service
aws ecs update-service \
  --cluster CLUSTER \
  --service SERVICE \
  --force-new-deployment \
  --task-definition TASK_DEFINITION:VERSION

# List tasks
aws ecs list-tasks --cluster CLUSTER --service SERVICE

# Describe task
aws ecs describe-tasks --cluster CLUSTER --tasks TASK_ARN

Examples:
aws ecs update-service --cluster prod --service myapp --force-new-deployment
aws ecs list-tasks --cluster prod --service myapp
```

**S3 Operations**
```bash
# Upload file
aws s3 cp FILE s3://BUCKET/PATH

# Sync directory
aws s3 sync LOCAL_DIR s3://BUCKET/PATH

# List objects
aws s3 ls s3://BUCKET/PATH

Examples:
aws s3 cp backup.sql.gz s3://myapp-backups/
aws s3 sync ./dist s3://myapp-static/
aws s3 ls s3://myapp-backups/ --recursive
```

### Google Cloud CLI (gcloud)

**Compute Engine**
```bash
# List instances
gcloud compute instances list

# SSH to instance
gcloud compute ssh INSTANCE_NAME

# Create instance
gcloud compute instances create INSTANCE_NAME \
  --image-family=IMAGE_FAMILY \
  --image-project=IMAGE_PROJECT \
  --machine-type=MACHINE_TYPE \
  --zone=ZONE

Examples:
gcloud compute instances list --filter="name~'^web-.*'"
gcloud compute ssh web-server-1 --zone=us-central1-a
```

**Kubernetes Engine (GKE)**
```bash
# Get cluster credentials
gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE

# List clusters
gcloud container clusters list

# Create cluster
gcloud container clusters create CLUSTER_NAME \
  --num-nodes=NUM \
  --machine-type=MACHINE_TYPE \
  --zone=ZONE

Examples:
gcloud container clusters get-credentials prod-cluster --zone=us-central1-a
gcloud container clusters list
```

### Azure CLI

**Virtual Machines**
```bash
# List VMs
az vm list [--resource-group GROUP]

# Start/Stop VM
az vm start --resource-group GROUP --name VM_NAME
az vm stop --resource-group GROUP --name VM_NAME

# Create VM
az vm create \
  --resource-group GROUP \
  --name VM_NAME \
  --image IMAGE \
  --size SIZE \
  --admin-username USER

Examples:
az vm list --resource-group myapp-rg --output table
az vm start --resource-group myapp-rg --name web-vm
```

**AKS (Azure Kubernetes Service)**
```bash
# Get credentials
az aks get-credentials --resource-group GROUP --name CLUSTER_NAME

# List clusters
az aks list [--resource-group GROUP]

# Scale cluster
az aks scale \
  --resource-group GROUP \
  --name CLUSTER_NAME \
  --node-count COUNT

Examples:
az aks get-credentials --resource-group myapp-rg --name prod-cluster
az aks scale --resource-group myapp-rg --name prod-cluster --node-count 5
```

---

## Terraform

### Core Commands

```bash
# Initialize working directory
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan [OPTIONS]

Options:
  -out=FILE               # Save plan to file
  -var KEY=VALUE          # Set variable
  -var-file=FILE          # Load variables from file

# Apply changes
terraform apply [OPTIONS]

Options:
  -auto-approve           # Skip approval prompt
  PLAN_FILE               # Apply saved plan

# Destroy resources
terraform destroy [OPTIONS]

# Other commands
terraform fmt               # Format configuration
terraform show              # Show current state
terraform output [NAME]     # Show output values
terraform state list        # List resources in state

Examples:
terraform init
terraform plan -out=tfplan
terraform apply tfplan
terraform apply -auto-approve
terraform destroy -auto-approve
terraform output database_url
```

### Resource Syntax

```hcl
# Provider configuration
provider "aws" {
  region = var.region
  version = "~> 5.0"
}

# Resource definition
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.medium"

  tags = {
    Name = "WebServer"
    Environment = var.environment
  }
}

# Data source
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# Output
output "instance_ip" {
  value = aws_instance.web.public_ip
}

# Variable
variable "region" {
  type    = string
  default = "us-east-1"
}
```

---

## CI/CD Configuration

### GitHub Actions

**Workflow Syntax**
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build
      run: npm run build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster production \
          --service myapp \
          --force-new-deployment
```

### GitLab CI

**.gitlab-ci.yml Syntax**
```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE

test:
  stage: test
  image: node:18
  script:
    - npm ci
    - npm test

deploy_production:
  stage: deploy
  image: bitnami/kubectl:latest
  only:
    - main
  script:
    - kubectl config use-context production
    - kubectl set image deployment/myapp myapp=$DOCKER_IMAGE
    - kubectl rollout status deployment/myapp
  environment:
    name: production
    url: https://myapp.example.com
```

---

## Monitoring Tools

### Prometheus Query Language (PromQL)

**Basic Queries**
```promql
# Current value
http_requests_total

# Rate over time
rate(http_requests_total[5m])

# Sum by label
sum(rate(http_requests_total[5m])) by (method, status)

# Percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Quantiles
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Alert Rules**
```yaml
groups:
  - name: example
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 10m
      labels:
        severity: critical
      annotations:
        summary: "High error rate"
        description: "Error rate is {{ $value }}"
```

---

## Helm Charts

**Chart Structure**
```
mychart/
  Chart.yaml          # Chart metadata
  values.yaml         # Default values
  templates/          # Kubernetes manifests
    deployment.yaml
    service.yaml
    ingress.yaml
```

**Helm Commands**
```bash
# Install chart
helm install RELEASE_NAME CHART [OPTIONS]

# Upgrade release
helm upgrade RELEASE_NAME CHART [OPTIONS]

# Rollback
helm rollback RELEASE_NAME [REVISION]

# List releases
helm list

# Uninstall
helm uninstall RELEASE_NAME

Options:
  --values FILE          # Values file
  --set KEY=VALUE        # Set value
  --namespace NS         # Namespace
  --create-namespace     # Create namespace if missing

Examples:
helm install myapp ./mychart
helm install myapp ./mychart --values prod-values.yaml
helm upgrade myapp ./mychart --set replicas=5
helm rollback myapp 1
```

---

## Related Documentation

- **[Core Concepts](core-concepts.md)**: Understand when to use these tools
- **[Best Practices](best-practices.md)**: How to use tools effectively
- **[Examples](../examples/)**: See tools in action

---

**Quick Reference**: Bookmark this page for fast command lookup during deployments.
