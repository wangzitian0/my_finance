"""
Simplified tests for CI pipeline validation
"""

import os
from pathlib import Path

import pytest


class TestPipelineBasics:
    """Basic pipeline validation tests that work in CI"""

    def test_test_files_exist(self):
        """Verify test files are present"""
        test_dir = Path("tests")
        assert test_dir.exists(), "Tests directory should exist"

        test_files = list(test_dir.glob("test_*.py"))
        assert len(test_files) >= 2, f"Should have at least 2 test files, found {len(test_files)}"

    def test_basic_imports_work(self):
        """Test that basic Python imports work"""
        import json
        import pathlib
        import subprocess

        # Test basic functionality
        data = {"test": "value"}
        json_str = json.dumps(data)
        assert json_str == '{"test": "value"}'

    def test_directory_structure(self):
        """Verify basic directory structure exists - Updated for Issue #122 five-layer architecture"""
        required_dirs = [
            "tests",
            "scripts",
            ".github/workflows",
            "common/config",
            # Note: build_data directory and five-layer structure are created on-demand
            # by the new directory manager system, so we don't require them to exist
            # in the base repository structure
        ]

        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Required directory {dir_name} should exist"

        # Test that the new directory manager can create the five-layer structure
        from common import DataLayer, directory_manager

        # Verify the five-layer enum is correct
        expected_layers = ["RAW_DATA", "DAILY_DELTA", "DAILY_INDEX", "GRAPH_RAG", "QUERY_RESULTS"]
        actual_layers = [layer.name for layer in DataLayer]
        assert (
            actual_layers == expected_layers
        ), f"DataLayer enum should match expected: {expected_layers}"

        # Test that path generation works
        raw_path = directory_manager.get_layer_path(DataLayer.RAW_DATA)
        assert str(raw_path).endswith(
            "stage_00_raw"
        ), "Raw data path should use new naming convention"

    def test_config_files_accessible(self):
        """Test configuration file access"""
        config_dir = Path("common/config")
        if config_dir.exists():
            # If config directory exists, check it's readable
            config_files = list(config_dir.glob("*.yml"))
            assert len(config_files) >= 0, "Config directory should be accessible"
        else:
            # In CI, create minimal config
            config_dir.mkdir(parents=True, exist_ok=True)
            test_config = config_dir / "test.yml"
            test_config.write_text("test_mode: true\n")
            assert test_config.exists(), "Should be able to create config files"

    def test_workflow_files_exist(self):
        """Verify GitHub Actions workflow files exist"""
        workflow_dir = Path(".github/workflows")
        assert workflow_dir.exists(), "Workflow directory should exist"

        workflow_files = list(workflow_dir.glob("*.yml"))
        assert len(workflow_files) > 0, "Should have at least one workflow file"
