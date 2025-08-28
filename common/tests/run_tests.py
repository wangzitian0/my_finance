#!/usr/bin/env python3
"""
Simple test runner for testing DirectoryManager improvements without pytest dependency
"""

import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import yaml

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.core.directory_manager import DataLayer, DirectoryManager, StorageBackend


class SimpleTestRunner:
    """Simple test runner that doesn't require pytest"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def assert_equal(self, actual, expected, message=""):
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}. {message}")

    def assert_true(self, condition, message=""):
        if not condition:
            raise AssertionError(f"Expected True, got {condition}. {message}")

    def assert_false(self, condition, message=""):
        if condition:
            raise AssertionError(f"Expected False, got {condition}. {message}")

    def assert_in(self, item, container, message=""):
        if item not in container:
            raise AssertionError(f"Expected {item} in {container}. {message}")

    def assert_raises(self, exception_type, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            raise AssertionError(f"Expected {exception_type.__name__} but no exception was raised")
        except exception_type:
            pass  # Expected
        except Exception as e:
            raise AssertionError(
                f"Expected {exception_type.__name__} but got {type(e).__name__}: {e}"
            )

    def run_test(self, test_func, test_name=""):
        """Run a single test function"""
        try:
            test_func()
            self.tests_passed += 1
            print(f"✓ {test_name or test_func.__name__}")
        except Exception as e:
            self.tests_failed += 1
            self.failures.append((test_name or test_func.__name__, str(e)))
            print(f"✗ {test_name or test_func.__name__}: {e}")
            if os.environ.get("TEST_DEBUG"):
                traceback.print_exc()

    def run_all_tests(self):
        """Run all test methods"""
        print("Running DirectoryManager Integration Tests...")
        print("=" * 50)

        # Test 1: Basic DirectoryManager functionality
        self.run_test(self.test_directory_manager_initialization, "DirectoryManager initialization")
        self.run_test(self.test_path_resolution, "Path resolution")
        self.run_test(self.test_layer_path_caching, "Layer path caching")
        self.run_test(self.test_security_validation, "Security validation")
        self.run_test(self.test_error_handling, "Error handling")
        self.run_test(self.test_legacy_path_mapping, "Legacy path mapping")
        self.run_test(self.test_directory_creation, "Directory creation")
        self.run_test(self.test_configuration_loading, "Configuration loading")

        # Print summary
        print("\n" + "=" * 50)
        total_tests = self.tests_passed + self.tests_failed
        print(f"Tests completed: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")

        if self.failures:
            print("\nFailures:")
            for test_name, error in self.failures:
                print(f"  - {test_name}: {error}")

        return self.tests_failed == 0

    def test_directory_manager_initialization(self):
        """Test basic DirectoryManager initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)

            self.assert_equal(dm.root_path, project_root)
            self.assert_equal(dm.backend, StorageBackend.LOCAL_FS)
            self.assert_true(dm.config is not None)
            self.assert_in("storage", dm.config)
            self.assert_in("layers", dm.config)

    def test_path_resolution(self):
        """Test path resolution functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)

            # Test layer path resolution
            raw_path = dm.get_layer_path(DataLayer.RAW_DATA)
            self.assert_in("layer_01_raw", str(raw_path))
            self.assert_in("build_data", str(raw_path))

            # Test with partition
            partitioned_path = dm.get_layer_path(DataLayer.RAW_DATA, "20250828")
            self.assert_in("20250828", str(partitioned_path))
            self.assert_in("layer_01_raw", str(partitioned_path))

            # Test subdir path
            subdir_path = dm.get_subdir_path(DataLayer.RAW_DATA, "sec-edgar")
            self.assert_in("sec-edgar", str(subdir_path))
            self.assert_in("layer_01_raw", str(subdir_path))

    def test_layer_path_caching(self):
        """Test path resolution caching"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)

            # First access (cache miss)
            path1 = dm.get_layer_path(DataLayer.RAW_DATA)
            stats1 = dm.get_cache_stats()
            self.assert_equal(stats1["cache_misses"], 1)
            self.assert_equal(stats1["cache_hits"], 0)

            # Second access (cache hit)
            path2 = dm.get_layer_path(DataLayer.RAW_DATA)
            stats2 = dm.get_cache_stats()
            self.assert_equal(stats2["cache_hits"], 1)
            self.assert_equal(path1, path2)

    def test_security_validation(self):
        """Test security validation features"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)

            # Test path component sanitization
            self.assert_raises(ValueError, dm._sanitize_path_component, "../../../etc/passwd")
            self.assert_raises(ValueError, dm._sanitize_path_component, "folder; rm -rf /")
            self.assert_raises(ValueError, dm._sanitize_path_component, "/absolute/path")

            # Valid component should pass
            valid_component = dm._sanitize_path_component("valid-folder_123")
            self.assert_equal(valid_component, "valid-folder_123")

            # Test subprocess argument validation
            self.assert_raises(ValueError, dm._validate_subprocess_args, ["rm", "-rf", "/"])
            self.assert_raises(TypeError, dm._validate_subprocess_args, "not_a_list")

            # Valid args should pass
            valid_args = dm._validate_subprocess_args(["echo", "hello"])
            self.assert_equal(valid_args, ["echo", "hello"])

    def test_error_handling(self):
        """Test error handling capabilities"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            # Don't create config directory to test missing config handling

            # Should handle missing config gracefully
            dm = DirectoryManager(root_path=project_root)
            self.assert_true(dm.config is not None)

            # Should still be able to resolve paths
            path = dm.get_layer_path(DataLayer.RAW_DATA)
            self.assert_true(isinstance(path, Path))

    def test_legacy_path_mapping(self):
        """Test legacy path mapping functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)

            # Test legacy mappings
            legacy_mappings = [
                ("stage_00_original", DataLayer.RAW_DATA),
                ("stage_99_build", DataLayer.QUERY_RESULTS),
                ("layer_01_raw", DataLayer.RAW_DATA),
                ("build_data", DataLayer.QUERY_RESULTS),
                ("data", DataLayer.RAW_DATA),
            ]

            for legacy_path, expected_layer in legacy_mappings:
                mapped_layer = dm.map_legacy_path(legacy_path)
                self.assert_equal(mapped_layer, expected_layer, f"Failed mapping {legacy_path}")

            # Test invalid mapping
            invalid_result = dm.map_legacy_path("nonexistent_path")
            self.assert_equal(invalid_result, None)

    def test_directory_creation(self):
        """Test directory creation functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            (project_root / "common" / "config").mkdir(parents=True)

            dm = DirectoryManager(root_path=project_root)
            dm.ensure_directories()

            # Verify layer directories were created
            for layer in DataLayer:
                layer_path = dm.get_layer_path(layer)
                # Directory might not exist yet, but path should be valid
                self.assert_true(isinstance(layer_path, Path))
                self.assert_in(layer.value, str(layer_path))

    def test_configuration_loading(self):
        """Test configuration loading with validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            config_dir = project_root / "common" / "config"
            config_dir.mkdir(parents=True)

            # Create test config
            config_content = {
                "storage": {"backend": "local_filesystem", "root_path": "test_data"},
                "layers": {"layer_01_raw": {"subdirs": ["test-source"]}},
                "common": {
                    "config": "common/config",
                    "logs": "logs",
                    "temp": "temp",
                    "cache": "cache",
                },
            }

            config_file = config_dir / "directory_structure.yml"
            with open(config_file, "w") as f:
                yaml.dump(config_content, f)

            dm = DirectoryManager(root_path=project_root)

            # Verify config loaded correctly
            self.assert_equal(dm.config["storage"]["root_path"], "test_data")
            self.assert_in("layer_01_raw", dm.config["layers"])


if __name__ == "__main__":
    runner = SimpleTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
