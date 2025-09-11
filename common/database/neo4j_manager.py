#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Connection Manager with Environment Detection

Provides unified Neo4j connection management across development, CI, and production
environments with automatic environment detection and configuration loading.

Issue #266: Comprehensive Neo4j Testing Infrastructure
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

from .config_loader import config_loader


class Neo4jManager:
    """
    Neo4j connection manager with multi-environment support.
    
    Features:
    - Automatic environment detection (dev/CI/prod)
    - Configuration-driven connection management
    - Connection pooling and health monitoring
    - Graceful fallback for testing environments
    """
    
    def __init__(self, environment: Optional[str] = None):
        """
        Initialize Neo4j manager.
        
        Args:
            environment: Explicit environment override (dev, ci, production)
        """
        self.environment = environment or self._detect_environment()
        self.config = self._load_config()
        self.driver: Optional[Driver] = None
        self._logger = logging.getLogger(__name__)
        
    def _detect_environment(self) -> str:
        """
        Detect current environment based on environment variables.
        
        Returns:
            Environment string: 'ci', 'production', or 'development'
        """
        if os.getenv('CI'):
            return 'ci'
        elif os.getenv('PRODUCTION') or os.getenv('NEO4J_PRODUCTION'):
            return 'production'
        else:
            return 'development'
            
    def _load_config(self) -> Dict[str, Any]:
        """
        Load environment-specific Neo4j configuration using improved config loader.
        
        Returns:
            Configuration dictionary with connection parameters
        """
        try:
            # Use improved config loader with inheritance support
            full_config = config_loader.load_config(self.environment)
            return full_config.get('neo4j', {})
        except Exception:
            # Fallback to default configuration
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration based on environment.
        
        Returns:
            Default configuration dictionary
        """
        defaults = {
            'development': {
                'host': 'localhost',
                'port': 7687,
                'database': 'neo4j',
                'auth': {
                    'user': 'neo4j',
                    'password': 'finance123'
                },
                'connection': {
                    'timeout': 30,
                    'max_retry_attempts': 3,
                    'pool_max_size': 50
                }
            },
            'ci': {
                'host': 'localhost',
                'port': 7687,
                'database': 'neo4j',
                'auth': {
                    'user': 'neo4j',
                    'password': 'ci_test_password'
                },
                'connection': {
                    'timeout': 15,
                    'max_retry_attempts': 2,
                    'pool_max_size': 10
                }
            },
            'production': {
                'host': os.getenv('NEO4J_HOST', 'neo4j-prod.internal'),
                'port': int(os.getenv('NEO4J_PORT', '7687')),
                'database': os.getenv('NEO4J_DATABASE', 'finance_prod'),
                'auth': {
                    'user': os.getenv('NEO4J_USER', 'neo4j'),
                    'password': os.getenv('NEO4J_PASSWORD', '')
                },
                'connection': {
                    'timeout': 60,
                    'max_retry_attempts': 5,
                    'pool_max_size': 100
                }
            }
        }
        
        return defaults.get(self.environment, defaults['development'])
        
    def get_connection_uri(self) -> str:
        """
        Build Neo4j connection URI.
        
        Returns:
            Neo4j bolt URI string
        """
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 7687)
        return f"bolt://{host}:{port}"
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not NEO4J_AVAILABLE:
            self._logger.warning("Neo4j driver not available - using mock mode")
            return False
            
        try:
            uri = self.get_connection_uri()
            auth_config = self.config.get('auth', {})
            user = auth_config.get('user', 'neo4j')
            password = auth_config.get('password', '')
            
            self.driver = GraphDatabase.driver(
                uri,
                auth=(user, password),
                max_connection_lifetime=self.config.get('connection', {}).get('timeout', 30)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value == 1:
                    self._logger.info(f"Successfully connected to Neo4j ({self.environment} environment)")
                    return True
                    
        except Exception as e:
            self._logger.error(f"Failed to connect to Neo4j: {e}")
            
        return False
        
    def get_session(self):
        """
        Get Neo4j session for database operations.
        
        Returns:
            Neo4j session or None if not connected
        """
        if not self.driver:
            if not self.connect():
                return None
                
        return self.driver.session(database=self.config.get('database', 'neo4j'))
        
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            self._logger.info("Neo4j connection closed")
            
    def test_connectivity(self) -> Dict[str, Any]:
        """
        Test Neo4j connectivity and return detailed status.
        
        Returns:
            Dictionary with connectivity test results
        """
        result = {
            'environment': self.environment,
            'neo4j_available': NEO4J_AVAILABLE,
            'connected': False,
            'response_time_ms': None,
            'error': None
        }
        
        if not NEO4J_AVAILABLE:
            result['error'] = 'Neo4j driver not installed'
            return result
            
        try:
            import time
            start_time = time.time()
            
            if self.connect():
                with self.get_session() as session:
                    session.run("RETURN 1")
                    
                result['connected'] = True
                result['response_time_ms'] = int((time.time() - start_time) * 1000)
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
        
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_neo4j_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Neo4j configuration for specified environment.
    
    Args:
        environment: Target environment (dev, ci, production)
        
    Returns:
        Neo4j configuration dictionary
    """
    manager = Neo4jManager(environment)
    return manager.config