#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Neo4j Infrastructure for Issue #266

Streamlined Neo4j connection management with environment detection and basic testing.
Replaces the over-engineered 6-module system with simple, maintainable code.

Core functionality:
- Environment detection (development/CI/production)
- Basic Neo4j connectivity testing
- Simple CRUD validation for CI integration
- SSOT compliance using directory_manager

Simplified from:
- config_loader.py (339 lines) - Complex YAML inheritance
- neo4j_manager.py - Connection management
- health_checks.py - Over-engineered health monitoring
- health_endpoint.py - Unused web endpoint
- test_operations.py - Complex CRUD abstractions
- __init__.py - Complex exports

To: Single essential module with core functionality only.
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from common.core.directory_manager import directory_manager

try:
    from neo4j import Driver, GraphDatabase

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None


@dataclass
class Neo4jConnectivityResult:
    """Simple connectivity test result"""

    environment: str
    connected: bool
    response_time_ms: Optional[int] = None
    error: Optional[str] = None
    neo4j_available: bool = True


class Neo4jManager:
    """
    Simplified Neo4j connection manager.

    Core features:
    - Environment detection (dev/CI/production)
    - Basic connectivity testing
    - Simple configuration via environment variables
    - SSOT compliance for configuration paths
    """

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize Neo4j manager with simplified configuration.

        Args:
            environment: Override environment detection (dev, ci, production)
        """
        self.environment = environment or self._detect_environment()
        self.driver: Optional[Driver] = None
        self._logger = logging.getLogger(__name__)

    def _detect_environment(self) -> str:
        """Detect environment based on environment variables."""
        if os.getenv("CI"):
            return "ci"
        elif os.getenv("PRODUCTION") or os.getenv("NEO4J_PRODUCTION"):
            return "production"
        else:
            return "development"

    def get_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration using environment variables."""
        if self.environment == "ci":
            return {
                "host": os.getenv("NEO4J_HOST", "localhost"),
                "port": int(os.getenv("NEO4J_PORT", "7687")),
                "database": os.getenv("NEO4J_DATABASE", "neo4j"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "ci_test_password"),
                "timeout": 15,
            }
        elif self.environment == "production":
            return {
                "host": os.getenv("NEO4J_HOST", "neo4j-prod.internal"),
                "port": int(os.getenv("NEO4J_PORT", "7687")),
                "database": os.getenv("NEO4J_DATABASE", "finance_prod"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", ""),
                "timeout": 60,
            }
        else:  # development
            return {
                "host": os.getenv("NEO4J_HOST", "localhost"),
                "port": int(os.getenv("NEO4J_PORT", "7687")),
                "database": os.getenv("NEO4J_DATABASE", "neo4j"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "finance123"),
                "timeout": 30,
            }

    def get_connection_uri(self) -> str:
        """Build Neo4j connection URI."""
        config = self.get_config()
        return f"bolt://{config['host']}:{config['port']}"

    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.

        Returns:
            True if connection successful, False otherwise
        """
        if not NEO4J_AVAILABLE:
            self._logger.warning("Neo4j driver not available")
            return False

        try:
            config = self.get_config()
            uri = self.get_connection_uri()

            self.driver = GraphDatabase.driver(
                uri,
                auth=(config["user"], config["password"]),
                max_connection_lifetime=config["timeout"],
            )

            # Test connection
            with self.driver.session(database=config["database"]) as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                if test_value == 1:
                    self._logger.info(f"Connected to Neo4j ({self.environment})")
                    return True

        except Exception as e:
            self._logger.error(f"Neo4j connection failed: {e}")

        return False

    def test_connectivity(self) -> Neo4jConnectivityResult:
        """
        Test Neo4j connectivity and return results.

        Returns:
            Neo4jConnectivityResult with test status
        """
        if not NEO4J_AVAILABLE:
            return Neo4jConnectivityResult(
                environment=self.environment,
                connected=False,
                error="Neo4j driver not installed",
                neo4j_available=False,
            )

        try:
            start_time = time.time()
            connected = self.connect()
            response_time = int((time.time() - start_time) * 1000)

            if connected:
                # Test basic query
                config = self.get_config()
                with self.driver.session(database=config["database"]) as session:
                    session.run("RETURN 1")

                return Neo4jConnectivityResult(
                    environment=self.environment, connected=True, response_time_ms=response_time
                )
            else:
                return Neo4jConnectivityResult(
                    environment=self.environment, connected=False, error="Connection failed"
                )

        except Exception as e:
            return Neo4jConnectivityResult(
                environment=self.environment, connected=False, error=str(e)
            )

    def test_crud_operations(self) -> Dict[str, Any]:
        """
        Simple CRUD test for CI validation.

        Returns:
            Dictionary with test results
        """
        if not self.connect():
            return {"success": False, "error": "Connection failed"}

        test_id = f"test_{self.environment}_{uuid4().hex[:8]}"

        try:
            config = self.get_config()
            with self.driver.session(database=config["database"]) as session:
                # CREATE
                create_query = """
                CREATE (n:TestNode {id: $id, environment: $env, timestamp: $timestamp})
                RETURN n.id AS created_id
                """
                result = session.run(
                    create_query,
                    id=test_id,
                    env=self.environment,
                    timestamp=datetime.now().isoformat(),
                )
                created_id = result.single()["created_id"]

                if created_id != test_id:
                    return {"success": False, "error": "Create failed"}

                # READ
                read_query = "MATCH (n:TestNode {id: $id}) RETURN n"
                result = session.run(read_query, id=test_id)
                if not result.single():
                    return {"success": False, "error": "Read failed"}

                # UPDATE
                update_query = """
                MATCH (n:TestNode {id: $id}) 
                SET n.updated = $timestamp 
                RETURN n.id AS updated_id
                """
                result = session.run(update_query, id=test_id, timestamp=datetime.now().isoformat())
                if not result.single():
                    return {"success": False, "error": "Update failed"}

                # DELETE
                delete_query = """
                MATCH (n:TestNode {id: $id}) 
                DELETE n 
                RETURN count(n) AS deleted_count
                """
                result = session.run(delete_query, id=test_id)
                deleted_count = result.single()["deleted_count"]

                if deleted_count == 0:
                    return {"success": False, "error": "Delete failed"}

                return {"success": True, "test_id": test_id}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            self._logger.info("Neo4j connection closed")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience functions for backward compatibility
def get_neo4j_manager(environment: Optional[str] = None) -> Neo4jManager:
    """Get Neo4j manager instance."""
    return Neo4jManager(environment)


def test_neo4j_connectivity(environment: Optional[str] = None) -> Neo4jConnectivityResult:
    """Test Neo4j connectivity for given environment."""
    manager = Neo4jManager(environment)
    return manager.test_connectivity()


def validate_neo4j_environment(environment: Optional[str] = None) -> bool:
    """Validate Neo4j environment is working."""
    result = test_neo4j_connectivity(environment)
    return result.connected


# For Issue #266 requirements - main functionality preserved
__all__ = [
    "Neo4jManager",
    "Neo4jConnectivityResult",
    "get_neo4j_manager",
    "test_neo4j_connectivity",
    "validate_neo4j_environment",
]
