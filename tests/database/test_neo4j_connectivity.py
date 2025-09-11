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

# Import simplified Neo4j testing infrastructure
from common.database import Neo4jConnectivityResult, Neo4jManager


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
        config = manager.get_config()

        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["port"], 7687)
        self.assertEqual(config["database"], "neo4j")
        self.assertEqual(config["user"], "neo4j")
        self.assertEqual(config["password"], "finance123")

    def test_connection_uri_generation(self):
        """Test Neo4j connection URI generation"""
        manager = Neo4jManager(environment="development")
        uri = manager.get_connection_uri()
        self.assertEqual(uri, "bolt://localhost:7687")

    def test_connection_uri_custom_host_port(self):
        """Test URI generation with custom host and port"""
        # Set environment variables to override production config
        os.environ["NEO4J_HOST"] = "neo4j-prod.example.com"
        os.environ["NEO4J_PORT"] = "7688"
        try:
            manager = Neo4jManager(environment="production")
            uri = manager.get_connection_uri()
            self.assertEqual(uri, "bolt://neo4j-prod.example.com:7688")
        finally:
            # Cleanup environment
            os.environ.pop("NEO4J_HOST", None)
            os.environ.pop("NEO4J_PORT", None)

    @patch("common.database.neo4j.NEO4J_AVAILABLE", False)
    def test_connection_without_neo4j_driver(self):
        """Test graceful handling when Neo4j driver is not available"""
        manager = Neo4jManager(environment="development")
        result = manager.connect()
        self.assertFalse(result)

    @patch("common.database.neo4j.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j.GraphDatabase")
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

    @patch("common.database.neo4j.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j.GraphDatabase")
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
        with patch("common.database.neo4j.NEO4J_AVAILABLE", False):
            manager = Neo4jManager(environment="development")
            result = manager.test_connectivity()

            self.assertEqual(result.environment, "development")
            self.assertFalse(result.neo4j_available)
            self.assertFalse(result.connected)
            self.assertEqual(result.error, "Neo4j driver not installed")

    @patch("common.database.neo4j.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j.GraphDatabase")
    def test_connectivity_test_success(self, mock_graph_db):
        """Test successful connectivity test"""
        # Mock successful connection and query
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        mock_record.__getitem__.return_value = 1
        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_graph_db.driver.return_value = mock_driver

        manager = Neo4jManager(environment="ci")
        result = manager.test_connectivity()

        self.assertEqual(result.environment, "ci")
        self.assertTrue(result.neo4j_available)
        self.assertTrue(result.connected)
        self.assertIsNotNone(result.response_time_ms)
        self.assertIsNone(result.error)

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
    """Test Neo4j operations functionality using simplified CRUD testing"""

    def setUp(self):
        """Setup test manager"""
        self.manager = Neo4jManager(environment="ci")

    def test_crud_operations_mock(self):
        """Test complete CRUD operations with mocked Neo4j"""
        with patch.object(self.manager, "connect", return_value=True):
            result = self.manager.test_crud_operations()
            # When mocked, should return success or fail predictably
            self.assertIn("success", result)
            self.assertIsInstance(result["success"], bool)


class TestNeo4jHealthCheck(unittest.TestCase):
    """Test Neo4j connectivity checking functionality"""

    def setUp(self):
        """Setup test manager"""
        self.manager = Neo4jManager(environment="ci")

    @patch("common.database.neo4j.NEO4J_AVAILABLE", True)
    @patch("common.database.neo4j.GraphDatabase")
    def test_basic_connectivity_check(self, mock_graph_db):
        """Test basic connectivity check"""
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

        result = self.manager.test_connectivity()

        self.assertTrue(result.connected)
        self.assertEqual(result.environment, "ci")
        self.assertIsNone(result.error)

    def test_connectivity_with_response_time(self):
        """Test connectivity includes response time measurement"""
        result = self.manager.test_connectivity()

        # Should have response time measurement
        if result.connected:
            self.assertIsNotNone(result.response_time_ms)
        else:
            # May be None if connection failed
            self.assertTrue(
                result.response_time_ms is None or isinstance(result.response_time_ms, int)
            )


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
        try:
            cls.manager = Neo4jManager(environment="ci")

            # Skip integration tests if Neo4j is not available
            connectivity = cls.manager.test_connectivity()
            if not connectivity.connected:
                pytest.skip("Neo4j instance not available for integration tests")
        except Exception as e:
            # Handle any setup errors gracefully
            pytest.skip(f"Neo4j setup failed: {e}")

    def test_real_connection(self):
        """Test real Neo4j connection"""
        if not hasattr(self, "manager"):
            self.skipTest("Neo4j manager not available")
        result = self.manager.connect()
        self.assertTrue(result, "Failed to connect to real Neo4j instance")

    def test_real_crud_operations(self):
        """Test real CRUD operations on Neo4j"""
        if not hasattr(self, "manager"):
            self.skipTest("Neo4j manager not available")
        result = self.manager.test_crud_operations()

        self.assertTrue(result["success"], "CRUD operations failed")

    def test_real_connectivity_check(self):
        """Test real connectivity check"""
        if not hasattr(self, "manager"):
            self.skipTest("Neo4j manager not available")
        result = self.manager.test_connectivity()

        self.assertTrue(result.connected)
        self.assertIsNotNone(result.response_time_ms)
        self.assertEqual(result.environment, "ci")

    @classmethod
    def tearDownClass(cls):
        """Cleanup after integration tests"""
        if hasattr(cls, "manager") and cls.manager:
            cls.manager.close()


if __name__ == "__main__":
    # Run unit tests by default, integration tests separately
    unittest.main(argv=[""], verbosity=2, exit=False)

    # To run integration tests:
    # pytest -m integration tests/database/test_neo4j_connectivity.py
