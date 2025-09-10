#!/usr/bin/env python3
"""
Common test configuration and fixtures for the entire test suite.
Provides reusable fixtures, utilities, and test setup/teardown.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# =============================================================================
# Core Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provides path to test data directory."""
    return TEST_DATA_DIR


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Creates a temporary directory for test use."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_project_root(temp_dir: Path) -> Path:
    """Creates a mock project root structure for testing."""
    project_root = temp_dir / "mock_project"
    project_root.mkdir()

    # Create common directory structure
    (project_root / "common").mkdir()
    (project_root / "common" / "config").mkdir()
    (project_root / "build_data").mkdir()

    return project_root


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def sample_config_data() -> Dict[str, Any]:
    """Provides sample configuration data for testing."""
    return {
        "storage": {"backend": "local_filesystem", "root_path": "build_data"},
        "layers": {
            "stage_00_raw": "Raw Data Layer",
            "stage_01_daily_delta": "Daily Delta Layer",
            "stage_02_daily_index": "Daily Index Layer",
            "stage_03_graph_rag": "Graph RAG Layer",
            "stage_04_query_results": "Query Results Layer",
        },
        "logging": {"level": "INFO", "format": "%(asctime)s - %(levelname)s - %(message)s"},
    }


@pytest.fixture
def mock_config_file(temp_dir: Path, sample_config_data: Dict[str, Any]) -> Path:
    """Creates a mock configuration file for testing."""
    config_file = temp_dir / "test_config.yml"
    with open(config_file, "w") as f:
        yaml.dump(sample_config_data, f)
    return config_file


@pytest.fixture
def sample_company_data() -> Dict[str, Any]:
    """Provides sample company data for testing."""
    return {
        "companies": [
            {"ticker": "AAPL", "name": "Apple Inc.", "cik": "0000320193", "sector": "Technology"},
            {
                "ticker": "MSFT",
                "name": "Microsoft Corporation",
                "cik": "0000789019",
                "sector": "Technology",
            },
        ]
    }


# =============================================================================
# Directory Manager Fixtures
# =============================================================================


@pytest.fixture
def mock_directory_config(temp_dir: Path) -> Dict[str, Any]:
    """Provides mock directory configuration."""
    return {
        "storage": {"backend": "local_filesystem", "root_path": str(temp_dir / "build_data")},
        "paths": {
            "config": str(temp_dir / "common" / "config"),
            "logs": str(temp_dir / "build_data" / "logs"),
            "cache": str(temp_dir / "cache"),
            "temp": str(temp_dir / "temp"),
        },
        "data_layers": {
            "stage_00_raw": "stage_00_raw",
            "stage_01_daily_delta": "stage_01_daily_delta",
            "stage_02_daily_index": "stage_02_daily_index",
            "stage_03_graph_rag": "stage_03_graph_rag",
            "stage_04_query_results": "stage_04_query_results",
        },
    }


@pytest.fixture
def mock_directory_manager(mock_project_root: Path, mock_directory_config: Dict[str, Any]):
    """Provides a mock DirectoryManager instance for testing."""
    with patch("common.core.directory_manager.DirectoryManager") as mock_dm:
        # Setup mock methods
        mock_instance = mock_dm.return_value
        mock_instance.get_layer_path.return_value = (
            mock_project_root / "build_data" / "stage_00_raw"
        )
        mock_instance.get_config_path.return_value = mock_project_root / "common" / "config"
        mock_instance.get_logs_path.return_value = mock_project_root / "build_data" / "logs"
        mock_instance.config = mock_directory_config

        yield mock_instance


# =============================================================================
# Storage Manager Fixtures
# =============================================================================


@pytest.fixture
def mock_storage_backend():
    """Provides a mock storage backend for testing."""
    mock_backend = MagicMock()
    mock_backend.read_text.return_value = "mock file content"
    mock_backend.write_text.return_value = None
    mock_backend.exists.return_value = True
    mock_backend.list_directory.return_value = ["file1.txt", "file2.json"]
    return mock_backend


# =============================================================================
# Agent-related Fixtures
# =============================================================================


@pytest.fixture
def mock_agent_config() -> Dict[str, Any]:
    """Provides mock agent configuration data."""
    return {
        "coordination": {"max_agents": 10, "timeout_seconds": 300, "retry_attempts": 3},
        "performance": {
            "monitoring_enabled": True,
            "metrics_interval": 60,
            "alert_thresholds": {"cpu_percent": 80, "memory_mb": 1000},
        },
        "hrbp": {"automation_enabled": True, "review_cycle_days": 30, "pr_threshold": 20},
    }


# =============================================================================
# Build System Fixtures
# =============================================================================


@pytest.fixture
def mock_build_manifest() -> Dict[str, Any]:
    """Provides mock build manifest data."""
    return {
        "build_id": "test-build-12345",
        "timestamp": "2025-01-01T00:00:00Z",
        "tier": "f2",
        "status": "success",
        "files_processed": 10,
        "execution_time_seconds": 120,
        "data_layers": {
            "stage_00_raw": {"files": 5, "size_mb": 100},
            "stage_04_query_results": {"files": 2, "size_mb": 50},
        },
    }


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def mock_snowflake_id() -> str:
    """Provides a mock snowflake ID for testing."""
    return "123456789012345678"


@pytest.fixture
def mock_timestamp() -> str:
    """Provides a mock timestamp for testing."""
    return "2025-01-01T00:00:00Z"


# =============================================================================
# Environment Setup/Teardown
# =============================================================================


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Sets up clean test environment for each test."""
    # Mock environment variables
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Mock external dependencies that might not be available
    with patch.dict("sys.modules", {"yaml": MagicMock()}):
        yield


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here if needed


# =============================================================================
# Test Markers and Categories
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line(
        "markers", "integration: Integration tests for cross-module functionality"
    )
    config.addinivalue_line("markers", "slow: Slow tests that may take longer to run")
    config.addinivalue_line("markers", "core: Tests for core system components")
    config.addinivalue_line("markers", "agents: Tests for agent-related modules")
    config.addinivalue_line("markers", "build: Tests for build and quality modules")
    config.addinivalue_line("markers", "monitoring: Tests for monitoring components")
    config.addinivalue_line("markers", "schemas: Tests for schema definitions")
    config.addinivalue_line("markers", "utils: Tests for utility modules")
    config.addinivalue_line("markers", "legacy: Tests for legacy/deprecated components")
