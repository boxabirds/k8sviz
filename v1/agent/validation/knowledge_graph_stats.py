#!/usr/bin/env python3
"""
Knowledge Graph Statistics

This script analyzes the Kubernetes knowledge graph and provides statistics
about the concepts, relationships, and coverage.
"""

import re
from collections import defaultdict
from typing import Dict, Set, Tuple


def parse_turtle_file(filename: str) -> Dict[str, Set[str]]:
    """Parse Turtle file and extract statistics."""
    stats = defaultdict(set)
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract classes
    class_pattern = r'(k8s:\w+)\s+a\s+owl:Class'
    for match in re.finditer(class_pattern, content):
        stats['classes'].add(match.group(1))
    
    # Extract properties
    property_patterns = [
        r'(k8s:\w+)\s+a\s+owl:ObjectProperty',
        r'(k8s:\w+)\s+a\s+owl:DatatypeProperty'
    ]
    for pattern in property_patterns:
        for match in re.finditer(pattern, content):
            stats['properties'].add(match.group(1))
    
    # Extract specific resource types
    workload_pattern = r'(k8s:\w+)\s+.*?rdfs:subClassOf\s+k8s:WorkloadResource'
    for match in re.finditer(workload_pattern, content, re.DOTALL):
        stats['workload_resources'].add(match.group(1))
    
    # Extract constraints
    constraint_pattern = r'(k8s:\w+Constraint)\s+a\s+owl:Class'
    for match in re.finditer(constraint_pattern, content):
        stats['constraints'].add(match.group(1))
    
    # Extract best practices
    practice_pattern = r'(k8s:\w+)\s+a\s+k8s:BestPractice'
    for match in re.finditer(practice_pattern, content):
        stats['best_practices'].add(match.group(1))
    
    # Extract service types
    service_type_pattern = r'(k8s:\w+)\s+a\s+k8s:ServiceType'
    for match in re.finditer(service_type_pattern, content):
        stats['service_types'].add(match.group(1))
    
    # Extract probe types
    probe_pattern = r'(k8s:\w+Probe)\s+a\s+.*?[owl:Class|k8s:ProbeType]'
    for match in re.finditer(probe_pattern, content):
        stats['probe_types'].add(match.group(1))
    
    # Extract RBAC resources
    rbac_pattern = r'(k8s:(?:Role|Binding|Account)\w*)\s+a\s+owl:Class'
    for match in re.finditer(rbac_pattern, content):
        stats['rbac_resources'].add(match.group(1))
    
    # Extract volume types
    volume_pattern = r'(k8s:\w+)\s+a\s+k8s:VolumeType'
    for match in re.finditer(volume_pattern, content):
        stats['volume_types'].add(match.group(1))
    
    # Count provenance links
    prov_pattern = r'prov:wasDerivedFrom\s+<([^>]+)>'
    stats['provenance_links'] = set(re.findall(prov_pattern, content))
    
    return dict(stats)


def print_statistics(stats: Dict[str, Set[str]]) -> None:
    """Print formatted statistics."""
    print("=" * 60)
    print("KUBERNETES KNOWLEDGE GRAPH STATISTICS")
    print("=" * 60)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Classes: {len(stats.get('classes', []))}")
    print(f"   Total Properties: {len(stats.get('properties', []))}")
    print(f"   Total Constraints: {len(stats.get('constraints', []))}")
    print(f"   Total Best Practices: {len(stats.get('best_practices', []))}")
    print(f"   Provenance Links: {len(stats.get('provenance_links', []))}")
    
    print(f"\n🚀 WORKLOAD RESOURCES ({len(stats.get('workload_resources', []))}):")
    for resource in sorted(stats.get('workload_resources', [])):
        print(f"   - {resource.replace('k8s:', '')}")
    
    print(f"\n🌐 SERVICE TYPES ({len(stats.get('service_types', []))}):")
    for svc_type in sorted(stats.get('service_types', [])):
        print(f"   - {svc_type.replace('k8s:', '')}")
    
    print(f"\n🔍 PROBE TYPES ({len(stats.get('probe_types', []))}):")
    for probe in sorted(stats.get('probe_types', [])):
        print(f"   - {probe.replace('k8s:', '')}")
    
    print(f"\n🔐 RBAC RESOURCES ({len(stats.get('rbac_resources', []))}):")
    for rbac in sorted(stats.get('rbac_resources', [])):
        print(f"   - {rbac.replace('k8s:', '')}")
    
    print(f"\n💾 VOLUME TYPES ({len(stats.get('volume_types', []))}):")
    for vol in sorted(stats.get('volume_types', [])):
        print(f"   - {vol.replace('k8s:', '')}")
    
    print(f"\n⚠️  CONSTRAINTS ({len(stats.get('constraints', []))}):")
    for constraint in sorted(stats.get('constraints', [])):
        print(f"   - {constraint.replace('k8s:', '')}")
    
    print(f"\n✅ BEST PRACTICES ({len(stats.get('best_practices', []))}):")
    for practice in sorted(stats.get('best_practices', [])):
        print(f"   - {practice.replace('k8s:', '')}")
    
    # Show coverage analysis
    print(f"\n📈 COVERAGE ANALYSIS:")
    core_resources = {
        'Pod', 'Deployment', 'Service', 'ConfigMap', 'Secret',
        'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Ingress',
        'PersistentVolume', 'PersistentVolumeClaim', 'Namespace',
        'ServiceAccount', 'Role', 'RoleBinding', 'ClusterRole',
        'ClusterRoleBinding', 'NetworkPolicy', 'ResourceQuota',
        'LimitRange', 'HorizontalPodAutoscaler'
    }
    
    covered = set()
    for cls in stats.get('classes', []):
        cls_name = cls.replace('k8s:', '')
        if cls_name in core_resources:
            covered.add(cls_name)
    
    print(f"   Core Resources Covered: {len(covered)}/{len(core_resources)} ({len(covered)*100/len(core_resources):.1f}%)")
    
    missing = core_resources - covered
    if missing:
        print(f"   Missing Core Resources:")
        for res in sorted(missing):
            print(f"      - {res}")
    
    # Sample provenance links
    print(f"\n🔗 SAMPLE PROVENANCE LINKS:")
    for i, link in enumerate(sorted(list(stats.get('provenance_links', []))[:5])):
        print(f"   {i+1}. {link}")
    if len(stats.get('provenance_links', [])) > 5:
        print(f"   ... and {len(stats.get('provenance_links', [])) - 5} more")


def main():
    """Main function."""
    import sys
    import os
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Default to the knowledge graph file
        filename = os.path.join(os.path.dirname(__file__), '../knowledge/kubernetes.ttl')
    
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    
    print(f"Analyzing: {filename}\n")
    stats = parse_turtle_file(filename)
    print_statistics(stats)


if __name__ == '__main__':
    main()