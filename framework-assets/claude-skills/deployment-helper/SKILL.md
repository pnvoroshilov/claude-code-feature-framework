---
name: deployment-helper
description: Comprehensive skill for automating application deployments, infrastructure setup, and DevOps workflows with containerization, CI/CD, and cloud management
version: 1.0.0
tags: [deployment, devops, ci-cd, docker, kubernetes]
---

# Deployment Helper - Application Deployment Automation

A comprehensive skill for automating application deployments, infrastructure setup, and DevOps workflows. Master containerization, CI/CD pipelines, cloud deployments, monitoring, and production-ready infrastructure management.

## Overview

Deployment Helper provides end-to-end guidance for deploying modern applications across various environments and platforms. Whether you're deploying a simple web app to a VPS, orchestrating microservices on Kubernetes, or setting up multi-region cloud infrastructure, this skill covers everything from basic deployments to advanced production scenarios.

## Quick Start

### Basic Deployment Checklist

```
Deployment Preparation:
- [ ] Code is tested and passes all checks
- [ ] Environment variables configured
- [ ] Database migrations prepared
- [ ] Dependencies documented
- [ ] Deployment target selected
- [ ] Rollback plan created
- [ ] Monitoring configured
```

### Simple Deployment Example

```bash
# 1. Build application
npm run build  # or: python -m build

# 2. Create deployment package
tar -czf app.tar.gz dist/ package.json

# 3. Deploy to server
scp app.tar.gz user@server:/var/www/app/
ssh user@server 'cd /var/www/app && tar -xzf app.tar.gz && pm2 restart app'

# 4. Verify deployment
curl https://yourdomain.com/health
```

## Core Capabilities

This skill covers **20+ deployment scenarios** and techniques:

### Infrastructure & Environment Setup
1. **Server Provisioning** - Configure VPS, cloud instances, bare metal servers
2. **Environment Configuration** - Manage environment variables, secrets, configs
3. **Network Setup** - Configure firewalls, load balancers, DNS, CDN
4. **SSL/TLS Configuration** - Set up HTTPS with Let's Encrypt, managed certificates
5. **Database Setup** - Deploy and configure PostgreSQL, MongoDB, Redis, etc.

### Containerization & Orchestration
6. **Docker Containerization** - Create optimized Docker images and containers
7. **Docker Compose** - Multi-container application orchestration
8. **Kubernetes Deployment** - Deploy and manage apps on K8s clusters
9. **Container Registries** - Use Docker Hub, ECR, GCR, private registries
10. **Service Mesh** - Implement Istio, Linkerd for microservices

### CI/CD & Automation
11. **GitHub Actions** - Automated testing, building, and deployment
12. **GitLab CI/CD** - Complete pipeline automation
13. **Jenkins Pipelines** - Advanced build and deployment automation
14. **Deployment Strategies** - Blue-green, canary, rolling deployments
15. **Infrastructure as Code** - Terraform, CloudFormation, Pulumi

### Cloud Platforms
16. **AWS Deployment** - EC2, ECS, EKS, Lambda, Elastic Beanstalk
17. **Google Cloud** - GCE, GKE, Cloud Run, App Engine
18. **Azure Deployment** - VMs, AKS, App Service, Functions
19. **Platform Services** - Heroku, Vercel, Netlify, Railway
20. **Multi-Cloud Strategy** - Deploy across multiple providers

### Monitoring & Operations
21. **Application Monitoring** - Set up Prometheus, Grafana, DataDog
22. **Log Aggregation** - Centralized logging with ELK, Loki, CloudWatch
23. **Error Tracking** - Sentry, Rollbar, Bugsnag integration
24. **Performance Monitoring** - APM tools, tracing, profiling
25. **Alerting & Incident Response** - PagerDuty, Opsgenie, on-call management

## Documentation

### Core Concepts
**[docs/core-concepts.md](docs/core-concepts.md)** - Fundamental deployment concepts
- Deployment fundamentals and lifecycle
- Infrastructure types and selection
- Environment management strategies
- Container orchestration principles
- CI/CD pipeline architecture
- Security and compliance basics
- Networking and load balancing
- Database deployment patterns
- Scaling strategies
- Disaster recovery planning

### Best Practices
**[docs/best-practices.md](docs/best-practices.md)** - Industry-standard deployment practices
- Pre-deployment checklist and validation
- Zero-downtime deployment techniques
- Database migration strategies
- Secret management best practices
- Container optimization guidelines
- Monitoring and observability standards
- Security hardening procedures
- Backup and recovery protocols
- Cost optimization strategies
- Team collaboration workflows

