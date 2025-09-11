#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Health Check Utilities

Provides comprehensive health monitoring for Neo4j database instances
across all environments with performance metrics and status reporting.

Issue #266: Comprehensive Neo4j Testing Infrastructure
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .neo4j_manager import Neo4jManager
from .test_operations import TestOperations


@dataclass
class HealthStatus:
    """Health check status data structure."""
    status: str  # healthy, degraded, unhealthy
    response_time_ms: int
    last_test_timestamp: str
    environment: str
    version: Optional[str] = None
    test_operations: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


class HealthChecker:
    """
    Neo4j health monitoring and status reporting.
    
    Provides comprehensive health checks for Neo4j instances including:
    - Basic connectivity testing
    - CRUD operation validation
    - Performance baseline monitoring
    - Status reporting for monitoring systems
    """
    
    def __init__(self, manager: Neo4jManager):
        """
        Initialize health checker.
        
        Args:
            manager: Neo4jManager instance
        """
        self.manager = manager
        self.test_ops = TestOperations(manager)
        self.performance_baseline_ms = 100  # Default baseline
        
    def check_basic_connectivity(self) -> Dict[str, Any]:
        """
        Perform basic Neo4j connectivity check.
        
        Returns:
            Basic connectivity status dictionary
        """
        return self.manager.test_connectivity()
        
    def check_database_operations(self) -> Dict[str, Any]:
        """
        Check database CRUD operations functionality.
        
        Returns:
            CRUD operations test results
        """
        return self.test_ops.test_crud_operations()
        
    def check_performance_baseline(self) -> Dict[str, Any]:
        """
        Check if database performance meets baseline requirements.
        
        Returns:
            Performance test results
        """
        results = {
            'baseline_met': False,
            'response_time_ms': None,
            'baseline_threshold_ms': self.performance_baseline_ms,
            'performance_ratio': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            
            with self.manager.get_session() as session:
                # Simple query to test response time
                session.run("RETURN 1")
                
            response_time = int((time.time() - start_time) * 1000)
            results['response_time_ms'] = response_time
            results['baseline_met'] = response_time <= self.performance_baseline_ms
            results['performance_ratio'] = round(response_time / self.performance_baseline_ms, 2)
            
        except Exception as e:
            results['error'] = str(e)
            
        return results
        
    def get_database_version(self) -> Optional[str]:
        """
        Get Neo4j database version information.
        
        Returns:
            Version string or None if unavailable
        """
        try:
            with self.manager.get_session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                for record in result:
                    if record["name"] == "Neo4j Kernel":
                        return record["versions"][0]
                        
        except Exception:
            pass
            
        return None
        
    def comprehensive_health_check(self, include_crud: bool = True) -> HealthStatus:
        """
        Perform comprehensive health check of Neo4j instance.
        
        Args:
            include_crud: Whether to include CRUD operation tests
            
        Returns:
            HealthStatus object with complete health information
        """
        start_time = time.time()
        warnings = []
        
        # Basic connectivity
        connectivity = self.check_basic_connectivity()
        
        if not connectivity['connected']:
            return HealthStatus(
                status='unhealthy',
                response_time_ms=0,
                last_test_timestamp=datetime.now().isoformat(),
                environment=self.manager.environment,
                error=connectivity.get('error', 'Connection failed'),
                test_operations={'connection': 'failed'}
            )
            
        # Performance check
        performance = self.check_performance_baseline()
        if not performance['baseline_met']:
            warnings.append(f"Performance below baseline: {performance['response_time_ms']}ms > {performance['baseline_threshold_ms']}ms")
            
        # CRUD operations check (optional for production)
        test_operations = {'connection': 'success'}
        
        if include_crud:
            crud_results = self.check_database_operations()
            test_operations.update({
                'read': 'success' if crud_results['read'] else 'failed',
                'write': 'success' if crud_results['create'] else 'failed',
                'update': 'success' if crud_results['update'] else 'failed',
                'delete': 'success' if crud_results['delete'] else 'failed'
            })
            
            # Check if any CRUD operations failed
            if not all(crud_results[op] for op in ['create', 'read', 'update', 'delete']):
                warnings.append("Some CRUD operations failed")
                
        # Determine overall status
        total_time = int((time.time() - start_time) * 1000)
        
        if warnings:
            status = 'degraded'
        else:
            status = 'healthy'
            
        return HealthStatus(
            status=status,
            response_time_ms=total_time,
            last_test_timestamp=datetime.now().isoformat(),
            environment=self.manager.environment,
            version=self.get_database_version(),
            test_operations=test_operations,
            warnings=warnings if warnings else None
        )
        
    def health_check_endpoint(self, include_crud: bool = None) -> Dict[str, Any]:
        """
        Generate health check response suitable for HTTP endpoints.
        
        Args:
            include_crud: Override CRUD testing (default: False for production)
            
        Returns:
            Health check response dictionary
        """
        # Default: no CRUD tests in production for safety
        if include_crud is None:
            include_crud = self.manager.environment != 'production'
            
        health_status = self.comprehensive_health_check(include_crud)
        
        response = asdict(health_status)
        
        # Add additional metadata
        response.update({
            'timestamp': datetime.now().isoformat(),
            'check_type': 'comprehensive' if include_crud else 'basic',
            'neo4j_driver_available': self.manager.config.get('neo4j_available', True)
        })
        
        return response
        
    def monitoring_metrics(self) -> Dict[str, Any]:
        """
        Generate metrics suitable for monitoring systems (Prometheus, etc.).
        
        Returns:
            Metrics dictionary with numerical values
        """
        health_status = self.comprehensive_health_check(include_crud=False)
        
        # Convert status to numerical values for monitoring
        status_values = {
            'healthy': 1,
            'degraded': 0.5,
            'unhealthy': 0
        }
        
        return {
            'neo4j_health_status': status_values.get(health_status.status, 0),
            'neo4j_response_time_ms': health_status.response_time_ms,
            'neo4j_connection_success': 1 if health_status.test_operations.get('connection') == 'success' else 0,
            'neo4j_environment': health_status.environment,
            'neo4j_check_timestamp': int(datetime.now().timestamp())
        }
        
    def export_health_report(self, filepath: str, include_crud: bool = None) -> bool:
        """
        Export detailed health report to file.
        
        Args:
            filepath: Path to save the health report
            include_crud: Whether to include CRUD testing
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            health_data = self.health_check_endpoint(include_crud)
            
            # Add detailed performance information
            health_data['detailed_metrics'] = {
                'performance_baseline_ms': self.performance_baseline_ms,
                'performance_check': self.check_performance_baseline(),
                'connectivity_details': self.check_basic_connectivity()
            }
            
            with open(filepath, 'w') as f:
                json.dump(health_data, f, indent=2)
                
            return True
            
        except Exception as e:
            self.manager._logger.error(f"Failed to export health report: {e}")
            return False