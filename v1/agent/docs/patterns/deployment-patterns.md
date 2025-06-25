# Kubernetes Deployment Patterns

## Overview
This document describes common patterns for deploying applications in Kubernetes, based on the knowledge graph relationships and best practices.

## Basic Deployment Pattern

### Single Container Pod
The simplest pattern deploys a single container in a Pod managed by a Deployment.

**Key Components:**
- Deployment (manages ReplicaSets)
- ReplicaSet (manages Pods)
- Pod (runs container)
- Service (exposes Pods)

**Best Practices:**
- Always use Deployments instead of creating Pods directly
- Set resource requests and limits
- Configure liveness and readiness probes
- Use labels for organization and selection

### Multi-Replica Deployment
For high availability, deploy multiple replicas of your application.

**Key Considerations:**
- Set appropriate replica count (minimum 2 for HA)
- Use Pod anti-affinity to spread across nodes
- Configure horizontal pod autoscaling
- Ensure stateless design

## StatefulSet Pattern

### When to Use
- Applications requiring stable network identities
- Ordered deployment and scaling
- Persistent storage per Pod

### Key Differences from Deployment
- Pods have stable, persistent identifiers
- Ordered, graceful deployment and scaling
- Stable persistent storage

### Common Use Cases
- Databases (PostgreSQL, MySQL, MongoDB)
- Message queues (Kafka, RabbitMQ)
- Distributed systems requiring stable identities

## Service Exposure Patterns

### Internal Services (ClusterIP)
Default service type for internal communication.

**Use Cases:**
- Backend services
- Databases
- Internal APIs

### External Services

#### NodePort
Exposes service on each node's IP at a static port.

**Use Cases:**
- Development environments
- Simple external access
- When LoadBalancer not available

#### LoadBalancer
Provisions cloud provider load balancer.

**Use Cases:**
- Production external services
- When using cloud providers
- High-traffic applications

#### Ingress
HTTP/HTTPS routing with single entry point.

**Use Cases:**
- Multiple services behind single domain
- SSL/TLS termination
- Path-based routing
- Virtual hosting

## Configuration Management

### ConfigMaps
For non-sensitive configuration data.

**Best Practices:**
- Separate configuration from code
- Use for environment-specific settings
- Mount as files or environment variables

### Secrets
For sensitive data like passwords and API keys.

**Best Practices:**
- Never commit secrets to version control
- Use RBAC to limit access
- Consider external secret management tools
- Enable encryption at rest

## Health Check Patterns

### Startup Probe
For slow-starting applications.

**Configuration:**
```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

### Liveness Probe
Detects when to restart containers.

**Configuration:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Readiness Probe
Determines when container can receive traffic.

**Configuration:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Scaling Patterns

### Horizontal Pod Autoscaling
Automatically scale based on metrics.

**Metrics:**
- CPU utilization
- Memory utilization
- Custom metrics

**Best Practices:**
- Set appropriate min/max replicas
- Configure scaling behavior
- Test scaling thresholds

### Vertical Pod Autoscaling
Adjust resource requests/limits automatically.

**Use Cases:**
- Right-sizing containers
- Handling variable workloads
- Cost optimization

## Security Patterns

### Pod Security Context
Configure security settings for Pods.

**Key Settings:**
- `runAsNonRoot: true`
- `readOnlyRootFilesystem: true`
- `runAsUser: 1000`

### RBAC Pattern
Implement least privilege access.

**Components:**
1. ServiceAccount (identity)
2. Role/ClusterRole (permissions)
3. RoleBinding/ClusterRoleBinding (assignment)

### Network Policies
Control traffic between Pods.

**Types:**
- Ingress rules (incoming traffic)
- Egress rules (outgoing traffic)

## Storage Patterns

### Ephemeral Storage
Using emptyDir for temporary data.

**Use Cases:**
- Cache
- Temporary processing
- Shared data between containers

### Persistent Storage
Using PersistentVolumeClaims.

**Patterns:**
- Static provisioning
- Dynamic provisioning with StorageClasses
- Volume snapshots for backups

## Multi-Container Patterns

### Sidecar Pattern
Helper container alongside main container.

**Use Cases:**
- Log shipping
- Monitoring agents
- Proxy containers

### Init Container Pattern
Containers that run before main containers.

**Use Cases:**
- Database migrations
- Configuration setup
- Dependency checks

### Ambassador Pattern
Proxy container for external services.

**Use Cases:**
- Service mesh integration
- API gateway functionality
- Protocol translation

## Batch Processing Patterns

### Job Pattern
For one-time tasks.

**Configuration:**
- Set completions and parallelism
- Configure backoff limits
- Use appropriate restart policy

### CronJob Pattern
For scheduled tasks.

**Use Cases:**
- Backups
- Report generation
- Cleanup tasks

## Resource Management Patterns

### ResourceQuota
Limit resource consumption per namespace.

**Quotas:**
- CPU and memory limits
- Object counts
- Storage limits

### LimitRange
Set default and maximum resource limits.

**Benefits:**
- Prevent resource exhaustion
- Ensure fair resource distribution
- Cost control

## Deployment Strategies

### Rolling Update
Default strategy for Deployments.

**Configuration:**
- maxSurge: additional Pods during update
- maxUnavailable: Pods that can be unavailable

### Recreate
Terminate all Pods before creating new ones.

**Use Cases:**
- Development environments
- When running multiple versions isn't possible

### Blue-Green Deployment
Two identical environments, switch traffic.

**Implementation:**
- Use labels to differentiate versions
- Update Service selector to switch

### Canary Deployment
Gradual rollout to subset of users.

**Implementation:**
- Deploy new version with fewer replicas
- Use Ingress or Service Mesh for traffic splitting
- Monitor metrics before full rollout