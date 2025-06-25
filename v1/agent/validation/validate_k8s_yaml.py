#!/usr/bin/env python3
"""
Kubernetes YAML Validator

This script validates Kubernetes YAML configurations against the rules
and constraints defined in the knowledge graph.
"""

import yaml
import sys
import argparse
from typing import Dict, List, Any, Tuple
import re


class KubernetesValidator:
    """Validates Kubernetes configurations against knowledge graph rules."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filename: str) -> bool:
        """Validate a Kubernetes YAML file."""
        try:
            with open(filename, 'r') as f:
                docs = list(yaml.safe_load_all(f))
            
            for doc in docs:
                if doc:
                    self.validate_resource(doc)
            
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Failed to parse YAML: {e}")
            return False
    
    def validate_resource(self, resource: Dict[str, Any]) -> None:
        """Validate a single Kubernetes resource."""
        kind = resource.get('kind', '')
        
        # Route to specific validators
        validators = {
            'Deployment': self.validate_deployment,
            'StatefulSet': self.validate_statefulset,
            'Service': self.validate_service,
            'Job': self.validate_job,
            'CronJob': self.validate_cronjob,
            'ConfigMap': self.validate_configmap,
            'Secret': self.validate_secret,
            'PersistentVolumeClaim': self.validate_pvc,
            'HorizontalPodAutoscaler': self.validate_hpa,
            'NetworkPolicy': self.validate_networkpolicy,
            'Ingress': self.validate_ingress,
            'Role': self.validate_role,
            'RoleBinding': self.validate_rolebinding,
        }
        
        # Common validations
        self.validate_metadata(resource)
        
        # Kind-specific validation
        validator = validators.get(kind)
        if validator:
            validator(resource)
    
    def validate_metadata(self, resource: Dict[str, Any]) -> None:
        """Validate metadata fields."""
        metadata = resource.get('metadata', {})
        
        # Check required fields
        if not metadata.get('name'):
            self.errors.append(f"{resource.get('kind')} missing metadata.name")
        
        # Validate name format (DNS subdomain)
        name = metadata.get('name', '')
        if name and not re.match(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$', name):
            self.errors.append(f"Invalid name '{name}': must be valid DNS subdomain")
    
    def validate_deployment(self, deployment: Dict[str, Any]) -> None:
        """Validate Deployment specific rules."""
        spec = deployment.get('spec', {})
        
        # Check replicas
        replicas = spec.get('replicas', 1)
        if replicas < 1:
            self.errors.append("Deployment replicas must be >= 1")
        
        # Validate selector
        if not spec.get('selector'):
            self.errors.append("Deployment must have selector")
        
        # Validate pod template
        template = spec.get('template', {})
        if not template:
            self.errors.append("Deployment must have pod template")
        else:
            self.validate_pod_template(template)
        
        # Best practice: multiple replicas for HA
        if replicas == 1:
            self.warnings.append("Consider using multiple replicas for high availability")
    
    def validate_statefulset(self, statefulset: Dict[str, Any]) -> None:
        """Validate StatefulSet specific rules."""
        spec = statefulset.get('spec', {})
        
        # Check serviceName
        if not spec.get('serviceName'):
            self.errors.append("StatefulSet must have serviceName")
        
        # Validate pod template
        template = spec.get('template', {})
        if template:
            self.validate_pod_template(template)
        
        # Check volumeClaimTemplates for persistent storage
        if not spec.get('volumeClaimTemplates'):
            self.warnings.append("StatefulSet typically uses volumeClaimTemplates for persistent storage")
    
    def validate_pod_template(self, template: Dict[str, Any]) -> None:
        """Validate pod template."""
        spec = template.get('spec', {})
        containers = spec.get('containers', [])
        
        if not containers:
            self.errors.append("Pod must have at least one container")
            return
        
        for i, container in enumerate(containers):
            self.validate_container(container, i)
        
        # Check for security context
        if not spec.get('securityContext') and not any(c.get('securityContext') for c in containers):
            self.warnings.append("Consider adding security context for defense in depth")
    
    def validate_container(self, container: Dict[str, Any], index: int) -> None:
        """Validate container configuration."""
        # Check required fields
        if not container.get('name'):
            self.errors.append(f"Container {index} missing name")
        
        if not container.get('image'):
            self.errors.append(f"Container {container.get('name', index)} missing image")
        
        # Check resource limits
        resources = container.get('resources', {})
        if not resources.get('requests'):
            self.warnings.append(f"Container {container.get('name', index)} missing resource requests")
        if not resources.get('limits'):
            self.warnings.append(f"Container {container.get('name', index)} missing resource limits")
        
        # Check probes
        if not container.get('livenessProbe'):
            self.warnings.append(f"Container {container.get('name', index)} missing liveness probe")
        if not container.get('readinessProbe'):
            self.warnings.append(f"Container {container.get('name', index)} missing readiness probe")
        
        # Validate probes
        for probe_type in ['livenessProbe', 'readinessProbe', 'startupProbe']:
            probe = container.get(probe_type)
            if probe:
                self.validate_probe(probe, probe_type, container.get('name', index))
    
    def validate_probe(self, probe: Dict[str, Any], probe_type: str, container_name: str) -> None:
        """Validate probe configuration."""
        # Check probe type
        probe_types = ['httpGet', 'tcpSocket', 'exec', 'grpc']
        if not any(probe.get(pt) for pt in probe_types):
            self.errors.append(f"{probe_type} for {container_name} must define probe type")
        
        # Validate successThreshold for liveness and startup
        if probe_type in ['livenessProbe', 'startupProbe']:
            if probe.get('successThreshold', 1) != 1:
                self.errors.append(f"{probe_type} successThreshold must be 1")
    
    def validate_service(self, service: Dict[str, Any]) -> None:
        """Validate Service configuration."""
        spec = service.get('spec', {})
        
        # Check selector for non-headless services
        if spec.get('clusterIP') != 'None' and not spec.get('selector'):
            self.warnings.append("Service without selector won't route to any pods")
        
        # Check ports
        if not spec.get('ports'):
            self.errors.append("Service must define at least one port")
    
    def validate_job(self, job: Dict[str, Any]) -> None:
        """Validate Job configuration."""
        spec = job.get('spec', {})
        template = spec.get('template', {})
        
        # Check restart policy
        restart_policy = template.get('spec', {}).get('restartPolicy')
        if restart_policy not in ['Never', 'OnFailure']:
            self.errors.append("Job must have restartPolicy of Never or OnFailure")
    
    def validate_cronjob(self, cronjob: Dict[str, Any]) -> None:
        """Validate CronJob configuration."""
        spec = cronjob.get('spec', {})
        
        # Check schedule
        if not spec.get('schedule'):
            self.errors.append("CronJob must have schedule field")
        
        # Validate cron expression (basic check)
        schedule = spec.get('schedule', '')
        if schedule and len(schedule.split()) != 5:
            self.errors.append("CronJob schedule must be valid cron expression")
    
    def validate_configmap(self, configmap: Dict[str, Any]) -> None:
        """Validate ConfigMap configuration."""
        # Check data size (1 MiB limit)
        data = configmap.get('data', {})
        binary_data = configmap.get('binaryData', {})
        
        total_size = sum(len(str(v)) for v in data.values())
        total_size += sum(len(str(v)) for v in binary_data.values())
        
        if total_size > 1048576:  # 1 MiB
            self.errors.append("ConfigMap data cannot exceed 1 MiB")
    
    def validate_secret(self, secret: Dict[str, Any]) -> None:
        """Validate Secret configuration."""
        # Similar size check as ConfigMap
        data = secret.get('data', {})
        string_data = secret.get('stringData', {})
        
        if data and string_data:
            self.warnings.append("Secret has both data and stringData fields")
    
    def validate_pvc(self, pvc: Dict[str, Any]) -> None:
        """Validate PersistentVolumeClaim."""
        spec = pvc.get('spec', {})
        
        # Check access modes
        access_modes = spec.get('accessModes', [])
        if not access_modes:
            self.errors.append("PVC must specify accessModes")
        
        # Check storage request
        resources = spec.get('resources', {})
        if not resources.get('requests', {}).get('storage'):
            self.errors.append("PVC must specify storage request")
    
    def validate_hpa(self, hpa: Dict[str, Any]) -> None:
        """Validate HorizontalPodAutoscaler."""
        spec = hpa.get('spec', {})
        
        # Check scale target
        if not spec.get('scaleTargetRef'):
            self.errors.append("HPA must have scaleTargetRef")
        
        # Check min/max replicas
        min_replicas = spec.get('minReplicas', 1)
        max_replicas = spec.get('maxReplicas')
        
        if not max_replicas:
            self.errors.append("HPA must specify maxReplicas")
        elif max_replicas < min_replicas:
            self.errors.append("HPA maxReplicas must be >= minReplicas")
        
        # Check metrics
        if not spec.get('metrics') and not spec.get('targetCPUUtilizationPercentage'):
            self.errors.append("HPA must specify metrics or targetCPUUtilizationPercentage")
    
    def validate_networkpolicy(self, netpol: Dict[str, Any]) -> None:
        """Validate NetworkPolicy."""
        spec = netpol.get('spec', {})
        
        # Check pod selector
        if 'podSelector' not in spec:
            self.errors.append("NetworkPolicy must have podSelector")
        
        # Check policy types
        policy_types = spec.get('policyTypes', [])
        if not policy_types:
            self.warnings.append("NetworkPolicy should specify policyTypes")
    
    def validate_ingress(self, ingress: Dict[str, Any]) -> None:
        """Validate Ingress."""
        spec = ingress.get('spec', {})
        
        # Check rules
        rules = spec.get('rules', [])
        if not rules:
            self.errors.append("Ingress should have at least one rule")
        
        # Validate paths
        for rule in rules:
            http = rule.get('http', {})
            for path in http.get('paths', []):
                if not path.get('pathType'):
                    self.errors.append("Ingress path must have pathType")
                
                path_type = path.get('pathType')
                if path_type not in ['Exact', 'Prefix', 'ImplementationSpecific']:
                    self.errors.append(f"Invalid pathType: {path_type}")
    
    def validate_role(self, role: Dict[str, Any]) -> None:
        """Validate Role/ClusterRole."""
        rules = role.get('rules', [])
        
        if not rules:
            self.warnings.append(f"{role.get('kind')} has no rules")
        
        for rule in rules:
            if not rule.get('verbs'):
                self.errors.append(f"{role.get('kind')} rule missing verbs")
            
            # Check for overly permissive rules
            if '*' in rule.get('verbs', []):
                self.warnings.append(f"{role.get('kind')} uses wildcard verbs - follow least privilege")
    
    def validate_rolebinding(self, binding: Dict[str, Any]) -> None:
        """Validate RoleBinding/ClusterRoleBinding."""
        # Check roleRef
        if not binding.get('roleRef'):
            self.errors.append(f"{binding.get('kind')} must have roleRef")
        
        # Check subjects
        if not binding.get('subjects'):
            self.errors.append(f"{binding.get('kind')} must have subjects")
    
    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print("ERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Validation passed - no issues found")
        elif not self.errors:
            print("\n✅ Validation passed with warnings")
        else:
            print("\n❌ Validation failed")


def main():
    parser = argparse.ArgumentParser(description='Validate Kubernetes YAML against knowledge graph rules')
    parser.add_argument('files', nargs='+', help='YAML files to validate')
    parser.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    validator = KubernetesValidator()
    all_valid = True
    
    for file in args.files:
        print(f"\nValidating {file}...")
        validator.errors = []
        validator.warnings = []
        
        valid = validator.validate_file(file)
        validator.print_results()
        
        if not valid or (args.strict and validator.warnings):
            all_valid = False
    
    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()