### Patterns & Strategies
**[docs/patterns.md](docs/patterns.md)** - Common deployment patterns
- Blue-Green deployment pattern
- Canary release strategy
- Rolling update pattern
- Feature flag deployments
- A/B testing infrastructure
- Multi-region deployments
- Microservices deployment patterns
- Serverless deployment strategies
- Hybrid cloud patterns
- Edge computing deployments

### Advanced Topics
**[docs/advanced-topics.md](docs/advanced-topics.md)** - Expert-level deployment
- Advanced Kubernetes operators
- Service mesh implementation
- GitOps workflows with ArgoCD/Flux
- Multi-tenancy architectures
- Chaos engineering and resilience testing
- Advanced monitoring and tracing
- Infrastructure automation at scale
- Compliance and audit automation
- Custom CI/CD pipeline development
- Performance optimization techniques

### Troubleshooting
**[docs/troubleshooting.md](docs/troubleshooting.md)** - Common deployment issues
- Deployment failures and rollbacks
- Container startup issues
- Networking and connectivity problems
- Database migration failures
- SSL/TLS certificate issues
- Resource exhaustion problems
- CI/CD pipeline debugging
- Cloud provider-specific issues
- Monitoring and alerting gaps
- Performance degradation analysis

### API & Tools Reference
**[docs/api-reference.md](docs/api-reference.md)** - Complete tool documentation
- Docker commands and configuration
- Kubernetes API and kubectl reference
- Cloud CLI tools (AWS, GCP, Azure)
- Terraform resource reference
- CI/CD configuration syntax
- Monitoring tool APIs
- Infrastructure automation tools
- Deployment automation scripts
- Configuration management tools
- Security and compliance tools

## Examples

### Basic Examples
Master foundational deployment scenarios:

- **[Simple VPS Deployment](examples/basic/simple-vps-deployment.md)** - Deploy Node.js/Python app to a VPS with PM2/systemd
- **[Docker Containerization](examples/basic/docker-containerization.md)** - Create production-ready Docker images
- **[Docker Compose Setup](examples/basic/docker-compose-setup.md)** - Multi-container application with database

### Intermediate Examples
Implement production-ready deployments:

- **[GitHub Actions CI/CD](examples/intermediate/github-actions-cicd.md)** - Complete automated pipeline
- **[Kubernetes Deployment](examples/intermediate/kubernetes-deployment.md)** - Deploy app to K8s cluster
- **[AWS EC2 Deployment](examples/intermediate/aws-ec2-deployment.md)** - Deploy to AWS with load balancer

### Advanced Examples
Master complex deployment scenarios:

- **[Multi-Region Kubernetes](examples/advanced/multi-region-kubernetes.md)** - Global K8s deployment with traffic management
- **[GitOps with ArgoCD](examples/advanced/gitops-argocd.md)** - Declarative GitOps deployment
- **[Blue-Green Deployment](examples/advanced/blue-green-deployment.md)** - Zero-downtime deployment strategy

## Templates

Ready-to-use deployment templates:

### **[Basic Deployment Template](templates/basic-deployment-template.md)**
Simple deployment configuration for small applications. Includes:
- Single-server deployment script
- Environment configuration
- Basic monitoring setup
- Simple backup strategy

### **[Production Deployment Template](templates/production-deployment-template.md)**
Production-ready deployment infrastructure. Includes:
- Multi-container setup with Docker Compose
- Load balancer configuration
- Database with replication
- Comprehensive monitoring
- Automated backup and recovery

### **[Kubernetes Production Template](templates/kubernetes-production-template.md)**
Complete Kubernetes deployment. Includes:
- Multi-environment K8s manifests
- Helm charts and configurations
- Ingress and service mesh setup
- HPA and cluster autoscaling
- Full observability stack

## Resources

### **[Quality Checklists](resources/checklists.md)**
Comprehensive deployment checklists:
- Pre-deployment validation checklist
- Security hardening checklist
- Performance optimization checklist
- Post-deployment verification checklist
- Disaster recovery readiness checklist
- Cost optimization checklist

### **[Deployment Glossary](resources/glossary.md)**
Complete terminology guide:
- Infrastructure terms (VPS, cloud, bare metal)
- Container concepts (Docker, K8s, orchestration)
- CI/CD terminology (pipeline, stages, artifacts)
- Networking terms (load balancer, CDN, DNS)
- Monitoring and observability terms

### **[External References](resources/references.md)**
Curated resource collection:
- Official documentation links
- Platform-specific guides
- Best practice articles
- Community resources
- Tool comparisons
- Learning paths

