# Kubernetes Knowledge Graph

A comprehensive RDF knowledge graph representing Kubernetes concepts, resources, and relationships for generating Kubernetes configurations from natural language.

## Overview

This project provides a complete semantic model of Kubernetes in Turtle (RDF) format, enabling intelligent systems to understand and generate valid Kubernetes configurations. The knowledge graph includes:

- **Core Resources**: Pods, Deployments, Services, StatefulSets, etc.
- **Relationships**: How resources connect and depend on each other
- **Constraints**: Rules and limitations for valid configurations
- **Best Practices**: Recommended patterns and approaches
- **Provenance**: Links to official Kubernetes documentation for each fact

## Directory Structure

```
agent/
├── knowledge/
│   └── kubernetes.ttl          # Main knowledge graph in Turtle format
├── tests/
│   ├── queries/               # SPARQL queries for different scenarios
│   └── expected/              # Expected YAML outputs for test queries
├── examples/                  # Complete example configurations
├── docs/
│   └── patterns/             # Documentation of common patterns
└── validation/               # Scripts to validate generated YAML
```

## Knowledge Graph Structure

The knowledge graph uses the following namespaces:

- `k8s:` - Kubernetes ontology (http://kubernetes.io/ontology#)
- `rdfs:` - RDF Schema
- `owl:` - Web Ontology Language
- `prov:` - PROV-O for provenance

### Core Classes

- **Workload Resources**: Deployment, StatefulSet, DaemonSet, Job, CronJob
- **Networking**: Service, Ingress, NetworkPolicy, Endpoints
- **Storage**: PersistentVolume, PersistentVolumeClaim, StorageClass
- **Configuration**: ConfigMap, Secret
- **Security**: Role, ClusterRole, ServiceAccount, SecurityContext
- **Scaling**: HorizontalPodAutoscaler, VerticalPodAutoscaler

### Key Relationships

- `k8s:creates` - Resource creation hierarchy
- `k8s:manages` - Lifecycle management
- `k8s:references` - Resource references
- `k8s:selectsPod` - Label-based selection
- `k8s:inNamespace` - Namespace scoping

## Usage

### Querying the Knowledge Graph

Use SPARQL to query the knowledge graph for specific information:

```sparql
PREFIX k8s: <http://kubernetes.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?comment
WHERE {
  ?resource a k8s:WorkloadResource ;
            rdfs:comment ?comment .
}
```

### Validation

Validate generated YAML against knowledge graph rules:

```bash
python agent/validation/validate_k8s_yaml.py myconfig.yaml
```

The validator checks:
- Required fields and structure
- Constraint compliance
- Best practice adherence
- Resource relationships

### Test Scenarios

The `tests/` directory contains queries and expected outputs for common scenarios:

1. **Basic Deployment**: Simple web application with replicas
2. **StatefulSet with Storage**: Database deployment with persistent volumes
3. **Service and Ingress**: External application exposure
4. **Autoscaling**: HPA configuration
5. **RBAC**: Role-based access control setup

## Examples

### Complete Microservices Deployment

See `examples/microservices-deployment.yaml` for a production-ready example including:

- Multi-tier application (frontend, API, database, cache)
- Service discovery and networking
- Persistent storage
- Security policies
- Resource management
- Autoscaling
- Monitoring setup

## Patterns Documentation

The `docs/patterns/` directory contains detailed documentation on:

- Deployment strategies
- Service exposure patterns
- Configuration management
- Security patterns
- Scaling approaches
- Storage patterns
- Multi-container patterns

## Best Practices Encoded

The knowledge graph enforces Kubernetes best practices:

1. **Resource Management**: Always set resource requests and limits
2. **Health Checks**: Configure liveness and readiness probes
3. **Security**: Use security contexts and RBAC
4. **High Availability**: Deploy multiple replicas with anti-affinity
5. **Configuration**: Separate config from code using ConfigMaps/Secrets

## Constraints and Rules

Key constraints enforced by the knowledge graph:

- Pod names must follow DNS subdomain rules
- ConfigMaps limited to 1 MiB
- Jobs only support Never or OnFailure restart policies
- CronJob schedule field is required
- StatefulSets require serviceName
- HPA doesn't apply to DaemonSets
- RBAC permissions are additive only

## Extending the Knowledge Graph

To add new concepts:

1. Define the class with appropriate superclass
2. Add properties with domains and ranges
3. Document with rdfs:comment
4. Include provenance with prov:wasDerivedFrom
5. Define relationships to existing concepts
6. Add constraints and best practices

Example:
```turtle
k8s:MyNewResource a owl:Class ;
    rdfs:subClassOf k8s:APIObject ;
    rdfs:label "My New Resource"@en ;
    rdfs:comment "Description of the resource"@en ;
    prov:wasDerivedFrom <https://kubernetes.io/docs/...> .
```

## Integration with AI Systems

This knowledge graph is designed for integration with:

- Natural language processing systems
- Configuration generators
- Validation tools
- Documentation systems
- Training datasets

The semantic model enables AI systems to:
- Understand Kubernetes concepts and relationships
- Generate valid configurations from descriptions
- Validate existing configurations
- Suggest improvements based on best practices
- Explain configuration decisions with provenance

## Contributing

When contributing to the knowledge graph:

1. Ensure all facts have provenance links
2. Follow existing naming conventions
3. Add test cases for new patterns
4. Update documentation
5. Validate changes don't break existing queries

## License

This knowledge graph is based on official Kubernetes documentation and follows the same licensing terms as the Kubernetes project.

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [RDF 1.1 Turtle](https://www.w3.org/TR/turtle/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)