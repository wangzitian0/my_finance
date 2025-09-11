#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Neo4j Database Infrastructure - Issue #266

Streamlined Neo4j connectivity and testing with environment detection.
Replaces over-engineered 6-module system with essential functionality only.

Core features:
- Neo4j connection management with environment detection
- Basic connectivity testing for CI integration
- Simple CRUD validation
- SSOT compliance
"""

from .neo4j import (
    Neo4jConnectivityResult,
    Neo4jManager,
    get_neo4j_manager,
    test_neo4j_connectivity,
    validate_neo4j_environment,
)

# Backward compatibility aliases
HealthChecker = Neo4jManager  # For existing test compatibility
TestOperations = Neo4jManager  # For existing test compatibility

# Primary exports for simplified usage
__all__ = [
    # Core simplified functionality
    "Neo4jManager",
    "Neo4jConnectivityResult",
    "get_neo4j_manager",
    "test_neo4j_connectivity",
    "validate_neo4j_environment",
    # Backward compatibility
    "HealthChecker",
    "TestOperations",
]
