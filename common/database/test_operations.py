#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Test Operations for Database Validation

Provides CRUD operations on a dedicated test table for Neo4j connectivity
and functionality validation across all environments.

Issue #266: Comprehensive Neo4j Testing Infrastructure
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .neo4j_manager import Neo4jManager


class TestOperations:
    """
    Neo4j test operations for database validation.

    Implements CRUD operations on a dedicated TestNode table for:
    - Connectivity validation
    - Database functionality testing
    - Environment-specific testing
    """

    def __init__(self, manager: Neo4jManager):
        """
        Initialize test operations.

        Args:
            manager: Neo4jManager instance
        """
        self.manager = manager
        self.test_label = "TestNode"

    def setup_test_schema(self) -> bool:
        """
        Setup test table schema and constraints.

        Returns:
            True if schema setup successful, False otherwise
        """
        try:
            with self.manager.get_session() as session:
                # Create unique constraint on test node ID
                constraint_query = f"""
                CREATE CONSTRAINT test_node_id IF NOT EXISTS 
                FOR (n:{self.test_label}) REQUIRE n.id IS UNIQUE
                """
                session.run(constraint_query)

                # Create index for environment queries
                index_query = f"""
                CREATE INDEX test_node_env IF NOT EXISTS 
                FOR (n:{self.test_label}) ON (n.environment)
                """
                session.run(index_query)

                return True

        except Exception as e:
            self.manager._logger.error(f"Failed to setup test schema: {e}")
            return False

    def create_test_node(
        self, test_id: Optional[str] = None, test_data: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create a test node in the database.

        Args:
            test_id: Unique test identifier (auto-generated if None)
            test_data: Additional test data to store

        Returns:
            Test node ID if successful, None otherwise
        """
        if test_id is None:
            test_id = f"test_{self.manager.environment}_{uuid4().hex[:8]}"

        node_data = {
            "id": test_id,
            "environment": self.manager.environment,
            "timestamp": datetime.now().isoformat(),
            "test_data": "connectivity_validation",
            "version": "1.0",
        }

        if test_data:
            node_data.update(test_data)

        try:
            with self.manager.get_session() as session:
                query = f"""
                CREATE (n:{self.test_label} $properties)
                RETURN n.id AS id
                """
                result = session.run(query, properties=node_data)
                created_id = result.single()["id"]

                self.manager._logger.info(f"Created test node: {created_id}")
                return created_id

        except Exception as e:
            self.manager._logger.error(f"Failed to create test node: {e}")
            return None

    def read_test_node(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a test node from the database.

        Args:
            test_id: Test node identifier

        Returns:
            Test node data dictionary or None if not found
        """
        try:
            with self.manager.get_session() as session:
                query = f"""
                MATCH (n:{self.test_label} {{id: $test_id}})
                RETURN n
                """
                result = session.run(query, test_id=test_id)
                record = result.single()

                if record:
                    node_data = dict(record["n"])
                    self.manager._logger.info(f"Read test node: {test_id}")
                    return node_data

        except Exception as e:
            self.manager._logger.error(f"Failed to read test node {test_id}: {e}")

        return None

    def update_test_node(self, test_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a test node in the database.

        Args:
            test_id: Test node identifier
            updates: Data to update

        Returns:
            True if update successful, False otherwise
        """
        try:
            # Add timestamp to updates
            updates["last_updated"] = datetime.now().isoformat()

            with self.manager.get_session() as session:
                query = f"""
                MATCH (n:{self.test_label} {{id: $test_id}})
                SET n += $updates
                RETURN n.id AS id
                """
                result = session.run(query, test_id=test_id, updates=updates)

                if result.single():
                    self.manager._logger.info(f"Updated test node: {test_id}")
                    return True

        except Exception as e:
            self.manager._logger.error(f"Failed to update test node {test_id}: {e}")

        return False

    def delete_test_node(self, test_id: str) -> bool:
        """
        Delete a test node from the database.

        Args:
            test_id: Test node identifier

        Returns:
            True if deletion successful, False otherwise
        """
        try:
            with self.manager.get_session() as session:
                query = f"""
                MATCH (n:{self.test_label} {{id: $test_id}})
                DELETE n
                RETURN count(n) AS deleted_count
                """
                result = session.run(query, test_id=test_id)
                deleted_count = result.single()["deleted_count"]

                if deleted_count > 0:
                    self.manager._logger.info(f"Deleted test node: {test_id}")
                    return True

        except Exception as e:
            self.manager._logger.error(f"Failed to delete test node {test_id}: {e}")

        return False

    def list_test_nodes(self, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all test nodes, optionally filtered by environment.

        Args:
            environment: Filter by environment (None for all)

        Returns:
            List of test node data dictionaries
        """
        try:
            with self.manager.get_session() as session:
                if environment:
                    query = f"""
                    MATCH (n:{self.test_label} {{environment: $environment}})
                    RETURN n
                    ORDER BY n.timestamp DESC
                    """
                    result = session.run(query, environment=environment)
                else:
                    query = f"""
                    MATCH (n:{self.test_label})
                    RETURN n
                    ORDER BY n.timestamp DESC
                    """
                    result = session.run(query)

                nodes = [dict(record["n"]) for record in result]
                return nodes

        except Exception as e:
            self.manager._logger.error(f"Failed to list test nodes: {e}")
            return []

    def cleanup_test_nodes(
        self, environment: Optional[str] = None, older_than_hours: int = 24
    ) -> int:
        """
        Clean up old test nodes.

        Args:
            environment: Environment to clean (None for all)
            older_than_hours: Delete nodes older than this many hours

        Returns:
            Number of nodes deleted
        """
        try:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            cutoff_iso = datetime.fromtimestamp(cutoff_time).isoformat()

            with self.manager.get_session() as session:
                if environment:
                    query = f"""
                    MATCH (n:{self.test_label} {{environment: $environment}})
                    WHERE n.timestamp < $cutoff_time
                    DELETE n
                    RETURN count(n) AS deleted_count
                    """
                    result = session.run(query, environment=environment, cutoff_time=cutoff_iso)
                else:
                    query = f"""
                    MATCH (n:{self.test_label})
                    WHERE n.timestamp < $cutoff_time
                    DELETE n
                    RETURN count(n) AS deleted_count
                    """
                    result = session.run(query, cutoff_time=cutoff_iso)

                deleted_count = result.single()["deleted_count"]

                if deleted_count > 0:
                    self.manager._logger.info(f"Cleaned up {deleted_count} old test nodes")

                return deleted_count

        except Exception as e:
            self.manager._logger.error(f"Failed to cleanup test nodes: {e}")
            return 0

    def test_crud_operations(self) -> Dict[str, Any]:
        """
        Test all CRUD operations and return results.

        Returns:
            Dictionary with test results for each operation
        """
        results = {
            "schema_setup": False,
            "create": False,
            "read": False,
            "update": False,
            "delete": False,
            "performance_ms": {},
            "errors": [],
        }

        test_id = f"crud_test_{uuid4().hex[:8]}"

        try:
            # Setup schema
            start_time = time.time()
            results["schema_setup"] = self.setup_test_schema()
            results["performance_ms"]["schema_setup"] = int((time.time() - start_time) * 1000)

            # Test CREATE
            start_time = time.time()
            created_id = self.create_test_node(test_id, {"test_type": "crud_validation"})
            results["create"] = created_id is not None
            results["performance_ms"]["create"] = int((time.time() - start_time) * 1000)

            if not results["create"]:
                results["errors"].append("Failed to create test node")
                return results

            # Test READ
            start_time = time.time()
            node_data = self.read_test_node(test_id)
            results["read"] = node_data is not None and node_data.get("id") == test_id
            results["performance_ms"]["read"] = int((time.time() - start_time) * 1000)

            # Test UPDATE
            start_time = time.time()
            results["update"] = self.update_test_node(test_id, {"crud_test_updated": True})
            results["performance_ms"]["update"] = int((time.time() - start_time) * 1000)

            # Test DELETE
            start_time = time.time()
            results["delete"] = self.delete_test_node(test_id)
            results["performance_ms"]["delete"] = int((time.time() - start_time) * 1000)

        except Exception as e:
            results["errors"].append(f"CRUD test error: {e}")

        return results