### **[Deployment Workflows](resources/workflows.md)**
Step-by-step procedures:
- Complete deployment workflow
- CI/CD setup workflow
- Kubernetes deployment workflow
- Database migration workflow
- Security hardening workflow
- Monitoring setup workflow

## Common Deployment Scenarios

### Scenario 1: Small Web Application
**Tech Stack**: Node.js/Python, PostgreSQL, Nginx
**Deployment**: Single VPS with PM2/systemd
**See**: [Simple VPS Deployment](examples/basic/simple-vps-deployment.md)

### Scenario 2: Containerized Application
**Tech Stack**: Any language, Docker, Docker Compose
**Deployment**: Single server or cloud instance
**See**: [Docker Compose Setup](examples/basic/docker-compose-setup.md)

### Scenario 3: Scalable Cloud Application
**Tech Stack**: Microservices, Kubernetes, Cloud provider
**Deployment**: Multi-node cluster with autoscaling
**See**: [Kubernetes Deployment](examples/intermediate/kubernetes-deployment.md)

### Scenario 4: Global Application
**Tech Stack**: Multi-region, CDN, database replication
**Deployment**: Multi-region with traffic management
**See**: [Multi-Region Kubernetes](examples/advanced/multi-region-kubernetes.md)

## Deployment Decision Tree

```
START: What are you deploying?
│
├─ Simple app, low traffic → VPS Deployment
│  └─ See: Basic VPS Deployment example
│
├─ Containerized app, moderate traffic → Container Platform
│  ├─ Single server → Docker Compose
│  └─ Multiple servers → Kubernetes
│
├─ Microservices, high traffic → Orchestration Platform
│  ├─ Self-managed → Kubernetes
│  └─ Managed service → ECS, GKE, AKS
│
└─ Serverless functions → Function Platform
   └─ AWS Lambda, Cloud Functions, Azure Functions
```

## Getting Started Path

### Step 1: Choose Your Deployment Strategy
Start with **[Core Concepts](docs/core-concepts.md)** to understand deployment fundamentals and select the right approach for your application.

### Step 2: Learn Basic Deployment
Work through **basic examples**:
1. [Simple VPS Deployment](examples/basic/simple-vps-deployment.md) - Manual deployment
2. [Docker Containerization](examples/basic/docker-containerization.md) - Container basics
3. [Docker Compose Setup](examples/basic/docker-compose-setup.md) - Multi-container apps

### Step 3: Implement CI/CD
Move to **intermediate examples**:
1. [GitHub Actions CI/CD](examples/intermediate/github-actions-cicd.md) - Automated pipeline
2. [Kubernetes Deployment](examples/intermediate/kubernetes-deployment.md) - Container orchestration
3. [AWS EC2 Deployment](examples/intermediate/aws-ec2-deployment.md) - Cloud deployment

### Step 4: Master Advanced Patterns
Explore **advanced examples**:
1. [Multi-Region Kubernetes](examples/advanced/multi-region-kubernetes.md) - Global deployment
2. [GitOps with ArgoCD](examples/advanced/gitops-argocd.md) - Declarative automation
3. [Blue-Green Deployment](examples/advanced/blue-green-deployment.md) - Zero-downtime

### Step 5: Use Production Templates
Start with **templates** for your use case:
- Small project → [Basic Deployment Template](templates/basic-deployment-template.md)
- Production app → [Production Deployment Template](templates/production-deployment-template.md)
- Enterprise scale → [Kubernetes Production Template](templates/kubernetes-production-template.md)

## Platform-Specific Guides

### Cloud Platforms
- **AWS**: EC2, ECS, EKS, Lambda, Elastic Beanstalk - See [AWS EC2 Deployment](examples/intermediate/aws-ec2-deployment.md)
- **Google Cloud**: GCE, GKE, Cloud Run - See [Kubernetes Deployment](examples/intermediate/kubernetes-deployment.md)
- **Azure**: VMs, AKS, App Service - See [Core Concepts](docs/core-concepts.md)
- **DigitalOcean**: Droplets, Kubernetes - See [Simple VPS Deployment](examples/basic/simple-vps-deployment.md)

### Container Orchestration
- **Kubernetes**: Self-managed and managed clusters - See [Kubernetes Deployment](examples/intermediate/kubernetes-deployment.md)
- **Docker Swarm**: Simple orchestration - See [Patterns](docs/patterns.md)
- **AWS ECS**: Container service - See [Advanced Topics](docs/advanced-topics.md)
- **Nomad**: HashiCorp orchestration - See [Patterns](docs/patterns.md)

