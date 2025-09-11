#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Connectivity Unit Tests

Comprehensive test suite for Neo4j connectivity and operations across
all environments with automatic environment detection.

Issue #266: Comprehensive Neo4j Testing Infrastructure
"""

import os
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import Neo4j testing infrastructure
from common.database import HealthChecker, Neo4jManager, TestOperations


class TestNeo4jConnectivity(unittest.TestCase):
    """
    Neo4j connectivity and operations test suite.
    Reusable across all environments with environment-specific configuration.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize Neo4j connection based on environment"""
        cls.original_env = os.environ.copy()

    @classmethod
    def tearDownClass(cls):
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(cls.original_env)

    def setUp(self):
        """Setup for each test"""
        # Clear environment variables for clean state
        for key in ["CI", "PRODUCTION", "NEO4J_PRODUCTION"]:
            os.environ.pop(key, None)

    def test_environment_detection_development(self):
        """Test environment detection for development"""
        manager = Neo4jManager()
        self.assertEqual(manager.environment, "development")

    def test_environment_detection_ci(self):
        """Test environment detection for CI"""
        os.environ["CI"] = "true"
        manager = Neo4jManager()
        self.assertEqual(manager.environment, "ci")

    def test_environment_detection_production(self):
        """Test environment detection for production"""
        os.environ["PRODUCTION"] = "true"
        manager = Neo4jManager()
        self.assertEqual(manager.environment, "production")

    def test_explicit_environment_override(self):
        """Test explicit environment parameter override"""
        os.environ["CI"] = "true"  # Should be overridden
        manager = Neo4jManager(environment="development")
        self.assertEqual(manager.environment, "development")

    def test_configuration_loading_default(self):
        """Test configuration loading with defaults"""
        manager = Neo4jManager(environment="development")
        config = manager.config

        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["port"], 7687)
        self.assertEqual(config["database"], "neo4j")
        self.assertIn("auth", config)
        self.assertIn("connection", config)

    def test_connection_uri_generation(self):
        """Test Neo4j connection URI generation"""
        manager = Neo4jManager(environment="development")
        uri = manager.get_connection_uri()
        self.assertEqual(uri, "bolt://localhost:7687")

    def test_connection_uri_custom_host_port(self):
        """Test URI generation with custom host and port"""
        manager = Neo4jManager(environment="production")
        # Mock production config
        manager.config = {"host": "neo4j-prod.example.com", "port": 7688}
        uri = manager.get_connection_uri()
        self.assertEqual(uri, "bolt://neo4j-prod.example.com:7688")

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", False)
    def test_connection_without_neo4j_driver(self):
        """Test graceful handling when Neo4j driver is not available"""
        manager = Neo4jManager(environment="development")
        result = manager.connect()
        self.assertFalse(result)

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j_manager.GraphDatabase")
    def test_connection_success(self, mock_graph_db):
        """Test successful Neo4j connection"""
        # Mock successful connection
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = 1
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        manager = Neo4jManager(environment="development")
        result = manager.connect()

        self.assertTrue(result)
        self.assertIsNotNone(manager.driver)

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j_manager.GraphDatabase")
    def test_connection_failure(self, mock_graph_db):
        """Test Neo4j connection failure handling"""
        # Mock connection failure
        mock_graph_db.driver.side_effect = Exception("Connection failed")

        manager = Neo4jManager(environment="development")
        result = manager.connect()

        self.assertFalse(result)
        self.assertIsNone(manager.driver)

    def test_connectivity_test_without_driver(self):
        """Test connectivity test when Neo4j driver is not available"""
        with patch("common.database.neo4j_manager.NEO4J_AVAILABLE", False):
            manager = Neo4jManager(environment="development")
            result = manager.test_connectivity()

            self.assertEqual(result["environment"], "development")
            self.assertFalse(result["neo4j_available"])
            self.assertFalse(result["connected"])
            self.assertEqual(result["error"], "Neo4j driver not installed")

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j_manager.GraphDatabase")
    def test_connectivity_test_success(self, mock_graph_db):
        """Test successful connectivity test"""
        # Mock successful connection and query
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        manager = Neo4jManager(environment="ci")

        with patch.object(manager, "connect", return_value=True):
            with patch.object(manager, "get_session", return_value=mock_session):
                result = manager.test_connectivity()

                self.assertEqual(result["environment"], "ci")
                self.assertTrue(result["neo4j_available"])
                self.assertTrue(result["connected"])
                self.assertIsNotNone(result["response_time_ms"])
                self.assertIsNone(result["error"])

    def test_context_manager(self):
        """Test Neo4jManager as context manager"""
        manager = Neo4jManager(environment="development")

        with patch.object(manager, "connect", return_value=True) as mock_connect:
            with patch.object(manager, "close") as mock_close:
                with manager:
                    pass

                mock_connect.assert_called_once()
                mock_close.assert_called_once()


class TestNeo4jOperations(unittest.TestCase):
    """Test Neo4j test operations functionality"""

    def setUp(self):
        """Setup test manager and operations"""
        self.manager = Neo4jManager(environment="ci")
        self.test_ops = TestOperations(self.manager)

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", True)
    def test_setup_test_schema(self):
        """Test test schema setup"""
        mock_session = MagicMock()

        with patch.object(self.manager, "get_session", return_value=mock_session):
            with patch.object(mock_session, "__enter__", return_value=mock_session):
                with patch.object(mock_session, "__exit__", return_value=None):
                    result = self.test_ops.setup_test_schema()

                    self.assertTrue(result)
                    # Verify schema creation queries were called
                    self.assertEqual(mock_session.run.call_count, 2)

    @patch("common.database.neo4j_manager.NEO4J_AVAILABLE", True)
    def test_create_test_node(self):
        """Test test node creation"""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = "test_node_123"
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result

        with patch.object(self.manager, "get_session", return_value=mock_session):
            with patch.object(mock_session, "__enter__", return_value=mock_session):
                with patch.object(mock_session, "__exit__", return_value=None):
                    result = self.test_ops.create_test_node("test_node_123")

                    self.assertEqual(result, "test_node_123")
                    mock_session.run.assert_called_once()

    def test_crud_operations_mock(self):
        """Test complete CRUD operations with mocked Neo4j"""
        with patch.object(self.test_ops, "setup_test_schema", return_value=True):
            with patch.object(self.test_ops, "create_test_node", return_value="test_id"):
                with patch.object(self.test_ops, "read_test_node", return_value={"id": "test_id"}):
                    with patch.object(self.test_ops, "update_test_node", return_value=True):
                        with patch.object(self.test_ops, "delete_test_node", return_value=True):

                            result = self.test_ops.test_crud_operations()

                            self.assertTrue(result["schema_setup"])
                            self.assertTrue(result["create"])
                            self.assertTrue(result["read"])
                            self.assertTrue(result["update"])
                            self.assertTrue(result["delete"])
                            self.assertIn("performance_ms", result)
                            self.assertEqual(len(result["errors"]), 0)


class TestNeo4jHealthCheck(unittest.TestCase):
    """Test Neo4j health checking functionality"""

    def setUp(self):
        """Setup test manager and health checker"""
        self.manager = Neo4jManager(environment="ci")
        self.health_checker = HealthChecker(self.manager)

    def test_basic_connectivity_check(self):
        """Test basic connectivity health check"""
        mock_connectivity = {
            "environment": "ci",
            "neo4j_available": True,
            "connected": True,
            "response_time_ms": 50,
            "error": None,
        }

        with patch.object(self.manager, "test_connectivity", return_value=mock_connectivity):
            result = self.health_checker.check_basic_connectivity()

            self.assertTrue(result["connected"])
            self.assertEqual(result["environment"], "ci")
            self.assertIsNone(result["error"])

    def test_performance_baseline_check(self):
        """Test performance baseline validation"""
        mock_session = MagicMock()

        with patch.object(self.manager, "get_session", return_value=mock_session):
            with patch.object(mock_session, "__enter__", return_value=mock_session):
                with patch.object(mock_session, "__exit__", return_value=None):
                    with patch("time.time", side_effect=[0, 0.05]):  # 50ms response
                        result = self.health_checker.check_performance_baseline()

                        self.assertTrue(result["baseline_met"])
                        self.assertEqual(result["response_time_ms"], 50)
                        self.assertIsNone(result["error"])

    def test_comprehensive_health_check_healthy(self):
        """Test comprehensive health check with healthy status"""
        # Mock all sub-checks to return healthy results
        mock_connectivity = {"connected": True, "error": None}
        mock_performance = {"baseline_met": True, "response_time_ms": 30}
        mock_crud = {"create": True, "read": True, "update": True, "delete": True, "errors": []}

        with patch.object(
            self.health_checker, "check_basic_connectivity", return_value=mock_connectivity
        ):
            with patch.object(
                self.health_checker, "check_performance_baseline", return_value=mock_performance
            ):
                with patch.object(
                    self.health_checker, "check_database_operations", return_value=mock_crud
                ):
                    with patch.object(
                        self.health_checker, "get_database_version", return_value="5.15.0"
                    ):

                        result = self.health_checker.comprehensive_health_check()

                        self.assertEqual(result.status, "healthy")
                        self.assertEqual(result.environment, "ci")
                        self.assertIsNotNone(result.response_time_ms)
                        self.assertIsNone(result.warnings)

    def test_health_check_endpoint_format(self):
        """Test health check endpoint response format"""
        from common.database.health_checks import HealthStatus

        with patch.object(self.health_checker, "comprehensive_health_check") as mock_check:
            mock_status = HealthStatus(
                status="healthy",
                response_time_ms=45,
                environment="ci",
                last_test_timestamp="2025-01-11T10:30:00Z",
                version="5.15.0",
                test_operations={"connection": "success"},
                warnings=None,
                error=None,
            )

            mock_check.return_value = mock_status

            result = self.health_checker.health_check_endpoint()

            # Verify required fields are present
            self.assertIn("status", result)
            self.assertIn("response_time_ms", result)
            self.assertIn("environment", result)
            self.assertIn("timestamp", result)
            self.assertIn("check_type", result)


# Integration tests (require actual Neo4j instance)
@pytest.mark.integration
class TestNeo4jIntegration(unittest.TestCase):
    """
    Integration tests that require a running Neo4j instance.

    These tests are marked with @pytest.mark.integration and can be run
    separately when a Neo4j instance is available.
    """

    @classmethod
    def setUpClass(cls):
        """Setup for integration tests"""
        cls.manager = Neo4jManager(environment="ci")

        # Skip integration tests if Neo4j is not available
        connectivity = cls.manager.test_connectivity()
        if not connectivity["connected"]:
            pytest.skip("Neo4j instance not available for integration tests")

    def test_real_connection(self):
        """Test real Neo4j connection"""
        result = self.manager.connect()
        self.assertTrue(result, "Failed to connect to real Neo4j instance")

    def test_real_crud_operations(self):
        """Test real CRUD operations on Neo4j"""
        test_ops = TestOperations(self.manager)
        result = test_ops.test_crud_operations()

        self.assertTrue(result["schema_setup"], "Schema setup failed")
        self.assertTrue(result["create"], "Create operation failed")
        self.assertTrue(result["read"], "Read operation failed")
        self.assertTrue(result["update"], "Update operation failed")
        self.assertTrue(result["delete"], "Delete operation failed")

    def test_real_health_check(self):
        """Test real health check"""
        health_checker = HealthChecker(self.manager)
        result = health_checker.comprehensive_health_check()

        self.assertIn(result.status, ["healthy", "degraded"])
        self.assertIsNotNone(result.response_time_ms)
        self.assertEqual(result.environment, "ci")

    @classmethod
    def tearDownClass(cls):
        """Cleanup after integration tests"""
        if hasattr(cls, "manager") and cls.manager:
            # Clean up any test data
            test_ops = TestOperations(cls.manager)
            test_ops.cleanup_test_nodes(environment="ci", older_than_hours=0)
            cls.manager.close()


if __name__ == "__main__":
    # Run unit tests by default, integration tests separately
    unittest.main(argv=[""], verbosity=2, exit=False)

    # To run integration tests:
    # pytest -m integration tests/database/test_neo4j_connectivity.py
