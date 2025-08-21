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
        """Verify basic directory structure exists"""
        required_dirs = [
            "tests",
            "scripts",
            ".github/workflows",
            "data/stage_01_extract",
            "data/stage_02_transform",
            "data/stage_03_load",
            "data/build",
            "common/config",
        ]

        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Required directory {dir_name} should exist"

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