### Platform Services
- **Heroku**: Simple PaaS - See [Core Concepts](docs/core-concepts.md)
- **Vercel**: Frontend deployment - See [Best Practices](docs/best-practices.md)
- **Netlify**: Jamstack hosting - See [Best Practices](docs/best-practices.md)
- **Railway**: Modern PaaS - See [Core Concepts](docs/core-concepts.md)

## Security & Compliance

### Security Essentials
- SSL/TLS certificate management
- Secret management (Vault, AWS Secrets Manager)
- Network security and firewalls
- Container security scanning
- Access control and authentication
- Audit logging and compliance

**See**: [Best Practices - Security](docs/best-practices.md#security-hardening)

### Compliance Frameworks
- SOC 2 compliance setup
- GDPR data protection
- HIPAA for healthcare
- PCI-DSS for payments
- ISO 27001 standards

**See**: [Advanced Topics - Compliance](docs/advanced-topics.md#compliance-automation)

## Monitoring & Observability

### Essential Monitoring
```yaml
# Complete observability stack
monitoring:
  metrics: Prometheus + Grafana
  logs: ELK Stack or Loki
  traces: Jaeger or Tempo
  alerts: Alertmanager + PagerDuty
  uptime: UptimeRobot or Pingdom
  apm: DataDog or New Relic
```

**See**: [Monitoring Setup Workflow](resources/workflows.md#monitoring-setup)

## Cost Optimization

### Cost Control Strategies
1. **Right-sizing**: Match resources to actual needs
2. **Auto-scaling**: Scale down during low traffic
3. **Spot instances**: Use for non-critical workloads
4. **Reserved capacity**: Commit for predictable workloads
5. **Resource tagging**: Track costs by project/team
6. **Storage lifecycle**: Archive old data to cheaper storage

**See**: [Best Practices - Cost Optimization](docs/best-practices.md#cost-optimization)

## Disaster Recovery

### Recovery Strategies
- **RTO** (Recovery Time Objective): Target recovery time
- **RPO** (Recovery Point Objective): Maximum acceptable data loss
- **Backup strategies**: Automated, tested, versioned
- **Failover procedures**: Documented, practiced, automated
- **Multi-region**: Active-active or active-passive

**See**: [Core Concepts - Disaster Recovery](docs/core-concepts.md#disaster-recovery-planning)

## Team Collaboration

### Deployment Roles
- **Developers**: Create deployment configurations
- **DevOps Engineers**: Manage infrastructure and automation
- **SREs**: Ensure reliability and performance
- **Security Team**: Validate security and compliance
- **Platform Team**: Maintain deployment platforms

### Collaboration Tools
- **GitOps**: Git as source of truth for infrastructure
- **ChatOps**: Deploy and manage via Slack/Teams
- **Runbooks**: Documented procedures for common tasks
- **Post-mortems**: Learn from incidents and improve

**See**: [Best Practices - Team Collaboration](docs/best-practices.md#team-collaboration)

## Quick Reference Commands

### Docker
```bash
# Build and tag image
docker build -t myapp:v1.0 .

# Run container
docker run -d -p 8080:8080 myapp:v1.0

# Push to registry
docker push myregistry/myapp:v1.0
```

### Kubernetes
```bash
# Deploy application
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -n production

# Scale deployment
kubectl scale deployment myapp --replicas=5
```

### Terraform
```bash
# Initialize and plan
terraform init
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

## Next Steps

1. **Start Learning**: Read [Core Concepts](docs/core-concepts.md) to understand fundamentals
2. **Practice**: Work through [Basic Examples](examples/basic/) hands-on
3. **Apply Best Practices**: Review [Best Practices](docs/best-practices.md) guide
4. **Use Templates**: Adapt [Templates](templates/) to your needs
5. **Go Advanced**: Explore [Advanced Topics](docs/advanced-topics.md) for complex scenarios

## Support & Community

### Getting Help
- Review [Troubleshooting Guide](docs/troubleshooting.md) for common issues
- Check [Glossary](resources/glossary.md) for terminology
- Explore [References](resources/references.md) for official documentation
- Follow [Workflows](resources/workflows.md) for step-by-step guidance

### Continuous Improvement
- Keep deployment configurations in version control
- Document custom procedures and lessons learned
- Automate repetitive tasks
- Regularly review and update security
- Monitor costs and optimize resources
- Practice disaster recovery procedures

---

**Ready to deploy?** Start with the [Simple VPS Deployment](examples/basic/simple-vps-deployment.md) example or choose a [template](templates/) that matches your needs!
